#!/bin/bash

# Update script for paraguay-tax-automation
# This script pulls the latest changes and updates dependencies

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "=== Paraguay Tax Automation - Update ==="
echo ""

# Pull latest changes from git
echo "Pulling latest changes from git..."
git pull

echo ""

# Check Python version
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is required but not found."
    echo "Please install Python 3.8 or higher."
    exit 1
fi

# Check if Poetry is available
if command -v poetry &> /dev/null; then
    echo "Updating dependencies..."
    poetry install
elif [ -d "venv" ]; then
    echo "Updating dependencies..."
    ./venv/bin/pip install --upgrade pip -q
    ./venv/bin/pip install -r requirements.txt -q
else
    echo "ERROR: No environment found."
    echo "Please run ./install.sh first to create the initial setup."
    exit 1
fi

echo ""
echo "=== Update complete ==="
echo ""
