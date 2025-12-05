# Cover Letter – Test Checklist

Manual test scenarios for the Cover Letter feature (both mock mode and real API):

1. **Valid Submit (Mock & Real API):**
   - Fill all fields with realistic data and submit.
   - Expect a generated cover letter to appear with no errors.
   - In mock mode, the letter should be deterministic and not AI-generated.

2. **Missing Required Fields:**
   - Leave Name, Company, or Role empty and try to submit.
   - Expect a validation error and no request sent.

3. **Long Job Description:**
   - Enter a very long job description (e.g., 1000+ characters).
   - Submit and verify the cover letter is generated and not truncated.

4. **Network Offline Case:**
   - Disconnect from the network or stop the backend server.
   - Submit the form and expect a friendly error banner about network issues.

5. **Mock-Mode Banner Present:**
   - With no OpenAI API key set, submit a valid form.
   - Confirm the generated letter is a mock and notifies the user (e.g., deterministic content, not AI-generated).

6. **Copy-to-Clipboard Works:**
   - After a cover letter is generated, click the Copy button.
   - Confirm the button shows a "Copied!" message and the clipboard contains the full letter text.

Repeat these checks for both mock mode (no API key) and real API mode (valid OpenAI key set).

# AI-Powered Resume & Cover Letter Builder

## 📌 Description
This project is a web application that helps users generate tailored **resumes** and **cover letters** using AI.  
It takes user input (experience, education, skills) and job descriptions, then produces professional, export-ready documents.  

## 🛠 Tech Stack
- **Python (Flask or FastAPI)** – backend  
- **Flutter (Dart, running as a web app)** – frontend  
- **OpenAI / Claude API** – AI-powered content generation  
- **Export libraries** – PDF/Word output  

## 🚀 Getting Started

### Prerequisites
- Python 3.8 or higher
- Flutter SDK 3.0 or higher
- OpenAI API key (optional - app works with placeholder format without it)

### Backend Setup

1. Clone this repository:
   ```bash
   git clone https://github.com/BrianDornellas/resume-ai-builder.git
   cd resume-ai-builder
   ```

2. Set up the backend:
   ```bash
   cd backend
   source venv/bin/activate
   pip install -r requirements.txt
   ```

3. (Optional) Create a `.env` file in the `backend` directory for AI-powered resume generation:
   ```bash
   cp .env.example .env
   ```
   Then edit `.env` and add your OpenAI API key:
   ```
   OPENAI_API_KEY=your_actual_api_key_here
   FLASK_DEBUG=True
   ```
   Note: The app works without an API key using a placeholder format. Set `FLASK_DEBUG=False` in production environments.

4. Run the backend server:
   ```bash
   python app.py
   ```
   The backend will run on `http://localhost:5000`

### Frontend Setup

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   flutter pub get
   ```

3. Run the Flutter web app:
   ```bash
   flutter run -d chrome
   ```

### Using the Application

1. Make sure the backend is running on `http://localhost:5000`
2. Open the Flutter web app in your browser
3. Fill in the form with your information:
   - **Name**: Your full name
   - **Education**: Your educational background
   - **Experience**: Your work experience
   - **Skills**: Your technical and professional skills
   - **Template**: Choose between Chronological or Functional layout
4. Click "Generate Resume"
5. The AI-generated resume will appear below the form in beautifully formatted Markdown

#### Resume Templates

**Chronological Template:**
- Emphasizes work history in reverse chronological order
- Ideal for traditional career progression
- Best for candidates with consistent work history

**Functional Template:**
- Emphasizes skills and competencies over timeline
- Ideal for career changers or those with employment gaps
- Best for highlighting transferable skills

For detailed usage instructions and examples, see [USAGE_GUIDE.md](USAGE_GUIDE.md)

For architecture and technical details, see [ARCHITECTURE.md](ARCHITECTURE.md)

## 📄 PDF Export

The application supports exporting resumes and cover letters as PDF files with two template styles:

- **Classic**: Traditional layout with serif fonts and horizontal rules
- **Modern**: Contemporary layout with sans-serif fonts and accent colors

### PDF Export API

**Endpoint**: `POST /export-pdf`

**Request Body**:
```json
{
  "document_type": "resume" | "cover_letter",
  "content": "Your document content (plain text or Markdown)",
  "template": "classic" | "modern"
}
```

**Response**: PDF binary stream with `application/pdf` content type.

### Health Check

**Endpoint**: `GET /health/pdf`

**Response**:
```json
{
  "pdf_templates": ["classic", "modern"]
}
```

### Smoke Test Script

A smoke test script is provided to verify the PDF export functionality:

```bash
# Prerequisites: Backend server must be running
cd backend && python app.py &

# Install requests if needed
pip install requests

# Run the smoke test (saves output to out.pdf by default)
python scripts/smoke_pdf.py

# Options:
python scripts/smoke_pdf.py --template modern --output my_resume.pdf
python scripts/smoke_pdf.py --type cover_letter --template classic
```

## 📋 Roadmap

Week 1: Repo + README setup ✅

Week 2: Resume generation (basic text) ✅

Week 3: Resume templates ✅

Week 4: Cover letter generation ✅

Week 5: Keyword optimization ✅

Week 6: PDF export ✅

Week 7: Save & polish features ✅

Week 8: Finalize & demo

## 💾 Working with Drafts

The application supports saving and loading drafts for both resumes and cover letters. Drafts are stored in your browser's localStorage, so they persist between sessions.

### Saving Drafts

1. Fill in any fields on the Resume or Cover Letter form
2. Click the **"Save Draft"** button in the top-right corner
3. A confirmation message will appear when the draft is saved

Drafts automatically capture:
- All form field values (name, education, experience, skills, etc.)
- The selected template
- Any generated resume or cover letter text

### Loading Drafts

1. Click the **"My Drafts"** button to open the drafts dialog
2. Browse your saved drafts (sorted by most recent)
3. Click on a draft to load it into the form
4. The form fields and any generated content will be restored

### Managing Drafts

From the My Drafts dialog, you can:
- **Rename**: Click the edit icon to change a draft's title
- **Delete**: Click the trash icon to permanently remove a draft
- **Load**: Click anywhere on a draft card to load it

### Notes

- Drafts are stored locally in your browser and are not synced across devices
- Clearing your browser data will delete all saved drafts
- Each draft type (resume/cover letter) has its own separate list