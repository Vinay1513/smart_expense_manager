@echo off
setlocal enabledelayedexpansion

echo 🚀 Setting up Smart Expense Manager...

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed. Please install Python 3.8+ and try again.
    pause
    exit /b 1
)

REM Check if Node.js is installed
node --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Node.js is not installed. Please install Node.js 16+ and try again.
    pause
    exit /b 1
)

REM Check if npm is installed
npm --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] npm is not installed. Please install npm and try again.
    pause
    exit /b 1
)

echo [INFO] Checking system requirements...
echo [SUCCESS] All system requirements met!

REM Backend Setup
echo [INFO] Setting up Django backend...

cd backend

REM Create virtual environment
if not exist "venv" (
    echo [INFO] Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo [INFO] Activating virtual environment...
call venv\Scripts\activate.bat

REM Install Python dependencies
echo [INFO] Installing Python dependencies...
pip install -r requirements.txt

REM Create .env file if it doesn't exist
if not exist ".env" (
    echo [INFO] Creating .env file...
    copy env.example .env
    echo [WARNING] Please update the .env file with your configuration.
)

REM Run Django migrations
echo [INFO] Running Django migrations...
python manage.py makemigrations
python manage.py migrate

REM Create default categories and superuser
echo [INFO] Setting up default data...
python setup.py

echo [SUCCESS] Backend setup completed!

REM Frontend Setup
echo [INFO] Setting up React frontend...

cd ..\frontend

REM Install Node.js dependencies
echo [INFO] Installing Node.js dependencies...
npm install

REM Create .env file if it doesn't exist
if not exist ".env" (
    echo [INFO] Creating .env file...
    copy env.example .env
)

echo [SUCCESS] Frontend setup completed!

REM Return to root directory
cd ..

echo [SUCCESS] 🎉 Setup completed successfully!
echo.
echo 📋 Next steps:
echo 1. Start the Django backend:
echo    cd backend
echo    venv\Scripts\activate
echo    python manage.py runserver
echo.
echo 2. Start the React frontend (in a new terminal):
echo    cd frontend
echo    npm start
echo.
echo 3. Open your browser and navigate to:
echo    Frontend: http://localhost:3000
echo    Backend API: http://localhost:8000/api
echo    Django Admin: http://localhost:8000/admin
echo.
echo 📚 Documentation:
echo    - Backend API docs: http://localhost:8000/api/
echo    - Read the README.md file for more information
echo.
echo [WARNING] Remember to update the .env files with your specific configuration!
pause 