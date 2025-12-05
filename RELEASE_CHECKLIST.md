# Release Checklist

Pre-release verification checklist for the AI-Powered Resume & Cover Letter Builder.

## 🔍 Lint & Format Checks

### Dart (Frontend)

```bash
cd frontend

# Analyze Dart code for issues
flutter analyze

# Check formatting
dart format --set-exit-if-changed lib/ test/

# Fix formatting issues
dart format lib/ test/
```

### Python (Backend)

```bash
cd backend

# Activate virtual environment
source venv/bin/activate

# Check with flake8 (install if needed: pip install flake8)
flake8 app.py pdf_generator.py templates.py --max-line-length=120

# Check with pylint (install if needed: pip install pylint)
pylint app.py pdf_generator.py templates.py --disable=C0114,C0115,C0116

# Format with black (install if needed: pip install black)
black --check app.py pdf_generator.py templates.py

# Fix formatting
black app.py pdf_generator.py templates.py
```

## ✅ Manual Test Checklist

### Resume Generation

- [ ] Fill all fields (name, education, experience, skills) and generate
- [ ] Test with Chronological template
- [ ] Test with Functional template
- [ ] Verify Markdown renders correctly
- [ ] Test with empty fields (should show validation error)
- [ ] Test with very long input (1000+ characters)

### Cover Letter Generation

- [ ] Fill all fields (name, company, role, job description, experience, skills)
- [ ] Generate cover letter
- [ ] Verify content is professional and contextual
- [ ] Test copy-to-clipboard functionality
- [ ] Test with missing required fields (should show validation error)

### Resume Optimization

- [ ] Generate a resume first
- [ ] Enter a job description
- [ ] Run optimization
- [ ] Verify missing keywords are identified
- [ ] Verify strengths are highlighted
- [ ] Verify suggested edits are actionable

### PDF Export

- [ ] Generate a resume
- [ ] Export with Classic template
- [ ] Export with Modern template
- [ ] Open PDF in viewer and verify formatting
- [ ] Generate a cover letter
- [ ] Export cover letter as PDF
- [ ] Verify PDF file size is reasonable (<1MB)

### Drafts

- [ ] Save a resume draft
- [ ] Save a cover letter draft
- [ ] Close and reopen browser
- [ ] Load saved drafts
- [ ] Rename a draft
- [ ] Delete a draft
- [ ] Verify localStorage persistence

## 🌐 Browser Compatibility

### Chrome (Primary)

- [ ] All features work correctly
- [ ] No console errors
- [ ] Responsive design at different viewport sizes
- [ ] PDF download works

### Firefox

- [ ] All features work correctly
- [ ] No console errors
- [ ] localStorage works correctly
- [ ] PDF download works

### Edge (Optional)

- [ ] Basic functionality works
- [ ] No critical errors

## 🎬 Demo Script (2–3 Minutes)

### Introduction (30 seconds)

1. "This is an AI-powered Resume and Cover Letter Builder"
2. "Built with Flutter Web frontend and Flask backend"
3. "Works in mock mode without API keys, or with real AI using OpenAI/Gemini"

### Resume Demo (60 seconds)

1. Navigate to Resume tab
2. Fill in sample data:
   - Name: "Jane Developer"
   - Education: "MS Computer Science, Tech University, 2022"
   - Experience: "Senior Software Engineer at InnovateTech (2022-present)"
   - Skills: "Python, React, AWS, Docker, Agile"
3. Select Chronological template
4. Click "Generate Resume"
5. Show generated Markdown output
6. Click "Export PDF" with Modern template
7. Open downloaded PDF

### Cover Letter Demo (45 seconds)

1. Navigate to Cover Letter tab
2. Fill in targeting a specific job:
   - Company: "Dream Company Inc"
   - Role: "Lead Developer"
   - Job Description: "Looking for experienced developer..."
3. Generate cover letter
4. Highlight how it's tailored to the role
5. Use copy-to-clipboard feature

### Optimization Demo (30 seconds)

1. Navigate to Optimize tab
2. Paste a job description
3. Show keyword analysis
4. Highlight missing keywords and suggestions

### Closing (15 seconds)

1. Show drafts feature
2. Mention browser localStorage
3. "Questions?"

## 🔒 Privacy & Security Notes

### API Keys

- [ ] **No API keys committed to repository**
- [ ] `.env` file is in `.gitignore`
- [ ] `.env.example` contains only placeholder values
- [ ] README documents `.env` setup without real keys

### Environment Variables

Required for real AI mode (optional):
```
OPENAI_API_KEY=sk-...     # OpenAI API key
GEMINI_API_KEY=...        # Google Gemini API key
FLASK_DEBUG=False         # Must be False in production
```

### Production Checklist

- [ ] `FLASK_DEBUG=False` is set
- [ ] No debug endpoints exposed
- [ ] CORS is properly configured for production domain
- [ ] Error messages don't leak stack traces
- [ ] Rate limiting considered for public deployment

## 📋 Final Verification

- [ ] All tests pass (`flutter test` and `python -m pytest`)
- [ ] No linting errors
- [ ] README is up to date
- [ ] ARCHITECTURE.md reflects current implementation
- [ ] Demo script rehearsed and timing verified
- [ ] Backup demo data prepared (in case of API issues)

---

*Last updated: Week 8*
