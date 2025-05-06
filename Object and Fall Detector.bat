@echo off
REM Set the directory where your app is located
set APP_PATH=C:\Users\KIIT\Desktop\Minor_Project_final\Object and Fall Detection

REM Change to that directory
cd /d "%C:\Users\KIIT\Desktop\Minor_Project_final\Object and Fall Detection%"

REM Run your command (example: Python server or Node.js app)
REM Replace the below line with your actual command
start cmd /k "python app.py"

REM Wait a moment for the server to start
timeout /t 3 >nul

REM Open the localhost link in the default browser
start http://localhost:5000
