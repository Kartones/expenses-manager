"""Qt-based viewer for DAT files."""

from pathlib import Path
from typing import Optional

from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QPushButton, QTextEdit, QFileDialog


class DatViewer(QMainWindow):
    def __init__(self, initial_dir: str = ".") -> None:
        super().__init__()
        self.setWindowTitle("DAT File Viewer")
        self.initial_dir = str(Path(initial_dir).resolve())
        self.setup_ui()
        self._content: Optional[str] = None

    def setup_ui(self) -> None:
        """Setup the basic UI components"""
        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Create open file button
        self.open_button = QPushButton("Open DAT File")
        self.open_button.clicked.connect(self._open_file_dialog)
        layout.addWidget(self.open_button)

        # Create text display area
        self.text_display = QTextEdit()
        self.text_display.setReadOnly(True)
        layout.addWidget(self.text_display)

        # Set a reasonable default size
        self.resize(800, 600)

    def _open_file_dialog(self) -> None:
        """Open a file dialog to select a .dat file"""
        file_name, _ = QFileDialog.getOpenFileName(
            self, "Open DAT File", self.initial_dir, "DAT Files (*.dat);;All Files (*)"
        )
        if file_name:
            self.load_file(file_name)

    def load_file(self, file_path: str) -> None:
        """Load and display the contents of a .dat file"""
        try:
            content = Path(file_path).read_text()
            self._content = content
            self.text_display.setText(content)
        except Exception as e:
            self.text_display.setText(f"Error loading file: {str(e)}")

    def get_content(self) -> Optional[str]:
        """Return the currently loaded file content"""
        return self._content
