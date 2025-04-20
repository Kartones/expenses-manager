from typing import Generator
from unittest.mock import patch, Mock
import pytest

from src.expenses.input_manager import InputManager


class TestInputManager:
    @pytest.fixture
    def input_manager(self) -> InputManager:
        """Create a new InputManager instance for testing."""
        return InputManager()

    @pytest.fixture
    def mock_input(self) -> Generator[Mock, None, None]:
        """Create a mock for the input function."""
        with patch("builtins.input") as mock:
            yield mock

    def test_set_country_valid_inputs(self, input_manager: InputManager) -> None:
        """Test country selection with valid inputs."""
        # Test Spain selection
        with patch("builtins.input", return_value="es"):
            input_manager.set_country()
            assert input_manager.country == "es"

        # Test Sweden selection
        with patch("builtins.input", return_value="se"):
            input_manager.set_country()
            assert input_manager.country == "se"

    def test_set_country_default(self, input_manager: InputManager) -> None:
        """Test country selection with empty input (should default to se)."""
        with patch("builtins.input", return_value=""):
            input_manager.set_country()
            assert input_manager.country == "se"

    def test_set_country_invalid_input(self, input_manager: InputManager, mock_input) -> None:
        """Test country selection with invalid input."""
        mock_input.side_effect = ["us", "se"]
        input_manager.set_country()
        assert input_manager.country == "se"

    def test_set_country_whitespace_handling(self, input_manager: InputManager, mock_input) -> None:
        """Test that whitespace is properly stripped from country input."""
        mock_input.return_value = "  es  "
        input_manager.set_country()
        assert input_manager.country == "es"
