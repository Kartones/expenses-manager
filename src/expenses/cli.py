from enum import Enum
from dataclasses import dataclass
from datetime import datetime, date
import argparse

from src.expenses.input_manager import InputManager
from src.expenses.models import Entry, EntryLine, EntryType, VALID_COUNTRY_CURRENCIES
from src.expenses.persistence import EntryRepository


class CommandType(Enum):
    """Available CLI commands."""

    ADD_EXPENSE = "expense"
    ADD_INCOME = "income"
    QUIT = "quit"

    @classmethod
    def from_string(cls, command: str) -> "CommandType":
        """Convert a string command to enum value.

        Args:
            command: The command string to parse.

        Returns:
            The matching CommandType enum value.

        Raises:
            ValueError: If the command is invalid.
        """
        command = command.strip().lower()
        if command in ["expense", "e"]:
            return cls.ADD_EXPENSE
        elif command in ["income", "i"]:
            return cls.ADD_INCOME
        elif command in ["quit", "q"]:
            return cls.QUIT
        raise ValueError(f"Invalid command: {command}")


@dataclass
class CLI:
    """Command Line Interface for the expenses manager."""

    input_manager: InputManager
    repository: EntryRepository | None = None
    parser: argparse.ArgumentParser | None = None

    def __post_init__(self) -> None:
        """Initialize repository if not provided and setup argument parser."""
        if self.repository is None:
            self.repository = EntryRepository(data_dir=".", country_code=self.input_manager.country)

        if self.parser is None:
            self.parser = argparse.ArgumentParser(
                description="Expenses Manager - A CLI tool for managing expenses and income"
            )
            self.parser.add_argument(
                "--data-dir",
                type=str,
                default=".",
                help="Directory where data files are stored (default: current directory)",
            )
            self.parser.add_argument(
                "--interactive",
                action="store_true",
                help="Run in interactive mode (default: True)",
            )

    def parse_args(self) -> argparse.Namespace:
        """Parse command line arguments.

        Returns:
            Parsed command line arguments.
        """
        if self.parser is None:
            raise RuntimeError("Parser not initialized")
        return self.parser.parse_args()

    def parse_command(self, command: str) -> CommandType:
        """Parse and validate a command string.

        Args:
            command: The command string to parse.

        Returns:
            The parsed command type.

        Raises:
            ValueError: If the command is invalid.
        """
        return CommandType.from_string(command)

    def _validate_date(self, date_str: str) -> date:
        """Validate and parse a date string.

        Args:
            date_str: Date string in YYYY/MM/DD format

        Returns:
            Parsed date object

        Raises:
            ValueError: If the date format is invalid
        """
        try:
            return datetime.strptime(date_str, "%Y/%m/%d").date()
        except ValueError:
            raise ValueError("Invalid date format. Use YYYY/MM/DD")

    def _validate_amount(self, amount_str: str) -> int:
        """Validate and parse an amount string.

        Args:
            amount_str: Amount string to validate

        Returns:
            Parsed positive integer amount

        Raises:
            ValueError: If the amount is invalid or not positive
        """
        try:
            amount = int(amount_str)
            if amount <= 0:
                raise ValueError("Amount must be a positive number")
            return amount
        except ValueError as e:
            if "invalid literal for int()" in str(e):
                raise ValueError("Amount must be a positive number")
            raise

    def handle_add_expense(
        self,
        date_str: str,
        category: str,
        amount_str: str,
        description: str,
    ) -> None:
        """Handle the add-expense command.

        Args:
            date_str: Date in YYYY/MM/DD format
            category: Entry category
            amount_str: Amount as string (must be positive integer)
            description: Entry description

        Raises:
            ValueError: If any argument is invalid
            RuntimeError: If repository is not initialized
        """
        entry_date = self._validate_date(date_str)
        amount = self._validate_amount(amount_str)

        if self.repository is None:
            raise RuntimeError("Repository not initialized")

        entry = Entry(
            entry_date=entry_date,
            category=category,
            entry_type=EntryType.EXPENSE,
            currency=VALID_COUNTRY_CURRENCIES[self.input_manager.country],
            lines=[EntryLine(amount=amount, description=description)],
        )

        self.repository.save_entry(entry)

    def handle_add_income(
        self,
        date_str: str,
        category: str,
        amount_str: str,
        description: str,
    ) -> None:
        """Handle the add-income command.

        Args:
            date_str: Date in YYYY/MM/DD format
            category: Entry category
            amount_str: Amount as string (must be positive integer)
            description: Entry description

        Raises:
            ValueError: If any argument is invalid
            RuntimeError: If repository is not initialized
        """
        entry_date = self._validate_date(date_str)
        amount = self._validate_amount(amount_str)

        if self.repository is None:
            raise RuntimeError("Repository not initialized")

        entry = Entry(
            entry_date=entry_date,
            category=category,
            entry_type=EntryType.INCOME,
            currency=VALID_COUNTRY_CURRENCIES[self.input_manager.country],
            lines=[EntryLine(amount=amount, description=description)],
        )

        self.repository.save_entry(entry)

    def run(self) -> None:
        """Run the CLI in interactive mode."""
        print("\nExpenses Manager CLI")
        print("Available commands:")
        print("  expense/e - Add a new expense")
        print("  income/i - Add a new income")
        print("  quit/q   - Exit the program\n")

        while True:
            try:
                command = input("Command > ").strip()
                command_type = self.parse_command(command)

                if command_type == CommandType.QUIT:
                    print("Goodbye!")
                    break
                elif command_type == CommandType.ADD_EXPENSE:
                    print("\nAdding expense:")
                    print("Format: YYYY/MM/DD category amount description")
                    print("Example: 2024/03/15 food 1234 Lunch at restaurant\n")

                    raw_input = input("Enter details > ")
                    # Split by space, but rejoin the description parts
                    parts = raw_input.split()
                    if len(parts) < 4:
                        raise ValueError(
                            "Missing required fields. Please provide date, category, amount and description."
                        )

                    self.handle_add_expense(
                        date_str=parts[0],
                        category=parts[1],
                        amount_str=parts[2],
                        description=" ".join(parts[3:]),
                    )
                    print("✓ Expense added successfully")

                elif command_type == CommandType.ADD_INCOME:
                    print("\nAdding income:")
                    print("Format: YYYY/MM/DD category amount description")
                    print("Example: 2024/03/15 salary 5000 Monthly salary\n")

                    raw_input = input("Enter details > ")
                    # Split by space, but rejoin the description parts
                    parts = raw_input.split()
                    if len(parts) < 4:
                        raise ValueError(
                            "Missing required fields. Please provide date, category, amount and description."
                        )

                    self.handle_add_income(
                        date_str=parts[0],
                        category=parts[1],
                        amount_str=parts[2],
                        description=" ".join(parts[3:]),
                    )
                    print("✓ Income added successfully")

            except ValueError as e:
                print(f"\n❌ Error: {e}")
                print("Please try again with the correct format\n")
            except KeyboardInterrupt:
                print("\nOperation cancelled. Goodbye!")
                break
            except EOFError:
                print("\nGoodbye!")
                break
