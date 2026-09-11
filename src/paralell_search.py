import logging
from multiprocessing import Pool

from search import search
from utility import PROJECT_ROOT, configure_logger

DATA_DIR = PROJECT_ROOT / "data"

NUM_WORKERS = 5


def search_parallel(files, word, logger):
    with Pool(processes=NUM_WORKERS) as executor:
        results = list(
            executor.starmap(
                search,
                zip(
                    files,
                    [word for _ in range(len(files))],
                    [logger for _ in range(len(files))],
                ),
            )
        )

    result_dict = {}
    for file, result in zip(files, results):
        result_dict[file] = result
    return result_dict


if __name__ == "__main__":
    logger = logging.getLogger("Paralllel logger")
    configure_logger(logger, prefix="parallel")

    files = [file_path for file_path in DATA_DIR.iterdir() if file_path.is_file()]

    word = "she"

    logger.info("Starting")

    results = search_parallel(files, word, logger)
    for k, v in results.items():
        logger.debug("File: %s, result: %s", k, v)
