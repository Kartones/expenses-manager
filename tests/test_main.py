import tempfile
from unittest.mock import patch
import pytest

from src.expenses.main import ExpensesManager


class TestExpensesManager:
    @pytest.fixture
    def manager(self) -> ExpensesManager:
        """Create a new ExpensesManager instance for testing."""
        with patch("builtins.input", return_value="se"):  # Mock country input
            return ExpensesManager(data_dir=".")

    def test_initialization_with_data_dir(self) -> None:
        """Test that ExpensesManager is initialized with correct data directory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            with patch("builtins.input", return_value="se"):  # Mock country input
                manager = ExpensesManager(data_dir=temp_dir)
                assert manager.data_dir == temp_dir

    def test_initialization_defaults_to_current_dir(self) -> None:
        """Test that ExpensesManager defaults to current directory."""
        with patch("builtins.input", return_value="se"):  # Mock country input
            manager = ExpensesManager()
            assert manager.data_dir == "."

    def test_run_interactive_expense_entry(self, manager: ExpensesManager) -> None:
        """Test interactive expense entry."""
        with patch("builtins.input") as mock_input:
            mock_input.side_effect = [
                "add-expense",  # command
                "2024/03/21",  # date
                "Shopping",  # category
                "100",  # amount
                "Food:Groceries",  # description
                "quit",  # exit command
            ]
            manager.run_interactive()

    def test_run_interactive_income_entry(self, manager: ExpensesManager) -> None:
        """Test interactive income entry."""
        with patch("builtins.input") as mock_input:
            mock_input.side_effect = [
                "add-income",  # command
                "2024/03/21",  # date
                "Salary",  # category
                "1000,500",  # amounts
                "Salary:Monthly",  # description
                "quit",  # exit command
            ]
            manager.run_interactive()

    def test_run_interactive_with_invalid_inputs(self, manager: ExpensesManager) -> None:
        """Test that invalid inputs are handled gracefully."""
        with patch("builtins.input") as mock_input:
            mock_input.side_effect = [
                "invalid-command",  # invalid command
                "add-expense",  # valid command
                "invalid-date",  # invalid date
                "2024/03/21",  # valid date
                "Food Shopping",  # invalid category (spaces)
                "Food:Shopping",  # valid category
                "abc",  # invalid amount
                "100",  # valid amount
                "Food:Groceries",  # description
                "quit",  # exit command
            ]
            manager.run_interactive()
