from dataclasses import dataclass, field
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
    """Represents a single line in an expense/income entry.

    Comments associated with this specific line are preserved when reading from
    and writing to .dat files. Comments appear before the line in the file.
    """

    amount: int
    description: str
    comments: List[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        """Validate the entry line after initialization."""
        if self.amount < 0:
            raise InvalidEntryLineError("Amount must be greater than or equal to 0")

        if not self.description:
            raise InvalidEntryLineError("Description cannot be empty")

        if " " in self.description:
            raise InvalidEntryLineError("Description cannot contain spaces, use colons (:) to separate words")

        if not isinstance(self.comments, list) or not all(isinstance(comment, str) for comment in self.comments):
            raise InvalidEntryLineError("Comments must be a list of strings")


@dataclass
class Entry:
    """Represents an expense or income entry.

    Entry-level comments are preserved when reading from and writing to .dat files.
    These comments appear before the first line of the entry in the file.
    """

    entry_date: date
    category: str
    entry_type: EntryType
    currency: str
    lines: List[EntryLine]
    comments: List[str] = field(default_factory=list)

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

        if not isinstance(self.comments, list) or not all(isinstance(comment, str) for comment in self.comments):
            raise InvalidEntryError("Comments must be a list of strings")
