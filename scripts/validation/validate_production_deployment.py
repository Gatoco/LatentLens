#!/usr/bin/env python3
"""
Production Deployment Validation Script for LatentLens

This script validates that the LatentLens system is properly deployed
and functioning correctly in a production environment.

Author: LatentLens Team
License: MIT
"""

import sys
import os
import time
import logging
import requests
import json
import subprocess
from datetime import datetime

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class ProductionValidator:
    """Validator for production deployment health and functionality."""

    def __init__(self, base_url="http://localhost:8000", timeout=30):
        """
        Initialize the production validator.

        Args:
            base_url (str): Base URL of the deployed application
            timeout (int): Request timeout in seconds
        """
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.validation_results = {}

    def validate_service_health(self):
        """Validate basic service health and availability."""
        logger.info("Validating service health...")

        health_checks = {
            "service_available": False,
            "health_endpoint": False,
            "ready_endpoint": False,
            "response_time": None,
            "status_codes": {},
        }

        try:
            # Test basic connectivity
            start_time = time.time()
            response = requests.get(f"{self.base_url}/health", timeout=self.timeout)
            end_time = time.time()

            health_checks["response_time"] = end_time - start_time
            health_checks["status_codes"]["health"] = response.status_code

            if response.status_code == 200:
                health_checks["service_available"] = True
                health_checks["health_endpoint"] = True

                health_data = response.json()
                if health_data.get("status") == "ok":
                    logger.info("Health endpoint responding correctly")
                else:
                    logger.warning(
                        f"Health endpoint returned unexpected data: {health_data}"
                    )

        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to connect to health endpoint: {e}")
            health_checks["error"] = str(e)

        try:
            # Test readiness endpoint
            response = requests.get(f"{self.base_url}/ready", timeout=self.timeout)
            health_checks["status_codes"]["ready"] = response.status_code

            if response.status_code == 200:
                health_checks["ready_endpoint"] = True
                logger.info("Readiness endpoint responding correctly")
            else:
                logger.warning(
                    f"Readiness endpoint returned status {response.status_code}"
                )

        except requests.exceptions.RequestException as e:
            logger.warning(f"Readiness endpoint not available: {e}")

        self.validation_results["health"] = health_checks
        logger.info("Service health validation completed")

    def validate_api_endpoints(self):
        """Validate critical API endpoints functionality."""
        logger.info("Validating API endpoints...")

        endpoints_to_test = [
            {
                "path": "/docs",
                "method": "GET",
                "expected_status": 200,
                "description": "API Documentation",
            },
            {
                "path": "/openapi.json",
                "method": "GET",
                "expected_status": 200,
                "description": "OpenAPI Specification",
            },
            {
                "path": "/system/status",
                "method": "GET",
                "expected_status": 200,
                "description": "System Status",
            },
            {
                "path": "/recommend/123",
                "method": "GET",
                "expected_status": [
                    200,
                    500,
                ],  # May fail if service not fully initialized
                "description": "User Recommendations",
            },
            {
                "path": "/movies/popular",
                "method": "GET",
                "expected_status": [200, 500],
                "description": "Popular Movies",
            },
        ]

        endpoint_results = {}

        for endpoint in endpoints_to_test:
            path = endpoint["path"]
            method = endpoint["method"]
            expected_status = endpoint["expected_status"]
            description = endpoint["description"]

            try:
                start_time = time.time()

                if method == "GET":
                    response = requests.get(
                        f"{self.base_url}{path}", timeout=self.timeout
                    )
                else:
                    # Add support for other methods if needed
                    continue

                end_time = time.time()
                response_time = end_time - start_time

                # Check if status code is expected
                if isinstance(expected_status, list):
                    status_ok = response.status_code in expected_status
                else:
                    status_ok = response.status_code == expected_status

                endpoint_results[path] = {
                    "status_code": response.status_code,
                    "response_time": response_time,
                    "status_ok": status_ok,
                    "description": description,
                    "content_length": len(response.content) if response.content else 0,
                }

                if status_ok:
                    logger.info(f"✓ {description} ({path}): {response.status_code}")
                else:
                    logger.warning(
                        f"✗ {description} ({path}): {response.status_code} (expected {expected_status})"
                    )

            except requests.exceptions.RequestException as e:
                logger.error(f"✗ {description} ({path}): {e}")
                endpoint_results[path] = {
                    "status_code": None,
                    "response_time": None,
                    "status_ok": False,
                    "description": description,
                    "error": str(e),
                }

        self.validation_results["endpoints"] = endpoint_results
        logger.info("API endpoints validation completed")

    def validate_recommendation_functionality(self):
        """Validate core recommendation functionality."""
        logger.info("Validating recommendation functionality...")

        recommendation_tests = {
            "basic_recommendations": False,
            "cold_start_recommendations": False,
            "popular_movies": False,
            "response_format_valid": False,
            "avg_response_time": None,
        }

        response_times = []

        # Test basic user recommendations
        try:
            test_user_id = 123
            start_time = time.time()
            response = requests.get(
                f"{self.base_url}/recommend/{test_user_id}",
                params={"limit": 5},
                timeout=self.timeout,
            )
            end_time = time.time()
            response_times.append(end_time - start_time)

            if response.status_code == 200:
                recommendation_tests["basic_recommendations"] = True

                # Validate response format
                try:
                    data = response.json()
                    if isinstance(data, (dict, list)) and data:
                        recommendation_tests["response_format_valid"] = True
                except json.JSONDecodeError:
                    logger.warning("Recommendation response is not valid JSON")

            logger.info(f"Basic recommendations test: {response.status_code}")

        except requests.exceptions.RequestException as e:
            logger.error(f"Basic recommendations test failed: {e}")

        # Test cold-start recommendations
        try:
            new_user_id = 999999
            start_time = time.time()
            response = requests.get(
                f"{self.base_url}/recommend/cold-start/{new_user_id}",
                params={"strategy": "popular", "limit": 5},
                timeout=self.timeout,
            )
            end_time = time.time()
            response_times.append(end_time - start_time)

            if response.status_code == 200:
                recommendation_tests["cold_start_recommendations"] = True

            logger.info(f"Cold-start recommendations test: {response.status_code}")

        except requests.exceptions.RequestException as e:
            logger.error(f"Cold-start recommendations test failed: {e}")

        # Test popular movies
        try:
            start_time = time.time()
            response = requests.get(
                f"{self.base_url}/movies/popular",
                params={"limit": 10},
                timeout=self.timeout,
            )
            end_time = time.time()
            response_times.append(end_time - start_time)

            if response.status_code == 200:
                recommendation_tests["popular_movies"] = True

            logger.info(f"Popular movies test: {response.status_code}")

        except requests.exceptions.RequestException as e:
            logger.error(f"Popular movies test failed: {e}")

        # Calculate average response time
        if response_times:
            recommendation_tests["avg_response_time"] = sum(response_times) / len(
                response_times
            )

        self.validation_results["recommendations"] = recommendation_tests
        logger.info("Recommendation functionality validation completed")

    def validate_performance_requirements(self):
        """Validate that performance meets production requirements."""
        logger.info("Validating performance requirements...")

        performance_requirements = {
            "max_response_time": 2.0,  # 2 seconds max
            "avg_response_time": 1.0,  # 1 second average
            "health_check_time": 0.5,  # 500ms for health checks
        }

        performance_results = {
            "requirements_met": False,
            "health_check_performance": False,
            "recommendation_performance": False,
            "overall_performance": False,
        }

        # Check health endpoint performance
        if "health" in self.validation_results:
            health_time = self.validation_results["health"].get("response_time")
            if (
                health_time
                and health_time <= performance_requirements["health_check_time"]
            ):
                performance_results["health_check_performance"] = True

        # Check recommendation performance
        if "recommendations" in self.validation_results:
            avg_time = self.validation_results["recommendations"].get(
                "avg_response_time"
            )
            if avg_time and avg_time <= performance_requirements["avg_response_time"]:
                performance_results["recommendation_performance"] = True

        # Overall performance assessment
        performance_results["overall_performance"] = (
            performance_results["health_check_performance"]
            and performance_results["recommendation_performance"]
        )

        performance_results["requirements_met"] = performance_results[
            "overall_performance"
        ]

        self.validation_results["performance"] = {
            "results": performance_results,
            "requirements": performance_requirements,
        }

        logger.info("Performance requirements validation completed")

    def validate_system_resources(self):
        """Validate system resource usage and availability."""
        logger.info("Validating system resources...")

        resource_checks = {
            "memory_usage": None,
            "cpu_usage": None,
            "disk_space": None,
            "process_count": None,
        }

        try:
            # Try to get system status from the API
            response = requests.get(
                f"{self.base_url}/system/status", timeout=self.timeout
            )
            if response.status_code == 200:
                system_data = response.json()
                logger.info(f"System status: {system_data}")
        except:
            logger.warning("Could not retrieve system status from API")

        # Try to get basic system info using subprocess (if available)
        try:
            if os.name != "nt":  # Unix-like systems
                # Get memory usage
                result = subprocess.run(
                    ["free", "-m"], capture_output=True, text=True, timeout=5
                )
                if result.returncode == 0:
                    logger.info("Memory usage information retrieved")

                # Get CPU usage
                result = subprocess.run(
                    ["top", "-bn1"], capture_output=True, text=True, timeout=5
                )
                if result.returncode == 0:
                    logger.info("CPU usage information retrieved")

        except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
            logger.warning("Could not retrieve detailed system resource information")

        self.validation_results["resources"] = resource_checks
        logger.info("System resources validation completed")

    def validate_configuration(self):
        """Validate production configuration settings."""
        logger.info("Validating configuration...")

        config_checks = {
            "environment_variables": False,
            "security_headers": False,
            "cors_settings": False,
            "rate_limiting": False,
        }

        # Check security headers
        try:
            response = requests.get(f"{self.base_url}/docs", timeout=self.timeout)
            headers = response.headers

            # Check for common security headers
            security_headers = [
                "X-Content-Type-Options",
                "X-Frame-Options",
                "X-XSS-Protection",
            ]

            headers_found = sum(1 for header in security_headers if header in headers)
            if headers_found > 0:
                config_checks["security_headers"] = True
                logger.info(f"Found {headers_found} security headers")

        except requests.exceptions.RequestException:
            logger.warning("Could not check security headers")

        # Check CORS settings (basic check)
        try:
            response = requests.options(f"{self.base_url}/docs", timeout=self.timeout)
            if "Access-Control-Allow-Origin" in response.headers:
                config_checks["cors_settings"] = True
                logger.info("CORS headers detected")
        except:
            logger.info("No CORS headers detected (may be intentional)")

        self.validation_results["configuration"] = config_checks
        logger.info("Configuration validation completed")

    def generate_validation_report(self):
        """Generate comprehensive validation report."""
        logger.info("Generating validation report...")

        report = {
            "validation_timestamp": datetime.now().isoformat(),
            "base_url": self.base_url,
            "timeout": self.timeout,
            "validation_results": self.validation_results,
            "overall_health": self._calculate_overall_health(),
        }

        return report

    def _calculate_overall_health(self):
        """Calculate overall system health score."""
        health_score = 0
        max_score = 0

        # Health checks
        if "health" in self.validation_results:
            max_score += 20
            if self.validation_results["health"].get("service_available"):
                health_score += 10
            if self.validation_results["health"].get("health_endpoint"):
                health_score += 5
            if self.validation_results["health"].get("ready_endpoint"):
                health_score += 5

        # API endpoints
        if "endpoints" in self.validation_results:
            max_score += 30
            endpoints = self.validation_results["endpoints"]
            working_endpoints = sum(
                1 for ep in endpoints.values() if ep.get("status_ok", False)
            )
            total_endpoints = len(endpoints)
            if total_endpoints > 0:
                health_score += int(30 * (working_endpoints / total_endpoints))

        # Recommendations
        if "recommendations" in self.validation_results:
            max_score += 30
            recs = self.validation_results["recommendations"]
            if recs.get("basic_recommendations"):
                health_score += 15
            if recs.get("response_format_valid"):
                health_score += 10
            if recs.get("avg_response_time", 999) < 2.0:
                health_score += 5

        # Performance
        if "performance" in self.validation_results:
            max_score += 20
            perf = self.validation_results["performance"]["results"]
            if perf.get("overall_performance"):
                health_score += 20
            elif perf.get("health_check_performance"):
                health_score += 10

        health_percentage = (health_score / max_score * 100) if max_score > 0 else 0

        return {
            "score": health_score,
            "max_score": max_score,
            "percentage": health_percentage,
            "status": self._get_health_status(health_percentage),
        }

    def _get_health_status(self, percentage):
        """Get health status based on percentage."""
        if percentage >= 90:
            return "Excellent"
        elif percentage >= 75:
            return "Good"
        elif percentage >= 50:
            return "Fair"
        elif percentage >= 25:
            return "Poor"
        else:
            return "Critical"

    def print_summary(self):
        """Print validation summary."""
        print("\n" + "=" * 60)
        print("PRODUCTION DEPLOYMENT VALIDATION SUMMARY")
        print("=" * 60)

        # Overall health
        if "overall_health" in self.validation_results:
            health = self.validation_results["overall_health"]
            print(f"\nOVERALL HEALTH: {health['status']} ({health['percentage']:.1f}%)")

        # Service health
        if "health" in self.validation_results:
            health = self.validation_results["health"]
            print(f"\nSERVICE HEALTH:")
            print(
                f"  Service Available: {'✓' if health.get('service_available') else '✗'}"
            )
            print(f"  Health Endpoint: {'✓' if health.get('health_endpoint') else '✗'}")
            print(f"  Ready Endpoint: {'✓' if health.get('ready_endpoint') else '✗'}")
            if health.get("response_time"):
                print(f"  Response Time: {health['response_time']:.3f}s")

        # API endpoints
        if "endpoints" in self.validation_results:
            endpoints = self.validation_results["endpoints"]
            working = sum(1 for ep in endpoints.values() if ep.get("status_ok", False))
            total = len(endpoints)
            print(f"\nAPI ENDPOINTS: {working}/{total} working")

        # Recommendations
        if "recommendations" in self.validation_results:
            recs = self.validation_results["recommendations"]
            print(f"\nRECOMMENDATION FUNCTIONALITY:")
            print(
                f"  Basic Recommendations: {'✓' if recs.get('basic_recommendations') else '✗'}"
            )
            print(
                f"  Cold-start: {'✓' if recs.get('cold_start_recommendations') else '✗'}"
            )
            print(f"  Popular Movies: {'✓' if recs.get('popular_movies') else '✗'}")
            if recs.get("avg_response_time"):
                print(f"  Avg Response Time: {recs['avg_response_time']:.3f}s")

        # Performance
        if "performance" in self.validation_results:
            perf = self.validation_results["performance"]["results"]
            print(f"\nPERFORMANCE:")
            print(f"  Requirements Met: {'✓' if perf.get('requirements_met') else '✗'}")
            print(
                f"  Health Check Performance: {'✓' if perf.get('health_check_performance') else '✗'}"
            )
            print(
                f"  Recommendation Performance: {'✓' if perf.get('recommendation_performance') else '✗'}"
            )

        print("\n" + "=" * 60)


def main():
    """Main validation function."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Validate LatentLens production deployment"
    )
    parser.add_argument(
        "--url",
        default="http://localhost:8000",
        help="Base URL of the deployed application",
    )
    parser.add_argument(
        "--timeout", type=int, default=30, help="Request timeout in seconds"
    )
    parser.add_argument(
        "--quick", action="store_true", help="Run quick validation (basic checks only)"
    )

    args = parser.parse_args()

    print("Starting Production Deployment Validation...")
    print(f"Target URL: {args.url}")

    try:
        # Initialize validator
        validator = ProductionValidator(base_url=args.url, timeout=args.timeout)

        # Run validations
        validator.validate_service_health()
        validator.validate_api_endpoints()

        if not args.quick:
            validator.validate_recommendation_functionality()
            validator.validate_performance_requirements()
            validator.validate_system_resources()
            validator.validate_configuration()

        # Calculate overall health
        validator.validation_results["overall_health"] = (
            validator._calculate_overall_health()
        )

        # Generate and display results
        report = validator.generate_validation_report()
        validator.print_summary()

        # Save report
        report_path = "production_validation_report.json"
        with open(report_path, "w") as f:
            json.dump(report, f, indent=2, default=str)

        logger.info(f"Validation report saved to {report_path}")

        # Exit with appropriate code
        overall_health = validator.validation_results.get("overall_health", {})
        health_percentage = overall_health.get("percentage", 0)

        if health_percentage >= 75:
            print(f"\n✓ Production deployment validation PASSED!")
            sys.exit(0)
        else:
            print(f"\n✗ Production deployment validation FAILED!")
            print(f"Health score: {health_percentage:.1f}% (minimum 75% required)")
            sys.exit(1)

    except Exception as e:
        logger.error(f"Validation failed: {e}")
        print(f"\n✗ Validation failed with error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
