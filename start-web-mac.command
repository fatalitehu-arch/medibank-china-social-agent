#!/bin/bash
# Double-click on a Mac to start the Medibank social agent web app.
cd "$(dirname "$0")" || exit 1
if [ ! -d .venv ]; then
  echo "First run: setting up (about a minute)..."
  python3 -m venv .venv || { echo "Python 3 is needed: https://www.python.org/downloads/"; read -r; exit 1; }
fi
source .venv/bin/activate
pip install -q -r requirements.txt
python -m social_agent web
