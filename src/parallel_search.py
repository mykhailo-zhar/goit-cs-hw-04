import logging
from logging.handlers import QueueHandler, QueueListener
from multiprocessing import get_context
from pathlib import Path

if __package__:
    from .search import search
    from .utility import get_filehandler, get_files, get_formatter, get_streamhandler
else:
    from search import search
    from utility import get_filehandler, get_files, get_formatter, get_streamhandler

NUM_WORKERS = 5

ctx = get_context("spawn")


def init_worker(q):
    """Attach a queue handler so worker logs reach the parent process.

    Args:
        q: Multiprocessing queue consumed by a ``QueueListener``.
    """
    logger = logging.getLogger("Process Logger")
    handler = QueueHandler(q)
    handler.setLevel(logging.DEBUG)
    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG)


def search_worker(file, keywords):
    """Run :func:`search` in a worker process using the process logger.

    Args:
        file: Path of the file to scan.
        keywords: Search terms to look for.

    Returns:
        The ``(found, file_path)`` pair from :func:`search`.
    """
    logger = logging.getLogger("Process Logger")
    return search(file, keywords, logger)


def search_parallel(q, ctx, files, words: list[str]) -> dict[str, list[Path]]:
    """Search files for keywords using a process pool.

    Workers are initialized with :func:`init_worker` so their logs go through
    ``q``. Each file is submitted as a separate task; results are merged in
    the parent process.

    Args:
        q: Multiprocessing queue for worker log records.
        ctx: Multiprocessing context used to create the pool.
        files: Paths of files to scan.
        words: Search terms to look for.

    Returns:
        Mapping of lowercase keyword to the files that contain it. Keywords
        with no matches are present with an empty list.
    """
    results = {x.lower(): [] for x in words}
    keywords = list(results.keys())
    with ctx.Pool(
        processes=NUM_WORKERS, initializer=init_worker, initargs=(q,)
    ) as executor:
        for found, path in executor.starmap(
            search_worker,
            [(file, keywords) for file in files],
        ):
            for keyword in found:
                results[keyword].append(path)

    return results


if __name__ == "__main__":
    formatter = get_formatter()
    stream_handler = get_streamhandler(formatter)
    file_handler = get_filehandler(formatter, "parallel")

    logger = logging.getLogger("Parallel logger")
    logger.addHandler(stream_handler)
    logger.addHandler(file_handler)
    logger.setLevel(logging.DEBUG)

    with ctx.Manager() as manager:
        shared_queue = manager.Queue()

        p_logger = logging.getLogger("Parallel logger (QUEUE)")

        queue_handler = QueueListener(
            shared_queue, file_handler, stream_handler, respect_handler_level=True
        )
        p_logger.setLevel(logging.DEBUG)

        queue_handler.start()

        files = get_files()

        keywords = ["she", "like"]

        logger.info("Starting")

        results = search_parallel(shared_queue, ctx, files, keywords)
        queue_handler.stop()
        for word, found_files in results.items():
            logger.debug(
                "File: %s, result: %s", word, [x.as_posix() for x in found_files]
            )
