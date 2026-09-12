import logging
import os
from pathlib import Path


def search(file_path: Path, keywords: list[str], logger: logging.Logger) -> tuple[list[str], Path] :
    pid = os.getpid()
    keywords_set = set(x.lower() for x in keywords)
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
