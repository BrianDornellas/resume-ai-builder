#!/usr/bin/env python3
"""
Demo script to test the backend API without needing the Flutter frontend.
This script demonstrates how to use the API endpoints directly.
"""

import requests
import json
import sys

BASE_URL = "http://localhost:5000"

def test_health():
    """Test the health endpoint"""
    print("🏥 Testing health endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Health check passed: {data}")
            return True
        else:
            print(f"❌ Health check failed with status {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to backend. Is it running on localhost:5000?")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_generate_resume():
    """Test the resume generation endpoint with sample data"""
    print("\n📝 Testing resume generation endpoint...")
    
    sample_data = {
        "name": "Jane Smith",
        "education": "Master of Computer Science, Stanford University, 2021\nBachelor of Science in Software Engineering, MIT, 2019",
        "experience": "Senior Software Engineer at Tech Corp (2021-Present)\n"
                     "- Led development of cloud-based microservices architecture serving 1M+ users\n"
                     "- Managed team of 5 engineers and implemented agile methodologies\n"
                     "- Reduced deployment time by 60% through CI/CD pipeline improvements\n\n"
                     "Software Developer at StartupXYZ (2019-2021)\n"
                     "- Built scalable web applications using React and Node.js\n"
                     "- Implemented RESTful APIs and database optimization",
        "skills": "Python, Go, JavaScript, TypeScript, React, Node.js, Kubernetes, Docker, AWS, PostgreSQL, MongoDB, CI/CD, Agile, Git"
    }
    
    print(f"Sending request with data:")
    print(f"  Name: {sample_data['name']}")
    print(f"  Education: {sample_data['education'][:50]}...")
    print(f"  Experience: {sample_data['experience'][:50]}...")
    print(f"  Skills: {sample_data['skills'][:50]}...")
    
    try:
        response = requests.post(
            f"{BASE_URL}/generate-resume",
            json=sample_data,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                resume = data.get('resume', '')
                
                # Check if it's a placeholder or AI-generated
                is_placeholder = "This is a placeholder resume" in resume
                
                if is_placeholder:
                    print("\n✅ Resume generated successfully (using placeholder format)!")
                    print("   ℹ️  To enable AI-powered generation, add your OpenAI API key to backend/.env")
                else:
                    print("\n✅ Resume generated successfully (AI-powered)!")
                
                print("\n" + "="*60)
                print("GENERATED RESUME:")
                print("="*60)
                print(resume)
                print("="*60)
                return True
            else:
                print(f"❌ Generation failed: {data.get('error', 'Unknown error')}")
                return False
        else:
            print(f"❌ Request failed with status {response.status_code}")
            try:
                error_data = response.json()
                error_msg = error_data.get('error', 'Unknown error')
                print(f"   Error: {error_msg}")
            except:
                print(f"   Response: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print("❌ Request timed out. The AI might be taking longer than expected.")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_missing_fields():
    """Test that the API properly validates required fields"""
    print("\n🔍 Testing field validation...")
    
    incomplete_data = {
        "name": "Test User"
        # Missing other required fields
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/generate-resume",
            json=incomplete_data,
            headers={"Content-Type": "application/json"},
            timeout=5
        )
        
        if response.status_code == 400:
            data = response.json()
            print(f"✅ Validation working correctly: {data.get('error', '')}")
            return True
        else:
            print(f"❌ Expected 400 status, got {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    """Run all tests"""
    print("="*60)
    print("AI Resume Builder - Backend API Test")
    print("="*60)
    print("\nMake sure the backend is running: cd backend && python app.py")
    print("Note: The app works without an API key (using placeholder format).")
    print("For AI-powered resumes, set OPENAI_API_KEY in backend/.env")
    print()
    
    # Run tests
    results = []
    results.append(("Health Check", test_health()))
    results.append(("Field Validation", test_missing_fields()))
    results.append(("Resume Generation", test_generate_resume()))
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    for test_name, passed in results:
        if passed == True:
            status = "✅ PASSED"
        else:
            status = "❌ FAILED"
        print(f"{test_name:25} {status}")
    
    total_passed = sum(1 for _, passed in results if passed == True)
    print(f"\nTotal: {total_passed}/{len(results)} tests passed")
    
    if total_passed == len(results):
        print("\n🎉 All tests passed! The backend is working correctly.")
        return 0
    else:
        print("\n⚠️  Some tests failed. Check the output above for details.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
