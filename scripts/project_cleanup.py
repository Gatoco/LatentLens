#!/usr/bin/env python3
"""
Project Cleanup Script for LatentLens

This script performs comprehensive cleanup of the LatentLens project,
removing temporary files, optimizing structure, and ensuring clean state.

Author: LatentLens Team
License: MIT
"""

import os
import sys
import shutil
import glob
import logging
import argparse
from pathlib import Path
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class ProjectCleaner:
    """Comprehensive project cleanup utility."""

    def __init__(self, project_root=None, dry_run=False):
        """
        Initialize the project cleaner.

        Args:
            project_root (str): Root directory of the project
            dry_run (bool): If True, only show what would be cleaned
        """
        self.project_root = Path(project_root) if project_root else Path.cwd()
        self.dry_run = dry_run
        self.cleaned_files = []
        self.cleaned_dirs = []
        self.total_space_freed = 0

    def clean_python_cache(self):
        """Remove Python cache files and directories."""
        logger.info("Cleaning Python cache files...")

        cache_patterns = [
            "**/__pycache__",
            "**/*.pyc",
            "**/*.pyo",
            "**/*.pyd",
            "**/.pytest_cache",
            "**/*.egg-info",
            "**/build",
            "**/dist",
        ]

        for pattern in cache_patterns:
            for item in self.project_root.glob(pattern):
                if item.exists():
                    size = self._get_size(item)
                    if self.dry_run:
                        logger.info(f"Would remove: {item} ({size} bytes)")
                    else:
                        if item.is_dir():
                            shutil.rmtree(item)
                            self.cleaned_dirs.append(str(item))
                        else:
                            item.unlink()
                            self.cleaned_files.append(str(item))
                        logger.info(f"Removed: {item} ({size} bytes)")
                    self.total_space_freed += size

    def clean_temp_files(self):
        """Remove temporary files and directories."""
        logger.info("Cleaning temporary files...")

        temp_patterns = [
            "**/.DS_Store",
            "**/Thumbs.db",
            "**/*.tmp",
            "**/*.temp",
            "**/*.log",
            "**/*.bak",
            "**/*~",
            "**/.coverage",
            "**/htmlcov",
            "**/.tox",
            "**/.mypy_cache",
        ]

        for pattern in temp_patterns:
            for item in self.project_root.glob(pattern):
                if item.exists():
                    size = self._get_size(item)
                    if self.dry_run:
                        logger.info(f"Would remove: {item} ({size} bytes)")
                    else:
                        if item.is_dir():
                            shutil.rmtree(item)
                            self.cleaned_dirs.append(str(item))
                        else:
                            item.unlink()
                            self.cleaned_files.append(str(item))
                        logger.info(f"Removed: {item} ({size} bytes)")
                    self.total_space_freed += size

    def clean_ide_files(self):
        """Remove IDE-specific files and directories."""
        logger.info("Cleaning IDE files...")

        ide_patterns = [
            "**/.vscode",
            "**/.idea",
            "**/*.swp",
            "**/*.swo",
            "**/.vim",
            "**/.project",
            "**/.classpath",
            "**/.settings",
        ]

        for pattern in ide_patterns:
            for item in self.project_root.glob(pattern):
                if item.exists():
                    size = self._get_size(item)
                    if self.dry_run:
                        logger.info(f"Would remove: {item} ({size} bytes)")
                    else:
                        if item.is_dir():
                            shutil.rmtree(item)
                            self.cleaned_dirs.append(str(item))
                        else:
                            item.unlink()
                            self.cleaned_files.append(str(item))
                        logger.info(f"Removed: {item} ({size} bytes)")
                    self.total_space_freed += size

    def clean_node_modules(self):
        """Remove Node.js modules if present."""
        logger.info("Cleaning Node.js modules...")

        node_patterns = ["**/node_modules", "**/.npm", "**/package-lock.json"]

        for pattern in node_patterns:
            for item in self.project_root.glob(pattern):
                if item.exists():
                    size = self._get_size(item)
                    if self.dry_run:
                        logger.info(f"Would remove: {item} ({size} bytes)")
                    else:
                        if item.is_dir():
                            shutil.rmtree(item)
                            self.cleaned_dirs.append(str(item))
                        else:
                            item.unlink()
                            self.cleaned_files.append(str(item))
                        logger.info(f"Removed: {item} ({size} bytes)")
                    self.total_space_freed += size

    def clean_jupyter_checkpoints(self):
        """Remove Jupyter notebook checkpoints."""
        logger.info("Cleaning Jupyter checkpoints...")

        checkpoint_dirs = list(self.project_root.glob("**/.ipynb_checkpoints"))

        for checkpoint_dir in checkpoint_dirs:
            if checkpoint_dir.exists():
                size = self._get_size(checkpoint_dir)
                if self.dry_run:
                    logger.info(f"Would remove: {checkpoint_dir} ({size} bytes)")
                else:
                    shutil.rmtree(checkpoint_dir)
                    self.cleaned_dirs.append(str(checkpoint_dir))
                    logger.info(f"Removed: {checkpoint_dir} ({size} bytes)")
                self.total_space_freed += size

    def clean_mlflow_artifacts(self):
        """Clean up MLflow temporary artifacts."""
        logger.info("Cleaning MLflow artifacts...")

        mlflow_patterns = [
            "**/mlruns/**/artifacts/tmp*",
            "**/mlruns/**/meta.yaml.tmp",
            "**/.mlflow_tracking",
        ]

        for pattern in mlflow_patterns:
            for item in self.project_root.glob(pattern):
                if item.exists():
                    size = self._get_size(item)
                    if self.dry_run:
                        logger.info(f"Would remove: {item} ({size} bytes)")
                    else:
                        if item.is_dir():
                            shutil.rmtree(item)
                            self.cleaned_dirs.append(str(item))
                        else:
                            item.unlink()
                            self.cleaned_files.append(str(item))
                        logger.info(f"Removed: {item} ({size} bytes)")
                    self.total_space_freed += size

    def remove_empty_directories(self):
        """Remove empty directories."""
        logger.info("Removing empty directories...")

        # Walk the directory tree bottom-up
        for root, dirs, files in os.walk(self.project_root, topdown=False):
            for dir_name in dirs:
                dir_path = Path(root) / dir_name
                if dir_path.exists() and not any(dir_path.iterdir()):
                    if self.dry_run:
                        logger.info(f"Would remove empty directory: {dir_path}")
                    else:
                        dir_path.rmdir()
                        self.cleaned_dirs.append(str(dir_path))
                        logger.info(f"Removed empty directory: {dir_path}")

    def optimize_git_repository(self):
        """Optimize Git repository if present."""
        git_dir = self.project_root / ".git"
        if git_dir.exists():
            logger.info("Optimizing Git repository...")

            if not self.dry_run:
                try:
                    # Run git gc to clean up the repository
                    import subprocess

                    result = subprocess.run(
                        ["git", "gc", "--aggressive", "--prune=now"],
                        cwd=self.project_root,
                        capture_output=True,
                        text=True,
                    )
                    if result.returncode == 0:
                        logger.info("Git repository optimized successfully")
                    else:
                        logger.warning(f"Git optimization failed: {result.stderr}")
                except Exception as e:
                    logger.warning(f"Could not optimize Git repository: {e}")
            else:
                logger.info("Would optimize Git repository")

    def clean_test_artifacts(self):
        """Clean test artifacts and reports."""
        logger.info("Cleaning test artifacts...")

        test_patterns = [
            "**/.pytest_cache",
            "**/htmlcov",
            "**/.coverage",
            "**/coverage.xml",
            "**/test-results.xml",
            "**/junit.xml",
        ]

        for pattern in test_patterns:
            for item in self.project_root.glob(pattern):
                if item.exists():
                    size = self._get_size(item)
                    if self.dry_run:
                        logger.info(f"Would remove: {item} ({size} bytes)")
                    else:
                        if item.is_dir():
                            shutil.rmtree(item)
                            self.cleaned_dirs.append(str(item))
                        else:
                            item.unlink()
                            self.cleaned_files.append(str(item))
                        logger.info(f"Removed: {item} ({size} bytes)")
                    self.total_space_freed += size

    def _get_size(self, path):
        """Get the size of a file or directory in bytes."""
        if path.is_file():
            return path.stat().st_size
        elif path.is_dir():
            total = 0
            for item in path.rglob("*"):
                if item.is_file():
                    try:
                        total += item.stat().st_size
                    except (OSError, FileNotFoundError):
                        # Handle broken symlinks or permission issues
                        pass
            return total
        return 0

    def generate_report(self):
        """Generate cleanup report."""
        report = {
            "timestamp": datetime.now().isoformat(),
            "project_root": str(self.project_root),
            "dry_run": self.dry_run,
            "files_cleaned": len(self.cleaned_files),
            "directories_cleaned": len(self.cleaned_dirs),
            "total_space_freed_bytes": self.total_space_freed,
            "total_space_freed_mb": round(self.total_space_freed / (1024 * 1024), 2),
            "cleaned_files": self.cleaned_files,
            "cleaned_directories": self.cleaned_dirs,
        }
        return report

    def run_full_cleanup(self):
        """Run complete project cleanup."""
        logger.info(
            f"Starting {'dry run' if self.dry_run else 'cleanup'} of project: {self.project_root}"
        )

        # Run all cleanup methods
        self.clean_python_cache()
        self.clean_temp_files()
        self.clean_ide_files()
        self.clean_node_modules()
        self.clean_jupyter_checkpoints()
        self.clean_mlflow_artifacts()
        self.clean_test_artifacts()
        self.remove_empty_directories()

        # Optimize Git if not dry run
        if not self.dry_run:
            self.optimize_git_repository()

        # Generate and return report
        report = self.generate_report()

        logger.info(f"Cleanup completed:")
        logger.info(f"  Files cleaned: {report['files_cleaned']}")
        logger.info(f"  Directories cleaned: {report['directories_cleaned']}")
        logger.info(f"  Space freed: {report['total_space_freed_mb']} MB")

        return report


def main():
    """Main cleanup function."""
    parser = argparse.ArgumentParser(
        description="Clean up LatentLens project files and directories"
    )
    parser.add_argument(
        "--project-root",
        type=str,
        help="Root directory of the project (default: current directory)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be cleaned without actually doing it",
    )
    parser.add_argument(
        "--output", type=str, help="Output file for cleanup report (JSON format)"
    )
    parser.add_argument(
        "--quick", action="store_true", help="Quick cleanup (cache and temp files only)"
    )

    args = parser.parse_args()

    try:
        # Initialize cleaner
        cleaner = ProjectCleaner(project_root=args.project_root, dry_run=args.dry_run)

        # Run cleanup
        if args.quick:
            logger.info("Running quick cleanup...")
            cleaner.clean_python_cache()
            cleaner.clean_temp_files()
        else:
            logger.info("Running full cleanup...")
            report = cleaner.run_full_cleanup()

        # Save report if requested
        if args.output:
            import json

            with open(args.output, "w") as f:
                json.dump(report, f, indent=2)
            logger.info(f"Cleanup report saved to {args.output}")

        logger.info("Project cleanup completed successfully!")

    except Exception as e:
        logger.error(f"Cleanup failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
