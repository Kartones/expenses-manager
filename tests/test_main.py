from datetime import date
from pathlib import Path
from unittest.mock import patch


from expenses.main import main


def test_main_captures_expense_entry(data_dir: Path) -> None:
    # Given
    test_date = date(2024, 3, 21)
    test_inputs = [
        "se",  # Country at startup
        "expense",  # Entry type
        "2024-03-21",  # Date
        "Shopping",  # Category
        "weekly:groceries",  # Description
        "100",  # Amount
        "n",  # No more items
        "n",  # Don't add another entry
    ]

    # When
    with patch("builtins.input", side_effect=test_inputs), patch("sys.argv", ["main.py", str(data_dir)]):
        main()

    # Then
    expected_filename = data_dir / f"se-{test_date.year}-{test_date.month:02d}.dat"
    assert expected_filename.exists()

    content = expected_filename.read_text()
    expected_content = "2024/03/21 Shopping\n  weekly:groceries                     kr 100\n  * Assets:Checking\n"
    assert content == expected_content


def test_main_captures_income_entry(data_dir: Path) -> None:
    # Given
    test_date = date(2024, 3, 21)
    test_inputs = [
        "se",  # Country
        "income",  # Entry type
        "2024-03-21",  # Date
        "Salary",  # Category
        "monthly:salary",  # Description
        "25000",  # Amount
        "n",  # No more items
        "n",  # Don't add another entry
    ]

    # When
    with patch("builtins.input", side_effect=test_inputs), patch("sys.argv", ["main.py", str(data_dir)]):
        main()

    # Then
    expected_filename = data_dir / f"se-{test_date.year}-{test_date.month:02d}.dat"
    assert expected_filename.exists()

    content = expected_filename.read_text()
    expected_content = "2024/03/21 Salary\n  * Assets:Checking                    kr 25000\n  monthly:salary\n"
    assert content == expected_content


def test_main_handles_multiple_entries(data_dir: Path) -> None:
    # Given
    test_date = date(2024, 3, 21)
    test_inputs = [
        "se",  # Country at startup
        # First entry (expense)
        "expense",  # Entry type
        "2024-03-21",  # Date
        "Shopping",  # Category
        "weekly:groceries",  # Description
        "100",  # Amount
        "n",  # No more items
        "y",  # Add another entry
        # Second entry (income)
        "income",  # Entry type
        "2024-03-21",  # Date
        "Salary",  # Category
        "monthly:salary",  # Description
        "25000",  # Amount
        "n",  # No more items
        "n",  # Don't add another entry
    ]

    # When
    with patch("builtins.input", side_effect=test_inputs), patch("sys.argv", ["main.py", str(data_dir)]):
        main()

    # Then
    expected_filename = data_dir / f"se-{test_date.year}-{test_date.month:02d}.dat"
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


def test_main_handles_keyboard_interrupt(data_dir: Path) -> None:
    # Given
    test_inputs = [
        "se",  # Country at startup
        "expense",  # Will be interrupted after entry type
    ]

    # When
    with patch("builtins.input", side_effect=test_inputs), patch("sys.argv", ["main.py", str(data_dir)]):
        with patch("expenses.input_manager.InputManager.capture_entry", side_effect=KeyboardInterrupt):
            main()

    # Then
    # No files should be created
    assert not any(data_dir.iterdir())


def test_main_handles_error_and_retries(data_dir: Path) -> None:
    # Given
    test_date = date(2024, 3, 21)
    test_inputs = [
        "se",  # Country at startup
        # First attempt (will fail)
        "invalid",  # Invalid entry type
        "y",  # Try again
        # Second attempt (will succeed)
        "expense",  # Entry type
        "2024-03-21",  # Date
        "Shopping",  # Category
        "weekly:groceries",  # Description
        "100",  # Amount
        "n",  # No more items
        "n",  # Don't add another entry
    ]

    # When
    with patch("builtins.input", side_effect=test_inputs), patch("sys.argv", ["main.py", str(data_dir)]):
        main()

    # Then
    expected_filename = data_dir / f"se-{test_date.year}-{test_date.month:02d}.dat"
    assert expected_filename.exists()

    content = expected_filename.read_text()
    expected_content = "2024/03/21 Shopping\n  weekly:groceries                     kr 100\n  * Assets:Checking\n"
    assert content == expected_content
