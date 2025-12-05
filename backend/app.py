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
    return OpenAI(api_key=api_key)


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

        pdf_bytes = generate_pdf(content, template)
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
        app.logger.error(str(e))
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
        f"Write a professional cover letter:\n"
        f"Applicant: {data['name']}\n"
        f"Company: {data['company']}\n"
        f"Role: {data['role']}\n"
        f"Job Description: {data['job_description']}\n"
        f"Experience: {data['experience']}\n"
        f"Skills: {data['skills']}\n"
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


def build_ai_prompt(resume_text, job_description):
    return (
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
    )


# -----------------------------
# Optimize Resume Endpoint
# -----------------------------
@app.route("/optimize-resume", methods=["POST"])
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
            prompt = build_ai_prompt(resume_text, job_description)

            response = openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a resume optimization API."},
                    {"role": "user", "content": prompt},
                ],
            )

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
