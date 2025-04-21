from datetime import date
from unittest.mock import mock_open, patch
import pytest
import os

from src.expenses.models import Entry, EntryLine, EntryType
from src.expenses.persistence import EntryRepository


class TestEntryRepository:
    @pytest.fixture
    def expense_entry(self) -> Entry:
        """Create a sample expense entry for testing."""
        return Entry(
            entry_date=date(2024, 3, 21),
            category="Shopping",
            entry_type=EntryType.EXPENSE,
            currency="SEK",
            lines=[
                EntryLine(amount=100, description="Shopping:Food"),
                EntryLine(amount=200, description="Shopping:Clothes"),
            ],
        )

    @pytest.fixture
    def income_entry(self) -> Entry:
        """Create a sample income entry for testing."""
        return Entry(
            entry_date=date(2024, 3, 21),
            category="Salary",
            entry_type=EntryType.INCOME,
            currency="EUR",
            lines=[
                EntryLine(amount=1000, description="Salary:Monthly"),
                EntryLine(amount=500, description="Salary:Monthly"),
            ],
        )

    @pytest.fixture
    def repository_se(self) -> EntryRepository:
        """Create a repository instance for Swedish entries."""
        return EntryRepository(data_dir=".", country_code="se")

    @pytest.fixture
    def repository_es(self) -> EntryRepository:
        """Create a repository instance for Spanish entries."""
        return EntryRepository(data_dir=".", country_code="es")

    def test_get_filename_for_entry(self, repository_se: EntryRepository, repository_es: EntryRepository) -> None:
        """Test filename generation based on entry date and currency."""
        # Arrange
        entry_se = Entry(
            entry_date=date(2024, 3, 21),
            category="Test",
            entry_type=EntryType.EXPENSE,
            currency="SEK",
            lines=[EntryLine(amount=100, description="Test:Entry")],
        )
        entry_es = Entry(
            entry_date=date(2024, 3, 21),
            category="Test",
            entry_type=EntryType.EXPENSE,
            currency="EUR",
            lines=[EntryLine(amount=100, description="Test:Entry")],
        )

        # Act & Assert
        assert repository_se.get_filename_for_entry(entry_se) == "se-2024-03.dat"
        assert repository_es.get_filename_for_entry(entry_es) == "es-2024-03.dat"

    def test_format_expense_entry(self, expense_entry: Entry, repository_se: EntryRepository) -> None:
        """Test formatting of expense entries."""
        # Arrange
        expected_output = (
            "2024/03/21 Shopping\n"
            "  Shopping:Food                          SEK 100\n"
            "  Shopping:Clothes                       SEK 200\n"
            "  * Assets:Checking\n"
            "\n"
        )

        # Act
        result = repository_se.format_entry(expense_entry)

        # Assert
        assert result == expected_output

    def test_format_income_entry(self, income_entry: Entry, repository_es: EntryRepository) -> None:
        """Test formatting of income entries."""
        # Arrange
        expected_output = (
            "2024/03/21 Salary\n"
            "  * Assets:Checking                      EUR 1000\n"
            "  * Assets:Checking                      EUR 500\n"
            "  Salary:Monthly\n"
            "\n"
        )

        # Act
        result = repository_es.format_entry(income_entry)

        # Assert
        assert result == expected_output

    def test_save_entry_creates_file_if_not_exists(self, expense_entry: Entry, repository_se: EntryRepository) -> None:
        """Test that saving an entry creates a new file if it doesn't exist."""
        # Arrange
        mock_file = mock_open()

        # Act
        with patch("builtins.open", mock_file):
            with patch("os.path.exists", return_value=False):
                repository_se.save_entry(expense_entry)

        # Assert
        mock_file.assert_called_once_with(os.path.join(".", "se-2024-03.dat"), "w")
        mock_file().write.assert_called_once_with(repository_se.format_entry(expense_entry))

    def test_save_entry_maintains_order_with_existing_entries(
        self, expense_entry: Entry, repository_se: EntryRepository
    ) -> None:
        """Test that saving an entry maintains date order with existing entries."""
        # Arrange
        existing_content = (
            "2024/03/20 Shopping\n"
            "  Shopping:Food                          SEK 100\n"
            "  * Assets:Checking\n"
            "\n"
            "2024/03/22 Shopping\n"
            "  Shopping:Food                          SEK 100\n"
            "  * Assets:Checking\n"
            "\n"
        )
        expected_content = (
            "2024/03/20 Shopping\n"
            "  Shopping:Food                          SEK 100\n"
            "  * Assets:Checking\n"
            "\n"
            "2024/03/21 Shopping\n"
            "  Shopping:Food                          SEK 100\n"
            "  Shopping:Clothes                       SEK 200\n"
            "  * Assets:Checking\n"
            "\n"
            "2024/03/22 Shopping\n"
            "  Shopping:Food                          SEK 100\n"
            "  * Assets:Checking\n"
            "\n"
        )
        mock_file = mock_open(read_data=existing_content)

        # Act
        with patch("builtins.open", mock_file):
            with patch("os.path.exists", return_value=True):
                repository_se.save_entry(expense_entry)

        # Assert
        written_content = "".join(mock_file().write.call_args_list[0][0])
        assert written_content == expected_content

    def test_add_line_to_existing_expense_entry(self, repository_se: EntryRepository) -> None:
        """Test adding a new line to an existing expense entry."""
        # Arrange
        existing_content = (
            "2024/03/21 Shopping\n  Shopping:Food                          SEK 100\n  * Assets:Checking\n\n"
        )
        new_entry = Entry(
            entry_date=date(2024, 3, 21),
            category="Shopping",
            entry_type=EntryType.EXPENSE,
            currency="SEK",
            lines=[EntryLine(amount=200, description="Shopping:Clothes")],
        )
        expected_content = (
            "2024/03/21 Shopping\n"
            "  Shopping:Food                          SEK 100\n"
            "  Shopping:Clothes                       SEK 200\n"
            "  * Assets:Checking\n"
            "\n"
        )
        mock_file = mock_open(read_data=existing_content)

        # Act & Assert
        with patch("builtins.open", mock_file):
            with patch("os.path.exists", return_value=True):
                # First read existing entries
                entries = repository_se.read_entries("se-2024-03.dat")
                # Merge entries
                merged_entry = repository_se.merge_entries(entries[0], new_entry)
                # Write back
                repository_se.save_entry(merged_entry)

        # Verify the merged entry format
        assert repository_se.format_entry(merged_entry) == expected_content

    def test_add_line_to_existing_income_entry(self, repository_es: EntryRepository) -> None:
        """Test adding a new line to an existing income entry with same description."""
        # Arrange
        existing_content = "2024/03/21 Salary\n  * Assets:Checking                      EUR 1000\n  Salary:Monthly\n\n"
        new_entry = Entry(
            entry_date=date(2024, 3, 21),
            category="Salary",
            entry_type=EntryType.INCOME,
            currency="EUR",
            lines=[EntryLine(amount=500, description="Salary:Monthly")],
        )
        expected_content = (
            "2024/03/21 Salary\n"
            "  * Assets:Checking                      EUR 1000\n"
            "  * Assets:Checking                      EUR 500\n"
            "  Salary:Monthly\n"
            "\n"
        )
        mock_file = mock_open(read_data=existing_content)

        # Act & Assert
        with patch("builtins.open", mock_file):
            with patch("os.path.exists", return_value=True):
                # First read existing entries
                entries = repository_es.read_entries("es-2024-03.dat")
                # Merge entries
                merged_entry = repository_es.merge_entries(entries[0], new_entry)
                # Write back
                repository_es.save_entry(merged_entry)

        # Verify the merged entry format
        assert repository_es.format_entry(merged_entry) == expected_content

    def test_add_line_to_income_entry_with_different_description_raises_error(
        self, repository_es: EntryRepository
    ) -> None:
        """Test that adding a line with different description to income entry raises error."""
        # Arrange
        existing_entry = Entry(
            entry_date=date(2024, 3, 21),
            category="Salary",
            entry_type=EntryType.INCOME,
            currency="EUR",
            lines=[EntryLine(amount=1000, description="Salary:Monthly")],
        )
        new_entry = Entry(
            entry_date=date(2024, 3, 21),
            category="Salary",
            entry_type=EntryType.INCOME,
            currency="EUR",
            lines=[EntryLine(amount=500, description="Salary:Bonus")],
        )

        # Act & Assert
        with pytest.raises(ValueError, match="Cannot merge income entries with different descriptions"):
            repository_es.merge_entries(existing_entry, new_entry)

    def test_multiple_expense_entries_same_date_different_categories(self, repository_se: EntryRepository) -> None:
        """Test that multiple expense entries with same date but different categories are allowed."""
        # Arrange
        existing_content = (
            "2024/03/21 Shopping\n  Shopping:Food                          SEK 100\n  * Assets:Checking\n\n"
        )
        new_entry = Entry(
            entry_date=date(2024, 3, 21),
            category="Transport",
            entry_type=EntryType.EXPENSE,
            currency="SEK",
            lines=[EntryLine(amount=200, description="Transport:Bus")],
        )
        expected_content = (
            "2024/03/21 Shopping\n"
            "  Shopping:Food                          SEK 100\n"
            "  * Assets:Checking\n"
            "\n"
            "2024/03/21 Transport\n"
            "  Transport:Bus                          SEK 200\n"
            "  * Assets:Checking\n"
            "\n"
        )
        mock_file = mock_open(read_data=existing_content)

        # Act & Assert
        with patch("builtins.open", mock_file):
            with patch("os.path.exists", return_value=True):
                repository_se.save_entry(new_entry)

        # Verify content
        written_content = "".join(mock_file().write.call_args_list[0][0])
        assert written_content == expected_content

    def test_multiple_income_entries_same_date_raises_error(self, repository_es: EntryRepository) -> None:
        """Test that multiple income entries with same date raise error."""
        # Arrange
        existing_content = "2024/03/21 Salary\n  * Assets:Checking                      EUR 1000\n  Salary:Monthly\n\n"
        new_entry = Entry(
            entry_date=date(2024, 3, 21),
            category="Bonus",
            entry_type=EntryType.INCOME,
            currency="EUR",
            lines=[EntryLine(amount=500, description="Salary:Bonus")],
        )
        mock_file = mock_open(read_data=existing_content)

        # Act & Assert
        with patch("builtins.open", mock_file):
            with patch("os.path.exists", return_value=True):
                with pytest.raises(ValueError, match="Cannot have multiple income entries for the same date"):
                    repository_es.save_entry(new_entry)

    def test_currency_must_match_country_code(self) -> None:
        """Test that currency must match the country code."""
        # Arrange
        repository = EntryRepository(data_dir=".", country_code="se")
        entry = Entry(
            entry_date=date(2024, 3, 21),
            category="Test",
            entry_type=EntryType.EXPENSE,
            currency="EUR",
            lines=[EntryLine(amount=100, description="Test:Entry")],
        )

        # Act & Assert
        with pytest.raises(ValueError, match="Invalid currency EUR for country se. Expected SEK"):
            repository.validate_entries([entry])

    def test_save_entry_automatically_merges_matching_entries(self, repository_se: EntryRepository) -> None:
        """Test that save_entry automatically merges entries with same date and category."""
        # Arrange
        first_entry = Entry(
            entry_date=date(2024, 3, 21),
            category="Food",
            entry_type=EntryType.EXPENSE,
            currency="SEK",
            lines=[EntryLine(amount=100, description="Food:Lunch")],
        )
        second_entry = Entry(
            entry_date=date(2024, 3, 21),
            category="Food",
            entry_type=EntryType.EXPENSE,
            currency="SEK",
            lines=[EntryLine(amount=200, description="Food:Dinner")],
        )
        expected_content = (
            "2024/03/21 Food\n"
            "  Food:Lunch                             SEK 100\n"
            "  Food:Dinner                            SEK 200\n"
            "  * Assets:Checking\n"
            "\n"
        )
        mock_file = mock_open()

        # Act
        with patch("builtins.open", mock_file):
            with patch("os.path.exists", return_value=True):
                # Mock reading the first entry when saving the second
                with patch.object(repository_se, "read_entries", return_value=[first_entry]):
                    repository_se.save_entry(second_entry)

        # Assert
        mock_file().write.assert_called_once()
        written_content = "".join(mock_file().write.call_args_list[0][0])
        assert written_content == expected_content

    def test_read_entries_with_comments(self, repository_se: EntryRepository) -> None:
        """Test that comments in .dat files are properly ignored."""
        # Arrange
        content = (
            "; This is a comment at the start of file\n"
            "2024/03/21 Shopping\n"
            "  ; Comment before entry line\n"
            "  Shopping:Food                          SEK 100\n"
            "  ; Another comment\n"
            "  Shopping:Clothes                       SEK 200\n"
            "  * Assets:Checking\n"
            "\n"
            "; Comment between entries\n"
            "2024/03/20 Food\n"
            "  Food:Lunch                            SEK 50\n"
            "  * Assets:Checking\n"
            "\n"
        )
        mock_file = mock_open(read_data=content)

        # Act
        with patch("builtins.open", mock_file):
            entries = repository_se.read_entries("se-2024-03.dat")

        # Assert
        assert len(entries) == 2
        # First entry
        assert entries[0].entry_date == date(2024, 3, 21)
        assert entries[0].category == "Shopping"
        assert len(entries[0].lines) == 2
        assert entries[0].lines[0].amount == 100
        assert entries[0].lines[0].description == "Shopping:Food"
        assert entries[0].lines[1].amount == 200
        assert entries[0].lines[1].description == "Shopping:Clothes"
        # Second entry
        assert entries[1].entry_date == date(2024, 3, 20)
        assert entries[1].category == "Food"
        assert len(entries[1].lines) == 1
        assert entries[1].lines[0].amount == 50
        assert entries[1].lines[0].description == "Food:Lunch"
