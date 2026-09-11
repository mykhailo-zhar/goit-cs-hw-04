import logging
from pathlib import Path


def search(file_path: Path, word: str, logger: logging.Logger) -> bool:
    try:
        with file_path.open() as file:
            logger.debug("Starting search for %s in %s", word, file_path.name)
            file_content = file.read()
            words = file_content.split()

            for file_word in words:
                if file_word.lower() == word:
                    logger.debug("Search ended successfully %s", file_path.name)
                    return True

    except FileNotFoundError as e:
        logger.error(f"Error: Could not find file - {e.filename}")
    except PermissionError as e:
        logger.error(
            f"Unable to read file. Insufficient permissions - {e.filename}",
        )
    except OSError as e:
        logger.error(f"Other error: - {e}")

    logger.debug("Search ended %s", file_path.name)
    return False
