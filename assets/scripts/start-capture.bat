@echo off
setlocal enableextensions

REM ============================================================
REM  start-capture.bat
REM  - Ensures mitmproxy's CA exists and is trusted (CurrentUser
REM    Root store, no admin needed).
REM  - Launches mitmdump on port 8081, writing to a .flow path.
REM
REM  Usage:
REM    start-capture.bat                          (default flow path)
REM    start-capture.bat output\captures\foo.flow (indicated path)
REM
REM  Output goes under <repo>\output\captures\ regardless of where this
REM  script is launched from (paths are anchored to the script location).
REM ============================================================

set "PORT=8081"
set "CERT=%USERPROFILE%\.mitmproxy\mitmproxy-ca-cert.cer"

REM ---- Repo root = two levels up from this script (assets\scripts\) ----
set "REPO_ROOT=%~dp0..\.."

REM ---- Output flow path: arg 1, or a sensible default ----
if "%~1"=="" (
    set "FLOW=%REPO_ROOT%\output\captures\capture.flow"
) else (
    set "FLOW=%~1"
)

REM ---- Make sure the target directory exists ----
for %%F in ("%FLOW%") do set "FLOWDIR=%%~dpF"
if not exist "%FLOWDIR%" mkdir "%FLOWDIR%"

REM ---- Generate the CA the first time (mitmdump creates it on start) ----
if not exist "%CERT%" (
    echo [*] mitmproxy CA not found - generating it...
    start "mitm-gen" /min mitmdump --listen-port %PORT%
    timeout /t 3 /nobreak >nul
    taskkill /im mitmdump.exe /f >nul 2>&1
)

REM ---- Trust the CA only if it isn't already in the store ----
REM  Do NOT test certutil's own errorlevel: it returns 0 when the cert is
REM  present but a large NEGATIVE HRESULT (e.g. -2146893807) when missing,
REM  and "if errorlevel 1" (exit code >= 1) is false for both - so it could
REM  never take the "add" path. Pipe through findstr, which yields a clean
REM  0 (found) / 1 (not found).
certutil -user -store Root mitmproxy 2>nul | findstr /i "mitmproxy" >nul
if errorlevel 1 (
    echo [*] Adding mitmproxy CA to CurrentUser Root store...
    certutil -user -addstore -f Root "%CERT%"
) else (
    echo [*] mitmproxy CA already trusted.
)

REM ---- Capture (Ctrl+C to stop) ----
echo.
echo [*] Capturing to "%FLOW%" on 127.0.0.1:%PORT%
echo [*] Press Ctrl+C to stop.
echo.
mitmdump --listen-port %PORT% -w "%FLOW%"

endlocal
