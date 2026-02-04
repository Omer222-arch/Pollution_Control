"""
Data preprocessing and scaling for model training.
"""

import pandas as pd
import numpy as np
from typing import Tuple
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split, TimeSeriesSplit
from src.utils.config import TRAINING_CONFIG
from src.utils.helpers import setup_logging, save_model, load_model
from pathlib import Path

logger = setup_logging(__name__)


class DataPreprocessor:
    """
    Preprocess data for model training.
    """
    
    def __init__(self, config: dict = None):
        """
        Initialize preprocessor.
        
        Args:
            config: Training configuration dictionary
        """
        self.config = config or TRAINING_CONFIG
        self.scaler = StandardScaler()
        self.is_fitted = False
        
    def time_series_split(self,
                         X: pd.DataFrame,
                         y: pd.Series,
                         test_size: float = None) -> Tuple[pd.DataFrame, pd.DataFrame, 
                                                            pd.Series, pd.Series]:
        """
        Split data using time-aware strategy (no shuffling).
        
        Args:
            X: Feature matrix
            y: Target vector
            test_size: Proportion of data for testing
            
        Returns:
            Tuple of (X_train, X_test, y_train, y_test)
        """
        test_size = test_size or self.config['test_size']
        
        # Calculate split index
        n_samples = len(X)
        split_idx = int(n_samples * (1 - test_size))
        
        # Split data chronologically
        X_train = X.iloc[:split_idx]
        X_test = X.iloc[split_idx:]
        y_train = y.iloc[:split_idx]
        y_test = y.iloc[split_idx:]
        
        logger.info(f"Time-series split: Train={len(X_train)}, Test={len(X_test)}")
        logger.info(f"Train period: {X_train.index[0]} to {X_train.index[-1]}")
        logger.info(f"Test period: {X_test.index[0]} to {X_test.index[-1]}")
        
        return X_train, X_test, y_train, y_test
    
    def fit_scaler(self, X_train: pd.DataFrame) -> None:
        """
        Fit scaler on training data.
        
        Args:
            X_train: Training feature matrix
        """
        self.scaler.fit(X_train)
        self.is_fitted = True
        logger.info("Scaler fitted on training data")
        
    def transform(self, X: pd.DataFrame) -> pd.DataFrame:
        """
        Transform features using fitted scaler.
        
        Args:
            X: Feature matrix
            
        Returns:
            Scaled feature matrix
        """
        if not self.is_fitted:
            raise ValueError("Scaler not fitted. Call fit_scaler first.")
        
        X_scaled = self.scaler.transform(X)
        X_scaled = pd.DataFrame(X_scaled, columns=X.columns, index=X.index)
        
        return X_scaled
    
    def fit_transform(self, X: pd.DataFrame) -> pd.DataFrame:
        """
        Fit scaler and transform features.
        
        Args:
            X: Feature matrix
            
        Returns:
            Scaled feature matrix
        """
        self.fit_scaler(X)
        return self.transform(X)
    
    def prepare_train_test_data(self,
                               X: pd.DataFrame,
                               y: pd.Series,
                               scale: bool = True) -> Tuple[pd.DataFrame, pd.DataFrame,
                                                            pd.Series, pd.Series]:
        """
        Complete preprocessing pipeline: split and scale data.
        
        Args:
            X: Feature matrix
            y: Target vector
            scale: Whether to scale features
            
        Returns:
            Tuple of (X_train, X_test, y_train, y_test)
        """
        # Time-series split
        X_train, X_test, y_train, y_test = self.time_series_split(X, y)
        
        # Scale features if requested
        if scale:
            X_train = self.fit_transform(X_train)
            X_test = self.transform(X_test)
            logger.info("Features scaled using StandardScaler")
        
        return X_train, X_test, y_train, y_test
    
    def get_cv_splitter(self, n_splits: int = None):
        """
        Get time-series cross-validation splitter.
        
        Args:
            n_splits: Number of CV folds
            
        Returns:
            TimeSeriesSplit object
        """
        n_splits = n_splits or self.config['cv_folds']
        return TimeSeriesSplit(n_splits=n_splits)
    
    def save_scaler(self, filepath: Path) -> None:
        """
        Save fitted scaler to disk.
        
        Args:
            filepath: Path to save the scaler
        """
        if not self.is_fitted:
            raise ValueError("Scaler not fitted. Cannot save.")
        save_model(self.scaler, filepath)
        
    def load_scaler(self, filepath: Path) -> None:
        """
        Load fitted scaler from disk.
        
        Args:
            filepath: Path to the saved scaler
        """
        self.scaler = load_model(filepath)
        self.is_fitted = True


def check_data_quality(X: pd.DataFrame, y: pd.Series) -> dict:
    """
    Check data quality and return statistics.
    
    Args:
        X: Feature matrix
        y: Target vector
        
    Returns:
        Dictionary with data quality metrics
    """
    quality_report = {
        'n_samples': len(X),
        'n_features': len(X.columns),
        'missing_values_X': X.isnull().sum().sum(),
        'missing_values_y': y.isnull().sum(),
        'infinite_values_X': np.isinf(X.select_dtypes(include=[np.number])).sum().sum(),
        'infinite_values_y': np.isinf(y).sum() if np.issubdtype(y.dtype, np.number) else 0,
        'feature_names': list(X.columns),
        'target_name': y.name,
        'target_mean': y.mean(),
        'target_std': y.std(),
        'target_min': y.min(),
        'target_max': y.max()
    }
    
    return quality_report


def print_data_quality_report(quality_report: dict) -> None:
    """
    Print formatted data quality report.
    
    Args:
        quality_report: Dictionary from check_data_quality
    """
    print("\n" + "="*70)
    print("DATA QUALITY REPORT")
    print("="*70)
    
    print(f"\nDataset Size:")
    print(f"  Samples: {quality_report['n_samples']}")
    print(f"  Features: {quality_report['n_features']}")
    
    print(f"\nData Quality:")
    print(f"  Missing values (X): {quality_report['missing_values_X']}")
    print(f"  Missing values (y): {quality_report['missing_values_y']}")
    print(f"  Infinite values (X): {quality_report['infinite_values_X']}")
    print(f"  Infinite values (y): {quality_report['infinite_values_y']}")
    
    print(f"\nTarget Variable: {quality_report['target_name']}")
    print(f"  Mean: {quality_report['target_mean']:.2f}")
    print(f"  Std: {quality_report['target_std']:.2f}")
    print(f"  Min: {quality_report['target_min']:.2f}")
    print(f"  Max: {quality_report['target_max']:.2f}")
    
    print("\n" + "="*70 + "\n")


def main():
    """
    Test preprocessing pipeline.
    """
    from src.data.data_generator import SyntheticDataGenerator
    from src.features.feature_engineering import FeatureEngineer
    from src.utils.config import POLLUTANTS
    
    # Generate data
    generator = SyntheticDataGenerator()
    traffic_data, pollution_data = generator.generate_complete_dataset()
    
    # Create features
    engineer = FeatureEngineer()
    pollutant = POLLUTANTS[0]  # Test with PM2.5
    
    df = engineer.create_all_features(traffic_data, pollution_data, pollutant)
    X, y = engineer.prepare_features_and_target(df, pollutant)
    
    # Check data quality
    quality_report = check_data_quality(X, y)
    print_data_quality_report(quality_report)
    
    # Preprocess data
    preprocessor = DataPreprocessor()
    X_train, X_test, y_train, y_test = preprocessor.prepare_train_test_data(X, y)
    
    print(f"Training set: X={X_train.shape}, y={y_train.shape}")
    print(f"Test set: X={X_test.shape}, y={y_test.shape}")
    
    print("\nScaled feature statistics (training set):")
    print(X_train.describe())


if __name__ == "__main__":
    main()
