#!/usr/bin/env bash
set -e

echo "========================================="
echo "CRM Backend Test & CI Script"
echo "========================================="

# Change to backend directory
cd "$(dirname "$0")/.."

echo ""
echo "1. Setting up Python environment..."
if [ ! -d ".venv" ]; then
    echo "   Creating virtual environment..."
    python3 -m venv .venv
fi
source .venv/bin/activate

echo ""
echo "2. Installing dependencies..."
pip install -q -e ".[dev]"

echo ""
echo "3. Running linting checks..."
echo "   - Running ruff check..."
if command -v ruff &> /dev/null; then
    ruff check app tests || echo "   Warning: ruff found issues"
else
    echo "   Skipping ruff (not installed)"
fi

echo ""
echo "4. Running type checks..."
if command -v mypy &> /dev/null; then
    mypy app --ignore-missing-imports || echo "   Warning: mypy found issues"
else
    echo "   Skipping mypy (not installed)"
fi

echo ""
echo "5. Running tests..."
pytest tests/ -v --tb=short

echo ""
echo "========================================="
echo "CI completed successfully!"
echo "========================================="
