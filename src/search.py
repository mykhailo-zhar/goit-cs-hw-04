import logging
import os
from pathlib import Path


def search(
    file_path: Path, keywords: list[str], logger: logging.Logger
) -> tuple[list[str], Path]:
    """Search a file for keywords and return those that occur at least once.

    Matching is case-insensitive and token-based (``str.split``). Each keyword
    is recorded at most once per file. Filesystem errors are logged and treated
    as a miss rather than raised.

    Args:
        file_path: File to scan.
        keywords: Search terms to look for.
        logger: Logger used for debug and error messages.

    Returns:
        A pair ``(found, file_path)`` where ``found`` is the list of matched
        keywords in file order.
    """
    pid = os.getpid()
    keywords_set = {x.lower() for x in keywords}
    result = []
    try:
        with file_path.open() as file:
            logger.debug(
                "PID(%s) Starting search for %s in %s", pid, keywords, file_path.name
            )
            file_content = file.read()
            words = file_content.split()

            for file_word in words:
                lower_word = file_word.lower()
                if not keywords_set:
                    break
                if lower_word in keywords_set:
                    result.append(lower_word)
                    keywords_set.remove(lower_word)

    except FileNotFoundError as e:
        logger.error("PID(%s) Error: Could not find file - %s", pid, e.filename)
    except PermissionError as e:
        logger.error(
            "PID(%s) Unable to read file. Insufficient permissions - %s",
            pid,
            e.filename,
        )
    except OSError as e:
        logger.error("PID(%s) Other error: - %s", pid, e)

    logger.debug("PID(%s) Search ended %s", pid, file_path.name)
    return result, file_path
