import json
from flask import Flask, request, jsonify, Response
from flask_cors import CORS
import os
import re

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None

try:
    import google.generativeai as genai
except ImportError:
    genai = None

from pdf_generator import generate_pdf, PDF_TEMPLATES

# -----------------------------
# Flask Setup
# -----------------------------
app = Flask(__name__)
CORS(app)


# -----------------------------
# Helpers
# -----------------------------
def json_error(message, status=400):
    return jsonify({"success": False, "error": message}), status


def get_json_or_error():
    try:
        data = request.get_json(force=True, silent=False)
        if data is None:
            return None, json_error("Request body must be valid JSON")
        return data, None
    except Exception:
        return None, json_error("Request body must be valid JSON")


def get_openai_client():
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key or not OpenAI:
        return None

    os.environ["OPENAI_API_KEY"] = api_key
    return OpenAI()



def get_gemini_client():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key or not genai:
        return None
    genai.configure(api_key=api_key)
    return genai.GenerativeModel("models/gemini-2.5-flash")


# -----------------------------
# Gemini JSON Sanitizer
# -----------------------------
def sanitize_ai_json(text):
    """
    Strips markdown/code fences & ensures JSON fields exist.
    Ensures suggested_edits is ALWAYS a list.
    """
    cleaned = (
        text.replace("```json", "")
        .replace("```", "")
        .replace("json", "")
        .strip()
    )

    try:
        data = json.loads(cleaned)
    except Exception:
        return None

    data.setdefault("missing_keywords", [])
    data.setdefault("strengths", [])
    data.setdefault("suggested_edits", [])

    if isinstance(data["suggested_edits"], str):
        data["suggested_edits"] = [data["suggested_edits"]]

    return data


# -----------------------------
# Health Endpoints
# -----------------------------
@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "healthy"}), 200


@app.route("/health/pdf", methods=["GET"])
def health_pdf():
    return jsonify({"pdf_templates": PDF_TEMPLATES}), 200


# -----------------------------
# PDF Export Endpoint
# -----------------------------
@app.route("/export-pdf", methods=["POST"])
def export_pdf():
    try:
        data, error = get_json_or_error()
        if error:
            return error

        content = data.get("content")
        if not content or not isinstance(content, str) or not content.strip():
            return json_error("Content is required")

        document_type = data.get("document_type", "resume")
        template = data.get("template", "classic")

        if template not in PDF_TEMPLATES:
            return json_error(f"template must be one of: {PDF_TEMPLATES}")

        # Generate the PDF bytes from markdown content
        pdf_bytes = generate_pdf(content, template)

        # 🔐 Guard: make sure generate_pdf actually returned bytes
        if not isinstance(pdf_bytes, (bytes, bytearray)) or not pdf_bytes:
            app.logger.error("generate_pdf returned empty or invalid data")
            return json_error("Failed to generate the PDF content.", 500)

        filename = "resume.pdf" if document_type == "resume" else "cover_letter.pdf"

        return Response(
            pdf_bytes,
            mimetype="application/pdf",
            headers={
                "Content-Disposition": f'attachment; filename="{filename}"',
                "Content-Length": str(len(pdf_bytes)),
            },
        )

    except Exception as e:
        app.logger.error(f"Error generating PDF: {e}")
        return json_error("An error occurred while generating the PDF", 500)



# -----------------------------
# Resume Generation
# -----------------------------
@app.route("/generate-resume", methods=["POST"])
def generate_resume():
    try:
        data, error = get_json_or_error()
        if error:
            return error

        required_fields = ["name", "education", "experience", "skills"]
        for field in required_fields:
            if field not in data or not isinstance(data[field], str):
                return json_error(f"Missing required field: {field}")

        name = data["name"]
        education = data["education"]
        experience = data["experience"]
        skills = data["skills"]
        template = data.get("template", "chronological")

        gemini = get_gemini_client()
        openai_client = get_openai_client()

        from templates import create_ai_prompt, format_resume_mock

        prompt = create_ai_prompt(name, education, experience, skills, template)

        if gemini:
            system_instruction = (
                "You are an API that outputs ONLY valid JSON.\n"
                "NO markdown. NO code fences. NO backticks.\n"
                "Return ONLY this structure:\n"
                "{\n"
                '  "resume": "string"\n'
                "}\n"
            )

            model = genai.GenerativeModel(
                "models/gemini-2.5-flash",
                system_instruction=system_instruction,
            )
            response = model.generate_content(prompt)
            cleaned = response.text.replace("```", "").replace("json", "").strip()

            try:
                parsed = json.loads(cleaned)
                resume_text = parsed.get("resume", cleaned)
            except Exception:
                resume_text = cleaned

        elif openai_client:
            response = openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a professional resume writer.",
                    },
                    {"role": "user", "content": prompt},
                ],
            )
            resume_text = response.choices[0].message.content

        else:
            resume_text = format_resume_mock(
                name, education, experience, skills, template
            )

        return jsonify({"success": True, "resume": resume_text, "template": template})

    except Exception as e:
        app.logger.error(str(e))
        return json_error("An error occurred while generating the resume", 500)


# -----------------------------
# Cover Letter Prompt Builder
# -----------------------------
def build_cover_letter_prompt(data):
    return (
<<<<<<< HEAD
        f"Write a professional cover letter:\n"
        f"Applicant: {data['name']}\n"
        f"Company: {data['company']}\n"
        f"Role: {data['role']}\n"
        f"Job Description: {data['job_description']}\n"
        f"Experience: {data['experience']}\n"
        f"Skills: {data['skills']}\n"
=======
        f"Write a professional cover letter for the following job application. Do not include emojis in the cover letter.\n"
        f"Applicant Name: {data.get('name', '')}\n"
        f"Company: {data.get('company', '')}\n"
        f"Role: {data.get('role', '')}\n"
        f"Job Description: {data.get('job_description', '')}\n"
        f"Relevant Experience: {data.get('experience', '')}\n"
        f"Skills: {data.get('skills', '')}\n"
        f"Format the cover letter in plain text."
>>>>>>> 22a27ef8ed00107ca62be6acd41d0f0aba76e2e5
    )


# -----------------------------
# Cover Letter Endpoint
# -----------------------------
@app.route("/generate-cover-letter", methods=["POST"])
def generate_cover_letter():
    try:
        data, error = get_json_or_error()
        if error:
            return error

        fields = ["name", "company", "role", "job_description", "experience", "skills"]
        for f in fields:
            if f not in data or not isinstance(data[f], str):
                return json_error(f"Missing required field: {f}")

        gemini = get_gemini_client()
        openai_client = get_openai_client()

        prompt = build_cover_letter_prompt(data)

        if gemini:
            system_instruction = (
                "You are an API. Output ONLY JSON.\n"
                "Return: { \"cover_letter\": \"string\" }\n"
                "NO markdown, NO fences, NO extra text."
            )

            model = genai.GenerativeModel(
                "models/gemini-2.5-flash", system_instruction=system_instruction
            )

            response = model.generate_content(prompt)
            cleaned = response.text.replace("```", "").strip()

            try:
                parsed = json.loads(cleaned)
                cover_letter = parsed.get("cover_letter", cleaned)
            except Exception:
                cover_letter = cleaned

            return jsonify({"success": True, "cover_letter": cover_letter})

        # OpenAI fallback
        elif openai_client:
            response = openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Write a cover letter."},
                    {"role": "user", "content": prompt},
                ],
            )
            return jsonify(
                {"success": True, "cover_letter": response.choices[0].message.content}
            )

        # Mock mode
        else:
            return jsonify(
                {
                    "success": True,
                    "cover_letter": (
                        f"Dear {data['company']} Hiring Team,\n\n"
                        f"I am excited to apply for the {data['role']} role..."
                    ),
                }
            )

    except Exception as e:
        app.logger.error(str(e))
        return json_error("Error generating cover letter", 500)


# -----------------------------
# Resume Optimization Helpers
# -----------------------------
STOPWORDS = {...}  # You can keep your full stopword list as-is


def parse_keywords(text):
    words = re.findall(r"\b\w+\b", text.lower())
    return sorted({w for w in words if w not in STOPWORDS and len(w) > 2})


def analyze_alignment(resume_text, job_keywords):
    resume_lc = resume_text.lower()
    missing = [kw for kw in job_keywords if kw not in resume_lc]
    strengths = [kw for kw in job_keywords if kw in resume_lc]
    return missing, strengths

<<<<<<< HEAD
=======
def _extract_json_from_ai_response(content):
    """
    Extract JSON object from AI response, handling cases where it's wrapped in markdown code fences.
    Returns parsed JSON dict or None if parsing fails.
    """
    content = content.strip()
    
    # Remove markdown code fences if present
    if content.startswith('```'):
        # Find the first newline after ```
        start = content.find('\n')
        if start != -1:
            # Find the closing ```
            end = content.rfind('```')
            if end != -1:
                content = content[start+1:end].strip()
    
    # Try to parse JSON
    try:
        return json.loads(content)
    except json.JSONDecodeError:
        # Try to find JSON object within the text
        try:
            start = content.find('{')
            end = content.rfind('}')
            if start != -1 and end != -1 and end > start:
                return json.loads(content[start:end+1])
        except json.JSONDecodeError:
            pass
    
    return None

def _format_suggestions(text):
    """
    Format suggestions text to ensure it's properly bulleted.
    Converts raw text into bullet-point format if needed.
    """
    if not text or not isinstance(text, str):
        return ""
    
    text = text.strip()
    
    # If already properly formatted with bullets, return as-is
    lines = text.split('\n')
    if all(line.strip().startswith('-') or line.strip().startswith('•') or not line.strip() for line in lines):
        return text
    
    # Convert numbered lists or plain text to bullets
    formatted_lines = []
    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue
        
        # Remove common prefixes (numbers, existing bullets, etc.)
        stripped = re.sub(r'^\d+[\.\)]\s*', '', stripped)  # Remove "1. " or "1) "
        stripped = re.sub(r'^[•\-\*]\s*', '', stripped)     # Remove existing bullets
        
        if stripped:
            formatted_lines.append(f"- {stripped}")
    
    return '\n'.join(formatted_lines) if formatted_lines else text
>>>>>>> 22a27ef8ed00107ca62be6acd41d0f0aba76e2e5

def build_ai_prompt(resume_text, job_description):
    return (
<<<<<<< HEAD
        "You are a resume optimization API.\n"
        "Output ONLY this exact JSON structure:\n"
        "{\n"
        '  "missing_keywords": ["string"],\n'
        '  "strengths": ["string"],\n'
        '  "suggested_edits": ["string"]\n'
        "}\n\n"
        "Rules:\n"
        "- No markdown.\n"
        "- No code fences.\n"
        "- No backticks.\n"
        "- suggested_edits MUST be a list.\n\n"
        f"Resume:\n{resume_text}\n\n"
        f"Job Description:\n{job_description}\n"
=======
        "You are a resume optimization assistant. "
        "Given the following resume and job description, analyze them and respond ONLY with valid JSON in this exact format:\n"
        '{"missing_keywords": ["keyword1", "keyword2"], "strengths": ["strength1", "strength2"], "suggested_edits": "- suggestion1\\n- suggestion2\\n- suggestion3"}\n\n'
        f"Resume:\n{resume_text}\n\n"
        f"Job Description:\n{job_description}\n\n"
        "Requirements:\n"
        "- missing_keywords: Array of specific keywords/skills from job description NOT in the resume\n"
        "- strengths: Array of areas where resume aligns well with job description\n"
        "- suggested_edits: String with 3-6 bullet points (each line must start with '- '). Give actionable suggestions to improve the resume.\n\n"
        "Return ONLY the JSON object, no other text or explanation."
>>>>>>> 22a27ef8ed00107ca62be6acd41d0f0aba76e2e5
    )


<<<<<<< HEAD
# -----------------------------
# Optimize Resume Endpoint
# -----------------------------
@app.route("/optimize-resume", methods=["POST"])
=======
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
>>>>>>> 22a27ef8ed00107ca62be6acd41d0f0aba76e2e5
def optimize_resume():
    try:
        data, error = get_json_or_error()
        if error:
            return error

        resume_text = data.get("resume_text", "").strip()
        job_description = data.get("job_description", "").strip()

        if not resume_text or not job_description:
            return jsonify(
                {
                    "success": True,
                    "missing_keywords": [],
                    "strengths": [],
                    "suggested_edits": ["Please provide resume_text and job_description."],
                }
            )

        gemini = get_gemini_client()
        openai_client = get_openai_client()

        # -----------------
        # Gemini Path
        # -----------------
        if gemini:
            system_instruction = (
                "You are an API that outputs ONLY valid JSON.\n"
                "NO markdown, NO code fences, NO extra text.\n"
                "Valid keys: missing_keywords, strengths, suggested_edits."
            )

            model = genai.GenerativeModel(
                "models/gemini-2.5-flash",
                system_instruction=system_instruction,
            )

            prompt = build_ai_prompt(resume_text, job_description)
<<<<<<< HEAD
            response = model.generate_content(prompt)
            cleaned = response.text.replace("```", "").replace("json", "").strip()

            parsed = sanitize_ai_json(cleaned)
            if parsed:
                parsed["success"] = True
                return jsonify(parsed)

            # fallback if JSON parsing fails
            return jsonify(
                {
                    "success": True,
                    "missing_keywords": [],
                    "strengths": [],
                    "suggested_edits": [cleaned],  # force as list
                }
            )

        # -----------------
        # OpenAI Path
        # -----------------
        elif openai_client:
=======
            response = gemini.generate_content(prompt)
            ai_content = response.text.strip()
            # Try to extract JSON from the response
            ai_json = _extract_json_from_ai_response(ai_content)
            if ai_json:
                return jsonify({
                    "success": True,
                    "missing_keywords": ai_json.get('missing_keywords', []),
                    "strengths": ai_json.get('strengths', []),
                    "suggested_edits": _format_suggestions(ai_json.get('suggested_edits', ''))
                }), 200
            else:
                # Fallback: parse the raw text into bullets
                return jsonify({
                    "success": True,
                    "missing_keywords": [],
                    "strengths": [],
                    "suggested_edits": _format_suggestions(ai_content)
                }), 200
        elif client:
>>>>>>> 22a27ef8ed00107ca62be6acd41d0f0aba76e2e5
            prompt = build_ai_prompt(resume_text, job_description)

            response = openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
<<<<<<< HEAD
                    {"role": "system", "content": "You are a resume optimization API."},
                    {"role": "user", "content": prompt},
=======
                    {"role": "system", "content": "You are a resume optimization assistant. Always respond with valid JSON."},
                    {"role": "user", "content": prompt}
>>>>>>> 22a27ef8ed00107ca62be6acd41d0f0aba76e2e5
                ],
            )
<<<<<<< HEAD

            raw = response.choices[0].message.content.strip()
            parsed = sanitize_ai_json(raw)

            if parsed:
                parsed["success"] = True
                return jsonify(parsed)

            return jsonify(
                {
                    "success": True,
                    "missing_keywords": [],
                    "strengths": [],
                    "suggested_edits": [raw],
                }
            )

        # -----------------
        # Mock Fallback Mode
        # -----------------
        job_keywords = parse_keywords(job_description)
        missing, strengths = analyze_alignment(resume_text, job_keywords)

        suggestions = [
            f"Add '{kw}' under Skills or Experience." for kw in missing[:3]
        ] + [
            f"Highlight experience with '{kw}'." for kw in strengths[:2]
        ]

        if not suggestions:
            suggestions.append("Consider adding more technical detail to your resume.")

        return jsonify(
            {
=======
            ai_content = response.choices[0].message.content.strip()
            # Try to extract JSON from the response
            ai_json = _extract_json_from_ai_response(ai_content)
            if ai_json:
                return jsonify({
                    "success": True,
                    "missing_keywords": ai_json.get('missing_keywords', []),
                    "strengths": ai_json.get('strengths', []),
                    "suggested_edits": _format_suggestions(ai_json.get('suggested_edits', ''))
                }), 200
            else:
                # Fallback: parse the raw text into bullets
                return jsonify({
                    "success": True,
                    "missing_keywords": [],
                    "strengths": [],
                    "suggested_edits": _format_suggestions(ai_content)
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
>>>>>>> 22a27ef8ed00107ca62be6acd41d0f0aba76e2e5
                "success": True,
                "missing_keywords": missing,
                "strengths": strengths,
                "suggested_edits": suggestions,
            }
        )

    except Exception as e:
        app.logger.error(str(e))
        return json_error("Error optimizing resume", 500)


# -----------------------------
# Run Flask
# -----------------------------
if __name__ == "__main__":
    debug_mode = os.getenv("FLASK_DEBUG", "False").lower() == "true"
    app.run(debug=debug_mode, host="0.0.0.0", port=5000)
