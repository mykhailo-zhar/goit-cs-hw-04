import logging
import timeit
from functools import partial

from src.concurrent_search import search_concurrent
from src.parallel_search import search_parallel
from src.utility import configure_logger, get_files

ITERATIONS = 100


def main():
    logger = logging.getLogger("Time logger")
    configure_logger(logger, prefix="time")

    files = get_files()
    keywords = ["she", "like"]
    quiet_logger = logging.getLogger("None")

    search_funcs = [search_parallel, search_concurrent]

    for search_fn in search_funcs:
        elapsed = timeit.timeit(
            partial(search_fn, files, keywords, quiet_logger),
            number=ITERATIONS,
        )
        logger.info(
            "%s: %.4f s total, %.4f s/iter (%d iterations)",
            search_fn.__name__,
            elapsed,
            elapsed / ITERATIONS,
            ITERATIONS,
        )


if __name__ == "__main__":
    main()
