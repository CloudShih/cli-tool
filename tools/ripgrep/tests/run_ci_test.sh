#!/bin/bash
# Continuous Integration Test Runner for Unix-like systems
# Designed for automated CI/CD pipelines

set -e  # Exit on any error

echo "============================================"
echo "Ripgrep Plugin CI/CD QA Test Suite"
echo "============================================"

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Check Python version
if ! command -v python3 &> /dev/null; then
    echo "ERROR: python3 not found"
    echo "Please install Python 3.7+ for CI testing"
    exit 1
fi

PYTHON_VERSION=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
echo "Using Python $PYTHON_VERSION"

# Check if ripgrep is available
if ! command -v rg &> /dev/null; then
    echo "WARNING: ripgrep not found in PATH"
    echo "Installing ripgrep is recommended for complete testing"
    
    # Attempt to install ripgrep based on system
    if command -v apt-get &> /dev/null; then
        echo "Attempting to install ripgrep via apt..."
        sudo apt-get update && sudo apt-get install -y ripgrep
    elif command -v yum &> /dev/null; then
        echo "Attempting to install ripgrep via yum..."
        sudo yum install -y ripgrep
    elif command -v brew &> /dev/null; then
        echo "Attempting to install ripgrep via homebrew..."
        brew install ripgrep
    else
        echo "Could not auto-install ripgrep. Some tests may fail."
    fi
fi

# Create results directory
mkdir -p results

# Set environment variables for CI
export CI=true
export PYTHONPATH="${SCRIPT_DIR}/../../../:${PYTHONPATH}"

# Run CI test suite with timeout
echo "Running CI test suite..."
echo "Maximum execution time: 15 minutes"

# Use timeout command if available
if command -v timeout &> /dev/null; then
    timeout 900 python3 run_qa_suite.py ci --verbose --save-results --output-dir results
    EXIT_CODE=$?
    
    if [ $EXIT_CODE -eq 124 ]; then
        echo "ERROR: Test suite timed out after 15 minutes"
        exit 124
    fi
else
    # Fallback without timeout
    python3 run_qa_suite.py ci --verbose --save-results --output-dir results
    EXIT_CODE=$?
fi

# Generate CI-specific output
echo ""
echo "============================================"
echo "CI TEST RESULTS SUMMARY"
echo "============================================"

case $EXIT_CODE in
    0)
        echo "✅ CI TESTS PASSED"
        echo "Status: READY FOR DEPLOYMENT"
        echo "All critical tests passed successfully."
        ;;
    1)
        echo "⚠️  CI TESTS PASSED WITH WARNINGS"
        echo "Status: CONDITIONAL DEPLOYMENT"
        echo "Some non-critical tests failed. Review and consider fixes."
        ;;
    2)
        echo "❌ CI TESTS FAILED"
        echo "Status: DEPLOYMENT BLOCKED"
        echo "Critical tests failed. Must fix before deployment."
        ;;
    3)
        echo "⚠️  CI TESTS INTERRUPTED"
        echo "Status: UNKNOWN"
        echo "Tests were interrupted by user or system."
        ;;
    *)
        echo "💥 CI TEST RUNNER ERROR"
        echo "Status: RUNNER FAILURE"
        echo "Test runner encountered an error."
        ;;
esac

# Save exit code for CI systems
echo "Exit Code: $EXIT_CODE"

# Output key metrics for CI dashboards
if [ -f "results/qa_results_ci_"*.json ]; then
    LATEST_RESULT=$(ls -t results/qa_results_ci_*.json | head -n1)
    echo "Latest Results File: $LATEST_RESULT"
    
    # Extract key metrics using Python if available
    if command -v python3 &> /dev/null; then
        python3 -c "
import json, sys
try:
    with open('$LATEST_RESULT', 'r') as f:
        data = json.load(f)
    summary = data.get('test_summary', {})
    print(f\"Tests Run: {summary.get('total_tests', 'N/A')}\")
    print(f\"Success Rate: {summary.get('success_rate', 'N/A'):.1f}%\")
    print(f\"Execution Time: {data.get('total_execution_time', 'N/A'):.1f}s\")
except Exception as e:
    print(f'Could not parse results: {e}')
"
    fi
fi

echo "============================================"

exit $EXIT_CODE