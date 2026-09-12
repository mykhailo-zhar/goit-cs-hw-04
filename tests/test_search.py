"""White-box tests for :func:`src.search.search`.

Derived from the function's control-flow graph:

1. Keywords are lowercased into a set; matches are removed as they are found.
2. ``Path.open`` / ``read`` / ``split`` succeed.
3. ``for file_word in words`` — 0, 1, or many iterations.
4. ``if not keywords_set: break`` after every remaining keyword is found.
5. Predicate ``lower_word in keywords_set`` — true or false.
6. Exception handlers, in declaration order:
   ``FileNotFoundError``, ``PermissionError``, other ``OSError``.
7. Always logs ``Search ended`` and returns ``(found, file_path)``.
"""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

import pytest

from src.search import search

PID = 4242


@pytest.fixture(autouse=True)
def fixed_pid(monkeypatch: pytest.MonkeyPatch) -> int:
    monkeypatch.setattr("src.search.os.getpid", lambda: PID)
    return PID


@pytest.mark.parametrize(
    ("content", "keywords", "expected_found"),
    [
        ("hello world", ["hello"], ["hello"]),
        ("hello world", ["world"], ["world"]),
        ("alpha beta gamma", ["beta"], ["beta"]),
        ("Hello", ["hello"], ["hello"]),
        ("hello", ["Hello"], ["hello"]),
        ("hello world", ["missing"], []),
        ("", ["hello"], []),
        ("   \n\t  ", ["hello"], []),
        ("one", ["one"], ["one"]),
        ("one", ["two"], []),
        ("hello\nworld", ["world"], ["world"]),
        ("hello\tworld", ["hello"], ["hello"]),
        ("hello,world", ["hello"], []),
        ("", [""], []),
        ("alpha beta", ["beta", "alpha"], ["alpha", "beta"]),
        ("hello world", ["hello", "missing"], ["hello"]),
        ("hello hello", ["hello"], ["hello"]),
        ("a b c", [], []),
    ],
    ids=[
        "match_first_of_many",
        "match_last_of_many",
        "match_middle",
        "file_token_is_lowercased",
        "query_is_lowercased",
        "no_match_many_tokens",
        "empty_file_zero_iterations",
        "whitespace_only_zero_iterations",
        "single_token_hit",
        "single_token_miss",
        "newline_is_delimiter",
        "tab_is_delimiter",
        "punctuation_stays_attached",
        "empty_query_never_matches",
        "multiple_keywords_file_order",
        "partial_keyword_match",
        "keyword_matched_only_once",
        "empty_keywords_break",
    ],
)
def test_search_word_loop_and_predicate(
    tmp_path: Path,
    mock_logger,
    content: str,
    keywords: list[str],
    expected_found: list[str],
) -> None:
    path = tmp_path / "sample.txt"
    path.write_text(content, encoding="utf-8")

    found, returned_path = search(path, keywords, mock_logger)

    assert found == expected_found
    assert returned_path == path
    mock_logger.error.assert_not_called()
    mock_logger.debug.assert_any_call(
        "PID(%s) Starting search for %s in %s", PID, keywords, path.name
    )
    mock_logger.debug.assert_any_call("PID(%s) Search ended %s", PID, path.name)
    assert mock_logger.debug.call_count == 2


def test_all_keywords_found_stops_scanning(tmp_path: Path, mock_logger) -> None:
    path = tmp_path / "sample.txt"
    path.write_text("target decoy leftover", encoding="utf-8")

    found, returned_path = search(path, ["target"], mock_logger)

    assert found == ["target"]
    assert returned_path == path
    mock_logger.error.assert_not_called()
    mock_logger.debug.assert_any_call("PID(%s) Search ended %s", PID, path.name)


def test_file_not_found_logs_and_returns_empty(tmp_path: Path, mock_logger) -> None:
    missing = tmp_path / "does-not-exist.txt"

    found, returned_path = search(missing, ["hello"], mock_logger)

    assert found == []
    assert returned_path == missing
    mock_logger.error.assert_called_once_with(
        "PID(%s) Error: Could not find file - %s", PID, str(missing)
    )
    mock_logger.debug.assert_called_once_with(
        "PID(%s) Search ended %s", PID, missing.name
    )


def test_permission_error_logs_and_returns_empty(tmp_path: Path, mock_logger) -> None:
    path = tmp_path / "locked.txt"
    error = PermissionError(13, "Permission denied", str(path))

    with patch.object(Path, "open", side_effect=error):
        found, returned_path = search(path, ["secret"], mock_logger)

    assert found == []
    assert returned_path == path
    mock_logger.error.assert_called_once_with(
        "PID(%s) Unable to read file. Insufficient permissions - %s",
        PID,
        str(path),
    )
    mock_logger.debug.assert_called_once_with("PID(%s) Search ended %s", PID, path.name)


def test_oserror_logs_and_returns_empty(tmp_path: Path, mock_logger) -> None:
    path = tmp_path / "unreadable.txt"
    error = OSError("I/O error")

    with patch.object(Path, "open", side_effect=error):
        found, returned_path = search(path, ["hello"], mock_logger)

    assert found == []
    assert returned_path == path
    mock_logger.error.assert_called_once_with("PID(%s) Other error: - %s", PID, error)
    mock_logger.debug.assert_called_once_with("PID(%s) Search ended %s", PID, path.name)


def test_directory_path_is_handled_as_oserror(tmp_path: Path, mock_logger) -> None:
    """``IsADirectoryError`` is an ``OSError`` but not the two specific handlers."""
    found, returned_path = search(tmp_path, ["hello"], mock_logger)

    assert found == []
    assert returned_path == tmp_path
    mock_logger.error.assert_called_once()
    fmt, logged_pid, exc = mock_logger.error.call_args.args
    assert fmt == "PID(%s) Other error: - %s"
    assert logged_pid == PID
    assert isinstance(exc, OSError)
    mock_logger.debug.assert_called_once_with(
        "PID(%s) Search ended %s", PID, tmp_path.name
    )
