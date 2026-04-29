@echo off
set PYTHONNOUSERSITE=1
echo Starting LacriMetric Diagnostics...

IF NOT EXIST venv (
    echo Creating an isolated Virtual Environment to fix dependency conflicts...
    python -m venv venv
)

echo Activating virtual environment and installing dependencies...
call venv\Scripts\pip install -r requirements.txt

echo.
echo Starting the Flask Web Server on http://127.0.0.1:5000
call venv\Scripts\python app.py

pause
