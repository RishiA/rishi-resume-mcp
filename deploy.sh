#!/bin/bash

echo "🚀 Rishi's Resume MCP Server - Deployment Script"
echo "================================================"
echo ""

# Check if Docker is installed
if command -v docker &> /dev/null; then
    echo "✅ Docker is installed"
    echo ""
    echo "Option 1: Run with Docker (Recommended)"
    echo "----------------------------------------"
    echo "Building Docker image..."
    docker build -t rishi-resume-mcp .
    echo ""
    echo "To run the server:"
    echo "  docker run -p 8000:8000 rishi-resume-mcp"
    echo ""
else
    echo "⚠️  Docker not found. Using Python instead."
fi

# Check Python
if command -v python3 &> /dev/null; then
    echo "✅ Python3 is installed"
    echo ""
    echo "Option 2: Run with Python"
    echo "-------------------------"
    echo "Installing dependencies..."
    pip3 install -r requirements.txt
    echo ""
    echo "To run the server:"
    echo "  python3 server.py"
    echo ""
elif command -v python &> /dev/null; then
    echo "✅ Python is installed"
    echo ""
    echo "Option 2: Run with Python"
    echo "-------------------------"
    echo "Installing dependencies..."
    pip install -r requirements.txt
    echo ""
    echo "To run the server:"
    echo "  python server.py"
    echo ""
else
    echo "❌ Neither Docker nor Python found. Please install one of them."
    exit 1
fi

echo "📝 Sample Questions"
echo "==================="
cat demo/sample_questions.md | head -20
echo ""
echo "... (more questions in demo/sample_questions.md)"
echo ""
echo "🎯 Ready to impress your hiring manager!"