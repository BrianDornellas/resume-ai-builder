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
        "skills": "Python, JavaScript, React, Node.js"
    }
    """
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['name', 'education', 'experience', 'skills']
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing required field: {field}"}), 400
        
<<<<<<< HEAD
        # Check if OpenAI API key is configured
        client = get_openai_client()
        if not client:
            # Return a mock resume so you can test without API key
            mock_resume = f"""
            {data['name']}
            
            Education:
            {data['education']}
            
            Experience:
            {data['experience']}
            
            Skills:
            {data['skills']}
            
            ---
            (Mock resume generated locally. Add your OpenAI API key to enable AI-powered generation.)
            """
            return jsonify({
                "success": True,
                "resume": mock_resume.strip()
            }), 200

        
=======
>>>>>>> 9c3ac1938151f2813d12fa521542a4d61050e97a
        # Extract user data
        name = data['name']
        education = data['education']
        experience = data['experience']
        skills = data['skills']
        
        # Check if OpenAI API key is configured
        client = get_openai_client()
        
        if not client:
            # Generate a placeholder resume when API key is not configured
            resume_text = f"""
{name}
{'=' * len(name)}

EDUCATION
---------
{education}

EXPERIENCE
----------
{experience}

SKILLS
------
{skills}

---
Note: This is a placeholder resume. Configure your OpenAI API key to generate AI-powered resumes.
To add your API key, create a .env file in the backend directory with:
OPENAI_API_KEY=your_api_key_here
"""
        else:
            # Create structured prompt for AI
            prompt = f"""Generate a professional resume based on the following information:

            Name: {name}

            Education: {education}

            Experience: {experience}

            Skills: {skills}

            Please create a well-formatted, professional resume in plain text format. Include appropriate sections and make it suitable for job applications."""

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
            "resume": resume_text
        }), 200
        
    except Exception as e:
        # Log the full error for debugging (in production, use proper logging)
        app.logger.error(f"Error generating resume: {str(e)}")
        
        # Return a generic error message to avoid exposing stack traces
        return jsonify({
            "success": False,
            "error": f"An error occurred while generating the resume. Please try again. {str(e)}"
        }), 500

if __name__ == '__main__':
    # Use debug mode only in development
    # In production, use a WSGI server like gunicorn
    debug_mode = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    app.run(debug=debug_mode, host='0.0.0.0', port=5000)
