import shutil
from pathlib import Path
import pytest


@pytest.fixture(autouse=True)
def setup_config():
    """Set up test configuration before each test."""
    # Save original config if it exists
    config_path = Path("src/expenses/config.py")
    config_backup = None
    if config_path.exists():
        config_backup = config_path.with_suffix(".py.bak")
        shutil.copy2(config_path, config_backup)

    # Copy sample config for tests
    shutil.copy2(Path("src/expenses/config.py.sample"), config_path)

    yield

    # Restore original config if it existed
    if config_backup and config_backup.exists():
        shutil.copy2(config_backup, config_path)
        config_backup.unlink()
    else:
        # Remove test config if no original existed
        config_path.unlink(missing_ok=True)
