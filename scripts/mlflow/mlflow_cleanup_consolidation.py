#!/usr/bin/env python3
"""
MLflow Cleanup and Consolidation Script for LatentLens

This script consolidates and cleans up MLflow experiments and runs,
removing duplicates, organizing data, and optimizing storage.

Author: LatentLens Team
License: MIT
"""

import os
import sys
import time
import logging
import argparse
import json
import shutil
from datetime import datetime, timedelta
from pathlib import Path
from collections import defaultdict

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# MLflow imports with error handling
try:
    import mlflow
    from mlflow.tracking import MlflowClient

    MLFLOW_AVAILABLE = True
except ImportError:
    logger.warning("MLflow not available. Only file-based cleanup will be performed.")
    MLFLOW_AVAILABLE = False


class MLflowCleanupConsolidator:
    """MLflow experiment cleanup and consolidation utility."""

    def __init__(self, tracking_uri=None, mlruns_path="mlruns", dry_run=False):
        """
        Initialize the cleanup consolidator.

        Args:
            tracking_uri (str): MLflow tracking server URI
            mlruns_path (str): Path to mlruns directory
            dry_run (bool): If True, only show what would be cleaned
        """
        self.tracking_uri = tracking_uri
        self.mlruns_path = Path(mlruns_path)
        self.dry_run = dry_run
        self.cleanup_stats = {
            "experiments_processed": 0,
            "runs_processed": 0,
            "duplicate_runs_found": 0,
            "failed_runs_found": 0,
            "old_runs_found": 0,
            "artifacts_cleaned": 0,
            "space_saved_mb": 0.0,
        }

        if MLFLOW_AVAILABLE and tracking_uri:
            self._setup_mlflow_client()

    def _setup_mlflow_client(self):
        """Setup MLflow client connection."""
        try:
            if self.tracking_uri:
                mlflow.set_tracking_uri(self.tracking_uri)

            self.client = MlflowClient()
            logger.info(
                f"Connected to MLflow tracking server: {self.tracking_uri or 'local'}"
            )

        except Exception as e:
            logger.error(f"Failed to setup MLflow client: {e}")
            global MLFLOW_AVAILABLE
            MLFLOW_AVAILABLE = False

    def analyze_experiments(self):
        """Analyze all experiments for cleanup opportunities."""
        logger.info("Analyzing MLflow experiments...")

        analysis = {
            "experiments": [],
            "total_runs": 0,
            "duplicate_candidates": [],
            "failed_runs": [],
            "old_runs": [],
        }

        if MLFLOW_AVAILABLE:
            try:
                experiments = self.client.list_experiments()

                for experiment in experiments:
                    exp_analysis = self._analyze_single_experiment(experiment)
                    analysis["experiments"].append(exp_analysis)
                    analysis["total_runs"] += exp_analysis["run_count"]
                    analysis["duplicate_candidates"].extend(
                        exp_analysis["duplicate_candidates"]
                    )
                    analysis["failed_runs"].extend(exp_analysis["failed_runs"])
                    analysis["old_runs"].extend(exp_analysis["old_runs"])

            except Exception as e:
                logger.error(f"Failed to analyze experiments: {e}")

        else:
            # File-based analysis
            analysis = self._analyze_experiments_file_based()

        self.analysis = analysis

        logger.info(f"Analysis complete:")
        logger.info(f"  Total experiments: {len(analysis['experiments'])}")
        logger.info(f"  Total runs: {analysis['total_runs']}")
        logger.info(f"  Duplicate candidates: {len(analysis['duplicate_candidates'])}")
        logger.info(f"  Failed runs: {len(analysis['failed_runs'])}")
        logger.info(f"  Old runs: {len(analysis['old_runs'])}")

        return analysis

    def _analyze_single_experiment(self, experiment):
        """Analyze a single experiment for cleanup opportunities."""
        exp_id = experiment.experiment_id
        exp_name = experiment.name

        logger.info(f"Analyzing experiment: {exp_name} ({exp_id})")

        try:
            runs = self.client.search_runs(experiment_ids=[exp_id])

            exp_analysis = {
                "experiment_id": exp_id,
                "experiment_name": exp_name,
                "run_count": len(runs),
                "duplicate_candidates": [],
                "failed_runs": [],
                "old_runs": [],
                "total_artifacts_size": 0,
            }

            # Group runs by parameters to find duplicates
            param_groups = defaultdict(list)

            for run in runs:
                # Check for failed runs
                if run.info.status == "FAILED":
                    exp_analysis["failed_runs"].append(
                        {
                            "run_id": run.info.run_id,
                            "experiment_id": exp_id,
                            "start_time": run.info.start_time,
                            "end_time": run.info.end_time,
                        }
                    )

                # Check for old runs (older than 30 days)
                if run.info.start_time:
                    run_date = datetime.fromtimestamp(run.info.start_time / 1000)
                    if run_date < datetime.now() - timedelta(days=30):
                        exp_analysis["old_runs"].append(
                            {
                                "run_id": run.info.run_id,
                                "experiment_id": exp_id,
                                "start_time": run.info.start_time,
                                "age_days": (datetime.now() - run_date).days,
                            }
                        )

                # Group by parameters to find potential duplicates
                param_key = json.dumps(run.data.params, sort_keys=True)
                param_groups[param_key].append(
                    {
                        "run_id": run.info.run_id,
                        "start_time": run.info.start_time,
                        "status": run.info.status,
                        "metrics": run.data.metrics,
                    }
                )

            # Find duplicate candidates
            for param_key, group_runs in param_groups.items():
                if len(group_runs) > 1:
                    # Sort by start time, keep the latest successful run
                    successful_runs = [
                        r for r in group_runs if r["status"] == "FINISHED"
                    ]
                    if len(successful_runs) > 1:
                        successful_runs.sort(
                            key=lambda x: x["start_time"], reverse=True
                        )
                        duplicates = successful_runs[1:]  # All but the latest

                        exp_analysis["duplicate_candidates"].extend(
                            [
                                {
                                    "run_id": run["run_id"],
                                    "experiment_id": exp_id,
                                    "reason": "duplicate_parameters",
                                    "keep_run_id": successful_runs[0]["run_id"],
                                }
                                for run in duplicates
                            ]
                        )

            return exp_analysis

        except Exception as e:
            logger.error(f"Failed to analyze experiment {exp_name}: {e}")
            return {
                "experiment_id": exp_id,
                "experiment_name": exp_name,
                "run_count": 0,
                "duplicate_candidates": [],
                "failed_runs": [],
                "old_runs": [],
                "error": str(e),
            }

    def cleanup_duplicate_runs(self):
        """Clean up duplicate runs identified in analysis."""
        if not hasattr(self, "analysis"):
            logger.warning("Run analyze_experiments() first")
            return

        duplicate_candidates = self.analysis["duplicate_candidates"]

        if not duplicate_candidates:
            logger.info("No duplicate runs found to clean up")
            return

        logger.info(f"Cleaning up {len(duplicate_candidates)} duplicate runs...")

        for duplicate in duplicate_candidates:
            run_id = duplicate["run_id"]
            exp_id = duplicate["experiment_id"]

            if self.dry_run:
                logger.info(
                    f"Would delete duplicate run: {run_id} (experiment: {exp_id})"
                )
            else:
                try:
                    if MLFLOW_AVAILABLE:
                        self.client.delete_run(run_id)
                        logger.info(f"Deleted duplicate run: {run_id}")
                    else:
                        # File-based deletion
                        run_path = self.mlruns_path / exp_id / run_id
                        if run_path.exists():
                            shutil.rmtree(run_path)
                            logger.info(f"Deleted duplicate run directory: {run_path}")

                    self.cleanup_stats["duplicate_runs_found"] += 1

                except Exception as e:
                    logger.error(f"Failed to delete duplicate run {run_id}: {e}")


def main():
    """Main cleanup function."""
    parser = argparse.ArgumentParser(
        description="Clean up and consolidate MLflow experiments and runs"
    )
    parser.add_argument("--tracking-uri", type=str, help="MLflow tracking server URI")
    parser.add_argument(
        "--mlruns-path",
        type=str,
        default="mlruns",
        help="Path to mlruns directory (default: mlruns)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be cleaned without actually doing it",
    )

    args = parser.parse_args()

    try:
        # Initialize consolidator
        consolidator = MLflowCleanupConsolidator(
            tracking_uri=args.tracking_uri,
            mlruns_path=args.mlruns_path,
            dry_run=args.dry_run,
        )

        # Run analysis
        consolidator.analyze_experiments()
        consolidator.cleanup_duplicate_runs()

        logger.info("MLflow cleanup completed successfully!")

    except Exception as e:
        logger.error(f"Cleanup failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
