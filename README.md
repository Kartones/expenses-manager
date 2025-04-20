[![CircleCI](https://circleci.com/gh/Kartones/expenses-manager/tree/main.svg?style=svg)](https://circleci.com/gh/Kartones/expenses-manager/tree/main)

# Expenses Manager

A simple command-line tool to track personal expenses and income. It uses a simplified version of the [Ledger](https://ledger-cli.org/doc/ledger3.html) format. Check [the specs](specs/data-format.md) for more details.

⚠️ This is a Vibe-coding experiment: 100% AI-built via prompting, excepting this README's introduction. ⚠️

## Features

- Track both expenses and income
- Support for multiple currencies (EUR for Spain, SEK for Sweden)
- Automatic file organization by country and month
- Interactive command-line interface
- Automatic entry merging for same date/category
- Input validation and error handling

## Requirements

- Python 3.13 or higher
- pip (Python package installer)
- virtualenv (recommended)

## Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd expenses-manager
   ```

2. Run the application using the provided script:
   ```bash
   ./run.sh [data_dir]
   ```
   The script will:
   - Create a virtual environment if not present
   - Install dependencies
   - Run the application
   - Clean up when done

## Usage

### Commands

- `expense` or `e`: Add a new expense entry
- `income` or `i`: Add a new income entry
- `quit` or `q`: Exit the application

### Data Entry

For both expense and income entries:
- Date: YYYY/MM/DD format (defaults to today if empty)
- Category: Words separated by colons (e.g., "Food:Groceries")
- Description: Words separated by colons (e.g., "Weekly:Shopping")
- Amount: Positive integer values

### Special Features

- **Multiple Income Amounts**: For income entries, you can enter multiple amounts separated by commas
- **Automatic Entry Merging**: If you add an entry with the same date and category as an existing one:
  - For expenses: The new entry lines are added to the existing entry
  - For income: The new amounts are added if the description matches

### Example: Adding an Expense

```
Enter command (expense/e, income/i, quit/q): e
Enter date (YYYY/MM/DD) [2024/03/21]: 2024/03/21
Category: Food:Groceries
Amount: 150
Description: Weekly:Shopping

Entry saved successfully!
```

### Example: Adding Income with Multiple Amounts

```
Enter command (expense/e, income/i, quit/q): income
Enter date (YYYY/MM/DD) [2024/03/21]: 2024/03/25
Category: Salary
Amount(s) (comma-separated for multiple): 2000,500
Description: Monthly:Salary

Entry saved successfully!
```

### File Organization

The application automatically organizes entries in files following this pattern:
- Spain (EUR): `es-YYYY-MM.dat`
- Sweden (SEK): `se-YYYY-MM.dat`

## Development

### Running Tests

```bash
# Activate virtual environment
source .venv/bin/activate  # Unix/macOS
# or
.venv\Scripts\activate    # Windows

# Run tests
python -m pytest tests/ -v
```

### Type Checking

```bash
mypy src/ tests/
```

## Data Format

For detailed information about the data format and validation rules, see [specs/data-format.md](specs/data-format.md).
