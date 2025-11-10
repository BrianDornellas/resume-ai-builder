# Week 2 MVP - Resume Generation Usage Guide

## Overview
This document provides a guide for using the AI Resume Builder MVP implemented in Week 2.

## Features Implemented

### Backend API
1. **Health Check Endpoint** - `GET /health`
   - Returns server status
   - Example response:
     ```json
     {"status": "healthy"}
     ```

2. **Resume Generation Endpoint** - `POST /generate-resume`
   - Accepts user information and generates a professional resume using AI
   - Request format:
     ```json
     {
       "name": "John Doe",
       "education": "Bachelor of Science in Computer Science, XYZ University, 2020",
       "experience": "Software Engineer at ABC Corp (2020-2023): Developed web applications using React and Node.js. Led a team of 3 developers.",
       "skills": "Python, JavaScript, React, Node.js, Flask, Docker"
     }
     ```
   - Response format:
     ```json
     {
       "success": true,
       "resume": "Generated resume text here..."
     }
     ```

### Frontend UI
- Clean, modern Material Design interface
- Form with four input fields:
  - **Name**: Text input for full name
  - **Education**: Multi-line text area for educational background
  - **Experience**: Multi-line text area for work experience
  - **Skills**: Multi-line text area for skills list
- "Generate Resume" button with loading indicator
- Resume display area that shows the AI-generated resume

## Example Usage

### 1. Start the Backend
```bash
cd backend
python app.py
```

The server will start on `http://localhost:5000`

### 2. Start the Frontend
```bash
cd frontend
flutter run -d chrome
```

The Flutter web app will open in Chrome

### 3. Fill in Your Information
Enter your details in the form:
- **Name**: Jane Smith
- **Education**: Master of Computer Science, Stanford University, 2021
- **Experience**: Senior Software Engineer at Tech Corp (2021-2025): Led development of cloud-based microservices architecture. Managed team of 5 engineers. Implemented CI/CD pipelines reducing deployment time by 60%.
- **Skills**: Python, Go, Kubernetes, Docker, AWS, PostgreSQL, React, TypeScript

### 4. Generate Resume
Click the "Generate Resume" button and wait a few seconds while the AI processes your information.

### 5. View Results
The generated resume will appear below the form in a formatted text box.

## Testing the API Directly

You can also test the backend API directly using curl:

```bash
curl -X POST http://localhost:5000/generate-resume \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test User",
    "education": "BS Computer Science, MIT, 2020",
    "experience": "Software Developer at Example Co: Built web apps",
    "skills": "Python, JavaScript, SQL"
  }'
```

## Environment Configuration

### Development
- Set `FLASK_DEBUG=True` in your `.env` file for detailed error messages
- API calls are made to `http://localhost:5000`

### Production
- Set `FLASK_DEBUG=False` for security
- Use a production WSGI server (e.g., gunicorn) instead of Flask's built-in server
- Configure proper CORS settings for your production domain

## Troubleshooting

### Backend Issues
1. **OpenAI API Key Error**: Make sure `OPENAI_API_KEY` is set in the `.env` file
2. **Port Already in Use**: Change the port in `app.py` if 5000 is occupied
3. **Module Import Errors**: Run `pip install -r requirements.txt` to install dependencies

### Frontend Issues
1. **Connection Refused**: Ensure the backend is running on `http://localhost:5000`
2. **CORS Errors**: The backend has CORS enabled for all origins in development
3. **Flutter Dependencies**: Run `flutter pub get` to install required packages

## Next Steps (Week 3+)
- Add resume templates with different formatting styles
- Implement cover letter generation
- Add keyword optimization based on job descriptions
- PDF export functionality
- Save and manage multiple resume versions
