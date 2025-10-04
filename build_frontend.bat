@echo off
REM Build script for TruthTrack application (Windows)
echo Building TruthTrack React Frontend...

REM Navigate to client directory
cd client

REM Install dependencies
echo Installing React dependencies...
npm install

REM Build React app for production
echo Building React app...
npm run build

REM Create build directory in Flask app if it doesn't exist
if not exist "..\client\build" mkdir "..\client\build"

echo ✅ React build completed successfully!
echo 🚀 React app is ready for deployment with Flask backend
echo.
echo To run the application:
echo 1. Set up your Firebase credentials in .env file
echo 2. Install Python dependencies: pip install -r requirements.txt
echo 3. Run Flask app: python main.py
pause
