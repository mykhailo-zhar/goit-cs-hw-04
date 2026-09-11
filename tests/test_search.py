"""White-box tests for :func:`search.search`.

Derived from the function's control-flow graph:

1. ``Path.open`` / ``read`` / ``split`` succeed.
2. ``for file_word in words`` — 0, 1, or many iterations.
3. Predicate ``file_word.lower() == word`` — true or false.
   Only the token from the file is lowercased; ``word`` is compared as given.
4. Early ``return True`` on the first match.
5. Exception handlers, in declaration order:
   ``FileNotFoundError``, ``PermissionError``, other ``OSError``.
6. Fall-through ``return False`` (no match or after a handled error).
"""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

import pytest

from search import search


@pytest.mark.parametrize(
    ("content", "word", "expected"),
    [
        ("hello world", "hello", True),
        ("hello world", "world", True),
        ("alpha beta gamma", "beta", True),
        ("Hello", "hello", True),
        ("hello", "Hello", False),
        ("hello world", "missing", False),
        ("", "hello", False),
        ("   \n\t  ", "hello", False),
        ("one", "one", True),
        ("one", "two", False),
        ("hello\nworld", "world", True),
        ("hello\tworld", "hello", True),
        ("hello,world", "hello", False),
        ("", "", False),
    ],
    ids=[
        "match_first_of_many",
        "match_last_of_many",
        "match_middle",
        "file_token_is_lowercased",
        "query_is_not_lowercased",
        "no_match_many_tokens",
        "empty_file_zero_iterations",
        "whitespace_only_zero_iterations",
        "single_token_hit",
        "single_token_miss",
        "newline_is_delimiter",
        "tab_is_delimiter",
        "punctuation_stays_attached",
        "empty_query_never_matches",
    ],
)
def test_search_word_loop_and_predicate(
    tmp_path: Path,
    mock_logger,
    content: str,
    word: str,
    expected: bool,
) -> None:
    path = tmp_path / "sample.txt"
    path.write_text(content, encoding="utf-8")

    assert search(path, word, mock_logger) is expected
    mock_logger.debug.assert_any_call("Starting search for %s in %s", word, path.name)
    if expected:
        mock_logger.debug.assert_any_call("Search ended successfully %s", path.name)
    else:
        mock_logger.debug.assert_any_call("Search ended %s", path.name)
    assert mock_logger.debug.call_count == 2


def test_first_match_returns_without_scanning_further(
    tmp_path: Path, mock_logger
) -> None:
    path = tmp_path / "sample.txt"
    path.write_text("target decoy target", encoding="utf-8")

    assert search(path, "target", mock_logger) is True
    mock_logger.debug.assert_any_call("Search ended successfully %s", path.name)


def test_file_not_found_logs_and_returns_false(tmp_path: Path, mock_logger) -> None:
    missing = tmp_path / "does-not-exist.txt"

    assert search(missing, "hello", mock_logger) is False

    mock_logger.error.assert_called_once_with(f"Error: Could not find file - {missing}")


def test_permission_error_logs_and_returns_false(tmp_path: Path, mock_logger) -> None:
    path = tmp_path / "locked.txt"
    error = PermissionError(13, "Permission denied", str(path))

    with patch.object(Path, "open", side_effect=error):
        assert search(path, "secret", mock_logger) is False

    mock_logger.error.assert_called_once_with(
        f"Unable to read file. Insufficient permissions - {path}"
    )


def test_oserror_logs_and_returns_false(tmp_path: Path, mock_logger) -> None:
    path = tmp_path / "unreadable.txt"
    error = OSError("I/O error")

    with patch.object(Path, "open", side_effect=error):
        assert search(path, "hello", mock_logger) is False

    mock_logger.error.assert_called_once_with(f"Other error: - {error}")


def test_directory_path_is_handled_as_oserror(tmp_path: Path, mock_logger) -> None:
    """``IsADirectoryError`` is an ``OSError`` but not the two specific handlers."""
    assert search(tmp_path, "hello", mock_logger) is False

    mock_logger.error.assert_called_once()
    (message,) = mock_logger.error.call_args.args
    assert message.startswith("Other error: - ")
    mock_logger.debug.assert_called_once_with("Search ended %s", tmp_path.name)
