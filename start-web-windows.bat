@echo off
REM Double-click on Windows to start the Medibank social agent web app.
cd /d "%~dp0"
if not exist .venv (
  echo First run: setting up, about a minute...
  py -3 -m venv .venv || (echo Python 3 is needed: https://www.python.org/downloads/ & pause & exit /b 1)
)
call .venv\Scripts\activate.bat
pip install -q -r requirements.txt
python -m social_agent web
pause
