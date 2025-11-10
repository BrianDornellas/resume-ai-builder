#!/bin/bash

# Setup verification script for AI Resume Builder

echo "🔍 AI Resume Builder - Setup Verification"
echo "=========================================="
echo ""

# Check Python
echo "Checking Python installation..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version)
    echo "✅ $PYTHON_VERSION found"
else
    echo "❌ Python 3 not found. Please install Python 3.8 or higher."
    exit 1
fi

# Check Flutter
echo ""
echo "Checking Flutter installation..."
if command -v flutter &> /dev/null; then
    FLUTTER_VERSION=$(flutter --version | head -n 1)
    echo "✅ $FLUTTER_VERSION found"
else
    echo "⚠️  Flutter not found. Please install Flutter SDK 3.0 or higher for frontend development."
fi

# Check backend dependencies
echo ""
echo "Checking backend setup..."
if [ -f "backend/requirements.txt" ]; then
    echo "✅ requirements.txt found"
    
    if [ -f "backend/.env" ]; then
        echo "✅ .env file found"
        
        # Check if OpenAI API key is configured
        if grep -q "OPENAI_API_KEY=your_openai_api_key_here" backend/.env 2>/dev/null; then
            echo "ℹ️  OpenAI API key not configured (using placeholder format)."
            echo "   Add your API key to backend/.env for AI-powered resumes."
        elif grep -q "OPENAI_API_KEY=" backend/.env 2>/dev/null; then
            echo "✅ OpenAI API key appears to be configured (AI-powered mode)"
        else
            echo "ℹ️  OpenAI API key not found in .env file (using placeholder format)"
        fi
    else
        echo "ℹ️  .env file not found (app will use placeholder format)."
        echo "   To enable AI-powered resumes, copy .env.example to .env and add your API key."
    fi
else
    echo "❌ backend/requirements.txt not found"
fi

# Check if backend dependencies are installed
echo ""
echo "Checking backend dependencies..."
if python3 -c "import flask" 2>/dev/null; then
    echo "✅ Flask installed"
else
    echo "⚠️  Flask not installed. Run: cd backend && pip install -r requirements.txt"
fi

if python3 -c "import openai" 2>/dev/null; then
    echo "✅ OpenAI library installed"
else
    echo "⚠️  OpenAI library not installed. Run: cd backend && pip install -r requirements.txt"
fi

# Check frontend
echo ""
echo "Checking frontend setup..."
if [ -f "frontend/pubspec.yaml" ]; then
    echo "✅ pubspec.yaml found"
    
    if [ -d "frontend/.dart_tool" ]; then
        echo "✅ Flutter dependencies installed"
    else
        echo "⚠️  Flutter dependencies not installed. Run: cd frontend && flutter pub get"
    fi
else
    echo "❌ frontend/pubspec.yaml not found"
fi

# Summary
echo ""
echo "=========================================="
echo "📋 Summary"
echo "=========================================="
echo ""
echo "To start the backend:"
echo "  cd backend && python3 app.py"
echo ""
echo "To start the frontend:"
echo "  cd frontend && flutter run -d chrome"
echo ""
echo "For detailed instructions, see README.md"
