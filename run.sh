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

# Run the application, passing through any arguments
python -m src.expenses.main "$@"

# Deactivate virtual environment
deactivate