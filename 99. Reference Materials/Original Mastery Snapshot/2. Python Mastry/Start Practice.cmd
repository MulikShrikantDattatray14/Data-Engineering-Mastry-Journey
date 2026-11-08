@echo off
cd /d "%~dp0"
if exist "%LOCALAPPDATA%\Programs\Python\Python314\python.exe" (
    "%LOCALAPPDATA%\Programs\Python\Python314\python.exe" "%~dp0practice_runner.py"
) else (
    py "%~dp0practice_runner.py"
)
if errorlevel 1 pause
