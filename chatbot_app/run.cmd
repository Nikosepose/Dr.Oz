@echo off
setlocal
rem Run from this directory even when launched from Explorer or another folder.
pushd "%~dp0" || exit /b 1

set "CHATBOT_PYTHON="
set "CHATBOT_PYTHON_ARGS="
call :try_python "%~dp0.venv\Scripts\python.exe"
if not defined CHATBOT_PYTHON call :try_python "%~dp0..\.venv\Scripts\python.exe"
if not defined CHATBOT_PYTHON call :try_python "py" "-3"
if not defined CHATBOT_PYTHON call :try_python "python"
if not defined CHATBOT_PYTHON call :try_python "python3"
if not defined CHATBOT_PYTHON call :try_python "%USERPROFILE%\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe"

if not defined CHATBOT_PYTHON (
    echo Python 3.10 or later with Tkinter could not be found.
    echo Install Python with its Tcl/Tk component, then try again.
    popd
    exit /b 1
)

echo Using Python: %CHATBOT_PYTHON% %CHATBOT_PYTHON_ARGS%
if "%~1"=="" goto run_app
if /i "%~1"=="test" goto run_tests
echo Usage: run.cmd [test]
set "CHATBOT_EXIT_CODE=2"
goto finish

:run_app
"%CHATBOT_PYTHON%" %CHATBOT_PYTHON_ARGS% main.py
set "CHATBOT_EXIT_CODE=%ERRORLEVEL%"
goto finish

:run_tests
"%CHATBOT_PYTHON%" %CHATBOT_PYTHON_ARGS% -m unittest discover -s tests -v
set "CHATBOT_EXIT_CODE=%ERRORLEVEL%"
goto finish

:finish
popd
exit /b %CHATBOT_EXIT_CODE%

:try_python
rem Ignore missing executables and Store aliases; require our minimum runtime.
"%~1" %~2 -c "import sys, tkinter; sys.exit(sys.version_info < (3, 10))" >nul 2>&1
if errorlevel 1 exit /b 0
set "CHATBOT_PYTHON=%~1"
set "CHATBOT_PYTHON_ARGS=%~2"
exit /b 0
