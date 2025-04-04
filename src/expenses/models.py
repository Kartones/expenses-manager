from dataclasses import dataclass
from datetime import date
from typing import List


class InvalidAmountError(ValueError):
    """Raised when an amount is invalid (zero, negative, or decimal)."""

    pass


class InvalidDescriptionError(ValueError):
    """Raised when a description contains spaces instead of colons."""

    pass


@dataclass
class ExpenseItem:
    description: str
    amount: int
    currency: str = "kr"

    def __post_init__(self) -> None:
        if not isinstance(self.amount, int):
            raise InvalidAmountError("Amount must be an integer")
        if self.amount <= 0:
            raise InvalidAmountError("Expense amount must be greater than zero")
        if " " in self.description:
            raise InvalidDescriptionError("Description must use colons (:) instead of spaces")


@dataclass
class IncomeItem:
    amount: int
    currency: str = "kr"

    def __post_init__(self) -> None:
        if not isinstance(self.amount, int):
            raise InvalidAmountError("Amount must be an integer")
        if self.amount <= 0:
            raise InvalidAmountError("Income amount must be greater than zero")


@dataclass
class BaseEntry:
    date: date
    category: str
    account: str

    def __post_init__(self) -> None:
        if " " in self.category:
            raise InvalidDescriptionError("Category must use colons (:) instead of spaces")


@dataclass
class ExpenseEntry(BaseEntry):
    items: List[ExpenseItem]

    def __init__(self, date: date, category: str, items: List[ExpenseItem], account: str = "Assets:Checking") -> None:
        super().__init__(date=date, category=category, account=account)
        self.items = items


@dataclass
class IncomeEntry(BaseEntry):
    description: str
    items: List[IncomeItem]

    def __init__(
        self,
        date: date,
        category: str,
        description: str,
        items: List[IncomeItem],
        account: str = "Assets:Checking",
    ) -> None:
        super().__init__(date=date, category=category, account=account)
        if " " in description:
            raise InvalidDescriptionError("Description must use colons (:) instead of spaces")
        self.description = description
        self.items = items
