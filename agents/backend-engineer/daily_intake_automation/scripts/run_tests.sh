#!/bin/bash
# Test runner for Daily Intake Automation
# Runs all tests and generates a test report

set -e

echo "========================================"
echo "Daily Intake Automation - Test Suite"
echo "========================================"
echo ""

# Change to project directory
cd "$(dirname "$0")/.."

# Check if virtual environment exists, create if not
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv .venv
fi

# Activate virtual environment
source .venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -q -r requirements.txt

echo ""
echo "Running tests..."
echo ""

# Run pytest with coverage and generate report
python -m pytest tests/ -v \
    --tb=short \
    --cov=src \
    --cov-report=term-missing \
    --cov-report=html:htmlcov \
    -o "console_output_style=progress"

TEST_EXIT_CODE=$?

echo ""
echo "========================================"

if [ $TEST_EXIT_CODE -eq 0 ]; then
    echo "✓ All tests passed!"
    echo ""
    echo "Coverage report generated:"
    echo "  - Terminal: Above"
    echo "  - HTML: htmlcov/index.html"
else
    echo "✗ Some tests failed. See above for details."
fi

echo "========================================"

exit $TEST_EXIT_CODE
