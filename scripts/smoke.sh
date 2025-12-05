#!/bin/bash
# Smoke test script for resume-ai-builder
# Tests /health, /health/pdf, and /generate-resume endpoints

set -e

BASE_URL="${BASE_URL:-http://localhost:5000}"

echo "🧪 Running smoke tests against $BASE_URL"
echo "============================================"

# Test 1: Health check
echo ""
echo "1️⃣  Testing GET /health..."
HEALTH_RESPONSE=$(curl -s -w "\n%{http_code}" "$BASE_URL/health")
HEALTH_BODY=$(echo "$HEALTH_RESPONSE" | head -n -1)
HEALTH_CODE=$(echo "$HEALTH_RESPONSE" | tail -n 1)

if [ "$HEALTH_CODE" = "200" ]; then
    echo "   ✅ Status: $HEALTH_CODE"
    echo "   Response: $HEALTH_BODY"
else
    echo "   ❌ Status: $HEALTH_CODE (expected 200)"
    echo "   Response: $HEALTH_BODY"
    exit 1
fi

# Test 2: PDF health check
echo ""
echo "2️⃣  Testing GET /health/pdf..."
PDF_HEALTH_RESPONSE=$(curl -s -w "\n%{http_code}" "$BASE_URL/health/pdf")
PDF_HEALTH_BODY=$(echo "$PDF_HEALTH_RESPONSE" | head -n -1)
PDF_HEALTH_CODE=$(echo "$PDF_HEALTH_RESPONSE" | tail -n 1)

if [ "$PDF_HEALTH_CODE" = "200" ]; then
    echo "   ✅ Status: $PDF_HEALTH_CODE"
    echo "   Response: $PDF_HEALTH_BODY"
else
    echo "   ❌ Status: $PDF_HEALTH_CODE (expected 200)"
    echo "   Response: $PDF_HEALTH_BODY"
    exit 1
fi

# Test 3: Generate resume (mock mode)
echo ""
echo "3️⃣  Testing POST /generate-resume (mock mode)..."
RESUME_RESPONSE=$(curl -s -w "\n%{http_code}" -X POST "$BASE_URL/generate-resume" \
    -H "Content-Type: application/json" \
    -d '{
        "name": "Test User",
        "education": "BS Computer Science, Test University, 2023",
        "experience": "Software Developer at Test Corp (2023-present)",
        "skills": "Python, Flask, Testing",
        "template": "chronological"
    }')
RESUME_BODY=$(echo "$RESUME_RESPONSE" | head -n -1)
RESUME_CODE=$(echo "$RESUME_RESPONSE" | tail -n 1)

if [ "$RESUME_CODE" = "200" ]; then
    echo "   ✅ Status: $RESUME_CODE"
    # Check if response contains success:true (with or without space)
    if echo "$RESUME_BODY" | grep -qE '"success":\s*true'; then
        echo "   ✅ Response contains success: true"
    else
        echo "   ⚠️  Response may not indicate success"
    fi
    # Show truncated response
    echo "   Response (truncated): $(echo "$RESUME_BODY" | head -c 200)..."
else
    echo "   ❌ Status: $RESUME_CODE (expected 200)"
    echo "   Response: $RESUME_BODY"
    exit 1
fi

echo ""
echo "============================================"
echo "✅ All smoke tests passed!"
