@echo off
echo 🚀 Setting up FPL Player Combination Web App...
echo ================================================

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python is not installed. Please install Python first.
    echo    You can download it from: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo ✅ Python found

REM Check if we're in the webapp directory
if not exist app.py (
    echo ❌ Please run this script from the webapp directory
    pause
    exit /b 1
)

REM Install requirements
echo 📦 Installing required packages...
pip install -r requirements.txt

if %errorlevel% equ 0 (
    echo ✅ Packages installed successfully
) else (
    echo ❌ Failed to install packages. Trying with user install...
    pip install --user -r requirements.txt
)

echo.
echo 🎉 Setup complete!
echo.
echo To start the web app:
echo 1. Run: python app.py
echo 2. Open your web browser and go to: http://localhost:5001
echo 3. Press Ctrl+C in the terminal to stop the server
echo.
echo 📱 The web app will be accessible to anyone on your local network
echo 🔄 Your existing cache files will be used automatically
echo.
pause
