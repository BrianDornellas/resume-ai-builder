#!/bin/bash
# Backend startup script for resume-ai-builder
# Creates venv if missing, installs requirements, and runs Flask

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "🚀 Starting Resume AI Builder Backend..."

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install/update requirements
echo "📥 Installing dependencies..."
pip install -q -r requirements.txt

# Load environment variables if .env exists
if [ -f ".env" ]; then
    echo "🔑 Loading environment variables from .env..."
    set -a
    source .env
    set +a
fi

# Set default FLASK_DEBUG if not set
export FLASK_DEBUG="${FLASK_DEBUG:-True}"

echo "✅ Backend ready! Running on http://localhost:5000"
echo "   Press Ctrl+C to stop"
echo ""

# Run Flask
python app.py
