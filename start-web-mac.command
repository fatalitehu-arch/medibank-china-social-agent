#!/bin/bash
# Double-click on a Mac to start the Medibank social agent web app. Needs Python 3.10 or newer.
cd "$(dirname "$0")" || exit 1
PY=""
for c in python3.13 python3.12 python3.11 python3.10 python3; do
  if command -v "$c" >/dev/null 2>&1 && "$c" -c 'import sys; sys.exit(0 if sys.version_info >= (3, 10) else 1)' 2>/dev/null; then
    PY="$c"; break
  fi
done
if [ -z "$PY" ]; then
  echo "Python 3.10 or newer is needed (this Mac's built-in Python is too old)."
  echo "Install Python 3.12 from https://www.python.org/downloads/macos/ and double-click this file again."
  read -r; exit 1
fi
if [ ! -x .venv/bin/python ] || ! .venv/bin/python -c 'import sys; sys.exit(0 if sys.version_info >= (3, 10) else 1)' 2>/dev/null; then
  echo "First run: setting up (about a minute)..."
  rm -rf .venv
  "$PY" -m venv .venv || { echo "Could not create the environment."; read -r; exit 1; }
fi
.venv/bin/python -m pip install -q --upgrade pip
.venv/bin/python -m pip install -q -r requirements.txt || { echo "Installing packages failed. Check the internet connection."; read -r; exit 1; }
.venv/bin/python -m social_agent web
