@echo off
REM =========================================
REM SETTINGS
REM =========================================
set "USE_IP_BASE=FALSE"
set "IP_BASE=10.201.52"

set "SSH_USER=CHANGEME"
set "SSH_PASSWORD=CHANGEME"

set "SSH_LOCAL_PORT=10060"
set "SSH_REMOTE_PORT=5900"
set "VNC_PORT=5900"
set "SSH_TIMEOUT=3"
set "CLEANUP_TIMEOUT=2"

set "PUTTY_PATH=C:\Program Files\PuTTY"
set "VNC_PATH=C:\Program Files\TigerVNC"

REM Alternative VNC viewers (using vncviewer.exe):
REM UltraVNC: C:\Program Files\uvnc bvba\UltraVNC
REM RealVNC: C:\Program Files\RealVNC\VNC Viewer

setlocal enabledelayedexpansion

echo =========================================
echo   Engel CC300 Remote View
echo   Author: Jorge Santos (JorgeS15)
echo   Version: 1.9 (07/10/2025)
echo.
echo   github.com/JorgeS15/cc300remoteview
echo =========================================
echo.

REM Check if should use base IP or complete IP
if /i "!USE_IP_BASE!"=="TRUE" (
    goto input_octet
) else (
    goto input_complete_ip
)

REM Request complete IP
:input_complete_ip
set "ip_address="
set /p ip_address="Enter the complete machine IP address: "

REM Validate if input is not empty
if "!ip_address!"=="" (
    echo Error: The IPv4 address cannot be empty.
    echo.
    goto input_complete_ip
)

REM Split IP into octets and validate
for /f "tokens=1,2,3,4 delims=." %%a in ("!ip_address!") do (
    set octet1=%%a
    set octet2=%%b
    set octet3=%%c
    set octet4=%%d
)

REM Check if all octets were parsed
if "!octet1!"=="" goto invalid_format
if "!octet2!"=="" goto invalid_format
if "!octet3!"=="" goto invalid_format
if "!octet4!"=="" goto invalid_format

REM Validate octet ranges (0-255)
if !octet1! GTR 255 goto invalid_range
if !octet2! GTR 255 goto invalid_range
if !octet3! GTR 255 goto invalid_range
if !octet4! GTR 255 goto invalid_range

goto ask_ssh

REM Request last octet of IPv4
:input_octet
set "last_octet="
set /p last_octet="Enter the machine IP %IP_BASE%."

REM Validate if input is not empty
if "!last_octet!"=="" (
    echo Error: The octet cannot be empty.
    echo.
    goto input_octet
)

REM Validate if it's a number
set "valid=1"
for /f "delims=0123456789" %%i in ("!last_octet!") do set "valid=0"
if !valid! EQU 0 (
    echo Error: The octet must be a number.
    echo.
    goto input_octet
)

REM Validate range (0-255)
if !last_octet! GTR 255 (
    echo Error: The octet must be between 0 and 255.
    echo.
    goto input_octet
)

if !last_octet! LSS 0 (
    echo Error: The octet must be between 0 and 255.
    echo.
    goto input_octet
)

REM Build complete IP
set "ip_address=%IP_BASE%.!last_octet!"

REM Ask if SSH tunnel is necessary
:ask_ssh
set "ssh_choice="
set /p ssh_choice="Is it necessary to establish an SSH tunnel? (Y/N): "

if /i "!ssh_choice!"=="Y" goto with_ssh
if /i "!ssh_choice!"=="N" goto without_ssh

echo Invalid option. Please choose Y or N.
echo.
goto ask_ssh

REM Direct connection without SSH
:without_ssh
echo.
echo Establishing direct VNC connection...
echo.
cd "%VNC_PATH%"
if errorlevel 1 (
    echo Error: Unable to access VNC Viewer directory.
    echo Path: %VNC_PATH%
    pause
    exit /b 1
)
vncviewer.exe !ip_address!:%VNC_PORT%
goto end

REM Connection with SSH tunnel
:with_ssh
echo.
echo Establishing SSH tunnel... (port: %SSH_LOCAL_PORT%)
echo.

REM Create a temporary script for SSH tunnel
set "temp_script=%TEMP%\ssh_tunnel_%RANDOM%.bat"
echo @echo off > "!temp_script!"
echo cd "%PUTTY_PATH%" >> "!temp_script!"
echo ^(echo y^) ^| plink.exe -N -pw %SSH_PASSWORD% %SSH_USER%@!ip_address! -L %SSH_LOCAL_PORT%:localhost:%SSH_REMOTE_PORT% >> "!temp_script!"

REM Start SSH tunnel in background that closes automatically
start "SSH Tunnel" /MIN cmd /c "!temp_script!"

REM Wait a few seconds for tunnel to establish
echo Waiting for SSH tunnel establishment (%SSH_TIMEOUT% seconds)...
timeout /t %SSH_TIMEOUT% /nobreak >nul

echo.
echo Opening VNC Viewer through tunnel...
echo.
cd "%VNC_PATH%"
if errorlevel 1 (
    echo Error: Unable to access VNC Viewer directory.
    echo Path: %VNC_PATH%
    pause
    exit /b 1
)
vncviewer.exe localhost:%SSH_LOCAL_PORT%

REM Wait a moment before cleaning up SSH process
timeout /t %CLEANUP_TIMEOUT% /nobreak >nul

REM Terminate plink process automatically
taskkill /F /IM plink.exe >nul 2>&1

REM Clean up temporary file
if exist "!temp_script!" del "!temp_script!" >nul 2>&1

echo.
echo SSH tunnel closed automatically.

goto end

REM Error handling for validation
:invalid_format
echo.
echo Error: Invalid IP address. Correct format: xxx.xxx.xxx.xxx
echo.
goto input_complete_ip

:invalid_range
echo.
echo Error: Invalid IP address. Octets must be between 0-255.
echo.
goto input_complete_ip

:end
echo.
echo Script completed.
endlocal
exit /b 0