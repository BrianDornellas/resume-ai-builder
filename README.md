
# AI-Powered Resume & Cover Letter Builder

An intelligent web application for creating professional, tailored resumes and cover letters using AI. Built with Flutter Web and Flask, it supports real-time editing, AI-powered optimization, PDF export, and draft management.

---

## 🚀 Features

- **Editable Resume Area:** Edit generated resumes directly in the browser before exporting or optimizing.
- **Markdown Rendering:** Resumes are rendered with Markdown for rich formatting and easy editing.
- **AI-Powered Generation:** Supports both OpenAI GPT-3.5 and Google Gemini for resume and cover letter creation.
- **Keyword Optimization:** Analyze your resume against job descriptions for missing keywords and strengths.
- **Strict JSON Output:** Gemini integration enforces clean, valid JSON responses for reliable frontend parsing.
- **Multiple PDF Templates:** Export resumes and cover letters as PDF using Classic or Modern templates.
- **Draft Saving & Loading:** Save, load, rename, and delete drafts using browser localStorage.
- **Mock Mode:** Use deterministic, template-based output for development and demos without API keys.
- **Customizable Frontend Port:** Run the Flutter web app on any port (e.g., 6969) for local development.

---

## 🛠 Tech Stack

| Layer      | Technology                                          |
|------------|-----------------------------------------------------|
| Frontend   | Flutter Web (Dart 3.0+)                             |
| Backend    | Python 3.8+ with Flask 3.0                          |
| AI         | OpenAI GPT-3.5 / Google Gemini (optional)           |
| PDF Export | ReportLab                                           |
| Storage    | Browser localStorage (drafts)                       |

## 🚀 Prerequisites & Quickstart

### Prerequisites

- **Python 3.8+** – for the backend API
- **Flutter SDK 3.0+** – for the web frontend
- **Chrome browser** – recommended for development
- **OpenAI or Gemini API key** (optional) – enables real AI generation; app works in mock mode without it

### Backend Setup

```bash
# 1. Navigate to backend directory
cd backend

# 2. Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. (Optional) Configure environment variables
cp .env.example .env
# Edit .env and set:
#   OPENAI_API_KEY=your_key_here   (for OpenAI)
#   GEMINI_API_KEY=your_key_here   (for Google Gemini)
#   FLASK_DEBUG=True               (for development)

# Or export your Gemini API key in your terminal (before running the backend):
export GEMINI_API_KEY=your-gemini-api-key-here

# 5. Run the server
python app.py
# Server runs at http://localhost:5000
```

### Frontend Setup

```bash
# 1. Navigate to frontend directory
cd frontend

# 2. Verify Flutter installation
flutter doctor

# 3. Install dependencies
flutter pub get

# 4. Run the web app
flutter run -d chrome
or
flutter run -d chrome --web-hostname localhost --web-port 6969
# Or use any available port
```

---

## 📡 API Endpoints

| Method | Path                    | Description                                          |
|--------|-------------------------|------------------------------------------------------|
| GET    | `/health`               | Health check – returns `{"status": "healthy"}`       |
| GET    | `/health/pdf`           | PDF health check – returns available templates       |
| POST   | `/generate-resume`      | Generate a resume from user profile and template     |
| POST   | `/generate-cover-letter`| Generate a cover letter for a specific job           |
| POST   | `/optimize-resume`      | Analyze resume against job description for keywords  |
| POST   | `/export-pdf`           | Export resume or cover letter as PDF                 |

### Example: Generate Resume

```bash
curl -X POST http://localhost:5000/generate-resume \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John Doe",
    "education": "BS Computer Science, State University, 2020",
    "experience": "Software Engineer at Tech Corp (2020-2023)",
    "skills": "Python, JavaScript, React, Flask",
    "template": "chronological"
  }'
```

---

## 🤖 Modes: Mock vs Real AI

| Mode     | Trigger                                | Behavior                                           |
|----------|----------------------------------------|----------------------------------------------------|
| **Mock** | No API key in `.env`                   | Returns deterministic, template-based output       |
| **Real** | `OPENAI_API_KEY` or `GEMINI_API_KEY` set | Calls AI API for dynamic, personalized content   |

**Mock mode** is ideal for:
- Development and testing without API costs
- Demos where consistent output is preferred
- Environments where API access is restricted

**Real AI mode** provides:
- Personalized, context-aware content
- Better keyword optimization suggestions
- More natural language in generated documents

## 📄 PDF Export

Export resumes and cover letters as professional PDF documents:

### Available Templates

- **Classic**: Traditional layout with serif fonts and horizontal rules
- **Modern**: Contemporary layout with sans-serif fonts and accent colors

### API Usage

```bash
curl -X POST http://localhost:5000/export-pdf \
  -H "Content-Type: application/json" \
  -d '{
    "document_type": "resume",
    "content": "Your resume content here...",
    "template": "modern"
  }' --output resume.pdf
```

### Health Check

```bash
curl http://localhost:5000/health/pdf
# Returns: {"pdf_templates": ["classic", "modern"]}
```

## 💾 Drafts & localStorage

Drafts are automatically saved to your browser's localStorage:

- **Save**: Click "Save Draft" to capture all form fields and generated content
- **Load**: Click "My Drafts" to browse and restore previous work
- **Manage**: Rename or delete drafts from the drafts dialog

**Important Notes:**
- Drafts are stored locally and do not sync across devices
- Clearing browser data will delete all saved drafts
- Resume and cover letter drafts are stored separately

## 🔧 Quick Dev Scripts

Convenience scripts for rapid development:

```bash
# Start backend (creates venv if needed, installs deps, runs Flask)
./backend/start.sh

# Start frontend (runs Flutter web on Chrome)
./frontend/start.sh

# Smoke test (checks /health, /health/pdf, and /generate-resume mock)
./scripts/smoke.sh
```

See the scripts for details on what each one does.

## 🐛 Troubleshooting

### CORS Errors

**Symptom**: Browser console shows "Access-Control-Allow-Origin" errors.

**Solution**: Ensure the backend is running with CORS enabled (it is by default via `flask-cors`). Check that you're accessing the frontend from a proper origin, not `file://`.

### 500 Internal Server Errors

**Symptom**: API returns 500 status code.

**Possible causes**:
1. Missing required fields in request body
2. Invalid JSON payload
3. Backend dependencies not installed

**Debug steps**:
```bash
# Check backend logs
FLASK_DEBUG=True python app.py

# Verify request format
curl -X POST http://localhost:5000/generate-resume \
  -H "Content-Type: application/json" \
  -d '{"name":"Test","education":"Test","experience":"Test","skills":"Test"}'
```

### Bad JSON / Parse Errors

**Symptom**: "Request body must be valid JSON" error.

**Solution**: Ensure your request:
1. Has `Content-Type: application/json` header
2. Contains valid JSON (no trailing commas, proper quotes)
3. Includes all required fields as strings

### Flutter Web Not Loading

**Symptom**: Blank page or loading spinner.

**Solution**:
```bash
# Clean and rebuild
cd frontend
flutter clean
flutter pub get
flutter run -d chrome --web-port=8080
```

### PDF Generation Fails

**Symptom**: PDF export returns error or corrupted file.

**Solution**: Ensure ReportLab is installed:
```bash
pip install reportlab==4.2.0
```

---

## 📋 Additional Documentation

- [USAGE_GUIDE.md](USAGE_GUIDE.md) – Detailed usage instructions and examples
- [ARCHITECTURE.md](ARCHITECTURE.md) – Technical architecture and design decisions
- [RELEASE_CHECKLIST.md](RELEASE_CHECKLIST.md) – Pre-release verification checklist

---

## 📜 License & Credits

**Course**: CMPS 357 – Software Engineering

**Contributors**: Brian Dornellas

**Acknowledgments**:
- OpenAI for GPT API
- Google for Gemini API
- Flutter and Flask communities

---

*Built with ❤️ for CMPS 357*