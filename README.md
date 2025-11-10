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
- OpenAI API key

### Backend Setup

1. Clone this repository:
   ```bash
   git clone https://github.com/BrianDornellas/resume-ai-builder.git
   cd resume-ai-builder
   ```

2. Set up the backend:
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

3. Create a `.env` file in the `backend` directory:
   ```bash
   cp .env.example .env
   ```
   Then edit `.env` and add your OpenAI API key:
   ```
   OPENAI_API_KEY=your_actual_api_key_here
   FLASK_DEBUG=True
   ```
   Note: Set `FLASK_DEBUG=False` in production environments.

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
4. Click "Generate Resume"
5. The AI-generated resume will appear below the form

## 📋 Roadmap

Week 1: Repo + README setup ✅

Week 2: Resume generation (basic text) ✅

Week 3: Resume templates

Week 4: Cover letter generation

Week 5: Keyword optimization

Week 6: PDF export

Week 7: Save & polish features

Week 8: Finalize & demo