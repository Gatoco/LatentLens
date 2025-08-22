#!/usr/bin/env python3
"""
🧪 Docker Hub Deployment Verification Script
Verifica que la imagen de LatentLens desplegada en Docker Hub funciona correctamente
"""

import requests
import time
import subprocess
import sys
import json
from datetime import datetime

def run_command(command):
    """Ejecuta un comando y retorna el resultado"""
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def test_docker_pull():
    """Test 1: Verificar que se puede hacer pull de la imagen"""
    print("🔄 Test 1: Pulling LatentLens image from Docker Hub...")
    
    success, stdout, stderr = run_command("docker pull gatoco/latentlens:latest")
    
    if success:
        print("✅ Successfully pulled gatoco/latentlens:latest")
        return True
    else:
        print(f"❌ Failed to pull image: {stderr}")
        return False

def test_docker_run():
    """Test 2: Verificar que la imagen se ejecuta correctamente"""
    print("🚀 Test 2: Starting LatentLens container...")
    
    # Parar cualquier contenedor existente
    run_command("docker stop latentlens-test 2>/dev/null")
    run_command("docker rm latentlens-test 2>/dev/null")
    
    # Ejecutar nuevo contenedor
    success, stdout, stderr = run_command(
        "docker run -d --name latentlens-test -p 8001:8000 gatoco/latentlens:latest"
    )
    
    if success:
        print("✅ Container started successfully")
        time.sleep(10)  # Esperar que la aplicación se inicie
        return True
    else:
        print(f"❌ Failed to start container: {stderr}")
        return False

def test_health_endpoint():
    """Test 3: Verificar que el endpoint de salud responde"""
    print("🏥 Test 3: Testing health endpoint...")
    
    try:
        response = requests.get("http://localhost:8001/health", timeout=30)
        
        if response.status_code == 200:
            health_data = response.json()
            print(f"✅ Health endpoint OK: {health_data}")
            return True
        else:
            print(f"❌ Health endpoint failed: Status {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Health endpoint unreachable: {e}")
        return False

def test_api_docs():
    """Test 4: Verificar que la documentación de la API está disponible"""
    print("📚 Test 4: Testing API documentation...")
    
    try:
        response = requests.get("http://localhost:8001/docs", timeout=30)
        
        if response.status_code == 200:
            print("✅ API documentation is accessible")
            return True
        else:
            print(f"❌ API docs failed: Status {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ API docs unreachable: {e}")
        return False

def test_recommendation_endpoint():
    """Test 5: Verificar que el endpoint de recomendaciones funciona"""
    print("🎯 Test 5: Testing recommendation endpoint...")
    
    try:
        # Test con un user_id que debería funcionar con el cold start
        response = requests.get("http://localhost:8001/recommend/hybrid/999999", timeout=60)
        
        if response.status_code == 200:
            rec_data = response.json()
            print(f"✅ Recommendations endpoint OK: {len(rec_data.get('recommendations', []))} recommendations")
            return True
        else:
            print(f"❌ Recommendations endpoint failed: Status {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Recommendations endpoint unreachable: {e}")
        return False

def test_container_logs():
    """Test 6: Verificar los logs del contenedor"""
    print("📝 Test 6: Checking container logs...")
    
    success, stdout, stderr = run_command("docker logs latentlens-test --tail 20")
    
    if success:
        print("✅ Container logs retrieved:")
        print("--- CONTAINER LOGS ---")
        print(stdout)
        print("--- END LOGS ---")
        return True
    else:
        print(f"❌ Failed to get container logs: {stderr}")
        return False

def cleanup():
    """Limpiar recursos de testing"""
    print("🧹 Cleaning up test resources...")
    run_command("docker stop latentlens-test")
    run_command("docker rm latentlens-test")
    print("✅ Cleanup completed")

def main():
    """Ejecutar todos los tests"""
    print("=" * 60)
    print("🚀 LatentLens Docker Hub Deployment Verification")
    print("=" * 60)
    
    start_time = datetime.now()
    
    tests = [
        ("Pull Image", test_docker_pull),
        ("Run Container", test_docker_run),
        ("Health Check", test_health_endpoint),
        ("API Documentation", test_api_docs),
        ("Recommendations", test_recommendation_endpoint),
        ("Container Logs", test_container_logs)
    ]
    
    results = {}
    
    try:
        for test_name, test_func in tests:
            print(f"\n{'='*40}")
            print(f"Running: {test_name}")
            print(f"{'='*40}")
            
            result = test_func()
            results[test_name] = result
            
            if not result:
                print(f"❌ Test '{test_name}' failed - stopping here")
                break
                
        # Mostrar resumen
        print(f"\n{'='*60}")
        print("📊 TEST SUMMARY")
        print(f"{'='*60}")
        
        total_tests = len(results)
        passed_tests = sum(results.values())
        
        for test_name, result in results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{test_name:<20} {status}")
        
        print(f"\nTotal: {passed_tests}/{total_tests} tests passed")
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        print(f"Duration: {duration:.1f} seconds")
        
        if passed_tests == total_tests:
            print("\n🎉 ALL TESTS PASSED! LatentLens deployment verified successfully!")
            print("\n🚀 Your Docker image is ready for production!")
            print(f"   Pull: docker pull gatoco/latentlens:latest")
            print(f"   Run:  docker run -p 8000:8000 gatoco/latentlens:latest")
            return 0
        else:
            print(f"\n❌ {total_tests - passed_tests} test(s) failed")
            return 1
            
    except KeyboardInterrupt:
        print("\n⚠️ Tests interrupted by user")
        return 1
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        return 1
    finally:
        cleanup()

if __name__ == "__main__":
    sys.exit(main())
