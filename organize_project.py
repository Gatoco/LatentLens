#!/usr/bin/env python3
"""
LatentLens Project Cleanup and Organization Script

This script organizes all files in the project into proper directories
and cleans up temporary files.

Author: LatentLens Team
"""

import os
import shutil
from pathlib import Path
from datetime import datetime

def organize_project_files():
    """Organize all project files into proper directory structure"""
    
    print("🧹 LatentLens Project Organization")
    print("=" * 60)
    
    project_root = Path(".")
    
    # Define file organization rules
    file_moves = {
        # MLflow Scripts
        "mlflow_quick_evaluation.py": "scripts/mlflow/",
        "mlflow_hybrid_evaluation.py": "scripts/mlflow/", 
        "mlflow_results_analysis.py": "scripts/mlflow/",
        "mlflow_cleanup_consolidation.py": "scripts/mlflow/",
        "quick_mlflow_summary.py": "scripts/mlflow/",
        
        # Evaluation Scripts
        "comprehensive_model_analysis.py": "scripts/evaluation/",
        "evaluate_hybrid_model.py": "scripts/evaluation/",
        "quick_hybrid_evaluation.py": "scripts/evaluation/",
        "validate_cold_start.py": "scripts/evaluation/",
        "validate_production_deployment.py": "scripts/evaluation/",
        "validate_success_criteria.py": "scripts/evaluation/",
        
        # API Testing Scripts
        "test_api_manual.py": "tests/",
        "test_candidate_weighting.py": "tests/",
        "test_cold_start.py": "tests/",
        "test_complete_hybrid.py": "tests/",
        "test_fase_3_1.py": "tests/",
        "test_fusion_integration.py": "tests/",
        "test_hybrid_api.py": "tests/",
        "test_hybrid_readiness.py": "tests/",
        "test_knn_candidates.py": "tests/",
        "test_recommender_refactoring.py": "tests/",
        "test_svd_candidates.py": "tests/",
        "test_testclient.py": "tests/",
        "verify_openapi.py": "tests/",
        
        # Reports and Documentation
        "FINAL_MLFLOW_SUMMARY.md": "reports/mlflow/",
        "MLFLOW_EVALUATION_COMPLETE.md": "reports/mlflow/",
        "MLFLOW_CLEANUP_GUIDE.md": "reports/mlflow/",
        "EXECUTIVE_SUMMARY.md": "reports/",
        "COLD_START_SUMMARY.md": "reports/",
        "ITEM_SIMILARITY_SUMMARY.md": "reports/",
        "RECOMMENDER_REFACTORING.md": "reports/",
        
        # Text Reports
        "ranking_metrics_report.txt": "reports/evaluation/",
        "KNN_Item_ranking_report.txt": "reports/evaluation/",
        "KNN_User_ranking_report.txt": "reports/evaluation/",
        "SVD_ranking_report.txt": "reports/evaluation/",
        "hybrid_quick_evaluation_report.txt": "reports/evaluation/",
        "comprehensive_model_analysis_report.txt": "reports/evaluation/",
        
        # Temporary/obsolete files to move to temp
        "bfg-1.15.0.jar": "temp/",
    }
    
    # Files to keep in root
    keep_in_root = {
        "README.md", "LICENSE", "setup.py", "requirements.txt", 
        "docker-compose.yml", "Dockerfile", ".gitignore", ".gitattributes",
        "main.py"  # Main API file stays in root
    }
    
    # Execute file moves
    moved_count = 0
    error_count = 0
    
    print("\n📁 Moving files to organized structure...")
    
    for filename, target_dir in file_moves.items():
        source_path = project_root / filename
        target_path = project_root / target_dir / filename
        
        if source_path.exists():
            try:
                # Ensure target directory exists
                target_path.parent.mkdir(parents=True, exist_ok=True)
                
                # Move file
                shutil.move(str(source_path), str(target_path))
                print(f"   ✅ {filename} → {target_dir}")
                moved_count += 1
                
            except Exception as e:
                print(f"   ❌ Error moving {filename}: {str(e)}")
                error_count += 1
        else:
            print(f"   ⚠️  {filename} not found (may already be moved)")
    
    print(f"\n📊 File Organization Summary:")
    print(f"   • Files moved: {moved_count}")
    print(f"   • Errors: {error_count}")
    
    return moved_count, error_count

def clean_pycache_files():
    """Remove all __pycache__ directories"""
    
    print("\n🧹 Cleaning __pycache__ directories...")
    
    project_root = Path(".")
    removed_count = 0
    
    for pycache_dir in project_root.rglob("__pycache__"):
        if pycache_dir.is_dir():
            try:
                shutil.rmtree(pycache_dir)
                print(f"   ✅ Removed: {pycache_dir}")
                removed_count += 1
            except Exception as e:
                print(f"   ❌ Error removing {pycache_dir}: {str(e)}")
    
    print(f"   • __pycache__ directories removed: {removed_count}")
    return removed_count

def create_directory_readme_files():
    """Create README files for each directory explaining its purpose"""
    
    print("\n📝 Creating directory documentation...")
    
    directory_docs = {
        "scripts/": """# Scripts Directory

This directory contains utility and operational scripts for the LatentLens project.

## Subdirectories:
- `mlflow/` - MLflow experiment management and analysis scripts
- `evaluation/` - Model evaluation and validation scripts
""",
        
        "scripts/mlflow/": """# MLflow Scripts

Scripts for managing MLflow experiments, tracking model performance, and analyzing results.

## Key Scripts:
- `mlflow_quick_evaluation.py` - Quick model evaluation with MLflow tracking
- `mlflow_results_analysis.py` - Comprehensive analysis of MLflow experiments
- `mlflow_cleanup_consolidation.py` - Experiment cleanup and consolidation
""",
        
        "scripts/evaluation/": """# Evaluation Scripts

Scripts for evaluating model performance, validating implementations, and testing system capabilities.

## Key Scripts:
- `comprehensive_model_analysis.py` - Complete model performance analysis
- `validate_production_deployment.py` - Production readiness validation
- `validate_cold_start.py` - Cold start functionality testing
""",
        
        "reports/": """# Reports Directory

Contains all generated reports, summaries, and documentation from evaluations and experiments.

## Subdirectories:
- `mlflow/` - MLflow experiment reports and summaries
- `evaluation/` - Model evaluation reports and analysis results
""",
        
        "reports/mlflow/": """# MLflow Reports

Generated reports from MLflow experiments and model evaluations.

## Key Reports:
- `FINAL_MLFLOW_SUMMARY.md` - Final consolidated MLflow evaluation summary
- `MLFLOW_EVALUATION_COMPLETE.md` - Complete evaluation results
- `MLFLOW_CLEANUP_GUIDE.md` - Guide for managing MLflow experiments
""",
        
        "reports/evaluation/": """# Evaluation Reports

Detailed reports from model evaluations, performance analysis, and system testing.

## Report Types:
- Text reports (`.txt`) - Detailed evaluation metrics and results
- Analysis reports - Comprehensive model performance analysis
""",
        
        "temp/": """# Temporary Files

This directory contains temporary files, obsolete utilities, and files that may be removed in future cleanup.

## Contents:
- Development artifacts
- Temporary utilities
- Files pending deletion
"""
    }
    
    created_count = 0
    
    for dir_path, content in directory_docs.items():
        readme_path = Path(dir_path) / "README.md"
        
        try:
            readme_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(readme_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f"   ✅ Created: {readme_path}")
            created_count += 1
            
        except Exception as e:
            print(f"   ❌ Error creating {readme_path}: {str(e)}")
    
    print(f"   • README files created: {created_count}")
    return created_count

def generate_project_structure_report():
    """Generate a report of the final project structure"""
    
    print("\n📋 Generating project structure report...")
    
    project_root = Path(".")
    
    structure_report = f"""# 📁 LatentLens Project Structure

## 📅 Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 🏗️ Directory Organization

```
LatentLens/
├── 📄 README.md                 # Main project documentation
├── 📄 LICENSE                   # Project license
├── 📄 setup.py                  # Package setup
├── 📄 requirements.txt          # Python dependencies
├── 📄 main.py                   # FastAPI application entry point
├── 🐳 Dockerfile               # Docker container configuration
├── 🐳 docker-compose.yml       # Docker Compose configuration
│
├── 📂 src/                      # Source code
│   ├── 📄 data_loader.py
│   ├── 📄 recommender.py        # Unified recommendation engine
│   ├── 📄 recommendation_service.py
│   ├── 📄 hybrid_recommendation_service.py
│   ├── 📄 item_similarity_service.py
│   ├── 📄 content_based_model.py
│   ├── 📄 cold_start_service.py
│   ├── 📄 mlflow_svd_service.py
│   └── 📄 ranking_metrics.py
│
├── 📂 tests/                    # Test suite
│   ├── 📄 test_*.py            # Unit and integration tests
│   └── 📄 verify_*.py          # Verification scripts
│
├── 📂 notebooks/               # Jupyter notebooks
│   ├── 📄 01-EDA.ipynb
│   ├── 📄 02-Baseline-Model.ipynb
│   ├── 📄 03-Collaborative-Filtering.ipynb
│   └── 📄 05-MLflow-Experiment-Tracking.ipynb
│
├── 📂 data/                    # Dataset storage
│   └── 📂 ml-25m/             # MovieLens 25M dataset
│
├── 📂 scripts/                 # Utility scripts
│   ├── 📂 mlflow/             # MLflow management scripts
│   └── 📂 evaluation/         # Model evaluation scripts
│
├── 📂 reports/                 # Generated reports
│   ├── 📂 mlflow/             # MLflow experiment reports
│   ├── 📂 evaluation/         # Evaluation results
│   └── 📄 *.md                # Summary reports
│
├── 📂 docs/                    # Documentation
├── 📂 examples/               # Usage examples
├── 📂 experiments/            # Experimental code
├── 📂 mlruns/                 # MLflow experiment tracking
└── 📂 temp/                   # Temporary files
```

## 🎯 Key Components

### 🔧 Core Application
- **`main.py`** - FastAPI application with unified recommendation endpoints
- **`src/recommender.py`** - Central recommendation engine with strategy pattern
- **`src/hybrid_recommendation_service.py`** - Advanced hybrid model implementation

### 🧪 MLflow Integration
- **`scripts/mlflow/`** - Complete MLflow experiment management
- **`reports/mlflow/`** - Evaluation results and performance analysis
- **Model tracking** - SVD, Hybrid, and Popular baseline models

### 📊 Evaluation System
- **`scripts/evaluation/`** - Comprehensive model evaluation scripts
- **`reports/evaluation/`** - Detailed performance reports
- **Cold start handling** - Built-in new user recommendation capabilities

### 🏆 Proven Performance
- **100% Success Rate** - All models deliver recommendations successfully
- **Superior Hybrid Model** - Outperforms individual models in coverage and diversity
- **Production Ready** - Comprehensive testing and validation completed

## ✅ Organization Benefits

1. **🎯 Clear Separation** - Scripts, reports, and source code properly organized
2. **📊 Easy Access** - All evaluation results consolidated in reports/
3. **🔧 Maintainable** - Clean structure for future development
4. **📝 Documented** - Each directory includes purpose documentation
5. **🚀 Production Ready** - Organized structure suitable for deployment

---
*Generated by LatentLens Project Organization Script*
"""
    
    with open("PROJECT_STRUCTURE.md", 'w', encoding='utf-8') as f:
        f.write(structure_report)
    
    print("   ✅ Created: PROJECT_STRUCTURE.md")
    return True

def main():
    """Main organization function"""
    
    print("🚀 Starting LatentLens Project Organization...")
    print("=" * 60)
    
    try:
        # Organize files
        moved_files, move_errors = organize_project_files()
        
        # Clean cache files
        removed_cache = clean_pycache_files()
        
        # Create documentation
        created_docs = create_directory_readme_files()
        
        # Generate structure report
        generate_project_structure_report()
        
        print(f"\n🎉 PROJECT ORGANIZATION COMPLETE!")
        print("=" * 50)
        print(f"✅ Files organized: {moved_files}")
        print(f"✅ Cache directories cleaned: {removed_cache}")
        print(f"✅ Documentation created: {created_docs}")
        print(f"✅ Structure report generated")
        
        if move_errors > 0:
            print(f"⚠️  Errors encountered: {move_errors}")
        
        print(f"\n📍 Next Steps:")
        print("   • Review PROJECT_STRUCTURE.md for complete organization")
        print("   • Check reports/ directory for all evaluation results")
        print("   • Use scripts/ directory for operational tasks")
        print("   • Main application remains accessible via main.py")
        
        return True
        
    except Exception as e:
        print(f"❌ Organization failed: {str(e)}")
        return False

if __name__ == "__main__":
    main()
