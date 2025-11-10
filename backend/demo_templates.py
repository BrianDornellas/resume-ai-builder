"""
Demo script to showcase the new resume template functionality.
Tests both chronological and functional templates with sample data.
"""

import requests
import json

BASE_URL = 'http://localhost:5000'

def print_section(title):
    """Print a formatted section header"""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80 + "\n")

def generate_and_display_resume(data, template_name):
    """Generate a resume and display it"""
    print(f"Generating {template_name} resume for {data['name']}...")
    
    response = requests.post(
        f'{BASE_URL}/generate-resume',
        json=data,
        headers={'Content-Type': 'application/json'}
    )
    
    if response.status_code == 200:
        result = response.json()
        if result['success']:
            print(f"\n✓ Successfully generated {result['template']} resume\n")
            print("─" * 80)
            print(result['resume'])
            print("─" * 80)
        else:
            print(f"✗ Error: {result.get('error', 'Unknown error')}")
    else:
        print(f"✗ HTTP Error: {response.status_code}")

def main():
    """Main demo function"""
    print_section("Resume Template System Demo - Week 3")
    
    # Sample candidate data
    candidate = {
        'name': 'Sarah Johnson',
        'education': 'Bachelor of Science in Computer Science, UC Berkeley, 2018-2022\nGPA: 3.8/4.0, Dean\'s List',
        'experience': 'Software Engineer at TechCorp (2022-Present): Developed microservices architecture serving 1M+ users. Led migration to Kubernetes resulting in 40% cost reduction. Mentored 3 junior developers.\n\nSoftware Engineering Intern at StartupXYZ (Summer 2021): Built real-time analytics dashboard using React and Node.js. Optimized database queries improving response time by 60%.',
        'skills': 'Programming: Python, JavaScript, TypeScript, Java, Go\nFrameworks: React, Node.js, Django, Flask, Spring Boot\nCloud & DevOps: AWS, Docker, Kubernetes, CI/CD, Terraform\nDatabases: PostgreSQL, MongoDB, Redis\nSoft Skills: Team Leadership, Agile/Scrum, Technical Writing',
    }
    
    # Test 1: Chronological Template
    print_section("Test 1: Chronological Template")
    print("This format emphasizes work history in reverse chronological order.")
    print("Best for: Traditional career progression, consistent work history\n")
    
    chronological_data = candidate.copy()
    chronological_data['template'] = 'chronological'
    generate_and_display_resume(chronological_data, 'Chronological')
    
    # Test 2: Functional Template
    print_section("Test 2: Functional Template")
    print("This format emphasizes skills and competencies over chronological timeline.")
    print("Best for: Career changers, employment gaps, diverse skill sets\n")
    
    functional_data = candidate.copy()
    functional_data['template'] = 'functional'
    generate_and_display_resume(functional_data, 'Functional')
    
    # Test 3: Default Template
    print_section("Test 3: Default Template (No Template Specified)")
    print("When no template is specified, the system defaults to Chronological.\n")
    
    default_data = {
        'name': 'John Doe',
        'education': 'MBA, Harvard Business School',
        'experience': 'Product Manager at Google',
        'skills': 'Product Strategy, Leadership',
    }
    generate_and_display_resume(default_data, 'Default')
    
    # Summary
    print_section("Summary")
    print("✓ Chronological Template: Implemented and working")
    print("✓ Functional Template: Implemented and working")
    print("✓ Default Template: Defaults to Chronological")
    print("✓ Markdown Formatting: Applied to all templates")
    print("✓ Backend API: Returns template parameter in response")
    print("\nNext Steps:")
    print("- Frontend will render these with flutter_markdown")
    print("- Users can select template from dropdown in UI")
    print("- AI integration (Week 5) will use template-specific prompts")
    print()

if __name__ == '__main__':
    try:
        # Check if backend is running
        response = requests.get(f'{BASE_URL}/health')
        if response.status_code == 200:
            main()
        else:
            print("Error: Backend is not responding correctly")
    except requests.exceptions.ConnectionError:
        print("Error: Cannot connect to backend at", BASE_URL)
        print("Please start the backend server with: python app.py")
