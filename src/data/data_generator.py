"""
Generate synthetic traffic and air quality data for model training and testing.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Tuple
from src.utils.config import (
    SYNTHETIC_DATA_CONFIG, VEHICLE_CATEGORIES, POLLUTANTS,
    EMISSION_FACTORS, AVERAGE_TRIP_DISTANCE, SYNTHETIC_DATA_DIR
)
from src.features.emission_factors import EmissionCalculator
from src.utils.helpers import setup_logging, save_dataframe

logger = setup_logging(__name__)


class SyntheticDataGenerator:
    """
    Generate realistic synthetic traffic and air quality data.
    """
    
    def __init__(self, config: dict = None):
        """
        Initialize data generator.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config or SYNTHETIC_DATA_CONFIG
        self.emission_calculator = EmissionCalculator()
        np.random.seed(42)  # For reproducibility
        
    def generate_timestamps(self) -> pd.DatetimeIndex:
        """
        Generate timestamp index.
        
        Returns:
            DatetimeIndex with hourly timestamps
        """
        start_date = pd.to_datetime(self.config['start_date'])
        n_hours = self.config['n_days'] * 24
        timestamps = pd.date_range(
            start=start_date,
            periods=n_hours,
            freq=self.config['time_resolution']
        )
        return timestamps
    
    def generate_traffic_pattern(self, timestamps: pd.DatetimeIndex) -> pd.DataFrame:
        """
        Generate realistic traffic patterns with daily and weekly cycles.
        
        Args:
            timestamps: DatetimeIndex
            
        Returns:
            DataFrame with vehicle counts
        """
        n_hours = len(timestamps)
        traffic_data = pd.DataFrame(index=timestamps)
        
        # Extract time features
        hours = timestamps.hour
        is_weekend = timestamps.dayofweek >= 5
        
        for vehicle_type in VEHICLE_CATEGORIES:
            base_count = self.config['base_traffic'][vehicle_type]
            rush_multiplier = self.config['rush_hour_multiplier'][vehicle_type]
            
            # Initialize with base traffic
            counts = np.full(n_hours, base_count, dtype=float)
            
            # Apply daily pattern (sinusoidal with peaks at rush hours)
            daily_pattern = 1 + 0.3 * np.sin(2 * np.pi * (hours - 6) / 24)
            counts *= daily_pattern
            
            # Apply rush hour multipliers
            morning_rush = (hours >= self.config['rush_hour_morning'][0]) & \
                          (hours < self.config['rush_hour_morning'][1])
            evening_rush = (hours >= self.config['rush_hour_evening'][0]) & \
                          (hours < self.config['rush_hour_evening'][1])
            
            counts[morning_rush | evening_rush] *= rush_multiplier
            
            # Reduce traffic on weekends
            counts[is_weekend] *= self.config['weekend_reduction_factor']
            
            # Add random noise (±15%)
            noise = np.random.normal(1, self.config['noise_std'], n_hours)
            counts *= noise
            
            # Add seasonal variation
            day_of_year = timestamps.dayofyear
            seasonal = 1 + self.config['seasonal_variation'] * np.sin(
                2 * np.pi * day_of_year / 365
            )
            counts *= seasonal
            
            # Ensure non-negative counts
            counts = np.maximum(counts, 0)
            
            # Round to integers
            traffic_data[vehicle_type] = np.round(counts).astype(int)
        
        return traffic_data
    
    def generate_pollution_from_traffic(self, 
                                       traffic_data: pd.DataFrame) -> pd.DataFrame:
        """
        Generate air quality data based on traffic emissions.
        
        Args:
            traffic_data: DataFrame with vehicle counts
            
        Returns:
            DataFrame with pollutant concentrations
        """
        pollution_data = pd.DataFrame(index=traffic_data.index)
        
        for pollutant in POLLUTANTS:
            # Calculate emissions from traffic (grams)
            emissions = self.emission_calculator.calculate_total_emissions(
                traffic_data, pollutant
            )
            
            # Convert emissions to concentration (simplified dispersion model)
            # Assume emissions disperse in a volume of air
            # This is a simplified model: concentration ∝ emissions
            
            # Normalization factor to get realistic concentration ranges
            # These are calibrated to produce typical urban pollution levels
            normalization_factors = {
                'PM2.5': 0.002,   # μg/m³ per gram of emissions
                'PM10': 0.003,
                'NO2': 0.001,
                'CO': 0.05
            }
            
            concentration = emissions * normalization_factors[pollutant]
            
            # Add background pollution
            background = self.config['background_pollution'][pollutant]
            concentration += background
            
            # Add meteorological variability (wind, temperature, etc.)
            n_hours = len(traffic_data)
            met_noise = np.random.normal(1, 0.2, n_hours)  # ±20% variability
            concentration *= met_noise
            
            # Add temporal autocorrelation (pollution persists)
            # Use exponential smoothing
            alpha = 0.3
            smoothed = np.zeros(n_hours)
            smoothed[0] = concentration.iloc[0]
            for i in range(1, n_hours):
                smoothed[i] = alpha * concentration.iloc[i] + (1 - alpha) * smoothed[i-1]
            
            concentration = pd.Series(smoothed, index=traffic_data.index)
            
            # Ensure non-negative concentrations
            concentration = np.maximum(concentration, 0)
            
            pollution_data[pollutant] = concentration
        
        return pollution_data
    
    def generate_complete_dataset(self) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Generate complete synthetic dataset with traffic and pollution data.
        
        Returns:
            Tuple of (traffic_data, pollution_data)
        """
        logger.info("Generating synthetic data...")
        
        # Generate timestamps
        timestamps = self.generate_timestamps()
        logger.info(f"Generated {len(timestamps)} hourly timestamps")
        
        # Generate traffic data
        traffic_data = self.generate_traffic_pattern(timestamps)
        logger.info(f"Generated traffic data with shape {traffic_data.shape}")
        
        # Generate pollution data
        pollution_data = self.generate_pollution_from_traffic(traffic_data)
        logger.info(f"Generated pollution data with shape {pollution_data.shape}")
        
        # Add timestamp as a column
        traffic_data['timestamp'] = timestamps
        pollution_data['timestamp'] = timestamps
        
        return traffic_data, pollution_data
    
    def save_synthetic_data(self, 
                           traffic_data: pd.DataFrame,
                           pollution_data: pd.DataFrame) -> None:
        """
        Save synthetic data to CSV files.
        
        Args:
            traffic_data: Traffic DataFrame
            pollution_data: Pollution DataFrame
        """
        traffic_path = SYNTHETIC_DATA_DIR / "synthetic_traffic_data.csv"
        pollution_path = SYNTHETIC_DATA_DIR / "synthetic_pollution_data.csv"
        
        save_dataframe(traffic_data, traffic_path)
        save_dataframe(pollution_data, pollution_path)
        
        logger.info(f"Synthetic data saved to {SYNTHETIC_DATA_DIR}")
    
    def generate_and_save(self) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Generate and save synthetic data.
        
        Returns:
            Tuple of (traffic_data, pollution_data)
        """
        traffic_data, pollution_data = self.generate_complete_dataset()
        self.save_synthetic_data(traffic_data, pollution_data)
        
        # Print summary statistics
        self._print_summary(traffic_data, pollution_data)
        
        return traffic_data, pollution_data
    
    def _print_summary(self, 
                      traffic_data: pd.DataFrame,
                      pollution_data: pd.DataFrame) -> None:
        """
        Print summary statistics of generated data.
        
        Args:
            traffic_data: Traffic DataFrame
            pollution_data: Pollution DataFrame
        """
        print("\n" + "="*70)
        print("SYNTHETIC DATA GENERATION SUMMARY")
        print("="*70)
        
        print(f"\nData period: {self.config['n_days']} days")
        print(f"Time resolution: {self.config['time_resolution']}")
        print(f"Total records: {len(traffic_data)}")
        
        print("\n--- Traffic Data Summary ---")
        print(traffic_data[VEHICLE_CATEGORIES].describe())
        
        print("\n--- Pollution Data Summary (μg/m³) ---")
        print(pollution_data[POLLUTANTS].describe())
        
        print("\n" + "="*70 + "\n")


def main():
    """
    Main function to generate synthetic data.
    """
    generator = SyntheticDataGenerator()
    traffic_data, pollution_data = generator.generate_and_save()
    
    print("Synthetic data generation complete!")
    print(f"Files saved in: {SYNTHETIC_DATA_DIR}")


if __name__ == "__main__":
    main()
