[![CircleCI](https://circleci.com/gh/Kartones/expenses-manager/tree/main.svg?style=svg)](https://circleci.com/gh/Kartones/expenses-manager/tree/main)

# Expenses Manager

A simple command-line tool to track personal expenses and income. It uses a simplified version of the [Ledger](https://ledger-cli.org/doc/ledger3.html) format.

⚠️ This is a Vibe-coding experiment: 100% AI-built via prompting, excepting this README's introduction. ⚠️


## Features

- Track both expenses and income entries
- Support for multiple items per entry
- Automatic file organization by month
- Input validation and error handling
- Simple text-based file format
- Multi-country support (Spain/Sweden) with automatic currency selection
- Automatic currency handling (€ for Spain, kr for Sweden)

## Requirements

- Python 3.13 or higher
- pip (Python package installer)
- virtualenv (recommended)

## Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd finances
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Unix/macOS
   # or
   .venv\Scripts\activate  # On Windows
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Quick Start
Run the application using the provided shell script:
```bash
./run.sh [data_dir]
```
This script will:
- Create virtual environment if not present
- Install dependencies if needed
- Run the application with the specified data directory (defaults to current directory)
- Clean up when done

### Manual Setup
1. Run the application:
   ```bash
   python -m src.expenses.main [data_dir]
   ```
   The optional `data_dir` argument specifies where expense/income files will be stored (defaults to current directory).

2. Follow the interactive prompts:
   - Select country (es/se) at startup [defaults to se]
   - Choose entry type: expense (E) or income (I)
   - Enter date in YYYY-MM-DD format [defaults to today]
   - Enter category (use colons instead of spaces)
   - For expenses: enter description and amount
   - For income: enter description and amount
   - Optionally add multiple items
   - Choose whether to add another entry

### Example Expense Entry (Sweden)

```
Enter country (es/se) [se]: se
Enter entry type: expense (E) or income (I): e
Enter date (YYYY-MM-DD) [2024-03-21]:
Enter category: Shopping
Enter description: weekly:groceries
Enter amount (integer): 100
Add another item? (y/n): n
Add another entry? (y/n): n
```

### Example Income Entry (Spain)

```
Enter country (es/se) [se]: es
Enter entry type: expense (E) or income (I): i
Enter date (YYYY-MM-DD) [2024-03-21]:
Enter category: Salary
Enter description: monthly:salary
Enter amount (integer): 25000
Add another item? (y/n): n
Add another entry? (y/n): n
```

## Configuration

The application stores expense/income files in the specified data directory (defaults to current directory if not provided).

## File Format

Entries are stored in monthly files named `{country}-YYYY-MM.dat` in the specified data directory, where `country` is either `es` or `se`. The file format is:

For expenses (Sweden):
```
2024/03/21 Shopping
  weekly:groceries                     kr 100
  * Assets:Checking
```

For income (Spain):
```
2024/03/21 Salary
  * Assets:Checking                    € 25000
  monthly:salary
```

## Development

### Running Tests

```bash
pip install -e .  # Install package in development mode
python -m pytest tests/ -v
```

### Type Checking

```bash
mypy src/ tests/
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests and type checking
5. Submit a pull request