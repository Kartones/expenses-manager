from enum import Enum
from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional
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
    repository: Optional[EntryRepository] = None
    parser: Optional[argparse.ArgumentParser] = None

    def __post_init__(self) -> None:
        """Initialize repository if not provided and setup argument parser."""
        if self.repository is None:
            self.repository = EntryRepository(data_dir=".", country_code=self.input_manager.country)

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

    def handle_add_expense(self, args: List[str]) -> None:
        """Handle the add-expense command.

        Args:
            args: List of command arguments [date, category, amount, description]

        Raises:
            ValueError: If the arguments are invalid
        """
        if len(args) != 4:
            raise ValueError("Usage: add-expense <date> <category> <amount> <description>")

        try:
            entry_date = datetime.strptime(args[0], "%Y/%m/%d").date()
        except ValueError:
            raise ValueError("Invalid date format. Use YYYY/MM/DD")

        category = args[1]

        try:
            amount = int(args[2])
            if amount <= 0:
                raise ValueError("Amount must be a positive number")
        except ValueError as e:
            if "invalid literal for int()" in str(e):
                raise ValueError("Amount must be a positive number")
            raise

        description = args[3]

        entry = Entry(
            entry_date=entry_date,
            category=category,
            entry_type=EntryType.EXPENSE,
            currency=VALID_COUNTRY_CURRENCIES[self.input_manager.country],
            lines=[EntryLine(amount=amount, description=description)],
        )

        if self.repository:
            self.repository.save_entry(entry)

    def handle_add_income(self, args: List[str]) -> None:
        """Handle the add-income command.

        Args:
            args: List of command arguments [date, category, amounts, description]
            amounts can be a single number or comma-separated numbers for multiple lines

        Raises:
            ValueError: If the arguments are invalid
        """
        if len(args) != 4:
            raise ValueError("Usage: add-income <date> <category> <amount> <description>")

        try:
            entry_date = datetime.strptime(args[0], "%Y/%m/%d").date()
        except ValueError:
            raise ValueError("Invalid date format. Use YYYY/MM/DD")

        category = args[1]

        # Handle multiple amounts
        amounts_str = args[2].split(",")
        amounts: List[int] = []
        for amount_str in amounts_str:
            try:
                amount = int(amount_str)
                if amount <= 0:
                    raise ValueError("Amount must be a positive number")
                amounts.append(amount)
            except ValueError as e:
                if "invalid literal for int()" in str(e):
                    raise ValueError("Amount must be a positive number")
                raise

        description = args[3]

        # Create entry lines with the same description
        lines = [EntryLine(amount=amount, description=description) for amount in amounts]

        entry = Entry(
            entry_date=entry_date,
            category=category,
            entry_type=EntryType.INCOME,
            currency=VALID_COUNTRY_CURRENCIES[self.input_manager.country],
            lines=lines,
        )

        if self.repository:
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

                    args = parts[:3] + [" ".join(parts[3:])]
                    self.handle_add_expense(args)
                    print("✓ Expense added successfully")

                elif command_type == CommandType.ADD_INCOME:
                    print("\nAdding income:")
                    print("Format: YYYY/MM/DD category amount description")
                    print("Example: 2024/03/15 salary 5000 Monthly salary")
                    print("For multiple amounts use commas: 1000,2000,3000\n")

                    raw_input = input("Enter details > ")
                    # Split by space, but rejoin the description parts
                    parts = raw_input.split()
                    if len(parts) < 4:
                        raise ValueError(
                            "Missing required fields. Please provide date, category, amount and description."
                        )

                    args = parts[:3] + [" ".join(parts[3:])]
                    self.handle_add_income(args)
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
