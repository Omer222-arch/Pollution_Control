"""
Visualization functions for pollution estimation model.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, List, Tuple
from pathlib import Path

from src.utils.config import VIZ_CONFIG, FIGURES_DIR, VEHICLE_CATEGORIES
from src.utils.helpers import setup_logging

logger = setup_logging(__name__)

# Set style
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette(VIZ_CONFIG['color_palette'])


class Visualizer:
    """
    Create visualizations for model results and analysis.
    """
    
    def __init__(self, save_dir: Path = FIGURES_DIR):
        """
        Initialize visualizer.
        
        Args:
            save_dir: Directory to save figures
        """
        self.save_dir = save_dir
        self.save_dir.mkdir(parents=True, exist_ok=True)
        
    def _save_figure(self, filename: str, pollutant: str = None) -> None:
        """
        Save current figure.
        
        Args:
            filename: Filename for the figure
            pollutant: Optional pollutant name for subdirectory
        """
        if pollutant:
            save_path = self.save_dir / pollutant
            save_path.mkdir(parents=True, exist_ok=True)
        else:
            save_path = self.save_dir
        
        filepath = save_path / f"{filename}.{VIZ_CONFIG['save_format']}"
        plt.savefig(filepath, dpi=VIZ_CONFIG['dpi'], bbox_inches='tight')
        logger.info(f"Figure saved: {filepath}")
        
    def plot_actual_vs_predicted(self,
                                 y_actual: np.ndarray,
                                 y_pred: np.ndarray,
                                 model_type: str,
                                 pollutant: str,
                                 dataset: str = 'test') -> None:
        """
        Plot actual vs predicted values.
        
        Args:
            y_actual: Actual values
            y_pred: Predicted values
            model_type: Model type name
            pollutant: Pollutant name
            dataset: Dataset name (train/test)
        """
        fig, ax = plt.subplots(figsize=VIZ_CONFIG['figure_size'])
        
        # Scatter plot
        ax.scatter(y_actual, y_pred, alpha=0.5, s=20)
        
        # Perfect prediction line
        min_val = min(y_actual.min(), y_pred.min())
        max_val = max(y_actual.max(), y_pred.max())
        ax.plot([min_val, max_val], [min_val, max_val], 'r--', lw=2, label='Perfect Prediction')
        
        # Labels and title
        ax.set_xlabel(f'Actual {pollutant} (μg/m³)', fontsize=12)
        ax.set_ylabel(f'Predicted {pollutant} (μg/m³)', fontsize=12)
        ax.set_title(f'Actual vs Predicted - {model_type} ({dataset})\n{pollutant}', 
                    fontsize=14, fontweight='bold')
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        self._save_figure(f'actual_vs_pred_{model_type}_{dataset}', pollutant)
        plt.close()
        
    def plot_residuals(self,
                      y_actual: np.ndarray,
                      y_pred: np.ndarray,
                      model_type: str,
                      pollutant: str) -> None:
        """
        Plot residual analysis.
        
        Args:
            y_actual: Actual values
            y_pred: Predicted values
            model_type: Model type name
            pollutant: Pollutant name
        """
        residuals = y_actual - y_pred
        
        fig, axes = plt.subplots(1, 2, figsize=(15, 5))
        
        # Residuals vs Predicted
        axes[0].scatter(y_pred, residuals, alpha=0.5, s=20)
        axes[0].axhline(y=0, color='r', linestyle='--', lw=2)
        axes[0].set_xlabel(f'Predicted {pollutant} (μg/m³)', fontsize=12)
        axes[0].set_ylabel('Residuals (μg/m³)', fontsize=12)
        axes[0].set_title('Residuals vs Predicted', fontsize=12, fontweight='bold')
        axes[0].grid(True, alpha=0.3)
        
        # Residuals histogram
        axes[1].hist(residuals, bins=50, edgecolor='black', alpha=0.7)
        axes[1].axvline(x=0, color='r', linestyle='--', lw=2)
        axes[1].set_xlabel('Residuals (μg/m³)', fontsize=12)
        axes[1].set_ylabel('Frequency', fontsize=12)
        axes[1].set_title('Residuals Distribution', fontsize=12, fontweight='bold')
        axes[1].grid(True, alpha=0.3)
        
        fig.suptitle(f'Residual Analysis - {model_type}\n{pollutant}', 
                    fontsize=14, fontweight='bold', y=1.02)
        
        self._save_figure(f'residuals_{model_type}', pollutant)
        plt.close()
        
    def plot_model_comparison(self,
                             comparison_df: pd.DataFrame,
                             pollutant: str,
                             metric: str = 'R2') -> None:
        """
        Plot model comparison bar chart.
        
        Args:
            comparison_df: DataFrame with model comparison
            pollutant: Pollutant name
            metric: Metric to plot (R2, RMSE, MAE)
        """
        fig, ax = plt.subplots(figsize=(12, 6))
        
        x = np.arange(len(comparison_df))
        width = 0.35
        
        train_col = f'Train_{metric}'
        test_col = f'Test_{metric}'
        
        ax.bar(x - width/2, comparison_df[train_col], width, label='Train', alpha=0.8)
        ax.bar(x + width/2, comparison_df[test_col], width, label='Test', alpha=0.8)
        
        ax.set_xlabel('Model', fontsize=12)
        ax.set_ylabel(metric, fontsize=12)
        ax.set_title(f'Model Comparison - {metric}\n{pollutant}', 
                    fontsize=14, fontweight='bold')
        ax.set_xticks(x)
        ax.set_xticklabels(comparison_df['Model'], rotation=45, ha='right')
        ax.legend()
        ax.grid(True, alpha=0.3, axis='y')
        
        self._save_figure(f'model_comparison_{metric}', pollutant)
        plt.close()
        
    def plot_feature_importance(self,
                               importance_df: pd.DataFrame,
                               model_type: str,
                               pollutant: str,
                               top_n: int = 20) -> None:
        """
        Plot feature importance.
        
        Args:
            importance_df: DataFrame with feature importance
            model_type: Model type name
            pollutant: Pollutant name
            top_n: Number of top features to plot
        """
        fig, ax = plt.subplots(figsize=(10, 8))
        
        top_features = importance_df.head(top_n)
        
        # Horizontal bar chart
        y_pos = np.arange(len(top_features))
        ax.barh(y_pos, top_features['importance_normalized'] * 100, alpha=0.8)
        
        ax.set_yticks(y_pos)
        ax.set_yticklabels(top_features['feature'])
        ax.invert_yaxis()
        ax.set_xlabel('Importance (%)', fontsize=12)
        ax.set_title(f'Top {top_n} Feature Importance - {model_type}\n{pollutant}', 
                    fontsize=14, fontweight='bold')
        ax.grid(True, alpha=0.3, axis='x')
        
        self._save_figure(f'feature_importance_{model_type}', pollutant)
        plt.close()
        
    def plot_category_importance(self,
                                 category_df: pd.DataFrame,
                                 model_type: str,
                                 pollutant: str) -> None:
        """
        Plot feature category importance.
        
        Args:
            category_df: DataFrame with category importance
            model_type: Model type name
            pollutant: Pollutant name
        """
        fig, ax = plt.subplots(figsize=(10, 6))
        
        ax.bar(category_df['category'], category_df['importance_normalized'] * 100, alpha=0.8)
        
        ax.set_xlabel('Feature Category', fontsize=12)
        ax.set_ylabel('Importance (%)', fontsize=12)
        ax.set_title(f'Feature Category Importance - {model_type}\n{pollutant}', 
                    fontsize=14, fontweight='bold')
        ax.set_xticklabels(category_df['category'], rotation=45, ha='right')
        ax.grid(True, alpha=0.3, axis='y')
        
        self._save_figure(f'category_importance_{model_type}', pollutant)
        plt.close()
        
    def plot_vehicle_contributions(self,
                                   contributions: Dict[str, Dict[str, float]],
                                   pollutant: str,
                                   model_type: str = None) -> None:
        """
        Plot vehicle category contributions as pie chart.
        
        Args:
            contributions: Dictionary with vehicle contributions
            pollutant: Pollutant name
            model_type: Optional model type name
        """
        fig, ax = plt.subplots(figsize=(10, 8))
        
        labels = []
        sizes = []
        
        for vehicle_type, contrib in contributions.items():
            labels.append(vehicle_type.replace('_', ' ').title())
            sizes.append(contrib['percentage_contribution'])
        
        # Create pie chart
        colors = sns.color_palette(VIZ_CONFIG['color_palette'], len(labels))
        wedges, texts, autotexts = ax.pie(sizes, labels=labels, autopct='%1.1f%%',
                                           colors=colors, startangle=90)
        
        # Enhance text
        for text in texts:
            text.set_fontsize(11)
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontweight('bold')
            autotext.set_fontsize(10)
        
        title = f'Vehicle Category Contributions to {pollutant}'
        if model_type:
            title += f'\n{model_type}'
        ax.set_title(title, fontsize=14, fontweight='bold')
        
        filename = f'vehicle_contributions_{model_type}' if model_type else 'vehicle_contributions'
        self._save_figure(filename, pollutant)
        plt.close()
        
    def plot_time_series_predictions(self,
                                     timestamps: pd.DatetimeIndex,
                                     y_actual: np.ndarray,
                                     y_pred: np.ndarray,
                                     model_type: str,
                                     pollutant: str,
                                     n_points: int = 500) -> None:
        """
        Plot time series of actual vs predicted values.
        
        Args:
            timestamps: Time index
            y_actual: Actual values
            y_pred: Predicted values
            model_type: Model type name
            pollutant: Pollutant name
            n_points: Number of points to plot (for readability)
        """
        fig, ax = plt.subplots(figsize=(15, 6))
        
        # Limit points for readability
        if len(timestamps) > n_points:
            indices = np.linspace(0, len(timestamps)-1, n_points, dtype=int)
            timestamps = timestamps[indices]
            y_actual = y_actual[indices]
            y_pred = y_pred[indices]
        
        ax.plot(timestamps, y_actual, label='Actual', alpha=0.7, linewidth=1.5)
        ax.plot(timestamps, y_pred, label='Predicted', alpha=0.7, linewidth=1.5)
        
        ax.set_xlabel('Time', fontsize=12)
        ax.set_ylabel(f'{pollutant} (μg/m³)', fontsize=12)
        ax.set_title(f'Time Series: Actual vs Predicted - {model_type}\n{pollutant}', 
                    fontsize=14, fontweight='bold')
        ax.legend()
        ax.grid(True, alpha=0.3)
        plt.xticks(rotation=45)
        
        self._save_figure(f'timeseries_{model_type}', pollutant)
        plt.close()
        
    def plot_correlation_heatmap(self,
                                X: pd.DataFrame,
                                pollutant: str,
                                top_n: int = 20) -> None:
        """
        Plot correlation heatmap of top features.
        
        Args:
            X: Feature matrix
            pollutant: Pollutant name
            top_n: Number of features to include
        """
        # Select top_n features by variance
        variances = X.var().sort_values(ascending=False)
        top_features = variances.head(top_n).index
        
        fig, ax = plt.subplots(figsize=(12, 10))
        
        corr_matrix = X[top_features].corr()
        
        sns.heatmap(corr_matrix, annot=False, cmap='coolwarm', center=0,
                   square=True, linewidths=0.5, cbar_kws={"shrink": 0.8}, ax=ax)
        
        ax.set_title(f'Feature Correlation Heatmap (Top {top_n})\n{pollutant}', 
                    fontsize=14, fontweight='bold')
        plt.xticks(rotation=45, ha='right')
        plt.yticks(rotation=0)
        
        self._save_figure(f'correlation_heatmap', pollutant)
        plt.close()
        
    def plot_all_pollutants_comparison(self,
                                      results: Dict[str, pd.DataFrame],
                                      metric: str = 'R2') -> None:
        """
        Plot comparison across all pollutants.
        
        Args:
            results: Dictionary of comparison DataFrames by pollutant
            metric: Metric to plot
        """
        fig, ax = plt.subplots(figsize=(14, 7))
        
        pollutants = list(results.keys())
        models = results[pollutants[0]]['Model'].tolist()
        
        x = np.arange(len(models))
        width = 0.8 / len(pollutants)
        
        for i, pollutant in enumerate(pollutants):
            offset = (i - len(pollutants)/2 + 0.5) * width
            values = results[pollutant][f'Test_{metric}'].values
            ax.bar(x + offset, values, width, label=pollutant, alpha=0.8)
        
        ax.set_xlabel('Model', fontsize=12)
        ax.set_ylabel(f'Test {metric}', fontsize=12)
        ax.set_title(f'Model Performance Across All Pollutants - {metric}', 
                    fontsize=14, fontweight='bold')
        ax.set_xticks(x)
        ax.set_xticklabels(models, rotation=45, ha='right')
        ax.legend()
        ax.grid(True, alpha=0.3, axis='y')
        
        self._save_figure(f'all_pollutants_comparison_{metric}')
        plt.close()


def main():
    """
    Test visualization functions.
    """
    from src.data.data_generator import SyntheticDataGenerator
    from src.features.feature_engineering import FeatureEngineer
    from src.features.preprocessing import DataPreprocessor
    from src.models.trainer import ModelTrainer
    from src.models.explainer import ModelExplainer
    
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
    
    # Train model
    trainer = ModelTrainer()
    model = trainer.train_single_model('random_forest', X_train, y_train, tune_hyperparameters=False)
    
    # Predictions
    y_test_pred = model.predict(X_test)
    
    # Visualize
    viz = Visualizer()
    
    print("Creating visualizations...")
    viz.plot_actual_vs_predicted(y_test.values, y_test_pred, 'random_forest', pollutant)
    viz.plot_residuals(y_test.values, y_test_pred, 'random_forest', pollutant)
    viz.plot_time_series_predictions(y_test.index, y_test.values, y_test_pred, 
                                     'random_forest', pollutant)
    
    # Feature importance
    explainer = ModelExplainer()
    importance_df = explainer.get_feature_importance(model, 'random_forest', X_train.columns.tolist())
    viz.plot_feature_importance(importance_df, 'random_forest', pollutant)
    
    # Vehicle contributions
    contributions = explainer.estimate_vehicle_contributions(model, X_test, y_test, X_test.columns.tolist())
    viz.plot_vehicle_contributions(contributions, pollutant, 'random_forest')
    
    print(f"Visualizations saved to {FIGURES_DIR / pollutant}")


if __name__ == "__main__":
    main()
