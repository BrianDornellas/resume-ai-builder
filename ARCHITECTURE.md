# Architecture Overview - Week 2 MVP

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         User Browser                             │
│                                                                   │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │              Flutter Web Application                        │ │
│  │  ┌──────────────────────────────────────────────────────┐  │ │
│  │  │  Resume Form Screen (resume_form_screen.dart)         │  │ │
│  │  │  - Name Input Field                                   │  │ │
│  │  │  - Education Input Field (multi-line)                 │  │ │
│  │  │  - Experience Input Field (multi-line)                │  │ │
│  │  │  - Skills Input Field (multi-line)                    │  │ │
│  │  │  - Generate Button                                    │  │ │
│  │  │  - Resume Display Area                                │  │ │
│  │  └──────────────────────────────────────────────────────┘  │ │
│  │                           ↓                                 │ │
│  │  ┌──────────────────────────────────────────────────────┐  │ │
│  │  │  API Service (api_service.dart)                       │  │ │
│  │  │  - generateResume() method                            │  │ │
│  │  │  - HTTP POST to backend                               │  │ │
│  │  └──────────────────────────────────────────────────────┘  │ │
│  └────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
                              ↓ HTTP POST
                              ↓ localhost:5000/generate-resume
┌─────────────────────────────────────────────────────────────────┐
│                     Flask Backend Server                         │
│                                                                   │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  app.py - Flask Application                               │ │
│  │                                                            │ │
│  │  GET  /health                                             │ │
│  │  POST /generate-resume                                    │ │
│  │       ├─ Validate input fields                            │ │
│  │       ├─ Check OpenAI API key                             │ │
│  │       ├─ Create structured prompt                         │ │
│  │       └─ Call OpenAI API                                  │ │
│  └────────────────────────────────────────────────────────────┘ │
│                              ↓                                   │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  OpenAI Client Integration                                │ │
│  │  - Model: gpt-3.5-turbo                                   │ │
│  │  - System: Professional resume writer                     │ │
│  │  - User prompt: Structured resume data                    │ │
│  └────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
                              ↓ API Call
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                      OpenAI API Service                          │
│  - Processes structured prompt                                  │
│  - Generates professional resume text                           │
│  - Returns formatted resume                                     │
└─────────────────────────────────────────────────────────────────┘
```

## Data Flow

### Request Flow (User → AI)
1. **User Input**: User fills form with personal information
2. **Form Validation**: Flutter validates all required fields are filled
3. **API Call**: Frontend sends POST request to `/generate-resume`
4. **Backend Validation**: Server validates JSON structure and fields
5. **API Key Check**: Server verifies OpenAI API key is configured
6. **Prompt Creation**: Server creates structured prompt with user data
7. **AI Processing**: OpenAI processes the prompt and generates resume
8. **Response**: Generated resume is returned to backend

### Response Flow (AI → User)
1. **Backend Response**: Server wraps resume in JSON response
2. **Frontend Processing**: Flutter receives and parses response
3. **UI Update**: Resume is displayed in the UI
4. **User View**: User sees generated resume below the form

## File Structure

```
resume-ai-builder/
├── backend/
│   ├── .env.example          # Environment variables template
│   ├── app.py                # Flask application & API endpoints
│   ├── templates.py          # Resume template formatting (Week 3)
│   ├── requirements.txt      # Python dependencies
│   ├── test_app.py          # Unit tests for backend
│   ├── demo.py              # Demo script for API testing
│   └── demo_templates.py    # Demo script for templates (Week 3)
├── frontend/
│   ├── lib/
│   │   ├── main.dart                    # App entry point
│   │   ├── screens/
│   │   │   └── resume_form_screen.dart  # Main form UI with template selector
│   │   └── services/
│   │       └── api_service.dart         # Backend communication
│   ├── web/
│   │   ├── index.html       # Web app HTML template
│   │   └── manifest.json    # PWA manifest
│   └── pubspec.yaml         # Flutter dependencies
├── .gitignore               # Git ignore rules
├── README.md                # Main documentation
├── USAGE_GUIDE.md          # Usage instructions
├── ARCHITECTURE.md         # System architecture
├── WEEK2_SUMMARY.md        # Week 2 implementation summary
├── WEEK3_SUMMARY.md        # Week 3 implementation summary
└── verify-setup.sh         # Setup verification script
```

## Technologies Used

### Backend
- **Flask 3.0.0**: Lightweight web framework
- **Flask-CORS 4.0.0**: CORS support for cross-origin requests
- **OpenAI 1.3.0**: OpenAI API client library
- **Python-dotenv 1.0.0**: Environment variable management

### Frontend
- **Flutter**: Cross-platform UI framework (Web target)
- **Dart**: Programming language
- **http package**: HTTP client for API calls
- **Material Design**: UI component library

### AI
- **OpenAI GPT-3.5-turbo**: Language model for resume generation
- **Temperature: 0.7**: Balanced creativity and consistency
- **Max tokens: 1000**: Sufficient for resume content

## Security Features

1. **Environment Variables**: API keys stored securely, not in code
2. **Debug Mode Control**: Production-safe debug configuration
3. **Error Handling**: Generic error messages to prevent information leakage
4. **CORS Configuration**: Controlled cross-origin access
5. **Input Validation**: All user inputs validated before processing
6. **Dependency Security**: All dependencies scanned for vulnerabilities

## API Specification

### POST /generate-resume

**Request:**
```json
{
  "name": "string (required)",
  "education": "string (required)",
  "experience": "string (required)",
  "skills": "string (required)",
  "template": "string (optional, default: 'chronological')"
}
```

**Template Options:**
- `"chronological"` - Traditional format with reverse chronological work history
- `"functional"` - Skills-based format emphasizing competencies

**Success Response (200):**
```json
{
  "success": true,
  "resume": "string (Markdown formatted resume)",
  "template": "string (template that was used)"
}
```

**Error Response (400/500):**
```json
{
  "success": false,
  "error": "string (error message)"
}
```

### GET /health

**Success Response (200):**
```json
{
  "status": "healthy"
}
```

## Week 3 Enhancements - Resume Templates

### Template System
The application now supports multiple resume layouts:

**Templates Available:**
- **Chronological**: Traditional format emphasizing work history in reverse chronological order
- **Functional**: Skills-based format emphasizing competencies over timeline

**Backend (`templates.py`):**
- Template formatting functions for mock resumes
- Template-specific AI prompt generators (ready for Week 5)
- Markdown output format for all templates

**API Updates:**
- `/generate-resume` accepts optional `template` parameter
- Returns `template` field in response
- Defaults to 'chronological' if not specified

**Frontend:**
- Template selector dropdown in form
- Template descriptions to guide user choice
- Markdown rendering using flutter_markdown
- Visual template indicator on generated resume

**Dependencies Added:**
- `flutter_markdown: ^0.6.18` for frontend Markdown rendering

## Future Enhancements (Weeks 4-8)

- Week 3: Multiple resume template formats ✅
- Week 4: Cover letter generation
- Week 5: Keyword optimization for job descriptions & AI API integration
- Week 6: PDF export functionality
- Week 7: Save and manage multiple versions
- Week 8: Final polish and demo preparation
