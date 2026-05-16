@echo off
echo Starting SHL Assessment Agent...
echo.

REM Check if virtual environment exists
if not exist venv (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Install dependencies
echo Installing dependencies...
pip install -r requirements.txt

REM Check for .env file
if not exist .env (
    echo WARNING: .env file not found. Please create one from .env.example
    echo Set your GEMINI_API_KEY in the .env file
    pause
    exit /b 1
)

REM Load environment variables
for /f "tokens=1,2 delims==" %%a in (.env) do set %%a=%%b

REM Start the server
echo.
echo Starting FastAPI server on http://localhost:8000
echo Press Ctrl+C to stop
echo.
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
