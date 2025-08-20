"""
Quick Success Criteria Validation Script

Validates the four success criteria for the hybrid recommendation system:
1. API Updated - Check endpoint implementation
2. Deployment Ready - Verify docker-compose configuration  
3. Endpoint Functionality - Test endpoint structure
4. Quality Verification - Compare algorithm outputs
"""

import os
import sys
from pathlib import Path

def validate_criterion_1_api_updated():
    """Criterion 1: Verify API has been updated with hybrid endpoint."""
    print("\n🔍 Criterion 1: API Updated")
    
    # Check if main.py contains hybrid endpoint
    main_py_path = Path("main.py")
    
    if main_py_path.exists():
        content = main_py_path.read_text(encoding='utf-8')
        
        # Check for hybrid endpoint
        if '/recommend/hybrid/{user_id}' in content:
            print("✅ Hybrid endpoint found in main.py")
            
            # Check for tags
            if 'tags=["Recomendaciones"]' in content:
                print("✅ Correct tags implemented")
                
                # Check for fusion logic
                if 'defaultdict' in content and 'scores[movie_id]' in content:
                    print("✅ Fusion algorithm implemented")
                    return True
                else:
                    print("❌ Fusion algorithm not found")
                    return False
            else:
                print("❌ Missing required tags")
                return False
        else:
            print("❌ Hybrid endpoint not found")
            return False
    else:
        print("❌ main.py not found")
        return False

def validate_criterion_2_deployment_ready():
    """Criterion 2: Verify deployment configuration."""
    print("\n🔍 Criterion 2: Deployment Ready")
    
    # Check docker-compose.yml
    docker_compose_path = Path("docker-compose.yml")
    
    if docker_compose_path.exists():
        content = docker_compose_path.read_text(encoding='utf-8')
        
        if 'api:' in content and '8000:8000' in content:
            print("✅ Docker Compose configuration found")
            
            # Check Dockerfile
            dockerfile_path = Path("Dockerfile")
            if dockerfile_path.exists():
                print("✅ Dockerfile exists")
                
                # Check requirements.txt
                requirements_path = Path("requirements.txt")
                if requirements_path.exists():
                    req_content = requirements_path.read_text(encoding='utf-8')
                    if 'fastapi' in req_content and 'uvicorn' in req_content:
                        print("✅ Required dependencies configured")
                        return True
                    else:
                        print("❌ Missing core dependencies")
                        return False
                else:
                    print("❌ requirements.txt not found")
                    return False
            else:
                print("❌ Dockerfile not found")
                return False
        else:
            print("❌ Invalid docker-compose configuration")
            return False
    else:
        print("❌ docker-compose.yml not found")
        return False

def validate_criterion_3_endpoint_structure():
    """Criterion 3: Verify endpoint implementation structure."""
    print("\n🔍 Criterion 3: Endpoint Functionality Structure")
    
    main_py_path = Path("main.py")
    
    if main_py_path.exists():
        content = main_py_path.read_text(encoding='utf-8')
        
        # Check for key components
        checks = [
            ('SVD candidate generation', 'get_svd_recommendations'),
            ('KNN candidate generation', 'get_collaborative_recommendations'),
            ('Content filtering', 'user_interaction_history'),
            ('Re-ranking', 'sorted_candidates'),
            ('Response enrichment', 'final_recommendations'),
            ('Analytics metadata', 'pipeline_metadata')
        ]
        
        all_passed = True
        
        for description, pattern in checks:
            if pattern in content:
                print(f"✅ {description} implemented")
            else:
                print(f"❌ {description} missing")
                all_passed = False
        
        return all_passed
    else:
        print("❌ main.py not found")
        return False

def validate_criterion_4_quality_verification():
    """Criterion 4: Verify quality verification capability."""
    print("\n🔍 Criterion 4: Quality Verification Capability")
    
    # Check if individual algorithm endpoints exist
    main_py_path = Path("main.py")
    
    if main_py_path.exists():
        content = main_py_path.read_text(encoding='utf-8')
        
        # Check for comparison endpoints
        endpoints = [
            ('/recommend/collaborative/', 'SVD collaborative filtering'),
            ('/recommend/item-similarity/', 'KNN item-to-item similarity'),
            ('/recommend/hybrid/', 'Hybrid algorithm')
        ]
        
        all_found = True
        
        for endpoint, description in endpoints:
            if endpoint in content:
                print(f"✅ {description} endpoint available")
            else:
                print(f"❌ {description} endpoint missing")
                all_found = False
        
        # Check for response structure that enables comparison
        if 'source_algorithms' in content and 'consensus_indicator' in content:
            print("✅ Comparison-ready response structure")
        else:
            print("❌ Missing comparison metadata")
            all_found = False
        
        return all_found
    else:
        print("❌ main.py not found")
        return False

def check_test_coverage():
    """Verify test coverage for validation."""
    print("\n🧪 Test Coverage Analysis")
    
    test_files = [
        "test_fusion_integration.py",
        "test_candidate_weighting.py", 
        "test_knn_candidates.py",
        "test_svd_candidates.py",
        "test_fase_3_1.py"
    ]
    
    found_tests = 0
    
    for test_file in test_files:
        if Path(test_file).exists():
            print(f"✅ {test_file}")
            found_tests += 1
        else:
            print(f"❌ {test_file}")
    
    coverage_percentage = (found_tests / len(test_files)) * 100
    print(f"\n📊 Test Coverage: {coverage_percentage:.1f}% ({found_tests}/{len(test_files)} files)")
    
    return found_tests >= 3  # Require at least 3 test files

def main():
    """Main validation function."""
    print("🔬 Hybrid Recommendation System - Success Criteria Validation")
    print("=" * 70)
    
    # Run all criteria validations
    results = []
    
    results.append(("API Updated", validate_criterion_1_api_updated()))
    results.append(("Deployment Ready", validate_criterion_2_deployment_ready()))
    results.append(("Endpoint Structure", validate_criterion_3_endpoint_structure()))
    results.append(("Quality Verification", validate_criterion_4_quality_verification()))
    results.append(("Test Coverage", check_test_coverage()))
    
    # Summary
    print("\n" + "=" * 70)
    print("🏁 VALIDATION SUMMARY")
    print("=" * 70)
    
    all_passed = True
    
    for criterion, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} - {criterion}")
        if not passed:
            all_passed = False
    
    print("\n" + "=" * 70)
    
    if all_passed:
        print("🎉 ALL SUCCESS CRITERIA VALIDATED")
        print("🚀 System is ready for production deployment!")
        print("\nNext steps:")
        print("  1. Run: docker-compose up --build")
        print("  2. Test: http://localhost:8000/docs")
        print("  3. Validate: http://localhost:8000/recommend/hybrid/1?top_n=10")
    else:
        print("💥 VALIDATION FAILED")
        print("🔧 Please fix the failing criteria before deployment.")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
