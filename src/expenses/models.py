from dataclasses import dataclass
from datetime import date
from enum import Enum, auto
from typing import List


class InvalidEntryLineError(Exception):
    """Raised when entry line validation fails."""

    pass


class InvalidEntryError(Exception):
    """Raised when entry validation fails."""

    pass


class EntryType(Enum):
    """Type of entry: expense or income."""

    EXPENSE = auto()
    INCOME = auto()


VALID_CURRENCIES = {"SEK", "EUR"}
VALID_COUNTRY_CURRENCIES = {"se": "SEK", "es": "EUR"}


@dataclass
class EntryLine:
    """Represents a single line in an expense/income entry."""

    amount: int
    description: str

    def __post_init__(self) -> None:
        """Validate the entry line after initialization."""
        if self.amount <= 0:
            raise InvalidEntryLineError("Amount must be positive")

        if not self.description:
            raise InvalidEntryLineError("Description cannot be empty")

        if " " in self.description:
            raise InvalidEntryLineError("Description cannot contain spaces, use colons (:) to separate words")


@dataclass
class Entry:
    """Represents an expense or income entry."""

    entry_date: date
    category: str
    entry_type: EntryType
    currency: str
    lines: List[EntryLine]

    def __post_init__(self) -> None:
        """Validate the entry after initialization."""
        if not self.lines:
            raise InvalidEntryError("Entry must have at least one line")

        if self.currency not in VALID_CURRENCIES:
            raise InvalidEntryError("Currency must be either SEK or EUR")

        # For income entries, all lines must have the same description
        if self.entry_type == EntryType.INCOME:
            descriptions = {line.description for line in self.lines}
            if len(descriptions) > 1:
                raise InvalidEntryError("Income entries must have same description for all lines")
