from datetime import date
from pathlib import Path
from typing import Union

from expenses.models import ExpenseEntry, IncomeEntry


class FileManager:
    def __init__(self, country: str = "se") -> None:
        """Initialize the FileManager.

        Args:
            country: The country code to use in filenames (default: "se")
        """
        self.country = country

    def generate_filename(self, entry_date: date) -> str:
        """Generate the appropriate filename for a given date.

        Args:
            entry_date: The date to generate the filename for

        Returns:
            The filename in the format {country}-YYYY-MM.dat
        """
        return f"{self.country}-{entry_date.year}-{entry_date.month:02d}.dat"

    def write_entry(self, base_path: Path, entry: Union[ExpenseEntry, IncomeEntry]) -> None:
        """Write an entry to the appropriate file.

        Args:
            base_path: The directory where the file should be written
            entry: The entry to write (either expense or income)
        """
        filename = base_path / self.generate_filename(entry.date)

        # Format the entry header
        lines = []

        # Add a blank line if file exists and has content
        if filename.exists() and filename.stat().st_size > 0:
            lines.append("")

        lines.append(f"{entry.date.year}/{entry.date.month:02d}/{entry.date.day:02d} {entry.category}")

        # Add items based on entry type
        if isinstance(entry, ExpenseEntry):
            # Add expense items
            for expenseItem in entry.items:
                lines.append(f"  {expenseItem.description.ljust(37)}{expenseItem.currency} {expenseItem.amount}")
            # Add the account line
            lines.append(f"  * {entry.account}")
        elif isinstance(entry, IncomeEntry):
            # Add income items
            for incomeItem in entry.items:
                lines.append(f"  * {entry.account.ljust(35)}{incomeItem.currency} {incomeItem.amount}")
            # Add the description
            lines.append(f"  {entry.description}")

        # Write to file (append mode if exists)
        mode = "a" if filename.exists() else "w"
        with open(filename, mode) as f:
            f.write("\n".join(lines) + "\n")
