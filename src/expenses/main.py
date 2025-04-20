from datetime import datetime

from src.expenses.cli import CLI, CommandType
from src.expenses.input_manager import InputManager
from src.expenses.persistence import EntryRepository


class ExpensesManager:
    """Main entry point for the expenses manager application."""

    def __init__(self, data_dir: str = ".") -> None:
        """Initialize the expenses manager.

        Args:
            data_dir: Directory where data files are stored. Defaults to current directory.
        """
        self.data_dir = data_dir
        self.input_manager = InputManager()
        self.input_manager.set_country()
        self.repository = EntryRepository(data_dir=data_dir, country_code=self.input_manager.country)
        self.cli = CLI(input_manager=self.input_manager, repository=self.repository)

    def run_interactive(self) -> None:
        """Run the application in interactive mode."""
        while True:
            command = input("Enter command (expense/e, income/i, quit/q): ").strip().lower()
            if command in ["q", "quit"]:
                break

            try:
                today_str = datetime.now().strftime("%Y/%m/%d")
                command_type = self.cli.parse_command(command)
                if command_type == CommandType.ADD_EXPENSE:
                    # Get date with default to today
                    date_str = input(f"Enter date (YYYY/MM/DD) [{today_str}]: ").strip()
                    if not date_str:
                        date_str = today_str

                    self.cli.handle_add_expense(
                        [
                            date_str,
                            input("Category: "),
                            input("Amount: "),
                            input("Description: "),
                        ]
                    )
                elif command_type == CommandType.ADD_INCOME:
                    # Get date with default to today
                    date_str = input(f"Enter date (YYYY/MM/DD) [{today_str}]: ").strip()
                    if not date_str:
                        date_str = today_str

                    self.cli.handle_add_income(
                        [
                            date_str,
                            input("Category: "),
                            input("Amount: "),
                            input("Description: "),
                        ]
                    )
            except ValueError as e:
                print(f"Error: {e}")
            except Exception as e:
                print(f"Unexpected error: {e}")


if __name__ == "__main__":
    import sys

    data_dir = sys.argv[1] if len(sys.argv) > 1 else "."
    manager = ExpensesManager(data_dir)
    manager.run_interactive()
