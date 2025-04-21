#!/bin/zsh

# Exit on error
set -e

# Check Python version
python_version=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
required_version="3.13"

if [ $(echo "$python_version < $required_version" | bc -l) -eq 1 ]; then
    echo "Error: Python $required_version or higher is required (found $python_version)"
    exit 1
fi

# Check number of arguments
if [ $# -gt 1 ]; then
    echo "Error: At most one argument (data folder) can be provided"
    exit 1
fi

# Get data directory argument or use current directory
DATA_DIR="${1:-.}"

# Display selected directory
echo "Running with data folder at $DATA_DIR"

# Create virtual environment if it doesn't exist
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv .venv
    source .venv/bin/activate
    echo "Installing dependencies..."
    pip install -r requirements.txt
else
    source .venv/bin/activate
fi

echo "Installing dependencies..."
pip install -r requirements.txt

# Install the package in development mode
pip install -e .

echo "Running DAT viewer application..."
python scripts/run_viewer.py "$DATA_DIR"

# Deactivate virtual environment on exit
deactivate