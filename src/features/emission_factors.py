"""
Emission factors for different vehicle categories and pollutants.
Based on EPA MOVES model and EMEP/EEA air pollutant emission inventory guidebook.
"""

import pandas as pd
import numpy as np
from typing import Dict, List
from src.utils.config import EMISSION_FACTORS, VEHICLE_CATEGORIES, POLLUTANTS, AVERAGE_TRIP_DISTANCE


class EmissionCalculator:
    """
    Calculate emissions from vehicle counts using EPA emission factors.
    """
    
    def __init__(self, emission_factors: Dict = None, trip_distance: float = AVERAGE_TRIP_DISTANCE):
        """
        Initialize emission calculator.
        
        Args:
            emission_factors: Dictionary of emission factors (g/km)
            trip_distance: Average trip distance in km
        """
        self.emission_factors = emission_factors or EMISSION_FACTORS
        self.trip_distance = trip_distance
        
    def calculate_emissions(self, 
                           vehicle_counts: pd.DataFrame,
                           pollutant: str) -> pd.DataFrame:
        """
        Calculate emissions for a specific pollutant from vehicle counts.
        
        Args:
            vehicle_counts: DataFrame with vehicle count columns
            pollutant: Pollutant name (PM2.5, PM10, NO2, CO)
            
        Returns:
            DataFrame with emission columns for each vehicle category
        """
        emissions = pd.DataFrame(index=vehicle_counts.index)
        
        for vehicle_type in VEHICLE_CATEGORIES:
            if vehicle_type in vehicle_counts.columns:
                # Emission (g) = vehicle_count × emission_factor (g/km) × trip_distance (km)
                emission_factor = self.emission_factors[vehicle_type][pollutant]
                emissions[f'{vehicle_type}_emission_{pollutant}'] = (
                    vehicle_counts[vehicle_type] * emission_factor * self.trip_distance
                )
        
        return emissions
    
    def calculate_all_emissions(self, vehicle_counts: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate emissions for all pollutants from vehicle counts.
        
        Args:
            vehicle_counts: DataFrame with vehicle count columns
            
        Returns:
            DataFrame with all emission columns
        """
        all_emissions = vehicle_counts.copy()
        
        for pollutant in POLLUTANTS:
            emissions = self.calculate_emissions(vehicle_counts, pollutant)
            all_emissions = pd.concat([all_emissions, emissions], axis=1)
        
        return all_emissions
    
    def calculate_total_emissions(self, 
                                  vehicle_counts: pd.DataFrame,
                                  pollutant: str) -> pd.Series:
        """
        Calculate total emissions for a pollutant across all vehicle types.
        
        Args:
            vehicle_counts: DataFrame with vehicle count columns
            pollutant: Pollutant name
            
        Returns:
            Series with total emissions
        """
        emissions = self.calculate_emissions(vehicle_counts, pollutant)
        total = emissions.sum(axis=1)
        return total
    
    def get_emission_factor(self, vehicle_type: str, pollutant: str) -> float:
        """
        Get emission factor for a specific vehicle type and pollutant.
        
        Args:
            vehicle_type: Vehicle category
            pollutant: Pollutant name
            
        Returns:
            Emission factor in g/km
        """
        return self.emission_factors[vehicle_type][pollutant]
    
    def get_all_emission_factors(self) -> pd.DataFrame:
        """
        Get all emission factors as a DataFrame.
        
        Returns:
            DataFrame with emission factors
        """
        return pd.DataFrame(self.emission_factors).T


def create_emission_features(vehicle_counts: pd.DataFrame) -> pd.DataFrame:
    """
    Create emission-based features from vehicle counts.
    
    Args:
        vehicle_counts: DataFrame with vehicle count columns
        
    Returns:
        DataFrame with emission features
    """
    calculator = EmissionCalculator()
    
    # Calculate emissions for all pollutants
    features = calculator.calculate_all_emissions(vehicle_counts)
    
    # Add total emissions for each pollutant
    for pollutant in POLLUTANTS:
        features[f'total_emission_{pollutant}'] = calculator.calculate_total_emissions(
            vehicle_counts, pollutant
        )
    
    # Add aggregate traffic features
    features['total_traffic'] = vehicle_counts[VEHICLE_CATEGORIES].sum(axis=1)
    
    # Add vehicle ratios
    total_traffic = features['total_traffic'].replace(0, 1)  # Avoid division by zero
    for vehicle_type in VEHICLE_CATEGORIES:
        features[f'{vehicle_type}_ratio'] = vehicle_counts[vehicle_type] / total_traffic
    
    # Heavy vehicle ratio (buses + trucks)
    features['heavy_vehicle_ratio'] = (
        (vehicle_counts['buses'] + vehicle_counts['trucks']) / total_traffic
    )
    
    # Light vehicle ratio (two-wheelers + cars)
    features['light_vehicle_ratio'] = (
        (vehicle_counts['two_wheelers'] + vehicle_counts['cars']) / total_traffic
    )
    
    return features


def print_emission_factors_table():
    """
    Print a formatted table of emission factors.
    """
    calculator = EmissionCalculator()
    df = calculator.get_all_emission_factors()
    
    print("\n" + "="*70)
    print("EPA EMISSION FACTORS (g/km per vehicle)")
    print("="*70)
    print(df.to_string())
    print("="*70)
    print(f"\nAverage trip distance: {AVERAGE_TRIP_DISTANCE} km")
    print("\nNote: Emission factors are based on EPA MOVES model and")
    print("EMEP/EEA air pollutant emission inventory guidebook.")
    print("="*70 + "\n")


if __name__ == "__main__":
    # Display emission factors
    print_emission_factors_table()
    
    # Example usage
    sample_data = pd.DataFrame({
        'two_wheelers': [500, 1000, 750],
        'cars': [800, 1200, 900],
        'buses': [50, 75, 60],
        'trucks': [100, 150, 120]
    })
    
    calculator = EmissionCalculator()
    
    print("\nSample Vehicle Counts:")
    print(sample_data)
    
    print("\n\nCalculated PM2.5 Emissions (grams):")
    pm25_emissions = calculator.calculate_emissions(sample_data, 'PM2.5')
    print(pm25_emissions)
    
    print("\n\nTotal PM2.5 Emissions:")
    total_pm25 = calculator.calculate_total_emissions(sample_data, 'PM2.5')
    print(total_pm25)
