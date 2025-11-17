from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from openai import OpenAI

app = Flask(__name__)
CORS(app)  # Enable CORS for Flutter web app

# Initialize OpenAI client - will be None if API key is not set
def get_openai_client():
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        return None
    return OpenAI(api_key=api_key)

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({"status": "healthy"}), 200

@app.route('/generate-resume', methods=['POST'])
def generate_resume():
    """
    Generate a resume from user input.
    Expected JSON format:
    {
        "name": "John Doe",
        "education": "Bachelor of Science in Computer Science, XYZ University, 2020",
        "experience": "Software Engineer at ABC Corp (2020-2023): Developed web applications...",
        "skills": "Python, JavaScript, React, Node.js",
        "template": "chronological"  # optional: chronological, functional
    }
    """
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['name', 'education', 'experience', 'skills']
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing required field: {field}"}), 400
        
        # Extract user data
        name = data['name']
        education = data['education']
        experience = data['experience']
        skills = data['skills']
        template = data.get('template', 'chronological')  # default to chronological
        
        # Check if OpenAI API key is configured
        client = get_openai_client()
        
        if not client:
            # Generate a mock resume in the requested template format
            from templates import format_resume_mock
            resume_text = format_resume_mock(name, education, experience, skills, template)
        else:
            # Create structured prompt for AI based on template
            from templates import create_ai_prompt
            prompt = create_ai_prompt(name, education, experience, skills, template)

            # Call OpenAI API
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a professional resume writer. Create clear, concise, and well-formatted resumes."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=1000
            )
            
            # Extract generated resume
            resume_text = response.choices[0].message.content
        
        return jsonify({
            "success": True,
            "resume": resume_text,
            "template": template
        }), 200
        
    except Exception as e:
        # Log the full error for debugging (in production, use proper logging)
        app.logger.error(f"Error generating resume: {str(e)}")
        
        # Return a generic error message to avoid exposing stack traces
        return jsonify({
            "success": False,
            "error": f"An error occurred while generating the resume. Please try again. {str(e)}"
        }), 500
    
    # Helper function to build the cover letter prompt
def build_cover_letter_prompt(data):
    """
    Returns a prompt string for the cover letter based on input data.
    data: dict with keys 'name', 'company', 'role', 'job_description', 'experience', 'skills'
    """
    return (
        f"Write a professional cover letter for the following job application.\n"
        f"Applicant Name: {data.get('name', '')}\n"
        f"Company: {data.get('company', '')}\n"
        f"Role: {data.get('role', '')}\n"
        f"Job Description: {data.get('job_description', '')}\n"
        f"Relevant Experience: {data.get('experience', '')}\n"
        f"Skills: {data.get('skills', '')}\n"
        f"Format the cover letter in plain text."
    )

# Example curl command for /generate-cover-letter
# curl -X POST http://localhost:5000/generate-cover-letter \
#   -H "Content-Type: application/json" \
#   -d '{"name": "Jane Doe", "company": "Acme Corp", "role": "Software Engineer", "job_description": "Develop and maintain web applications.", "experience": "3 years at Tech Solutions", "skills": "Python, Flask, React"}'

@app.route('/generate-cover-letter', methods=['POST'])
def generate_cover_letter():
    """
    Generate a cover letter from user input.
    Expected JSON format:
    {
        "name": "Jane Doe",
        "company": "Acme Corp",
        "role": "Software Engineer",
        "job_description": "Develop and maintain web applications.",
        "experience": "3 years at Tech Solutions",
        "skills": "Python, Flask, React"
    }
    """
    try:
        data = request.get_json()
        required_fields = ['name', 'company', 'role', 'job_description', 'experience', 'skills']
        for field in required_fields:
            if field not in data:
                return jsonify({"success": False, "error": f"Missing required field: {field}"}), 400

        client = get_openai_client()
        prompt = build_cover_letter_prompt(data)

        if not client:
            # Deterministic mock cover letter
            mock_letter = (
                f"Dear {data['company']} Hiring Team,\n\n"
                f"I am excited to apply for the {data['role']} position. "
                f"With experience in {data['experience']} and skills in {data['skills']}, "
                f"I believe I am a strong fit for your team.\n\n"
                f"Job Description Highlights: {data['job_description']}\n\n"
                f"Thank you for considering my application.\n\nSincerely,\n{data['name']}"
            )
            return jsonify({"success": True, "cover_letter": mock_letter}), 200

        # OpenAI API call
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a professional career coach. Write clear, concise, and tailored cover letters."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=800
        )
        cover_letter = response.choices[0].message.content
        return jsonify({"success": True, "cover_letter": cover_letter}), 200

    except Exception as e:
        app.logger.error(f"Error generating cover letter: {str(e)}")
        return jsonify({"success": False, "error": "An error occurred while generating the cover letter. Please try again."}), 500

if __name__ == '__main__':
    # Use debug mode only in development
    # In production, use a WSGI server like gunicorn
    debug_mode = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    app.run(debug=debug_mode, host='0.0.0.0', port=5000)
