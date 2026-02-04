"""
Model training pipeline for pollution estimation.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Any
from sklearn.linear_model import LinearRegression, Ridge, Lasso
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import GridSearchCV
from pathlib import Path

from src.utils.config import (
    MODEL_TYPES, POLLUTANTS, TRAINING_CONFIG, SAVED_MODELS_DIR
)
from src.utils.helpers import setup_logging, save_model, load_model, save_json
from src.features.preprocessing import DataPreprocessor

logger = setup_logging(__name__)


class ModelTrainer:
    """
    Train and manage multiple regression models for pollution estimation.
    """
    
    def __init__(self, config: dict = None):
        """
        Initialize model trainer.
        
        Args:
            config: Training configuration dictionary
        """
        self.config = config or TRAINING_CONFIG
        self.models = {}
        self.best_params = {}
        self.preprocessor = DataPreprocessor(config)
        
    def get_model(self, model_type: str) -> Any:
        """
        Get model instance by type.
        
        Args:
            model_type: Model type name
            
        Returns:
            Model instance
        """
        models_map = {
            'linear_regression': LinearRegression(),
            'ridge_regression': Ridge(random_state=self.config['random_state']),
            'lasso_regression': Lasso(random_state=self.config['random_state'], max_iter=5000),
            'decision_tree': DecisionTreeRegressor(random_state=self.config['random_state']),
            'random_forest': RandomForestRegressor(random_state=self.config['random_state'], n_jobs=-1)
        }
        
        if model_type not in models_map:
            raise ValueError(f"Unknown model type: {model_type}")
        
        return models_map[model_type]
    
    def get_param_grid(self, model_type: str) -> Dict:
        """
        Get hyperparameter grid for model tuning.
        
        Args:
            model_type: Model type name
            
        Returns:
            Parameter grid dictionary
        """
        param_grids = {
            'linear_regression': {},  # No hyperparameters to tune
            'ridge_regression': {
                'alpha': self.config['ridge_alphas']
            },
            'lasso_regression': {
                'alpha': self.config['lasso_alphas']
            },
            'decision_tree': {
                'max_depth': self.config['dt_max_depths'],
                'min_samples_split': [2, 5, 10],
                'min_samples_leaf': [1, 2, 4]
            },
            'random_forest': {
                'n_estimators': self.config['rf_n_estimators'],
                'max_depth': self.config['rf_max_depths'],
                'min_samples_split': [2, 5],
                'min_samples_leaf': [1, 2]
            }
        }
        
        return param_grids.get(model_type, {})
    
    def train_single_model(self,
                          model_type: str,
                          X_train: pd.DataFrame,
                          y_train: pd.Series,
                          tune_hyperparameters: bool = True) -> Any:
        """
        Train a single model with optional hyperparameter tuning.
        
        Args:
            model_type: Model type name
            X_train: Training features
            y_train: Training target
            tune_hyperparameters: Whether to perform hyperparameter tuning
            
        Returns:
            Trained model
        """
        logger.info(f"Training {model_type}...")
        
        model = self.get_model(model_type)
        param_grid = self.get_param_grid(model_type)
        
        # Perform hyperparameter tuning if grid is not empty
        if tune_hyperparameters and param_grid:
            cv_splitter = self.preprocessor.get_cv_splitter()
            
            grid_search = GridSearchCV(
                model,
                param_grid,
                cv=cv_splitter,
                scoring='neg_mean_squared_error',
                n_jobs=-1,
                verbose=0
            )
            
            grid_search.fit(X_train, y_train)
            model = grid_search.best_estimator_
            best_params = grid_search.best_params_
            
            logger.info(f"Best parameters for {model_type}: {best_params}")
            self.best_params[model_type] = best_params
        else:
            model.fit(X_train, y_train)
            logger.info(f"{model_type} trained without hyperparameter tuning")
        
        return model
    
    def train_all_models(self,
                        X_train: pd.DataFrame,
                        y_train: pd.Series,
                        pollutant: str,
                        tune_hyperparameters: bool = True) -> Dict[str, Any]:
        """
        Train all model types for a specific pollutant.
        
        Args:
            X_train: Training features
            y_train: Training target
            pollutant: Pollutant name
            tune_hyperparameters: Whether to perform hyperparameter tuning
            
        Returns:
            Dictionary of trained models
        """
        logger.info(f"\n{'='*70}")
        logger.info(f"Training models for {pollutant}")
        logger.info(f"{'='*70}")
        
        models = {}
        
        for model_type in MODEL_TYPES:
            try:
                model = self.train_single_model(
                    model_type, X_train, y_train, tune_hyperparameters
                )
                models[model_type] = model
                logger.info(f"✓ {model_type} trained successfully")
            except Exception as e:
                logger.error(f"✗ Error training {model_type}: {str(e)}")
                models[model_type] = None
        
        self.models[pollutant] = models
        return models
    
    def save_models(self, pollutant: str) -> None:
        """
        Save trained models for a pollutant.
        
        Args:
            pollutant: Pollutant name
        """
        if pollutant not in self.models:
            logger.warning(f"No models found for {pollutant}")
            return
        
        pollutant_dir = SAVED_MODELS_DIR / pollutant
        pollutant_dir.mkdir(parents=True, exist_ok=True)
        
        for model_type, model in self.models[pollutant].items():
            if model is not None:
                model_path = pollutant_dir / f"{model_type}.pkl"
                save_model(model, model_path)
        
        # Save best parameters
        if pollutant in self.best_params or self.best_params:
            params_path = pollutant_dir / "best_params.json"
            save_json(self.best_params, params_path)
        
        logger.info(f"Models for {pollutant} saved to {pollutant_dir}")
    
    def load_models(self, pollutant: str) -> Dict[str, Any]:
        """
        Load trained models for a pollutant.
        
        Args:
            pollutant: Pollutant name
            
        Returns:
            Dictionary of loaded models
        """
        pollutant_dir = SAVED_MODELS_DIR / pollutant
        
        if not pollutant_dir.exists():
            raise FileNotFoundError(f"No saved models found for {pollutant}")
        
        models = {}
        for model_type in MODEL_TYPES:
            model_path = pollutant_dir / f"{model_type}.pkl"
            if model_path.exists():
                models[model_type] = load_model(model_path)
            else:
                logger.warning(f"Model file not found: {model_path}")
        
        self.models[pollutant] = models
        logger.info(f"Loaded {len(models)} models for {pollutant}")
        
        return models
    
    def predict(self,
               model_type: str,
               pollutant: str,
               X: pd.DataFrame) -> np.ndarray:
        """
        Make predictions using a trained model.
        
        Args:
            model_type: Model type name
            pollutant: Pollutant name
            X: Feature matrix
            
        Returns:
            Predictions array
        """
        if pollutant not in self.models:
            raise ValueError(f"No models trained for {pollutant}")
        
        if model_type not in self.models[pollutant]:
            raise ValueError(f"Model {model_type} not found for {pollutant}")
        
        model = self.models[pollutant][model_type]
        predictions = model.predict(X)
        
        return predictions
    
    def get_feature_importance(self,
                              model_type: str,
                              pollutant: str,
                              feature_names: List[str]) -> pd.DataFrame:
        """
        Extract feature importance from trained model.
        
        Args:
            model_type: Model type name
            pollutant: Pollutant name
            feature_names: List of feature names
            
        Returns:
            DataFrame with feature importance
        """
        if pollutant not in self.models:
            raise ValueError(f"No models trained for {pollutant}")
        
        model = self.models[pollutant][model_type]
        
        if model is None:
            raise ValueError(f"Model {model_type} is None for {pollutant}")
        
        # Extract importance based on model type
        if model_type in ['linear_regression', 'ridge_regression', 'lasso_regression']:
            # Use absolute coefficients as importance
            importance = np.abs(model.coef_)
            importance_type = 'Absolute Coefficient'
        elif model_type in ['decision_tree', 'random_forest']:
            # Use built-in feature importance
            importance = model.feature_importances_
            importance_type = 'Feature Importance'
        else:
            raise ValueError(f"Feature importance not available for {model_type}")
        
        # Create DataFrame
        importance_df = pd.DataFrame({
            'feature': feature_names,
            'importance': importance,
            'importance_type': importance_type
        })
        
        # Sort by importance
        importance_df = importance_df.sort_values('importance', ascending=False)
        importance_df = importance_df.reset_index(drop=True)
        
        return importance_df


def main():
    """
    Test model training pipeline.
    """
    from src.data.data_generator import SyntheticDataGenerator
    from src.features.feature_engineering import FeatureEngineer
    from src.features.preprocessing import DataPreprocessor
    
    # Generate data
    print("Generating synthetic data...")
    generator = SyntheticDataGenerator()
    traffic_data, pollution_data = generator.generate_complete_dataset()
    
    # Test with one pollutant
    pollutant = 'PM2.5'
    print(f"\nTesting model training for {pollutant}...")
    
    # Create features
    engineer = FeatureEngineer()
    df = engineer.create_all_features(traffic_data, pollution_data, pollutant)
    X, y = engineer.prepare_features_and_target(df, pollutant)
    
    # Preprocess
    preprocessor = DataPreprocessor()
    X_train, X_test, y_train, y_test = preprocessor.prepare_train_test_data(X, y)
    
    # Train models
    trainer = ModelTrainer()
    models = trainer.train_all_models(X_train, y_train, pollutant, tune_hyperparameters=False)
    
    print(f"\nTrained {len(models)} models:")
    for model_type, model in models.items():
        if model is not None:
            print(f"  ✓ {model_type}")
    
    # Save models
    trainer.save_models(pollutant)
    print(f"\nModels saved to {SAVED_MODELS_DIR / pollutant}")


if __name__ == "__main__":
    main()
