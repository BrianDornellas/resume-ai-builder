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
    
    # Should always return 200 now (with placeholder if no API key)
    assert response.status_code == 200
    data = json.loads(response.data)
    
    assert 'success' in data
    assert data['success'] == True
    assert 'resume' in data
    
    # Check if it's placeholder or AI-generated
    if "placeholder resume" in data['resume']:
        print("✓ Generate resume structure test passed (using placeholder format)")
    else:
        print("✓ Generate resume structure test passed (AI-powered)")

def test_chronological_template():
    """Test chronological template generation"""
    client = app.test_client()
    
    test_data = {
        'name': 'Jane Smith',
        'education': 'MBA, Harvard Business School',
        'experience': 'Product Manager at Google',
        'skills': 'Leadership, Strategy',
        'template': 'chronological'
    }
    
    response = client.post(
        '/generate-resume',
        data=json.dumps(test_data),
        content_type='application/json'
    )
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['success'] == True
    assert 'resume' in data
    assert 'template' in data
    assert data['template'] == 'chronological'
    print("✓ Chronological template test passed")

def test_functional_template():
    """Test functional template generation"""
    client = app.test_client()
    
    test_data = {
        'name': 'Bob Johnson',
        'education': 'BS in Engineering',
        'experience': 'Software Developer',
        'skills': 'Python, Java, AWS',
        'template': 'functional'
    }
    
    response = client.post(
        '/generate-resume',
        data=json.dumps(test_data),
        content_type='application/json'
    )
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['success'] == True
    assert 'resume' in data
    assert 'template' in data
    assert data['template'] == 'functional'
    print("✓ Functional template test passed")

def test_default_template():
    """Test that default template is chronological when not specified"""
    client = app.test_client()
    
    test_data = {
        'name': 'Alice Brown',
        'education': 'PhD in Physics',
        'experience': 'Research Scientist',
        'skills': 'Data Analysis, Machine Learning'
    }
    
    response = client.post(
        '/generate-resume',
        data=json.dumps(test_data),
        content_type='application/json'
    )
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['success'] == True
    assert data['template'] == 'chronological'
    print("✓ Default template test passed")

if __name__ == '__main__':
    print("Running backend tests...\n")
    test_health_endpoint()
    test_generate_resume_missing_fields()
    test_generate_resume_structure()
    test_chronological_template()
    test_functional_template()
    test_default_template()
    print("\nAll tests completed!")
