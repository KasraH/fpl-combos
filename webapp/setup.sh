#!/bin/bash

# FPL Player Combination Web App Setup Script
# This script sets up and runs the web application

echo "🚀 Setting up FPL Player Combination Web App..."
echo "================================================"

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3 first."
    echo "   You can download it from: https://www.python.org/downloads/"
    exit 1
fi

echo "✅ Python 3 found"

# Check if we're in the webapp directory
if [ ! -f "app.py" ]; then
    echo "❌ Please run this script from the webapp directory"
    exit 1
fi

# Install requirements
echo "📦 Installing required packages..."
pip3 install -r requirements.txt

if [ $? -eq 0 ]; then
    echo "✅ Packages installed successfully"
else
    echo "❌ Failed to install packages. Trying with user install..."
    pip3 install --user -r requirements.txt
fi

echo ""
echo "🎉 Setup complete!"
echo ""
echo "To start the web app:"
echo "1. Run: python3 app.py"
echo "2. Open your web browser and go to: http://localhost:5001"
echo "3. Press Ctrl+C in this terminal to stop the server"
echo ""
echo "📱 The web app will be accessible to anyone on your local network"
echo "🔄 Your existing cache files will be used automatically"
