#!/bin/bash
set -e

echo "=========================================="
echo "  Running SpiceMart Test Automation Suite "
echo "=========================================="

# Ensure virtual environment exists
if [ ! -d ".venv" ]; then
  echo "Virtual environment not found. Initializing..."
  python3 -m venv .venv
  .venv/bin/pip install -r requirements.txt
  .venv/bin/playwright install chromium
fi

# Run Pytest with Playwright
.venv/bin/pytest "$@"

echo "=========================================="
echo "  All Tests Passed! Report generated at:  "
echo "  reports/report.html                     "
echo "=========================================="
