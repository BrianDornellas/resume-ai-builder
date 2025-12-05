#!/usr/bin/env python3
"""
Smoke test script for PDF export endpoint.

Usage:
    python scripts/smoke_pdf.py [--template classic|modern] [--output FILENAME]

Prerequisites:
    - Backend server must be running on http://localhost:5000
    - Start the backend with: cd backend && python app.py

Example:
    python scripts/smoke_pdf.py
    python scripts/smoke_pdf.py --template modern --output my_resume.pdf
"""

import argparse
import sys

try:
    import requests
except ImportError:
    print("Error: 'requests' package is required. Install it with: pip install requests")
    sys.exit(1)


SAMPLE_RESUME_CONTENT = """# John Doe

---

## 📚 Education

**Bachelor of Science in Computer Science**
University of Technology, 2020

---

## 💼 Professional Experience

**Software Engineer at Tech Corp** (2020-2023)
- Developed and maintained web applications using Python and React
- Led a team of 3 developers on a major product launch
- Improved system performance by 40% through code optimization

**Junior Developer at StartupXYZ** (2019-2020)
- Built RESTful APIs using Flask
- Collaborated with cross-functional teams

---

## 🛠 Technical Skills

Python, JavaScript, React, Flask, PostgreSQL, Docker, AWS
"""

SAMPLE_COVER_LETTER_CONTENT = """# Cover Letter

Dear Hiring Manager,

I am writing to express my interest in the Software Engineer position at your company.

## Why I'm a Great Fit

- 3+ years of experience in full-stack development
- Strong background in Python and JavaScript
- Excellent communication and teamwork skills

I am excited about the opportunity to contribute to your team and would welcome the chance to discuss how my skills align with your needs.

Sincerely,
John Doe
"""


def main():
    parser = argparse.ArgumentParser(description='Smoke test for PDF export endpoint')
    parser.add_argument('--template', choices=['classic', 'modern'], default='classic',
                        help='PDF template to use (default: classic)')
    parser.add_argument('--output', default='out.pdf',
                        help='Output filename (default: out.pdf)')
    parser.add_argument('--type', choices=['resume', 'cover_letter'], default='resume',
                        help='Document type (default: resume)')
    parser.add_argument('--url', default='http://localhost:5000',
                        help='Backend server URL (default: http://localhost:5000)')
    
    args = parser.parse_args()
    
    # Select content based on document type
    content = SAMPLE_RESUME_CONTENT if args.type == 'resume' else SAMPLE_COVER_LETTER_CONTENT
    
    payload = {
        'document_type': args.type,
        'content': content,
        'template': args.template,
    }
    
    print(f"Sending POST request to {args.url}/export-pdf")
    print(f"  Document type: {args.type}")
    print(f"  Template: {args.template}")
    print(f"  Output file: {args.output}")
    print()
    
    try:
        response = requests.post(
            f'{args.url}/export-pdf',
            json=payload,
            timeout=30,
        )
        
        if response.status_code == 200:
            with open(args.output, 'wb') as f:
                f.write(response.content)
            print(f"✓ Success! PDF saved to: {args.output}")
            print(f"  File size: {len(response.content)} bytes")
            return 0
        else:
            print(f"✗ Error: Server returned status {response.status_code}")
            try:
                error_data = response.json()
                print(f"  Message: {error_data.get('error', 'Unknown error')}")
            except Exception:
                print(f"  Response: {response.text[:200]}")
            return 1
            
    except requests.exceptions.ConnectionError:
        print("✗ Error: Could not connect to the server.")
        print(f"  Make sure the backend is running at {args.url}")
        print("  Start it with: cd backend && python app.py")
        return 1
    except requests.exceptions.Timeout:
        print("✗ Error: Request timed out.")
        return 1
    except Exception as e:
        print(f"✗ Error: {e}")
        return 1


if __name__ == '__main__':
    sys.exit(main())
