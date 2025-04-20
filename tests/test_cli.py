from datetime import date
from unittest.mock import Mock
import pytest

from src.expenses.cli import CLI, CommandType
from src.expenses.input_manager import InputManager
from src.expenses.models import EntryType, Entry, EntryLine
from src.expenses.persistence import EntryRepository


class TestCLI:
    @pytest.fixture
    def input_manager(self) -> InputManager:
        """Create a mocked InputManager for testing."""
        manager = Mock(spec=InputManager)
        manager.country = "se"
        return manager

    @pytest.fixture
    def cli(self, input_manager: InputManager) -> CLI:
        """Create a new CLI instance for testing."""
        return CLI(input_manager)

    @pytest.fixture
    def mock_repository(self) -> Mock:
        """Create a mock repository for testing."""
        return Mock()

    @pytest.fixture
    def income_entry(self) -> Entry:
        """Create a sample income entry for testing."""
        return Entry(
            entry_date=date(2024, 3, 21),
            category="Salary",
            entry_type=EntryType.INCOME,
            currency="EUR",
            lines=[EntryLine(amount=1000, description="Salary:Monthly")],
        )

    @pytest.fixture
    def repository_se(self) -> EntryRepository:
        """Create a repository instance for Swedish entries."""
        return EntryRepository(data_dir=".", country_code="se")

    @pytest.fixture
    def repository_es(self) -> EntryRepository:
        """Create a repository instance for Spanish entries."""
        return EntryRepository(data_dir=".", country_code="es")

    def test_cli_initialization(self, cli: CLI, input_manager: InputManager) -> None:
        """Test that CLI is properly initialized with an InputManager."""
        assert cli.input_manager == input_manager
        assert cli.input_manager.country == "se"

    def test_parse_command_valid(self, cli: CLI) -> None:
        """Test parsing of valid commands."""
        # Test full commands
        assert cli.parse_command("expense") == CommandType.ADD_EXPENSE
        assert cli.parse_command("income") == CommandType.ADD_INCOME
        # Test shortcuts
        assert cli.parse_command("e") == CommandType.ADD_EXPENSE
        assert cli.parse_command("i") == CommandType.ADD_INCOME
        # Test with whitespace
        assert cli.parse_command("  expense  ") == CommandType.ADD_EXPENSE
        assert cli.parse_command("  e  ") == CommandType.ADD_EXPENSE

    def test_parse_command_invalid(self, cli: CLI) -> None:
        """Test parsing of invalid commands raises ValueError."""
        with pytest.raises(ValueError, match="Invalid command: unknown"):
            cli.parse_command("unknown")
        with pytest.raises(ValueError, match="Invalid command: add-expense"):
            cli.parse_command("add-expense")
        with pytest.raises(ValueError, match="Invalid command: x"):
            cli.parse_command("x")

    def test_add_expense_command(self, cli: CLI, mock_repository: Mock) -> None:
        """Test adding an expense entry with a single line."""
        # Arrange
        cli.repository = mock_repository

        # Act
        cli.handle_add_expense(
            date_str="2024/03/21",
            category="Shopping",
            amount_str="100",
            description="Food:Groceries",
        )

        # Assert
        mock_repository.save_entry.assert_called_once()
        saved_entry = mock_repository.save_entry.call_args[0][0]
        assert saved_entry.entry_date == date(2024, 3, 21)
        assert saved_entry.category == "Shopping"
        assert saved_entry.entry_type == EntryType.EXPENSE
        assert saved_entry.currency == "SEK"  # Should match country (se)
        assert len(saved_entry.lines) == 1
        assert saved_entry.lines[0].amount == 100
        assert saved_entry.lines[0].description == "Food:Groceries"

    def test_add_expense_invalid_date_format(self, cli: CLI) -> None:
        """Test that invalid date format raises error."""
        with pytest.raises(ValueError, match="Invalid date format. Use YYYY/MM/DD"):
            cli.handle_add_expense(
                date_str="2024-03-21",
                category="Shopping",
                amount_str="100",
                description="Food:Groceries",
            )

    def test_add_expense_invalid_amount(self, cli: CLI) -> None:
        """Test that non-numeric amount raises error."""
        with pytest.raises(ValueError, match="Amount must be a positive number"):
            cli.handle_add_expense(
                date_str="2024/03/21",
                category="Shopping",
                amount_str="abc",
                description="Food:Groceries",
            )

    def test_add_expense_negative_amount(self, cli: CLI) -> None:
        """Test that negative amount raises error."""
        with pytest.raises(ValueError, match="Amount must be a positive number"):
            cli.handle_add_expense(
                date_str="2024/03/21",
                category="Shopping",
                amount_str="-100",
                description="Food:Groceries",
            )

    def test_add_expense_missing_arguments(self, cli: CLI) -> None:
        """Test that missing arguments raise error."""
        with pytest.raises(TypeError):
            cli.handle_add_expense(  # type: ignore[call-arg]
                date_str="2024/03/21",
                category="Shopping",
                amount_str="100",
            )

    def test_add_expense_extra_arguments(self, cli: CLI) -> None:
        """Test that extra arguments raise error."""
        with pytest.raises(TypeError):
            cli.handle_add_expense(  # type: ignore[call-arg]
                date_str="2024/03/21",
                category="Shopping",
                amount_str="100",
                description="Food:Groceries",
                extra="extra",
            )

    def test_add_expense_with_spaces_in_category(self, cli: CLI, mock_repository: Mock) -> None:
        """Test that category can contain spaces."""
        # Arrange
        cli.repository = mock_repository

        # Act
        cli.handle_add_expense(
            date_str="2024/03/21",
            category="Food and Drinks",
            amount_str="100",
            description="Food:Groceries",
        )

        # Assert
        mock_repository.save_entry.assert_called_once()
        saved_entry = mock_repository.save_entry.call_args[0][0]
        assert saved_entry.category == "Food and Drinks"

    def test_add_income_command(self, cli: CLI, mock_repository: Mock) -> None:
        """Test adding an income entry."""
        # Arrange
        cli.repository = mock_repository

        # Act
        cli.handle_add_income(
            date_str="2024/03/21",
            category="Salary",
            amount_str="1000",
            description="Salary:Monthly",
        )

        # Assert
        mock_repository.save_entry.assert_called_once()
        saved_entry = mock_repository.save_entry.call_args[0][0]
        assert saved_entry.entry_date == date(2024, 3, 21)
        assert saved_entry.category == "Salary"
        assert saved_entry.entry_type == EntryType.INCOME
        assert saved_entry.currency == "SEK"  # Should match country (se)
        assert len(saved_entry.lines) == 1
        assert saved_entry.lines[0].amount == 1000
        assert saved_entry.lines[0].description == "Salary:Monthly"

    def test_add_income_invalid_date_format(self, cli: CLI) -> None:
        """Test that invalid date format raises error."""
        with pytest.raises(ValueError, match="Invalid date format. Use YYYY/MM/DD"):
            cli.handle_add_income(
                date_str="2024-03-21",
                category="Salary",
                amount_str="1000",
                description="Salary:Monthly",
            )

    def test_add_income_invalid_amount(self, cli: CLI) -> None:
        """Test that non-numeric amount raises error."""
        with pytest.raises(ValueError, match="Amount must be a positive number"):
            cli.handle_add_income(
                date_str="2024/03/21",
                category="Salary",
                amount_str="abc",
                description="Salary:Monthly",
            )

    def test_add_income_negative_amount(self, cli: CLI) -> None:
        """Test that negative amount raises error."""
        with pytest.raises(ValueError, match="Amount must be a positive number"):
            cli.handle_add_income(
                date_str="2024/03/21",
                category="Salary",
                amount_str="-100",
                description="Salary:Monthly",
            )

    def test_add_income_missing_arguments(self, cli: CLI) -> None:
        """Test that missing arguments raise error."""
        with pytest.raises(TypeError):
            cli.handle_add_income(  # type: ignore[call-arg]
                date_str="2024/03/21",
                category="Salary",
                amount_str="1000",
            )

    def test_add_income_extra_arguments(self, cli: CLI) -> None:
        """Test that extra arguments raise error."""
        with pytest.raises(TypeError):
            cli.handle_add_income(  # type: ignore[call-arg]
                date_str="2024/03/21",
                category="Salary",
                amount_str="1000",
                description="Salary:Monthly",
                extra="extra",
            )

    def test_add_income_with_spaces_in_category(self, cli: CLI, mock_repository: Mock) -> None:
        """Test that category can contain spaces."""
        # Arrange
        cli.repository = mock_repository

        # Act
        cli.handle_add_income(
            date_str="2024/03/21",
            category="Monthly Salary",
            amount_str="1000",
            description="Salary:Monthly",
        )

        # Assert
        mock_repository.save_entry.assert_called_once()
        saved_entry = mock_repository.save_entry.call_args[0][0]
        assert saved_entry.category == "Monthly Salary"
