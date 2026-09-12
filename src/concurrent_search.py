import concurrent.futures
import logging
from pathlib import Path

if __package__:
    from .search import search
    from .utility import configure_logger, get_files
else:
    from search import search
    from utility import configure_logger, get_files

NUM_WORKERS = 5


def search_concurrent(files, words, logger) -> dict[str, list[Path]]:
    """Search files for keywords using a thread pool.

    Each file is submitted as a separate task. Results from all workers are
    merged in the calling thread.

    Args:
        files: Paths of files to scan.
        words: Search terms to look for.
        logger: Logger passed through to each worker.

    Returns:
        Mapping of lowercase keyword to the files that contain it. Keywords
        with no matches are present with an empty list.
    """

    results = {x.lower(): [] for x in words}
    keywords = results.keys()
    with concurrent.futures.ThreadPoolExecutor(max_workers=NUM_WORKERS) as executor:
        for found, path in executor.map(
            search,
            files,
            [keywords for _ in range(len(files))],
            [logger for _ in range(len(files))],
        ):
            for keyword in found:
                results[keyword].append(path)

    return results


if __name__ == "__main__":
    logger = logging.getLogger("Concurrent logger")
    configure_logger(logger)

    files = get_files()

    logger.info("Starting")

    keywords = ["she", "like"]

    results = search_concurrent(files, keywords, logger)
    for word, found_files in results.items():
        logger.debug("File: %s, result: %s", word, [x.as_posix() for x in found_files])
