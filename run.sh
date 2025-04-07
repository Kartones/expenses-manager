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

# Check number of arguments
if [ $# -gt 1 ]; then
    echo "Error: At most one argument (data folder) can be provided"
    exit 1
fi

# Set data folder and display message
data_folder=${1:-.}
echo "Running with data folder at $data_folder"

# Run the application with the data folder
python -m src.expenses.main "$data_folder"

# Deactivate virtual environment
deactivate