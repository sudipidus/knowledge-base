import pytest
from pathlib import Path
import tempfile
import shutil


@pytest.fixture
def tmp_vault(tmp_path):
    """Create a temporary vault directory structure."""
    dirs = [
        "schema/templates",
        "sources/raw",
        "sources/references",
        "sources/inbox",
        "wiki/entities",
        "wiki/concepts",
        "wiki/topics",
        "wiki/syntheses",
        "wiki/explorations",
    ]
    for d in dirs:
        (tmp_path / d).mkdir(parents=True)
    (tmp_path / "wiki/index.md").write_text("# Index\n")
    (tmp_path / "wiki/log.md").write_text("# Activity Log\n")
    return tmp_path
