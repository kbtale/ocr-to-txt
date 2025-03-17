@echo off
echo Installing dependencies for OCR to TXT Converter...

REM Install Python dependencies
pip install -r requirements.txt

echo.
echo Python dependencies installed successfully!
echo.
echo IMPORTANT: You need to manually install Tesseract OCR:
echo.
echo 1. Download Tesseract OCR from:
echo    https://github.com/UB-Mannheim/tesseract/releases/download/v5.3.1.20230401/tesseract-ocr-w64-setup-5.3.1.20230401.exe
echo.
echo 2. Run the installer and use the default installation path (C:\Program Files\Tesseract-OCR\)
echo.
echo 3. After installation, you can run the application using run.bat
echo.
echo Press any key to open the download page in your browser...
pause > nul
start "" "https://github.com/UB-Mannheim/tesseract/releases/tag/v5.3.1.20230401"
echo.
pause
