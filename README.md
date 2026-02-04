# Vehicular Pollution Estimation - Machine Learning Model

An explainable machine learning system to estimate vehicular contribution to air pollution using traffic volume and air quality data.

## Overview

This project implements a data-driven approach to estimate how much different vehicle categories contribute to urban air pollution. It uses EPA emission factors, synthetic traffic data, and multiple regression models to provide interpretable predictions and insights.

## Features

- **Multiple Regression Models**: Linear Regression, Ridge, Lasso, Decision Tree, Random Forest
- **EPA Emission Factors**: Standard emission factors for PM2.5, PM10, NO₂, and CO
- **Synthetic Data Generation**: Realistic traffic patterns with rush hours, weekends, and seasonal variations
- **Comprehensive Feature Engineering**: Emission-based, temporal, lagged, and rolling features
- **Model Explainability**: Feature importance, category analysis, and vehicle contribution estimation
- **Rich Visualizations**: Performance plots, residual analysis, feature importance, and contribution breakdowns
- **Time-Series Aware**: Proper train-test split respecting temporal order

## Project Structure

```
pollution_control/
├── data/
│   ├── raw/                    # Raw input data
│   ├── processed/              # Processed features
│   └── synthetic/              # Generated synthetic data
├── models/
│   ├── saved_models/           # Trained model files
│   └── results/                # Model outputs and predictions
├── src/
│   ├── data/
│   │   ├── data_generator.py   # Synthetic data generator
│   │   └── validator.py        # Data validation
│   ├── features/
│   │   ├── emission_factors.py # EPA emission factors
│   │   ├── feature_engineering.py # Feature creation
│   │   └── preprocessing.py    # Scaling and normalization
│   ├── models/
│   │   ├── trainer.py          # Model training pipeline
│   │   ├── evaluator.py        # Evaluation metrics
│   │   └── explainer.py        # Explainability analysis
│   ├── visualization/
│   │   └── plots.py            # Plotting functions
│   └── utils/
│       ├── config.py           # Configuration settings
│       └── helpers.py          # Utility functions
├── outputs/
│   ├── figures/                # Generated plots
│   ├── reports/                # Analysis reports
│   └── contributions/          # Contribution estimates
├── main.py                     # Main execution script
├── requirements.txt            # Python dependencies
└── README.md                   # This file
```

## Installation

### Prerequisites

- Python 3.8 or higher
- pip package manager

### Setup

1. **Clone or navigate to the project directory**:
   ```bash
   cd d:\pollution_control
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Quick Start - Run Complete Pipeline

Run the entire pipeline (data generation, training, evaluation, explainability, visualization):

```bash
python main.py --mode full
```

For faster execution without hyperparameter tuning:

```bash
python main.py --mode full --no-tune
```

### Individual Steps

**Generate synthetic data only**:
```bash
python main.py --mode generate
```

**Train models only**:
```bash
python main.py --mode train
```

**Evaluate existing models**:
```bash
python main.py --mode evaluate
```

**Generate explainability analysis**:
```bash
python main.py --mode explain
```

**Create visualizations**:
```bash
python main.py --mode visualize
```

## Data Format

### Traffic Data (CSV)

Expected columns:
- `timestamp`: DateTime in format YYYY-MM-DD HH:MM:SS
- `two_wheelers`: Count of two-wheelers
- `cars`: Count of cars
- `buses`: Count of buses
- `trucks`: Count of trucks/heavy vehicles

### Air Quality Data (CSV)

Expected columns:
- `timestamp`: DateTime in format YYYY-MM-DD HH:MM:SS
- `PM2.5`: PM2.5 concentration (μg/m³)
- `PM10`: PM10 concentration (μg/m³)
- `NO2`: NO₂ concentration (μg/m³)
- `CO`: CO concentration (μg/m³)

## EPA Emission Factors

The model uses standard EPA emission factors (g/km per vehicle):

| Vehicle Type | PM2.5 | PM10 | NO₂ | CO |
|--------------|-------|------|-----|-----|
| Two-wheelers | 0.015 | 0.020 | 0.080 | 2.500 |
| Cars | 0.005 | 0.008 | 0.150 | 1.200 |
| Buses | 0.120 | 0.150 | 2.500 | 3.000 |
| Trucks | 0.180 | 0.220 | 3.500 | 4.500 |

*Source: EPA MOVES model and EMEP/EEA air pollutant emission inventory guidebook*

## Model Architecture

### Regression Models

1. **Linear Regression**: Baseline interpretable model
2. **Ridge Regression**: L2 regularization for stability
3. **Lasso Regression**: L1 regularization for feature selection
4. **Decision Tree**: Non-linear, interpretable relationships
5. **Random Forest**: Ensemble method with feature importance

### Feature Engineering

- **Emission-based features**: Calculated from vehicle counts × emission factors
- **Aggregate features**: Total traffic, vehicle ratios
- **Temporal features**: Hour, day of week, weekend flag, rush hour indicator
- **Lagged features**: Previous 1h, 3h, 6h pollution values
- **Rolling features**: 6h, 12h, 24h rolling averages

### Training Strategy

- **Time-series split**: 80% training, 20% testing (chronological)
- **Cross-validation**: 5-fold time-series CV
- **Hyperparameter tuning**: GridSearchCV for optimal parameters
- **Separate models**: One model per pollutant (4 pollutants × 5 models = 20 models)

## Evaluation Metrics

- **RMSE** (Root Mean Squared Error): Penalizes large errors
- **MAE** (Mean Absolute Error): Average absolute deviation
- **R²** (Coefficient of Determination): Proportion of variance explained
- **MAPE** (Mean Absolute Percentage Error): Percentage error

## Explainability

### Feature Importance

- **Linear models**: Absolute coefficients
- **Tree models**: Gini importance
- **Permutation importance**: Model-agnostic importance

### Vehicle Contribution Estimation

Contribution is calculated by:
1. Making predictions with full feature set
2. Making predictions with each vehicle category set to zero
3. Computing difference as contribution
4. Expressing as percentage of actual pollution

**Formula**:
```
Vehicular Contribution (%) = (Predicted_pollution / Actual_pollution) × 100
```

## Output Files

### Models
- `models/saved_models/{pollutant}/{model_type}.pkl`: Trained models
- `models/saved_models/{pollutant}/best_params.json`: Hyperparameters

### Results
- `models/results/{pollutant}/model_comparison.csv`: Performance comparison
- `models/results/{pollutant}/detailed_results.json`: Detailed metrics

### Visualizations
- `outputs/figures/{pollutant}/actual_vs_pred_{model}.png`: Scatter plots
- `outputs/figures/{pollutant}/residuals_{model}.png`: Residual analysis
- `outputs/figures/{pollutant}/timeseries_{model}.png`: Time series plots
- `outputs/figures/{pollutant}/feature_importance_{model}.png`: Feature importance
- `outputs/figures/{pollutant}/vehicle_contributions_{model}.png`: Contribution pie charts
- `outputs/figures/all_pollutants_comparison_R2.png`: Cross-pollutant comparison

## Assumptions and Limitations

### Assumptions

1. **Linear relationship**: For linear models, assumes linear relationship between emissions and concentrations
2. **Emission factors**: EPA emission factors are representative of the local vehicle fleet
3. **Background pollution**: Captured implicitly in model intercept
4. **Meteorological effects**: Implicit in temporal patterns and noise
5. **Dispersion**: Simplified dispersion model for synthetic data

### Limitations

1. **Synthetic data**: Current implementation uses synthetic data; real-world data may have different patterns
2. **Emission factors**: Generic EPA factors may not reflect regional variations
3. **Meteorology**: Does not explicitly model wind, temperature, humidity effects
4. **Spatial variation**: Point-source model; does not account for spatial dispersion
5. **Non-vehicular sources**: Does not model industrial, residential, or natural pollution sources

## Customization

### Modify Emission Factors

Edit `src/utils/config.py`:

```python
EMISSION_FACTORS = {
    'two_wheelers': {
        'PM2.5': 0.015,  # Modify values here
        # ...
    },
    # ...
}
```

### Adjust Synthetic Data Parameters

Edit `src/utils/config.py`:

```python
SYNTHETIC_DATA_CONFIG = {
    'n_days': 90,  # Change number of days
    'rush_hour_morning': (7, 10),  # Adjust rush hours
    # ...
}
```

### Add New Features

Modify `src/features/feature_engineering.py` to add custom features.

### Change Model Hyperparameters

Edit `src/utils/config.py`:

```python
TRAINING_CONFIG = {
    'ridge_alphas': [0.1, 1.0, 10.0],  # Modify search space
    # ...
}
```

## Example Results

Expected model performance (synthetic data):

| Model | PM2.5 R² | PM10 R² | NO₂ R² | CO R² |
|-------|----------|---------|--------|-------|
| Random Forest | 0.85-0.95 | 0.85-0.95 | 0.80-0.90 | 0.80-0.90 |
| Ridge | 0.75-0.85 | 0.75-0.85 | 0.70-0.80 | 0.70-0.80 |
| Linear | 0.70-0.80 | 0.70-0.80 | 0.65-0.75 | 0.65-0.75 |

Expected vehicle contributions (typical urban scenario):
- Heavy vehicles (buses + trucks): 40-60%
- Cars: 25-35%
- Two-wheelers: 10-20%

## References

1. EPA MOVES (Motor Vehicle Emission Simulator): https://www.epa.gov/moves
2. EMEP/EEA Air Pollutant Emission Inventory Guidebook: https://www.eea.europa.eu/publications/emep-eea-guidebook-2019
3. Scikit-learn Documentation: https://scikit-learn.org/

## License

This project is intended for educational and research purposes.

## Contact

For questions or issues, please refer to the project documentation or create an issue in the repository.

---

**Note**: This is an academic project designed for university coursework and environmental analytics. For production use, validate with real-world data and domain experts.
