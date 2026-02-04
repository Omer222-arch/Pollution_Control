"""
Configuration settings for the vehicular pollution estimation model.
"""

import os
from pathlib import Path

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
SYNTHETIC_DATA_DIR = DATA_DIR / "synthetic"

MODELS_DIR = PROJECT_ROOT / "models"
SAVED_MODELS_DIR = MODELS_DIR / "saved_models"
RESULTS_DIR = MODELS_DIR / "results"

OUTPUTS_DIR = PROJECT_ROOT / "outputs"
FIGURES_DIR = OUTPUTS_DIR / "figures"
REPORTS_DIR = OUTPUTS_DIR / "reports"
CONTRIBUTIONS_DIR = OUTPUTS_DIR / "contributions"

# Ensure directories exist
for directory in [RAW_DATA_DIR, PROCESSED_DATA_DIR, SYNTHETIC_DATA_DIR,
                  SAVED_MODELS_DIR, RESULTS_DIR, FIGURES_DIR, 
                  REPORTS_DIR, CONTRIBUTIONS_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# Pollutants to model
POLLUTANTS = ['PM2.5', 'PM10', 'NO2', 'CO']

# Vehicle categories
VEHICLE_CATEGORIES = ['two_wheelers', 'cars', 'buses', 'trucks']

# Model types to train
MODEL_TYPES = [
    'linear_regression',
    'ridge_regression',
    'lasso_regression',
    'decision_tree',
    'random_forest'
]

# EPA Emission Factors (g/km per vehicle)
# Source: EPA MOVES model and EMEP/EEA air pollutant emission inventory guidebook
EMISSION_FACTORS = {
    'two_wheelers': {
        'PM2.5': 0.015,   # grams per km
        'PM10': 0.020,
        'NO2': 0.080,
        'CO': 2.500
    },
    'cars': {
        'PM2.5': 0.005,
        'PM10': 0.008,
        'NO2': 0.150,
        'CO': 1.200
    },
    'buses': {
        'PM2.5': 0.120,
        'PM10': 0.150,
        'NO2': 2.500,
        'CO': 3.000
    },
    'trucks': {
        'PM2.5': 0.180,
        'PM10': 0.220,
        'NO2': 3.500,
        'CO': 4.500
    }
}

# Synthetic data generation parameters
SYNTHETIC_DATA_CONFIG = {
    'n_days': 90,  # 3 months of data
    'start_date': '2024-01-01',
    'time_resolution': '1H',  # Hourly data
    
    # Traffic patterns
    'rush_hour_morning': (7, 10),  # 7 AM to 10 AM
    'rush_hour_evening': (17, 20),  # 5 PM to 8 PM
    'weekend_reduction_factor': 0.6,  # 40% less traffic on weekends
    
    # Base traffic volumes (vehicles per hour)
    'base_traffic': {
        'two_wheelers': 500,
        'cars': 800,
        'buses': 50,
        'trucks': 100
    },
    
    # Rush hour multipliers
    'rush_hour_multiplier': {
        'two_wheelers': 2.5,
        'cars': 2.0,
        'buses': 1.5,
        'trucks': 0.8  # Trucks avoid rush hours
    },
    
    # Background pollution levels (μg/m³)
    'background_pollution': {
        'PM2.5': 15.0,
        'PM10': 25.0,
        'NO2': 20.0,
        'CO': 500.0
    },
    
    # Noise parameters
    'noise_std': 0.15,  # 15% standard deviation for random noise
    'seasonal_variation': 0.1  # 10% seasonal variation
}

# Average trip distance (km) - used to convert vehicle counts to emissions
AVERAGE_TRIP_DISTANCE = 5.0  # km

# Feature engineering parameters
FEATURE_CONFIG = {
    'lag_hours': [1, 3, 6],  # Lagged pollution values
    'rolling_windows': [6, 12, 24],  # Rolling average windows (hours)
    'include_temporal_features': True,
    'include_lagged_features': True,
    'include_rolling_features': True
}

# Model training parameters
TRAINING_CONFIG = {
    'test_size': 0.2,  # 20% for testing
    'random_state': 42,
    'cv_folds': 5,  # Cross-validation folds
    
    # Hyperparameters for tuning
    'ridge_alphas': [0.1, 1.0, 10.0, 100.0],
    'lasso_alphas': [0.01, 0.1, 1.0, 10.0],
    'dt_max_depths': [5, 10, 15, 20, None],
    'rf_n_estimators': [50, 100, 200],
    'rf_max_depths': [10, 15, 20, None]
}

# Visualization parameters
VIZ_CONFIG = {
    'figure_size': (12, 8),
    'dpi': 300,
    'style': 'seaborn-v0_8-darkgrid',
    'color_palette': 'Set2',
    'save_format': 'png'
}

# Logging configuration
LOGGING_CONFIG = {
    'level': 'INFO',
    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    'datefmt': '%Y-%m-%d %H:%M:%S'
}
