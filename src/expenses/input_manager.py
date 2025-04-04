from datetime import date, datetime
from typing import List, Union

from expenses.models import ExpenseEntry, ExpenseItem, IncomeEntry, IncomeItem


class InputManager:
    def __init__(self) -> None:
        self.country = "se"  # Default country
        self.currency = "kr"  # Default currency

    def set_country(self) -> None:
        """Capture and validate the country selection.
        Sets both country code and currency based on selection.
        """
        while True:
            country = input("Enter country (es/se) [se]: ").lower().strip()
            if not country:
                self.country = "se"
                self.currency = "kr"
                return
            if country not in ["es", "se"]:
                print("Invalid country. Please enter 'es' or 'se'")
                continue
            self.country = country
            self.currency = "€" if country == "es" else "kr"
            return

    def capture_entry(self) -> Union[ExpenseEntry, IncomeEntry]:
        """Capture user input to create an expense or income entry.

        Returns:
            Either an ExpenseEntry or IncomeEntry based on user input

        Raises:
            ValueError: If the entry type is invalid
        """
        entry_type = input("Enter entry type: expense (E) or income (I): ").lower().strip()
        if entry_type not in ["e", "i", "expense", "income"]:
            raise ValueError("Invalid entry type")

        entry_date = self._capture_date()
        category = self._capture_category()

        items: Union[List[ExpenseItem], List[IncomeItem]] = []

        if entry_type in ["e", "expense"]:
            items = self._capture_expense_items()
            return ExpenseEntry(date=entry_date, category=category, items=items)
        else:  # entry_type in ["i", "income"]
            description = self._capture_description()
            items = self._capture_income_items()
            return IncomeEntry(date=entry_date, category=category, description=description, items=items)

    def _capture_date(self) -> date:
        """Capture and validate a date from user input.

        Returns:
            A valid date object
        """
        today = date.today()
        default_date = today.strftime("%Y-%m-%d")
        while True:
            try:
                date_str = input(f"Enter date (YYYY-MM-DD) [{default_date}]: ").strip()
                if not date_str:
                    return today
                return datetime.strptime(date_str, "%Y-%m-%d").date()
            except ValueError:
                print("Invalid date format. Please use YYYY-MM-DD")

    def _capture_category(self) -> str:
        """Capture and validate a category from user input.

        Returns:
            A valid category string
        """
        while True:
            category = input("Enter category: ").strip()
            if " " in category:
                print("Category cannot contain spaces. Use colons (:) instead")
            else:
                return category

    def _capture_description(self) -> str:
        """Capture and validate a description from user input.

        Returns:
            A valid description string
        """
        while True:
            description = input("Enter description: ").strip()
            if " " in description:
                print("Description cannot contain spaces. Use colons (:) instead")
            else:
                return description

    def _capture_amount(self) -> int:
        """Capture and validate an amount from user input.

        Returns:
            A valid integer amount
        """
        while True:
            try:
                amount_str = input("Enter amount (integer): ").strip()
                if "." in amount_str:
                    print("Amount must be an integer (no decimals)")
                    continue
                amount = int(amount_str)
                if amount <= 0:
                    print("Amount must be greater than zero")
                else:
                    return amount
            except ValueError:
                print("Invalid amount. Please enter a valid integer")

    def _capture_expense_items(self) -> List[ExpenseItem]:
        """Capture one or more expense items from user input.

        Returns:
            A list of ExpenseItem objects
        """
        items = []
        while True:
            description = self._capture_description()
            amount = self._capture_amount()
            items.append(ExpenseItem(description=description, amount=amount, currency=self.currency))

            if input("Add another item? (y/n): ").lower().strip() != "y":
                break

        return items

    def _capture_income_items(self) -> List[IncomeItem]:
        """Capture one or more income items from user input.

        Returns:
            A list of IncomeItem objects
        """
        items = []
        while True:
            amount = self._capture_amount()
            items.append(IncomeItem(amount=amount, currency=self.currency))

            if input("Add another item? (y/n): ").lower().strip() != "y":
                break

        return items
