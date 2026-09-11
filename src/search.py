import logging
import os
from pathlib import Path


def search(file_path: Path, word: str, logger: logging.Logger) -> bool:
    pid = os.getpid()
    try:
        with file_path.open() as file:
            logger.debug(
                "PID(%s) Starting search for %s in %s", pid, word, file_path.name
            )
            file_content = file.read()
            words = file_content.split()

            for file_word in words:
                if file_word.lower() == word:
                    logger.debug(
                        "PID(%s) Search ended successfully %s", pid, file_path.name
                    )
                    return True

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
    return False
