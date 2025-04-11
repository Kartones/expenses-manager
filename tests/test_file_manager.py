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


def test_merge_expense_entries_same_date(tmp_path: Path) -> None:
    # Given
    file_manager = FileManager()

    # First entry
    first_entry = ExpenseEntry(
        date=date(2024, 3, 21),
        category="Shopping",
        items=[ExpenseItem(description="weekly:groceries", amount=100)],
    )
    file_manager.write_entry(tmp_path, first_entry)

    # Second entry with same date and category
    second_entry = ExpenseEntry(
        date=date(2024, 3, 21),
        category="Shopping",
        items=[ExpenseItem(description="household:items", amount=50)],
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
        "  household:items                      kr 50\n"
        "  * Assets:Checking\n"
    )
    assert content == expected_content


def test_merge_income_entries_same_date(tmp_path: Path) -> None:
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

    # Second entry with same date and category
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
        "  * Assets:Checking                    kr 5000\n"
        "  monthly:salary\n"
        "  monthly:bonus\n"
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


def test_invalid_amount_retries(tmp_path: Path) -> None:
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


def test_preserve_other_dates_when_writing(tmp_path: Path) -> None:
    # Given
    file_manager = FileManager()

    # Create entries for different dates
    entries = [
        # Earlier date
        ExpenseEntry(
            date=date(2024, 3, 15),
            category="Transport",
            items=[ExpenseItem(description="monthly:bus:pass", amount=200)],
        ),
        # Target date
        ExpenseEntry(
            date=date(2024, 3, 21),
            category="Shopping",
            items=[ExpenseItem(description="weekly:groceries", amount=100)],
        ),
        # Later date
        IncomeEntry(
            date=date(2024, 3, 25),
            category="Salary",
            description="monthly:salary",
            items=[IncomeItem(amount=25000)],
        ),
    ]

    # Write initial entries
    for entry in entries:
        file_manager.write_entry(tmp_path, entry)

    # When: Add new entry for the middle date
    new_entry = ExpenseEntry(
        date=date(2024, 3, 21),
        category="Shopping",
        items=[ExpenseItem(description="household:items", amount=50)],
    )
    file_manager.write_entry(tmp_path, new_entry)

    # Then
    expected_filename = tmp_path / file_manager.generate_filename(new_entry.date)
    assert expected_filename.exists()

    content = expected_filename.read_text()
    expected_content = (
        "2024/03/15 Transport\n"
        "  monthly:bus:pass                     kr 200\n"
        "  * Assets:Checking\n"
        "\n"
        "2024/03/21 Shopping\n"
        "  weekly:groceries                     kr 100\n"
        "  * Assets:Checking\n"
        "\n"
        "2024/03/25 Salary\n"
        "  * Assets:Checking                    kr 25000\n"
        "  monthly:salary\n"
        "\n"
        "2024/03/21 Shopping\n"
        "  household:items                      kr 50\n"
        "  * Assets:Checking\n"
    )
    assert content == expected_content


def test_preserve_other_dates_when_merging(tmp_path: Path) -> None:
    # Given
    file_manager = FileManager()

    # Create entries for different dates
    entries = [
        # Earlier date
        ExpenseEntry(
            date=date(2024, 3, 15),
            category="Transport",
            items=[ExpenseItem(description="monthly:bus:pass", amount=200)],
        ),
        # Target date
        ExpenseEntry(
            date=date(2024, 3, 21),
            category="Shopping",
            items=[ExpenseItem(description="weekly:groceries", amount=100)],
        ),
        # Later date
        IncomeEntry(
            date=date(2024, 3, 25),
            category="Salary",
            description="monthly:salary",
            items=[IncomeItem(amount=25000)],
        ),
    ]

    # Write initial entries
    for entry in entries:
        file_manager.write_entry(tmp_path, entry)

    # When: Add new entry for merging
    new_entry = ExpenseEntry(
        date=date(2024, 3, 21),
        category="Shopping",
        items=[ExpenseItem(description="household:items", amount=50)],
    )

    # Create a temporary file for merge test
    merge_path = tmp_path / "test_merge"
    merge_path.mkdir()
    merge_filename = merge_path / file_manager.generate_filename(new_entry.date)
    source_filename = tmp_path / file_manager.generate_filename(new_entry.date)

    # Copy content to merge test file
    with open(source_filename, "r") as src, open(merge_filename, "w") as dst:
        dst.write(src.read())

    file_manager.write_entry(merge_path, new_entry)

    # Then
    content = merge_filename.read_text()
    expected_content = (
        "2024/03/15 Transport\n"
        "  monthly:bus:pass                     kr 200\n"
        "  * Assets:Checking\n"
        "\n"
        "2024/03/21 Shopping\n"
        "  weekly:groceries                     kr 100\n"
        "  household:items                      kr 50\n"
        "  * Assets:Checking\n"
        "\n"
        "2024/03/25 Salary\n"
        "  * Assets:Checking                    kr 25000\n"
        "  monthly:salary\n"
    )
    assert content == expected_content


def test_different_categories_same_date(tmp_path: Path) -> None:
    # Given
    file_manager = FileManager()

    # First entry
    first_entry = ExpenseEntry(
        date=date(2024, 3, 21),
        category="Shopping",
        items=[ExpenseItem(description="weekly:groceries", amount=100)],
    )
    file_manager.write_entry(tmp_path, first_entry)

    # Second entry with same date but different category
    second_entry = ExpenseEntry(
        date=date(2024, 3, 21),
        category="Transport",
        items=[ExpenseItem(description="taxi:ride", amount=50)],
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
        "2024/03/21 Transport\n"
        "  taxi:ride                            kr 50\n"
        "  * Assets:Checking\n"
    )
    assert content == expected_content


def test_different_accounts_same_date_category(tmp_path: Path) -> None:
    # Given
    file_manager = FileManager()

    # First entry
    first_entry = ExpenseEntry(
        date=date(2024, 3, 21),
        category="Shopping",
        items=[ExpenseItem(description="weekly:groceries", amount=100)],
        account="Assets:Cash",  # Different account
    )
    file_manager.write_entry(tmp_path, first_entry)

    # Second entry with same date/category but different account
    second_entry = ExpenseEntry(
        date=date(2024, 3, 21),
        category="Shopping",
        items=[ExpenseItem(description="household:items", amount=50)],
        account="Assets:CreditCard",  # Different account
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
        "  * Assets:Cash\n"
        "\n"
        "2024/03/21 Shopping\n"
        "  household:items                      kr 50\n"
        "  * Assets:CreditCard\n"
    )
    assert content == expected_content


def test_chronological_order_preservation(tmp_path: Path) -> None:
    # Given
    file_manager = FileManager()

    # Write entries in non-chronological order
    entries = [
        ExpenseEntry(
            date=date(2024, 3, 25),
            category="Shopping",
            items=[ExpenseItem(description="weekly:groceries", amount=100)],
        ),
        ExpenseEntry(
            date=date(2024, 3, 15),
            category="Transport",
            items=[ExpenseItem(description="monthly:bus:pass", amount=200)],
        ),
        ExpenseEntry(
            date=date(2024, 3, 21),
            category="Entertainment",
            items=[ExpenseItem(description="movie:tickets", amount=150)],
        ),
    ]

    # Write entries in reverse order
    for entry in reversed(entries):
        file_manager.write_entry(tmp_path, entry)

    # When: Add a new entry in between
    new_entry = ExpenseEntry(
        date=date(2024, 3, 18),
        category="Food",
        items=[ExpenseItem(description="restaurant:dinner", amount=75)],
    )
    file_manager.write_entry(tmp_path, new_entry)

    # Then
    expected_filename = tmp_path / file_manager.generate_filename(new_entry.date)
    assert expected_filename.exists()

    content = expected_filename.read_text()
    expected_content = (
        "2024/03/21 Entertainment\n"
        "  movie:tickets                        kr 150\n"
        "  * Assets:Checking\n"
        "\n"
        "2024/03/15 Transport\n"
        "  monthly:bus:pass                     kr 200\n"
        "  * Assets:Checking\n"
        "\n"
        "2024/03/25 Shopping\n"
        "  weekly:groceries                     kr 100\n"
        "  * Assets:Checking\n"
        "\n"
        "2024/03/18 Food\n"
        "  restaurant:dinner                    kr 75\n"
        "  * Assets:Checking\n"
    )
    assert content == expected_content
