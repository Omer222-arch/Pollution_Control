"""
Feature engineering for pollution estimation model.
"""

import pandas as pd
import numpy as np
from typing import Tuple, List
from src.utils.config import (
    FEATURE_CONFIG, VEHICLE_CATEGORIES, POLLUTANTS
)
from src.features.emission_factors import create_emission_features
from src.utils.helpers import setup_logging, get_time_features

logger = setup_logging(__name__)


class FeatureEngineer:
    """
    Create features for pollution estimation models.
    """
    
    def __init__(self, config: dict = None):
        """
        Initialize feature engineer.
        
        Args:
            config: Feature configuration dictionary
        """
        self.config = config or FEATURE_CONFIG
        
    def create_temporal_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Create temporal features from timestamp.
        
        Args:
            df: DataFrame with 'timestamp' column
            
        Returns:
            DataFrame with temporal features added
        """
        if 'timestamp' not in df.columns:
            logger.warning("No 'timestamp' column found. Skipping temporal features.")
            return df
        
        # Ensure timestamp is datetime
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        # Extract temporal features
        time_features = get_time_features(df['timestamp'])
        
        # Concatenate with original dataframe
        result = pd.concat([df, time_features], axis=1)
        
        logger.info(f"Created {len(time_features.columns)} temporal features")
        return result
    
    def create_lagged_features(self, 
                              df: pd.DataFrame,
                              pollutant: str) -> pd.DataFrame:
        """
        Create lagged pollution features.
        
        Args:
            df: DataFrame with pollutant column
            pollutant: Pollutant name
            
        Returns:
            DataFrame with lagged features added
        """
        result = df.copy()
        
        if pollutant not in df.columns:
            logger.warning(f"Pollutant {pollutant} not found. Skipping lagged features.")
            return result
        
        for lag in self.config['lag_hours']:
            col_name = f'{pollutant}_lag_{lag}h'
            result[col_name] = df[pollutant].shift(lag)
        
        logger.info(f"Created {len(self.config['lag_hours'])} lagged features for {pollutant}")
        return result
    
    def create_rolling_features(self,
                               df: pd.DataFrame,
                               pollutant: str) -> pd.DataFrame:
        """
        Create rolling average features.
        
        Args:
            df: DataFrame with pollutant column
            pollutant: Pollutant name
            
        Returns:
            DataFrame with rolling features added
        """
        result = df.copy()
        
        if pollutant not in df.columns:
            logger.warning(f"Pollutant {pollutant} not found. Skipping rolling features.")
            return result
        
        for window in self.config['rolling_windows']:
            col_name = f'{pollutant}_rolling_{window}h'
            result[col_name] = df[pollutant].rolling(window=window, min_periods=1).mean()
        
        logger.info(f"Created {len(self.config['rolling_windows'])} rolling features for {pollutant}")
        return result
    
    def create_all_features(self,
                           traffic_data: pd.DataFrame,
                           pollution_data: pd.DataFrame,
                           target_pollutant: str) -> pd.DataFrame:
        """
        Create all features for a specific pollutant.
        
        Args:
            traffic_data: DataFrame with traffic counts and timestamp
            pollution_data: DataFrame with pollution measurements and timestamp
            target_pollutant: Target pollutant to predict
            
        Returns:
            DataFrame with all features
        """
        logger.info(f"Creating features for {target_pollutant}...")
        
        # Merge traffic and pollution data on timestamp
        df = pd.merge(traffic_data, pollution_data, on='timestamp', how='inner')
        
        # Set timestamp as index
        df.set_index('timestamp', inplace=True)
        
        # 1. Create emission-based features
        emission_features = create_emission_features(df[VEHICLE_CATEGORIES])
        df = pd.concat([df, emission_features], axis=1)
        logger.info(f"Created {len(emission_features.columns)} emission-based features")
        
        # 2. Create temporal features
        if self.config['include_temporal_features']:
            df = df.reset_index()
            # Ensure timestamp is datetime
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df = self.create_temporal_features(df)
            # Convert to DatetimeIndex before setting as index
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df.set_index('timestamp', inplace=True)
        
        # 3. Create lagged features for target pollutant
        if self.config['include_lagged_features']:
            df = self.create_lagged_features(df, target_pollutant)
        
        # 4. Create rolling features for target pollutant
        if self.config['include_rolling_features']:
            df = self.create_rolling_features(df, target_pollutant)
        
        # Drop rows with NaN values (from lagging/rolling)
        initial_rows = len(df)
        df = df.dropna()
        dropped_rows = initial_rows - len(df)
        
        if dropped_rows > 0:
            logger.info(f"Dropped {dropped_rows} rows with NaN values")
        
        logger.info(f"Final feature set: {len(df.columns)} columns, {len(df)} rows")
        
        return df
    
    def get_feature_names(self, 
                         df: pd.DataFrame,
                         target_pollutant: str) -> List[str]:
        """
        Get list of feature column names (excluding target and other pollutants).
        
        Args:
            df: DataFrame with all features
            target_pollutant: Target pollutant
            
        Returns:
            List of feature column names
        """
        # Exclude target pollutant and other pollutants from features
        exclude_cols = POLLUTANTS.copy()
        
        # Include lagged and rolling features of target pollutant
        feature_cols = [col for col in df.columns 
                       if col not in exclude_cols or target_pollutant in col]
        
        # Remove the target itself (not lagged/rolling)
        if target_pollutant in feature_cols:
            feature_cols.remove(target_pollutant)
        
        return feature_cols
    
    def prepare_features_and_target(self,
                                   df: pd.DataFrame,
                                   target_pollutant: str) -> Tuple[pd.DataFrame, pd.Series]:
        """
        Prepare feature matrix X and target vector y.
        
        Args:
            df: DataFrame with all features and target
            target_pollutant: Target pollutant to predict
            
        Returns:
            Tuple of (X, y)
        """
        feature_cols = self.get_feature_names(df, target_pollutant)
        
        X = df[feature_cols]
        y = df[target_pollutant]
        
        logger.info(f"Prepared features: X shape = {X.shape}, y shape = {y.shape}")
        logger.info(f"Feature columns: {list(X.columns)}")
        
        return X, y


def main():
    """
    Test feature engineering pipeline.
    """
    from src.data.data_generator import SyntheticDataGenerator
    
    # Generate synthetic data
    generator = SyntheticDataGenerator()
    traffic_data, pollution_data = generator.generate_complete_dataset()
    
    # Create features
    engineer = FeatureEngineer()
    
    for pollutant in POLLUTANTS:
        print(f"\n{'='*70}")
        print(f"Creating features for {pollutant}")
        print('='*70)
        
        df = engineer.create_all_features(traffic_data, pollution_data, pollutant)
        X, y = engineer.prepare_features_and_target(df, pollutant)
        
        print(f"\nFeature matrix shape: {X.shape}")
        print(f"Target vector shape: {y.shape}")
        print(f"\nFeature columns ({len(X.columns)}):")
        for i, col in enumerate(X.columns, 1):
            print(f"  {i}. {col}")


if __name__ == "__main__":
    main()
