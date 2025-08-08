@echo off
REM Quick QA Test Runner for Windows
REM Runs essential tests in 5-10 minutes

echo ============================================
echo Ripgrep Plugin Quick QA Test Suite
echo ============================================

cd /d "%~dp0"

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found in PATH
    echo Please install Python 3.7+ and add to PATH
    pause
    exit /b 1
)

REM Run quick test suite
echo Running quick validation tests...
python run_qa_suite.py quick --verbose --save-results

if errorlevel 2 (
    echo.
    echo CRITICAL ISSUES DETECTED - Review test output
    echo.
    pause
    exit /b 2
) else if errorlevel 1 (
    echo.
    echo SOME ISSUES DETECTED - Review and fix if needed
    echo.
    pause
    exit /b 1
) else (
    echo.
    echo ALL TESTS PASSED - Plugin ready for further testing
    echo.
    pause
    exit /b 0
)