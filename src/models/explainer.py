"""
Model explainability and interpretation.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
from sklearn.inspection import permutation_importance

from src.utils.config import VEHICLE_CATEGORIES, POLLUTANTS
from src.utils.helpers import setup_logging, save_dataframe, calculate_percentage_contribution

logger = setup_logging(__name__)


class ModelExplainer:
    """
    Explain model predictions and feature importance.
    """
    
    def __init__(self):
        """Initialize explainer."""
        pass
    
    def get_feature_importance(self,
                              model,
                              model_type: str,
                              feature_names: List[str]) -> pd.DataFrame:
        """
        Extract feature importance from model.
        
        Args:
            model: Trained model
            model_type: Model type name
            feature_names: List of feature names
            
        Returns:
            DataFrame with feature importance
        """
        if model_type in ['linear_regression', 'ridge_regression', 'lasso_regression']:
            # Use absolute coefficients
            importance = np.abs(model.coef_)
            importance_type = 'Absolute Coefficient'
        elif model_type in ['decision_tree', 'random_forest']:
            # Use built-in feature importance
            importance = model.feature_importances_
            importance_type = 'Gini Importance'
        else:
            raise ValueError(f"Feature importance not supported for {model_type}")
        
        # Create DataFrame
        importance_df = pd.DataFrame({
            'feature': feature_names,
            'importance': importance,
            'importance_type': importance_type
        })
        
        # Normalize importance to sum to 1
        importance_df['importance_normalized'] = (
            importance_df['importance'] / importance_df['importance'].sum()
        )
        
        # Sort by importance
        importance_df = importance_df.sort_values('importance', ascending=False)
        importance_df = importance_df.reset_index(drop=True)
        
        return importance_df
    
    def get_permutation_importance(self,
                                  model,
                                  X: pd.DataFrame,
                                  y: pd.Series,
                                  n_repeats: int = 10) -> pd.DataFrame:
        """
        Calculate permutation importance.
        
        Args:
            model: Trained model
            X: Feature matrix
            y: Target vector
            n_repeats: Number of permutation repeats
            
        Returns:
            DataFrame with permutation importance
        """
        logger.info("Calculating permutation importance...")
        
        perm_importance = permutation_importance(
            model, X, y,
            n_repeats=n_repeats,
            random_state=42,
            n_jobs=-1
        )
        
        importance_df = pd.DataFrame({
            'feature': X.columns,
            'importance_mean': perm_importance.importances_mean,
            'importance_std': perm_importance.importances_std
        })
        
        importance_df = importance_df.sort_values('importance_mean', ascending=False)
        importance_df = importance_df.reset_index(drop=True)
        
        return importance_df
    
    def get_linear_coefficients(self,
                               model,
                               feature_names: List[str]) -> pd.DataFrame:
        """
        Get coefficients from linear models.
        
        Args:
            model: Trained linear model
            feature_names: List of feature names
            
        Returns:
            DataFrame with coefficients
        """
        if not hasattr(model, 'coef_'):
            raise ValueError("Model does not have coefficients")
        
        coef_df = pd.DataFrame({
            'feature': feature_names,
            'coefficient': model.coef_,
            'abs_coefficient': np.abs(model.coef_)
        })
        
        # Add intercept
        if hasattr(model, 'intercept_'):
            intercept_row = pd.DataFrame({
                'feature': ['intercept'],
                'coefficient': [model.intercept_],
                'abs_coefficient': [np.abs(model.intercept_)]
            })
            coef_df = pd.concat([intercept_row, coef_df], ignore_index=True)
        
        coef_df = coef_df.sort_values('abs_coefficient', ascending=False)
        coef_df = coef_df.reset_index(drop=True)
        
        return coef_df
    
    def categorize_features(self, feature_names: List[str]) -> Dict[str, List[str]]:
        """
        Categorize features into groups.
        
        Args:
            feature_names: List of feature names
            
        Returns:
            Dictionary of feature categories
        """
        categories = {
            'vehicle_counts': [],
            'emissions': [],
            'ratios': [],
            'temporal': [],
            'lagged': [],
            'rolling': [],
            'other': []
        }
        
        for feature in feature_names:
            if any(vehicle in feature for vehicle in VEHICLE_CATEGORIES):
                if 'emission' in feature:
                    categories['emissions'].append(feature)
                elif 'ratio' in feature:
                    categories['ratios'].append(feature)
                else:
                    categories['vehicle_counts'].append(feature)
            elif 'lag' in feature:
                categories['lagged'].append(feature)
            elif 'rolling' in feature:
                categories['rolling'].append(feature)
            elif any(temp in feature for temp in ['hour', 'day', 'weekend', 'rush', 'month']):
                categories['temporal'].append(feature)
            else:
                categories['other'].append(feature)
        
        # Remove empty categories
        categories = {k: v for k, v in categories.items() if v}
        
        return categories
    
    def get_category_importance(self,
                               importance_df: pd.DataFrame) -> pd.DataFrame:
        """
        Aggregate feature importance by category.
        
        Args:
            importance_df: DataFrame with feature importance
            
        Returns:
            DataFrame with category importance
        """
        feature_categories = self.categorize_features(importance_df['feature'].tolist())
        
        category_importance = []
        for category, features in feature_categories.items():
            category_features = importance_df[importance_df['feature'].isin(features)]
            total_importance = category_features['importance'].sum()
            
            category_importance.append({
                'category': category,
                'importance': total_importance,
                'n_features': len(features)
            })
        
        category_df = pd.DataFrame(category_importance)
        category_df = category_df.sort_values('importance', ascending=False)
        category_df = category_df.reset_index(drop=True)
        
        # Normalize
        category_df['importance_normalized'] = (
            category_df['importance'] / category_df['importance'].sum()
        )
        
        return category_df
    
    def estimate_vehicle_contributions(self,
                                      model,
                                      X: pd.DataFrame,
                                      y_actual: pd.Series,
                                      feature_names: List[str]) -> Dict[str, float]:
        """
        Estimate contribution of each vehicle category to pollution.
        
        Args:
            model: Trained model
            X: Feature matrix
            y_actual: Actual pollution values
            feature_names: List of feature names
            
        Returns:
            Dictionary with vehicle contributions
        """
        logger.info("Estimating vehicle contributions...")
        
        # Full prediction
        y_pred_full = model.predict(X)
        
        contributions = {}
        
        for vehicle_type in VEHICLE_CATEGORIES:
            # Create modified feature matrix with vehicle type set to zero
            X_modified = X.copy()
            
            # Set all features related to this vehicle type to zero
            vehicle_features = [f for f in feature_names if vehicle_type in f]
            for feature in vehicle_features:
                if feature in X_modified.columns:
                    X_modified[feature] = 0
            
            # Predict without this vehicle type
            y_pred_without = model.predict(X_modified)
            
            # Contribution is the difference
            contribution = y_pred_full - y_pred_without
            
            # Average contribution
            avg_contribution = np.mean(contribution)
            
            # Percentage of actual pollution
            avg_actual = np.mean(y_actual)
            contribution_pct = (avg_contribution / avg_actual) * 100 if avg_actual > 0 else 0
            
            contributions[vehicle_type] = {
                'absolute_contribution': avg_contribution,
                'percentage_contribution': contribution_pct
            }
        
        return contributions
    
    def print_feature_importance(self,
                                importance_df: pd.DataFrame,
                                top_n: int = 20) -> None:
        """
        Print formatted feature importance.
        
        Args:
            importance_df: DataFrame with feature importance
            top_n: Number of top features to display
        """
        print("\n" + "="*80)
        print(f"TOP {top_n} MOST IMPORTANT FEATURES")
        print("="*80)
        
        top_features = importance_df.head(top_n)
        
        for idx, row in top_features.iterrows():
            importance_pct = row['importance_normalized'] * 100
            print(f"{idx+1:2d}. {row['feature']:40s} {importance_pct:6.2f}%")
        
        print("="*80 + "\n")
    
    def print_vehicle_contributions(self, contributions: Dict[str, Dict[str, float]]) -> None:
        """
        Print formatted vehicle contributions.
        
        Args:
            contributions: Dictionary with vehicle contributions
        """
        print("\n" + "="*80)
        print("VEHICLE CATEGORY CONTRIBUTIONS TO POLLUTION")
        print("="*80)
        
        total_pct = sum(v['percentage_contribution'] for v in contributions.values())
        
        for vehicle_type, contrib in contributions.items():
            abs_contrib = contrib['absolute_contribution']
            pct_contrib = contrib['percentage_contribution']
            
            print(f"{vehicle_type:20s}: {abs_contrib:8.2f} μg/m³  ({pct_contrib:5.1f}%)")
        
        print("-" * 80)
        print(f"{'Total':20s}: {'':<8s}           ({total_pct:5.1f}%)")
        print("="*80 + "\n")


def main():
    """
    Test explainability pipeline.
    """
    from src.data.data_generator import SyntheticDataGenerator
    from src.features.feature_engineering import FeatureEngineer
    from src.features.preprocessing import DataPreprocessor
    from src.models.trainer import ModelTrainer
    
    # Generate data
    print("Generating synthetic data...")
    generator = SyntheticDataGenerator()
    traffic_data, pollution_data = generator.generate_complete_dataset()
    
    # Test with PM2.5
    pollutant = 'PM2.5'
    
    # Create features
    engineer = FeatureEngineer()
    df = engineer.create_all_features(traffic_data, pollution_data, pollutant)
    X, y = engineer.prepare_features_and_target(df, pollutant)
    
    # Preprocess
    preprocessor = DataPreprocessor()
    X_train, X_test, y_train, y_test = preprocessor.prepare_train_test_data(X, y)
    
    # Train a Random Forest model
    trainer = ModelTrainer()
    model = trainer.train_single_model('random_forest', X_train, y_train, tune_hyperparameters=False)
    
    # Explain model
    explainer = ModelExplainer()
    
    # Feature importance
    importance_df = explainer.get_feature_importance(model, 'random_forest', X_train.columns.tolist())
    explainer.print_feature_importance(importance_df, top_n=15)
    
    # Category importance
    category_importance = explainer.get_category_importance(importance_df)
    print("\nFeature Category Importance:")
    print(category_importance.to_string(index=False))
    
    # Vehicle contributions
    contributions = explainer.estimate_vehicle_contributions(
        model, X_test, y_test, X_test.columns.tolist()
    )
    explainer.print_vehicle_contributions(contributions)


if __name__ == "__main__":
    main()
