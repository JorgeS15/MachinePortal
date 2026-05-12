@echo off
setlocal

echo ============================================
echo  Machine Portal - Build Script
echo ============================================
echo.

REM Check Python is available
where python >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found. Install Python 3.11+ and add it to PATH.
    pause
    exit /b 1
)

REM Check required asset files exist
if not exist "dashboard\assets\plink.exe" (
    echo ERROR: assets\plink.exe is missing.
    echo Download plink.exe from: https://www.chiark.greenend.org.uk/~sgtatham/putty/latest.html
    pause
    exit /b 1
)
if not exist "dashboard\assets\vncviewer.exe" (
    echo ERROR: assets\vncviewer.exe is missing.
    echo Download the portable TigerVNC viewer from: https://github.com/TigerVNC/tigervnc/releases
    echo Look for: vncviewer64-X.Y.Z.exe  -^> rename to vncviewer.exe
    pause
    exit /b 1
)

REM Install/upgrade PyInstaller and required packages
echo Installing dependencies...
python -m pip install --upgrade pyinstaller PyNaCl >nul 2>&1

REM Build
echo Building MachinePortal.exe ...
cd dashboard
python -m PyInstaller machineportal.spec --distpath ..\dist --workpath ..\build --noconfirm --clean
cd ..

if errorlevel 1 (
    echo.
    echo BUILD FAILED. Check the output above for errors.
    pause
    exit /b 1
)

echo.
echo ============================================
echo  BUILD COMPLETE
echo  Output: dist\MachinePortal.exe
echo ============================================
pause
