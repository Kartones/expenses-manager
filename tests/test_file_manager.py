from datetime import date
from pathlib import Path
import pytest  # type: ignore

from expenses.file_manager import FileManager  # type: ignore
from expenses.models import (  # type: ignore
    ExpenseEntry,
    ExpenseItem,
    IncomeEntry,
    IncomeItem,
    InvalidAmountError,
    InvalidDescriptionError,
)


def test_generate_filename_for_date() -> None:
    # Given
    test_date = date(2024, 3, 21)
    file_manager = FileManager()  # Default country "se"

    # When
    filename = file_manager.generate_filename(test_date)

    # Assert
    assert filename == "se-2024-03.dat"


def test_generate_filename_for_date_with_country() -> None:
    # Given
    test_date = date(2024, 3, 21)
    file_manager = FileManager(country="es")

    # When
    filename = file_manager.generate_filename(test_date)

    # Assert
    assert filename == "es-2024-03.dat"


def test_write_expense_entry(tmp_path: Path) -> None:
    # Given
    test_date = date(2024, 3, 21)
    expense_entry = ExpenseEntry(
        date=test_date,
        category="Shopping",
        items=[ExpenseItem(description="weekly:groceries", amount=100)],
    )
    file_manager = FileManager()

    # When
    file_manager.write_entry(tmp_path, expense_entry)

    # Then
    expected_filename = tmp_path / file_manager.generate_filename(test_date)
    assert expected_filename.exists()

    content = expected_filename.read_text()
    expected_content = "2024/03/21 Shopping\n  weekly:groceries                     kr 100\n  * Assets:Checking\n"
    assert content == expected_content


def test_append_expense_entry(tmp_path: Path) -> None:
    # Given
    file_manager = FileManager()

    # First entry
    first_entry = ExpenseEntry(
        date=date(2024, 3, 21),
        category="Shopping",
        items=[ExpenseItem(description="weekly:groceries", amount=100)],
    )
    file_manager.write_entry(tmp_path, first_entry)

    # Second entry
    second_entry = ExpenseEntry(
        date=date(2024, 3, 21),
        category="Shopping",
        items=[ExpenseItem(description="weekly:groceries", amount=150)],
    )

    # When
    file_manager.write_entry(tmp_path, second_entry)

    # Then
    expected_filename = tmp_path / file_manager.generate_filename(first_entry.date)
    assert expected_filename.exists()

    content = expected_filename.read_text()
    expected_content = (
        "2024/03/21 Shopping\n"
        "  weekly:groceries                     kr 100\n"
        "  * Assets:Checking\n"
        "\n"
        "2024/03/21 Shopping\n"
        "  weekly:groceries                     kr 150\n"
        "  * Assets:Checking\n"
    )
    assert content == expected_content


def test_write_income_entry(tmp_path: Path) -> None:
    # Given
    test_date = date(2024, 3, 21)
    income_entry = IncomeEntry(
        date=test_date,
        category="Salary",
        description="monthly:salary",
        items=[IncomeItem(amount=25000)],
    )
    file_manager = FileManager()

    # When
    file_manager.write_entry(tmp_path, income_entry)

    # Then
    expected_filename = tmp_path / file_manager.generate_filename(test_date)
    assert expected_filename.exists()

    content = expected_filename.read_text()
    expected_content = "2024/03/21 Salary\n  * Assets:Checking                    kr 25000\n  monthly:salary\n"
    assert content == expected_content


def test_append_income_entry(tmp_path: Path) -> None:
    # Given
    file_manager = FileManager()

    # First entry
    first_entry = IncomeEntry(
        date=date(2024, 3, 21),
        category="Salary",
        description="monthly:salary",
        items=[IncomeItem(amount=25000)],
    )
    file_manager.write_entry(tmp_path, first_entry)

    # Second entry
    second_entry = IncomeEntry(
        date=date(2024, 3, 21),
        category="Salary",
        description="monthly:bonus",
        items=[IncomeItem(amount=5000)],
    )

    # When
    file_manager.write_entry(tmp_path, second_entry)

    # Then
    expected_filename = tmp_path / file_manager.generate_filename(first_entry.date)
    assert expected_filename.exists()

    content = expected_filename.read_text()
    expected_content = (
        "2024/03/21 Salary\n"
        "  * Assets:Checking                    kr 25000\n"
        "  monthly:salary\n"
        "\n"
        "2024/03/21 Salary\n"
        "  * Assets:Checking                    kr 5000\n"
        "  monthly:bonus\n"
    )
    assert content == expected_content


def test_mix_expense_and_income_entries(tmp_path: Path) -> None:
    # Given
    file_manager = FileManager()

    # First entry (expense)
    expense_entry = ExpenseEntry(
        date=date(2024, 3, 21),
        category="Shopping",
        items=[ExpenseItem(description="weekly:groceries", amount=100)],
    )
    file_manager.write_entry(tmp_path, expense_entry)

    # Second entry (income)
    income_entry = IncomeEntry(
        date=date(2024, 3, 21),
        category="Salary",
        description="monthly:salary",
        items=[IncomeItem(amount=25000)],
    )

    # When
    file_manager.write_entry(tmp_path, income_entry)

    # Then
    expected_filename = tmp_path / file_manager.generate_filename(expense_entry.date)
    assert expected_filename.exists()

    content = expected_filename.read_text()
    expected_content = (
        "2024/03/21 Shopping\n"
        "  weekly:groceries                     kr 100\n"
        "  * Assets:Checking\n"
        "\n"
        "2024/03/21 Salary\n"
        "  * Assets:Checking                    kr 25000\n"
        "  monthly:salary\n"
    )
    assert content == expected_content


def test_expense_entry_with_multiple_items(tmp_path: Path) -> None:
    # Given
    test_date = date(2024, 3, 21)
    expense_entry = ExpenseEntry(
        date=test_date,
        category="Shopping",
        items=[
            ExpenseItem(description="weekly:groceries", amount=100),
            ExpenseItem(description="household:items", amount=46),
            ExpenseItem(description="drinks:and:snacks", amount=24),
        ],
    )
    file_manager = FileManager()

    # When
    file_manager.write_entry(tmp_path, expense_entry)

    # Then
    expected_filename = tmp_path / file_manager.generate_filename(test_date)
    assert expected_filename.exists()

    content = expected_filename.read_text()
    expected_content = (
        "2024/03/21 Shopping\n"
        "  weekly:groceries                     kr 100\n"
        "  household:items                      kr 46\n"
        "  drinks:and:snacks                    kr 24\n"
        "  * Assets:Checking\n"
    )
    assert content == expected_content


def test_income_entry_with_multiple_items(tmp_path: Path) -> None:
    # Given
    test_date = date(2024, 3, 21)
    income_entry = IncomeEntry(
        date=test_date,
        category="Salary",
        description="monthly:compensation",
        items=[
            IncomeItem(amount=25000),
            IncomeItem(amount=5000),
            IncomeItem(amount=2500),
        ],
    )
    file_manager = FileManager()

    # When
    file_manager.write_entry(tmp_path, income_entry)

    # Then
    expected_filename = tmp_path / file_manager.generate_filename(test_date)
    assert expected_filename.exists()

    content = expected_filename.read_text()
    expected_content = (
        "2024/03/21 Salary\n"
        "  * Assets:Checking                    kr 25000\n"
        "  * Assets:Checking                    kr 5000\n"
        "  * Assets:Checking                    kr 2500\n"
        "  monthly:compensation\n"
    )
    assert content == expected_content


def test_expense_entry_with_zero_amount_fails() -> None:
    # When/Then
    with pytest.raises(InvalidAmountError, match="Expense amount must be greater than zero"):
        ExpenseItem(description="cancelled:item", amount=0)


def test_income_entry_with_zero_amount_fails() -> None:
    # When/Then
    with pytest.raises(InvalidAmountError, match="Income amount must be greater than zero"):
        IncomeItem(amount=0)


def test_expense_entry_with_negative_amount_fails() -> None:
    # When/Then
    with pytest.raises(InvalidAmountError, match="Expense amount must be greater than zero"):
        ExpenseItem(description="refund:amount", amount=-50)


def test_income_entry_with_negative_amount_fails() -> None:
    # When/Then
    with pytest.raises(InvalidAmountError, match="Income amount must be greater than zero"):
        IncomeItem(amount=-100)


def test_expense_item_with_spaces_in_description_fails() -> None:
    # When/Then
    with pytest.raises(InvalidDescriptionError, match=r"Description must use colons \(\:\) instead of spaces"):
        ExpenseItem(description="invalid description with spaces", amount=100)


def test_income_entry_with_spaces_in_description_fails() -> None:
    # When/Then
    with pytest.raises(InvalidDescriptionError, match=r"Description must use colons \(\:\) instead of spaces"):
        IncomeEntry(
            date=date(2024, 3, 21),
            category="Salary",
            description="invalid description with spaces",
            items=[IncomeItem(amount=100)],
        )


def test_entry_with_spaces_in_category_fails() -> None:
    # When/Then
    with pytest.raises(InvalidDescriptionError, match=r"Category must use colons \(\:\) instead of spaces"):
        ExpenseEntry(
            date=date(2024, 3, 21),
            category="Invalid Category",
            items=[ExpenseItem(description="valid:description", amount=100)],
        )
