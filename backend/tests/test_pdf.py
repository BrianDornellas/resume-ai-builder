"""Tests for PDF generation functionality."""
import sys
import os
import json

# Add the backend directory to the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app
from pdf_generator import generate_pdf, PDF_TEMPLATES


def test_generate_pdf_classic():
    """Test PDF generation with classic template."""
    content = """# John Doe

---

## Education

Bachelor of Science in Computer Science

---

## Experience

- Software Engineer at Tech Corp
- Built web applications

---

## Skills

Python, JavaScript, React
"""
    pdf_bytes = generate_pdf(content, "classic")
    assert isinstance(pdf_bytes, bytes)
    assert len(pdf_bytes) > 0
    # PDF files start with %PDF
    assert pdf_bytes[:4] == b'%PDF'
    print("✓ Classic PDF generation test passed")


def test_generate_pdf_modern():
    """Test PDF generation with modern template."""
    content = """# Jane Smith

## Skills

Python, Flask, React

## Experience

- 3 years at Acme Corp
"""
    pdf_bytes = generate_pdf(content, "modern")
    assert isinstance(pdf_bytes, bytes)
    assert len(pdf_bytes) > 0
    assert pdf_bytes[:4] == b'%PDF'
    print("✓ Modern PDF generation test passed")


def test_generate_pdf_invalid_template():
    """Test PDF generation with invalid template raises ValueError."""
    try:
        generate_pdf("Some content", "invalid")
        assert False, "Should have raised ValueError"
    except ValueError as e:
        assert "Unknown template" in str(e)
    print("✓ Invalid template error test passed")


def test_health_pdf_endpoint():
    """Test the /health/pdf endpoint."""
    client = app.test_client()
    response = client.get('/health/pdf')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'pdf_templates' in data
    assert data['pdf_templates'] == PDF_TEMPLATES
    assert "classic" in data['pdf_templates']
    assert "modern" in data['pdf_templates']
    print("✓ Health PDF endpoint test passed")


def test_export_pdf_endpoint_success():
    """Test the /export-pdf endpoint with valid data."""
    client = app.test_client()
    response = client.post(
        '/export-pdf',
        data=json.dumps({
            'document_type': 'resume',
            'content': '# Test Resume\n\n## Skills\n\nPython, JavaScript',
            'template': 'classic'
        }),
        content_type='application/json'
    )
    assert response.status_code == 200
    assert response.content_type == 'application/pdf'
    assert response.data[:4] == b'%PDF'
    print("✓ Export PDF endpoint success test passed")


def test_export_pdf_endpoint_modern_template():
    """Test the /export-pdf endpoint with modern template."""
    client = app.test_client()
    response = client.post(
        '/export-pdf',
        data=json.dumps({
            'document_type': 'cover_letter',
            'content': '# Cover Letter\n\nDear Hiring Manager...',
            'template': 'modern'
        }),
        content_type='application/json'
    )
    assert response.status_code == 200
    assert response.content_type == 'application/pdf'
    print("✓ Export PDF modern template test passed")


def test_export_pdf_endpoint_missing_content():
    """Test the /export-pdf endpoint with missing content."""
    client = app.test_client()
    response = client.post(
        '/export-pdf',
        data=json.dumps({
            'document_type': 'resume',
            'template': 'classic'
        }),
        content_type='application/json'
    )
    assert response.status_code == 400
    data = json.loads(response.data)
    assert 'error' in data
    assert 'Content is required' in data['error']
    print("✓ Export PDF missing content test passed")


def test_export_pdf_endpoint_empty_content():
    """Test the /export-pdf endpoint with empty content."""
    client = app.test_client()
    response = client.post(
        '/export-pdf',
        data=json.dumps({
            'document_type': 'resume',
            'content': '   ',
            'template': 'classic'
        }),
        content_type='application/json'
    )
    assert response.status_code == 400
    data = json.loads(response.data)
    assert 'error' in data
    print("✓ Export PDF empty content test passed")


def test_export_pdf_endpoint_invalid_template():
    """Test the /export-pdf endpoint with invalid template."""
    client = app.test_client()
    response = client.post(
        '/export-pdf',
        data=json.dumps({
            'document_type': 'resume',
            'content': '# Test',
            'template': 'invalid'
        }),
        content_type='application/json'
    )
    assert response.status_code == 400
    data = json.loads(response.data)
    assert 'error' in data
    assert 'template must be one of' in data['error']
    print("✓ Export PDF invalid template test passed")


def test_export_pdf_endpoint_invalid_document_type():
    """Test the /export-pdf endpoint with invalid document_type."""
    client = app.test_client()
    response = client.post(
        '/export-pdf',
        data=json.dumps({
            'document_type': 'invalid',
            'content': '# Test',
            'template': 'classic'
        }),
        content_type='application/json'
    )
    assert response.status_code == 400
    data = json.loads(response.data)
    assert 'error' in data
    print("✓ Export PDF invalid document_type test passed")


def test_export_pdf_endpoint_no_body():
    """Test the /export-pdf endpoint with no request body."""
    client = app.test_client()
    response = client.post(
        '/export-pdf',
        content_type='application/json'
    )
    assert response.status_code == 400
    print("✓ Export PDF no body test passed")


if __name__ == '__main__':
    print("Running PDF generation tests...\n")
    test_generate_pdf_classic()
    test_generate_pdf_modern()
    test_generate_pdf_invalid_template()
    test_health_pdf_endpoint()
    test_export_pdf_endpoint_success()
    test_export_pdf_endpoint_modern_template()
    test_export_pdf_endpoint_missing_content()
    test_export_pdf_endpoint_empty_content()
    test_export_pdf_endpoint_invalid_template()
    test_export_pdf_endpoint_invalid_document_type()
    test_export_pdf_endpoint_no_body()
    print("\nAll PDF tests completed!")
