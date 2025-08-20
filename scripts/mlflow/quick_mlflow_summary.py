#!/usr/bin/env python3
"""
Quick MLflow Summary Script
"""

import mlflow
import os

# Set tracking URI
mlflow.set_tracking_uri("./mlruns")

# Get client
client = mlflow.tracking.MlflowClient()

print("🔍 MLflow Experiments Summary")
print("=" * 50)

# Get all experiments
experiments = client.search_experiments()

for exp in experiments:
    print(f"\n📊 Experiment: {exp.name}")
    print(f"   ID: {exp.experiment_id}")
    
    # Get runs for this experiment
    runs = client.search_runs([exp.experiment_id])
    print(f"   Runs: {len(runs)}")
    
    for run in runs[:3]:  # Show first 3 runs
        print(f"      • {run.info.run_name}")
        print(f"        Status: {run.info.status}")
        print(f"        Metrics: {len(run.data.metrics)} items")
        
        # Show key metrics if available
        metrics = run.data.metrics
        key_metrics = ['success_rate', 'catalog_coverage', 'precision_at_10', 'hybrid_vs_svd_success_ratio']
        
        for metric in key_metrics:
            if metric in metrics:
                print(f"        {metric}: {metrics[metric]:.4f}")

print(f"\n✅ Summary completed!")
