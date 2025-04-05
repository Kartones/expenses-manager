from pathlib import Path
import pytest
from typing import Generator


@pytest.fixture
def data_dir(tmp_path: Path) -> Generator[Path, None, None]:
    """Provide a temporary directory for test data."""
    data_path = tmp_path / "data"
    data_path.mkdir(parents=True, exist_ok=True)
    yield data_path
