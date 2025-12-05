"""Tests for uniform error handling across all endpoints."""
import sys
import os
import json

# Add the backend directory to the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app


def test_generate_resume_invalid_json():
    """Test /generate-resume with invalid JSON body."""
    client = app.test_client()
    response = client.post(
        '/generate-resume',
        data='not valid json{',
        content_type='application/json'
    )
    assert response.status_code == 400
    data = json.loads(response.data)
    assert data['success'] is False
    assert 'error' in data
    assert 'JSON' in data['error']
    print("✓ Generate resume invalid JSON test passed")


def test_generate_resume_uniform_error_shape():
    """Test /generate-resume returns uniform error shape."""
    client = app.test_client()
    response = client.post(
        '/generate-resume',
        data=json.dumps({'name': 'Test'}),
        content_type='application/json'
    )
    assert response.status_code == 400
    data = json.loads(response.data)
    assert 'success' in data
    assert data['success'] is False
    assert 'error' in data
    assert isinstance(data['error'], str)
    print("✓ Generate resume uniform error shape test passed")


def test_generate_cover_letter_invalid_json():
    """Test /generate-cover-letter with invalid JSON body."""
    client = app.test_client()
    response = client.post(
        '/generate-cover-letter',
        data='{{invalid',
        content_type='application/json'
    )
    assert response.status_code == 400
    data = json.loads(response.data)
    assert data['success'] is False
    assert 'error' in data
    print("✓ Generate cover letter invalid JSON test passed")


def test_generate_cover_letter_uniform_error_shape():
    """Test /generate-cover-letter returns uniform error shape."""
    client = app.test_client()
    response = client.post(
        '/generate-cover-letter',
        data=json.dumps({'name': 'Test'}),
        content_type='application/json'
    )
    assert response.status_code == 400
    data = json.loads(response.data)
    assert 'success' in data
    assert data['success'] is False
    assert 'error' in data
    print("✓ Generate cover letter uniform error shape test passed")


def test_export_pdf_invalid_json():
    """Test /export-pdf with invalid JSON body."""
    client = app.test_client()
    response = client.post(
        '/export-pdf',
        data='not valid json',
        content_type='application/json'
    )
    assert response.status_code == 400
    data = json.loads(response.data)
    assert data['success'] is False
    assert 'error' in data
    print("✓ Export PDF invalid JSON test passed")


def test_export_pdf_uniform_error_shape():
    """Test /export-pdf returns uniform error shape."""
    client = app.test_client()
    response = client.post(
        '/export-pdf',
        data=json.dumps({'content': ''}),
        content_type='application/json'
    )
    assert response.status_code == 400
    data = json.loads(response.data)
    assert 'success' in data
    assert data['success'] is False
    assert 'error' in data
    print("✓ Export PDF uniform error shape test passed")


def test_optimize_resume_invalid_json():
    """Test /optimize-resume with invalid JSON body."""
    client = app.test_client()
    response = client.post(
        '/optimize-resume',
        data='broken json {',
        content_type='application/json'
    )
    assert response.status_code == 400
    data = json.loads(response.data)
    assert data['success'] is False
    assert 'error' in data
    print("✓ Optimize resume invalid JSON test passed")


def test_no_stack_traces_leaked():
    """Ensure error messages don't contain stack trace info."""
    client = app.test_client()
    
    # Test various invalid requests
    endpoints = [
        ('/generate-resume', {'name': 123}),  # Non-string value
        ('/generate-cover-letter', {}),
        ('/export-pdf', {'content': '', 'template': 'invalid'}),
        ('/optimize-resume', {'resume_text': 123}),  # Non-string value
    ]
    
    for endpoint, data in endpoints:
        response = client.post(
            endpoint,
            data=json.dumps(data),
            content_type='application/json'
        )
        resp_data = json.loads(response.data)
        error_msg = resp_data.get('error', '')
        
        # Check that error messages don't leak internal details
        assert 'Traceback' not in error_msg
        assert 'File "' not in error_msg
        assert 'line ' not in error_msg
    
    print("✓ No stack traces leaked test passed")


if __name__ == '__main__':
    print("Running error handling tests...\n")
    test_generate_resume_invalid_json()
    test_generate_resume_uniform_error_shape()
    test_generate_cover_letter_invalid_json()
    test_generate_cover_letter_uniform_error_shape()
    test_export_pdf_invalid_json()
    test_export_pdf_uniform_error_shape()
    test_optimize_resume_invalid_json()
    test_no_stack_traces_leaked()
    print("\nAll error handling tests completed!")
