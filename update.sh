#!/bin/bash

# Update script for paraguay-tax-automation
# This script pulls the latest changes and updates dependencies

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Parse command line arguments
INSTALL_DEV=false
FORCE_PIP=false
for arg in "$@"; do
    case $arg in
        --dev)
            INSTALL_DEV=true
            ;;
        --pip)
            FORCE_PIP=true
            ;;
    esac
done

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

# Detect which environment to use
USE_POETRY=false
if [ "$FORCE_PIP" != "true" ]; then
    # Check what's actually configured for this project
    # venv directory = pip installation, Poetry uses system cache
    if [ ! -d "venv" ] && command -v poetry &> /dev/null; then
        # Only use Poetry if venv doesn't exist (meaning Poetry is the configured tool)
        USE_POETRY=true
    fi
fi

# Auto-detect if dev dependencies are already installed
# This makes update consistent: if dev deps exist, keep them updated
if [ "$INSTALL_DEV" = false ]; then
    if [ "$USE_POETRY" = true ]; then
        # Check if pytest is installed in Poetry environment
        if poetry run python -c "import pytest" 2>/dev/null; then
            INSTALL_DEV=true
        fi
    elif [ -d "venv" ]; then
        # Check if pytest is installed in venv
        if ./venv/bin/python -c "import pytest" 2>/dev/null; then
            INSTALL_DEV=true
        fi
    fi
fi

# Check if Poetry is available (unless --pip flag is used)
if [ "$USE_POETRY" = true ]; then
    echo "Updating dependencies..."
    if [ "$INSTALL_DEV" = true ]; then
        poetry install
        echo "(updated: main + dev dependencies)"
    else
        poetry install --only main
        echo "(updated: main dependencies only)"
    fi
elif [ -d "venv" ]; then
    echo "Updating dependencies..."
    ./venv/bin/pip install --upgrade pip -q
    ./venv/bin/pip install -r requirements.txt -q
    if [ "$INSTALL_DEV" = true ]; then
        ./venv/bin/pip install -r requirements-dev.txt -q
        echo "(updated: main + dev dependencies)"
    else
        echo "(updated: main dependencies only)"
    fi
else
    echo "ERROR: No environment found."
    echo "Please run ./install.sh first to create the initial setup."
    exit 1
fi

echo ""
echo "=== Update complete ==="
echo ""
