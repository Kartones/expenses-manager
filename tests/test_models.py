from datetime import date
import pytest

from src.expenses.models import EntryLine, Entry, InvalidEntryLineError, InvalidEntryError, EntryType


class TestEntryLine:
    def test_valid_entry_line_creation(self) -> None:
        """Test creating a valid entry line with correct format."""
        # Arrange
        amount = 100
        description = "Shopping:Food"

        # Act
        entry_line = EntryLine(amount=amount, description=description)

        # Assert
        assert entry_line.amount == amount
        assert entry_line.description == description
        assert entry_line.comments == []

    def test_entry_line_with_single_comment(self) -> None:
        """Test creating an entry line with a single comment."""
        # Arrange
        amount = 100
        description = "Shopping:Food"
        comments = ["; A simple comment"]

        # Act
        entry_line = EntryLine(amount=amount, description=description, comments=comments)

        # Assert
        assert entry_line.comments == comments

    def test_entry_line_with_multiple_comments(self) -> None:
        """Test creating an entry line with multiple comments."""
        # Arrange
        amount = 100
        description = "Shopping:Food"
        comments = ["; First comment", "  ; Indented comment", ";Last comment"]

        # Act
        entry_line = EntryLine(amount=amount, description=description, comments=comments)

        # Assert
        assert entry_line.comments == comments

    def test_entry_line_invalid_comments_type_raises_error(self) -> None:
        """Test that invalid comments type raises an error."""
        with pytest.raises(InvalidEntryLineError, match="Comments must be a list of strings"):
            EntryLine(amount=100, description="Test", comments="not a list")  # type: ignore

    def test_entry_line_invalid_comment_items_raises_error(self) -> None:
        """Test that non-string comments raise an error."""
        with pytest.raises(InvalidEntryLineError, match="Comments must be a list of strings"):
            EntryLine(amount=100, description="Test", comments=["; valid", 42])  # type: ignore

    def test_invalid_amount_raises_error(self) -> None:
        """Test that negative amounts raise an error."""
        with pytest.raises(InvalidEntryLineError, match="Amount must be greater than or equal to 0"):
            EntryLine(amount=-100, description="Test")

    def test_zero_amount_is_valid(self) -> None:
        """Test that zero amount is valid."""
        entry_line = EntryLine(amount=0, description="Test")
        assert entry_line.amount == 0

    def test_invalid_description_format_raises_error(self) -> None:
        """Test that descriptions with spaces raise an error."""
        with pytest.raises(InvalidEntryLineError, match="Description cannot contain spaces"):
            EntryLine(amount=100, description="Test Description")

    def test_empty_description_raises_error(self) -> None:
        """Test that empty description raises an error."""
        with pytest.raises(InvalidEntryLineError, match="Description cannot be empty"):
            EntryLine(amount=100, description="")

    def test_description_with_multiple_colons(self) -> None:
        """Test that description can have multiple colon-separated parts."""
        entry_line = EntryLine(amount=100, description="Shopping:Food:Groceries")
        assert entry_line.description == "Shopping:Food:Groceries"


class TestEntry:
    def test_valid_expense_entry_creation(self) -> None:
        """Test creating a valid expense entry."""
        # Arrange
        entry_date = date(2024, 3, 21)
        category = "Shopping"
        lines = [
            EntryLine(amount=100, description="Shopping:Food"),
            EntryLine(amount=200, description="Shopping:Clothes"),
        ]

        # Act
        entry = Entry(
            entry_date=entry_date, category=category, entry_type=EntryType.EXPENSE, currency="SEK", lines=lines
        )

        # Assert
        assert entry.entry_date == entry_date
        assert entry.category == category
        assert entry.entry_type == EntryType.EXPENSE
        assert entry.currency == "SEK"
        assert entry.lines == lines
        assert entry.comments == []

    def test_valid_income_entry_creation(self) -> None:
        """Test creating a valid income entry with same descriptions."""
        # Arrange
        entry_date = date(2024, 3, 21)
        category = "Salary"
        lines = [
            EntryLine(amount=1000, description="Salary:Monthly"),
            EntryLine(amount=500, description="Salary:Monthly"),
        ]

        # Act
        entry = Entry(
            entry_date=entry_date, category=category, entry_type=EntryType.INCOME, currency="EUR", lines=lines
        )

        # Assert
        assert entry.entry_date == entry_date
        assert entry.category == category
        assert entry.entry_type == EntryType.INCOME
        assert entry.currency == "EUR"
        assert entry.lines == lines

    def test_income_entry_with_different_descriptions_raises_error(self) -> None:
        """Test that income entries must have same description for all lines."""
        with pytest.raises(InvalidEntryError, match="Income entries must have same description for all lines"):
            Entry(
                entry_date=date(2024, 3, 21),
                category="Income",
                entry_type=EntryType.INCOME,
                currency="SEK",
                lines=[
                    EntryLine(amount=1000, description="Salary:Monthly"),
                    EntryLine(amount=500, description="Bonus:Yearly"),
                ],
            )

    def test_invalid_currency_raises_error(self) -> None:
        """Test that only SEK and EUR are valid currencies."""
        with pytest.raises(InvalidEntryError, match="Currency must be either SEK or EUR"):
            Entry(
                entry_date=date(2024, 3, 21),
                category="Test",
                entry_type=EntryType.EXPENSE,
                currency="USD",
                lines=[EntryLine(amount=100, description="Test")],
            )

    def test_empty_lines_raises_error(self) -> None:
        """Test that entries must have at least one line."""
        with pytest.raises(InvalidEntryError, match="Entry must have at least one line"):
            Entry(entry_date=date(2024, 3, 21), category="Test", entry_type=EntryType.EXPENSE, currency="SEK", lines=[])

    def test_category_with_spaces_is_valid(self) -> None:
        """Test that categories can contain spaces."""
        # Arrange
        entry_date = date(2024, 3, 21)
        category = "Food and Drinks"
        lines = [EntryLine(amount=100, description="Food:Groceries")]

        # Act
        entry = Entry(
            entry_date=entry_date, category=category, entry_type=EntryType.EXPENSE, currency="SEK", lines=lines
        )

        # Assert
        assert entry.category == "Food and Drinks"

    def test_entry_with_comments(self) -> None:
        """Test creating an entry with comments."""
        # Arrange
        entry_date = date(2024, 3, 21)
        category = "Shopping"
        lines = [EntryLine(amount=100, description="Shopping:Food")]
        comments = ["; Entry comment", "  ; Another comment"]

        # Act
        entry = Entry(
            entry_date=entry_date,
            category=category,
            entry_type=EntryType.EXPENSE,
            currency="SEK",
            lines=lines,
            comments=comments,
        )

        # Assert
        assert entry.comments == comments

    def test_entry_with_line_and_entry_comments(self) -> None:
        """Test creating an entry with both entry and line comments."""
        # Arrange
        entry_date = date(2024, 3, 21)
        category = "Shopping"
        lines = [
            EntryLine(amount=100, description="Shopping:Food", comments=["; Line comment"]),
            EntryLine(amount=200, description="Shopping:Clothes"),
        ]
        entry_comments = ["; Entry comment"]

        # Act
        entry = Entry(
            entry_date=entry_date,
            category=category,
            entry_type=EntryType.EXPENSE,
            currency="SEK",
            lines=lines,
            comments=entry_comments,
        )

        # Assert
        assert entry.comments == entry_comments
        assert entry.lines[0].comments == ["; Line comment"]
        assert entry.lines[1].comments == []

    def test_entry_invalid_comments_type_raises_error(self) -> None:
        """Test that invalid comments type raises an error."""
        with pytest.raises(InvalidEntryError, match="Comments must be a list of strings"):
            Entry(
                entry_date=date(2024, 3, 21),
                category="Test",
                entry_type=EntryType.EXPENSE,
                currency="SEK",
                lines=[EntryLine(amount=100, description="Test")],
                comments="not a list",  # type: ignore
            )

    def test_entry_invalid_comment_items_raises_error(self) -> None:
        """Test that non-string comments raise an error."""
        with pytest.raises(InvalidEntryError, match="Comments must be a list of strings"):
            Entry(
                entry_date=date(2024, 3, 21),
                category="Test",
                entry_type=EntryType.EXPENSE,
                currency="SEK",
                lines=[EntryLine(amount=100, description="Test")],
                comments=["; valid", 42],  # type: ignore
            )
