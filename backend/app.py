
import json
from flask import Flask, request, jsonify, Response
from flask_cors import CORS
import os

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None

try:
    import google.generativeai as genai
except ImportError:
    genai = None
from pdf_generator import generate_pdf, PDF_TEMPLATES

app = Flask(__name__)
CORS(app)  # Enable CORS for Flutter web app


# --- Error Handling Helpers ---
def json_error(message, status=400):
    """
    Returns a standardized JSON error response.
    Shape: { "success": false, "error": string }
    Never leaks stack traces to clients.
    """
    return jsonify({"success": False, "error": message}), status


def get_json_or_error():
    """
    Safely parses JSON from request body.
    Returns (data, None) on success, or (None, error_response) on failure.
    """
    try:
        data = request.get_json(force=True, silent=False)
        if data is None:
            return None, json_error("Request body must be valid JSON")
        return data, None
    except Exception:
        return None, json_error("Request body must be valid JSON")


# Initialize OpenAI client - will be None if API key is not set

def get_openai_client():
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key or not OpenAI:
        return None
    return OpenAI(api_key=api_key)

def get_gemini_client():
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key or not genai:
        return None
    genai.configure(api_key=api_key)
    # Use the correct Gemini model name
    return genai.GenerativeModel('models/gemini-2.5-flash')

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({"status": "healthy"}), 200


@app.route('/health/pdf', methods=['GET'])
def health_pdf():
    """Health check endpoint for PDF templates"""
    return jsonify({"pdf_templates": PDF_TEMPLATES}), 200


@app.route('/export-pdf', methods=['POST'])
def export_pdf():
    """
    Export content as PDF.
    Expected JSON format:
    {
        "document_type": "resume" | "cover_letter",
        "content": string,
        "template": "classic" | "modern"
    }
    Returns: application/pdf binary stream
    """
    try:
        data, error_response = get_json_or_error()
        if error_response:
            return error_response
        
        # Validate required fields
        content = data.get('content')
        if not content or not isinstance(content, str) or not content.strip():
            return json_error("Content is required and cannot be empty")
        
        document_type = data.get('document_type', 'resume')
        if document_type not in ('resume', 'cover_letter'):
            return json_error("document_type must be 'resume' or 'cover_letter'")
        
        template = data.get('template', 'classic')
        if template not in PDF_TEMPLATES:
            return json_error(f"template must be one of: {PDF_TEMPLATES}")
        
        # Generate PDF
        pdf_bytes = generate_pdf(content, template)
        
        # Determine filename prefix
        filename_prefix = "resume" if document_type == "resume" else "cover_letter"
        
        return Response(
            pdf_bytes,
            mimetype='application/pdf',
            headers={
                'Content-Disposition': f'attachment; filename="{filename_prefix}.pdf"',
                'Content-Length': str(len(pdf_bytes)),
            }
        )
        
    except ValueError as e:
        return json_error(str(e))
    except Exception as e:
        app.logger.error(f"Error generating PDF: {str(e)}")
        return json_error("An error occurred while generating the PDF", 500)

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
        data, error_response = get_json_or_error()
        if error_response:
            return error_response
        
        # Validate required fields
        required_fields = ['name', 'education', 'experience', 'skills']
        for field in required_fields:
            if field not in data or not isinstance(data.get(field), str):
                return json_error(f"Missing required field: {field}")
        
        # Extract user data
        name = data['name']
        education = data['education']
        experience = data['experience']
        skills = data['skills']
        template = data.get('template', 'chronological')  # default to chronological
        
        # Check for Gemini, then OpenAI, then fallback to mock
        gemini = get_gemini_client()
        client = get_openai_client()
        if gemini:
            from templates import create_ai_prompt
            prompt = create_ai_prompt(name, education, experience, skills, template)
            response = gemini.generate_content(prompt)
            resume_text = response.text
        elif client:
            from templates import create_ai_prompt
            prompt = create_ai_prompt(name, education, experience, skills, template)
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a professional resume writer. Create clear, concise, and well-formatted resumes."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=1000
            )
            resume_text = response.choices[0].message.content
        else:
            from templates import format_resume_mock
            resume_text = format_resume_mock(name, education, experience, skills, template)
        return jsonify({
            "success": True,
            "resume": resume_text,
            "template": template
        }), 200
        
    except Exception as e:
        # Log the full error for debugging (in production, use proper logging)
        app.logger.error(f"Error generating resume: {str(e)}")
        
        # Return a generic error message to avoid exposing stack traces
        return json_error("An error occurred while generating the resume. Please try again.", 500)
    
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
        data, error_response = get_json_or_error()
        if error_response:
            return error_response
        
        required_fields = ['name', 'company', 'role', 'job_description', 'experience', 'skills']
        for field in required_fields:
            if field not in data or not isinstance(data.get(field), str):
                return json_error(f"Missing required field: {field}")

        gemini = get_gemini_client()
        client = get_openai_client()
        prompt = build_cover_letter_prompt(data)
        if gemini:
            response = gemini.generate_content(prompt)
            cover_letter = response.text
            return jsonify({"success": True, "cover_letter": cover_letter}), 200
        elif client:
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
        else:
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

    except Exception as e:
        app.logger.error(f"Error generating cover letter: {str(e)}")
        return json_error("An error occurred while generating the cover letter. Please try again.", 500)


# --- Resume Optimization Helpers ---
import re

STOPWORDS = set([
    'the', 'and', 'a', 'an', 'to', 'of', 'in', 'for', 'on', 'with', 'at', 'by', 'from', 'as', 'is', 'are', 'was', 'were', 'be', 'this', 'that', 'it', 'or', 'but', 'if', 'then', 'so', 'such', 'has', 'have', 'had', 'will', 'can', 'may', 'do', 'does', 'did', 'not', 'your', 'you', 'we', 'our', 'their', 'they', 'he', 'she', 'his', 'her', 'them', 'which', 'who', 'whom', 'been', 'being', 'into', 'out', 'about', 'over', 'under', 'above', 'below', 'up', 'down', 'off', 'no', 'yes', 'all', 'any', 'each', 'other', 'more', 'most', 'some', 'such', 'only', 'own', 'same', 'than', 'too', 'very', 's', 't', 'just', 'now', 'also', 'these', 'those', 'because', 'while', 'where', 'when', 'how', 'what', 'which', 'why', 'could', 'should', 'would', 'i', 'me', 'my', 'mine', 'your', 'yours', 'his', 'hers', 'its', 'ours', 'theirs', 'am'
])

def parse_keywords(text):
    """Extracts top keywords from text, lowercased, deduped, stopwords removed."""
    # Remove punctuation, split on whitespace
    words = re.findall(r'\b\w+\b', text.lower())
    keywords = [w for w in words if w not in STOPWORDS and len(w) > 2]
    return sorted(set(keywords))

def analyze_alignment(resume_text, job_keywords):
    """Returns (missing_keywords, strengths) based on keyword presence in resume_text."""
    resume_lc = resume_text.lower()
    missing = [kw for kw in job_keywords if kw not in resume_lc]
    strengths = [kw for kw in job_keywords if kw in resume_lc]
    return missing, strengths

def build_ai_prompt(resume_text, job_description):
    """Builds a prompt for the AI to analyze resume vs job description and return JSON schema."""
    return (
        "You are a resume optimization assistant. "
        "Given the following resume and job description, analyze them and respond in this JSON format: "
        '{"success": true, "missing_keywords": ["string"], "strengths": ["string"], "suggested_edits": "string"}'
        f"Resume:\n{resume_text}\n"
        f"Job Description:\n{job_description}\n"
        "- missing_keywords: List keywords/skills from the job description not present in the resume.\n"
        "- strengths: List areas where the resume aligns well with the job description.\n"
        "- suggested_edits: Give 3-6 concise bullet suggestions to improve the resume for this job. Do not rewrite the resume."
    )

# Example curl:
# curl -X POST http://localhost:5000/optimize-resume \
#   -H "Content-Type: application/json" \
#   -d '{"resume_text": "...", "job_description": "..."}'

@app.route('/improve-resume', methods=['POST'])
def improve_resume():
    """
    Improve a resume by applying suggested edits using AI.
    Expected JSON format:
    {
        "resume_text": "string",
        "job_description": "string",
        "suggested_edits": "string",
        "extra_details": "string (optional)"
    }
    """
    try:
        data, error_response = get_json_or_error()
        if error_response:
            return error_response
        
        # Validate required fields
        resume_text = data.get('resume_text', '')
        job_description = data.get('job_description', '')
        suggested_edits = data.get('suggested_edits', '')
        extra_details = data.get('extra_details', '')
        
        if not isinstance(resume_text, str) or not resume_text.strip():
            return json_error("resume_text is required and cannot be empty")
        if not isinstance(job_description, str) or not job_description.strip():
            return json_error("job_description is required and cannot be empty")
        if not isinstance(suggested_edits, str) or not suggested_edits.strip():
            return json_error("suggested_edits is required and cannot be empty")
        if not isinstance(extra_details, str):
            extra_details = ""
        
        # Build the prompt
        prompt = (
            "You are a resume optimization assistant.\n\n"
            f"Current resume:\n{resume_text}\n\n"
            f"Job description:\n{job_description}\n\n"
            f"Suggested edits to apply:\n{suggested_edits}\n\n"
            f"Additional details from the candidate (may be empty):\n{extra_details}\n\n"
            "Rewrite the full resume, applying the suggested edits and incorporating any relevant additional details. "
            "Do NOT invent any facts that are not implied by the resume, job description, or additional details. "
            "If a suggestion refers to missing information and the candidate did not provide more details, make a neutral, truthful improvement or leave that part as-is.\n\n"
            "Return ONLY the improved resume text in Markdown format. Do not include JSON, explanations, or code fences."
        )
        
        # Try Gemini, then OpenAI, then fallback to mock
        gemini = get_gemini_client()
        client = get_openai_client()
        
        if gemini:
            try:
                response = gemini.generate_content(prompt)
                improved_resume = response.text
            except Exception as e:
                app.logger.error(f"Gemini API error: {str(e)}")
                return json_error("AI service temporarily unavailable. Please try again later.", 503)
        elif client:
            try:
                response = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "You are a professional resume writer who helps optimize resumes for specific job opportunities."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.7,
                    max_tokens=1500
                )
                improved_resume = response.choices[0].message.content
            except Exception as e:
                app.logger.error(f"OpenAI API error: {str(e)}")
                return json_error("AI service temporarily unavailable. Please try again later.", 503)
        else:
            # Mock mode - create a simple improved version
            # Extract first few suggestions and add them as comments
            suggestions_list = suggested_edits.split('\n')[:3]
            suggestions_text = '\n'.join([f"<!-- TODO: {s.strip()} -->" for s in suggestions_list if s.strip()])
            improved_resume = (
                f"{resume_text}\n\n"
                f"<!-- Mock AI Improvement Mode -->\n"
                f"<!-- Suggested improvements to consider: -->\n"
                f"{suggestions_text}\n"
                f"<!-- Additional context provided: {extra_details if extra_details else 'None'} -->"
            )
        
        return jsonify({
            "success": True,
            "improved_resume": improved_resume
        }), 200
        
    except Exception as e:
        app.logger.error(f"Error improving resume: {str(e)}")
        return json_error("An error occurred while improving the resume. Please try again.", 500)


@app.route('/optimize-resume', methods=['POST'])
def optimize_resume():
    try:
        data, error_response = get_json_or_error()
        if error_response:
            return error_response
        
        resume_text = data.get('resume_text', '')
        job_description = data.get('job_description', '')
        
        if not isinstance(resume_text, str):
            return json_error("resume_text must be a string")
        if not isinstance(job_description, str):
            return json_error("job_description must be a string")
        
        if not resume_text.strip() or not job_description.strip():
            return jsonify({
                "success": True,
                "missing_keywords": [],
                "strengths": [],
                "suggested_edits": "Please provide both resume_text and job_description."
            }), 200

        gemini = get_gemini_client()
        client = get_openai_client()
        if gemini:
            prompt = build_ai_prompt(resume_text, job_description)
            response = gemini.generate_content(prompt)
            ai_content = response.text
            try:
                ai_json = json.loads(ai_content)
                ai_json['success'] = True
                return jsonify(ai_json), 200
            except Exception:
                return jsonify({
                    "success": True,
                    "missing_keywords": [],
                    "strengths": [],
                    "suggested_edits": ai_content.strip()
                }), 200
        elif client:
            prompt = build_ai_prompt(resume_text, job_description)
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a resume optimization assistant."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.4,
                max_tokens=600
            )
            ai_content = response.choices[0].message.content
            try:
                ai_json = json.loads(ai_content)
                ai_json['success'] = True
                return jsonify(ai_json), 200
            except Exception:
                return jsonify({
                    "success": True,
                    "missing_keywords": [],
                    "strengths": [],
                    "suggested_edits": ai_content.strip()
                }), 200
        else:
            # Local analysis (mock mode)
            job_keywords = parse_keywords(job_description)
            missing, strengths = analyze_alignment(resume_text, job_keywords)
            # Heuristic suggestions
            suggestions = []
            for kw in missing[:3]:
                suggestions.append(f"Add '{kw}' under Skills or Experience.")
            for kw in strengths[:2]:
                suggestions.append(f"Quantify your impact with '{kw}'.")
            if not suggestions:
                suggestions.append("Highlight more relevant skills from the job description.")
            suggested_edits = '\n'.join(f"- {s}" for s in suggestions)
            return jsonify({
                "success": True,
                "missing_keywords": missing,
                "strengths": strengths,
                "suggested_edits": suggested_edits
            }), 200
    except Exception as e:
        app.logger.error(f"Error optimizing resume: {str(e)}")
        return json_error("An error occurred while optimizing the resume. Please try again.", 500)


if __name__ == '__main__':
    # Use debug mode only in development
    # In production, use a WSGI server like gunicorn
    debug_mode = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    app.run(debug=debug_mode, host='0.0.0.0', port=5000)
