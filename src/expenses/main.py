from pathlib import Path

from expenses.file_manager import FileManager
from expenses.input_manager import InputManager


def main() -> None:
    """Main entry point for the expenses CLI."""
    print("Welcome to the Expenses Manager!")
    print("--------------------------------")

    input_manager = InputManager()
    input_manager.set_country()  # Get country selection at startup
    file_manager = FileManager(country=input_manager.country)
    base_path = Path.cwd()

    while True:
        try:
            # Capture the entry
            entry = input_manager.capture_entry()

            # Write to file
            file_manager.write_entry(base_path, entry)
            print("\nEntry saved successfully!")

            # Ask if user wants to continue
            if input("\nAdd another entry? (y/n): ").lower().strip() != "y":
                break

        except KeyboardInterrupt:
            print("\nOperation cancelled.")
            break
        except Exception as e:
            print(f"\nError: {str(e)}")
            if input("\nTry again? (y/n): ").lower().strip() != "y":
                break

    print("\nThank you for using Expenses Manager!")


if __name__ == "__main__":
    main()
