import os
from datetime import date
from typing import List

from .models import Entry, EntryLine, EntryType, VALID_COUNTRY_CURRENCIES


class EntryRepository:
    """Repository for managing expense/income entries in files."""

    def __init__(self, data_dir: str, country_code: str) -> None:
        """Initialize the repository with the data directory path."""
        self.data_dir = data_dir
        self.country_code = country_code.lower()
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)

    def get_filename_for_entry(self, entry: Entry) -> str:
        """Generate the base filename for an entry based on its date and currency."""
        country_code = "se" if entry.currency == "SEK" else "es"
        return f"{country_code}-{entry.entry_date.year}-{entry.entry_date.month:02d}.dat"

    def _get_filepath_for_entry(self, entry: Entry) -> str:
        """Get the full file path for an entry."""
        return os.path.join(self.data_dir, self.get_filename_for_entry(entry))

    def format_entry(self, entry: Entry) -> str:
        """Format an entry for writing to file."""
        lines = []
        lines.append(f"{entry.entry_date.strftime('%Y/%m/%d')} {entry.category}")

        if entry.entry_type == EntryType.EXPENSE:
            for line in entry.lines:
                # Total width before currency should be exactly 39 characters
                # This includes the 2 initial spaces and the description
                padding_length = 39 - len(line.description)
                lines.append(f"  {line.description}{' ' * padding_length}{entry.currency} {line.amount}")
            lines.append("  * Assets:Checking")
        else:  # INCOME
            for line in entry.lines:
                # Exactly 22 spaces between "* Assets:Checking" and currency
                lines.append(f"  * Assets:Checking{' ' * 22}{entry.currency} {line.amount}")
            lines.append(f"  {line.description}")

        # Ensure exactly two blank lines after each entry
        return "\n".join(lines) + "\n\n"

    def save_entry(self, entry: Entry) -> None:
        """Save an entry to its corresponding file, maintaining date order."""
        filename = self.get_filename_for_entry(entry)
        filepath = self._get_filepath_for_entry(entry)
        country_code = filename[:2]
        expected_currency = VALID_COUNTRY_CURRENCIES.get(country_code)
        if not expected_currency or entry.currency != expected_currency:
            raise ValueError(f"Currency {entry.currency} does not match country code {country_code}")

        # Read existing entries if file exists
        entries = []
        if os.path.exists(filepath):
            entries = self.read_entries(filepath)

            # For income entries, check if there's already an entry for this date
            if entry.entry_type == EntryType.INCOME:
                existing_income_entries = [
                    e
                    for e in entries
                    if e.entry_date == entry.entry_date
                    and e.entry_type == EntryType.INCOME
                    and e.category != entry.category  # Allow merging same category
                ]
                if existing_income_entries:
                    raise ValueError("Cannot have multiple income entries for the same date")

            # Check for entries that can be merged
            for existing_entry in entries:
                if (
                    existing_entry.entry_date == entry.entry_date
                    and existing_entry.category == entry.category
                    and existing_entry.entry_type == entry.entry_type
                    and existing_entry.currency == entry.currency
                ):
                    try:
                        # Merge entries
                        merged_entry = self.merge_entries(existing_entry, entry)
                        # Remove old entry and add merged one
                        entries.remove(existing_entry)
                        entries.append(merged_entry)
                        break
                    except ValueError:
                        # If merge fails (e.g. different descriptions for income), just add as new entry
                        entries.append(entry)
                        break
            else:
                # No matching entry found for merging
                entries.append(entry)
        else:
            # No existing entries
            entries.append(entry)

        # Sort and write all entries
        sorted_entries = self._sort_entries(entries)
        self._write_entries(sorted_entries, filepath)

    def save_entries(self, entries: List[Entry]) -> None:
        """Save multiple entries to a file, ensuring date order."""
        if not entries:
            return

        # Validate entries
        self.validate_entries(entries)

        # Sort entries and write
        filepath = self._get_filepath_for_entry(entries[0])
        sorted_entries = self._sort_entries(entries)
        self._write_entries(sorted_entries, filepath)

    def _write_entries(self, entries: List[Entry], filepath: str) -> None:
        """Write entries to a file, overwriting existing content."""
        content = []
        for entry in entries:
            content.append(self.format_entry(entry))
        with open(filepath, "w") as f:
            f.write("".join(content))

    def read_entries(self, filepath: str) -> List[Entry]:
        """Read all entries from a file."""
        entries: List[Entry] = []
        current_entry_lines: List[str] = []

        with open(filepath) as f:
            for line in f:
                line = line.rstrip()

                # Skip empty lines
                if not line:
                    if current_entry_lines:
                        entries.append(self._parse_entry(current_entry_lines))
                        current_entry_lines = []
                    continue

                # Skip comment lines
                if line.lstrip().startswith(";"):
                    continue

                current_entry_lines.append(line)

            # Handle last entry if file doesn't end with empty line
            if current_entry_lines:
                entries.append(self._parse_entry(current_entry_lines))

        return entries

    def merge_entries(self, existing_entry: Entry, new_entry: Entry) -> Entry:
        """Merge two entries with the same date."""
        if existing_entry.entry_date != new_entry.entry_date:
            raise ValueError("Cannot merge entries with different dates")

        if existing_entry.entry_type != new_entry.entry_type:
            raise ValueError("Cannot merge entries of different types")

        if existing_entry.currency != new_entry.currency:
            raise ValueError("Cannot merge entries with different currencies")

        if existing_entry.category != new_entry.category:
            raise ValueError("Cannot merge entries with different categories")

        if existing_entry.entry_type == EntryType.INCOME:
            # For income entries, descriptions must match
            existing_desc = existing_entry.lines[0].description
            new_desc = new_entry.lines[0].description
            if existing_desc != new_desc:
                raise ValueError("Cannot merge income entries with different descriptions")

        # Create new entry with combined lines
        return Entry(
            entry_date=existing_entry.entry_date,
            category=existing_entry.category,
            entry_type=existing_entry.entry_type,
            currency=existing_entry.currency,
            lines=existing_entry.lines + new_entry.lines,
        )

    def validate_entries(self, entries: List[Entry]) -> None:
        """Validate that all entries have the correct currency for the country code."""
        expected_currency = VALID_COUNTRY_CURRENCIES.get(self.country_code)
        if not expected_currency:
            raise ValueError(f"Invalid country code: {self.country_code}")

        for entry in entries:
            if entry.currency != expected_currency:
                raise ValueError(
                    f"Invalid currency {entry.currency} for country {self.country_code}. Expected {expected_currency}"
                )

    def _sort_entries(self, entries: List[Entry]) -> List[Entry]:
        """Sort entries by date in ascending order."""
        return sorted(entries, key=lambda e: e.entry_date)

    def _parse_entry(self, lines: List[str]) -> Entry:
        """Parse an entry from its lines."""
        # Filter out comment lines
        lines = [line for line in lines if not line.lstrip().startswith(";")]

        if not lines:
            raise ValueError("Empty entry")

        # Parse header
        header = lines[0].split(" ", 1)
        if len(header) != 2:
            raise ValueError("Invalid entry header")

        entry_date = date.fromisoformat(header[0].replace("/", "-"))
        category = header[1]

        # Determine entry type and currency
        is_expense = "* Assets:Checking" in lines[-1]
        entry_lines = []
        entry_currency = None

        if is_expense:
            entry_type = EntryType.EXPENSE
            # Parse expense lines (excluding header and footer)
            for line in lines[1:-1]:
                if "* Assets:Checking" in line:
                    continue
                parts = line.strip().split()
                if len(parts) < 3:
                    continue
                try:
                    currency = parts[-2]
                    amount = int(parts[-1])
                    description = " ".join(parts[:-2])
                    entry_lines.append(EntryLine(amount=amount, description=description))
                    if entry_currency is None:
                        entry_currency = currency
                except ValueError:
                    continue
        else:
            entry_type = EntryType.INCOME
            # Parse income lines (excluding header and description)
            description = lines[-1].strip()
            for line in lines[1:-1]:
                if not line.strip().startswith("* Assets:Checking"):
                    continue
                parts = line.strip().split()
                if len(parts) < 4:
                    continue
                try:
                    currency = parts[-2]
                    amount = int(parts[-1])
                    entry_lines.append(EntryLine(amount=amount, description=description))
                    if entry_currency is None:
                        entry_currency = currency
                except ValueError:
                    continue

        if not entry_lines:
            raise ValueError("No valid entry lines found")

        if entry_currency is None:
            raise ValueError("Could not determine entry currency")

        return Entry(
            entry_date=entry_date,
            category=category,
            entry_type=entry_type,
            currency=entry_currency,
            lines=entry_lines,
        )
