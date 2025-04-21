#!/usr/bin/env python3
"""Script to run the DAT viewer application."""

import sys
from PySide6.QtWidgets import QApplication
from expenses.app.viewer import DatViewer


def main() -> None:
    """Main entry point for the DAT viewer application."""
    app = QApplication(sys.argv)

    # Get initial directory from command line argument or use current directory
    initial_dir = sys.argv[1] if len(sys.argv) > 1 else "."

    viewer = DatViewer(initial_dir)
    viewer.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
