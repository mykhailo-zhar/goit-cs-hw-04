"""Shared fixtures and import path for tests."""

import logging
import sys
from pathlib import Path
from unittest.mock import MagicMock

import pytest

SRC = Path(__file__).resolve().parents[1] / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))


@pytest.fixture
def mock_logger() -> MagicMock:
    """Logger double so exception handlers can be asserted without I/O."""
    return MagicMock(spec=logging.Logger)
