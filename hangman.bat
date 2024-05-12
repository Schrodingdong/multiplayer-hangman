@echo off

REM Prompt the user to select between two choices
set /p choice="Select an option (1 or 2): 1. Host 2. Player ?> "

REM Validate the user input
if "%choice%"=="1" (
    REM start ngrok in a new terminal window
    start cmd.exe /c ngrok http 8000
)

REM Install pip dependencies
pip install -r .\requirements.txt

REM start application
python .\python_impl\src\main.py

