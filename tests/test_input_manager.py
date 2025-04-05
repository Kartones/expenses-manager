from datetime import date
from unittest.mock import patch
import pytest


from expenses.input_manager import InputManager
from expenses.models import ExpenseEntry, IncomeEntry


def test_capture_expense_entry() -> None:
    # Given
    input_manager = InputManager()
    test_date = date(2024, 3, 21)
    test_inputs = [
        "expense",  # Entry type
        "2024-03-21",  # Date
        "Shopping",  # Category
        "weekly:groceries",  # Description
        "100",  # Amount
        "n",  # No more items
    ]

    # When
    with patch("builtins.input", side_effect=test_inputs):
        entry = input_manager.capture_entry()

    # Then
    assert isinstance(entry, ExpenseEntry)
    assert entry.date == test_date
    assert entry.category == "Shopping"
    assert len(entry.items) == 1
    assert entry.items[0].description == "weekly:groceries"
    assert entry.items[0].amount == 100
    assert entry.items[0].currency == "kr"


def test_set_country_spanish() -> None:
    # Given
    input_manager = InputManager()
    test_inputs = ["es"]  # Spanish country code

    # When
    with patch("builtins.input", side_effect=test_inputs):
        input_manager.set_country()

    # Then
    assert input_manager.country == "es"
    assert input_manager.currency == "€"


def test_set_country_swedish() -> None:
    # Given
    input_manager = InputManager()
    test_inputs = ["se"]  # Swedish country code

    # When
    with patch("builtins.input", side_effect=test_inputs):
        input_manager.set_country()

    # Then
    assert input_manager.country == "se"
    assert input_manager.currency == "kr"


def test_set_country_default() -> None:
    # Given
    input_manager = InputManager()
    test_inputs = [""]  # Empty input for default

    # When
    with patch("builtins.input", side_effect=test_inputs):
        input_manager.set_country()

    # Then
    assert input_manager.country == "se"
    assert input_manager.currency == "kr"


def test_set_country_invalid_retries() -> None:
    # Given
    input_manager = InputManager()
    test_inputs = [
        "fr",  # Invalid country
        "uk",  # Invalid country
        "se",  # Valid country
    ]

    # When
    with patch("builtins.input", side_effect=test_inputs):
        input_manager.set_country()

    # Then
    assert input_manager.country == "se"
    assert input_manager.currency == "kr"


def test_capture_expense_entry_with_spanish_country() -> None:
    # Given
    input_manager = InputManager()
    test_date = date(2024, 3, 21)

    # Set country first
    with patch("builtins.input", side_effect=["es"]):
        input_manager.set_country()

    test_inputs = [
        "expense",  # Entry type
        "2024-03-21",  # Date
        "Shopping",  # Category
        "weekly:groceries",  # Description
        "100",  # Amount
        "n",  # No more items
    ]

    # When
    with patch("builtins.input", side_effect=test_inputs):
        entry = input_manager.capture_entry()

    # Then
    assert isinstance(entry, ExpenseEntry)
    assert entry.date == test_date
    assert entry.category == "Shopping"
    assert len(entry.items) == 1
    assert entry.items[0].description == "weekly:groceries"
    assert entry.items[0].amount == 100
    assert entry.items[0].currency == "€"
    assert input_manager.country == "es"


def test_capture_income_entry() -> None:
    # Given
    input_manager = InputManager()
    test_date = date(2024, 3, 21)

    # Set country first
    with patch("builtins.input", side_effect=["se"]):
        input_manager.set_country()

    test_inputs = [
        "income",  # Entry type
        "2024-03-21",  # Date
        "Salary",  # Category
        "monthly:salary",  # Description
        "25000",  # Amount
        "n",  # No more items
    ]

    # When
    with patch("builtins.input", side_effect=test_inputs):
        entry = input_manager.capture_entry()

    # Then
    assert isinstance(entry, IncomeEntry)
    assert entry.date == test_date
    assert entry.category == "Salary"
    assert entry.description == "monthly:salary"
    assert len(entry.items) == 1
    assert entry.items[0].amount == 25000
    assert entry.items[0].currency == "kr"
    assert input_manager.country == "se"


def test_capture_income_entry_with_spanish_country() -> None:
    # Given
    input_manager = InputManager()
    test_date = date(2024, 3, 21)

    # Set country first
    with patch("builtins.input", side_effect=["es"]):
        input_manager.set_country()

    test_inputs = [
        "income",  # Entry type
        "2024-03-21",  # Date
        "Salary",  # Category
        "monthly:salary",  # Description
        "25000",  # Amount
        "n",  # No more items
    ]

    # When
    with patch("builtins.input", side_effect=test_inputs):
        entry = input_manager.capture_entry()

    # Then
    assert isinstance(entry, IncomeEntry)
    assert entry.date == test_date
    assert entry.category == "Salary"
    assert entry.description == "monthly:salary"
    assert len(entry.items) == 1
    assert entry.items[0].amount == 25000
    assert entry.items[0].currency == "€"
    assert input_manager.country == "es"


def test_invalid_country_retries() -> None:
    # Given
    input_manager = InputManager()

    # Set country first with retries
    with patch("builtins.input", side_effect=["fr", "uk", "se"]):
        input_manager.set_country()

    test_inputs = [
        "expense",  # Entry type
        "2024-03-21",  # Date
        "Shopping",  # Category
        "weekly:groceries",  # Description
        "100",  # Amount
        "n",  # No more items
    ]

    # When
    with patch("builtins.input", side_effect=test_inputs):
        entry = input_manager.capture_entry()

    # Then
    assert isinstance(entry, ExpenseEntry)
    assert entry.items[0].currency == "kr"
    assert input_manager.country == "se"


def test_default_country_selection() -> None:
    # Given
    input_manager = InputManager()

    # Set country first with default
    with patch("builtins.input", side_effect=[""]):
        input_manager.set_country()

    test_inputs = [
        "expense",  # Entry type
        "2024-03-21",  # Date
        "Shopping",  # Category
        "weekly:groceries",  # Description
        "100",  # Amount
        "n",  # No more items
    ]

    # When
    with patch("builtins.input", side_effect=test_inputs):
        entry = input_manager.capture_entry()

    # Then
    assert isinstance(entry, ExpenseEntry)
    assert entry.items[0].currency == "kr"
    assert input_manager.country == "se"


def test_invalid_entry_type_raises_error() -> None:
    # Given
    input_manager = InputManager()
    test_inputs = [
        "se",  # Country
        "invalid",  # Invalid entry type
    ]

    # When/Then
    with patch("builtins.input", side_effect=test_inputs):
        with pytest.raises(ValueError, match="Invalid entry type"):
            input_manager.capture_entry()


def test_invalid_date_format_retries() -> None:
    # Given
    input_manager = InputManager()

    # Set country first
    with patch("builtins.input", side_effect=["se"]):
        input_manager.set_country()

    test_inputs = [
        "expense",  # Entry type
        "invalid-date",  # Invalid date format
        "2024-03-21",  # Valid date
        "Shopping",  # Category
        "weekly:groceries",  # Description
        "100",  # Amount
        "n",  # No more items
    ]

    # When
    with patch("builtins.input", side_effect=test_inputs):
        entry = input_manager.capture_entry()

    # Then
    assert isinstance(entry, ExpenseEntry)
    assert entry.date == date(2024, 3, 21)
    assert entry.items[0].currency == "kr"


def test_spaces_in_category_retries() -> None:
    # Given
    input_manager = InputManager()

    # Set country first
    with patch("builtins.input", side_effect=["se"]):
        input_manager.set_country()

    test_inputs = [
        "expense",  # Entry type
        "2024-03-21",  # Date
        "Grocery Shopping",  # Category with spaces (now valid)
        "weekly:groceries",  # Description
        "100",  # Amount
        "n",  # No more items
    ]

    # When
    with patch("builtins.input", side_effect=test_inputs):
        entry = input_manager.capture_entry()

    # Then
    assert isinstance(entry, ExpenseEntry)
    assert entry.category == "Grocery Shopping"
    assert entry.items[0].currency == "kr"


def test_spaces_in_description_retries() -> None:
    # Given
    input_manager = InputManager()

    # Set country first
    with patch("builtins.input", side_effect=["se"]):
        input_manager.set_country()

    test_inputs = [
        "expense",  # Entry type
        "2024-03-21",  # Date
        "Shopping",  # Category
        "Invalid Description",  # Invalid description with spaces
        "valid:description",  # Valid description with colons
        "100",  # Amount
        "n",  # No more items
    ]

    # When
    with patch("builtins.input", side_effect=test_inputs):
        entry = input_manager.capture_entry()

    # Then
    assert isinstance(entry, ExpenseEntry)
    assert entry.items[0].description == "valid:description"
    assert entry.items[0].currency == "kr"


def test_invalid_amount_retries() -> None:
    # Given
    input_manager = InputManager()

    # Set country first
    with patch("builtins.input", side_effect=["se"]):
        input_manager.set_country()

    test_inputs = [
        "expense",  # Entry type
        "2024-03-21",  # Date
        "Shopping",  # Category
        "weekly:groceries",  # Description
        "invalid",  # Invalid amount
        "-50",  # Negative amount
        "0",  # Zero amount
        "100",  # Valid amount
        "n",  # No more items
    ]

    # When
    with patch("builtins.input", side_effect=test_inputs):
        entry = input_manager.capture_entry()

    # Then
    assert isinstance(entry, ExpenseEntry)
    assert entry.items[0].amount == 100
    assert entry.items[0].currency == "kr"


def test_decimal_amount_retries() -> None:
    # Given
    input_manager = InputManager()

    # Set country first
    with patch("builtins.input", side_effect=["se"]):
        input_manager.set_country()

    test_inputs = [
        "expense",  # Entry type
        "2024-03-21",  # Date
        "Shopping",  # Category
        "weekly:groceries",  # Description
        "100.50",  # Decimal amount
        "100",  # Valid integer amount
        "n",  # No more items
    ]

    # When
    with patch("builtins.input", side_effect=test_inputs):
        entry = input_manager.capture_entry()

    # Then
    assert isinstance(entry, ExpenseEntry)
    assert entry.items[0].amount == 100
    assert entry.items[0].currency == "kr"


def test_spaces_in_income_description_retries() -> None:
    # Given
    input_manager = InputManager()

    # Set country first
    with patch("builtins.input", side_effect=["se"]):
        input_manager.set_country()

    test_inputs = [
        "income",  # Entry type
        "2024-03-21",  # Date
        "Salary",  # Category
        "Invalid Description",  # Invalid description with spaces
        "monthly:salary",  # Valid description with colons
        "25000",  # Amount
        "n",  # No more items
    ]

    # When
    with patch("builtins.input", side_effect=test_inputs):
        entry = input_manager.capture_entry()

    # Then
    assert isinstance(entry, IncomeEntry)
    assert entry.description == "monthly:salary"
    assert entry.items[0].currency == "kr"
