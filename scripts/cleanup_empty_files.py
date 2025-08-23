#!/usr/bin/env python3
"""
Automatic Empty Files Cleanup Script for LatentLens

This script automatically cleans up empty files in the project,
with intelligent logic to determine which files to keep, implement, or remove.

Author: LatentLens Team
License: MIT
"""

import os
import sys
import time
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class EmptyFilesCleanup:
    """Intelligent empty files cleanup manager."""

    def __init__(self, project_root="."):
        """
        Initialize the cleanup manager.

        Args:
            project_root (str): Root directory of the project
        """
        self.project_root = Path(project_root)
        self.empty_files = []
        self.cleanup_actions = {
            "keep_empty": [],  # Files that should remain empty
            "implement_content": [],  # Files that need implementation
            "safe_to_remove": [],  # Files safe to delete
            "review_required": [],  # Files needing manual review
        }

    def scan_empty_files(self):
        """Scan the project for empty files."""
        logger.info("Scanning for empty files...")

        self.empty_files = []

        # Exclude certain directories
        exclude_dirs = {
            "venv",
            ".venv",
            "node_modules",
            ".git",
            "__pycache__",
            ".pytest_cache",
            "LatentLens.egg-info",
            "build",
            "dist",
        }

        for file_path in self.project_root.rglob("*"):
            if (
                file_path.is_file()
                and file_path.stat().st_size == 0
                and not any(
                    exclude_dir in file_path.parts for exclude_dir in exclude_dirs
                )
            ):
                self.empty_files.append(file_path)

        logger.info(f"Found {len(self.empty_files)} empty files")
        return self.empty_files

    def categorize_files(self):
        """Categorize empty files based on intelligent rules."""
        logger.info("Categorizing empty files...")

        for file_path in self.empty_files:
            relative_path = file_path.relative_to(self.project_root)
            file_name = file_path.name
            parent_dir = file_path.parent.name

            # Files that should remain empty (infrastructure)
            if self._should_keep_empty(file_path, file_name):
                self.cleanup_actions["keep_empty"].append(relative_path)

            # Files that need implementation (functional)
            elif self._needs_implementation(file_path, file_name, parent_dir):
                self.cleanup_actions["implement_content"].append(relative_path)

            # Files safe to remove (duplicates, temporary)
            elif self._is_safe_to_remove(file_path, file_name, parent_dir):
                self.cleanup_actions["safe_to_remove"].append(relative_path)

            # Files requiring manual review
            else:
                self.cleanup_actions["review_required"].append(relative_path)

        logger.info("File categorization completed")

    def _should_keep_empty(self, file_path, file_name):
        """Determine if file should remain empty."""
        # Git keep files
        if file_name == ".gitkeep":
            return True

        # Python package init files (can be empty)
        if file_name == "__init__.py":
            return True

        # Type hint files
        if file_name.endswith(".pyi") or file_name == "py.typed":
            return True

        return False

    def _needs_implementation(self, file_path, file_name, parent_dir):
        """Determine if file needs content implementation."""
        # Test files that should have content
        if (
            file_name.startswith("test_")
            and file_name.endswith(".py")
            and parent_dir in ["tests", "models"]
        ):
            return True

        # Script files in scripts directory
        if (
            file_name.endswith(".py")
            and "scripts" in str(file_path)
            and not file_name.startswith("__")
        ):
            return True

        # Documentation files that should have content
        if file_name.endswith(".md") and any(
            keyword in file_name.upper()
            for keyword in ["PLAN", "REPORT", "SUMMARY", "GUIDE", "STATUS"]
        ):
            return True

        return False

    def _is_safe_to_remove(self, file_path, file_name, parent_dir):
        """Determine if file is safe to remove."""
        # Temporary files
        if file_name.startswith("temp_") or file_name.startswith("tmp_"):
            return True

        # Backup files
        if file_name.endswith(".bak") or file_name.endswith(".backup"):
            return True

        # Log files (usually regenerated)
        if file_name.endswith(".log") and file_path.parent.name == "logs":
            return True

        # Demo files that are empty
        if "demo" in file_name.lower() and file_name.endswith(".py"):
            return True

        return False

    def execute_cleanup(self, auto_remove=False, auto_implement=False):
        """Execute the cleanup actions."""
        logger.info("Executing cleanup actions...")

        results = {
            "files_removed": 0,
            "files_implemented": 0,
            "files_kept": 0,
            "errors": [],
        }

        # Remove files marked as safe to remove
        if auto_remove and self.cleanup_actions["safe_to_remove"]:
            for file_path in self.cleanup_actions["safe_to_remove"]:
                try:
                    full_path = self.project_root / file_path
                    full_path.unlink()
                    logger.info(f"Removed: {file_path}")
                    results["files_removed"] += 1
                except Exception as e:
                    error_msg = f"Failed to remove {file_path}: {e}"
                    logger.error(error_msg)
                    results["errors"].append(error_msg)

        # Implement basic content for files needing implementation
        if auto_implement and self.cleanup_actions["implement_content"]:
            for file_path in self.cleanup_actions["implement_content"]:
                try:
                    content = self._generate_basic_content(file_path)
                    if content:
                        full_path = self.project_root / file_path
                        full_path.write_text(content, encoding="utf-8")
                        logger.info(f"Implemented basic content: {file_path}")
                        results["files_implemented"] += 1
                except Exception as e:
                    error_msg = f"Failed to implement content for {file_path}: {e}"
                    logger.error(error_msg)
                    results["errors"].append(error_msg)

        # Count files kept empty
        results["files_kept"] = len(self.cleanup_actions["keep_empty"])

        logger.info(
            f"Cleanup completed: {results['files_removed']} removed, "
            f"{results['files_implemented']} implemented, "
            f"{results['files_kept']} kept empty"
        )

        return results

    def _generate_basic_content(self, file_path):
        """Generate basic content for empty files."""
        file_name = Path(file_path).name

        # Test files
        if file_name.startswith("test_") and file_name.endswith(".py"):
            module_name = file_name[5:-3]  # Remove 'test_' and '.py'
            return f'''"""
Test module for {module_name}

This module contains tests for the {module_name} component.
Tests should be implemented to verify functionality and edge cases.

Author: LatentLens Team
License: MIT
"""

import pytest


class Test{module_name.title().replace('_', '')}:
    """Test class for {module_name} functionality."""
    
    def test_placeholder(self):
        """Placeholder test - implement actual tests."""
        # TODO: Implement actual tests for {module_name}
        assert True, "Placeholder test - needs implementation"


if __name__ == "__main__":
    pytest.main([__file__])
'''

        # Script files
        if file_name.endswith(".py") and "scripts" in str(file_path):
            script_name = file_name[:-3]  # Remove '.py'
            return f'''#!/usr/bin/env python3
"""
{script_name.replace('_', ' ').title()} Script for LatentLens

This script provides {script_name.replace('_', ' ')} functionality.
Implementation details should be added based on requirements.

Author: LatentLens Team
License: MIT
"""

import sys
import os
import logging

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """Main function for {script_name}."""
    logger.info("Starting {script_name}...")
    
    # TODO: Implement {script_name} functionality
    print(f"{{script_name}} script executed successfully!")
    
    logger.info("{script_name} completed")


if __name__ == "__main__":
    main()
'''

        # Documentation files
        if file_name.endswith(".md"):
            doc_title = file_name[:-3].replace("_", " ").title()
            return f"""# {doc_title}

## Overview

This document provides {doc_title.lower()} for the LatentLens project.

## Content

*This section needs to be implemented with relevant content.*

## Status

- **Created:** {time.strftime('%Y-%m-%d')}
- **Status:** Draft - Needs Implementation
- **Author:** LatentLens Team

## Notes

This document was auto-generated as a placeholder and requires manual completion with actual content.
"""

        return None

    def print_report(self):
        """Print detailed cleanup report."""
        print("\n" + "=" * 60)
        print("EMPTY FILES CLEANUP REPORT")
        print("=" * 60)

        for action, files in self.cleanup_actions.items():
            if files:
                action_title = action.replace("_", " ").title()
                print(f"\n{action_title} ({len(files)} files):")
                for file_path in files:
                    print(f"  - {file_path}")

        print(f"\nSUMMARY:")
        print(f"  Total empty files: {len(self.empty_files)}")
        for action, files in self.cleanup_actions.items():
            print(f"  {action.replace('_', ' ').title()}: {len(files)}")

        print("\n" + "=" * 60)

    def interactive_cleanup(self):
        """Run interactive cleanup process."""
        print("Empty Files Cleanup - Interactive Mode")
        print("=" * 40)

        # Ask about automatic removal
        if self.cleanup_actions["safe_to_remove"]:
            print(
                f"\nFound {len(self.cleanup_actions['safe_to_remove'])} files safe to remove:"
            )
            for file_path in self.cleanup_actions["safe_to_remove"][:5]:  # Show first 5
                print(f"  - {file_path}")
            if len(self.cleanup_actions["safe_to_remove"]) > 5:
                print(
                    f"  ... and {len(self.cleanup_actions['safe_to_remove']) - 5} more"
                )

            remove_response = input("\nRemove these files? (y/N): ").strip().lower()
            auto_remove = remove_response in ["y", "yes"]
        else:
            auto_remove = False

        # Ask about automatic implementation
        if self.cleanup_actions["implement_content"]:
            print(
                f"\nFound {len(self.cleanup_actions['implement_content'])} files needing basic content:"
            )
            for file_path in self.cleanup_actions["implement_content"][
                :5
            ]:  # Show first 5
                print(f"  - {file_path}")
            if len(self.cleanup_actions["implement_content"]) > 5:
                print(
                    f"  ... and {len(self.cleanup_actions['implement_content']) - 5} more"
                )

            implement_response = (
                input("\nAdd basic placeholder content to these files? (y/N): ")
                .strip()
                .lower()
            )
            auto_implement = implement_response in ["y", "yes"]
        else:
            auto_implement = False

        # Execute cleanup
        results = self.execute_cleanup(
            auto_remove=auto_remove, auto_implement=auto_implement
        )

        print(f"\nCleanup Results:")
        print(f"  Files removed: {results['files_removed']}")
        print(f"  Files implemented: {results['files_implemented']}")
        print(f"  Files kept empty: {results['files_kept']}")

        if results["errors"]:
            print(f"  Errors: {len(results['errors'])}")
            for error in results["errors"]:
                print(f"    - {error}")


def main():
    """Main cleanup function."""
    print("LatentLens Empty Files Cleanup Tool")
    print("=" * 35)

    try:
        # Initialize cleanup manager
        cleanup = EmptyFilesCleanup()

        # Scan for empty files
        empty_files = cleanup.scan_empty_files()

        if not empty_files:
            print("No empty files found in the project!")
            return

        # Categorize files
        cleanup.categorize_files()

        # Print report
        cleanup.print_report()

        # Ask if user wants to proceed with interactive cleanup
        print("\nOptions:")
        print("1. Interactive cleanup (recommended)")
        print("2. View report only")

        choice = input("\nSelect option (1/2): ").strip()

        if choice == "1":
            cleanup.interactive_cleanup()
        else:
            print("Cleanup report completed. No files were modified.")

    except Exception as e:
        logger.error(f"Cleanup failed: {e}")
        raise


if __name__ == "__main__":
    main()
