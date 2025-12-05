#!/bin/bash
# Frontend startup script for resume-ai-builder
# Runs Flutter web on Chrome with proper web-port

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "🚀 Starting Resume AI Builder Frontend..."

# Check if Flutter is installed
if ! command -v flutter &> /dev/null; then
    echo "❌ Flutter is not installed or not in PATH"
    echo "   Please install Flutter: https://docs.flutter.dev/get-started/install"
    exit 1
fi

# Run flutter doctor to verify setup
echo "🔍 Checking Flutter installation..."
flutter doctor -v | head -20

# Get dependencies
echo "📥 Getting Flutter dependencies..."
flutter pub get

# Run on Chrome with specific web port
echo "✅ Frontend ready! Launching on http://localhost:8080"
echo "   Press 'q' to quit"
echo ""

flutter run -d chrome --web-port=8080
