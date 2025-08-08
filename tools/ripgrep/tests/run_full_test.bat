@echo off
REM Comprehensive QA Test Runner for Windows
REM Runs complete test suite in 30-60 minutes

echo ============================================
echo Ripgrep Plugin Comprehensive QA Test Suite
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

REM Check if ripgrep is available
rg --version >nul 2>&1
if errorlevel 1 (
    echo WARNING: ripgrep not found in PATH
    echo Some tests may fail. Install ripgrep for complete testing.
    echo.
    echo Continue anyway? (Y/N)
    set /p choice=
    if /i not "%choice%"=="Y" (
        echo Test cancelled by user
        pause
        exit /b 1
    )
)

REM Create results directory
if not exist "results" mkdir results

REM Run comprehensive test suite
echo Running comprehensive QA test suite...
echo This may take 30-60 minutes depending on your system.
echo.
python run_qa_suite.py full --verbose --save-results --output-dir results

REM Check results and provide guidance
if errorlevel 2 (
    echo.
    echo =========================================
    echo CRITICAL ISSUES DETECTED
    echo =========================================
    echo The plugin has serious issues that must be resolved
    echo before deployment. Review the detailed test output
    echo and fix all critical issues.
    echo.
    echo Check results/ directory for detailed reports.
    echo.
) else if errorlevel 1 (
    echo.
    echo =========================================
    echo SOME ISSUES DETECTED
    echo =========================================
    echo The plugin has some issues that should be addressed.
    echo Review the test output and consider fixing issues
    echo before production deployment.
    echo.
    echo Check results/ directory for detailed reports.
    echo.
) else (
    echo.
    echo =========================================
    echo ALL TESTS PASSED
    echo =========================================
    echo Congratulations! The plugin passes all quality checks
    echo and is ready for production deployment.
    echo.
    echo Check results/ directory for detailed reports.
    echo.
)

pause
exit /b %errorlevel%