#!/usr/bin/env python3
"""
CI/CD Pipeline Validation Script for LatentLens

This script validates the CI/CD pipeline configuration and ensures
all components are properly set up for automated testing and deployment.

Author: LatentLens Team
License: MIT
"""

import os
import sys
import json
import yaml
import logging
import argparse
import subprocess
from pathlib import Path
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class CICDValidator:
    """Validator for CI/CD pipeline configuration and components."""

    def __init__(self, project_root=None):
        """
        Initialize CI/CD validator.

        Args:
            project_root (str): Root directory of the project
        """
        self.project_root = Path(project_root) if project_root else Path.cwd()
        self.validation_results = {}

    def validate_git_configuration(self):
        """Validate Git repository configuration."""
        logger.info("Validating Git configuration...")

        git_checks = {
            "git_repository": False,
            "git_hooks": False,
            "gitignore": False,
            "git_config": False,
            "remote_configured": False,
        }

        # Check if .git directory exists
        git_dir = self.project_root / ".git"
        if git_dir.exists():
            git_checks["git_repository"] = True
            logger.info("Git repository found")
        else:
            logger.warning("No Git repository found")

        # Check for .gitignore
        gitignore_file = self.project_root / ".gitignore"
        if gitignore_file.exists():
            git_checks["gitignore"] = True
            logger.info(".gitignore file found")

            # Validate common entries
            gitignore_content = gitignore_file.read_text()
            required_patterns = [
                "__pycache__",
                "*.pyc",
                ".env",
                "venv/",
                "node_modules/",
            ]

            missing_patterns = []
            for pattern in required_patterns:
                if pattern not in gitignore_content:
                    missing_patterns.append(pattern)

            if missing_patterns:
                logger.warning(f"Missing .gitignore patterns: {missing_patterns}")
        else:
            logger.warning(".gitignore file not found")

        # Check Git hooks
        hooks_dir = git_dir / "hooks"
        if hooks_dir.exists():
            hook_files = list(hooks_dir.glob("*"))
            if hook_files:
                git_checks["git_hooks"] = True
                logger.info(f"Git hooks found: {[h.name for h in hook_files]}")

        # Check Git configuration
        try:
            result = subprocess.run(
                ["git", "config", "--list"],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=10,
            )
            if result.returncode == 0:
                git_checks["git_config"] = True

                # Check for remote
                if "remote.origin.url" in result.stdout:
                    git_checks["remote_configured"] = True
                    logger.info("Git remote configured")

        except (subprocess.TimeoutExpired, FileNotFoundError):
            logger.warning("Could not validate Git configuration")

        self.validation_results["git"] = git_checks
        logger.info("Git configuration validation completed")

    def validate_github_actions(self):
        """Validate GitHub Actions workflow configuration."""
        logger.info("Validating GitHub Actions...")

        github_checks = {
            "workflows_directory": False,
            "ci_workflow": False,
            "cd_workflow": False,
            "workflow_syntax": False,
            "required_jobs": False,
        }

        # Check for .github/workflows directory
        workflows_dir = self.project_root / ".github" / "workflows"
        if workflows_dir.exists():
            github_checks["workflows_directory"] = True
            logger.info("GitHub workflows directory found")

            # Look for workflow files
            workflow_files = list(workflows_dir.glob("*.yml")) + list(
                workflows_dir.glob("*.yaml")
            )

            if workflow_files:
                logger.info(f"Found workflow files: {[f.name for f in workflow_files]}")

                # Check for CI workflow
                ci_patterns = ["ci", "test", "build"]
                for workflow_file in workflow_files:
                    if any(
                        pattern in workflow_file.name.lower() for pattern in ci_patterns
                    ):
                        github_checks["ci_workflow"] = True
                        logger.info(f"CI workflow found: {workflow_file.name}")
                        break

                # Check for CD workflow
                cd_patterns = ["cd", "deploy", "release"]
                for workflow_file in workflow_files:
                    if any(
                        pattern in workflow_file.name.lower() for pattern in cd_patterns
                    ):
                        github_checks["cd_workflow"] = True
                        logger.info(f"CD workflow found: {workflow_file.name}")
                        break

                # Validate workflow syntax
                try:
                    for workflow_file in workflow_files:
                        with open(workflow_file, "r") as f:
                            workflow_content = yaml.safe_load(f)

                        if (
                            isinstance(workflow_content, dict)
                            and "jobs" in workflow_content
                        ):
                            github_checks["workflow_syntax"] = True

                            # Check for required jobs
                            jobs = workflow_content["jobs"]
                            required_job_types = ["test", "lint", "build"]

                            job_names = list(jobs.keys())
                            found_jobs = []

                            for job_name in job_names:
                                for job_type in required_job_types:
                                    if job_type in job_name.lower():
                                        found_jobs.append(job_type)
                                        break

                            if len(found_jobs) >= 2:  # At least 2 required job types
                                github_checks["required_jobs"] = True
                                logger.info(f"Required jobs found: {found_jobs}")

                except Exception as e:
                    logger.warning(f"Could not validate workflow syntax: {e}")
            else:
                logger.warning("No workflow files found in .github/workflows")
        else:
            logger.warning("GitHub workflows directory not found")

        self.validation_results["github_actions"] = github_checks
        logger.info("GitHub Actions validation completed")

    def validate_docker_configuration(self):
        """Validate Docker configuration for containerized deployments."""
        logger.info("Validating Docker configuration...")

        docker_checks = {
            "dockerfile": False,
            "docker_compose": False,
            "dockerignore": False,
            "multi_stage_build": False,
            "health_check": False,
        }

        # Check for Dockerfile
        dockerfile_paths = [
            self.project_root / "Dockerfile",
            self.project_root / "docker" / "Dockerfile",
        ]

        dockerfile_found = None
        for dockerfile_path in dockerfile_paths:
            if dockerfile_path.exists():
                docker_checks["dockerfile"] = True
                dockerfile_found = dockerfile_path
                logger.info(f"Dockerfile found: {dockerfile_path}")
                break

        if dockerfile_found:
            # Analyze Dockerfile content
            dockerfile_content = dockerfile_found.read_text()

            # Check for multi-stage build
            if "FROM" in dockerfile_content and dockerfile_content.count("FROM") > 1:
                docker_checks["multi_stage_build"] = True
                logger.info("Multi-stage Docker build detected")

            # Check for health check
            if "HEALTHCHECK" in dockerfile_content:
                docker_checks["health_check"] = True
                logger.info("Docker health check found")

        # Check for docker-compose.yml
        compose_files = [
            self.project_root / "docker-compose.yml",
            self.project_root / "docker-compose.yaml",
            self.project_root / "docker" / "docker-compose.yml",
        ]

        for compose_file in compose_files:
            if compose_file.exists():
                docker_checks["docker_compose"] = True
                logger.info(f"Docker Compose file found: {compose_file}")
                break

        # Check for .dockerignore
        dockerignore_file = self.project_root / ".dockerignore"
        if dockerignore_file.exists():
            docker_checks["dockerignore"] = True
            logger.info(".dockerignore file found")

        self.validation_results["docker"] = docker_checks
        logger.info("Docker configuration validation completed")

    def validate_testing_configuration(self):
        """Validate testing configuration and setup."""
        logger.info("Validating testing configuration...")

        testing_checks = {
            "test_directory": False,
            "pytest_config": False,
            "coverage_config": False,
            "test_requirements": False,
            "test_data": False,
        }

        # Check for tests directory
        test_dirs = [self.project_root / "tests", self.project_root / "test"]

        test_dir_found = None
        for test_dir in test_dirs:
            if test_dir.exists():
                testing_checks["test_directory"] = True
                test_dir_found = test_dir
                logger.info(f"Test directory found: {test_dir}")
                break

        # Check for pytest configuration
        pytest_configs = [
            self.project_root / "pytest.ini",
            self.project_root / "pyproject.toml",
            self.project_root / "setup.cfg",
        ]

        for config_file in pytest_configs:
            if config_file.exists():
                content = config_file.read_text()
                if "pytest" in content or "testpaths" in content:
                    testing_checks["pytest_config"] = True
                    logger.info(f"pytest configuration found: {config_file}")
                    break

        # Check for coverage configuration
        coverage_configs = [
            self.project_root / ".coveragerc",
            self.project_root / "pyproject.toml",
        ]

        for config_file in coverage_configs:
            if config_file.exists():
                content = config_file.read_text()
                if "coverage" in content or "--cov" in content:
                    testing_checks["coverage_config"] = True
                    logger.info(f"Coverage configuration found: {config_file}")
                    break

        # Check for test requirements
        requirements_files = [
            self.project_root / "requirements-test.txt",
            self.project_root / "requirements-dev.txt",
            self.project_root / "requirements.txt",
        ]

        for req_file in requirements_files:
            if req_file.exists():
                content = req_file.read_text()
                if "pytest" in content or "coverage" in content:
                    testing_checks["test_requirements"] = True
                    logger.info(f"Test requirements found: {req_file}")
                    break

        # Check for test data
        if test_dir_found:
            test_data_dirs = [
                test_dir_found / "data",
                test_dir_found / "test_data",
                test_dir_found / "fixtures",
            ]

            for data_dir in test_data_dirs:
                if data_dir.exists() and any(data_dir.iterdir()):
                    testing_checks["test_data"] = True
                    logger.info(f"Test data found: {data_dir}")
                    break

        self.validation_results["testing"] = testing_checks
        logger.info("Testing configuration validation completed")

    def validate_dependency_management(self):
        """Validate dependency management configuration."""
        logger.info("Validating dependency management...")

        dependency_checks = {
            "requirements_file": False,
            "setup_py": False,
            "pyproject_toml": False,
            "version_pinning": False,
            "dev_dependencies": False,
        }

        # Check for requirements.txt
        requirements_file = self.project_root / "requirements.txt"
        if requirements_file.exists():
            dependency_checks["requirements_file"] = True
            logger.info("requirements.txt found")

            # Check version pinning
            content = requirements_file.read_text()
            lines = content.strip().split("\n")
            pinned_lines = [
                line for line in lines if "==" in line or "~=" in line or ">=" in line
            ]

            if len(pinned_lines) >= len(lines) * 0.7:  # At least 70% pinned
                dependency_checks["version_pinning"] = True
                logger.info("Good version pinning found")

        # Check for setup.py
        setup_file = self.project_root / "setup.py"
        if setup_file.exists():
            dependency_checks["setup_py"] = True
            logger.info("setup.py found")

        # Check for pyproject.toml
        pyproject_file = self.project_root / "pyproject.toml"
        if pyproject_file.exists():
            dependency_checks["pyproject_toml"] = True
            logger.info("pyproject.toml found")

        # Check for development dependencies
        dev_files = [
            self.project_root / "requirements-dev.txt",
            self.project_root / "requirements-test.txt",
            self.project_root / "dev-requirements.txt",
        ]

        for dev_file in dev_files:
            if dev_file.exists():
                dependency_checks["dev_dependencies"] = True
                logger.info(f"Development dependencies found: {dev_file}")
                break

        self.validation_results["dependencies"] = dependency_checks
        logger.info("Dependency management validation completed")

    def validate_security_configuration(self):
        """Validate security-related configuration."""
        logger.info("Validating security configuration...")

        security_checks = {
            "secrets_in_code": True,  # Start as True, set False if issues found
            "env_file_template": False,
            "security_policies": False,
            "dependency_scanning": False,
            "code_scanning": False,
        }

        # Check for secrets in code (basic check)
        sensitive_patterns = ["password", "secret", "token", "api_key", "private_key"]

        python_files = list(self.project_root.rglob("*.py"))
        for python_file in python_files[:20]:  # Check first 20 files
            try:
                content = python_file.read_text().lower()
                for pattern in sensitive_patterns:
                    if f'{pattern} = "' in content or f"{pattern} = '" in content:
                        security_checks["secrets_in_code"] = False
                        logger.warning(f"Potential hardcoded secret in {python_file}")
                        break
            except Exception:
                continue

        # Check for .env template
        env_files = [
            self.project_root / ".env.example",
            self.project_root / ".env.template",
            self.project_root / "env.example",
        ]

        for env_file in env_files:
            if env_file.exists():
                security_checks["env_file_template"] = True
                logger.info(f"Environment template found: {env_file}")
                break

        # Check for security policies
        security_files = [
            self.project_root / "SECURITY.md",
            self.project_root / ".github" / "SECURITY.md",
        ]

        for security_file in security_files:
            if security_file.exists():
                security_checks["security_policies"] = True
                logger.info(f"Security policy found: {security_file}")
                break

        # Check for dependency scanning in workflows
        workflows_dir = self.project_root / ".github" / "workflows"
        if workflows_dir.exists():
            workflow_files = list(workflows_dir.glob("*.yml")) + list(
                workflows_dir.glob("*.yaml")
            )

            for workflow_file in workflow_files:
                try:
                    content = workflow_file.read_text()
                    if "dependabot" in content.lower() or "snyk" in content.lower():
                        security_checks["dependency_scanning"] = True
                        logger.info("Dependency scanning found in workflows")

                    if "codeql" in content.lower() or "security" in content.lower():
                        security_checks["code_scanning"] = True
                        logger.info("Code scanning found in workflows")
                except Exception:
                    continue

        self.validation_results["security"] = security_checks
        logger.info("Security configuration validation completed")

    def generate_validation_report(self):
        """Generate comprehensive CI/CD validation report."""
        logger.info("Generating CI/CD validation report...")

        report = {
            "validation_timestamp": datetime.now().isoformat(),
            "project_root": str(self.project_root),
            "validation_results": self.validation_results,
            "overall_score": self._calculate_overall_score(),
            "recommendations": self._generate_recommendations(),
        }

        return report

    def _calculate_overall_score(self):
        """Calculate overall CI/CD readiness score."""
        total_checks = 0
        passed_checks = 0

        for category, checks in self.validation_results.items():
            for check, passed in checks.items():
                total_checks += 1
                if passed:
                    passed_checks += 1

        score_percentage = (
            (passed_checks / total_checks * 100) if total_checks > 0 else 0
        )

        return {
            "passed_checks": passed_checks,
            "total_checks": total_checks,
            "percentage": round(score_percentage, 1),
            "status": self._get_status(score_percentage),
        }

    def _get_status(self, percentage):
        """Get status based on percentage score."""
        if percentage >= 90:
            return "Excellent"
        elif percentage >= 75:
            return "Good"
        elif percentage >= 50:
            return "Fair"
        else:
            return "Needs Improvement"

    def _generate_recommendations(self):
        """Generate recommendations based on validation results."""
        recommendations = []

        for category, checks in self.validation_results.items():
            failed_checks = [check for check, passed in checks.items() if not passed]

            if failed_checks:
                category_recommendations = self._get_category_recommendations(
                    category, failed_checks
                )
                recommendations.extend(category_recommendations)

        return recommendations

    def _get_category_recommendations(self, category, failed_checks):
        """Get recommendations for a specific category."""
        recommendations = []

        category_advice = {
            "git": {
                "git_repository": "Initialize Git repository with 'git init'",
                "gitignore": "Create .gitignore file with Python/ML specific patterns",
                "git_hooks": "Set up Git hooks for pre-commit validation",
                "remote_configured": "Add remote repository with 'git remote add origin <url>'",
            },
            "github_actions": {
                "workflows_directory": "Create .github/workflows directory",
                "ci_workflow": "Add CI workflow for automated testing",
                "cd_workflow": "Add CD workflow for automated deployment",
                "workflow_syntax": "Fix YAML syntax errors in workflow files",
                "required_jobs": "Add test, lint, and build jobs to workflows",
            },
            "docker": {
                "dockerfile": "Create Dockerfile for containerization",
                "docker_compose": "Add docker-compose.yml for local development",
                "dockerignore": "Create .dockerignore to optimize build context",
                "multi_stage_build": "Use multi-stage build for smaller images",
                "health_check": "Add HEALTHCHECK instruction to Dockerfile",
            },
            "testing": {
                "test_directory": "Create tests directory with test files",
                "pytest_config": "Add pytest.ini or pyproject.toml configuration",
                "coverage_config": "Configure code coverage reporting",
                "test_requirements": "Add testing dependencies to requirements file",
                "test_data": "Create test fixtures and sample data",
            },
            "dependencies": {
                "requirements_file": "Create requirements.txt with project dependencies",
                "version_pinning": "Pin dependency versions for reproducible builds",
                "dev_dependencies": "Separate development dependencies",
            },
            "security": {
                "secrets_in_code": "Remove hardcoded secrets, use environment variables",
                "env_file_template": "Create .env.example template",
                "security_policies": "Add SECURITY.md with security policies",
                "dependency_scanning": "Enable dependency vulnerability scanning",
                "code_scanning": "Enable code security scanning",
            },
        }

        for failed_check in failed_checks:
            if (
                category in category_advice
                and failed_check in category_advice[category]
            ):
                recommendations.append(
                    {
                        "category": category,
                        "check": failed_check,
                        "recommendation": category_advice[category][failed_check],
                    }
                )

        return recommendations

    def print_summary(self):
        """Print CI/CD validation summary."""
        print("\n" + "=" * 60)
        print("CI/CD PIPELINE VALIDATION SUMMARY")
        print("=" * 60)

        overall_score = self._calculate_overall_score()
        print(
            f"\nOVERALL SCORE: {overall_score['percentage']}% ({overall_score['status']})"
        )
        print(
            f"Passed: {overall_score['passed_checks']}/{overall_score['total_checks']} checks"
        )

        for category, checks in self.validation_results.items():
            print(f"\n{category.upper().replace('_', ' ')}:")
            for check, passed in checks.items():
                status = "✓" if passed else "✗"
                print(f"  {status} {check.replace('_', ' ').title()}")

        recommendations = self._generate_recommendations()
        if recommendations:
            print(f"\nRECOMMENDATIONS:")
            for i, rec in enumerate(recommendations[:5], 1):
                print(f"  {i}. {rec['recommendation']}")

        print("\n" + "=" * 60)


def main():
    """Main validation function."""
    parser = argparse.ArgumentParser(
        description="Validate CI/CD pipeline configuration for LatentLens"
    )
    parser.add_argument(
        "--project-root",
        type=str,
        help="Root directory of the project (default: current directory)",
    )
    parser.add_argument(
        "--output", type=str, help="Output file for validation report (JSON format)"
    )
    parser.add_argument(
        "--category",
        choices=["git", "github", "docker", "testing", "dependencies", "security"],
        help="Validate specific category only",
    )

    args = parser.parse_args()

    try:
        # Initialize validator
        validator = CICDValidator(project_root=args.project_root)

        # Run validations
        if args.category:
            if args.category == "git":
                validator.validate_git_configuration()
            elif args.category == "github":
                validator.validate_github_actions()
            elif args.category == "docker":
                validator.validate_docker_configuration()
            elif args.category == "testing":
                validator.validate_testing_configuration()
            elif args.category == "dependencies":
                validator.validate_dependency_management()
            elif args.category == "security":
                validator.validate_security_configuration()
        else:
            # Run all validations
            validator.validate_git_configuration()
            validator.validate_github_actions()
            validator.validate_docker_configuration()
            validator.validate_testing_configuration()
            validator.validate_dependency_management()
            validator.validate_security_configuration()

        # Generate and display results
        report = validator.generate_validation_report()
        validator.print_summary()

        # Save report if requested
        if args.output:
            with open(args.output, "w") as f:
                json.dump(report, f, indent=2, default=str)
            logger.info(f"Validation report saved to {args.output}")

        # Exit with appropriate code
        overall_score = report["overall_score"]
        if overall_score["percentage"] >= 75:
            print(f"\n✓ CI/CD validation PASSED!")
            sys.exit(0)
        else:
            print(f"\n✗ CI/CD validation FAILED!")
            print(f"Score: {overall_score['percentage']}% (minimum 75% required)")
            sys.exit(1)

    except Exception as e:
        logger.error(f"Validation failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
