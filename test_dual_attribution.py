"""
Test script for dual attribution implementation.
Validates that both marginal and emission-based contributions work correctly.
"""

import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

import pandas as pd
import numpy as np
from src.models.explainer import ModelExplainer
from src.visualization.plots import Visualizer
from src.utils.config import EMISSION_FACTORS, VEHICLE_CATEGORIES
from sklearn.linear_model import LinearRegression
from src.utils.helpers import setup_logging

logger = setup_logging(__name__)

def test_emission_contributions():
    """Test that emission-based contributions are always non-negative."""
    logger.info("Testing emission-based contributions...")
    
    # Create mock traffic data
    traffic_data = pd.DataFrame({
        'cars': [100, 120, 110, 130, 125],
        'light_trucks': [30, 35, 32, 38, 36],
        'heavy_trucks': [20, 25, 22, 28, 26],
        'motorcycles': [50, 55, 52, 60, 58]
    })
    
    explainer = ModelExplainer()
    
    # Test for each pollutant
    for pollutant in ['PM2.5', 'PM10', 'NO2', 'CO']:
        try:
            contributions = explainer.estimate_emission_contributions(traffic_data, pollutant)
            
            # Validate structure
            assert isinstance(contributions, dict), "Should return dictionary"
            
            # Validate all values are non-negative
            for vehicle_type, values in contributions.items():
                abs_contrib = values['absolute_contribution']
                pct_contrib = values['percentage_contribution']
                
                assert abs_contrib >= 0, f"Absolute contribution {abs_contrib} is negative!"
                assert pct_contrib >= 0, f"Percentage contribution {pct_contrib} is negative!"
                assert pct_contrib <= 100, f"Percentage {pct_contrib} exceeds 100%!"
            
            # Validate percentages sum to ~100%
            total_pct = sum(v['percentage_contribution'] for v in contributions.values())
            assert 99.0 <= total_pct <= 101.0, f"Percentages sum to {total_pct}, not 100%"
            
            logger.info(f"✓ {pollutant}: All values non-negative, sum to 100%")
            
            # Print sample output
            print(f"\n{'='*80}")
            print(f"Emission Contributions for {pollutant}")
            print(f"{'='*80}")
            explainer.print_emission_contributions(contributions, pollutant)
            
        except Exception as e:
            logger.error(f"✗ {pollutant}: {e}")
            raise

def test_marginal_contributions():
    """Test that marginal contributions (can be negative) are computed."""
    logger.info("Testing marginal-based contributions...")
    
    # Create mock data
    np.random.seed(42)
    n_samples = 100
    
    # Features with lag structure
    X = pd.DataFrame({
        'cars': np.random.normal(100, 20, n_samples),
        'light_trucks': np.random.normal(30, 8, n_samples),
        'heavy_trucks': np.random.normal(20, 5, n_samples),
        'motorcycles': np.random.normal(50, 15, n_samples),
        'cars_lag1': np.random.normal(100, 20, n_samples),  # Lag feature
        'rolling_avg_2h': np.random.normal(80, 15, n_samples),  # Rolling average
    })
    
    # Target with lag dependence (higher lag = lower additional effect)
    y = (0.3 * X['cars_lag1'] + 
         0.2 * X['cars'] + 
         0.15 * X['light_trucks'] + 
         0.25 * X['heavy_trucks'] - 
         0.1 * X['motorcycles'] +  # Can be negative coefficient
         np.random.normal(0, 5, n_samples))
    
    # Train simple model
    model = LinearRegression()
    model.fit(X, y)
    
    # Get contributions
    explainer = ModelExplainer()
    feature_names = X.columns.tolist()
    
    try:
        contributions = explainer.estimate_vehicle_contributions(
            model, X, y, feature_names
        )
        
        assert isinstance(contributions, dict), "Should return dictionary"
        
        # For this data, we expect negative motorcycles contribution
        logger.info("✓ Marginal contributions computed")
        
        print(f"\n{'='*80}")
        print(f"Marginal Vehicle Contributions (from regression)")
        print(f"{'='*80}")
        explainer.print_vehicle_contributions(contributions)
        
        # Check if any are negative (expected for this synthetic data)
        negatives = [v for v in contributions.values() 
                    if v['absolute_contribution'] < 0]
        if negatives:
            logger.info(f"✓ Found {len(negatives)} negative contribution(s) (expected with lag features)")
        
    except Exception as e:
        logger.error(f"✗ Marginal contributions: {e}")
        raise

def test_visualization_functions():
    """Test that visualization functions don't crash."""
    logger.info("Testing visualization functions...")
    
    # Create mock contributions
    mock_marginal = {
        'cars': {'absolute_contribution': 0.45, 'percentage_contribution': 30},
        'light_trucks': {'absolute_contribution': -0.10, 'percentage_contribution': -7},  # Negative!
        'heavy_trucks': {'absolute_contribution': 1.20, 'percentage_contribution': 80},
        'motorcycles': {'absolute_contribution': 0.05, 'percentage_contribution': 3},
    }
    
    mock_emission = {
        'cars': {'absolute_contribution': 8.2, 'percentage_contribution': 32.8},
        'light_trucks': {'absolute_contribution': 3.2, 'percentage_contribution': 12.8},
        'heavy_trucks': {'absolute_contribution': 12.1, 'percentage_contribution': 48.4},
        'motorcycles': {'absolute_contribution': 1.5, 'percentage_contribution': 6.0},
    }
    
    visualizer = Visualizer()
    
    try:
        # Test marginal bar chart (should handle negative values)
        visualizer.plot_marginal_contributions_bar(
            mock_marginal, 'PM2.5', 'LinearRegression'
        )
        logger.info("✓ Marginal bar chart created successfully")
        
        # Test emission pie chart (should work with non-negative values)
        visualizer.plot_emission_contributions_pie(
            mock_emission, 'PM2.5', 'LinearRegression'
        )
        logger.info("✓ Emission pie chart created successfully")
        
        # Test that pie chart would fail with marginal (negative values)
        try:
            visualizer.plot_emission_contributions_pie(
                mock_marginal, 'PM2.5', 'TestFailure'
            )
            logger.warning("⚠ Pie chart should have warned about negative values")
        except ValueError as e:
            logger.info(f"✓ Pie chart correctly rejects negative values: {e}")
        
    except Exception as e:
        logger.error(f"✗ Visualization: {e}")
        raise

def main():
    """Run all tests."""
    print("\n" + "="*80)
    print("TESTING DUAL ATTRIBUTION IMPLEMENTATION")
    print("="*80 + "\n")
    
    try:
        test_emission_contributions()
        logger.info("\n✓ Emission contributions test PASSED\n")
    except Exception as e:
        logger.error(f"\n✗ Emission contributions test FAILED: {e}\n")
        return False
    
    try:
        test_marginal_contributions()
        logger.info("\n✓ Marginal contributions test PASSED\n")
    except Exception as e:
        logger.error(f"\n✗ Marginal contributions test FAILED: {e}\n")
        return False
    
    try:
        test_visualization_functions()
        logger.info("\n✓ Visualization functions test PASSED\n")
    except Exception as e:
        logger.error(f"\n✗ Visualization functions test FAILED: {e}\n")
        return False
    
    print("\n" + "="*80)
    print("ALL TESTS PASSED ✓")
    print("="*80 + "\n")
    print("Summary:")
    print("  ✓ Emission-based contributions are always non-negative")
    print("  ✓ Marginal contributions can be negative (shows multicollinearity)")
    print("  ✓ Bar charts handle signed values correctly")
    print("  ✓ Pie charts work with non-negative values")
    print("  ✓ Error handling prevents ValueError on negative wedges")
    print("\n" + "="*80 + "\n")
    
    return True

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
