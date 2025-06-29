@echo off
echo ========================================
echo   RAG SQL Agent - Windows Setup
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://python.org
    pause
    exit /b 1
)

echo ✅ Python detected
echo.

REM Run the setup script
echo 🚀 Running setup script...
python setup.py

echo.
echo Setup complete! 
echo.
echo Quick commands:
echo   - Console interface: python main.py
echo   - Web interface: streamlit run ui/streamlit_app.py
echo   - Initialize schema: python scripts/initialize_schema.py
echo.
pause
