"""
Model evaluation and performance metrics.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from scipy import stats

from src.utils.config import MODEL_TYPES, RESULTS_DIR
from src.utils.helpers import setup_logging, save_dataframe, save_json

logger = setup_logging(__name__)


class ModelEvaluator:
    """
    Evaluate model performance and generate metrics.
    """
    
    def __init__(self):
        """Initialize evaluator."""
        self.results = {}
        
    def calculate_metrics(self,
                         y_true: np.ndarray,
                         y_pred: np.ndarray) -> Dict[str, float]:
        """
        Calculate regression metrics.
        
        Args:
            y_true: True values
            y_pred: Predicted values
            
        Returns:
            Dictionary of metrics
        """
        metrics = {
            'RMSE': np.sqrt(mean_squared_error(y_true, y_pred)),
            'MAE': mean_absolute_error(y_true, y_pred),
            'R2': r2_score(y_true, y_pred),
            'MAPE': self._calculate_mape(y_true, y_pred),
            'Mean_Error': np.mean(y_pred - y_true),
            'Std_Error': np.std(y_pred - y_true)
        }
        
        return metrics
    
    def _calculate_mape(self, y_true: np.ndarray, y_pred: np.ndarray) -> float:
        """
        Calculate Mean Absolute Percentage Error.
        
        Args:
            y_true: True values
            y_pred: Predicted values
            
        Returns:
            MAPE value
        """
        # Avoid division by zero
        mask = y_true != 0
        if mask.sum() == 0:
            return np.nan
        
        mape = np.mean(np.abs((y_true[mask] - y_pred[mask]) / y_true[mask])) * 100
        return mape
    
    def evaluate_model(self,
                      model_type: str,
                      pollutant: str,
                      y_train: np.ndarray,
                      y_train_pred: np.ndarray,
                      y_test: np.ndarray,
                      y_test_pred: np.ndarray) -> Dict[str, Dict[str, float]]:
        """
        Evaluate a single model on train and test sets.
        
        Args:
            model_type: Model type name
            pollutant: Pollutant name
            y_train: True training values
            y_train_pred: Predicted training values
            y_test: True test values
            y_test_pred: Predicted test values
            
        Returns:
            Dictionary with train and test metrics
        """
        train_metrics = self.calculate_metrics(y_train, y_train_pred)
        test_metrics = self.calculate_metrics(y_test, y_test_pred)
        
        results = {
            'train': train_metrics,
            'test': test_metrics
        }
        
        # Store results
        if pollutant not in self.results:
            self.results[pollutant] = {}
        self.results[pollutant][model_type] = results
        
        logger.info(f"{model_type} - {pollutant}:")
        logger.info(f"  Train R²: {train_metrics['R2']:.4f}, RMSE: {train_metrics['RMSE']:.4f}")
        logger.info(f"  Test R²: {test_metrics['R2']:.4f}, RMSE: {test_metrics['RMSE']:.4f}")
        
        return results
    
    def create_comparison_table(self, pollutant: str) -> pd.DataFrame:
        """
        Create comparison table for all models of a pollutant.
        
        Args:
            pollutant: Pollutant name
            
        Returns:
            DataFrame with model comparison
        """
        if pollutant not in self.results:
            raise ValueError(f"No results found for {pollutant}")
        
        data = []
        for model_type, metrics in self.results[pollutant].items():
            row = {
                'Model': model_type,
                'Train_R2': metrics['train']['R2'],
                'Test_R2': metrics['test']['R2'],
                'Train_RMSE': metrics['train']['RMSE'],
                'Test_RMSE': metrics['test']['RMSE'],
                'Train_MAE': metrics['train']['MAE'],
                'Test_MAE': metrics['test']['MAE'],
                'Test_MAPE': metrics['test']['MAPE']
            }
            data.append(row)
        
        df = pd.DataFrame(data)
        df = df.sort_values('Test_R2', ascending=False)
        df = df.reset_index(drop=True)
        
        return df
    
    def get_best_model(self, pollutant: str, metric: str = 'R2') -> Tuple[str, float]:
        """
        Get the best performing model for a pollutant.
        
        Args:
            pollutant: Pollutant name
            metric: Metric to use for comparison (R2, RMSE, MAE)
            
        Returns:
            Tuple of (model_type, metric_value)
        """
        if pollutant not in self.results:
            raise ValueError(f"No results found for {pollutant}")
        
        best_model = None
        best_value = -np.inf if metric == 'R2' else np.inf
        
        for model_type, metrics in self.results[pollutant].items():
            value = metrics['test'][metric]
            
            if metric == 'R2':
                if value > best_value:
                    best_value = value
                    best_model = model_type
            else:  # RMSE, MAE (lower is better)
                if value < best_value:
                    best_value = value
                    best_model = model_type
        
        return best_model, best_value
    
    def analyze_residuals(self,
                         y_true: np.ndarray,
                         y_pred: np.ndarray) -> Dict[str, float]:
        """
        Analyze residuals for model diagnostics.
        
        Args:
            y_true: True values
            y_pred: Predicted values
            
        Returns:
            Dictionary with residual statistics
        """
        residuals = y_true - y_pred
        
        # Normality test (Shapiro-Wilk)
        if len(residuals) >= 3:
            shapiro_stat, shapiro_p = stats.shapiro(residuals[:5000])  # Limit for performance
        else:
            shapiro_stat, shapiro_p = np.nan, np.nan
        
        analysis = {
            'mean_residual': np.mean(residuals),
            'std_residual': np.std(residuals),
            'min_residual': np.min(residuals),
            'max_residual': np.max(residuals),
            'shapiro_statistic': shapiro_stat,
            'shapiro_pvalue': shapiro_p,
            'residuals_normal': shapiro_p > 0.05 if not np.isnan(shapiro_p) else None
        }
        
        return analysis
    
    def save_results(self, pollutant: str) -> None:
        """
        Save evaluation results to disk.
        
        Args:
            pollutant: Pollutant name
        """
        if pollutant not in self.results:
            logger.warning(f"No results to save for {pollutant}")
            return
        
        pollutant_dir = RESULTS_DIR / pollutant
        pollutant_dir.mkdir(parents=True, exist_ok=True)
        
        # Save comparison table
        comparison_df = self.create_comparison_table(pollutant)
        table_path = pollutant_dir / "model_comparison.csv"
        save_dataframe(comparison_df, table_path)
        
        # Save detailed results as JSON
        results_path = pollutant_dir / "detailed_results.json"
        save_json(self.results[pollutant], results_path)
        
        logger.info(f"Results for {pollutant} saved to {pollutant_dir}")
    
    def print_summary(self, pollutant: str) -> None:
        """
        Print formatted summary of results.
        
        Args:
            pollutant: Pollutant name
        """
        if pollutant not in self.results:
            print(f"No results found for {pollutant}")
            return
        
        print("\n" + "="*80)
        print(f"MODEL EVALUATION SUMMARY - {pollutant}")
        print("="*80)
        
        comparison_df = self.create_comparison_table(pollutant)
        print("\n" + comparison_df.to_string(index=False))
        
        best_model, best_r2 = self.get_best_model(pollutant, 'R2')
        print(f"\n{'='*80}")
        print(f"Best Model (by R²): {best_model} (R² = {best_r2:.4f})")
        print("="*80 + "\n")


def create_predictions_dataframe(y_true: pd.Series,
                                 predictions: Dict[str, np.ndarray],
                                 model_types: List[str]) -> pd.DataFrame:
    """
    Create DataFrame with actual values and predictions from all models.
    
    Args:
        y_true: True values
        predictions: Dictionary of predictions by model type
        model_types: List of model types
        
    Returns:
        DataFrame with actual and predicted values
    """
    df = pd.DataFrame({
        'actual': y_true.values
    }, index=y_true.index)
    
    for model_type in model_types:
        if model_type in predictions:
            df[f'pred_{model_type}'] = predictions[model_type]
    
    return df


def main():
    """
    Test evaluation pipeline.
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
    
    # Train models
    trainer = ModelTrainer()
    models = trainer.train_all_models(X_train, y_train, pollutant, tune_hyperparameters=False)
    
    # Evaluate models
    evaluator = ModelEvaluator()
    
    for model_type in MODEL_TYPES:
        if models[model_type] is not None:
            y_train_pred = models[model_type].predict(X_train)
            y_test_pred = models[model_type].predict(X_test)
            
            evaluator.evaluate_model(
                model_type, pollutant,
                y_train.values, y_train_pred,
                y_test.values, y_test_pred
            )
    
    # Print summary
    evaluator.print_summary(pollutant)
    
    # Save results
    evaluator.save_results(pollutant)


if __name__ == "__main__":
    main()
