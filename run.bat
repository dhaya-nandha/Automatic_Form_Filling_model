@echo off
title FormFill AI Platform
echo ========================================================
echo Starting FormFill AI Web Application & FastAPI Server...
echo ========================================================
echo.
echo Verifying Python environment dependencies...
python -m pip install -r requirements.txt --quiet
echo.
python main.py
pause
