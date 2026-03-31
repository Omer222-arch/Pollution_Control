"""
Main execution script for vehicular pollution estimation model.

Usage:
    python main.py --mode full              # Run complete pipeline
    python main.py --mode train             # Train models only
    python main.py --mode evaluate          # Evaluate existing models
    python main.py --mode explain           # Generate explainability analysis
"""

import argparse
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.data.data_generator import SyntheticDataGenerator
from src.features.feature_engineering import FeatureEngineer
from src.features.preprocessing import DataPreprocessor
from src.models.trainer import ModelTrainer
from src.models.evaluator import ModelEvaluator, create_predictions_dataframe
from src.models.explainer import ModelExplainer
from src.visualization.plots import Visualizer
from src.utils.config import (
    POLLUTANTS, MODEL_TYPES, SYNTHETIC_DATA_DIR, 
    SAVED_MODELS_DIR, RESULTS_DIR, FIGURES_DIR
)
from src.utils.helpers import setup_logging, print_section_header

logger = setup_logging(__name__)


class PollutionEstimationPipeline:
    """
    Complete pipeline for pollution estimation model.
    """
    
    def __init__(self):
        """Initialize pipeline components."""
        self.generator = SyntheticDataGenerator()
        self.engineer = FeatureEngineer()
        self.preprocessor = DataPreprocessor()
        self.trainer = ModelTrainer()
        self.evaluator = ModelEvaluator()
        self.explainer = ModelExplainer()
        self.visualizer = Visualizer()
        
        self.traffic_data = None
        self.pollution_data = None
        
    def generate_data(self):
        """Generate synthetic data."""
        print_section_header("STEP 1: GENERATING SYNTHETIC DATA")
        
        self.traffic_data, self.pollution_data = self.generator.generate_and_save()
        
        logger.info(f"Data saved to {SYNTHETIC_DATA_DIR}")
        
    def train_models(self, tune_hyperparameters: bool = True):
        """Train models for all pollutants."""
        print_section_header("STEP 2: TRAINING MODELS")
        
        if self.traffic_data is None or self.pollution_data is None:
            logger.info("Loading synthetic data...")
            traffic_path = SYNTHETIC_DATA_DIR / "synthetic_traffic_data.csv"
            pollution_path = SYNTHETIC_DATA_DIR / "synthetic_pollution_data.csv"
            
            import pandas as pd
            self.traffic_data = pd.read_csv(traffic_path)
            self.pollution_data = pd.read_csv(pollution_path)
        
        for pollutant in POLLUTANTS:
            print(f"\n{'='*80}")
            print(f"TRAINING MODELS FOR {pollutant}")
            print(f"{'='*80}\n")
            
            # Create features
            logger.info(f"Creating features for {pollutant}...")
            df = self.engineer.create_all_features(
                self.traffic_data, self.pollution_data, pollutant
            )
            X, y = self.engineer.prepare_features_and_target(df, pollutant)
            
            # Preprocess
            logger.info("Preprocessing data...")
            X_train, X_test, y_train, y_test = self.preprocessor.prepare_train_test_data(X, y)
            
            # Train all models
            logger.info(f"Training {len(MODEL_TYPES)} models...")
            models = self.trainer.train_all_models(
                X_train, y_train, pollutant, tune_hyperparameters
            )
            
            # Save models
            self.trainer.save_models(pollutant)
            
            logger.info(f"✓ Completed training for {pollutant}\n")
        
        logger.info(f"All models saved to {SAVED_MODELS_DIR}")
        
    def evaluate_models(self):
        """Evaluate all trained models."""
        print_section_header("STEP 3: EVALUATING MODELS")
        
        if self.traffic_data is None or self.pollution_data is None:
            logger.info("Loading synthetic data...")
            import pandas as pd
            traffic_path = SYNTHETIC_DATA_DIR / "synthetic_traffic_data.csv"
            pollution_path = SYNTHETIC_DATA_DIR / "synthetic_pollution_data.csv"
            
            self.traffic_data = pd.read_csv(traffic_path)
            self.pollution_data = pd.read_csv(pollution_path)
        
        for pollutant in POLLUTANTS:
            print(f"\n{'='*80}")
            print(f"EVALUATING MODELS FOR {pollutant}")
            print(f"{'='*80}\n")
            
            # Create features
            df = self.engineer.create_all_features(
                self.traffic_data, self.pollution_data, pollutant
            )
            X, y = self.engineer.prepare_features_and_target(df, pollutant)
            
            # Preprocess
            X_train, X_test, y_train, y_test = self.preprocessor.prepare_train_test_data(X, y)
            
            # Load models
            models = self.trainer.load_models(pollutant)
            
            # Evaluate each model
            for model_type in MODEL_TYPES:
                if model_type in models and models[model_type] is not None:
                    model = models[model_type]
                    
                    # Predictions using trainer (handles feature selection consistency)
                    y_train_pred = self.trainer.predict(model_type, pollutant, X_train)
                    y_test_pred = self.trainer.predict(model_type, pollutant, X_test)
                    
                    # Evaluate
                    self.evaluator.evaluate_model(
                        model_type, pollutant,
                        y_train.values, y_train_pred,
                        y_test.values, y_test_pred
                    )
            
            # Print summary
            self.evaluator.print_summary(pollutant)
            
            # Save results
            self.evaluator.save_results(pollutant)
        
        logger.info(f"Evaluation results saved to {RESULTS_DIR}")
        
    def explain_models(self):
        """Generate explainability analysis."""
        print_section_header("STEP 4: EXPLAINABILITY ANALYSIS")
        
        if self.traffic_data is None or self.pollution_data is None:
            logger.info("Loading synthetic data...")
            import pandas as pd
            traffic_path = SYNTHETIC_DATA_DIR / "synthetic_traffic_data.csv"
            pollution_path = SYNTHETIC_DATA_DIR / "synthetic_pollution_data.csv"
            
            self.traffic_data = pd.read_csv(traffic_path)
            self.pollution_data = pd.read_csv(pollution_path)
        
        for pollutant in POLLUTANTS:
            print(f"\n{'='*80}")
            print(f"EXPLAINABILITY ANALYSIS FOR {pollutant}")
            print(f"{'='*80}\n")
            
            # Create features
            df = self.engineer.create_all_features(
                self.traffic_data, self.pollution_data, pollutant
            )
            X, y = self.engineer.prepare_features_and_target(df, pollutant)
            
            # Preprocess
            X_train, X_test, y_train, y_test = self.preprocessor.prepare_train_test_data(X, y)
            
            # Load models
            models = self.trainer.load_models(pollutant)
            
            # Analyze best performing model (Random Forest)
            model_type = 'random_forest'
            if model_type in models and models[model_type] is not None:
                model = models[model_type]
                
                # Feature importance
                importance_df = self.explainer.get_feature_importance(
                    model, model_type, X_train.columns.tolist()
                )
                self.explainer.print_feature_importance(importance_df, top_n=15)
                
                # Category importance
                category_importance = self.explainer.get_category_importance(importance_df)
                print("\nFeature Category Importance:")
                print(category_importance.to_string(index=False))
                print()
                
                # Vehicle contributions
                contributions = self.explainer.estimate_vehicle_contributions(
                    model, X_test, y_test, X_test.columns.tolist()
                )
                self.explainer.print_vehicle_contributions(contributions)
        
        logger.info("Explainability analysis complete")
        
    def visualize_results(self):
        """Generate visualizations."""
        print_section_header("STEP 5: GENERATING VISUALIZATIONS")
        
        if self.traffic_data is None or self.pollution_data is None:
            logger.info("Loading synthetic data...")
            import pandas as pd
            traffic_path = SYNTHETIC_DATA_DIR / "synthetic_traffic_data.csv"
            pollution_path = SYNTHETIC_DATA_DIR / "synthetic_pollution_data.csv"
            
            self.traffic_data = pd.read_csv(traffic_path)
            self.pollution_data = pd.read_csv(pollution_path)
        
        all_comparisons = {}
        
        for pollutant in POLLUTANTS:
            logger.info(f"Creating visualizations for {pollutant}...")
            
            # Create features
            df = self.engineer.create_all_features(
                self.traffic_data, self.pollution_data, pollutant
            )
            X, y = self.engineer.prepare_features_and_target(df, pollutant)
            
            # Preprocess
            X_train, X_test, y_train, y_test = self.preprocessor.prepare_train_test_data(X, y)
            
            # Load models
            models = self.trainer.load_models(pollutant)
            
            # Get comparison table
            comparison_df = self.evaluator.create_comparison_table(pollutant)
            all_comparisons[pollutant] = comparison_df
            
            # Visualize for each model
            for model_type in MODEL_TYPES:
                if model_type in models and models[model_type] is not None:
                    model = models[model_type]
                    
                    # Predictions using trainer (handles feature selection consistency)
                    y_test_pred = self.trainer.predict(model_type, pollutant, X_test)
                    
                    # Actual vs Predicted
                    self.visualizer.plot_actual_vs_predicted(
                        y_test.values, y_test_pred, model_type, pollutant
                    )
                    
                    # Residuals (only for best model)
                    if model_type == 'random_forest':
                        self.visualizer.plot_residuals(
                            y_test.values, y_test_pred, model_type, pollutant
                        )
                        
                        # Time series
                        self.visualizer.plot_time_series_predictions(
                            y_test.index, y_test.values, y_test_pred,
                            model_type, pollutant
                        )
                        
                        # Feature importance
                        importance_df = self.explainer.get_feature_importance(
                            model, model_type, X_train.columns.tolist()
                        )
                        self.visualizer.plot_feature_importance(
                            importance_df, model_type, pollutant
                        )
                        
                        # Category importance
                        category_df = self.explainer.get_category_importance(importance_df)
                        self.visualizer.plot_category_importance(
                            category_df, model_type, pollutant
                        )
                        
                        # MARGINAL contributions (model explainability - can be negative)
                        marginal_contrib = self.explainer.estimate_vehicle_contributions(
                            model, X_test, y_test, X_test.columns.tolist()
                        )
                        self.visualizer.plot_marginal_contributions_bar(
                            marginal_contrib, pollutant, model_type
                        )
                        
                        # EMISSION-BASED contributions (physical attribution - always positive)
                        # Extract traffic data for this pollutant
                        emission_contrib = self.explainer.estimate_emission_contributions(
                            self.traffic_data, pollutant
                        )
                        self.visualizer.plot_emission_contributions_pie(
                            emission_contrib, pollutant, model_type
                        )
            
            # Model comparison
            self.visualizer.plot_model_comparison(comparison_df, pollutant, 'R2')
            self.visualizer.plot_model_comparison(comparison_df, pollutant, 'RMSE')
            
            # Correlation heatmap
            self.visualizer.plot_correlation_heatmap(X_train, pollutant)
        
        # Cross-pollutant comparison
        self.visualizer.plot_all_pollutants_comparison(all_comparisons, 'R2')
        self.visualizer.plot_all_pollutants_comparison(all_comparisons, 'RMSE')
        
        logger.info(f"All visualizations saved to {FIGURES_DIR}")
        
    def run_full_pipeline(self, tune_hyperparameters: bool = True):
        """Run the complete pipeline."""
        print_section_header("VEHICULAR POLLUTION ESTIMATION - FULL PIPELINE")
        
        self.generate_data()
        self.train_models(tune_hyperparameters)
        self.evaluate_models()
        self.explain_models()
        self.visualize_results()
        
        print_section_header("PIPELINE COMPLETE")
        print(f"\nResults saved to:")
        print(f"  - Models: {SAVED_MODELS_DIR}")
        print(f"  - Evaluation: {RESULTS_DIR}")
        print(f"  - Visualizations: {FIGURES_DIR}")
        print()


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Vehicular Pollution Estimation Model',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py --mode full                    # Run complete pipeline
  python main.py --mode full --no-tune          # Run without hyperparameter tuning (faster)
  python main.py --mode train                   # Train models only
  python main.py --mode evaluate                # Evaluate existing models
  python main.py --mode explain                 # Generate explainability analysis
  python main.py --mode visualize               # Generate visualizations
        """
    )
    
    parser.add_argument(
        '--mode',
        type=str,
        choices=['full', 'train', 'evaluate', 'explain', 'visualize', 'generate'],
        default='full',
        help='Execution mode'
    )
    
    parser.add_argument(
        '--no-tune',
        action='store_true',
        help='Skip hyperparameter tuning (faster training)'
    )
    
    args = parser.parse_args()
    
    # Create pipeline
    pipeline = PollutionEstimationPipeline()
    
    # Execute based on mode
    try:
        if args.mode == 'full':
            pipeline.run_full_pipeline(tune_hyperparameters=not args.no_tune)
        elif args.mode == 'generate':
            pipeline.generate_data()
        elif args.mode == 'train':
            pipeline.train_models(tune_hyperparameters=not args.no_tune)
        elif args.mode == 'evaluate':
            pipeline.evaluate_models()
        elif args.mode == 'explain':
            pipeline.explain_models()
        elif args.mode == 'visualize':
            pipeline.visualize_results()
    except Exception as e:
        logger.error(f"Pipeline failed: {str(e)}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
