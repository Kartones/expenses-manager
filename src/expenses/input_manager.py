from typing import Optional


class InputManager:
    """Manages user input for the expenses CLI."""

    def __init__(self) -> None:
        """Initialize InputManager."""
        self.country: Optional[str] = None

    def set_country(self) -> None:
        """Set the country for expense tracking.

        Prompts user for country code (es/se) and validates input.
        Default is 'se' if no input provided.
        """
        while True:
            country = input("Enter country (es/se) [se]: ").lower().strip()
            if not country:
                country = "se"

            if country in ["es", "se"]:
                self.country = country
                break

            print("Invalid country. Please enter 'es' for Spain or 'se' for Sweden.")
