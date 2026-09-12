import logging
from multiprocessing import Pool
from pathlib import Path

if __package__:
    from .search import search
    from .utility import configure_logger, get_files
else:
    from search import search
    from utility import configure_logger, get_files

NUM_WORKERS = 5


def search_parallel(files, words: list[str], logger) -> dict[str, list[Path]]:
    results = {x.lower(): [] for x in words}
    keywords = list(results.keys())
    with Pool(processes=NUM_WORKERS) as executor:
        for found, path in executor.starmap(
            search,
            zip(
                files,
                [keywords for _ in range(len(files))],
                [logger for _ in range(len(files))],
            ),
        ):
            for keyword in found:
                results[keyword].append(path)

    return results


if __name__ == "__main__":
    logger = logging.getLogger("Parallel logger")
    configure_logger(logger, prefix="parallel")

    files = get_files()

    keywords = ["she", "like"]

    logger.info("Starting")

    results = search_parallel(files, keywords, logger)
    for word, found_files in results.items():
        logger.debug("File: %s, result: %s", word, [x.as_posix() for x in found_files])
