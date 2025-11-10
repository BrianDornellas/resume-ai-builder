import sys
import os

# Add the backend directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app
import json

def test_health_endpoint():
    """Test the health check endpoint"""
    client = app.test_client()
    response = client.get('/health')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['status'] == 'healthy'
    print("✓ Health endpoint test passed")

def test_generate_resume_missing_fields():
    """Test generate-resume endpoint with missing fields"""
    client = app.test_client()
    response = client.post(
        '/generate-resume',
        data=json.dumps({'name': 'Test'}),
        content_type='application/json'
    )
    assert response.status_code == 400
    data = json.loads(response.data)
    assert 'error' in data
    print("✓ Missing fields validation test passed")

def test_generate_resume_structure():
    """Test generate-resume endpoint structure (without actual API call)"""
    client = app.test_client()
    
    # This will fail if OpenAI API key is not set, but we're testing the structure
    test_data = {
        'name': 'John Doe',
        'education': 'BS in Computer Science',
        'experience': 'Software Engineer at Tech Co',
        'skills': 'Python, JavaScript'
    }
    
    response = client.post(
        '/generate-resume',
        data=json.dumps(test_data),
        content_type='application/json'
    )
    
    # We expect either 200 (success) or 500 (OpenAI error due to missing key)
    assert response.status_code in [200, 500]
    data = json.loads(response.data)
    
    if response.status_code == 200:
        assert 'success' in data
        assert 'resume' in data
        print("✓ Generate resume structure test passed (with API)")
    else:
        assert 'error' in data or 'success' in data
        print("✓ Generate resume structure test passed (API key not configured)")

if __name__ == '__main__':
    print("Running backend tests...\n")
    test_health_endpoint()
    test_generate_resume_missing_fields()
    test_generate_resume_structure()
    print("\nAll tests completed!")
