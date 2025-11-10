#!/bin/bash

# Week 3 - Resume Templates Verification Script
# Verifies that the template system is working correctly

set -e

echo "╔═══════════════════════════════════════════════════════════════╗"
echo "║  Week 3 - Resume Templates Verification                      ║"
echo "╚═══════════════════════════════════════════════════════════════╝"
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if backend is running
echo "Checking if backend is running..."
if curl -s http://localhost:5000/health > /dev/null 2>&1; then
    echo -e "${GREEN}✓${NC} Backend is running"
else
    echo -e "${RED}✗${NC} Backend is not running"
    echo "Please start the backend with: cd backend && python app.py"
    exit 1
fi

echo ""
echo "Running verification tests..."
echo ""

# Test 1: Backend tests
echo "1. Running backend unit tests..."
cd backend
if python test_app.py > /dev/null 2>&1; then
    echo -e "${GREEN}✓${NC} All 6 backend tests passing"
else
    echo -e "${RED}✗${NC} Backend tests failed"
    exit 1
fi

# Test 2: Chronological template
echo "2. Testing chronological template..."
RESULT=$(curl -s -X POST http://localhost:5000/generate-resume \
  -H "Content-Type: application/json" \
  -d '{"name":"Test User","education":"Test Edu","experience":"Test Exp","skills":"Test Skills","template":"chronological"}')

if echo "$RESULT" | grep -q '"template":"chronological"' && echo "$RESULT" | grep -q '"success":true'; then
    echo -e "${GREEN}✓${NC} Chronological template working"
else
    echo -e "${RED}✗${NC} Chronological template failed"
    exit 1
fi

# Test 3: Functional template
echo "3. Testing functional template..."
RESULT=$(curl -s -X POST http://localhost:5000/generate-resume \
  -H "Content-Type: application/json" \
  -d '{"name":"Test User","education":"Test Edu","experience":"Test Exp","skills":"Test Skills","template":"functional"}')

if echo "$RESULT" | grep -q '"template":"functional"' && echo "$RESULT" | grep -q '"success":true'; then
    echo -e "${GREEN}✓${NC} Functional template working"
else
    echo -e "${RED}✗${NC} Functional template failed"
    exit 1
fi

# Test 4: Default template
echo "4. Testing default template (chronological)..."
RESULT=$(curl -s -X POST http://localhost:5000/generate-resume \
  -H "Content-Type: application/json" \
  -d '{"name":"Test User","education":"Test Edu","experience":"Test Exp","skills":"Test Skills"}')

if echo "$RESULT" | grep -q '"template":"chronological"' && echo "$RESULT" | grep -q '"success":true'; then
    echo -e "${GREEN}✓${NC} Default template working (defaults to chronological)"
else
    echo -e "${RED}✗${NC} Default template failed"
    exit 1
fi

# Test 5: Markdown formatting
echo "5. Testing Markdown formatting..."
RESULT=$(curl -s -X POST http://localhost:5000/generate-resume \
  -H "Content-Type: application/json" \
  -d '{"name":"Test User","education":"Test Edu","experience":"Test Exp","skills":"Test Skills","template":"chronological"}')

if echo "$RESULT" | grep -q '# Test User' && echo "$RESULT" | grep -q '##'; then
    echo -e "${GREEN}✓${NC} Markdown formatting present"
else
    echo -e "${RED}✗${NC} Markdown formatting missing"
    exit 1
fi

# Test 6: File existence
echo "6. Checking file structure..."
cd ..
FILES=("backend/templates.py" "backend/test_app.py" "backend/demo_templates.py" 
       "frontend/lib/services/api_service.dart" "frontend/lib/screens/resume_form_screen.dart"
       "WEEK3_SUMMARY.md" "README.md" "ARCHITECTURE.md")

for file in "${FILES[@]}"; do
    if [ -f "$file" ]; then
        echo -e "   ${GREEN}✓${NC} $file exists"
    else
        echo -e "   ${RED}✗${NC} $file missing"
        exit 1
    fi
done

# Summary
echo ""
echo "╔═══════════════════════════════════════════════════════════════╗"
echo "║  Week 3 Verification Complete                                 ║"
echo "╚═══════════════════════════════════════════════════════════════╝"
echo ""
echo -e "${GREEN}✓${NC} All verification tests passed!"
echo ""
echo "Features verified:"
echo "  • Backend template system working"
echo "  • Chronological template functional"
echo "  • Functional template functional"
echo "  • Default template behavior correct"
echo "  • Markdown formatting applied"
echo "  • All required files present"
echo ""
echo "Week 3 implementation is complete and verified!"
echo ""
