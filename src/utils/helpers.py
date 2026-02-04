"""
Utility helper functions for the pollution estimation project.
"""

import logging
import json
import pickle
import joblib
from pathlib import Path
from typing import Any, Dict, List
import pandas as pd
import numpy as np
from src.utils.config import LOGGING_CONFIG


def setup_logging(name: str = __name__) -> logging.Logger:
    """
    Set up logging configuration.
    
    Args:
        name: Logger name
        
    Returns:
        Configured logger instance
    """
    logging.basicConfig(
        level=LOGGING_CONFIG['level'],
        format=LOGGING_CONFIG['format'],
        datefmt=LOGGING_CONFIG['datefmt']
    )
    return logging.getLogger(name)


def save_model(model: Any, filepath: Path) -> None:
    """
    Save a trained model to disk.
    
    Args:
        model: Trained model object
        filepath: Path to save the model
    """
    filepath.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, filepath)
    logging.info(f"Model saved to {filepath}")


def load_model(filepath: Path) -> Any:
    """
    Load a trained model from disk.
    
    Args:
        filepath: Path to the saved model
        
    Returns:
        Loaded model object
    """
    if not filepath.exists():
        raise FileNotFoundError(f"Model file not found: {filepath}")
    model = joblib.load(filepath)
    logging.info(f"Model loaded from {filepath}")
    return model


def save_json(data: Dict, filepath: Path) -> None:
    """
    Save dictionary to JSON file.
    
    Args:
        data: Dictionary to save
        filepath: Path to save the JSON file
    """
    filepath.parent.mkdir(parents=True, exist_ok=True)
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=4)
    logging.info(f"JSON saved to {filepath}")


def load_json(filepath: Path) -> Dict:
    """
    Load dictionary from JSON file.
    
    Args:
        filepath: Path to the JSON file
        
    Returns:
        Loaded dictionary
    """
    if not filepath.exists():
        raise FileNotFoundError(f"JSON file not found: {filepath}")
    with open(filepath, 'r') as f:
        data = json.load(f)
    logging.info(f"JSON loaded from {filepath}")
    return data


def save_dataframe(df: pd.DataFrame, filepath: Path, index: bool = False) -> None:
    """
    Save DataFrame to CSV file.
    
    Args:
        df: DataFrame to save
        filepath: Path to save the CSV file
        index: Whether to include index in CSV
    """
    filepath.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(filepath, index=index)
    logging.info(f"DataFrame saved to {filepath}")


def load_dataframe(filepath: Path) -> pd.DataFrame:
    """
    Load DataFrame from CSV file.
    
    Args:
        filepath: Path to the CSV file
        
    Returns:
        Loaded DataFrame
    """
    if not filepath.exists():
        raise FileNotFoundError(f"CSV file not found: {filepath}")
    df = pd.read_csv(filepath)
    logging.info(f"DataFrame loaded from {filepath}")
    return df


def calculate_percentage_contribution(predicted: np.ndarray, 
                                      actual: np.ndarray) -> np.ndarray:
    """
    Calculate percentage contribution of predicted values to actual values.
    
    Args:
        predicted: Predicted pollution values
        actual: Actual pollution values
        
    Returns:
        Percentage contributions
    """
    # Avoid division by zero
    with np.errstate(divide='ignore', invalid='ignore'):
        contribution = np.where(actual > 0, (predicted / actual) * 100, 0)
    
    # Cap at 100% to handle cases where prediction exceeds actual
    contribution = np.clip(contribution, 0, 100)
    
    return contribution


def get_time_features(timestamps: pd.DatetimeIndex) -> pd.DataFrame:
    """
    Extract temporal features from timestamps.
    
    Args:
        timestamps: DatetimeIndex or Series
        
    Returns:
        DataFrame with temporal features
    """
    # Convert to DatetimeIndex if it's a Series
    if isinstance(timestamps, pd.Series):
        timestamps = pd.DatetimeIndex(timestamps)
    
    features = pd.DataFrame(index=range(len(timestamps)))
    features['hour'] = timestamps.hour
    features['day_of_week'] = timestamps.dayofweek
    features['is_weekend'] = (timestamps.dayofweek >= 5).astype(int)
    features['is_rush_hour'] = (
        ((timestamps.hour >= 7) & (timestamps.hour < 10)) |
        ((timestamps.hour >= 17) & (timestamps.hour < 20))
    ).astype(int)
    features['month'] = timestamps.month
    features['day_of_year'] = timestamps.dayofyear
    
    return features


def create_summary_table(results: Dict[str, Dict[str, float]]) -> pd.DataFrame:
    """
    Create a summary table from results dictionary.
    
    Args:
        results: Nested dictionary of results
        
    Returns:
        DataFrame with formatted results
    """
    df = pd.DataFrame(results).T
    return df


def print_section_header(title: str, width: int = 80) -> None:
    """
    Print a formatted section header.
    
    Args:
        title: Section title
        width: Width of the header line
    """
    print("\n" + "=" * width)
    print(f"  {title}")
    print("=" * width + "\n")
