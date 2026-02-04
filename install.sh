#!/bin/bash

# Installation script for paraguay-tax-automation
# This script installs Python dependencies using Poetry or pip

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "=== Paraguay Tax Automation - Installation ==="
echo ""

# Check Python version
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
    echo "Found Python $PYTHON_VERSION"
else
    echo "ERROR: Python 3 is required but not found."
    echo "Please install Python 3.8 or higher."
    exit 1
fi

# Create .env from example if it doesn't exist
if [ ! -f ".env" ]; then
    if [ -f ".env.example" ]; then
        cp .env.example .env
        echo "Created .env from .env.example"
        echo "IMPORTANT: Edit .env and add your credentials!"
    fi
fi

# Check if Poetry is available
if command -v poetry &> /dev/null; then
    echo "Found Poetry, installing dependencies..."
    poetry install
    echo ""
    echo "=== Installation complete ==="
    echo ""
    echo "Run with:"
    echo "  cd $SCRIPT_DIR && poetry run python file_taxes.py"
    echo ""
    echo "Or activate the environment:"
    echo "  cd $SCRIPT_DIR && poetry shell"
    echo "  python file_taxes.py"
else
    echo "Poetry not found, using pip with virtual environment..."

    # Create virtual environment
    if [ ! -d "venv" ]; then
        echo "Creating virtual environment..."
        python3 -m venv venv
    fi

    # Activate and install
    echo "Installing dependencies..."
    ./venv/bin/pip install --upgrade pip -q
    ./venv/bin/pip install -r requirements.txt -q

    echo ""
    echo "=== Installation complete ==="
    echo ""
    echo "Run with:"
    echo "  $SCRIPT_DIR/venv/bin/python $SCRIPT_DIR/file_taxes.py"
    echo ""
    echo "Or activate the environment first:"
    echo "  source $SCRIPT_DIR/venv/bin/activate"
    echo "  python file_taxes.py"
fi

echo ""
echo "Configuration:"
echo "  Edit .env to set your credentials"
echo ""
