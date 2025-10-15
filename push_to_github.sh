#!/bin/bash

echo "🚀 Pushing to GitHub..."
echo ""

# Check if remote exists
if git remote | grep -q "origin"; then
    echo "✅ Remote 'origin' already configured"
else
    echo "Adding GitHub remote..."
    git remote add origin https://github.com/rishia/rishi-resume-mcp.git
fi

# Push to GitHub
echo "Pushing code to GitHub..."
git push -u origin main

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Successfully pushed to GitHub!"
    echo ""
    echo "🔗 Your repository is now live at:"
    echo "   https://github.com/rishia/rishi-resume-mcp"
    echo ""
    echo "📧 Share with hiring manager:"
    echo "   'I built an interactive AI-powered resume server to demonstrate"
    echo "   my technical depth and product thinking for the AI PM role.'"
    echo ""
    echo "🎯 Next steps:"
    echo "   1. Star the repo for visibility"
    echo "   2. Consider adding a demo GIF to the README"
    echo "   3. Deploy to Replit for one-click access"
else
    echo ""
    echo "❌ Push failed. Please ensure:"
    echo "   1. You've created the repo at https://github.com/new"
    echo "   2. Repository name: rishi-resume-mcp"
    echo "   3. Set to Public"
    echo "   4. Didn't initialize with README"
    echo ""
    echo "Then run this script again."
fi