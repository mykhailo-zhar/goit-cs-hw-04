import concurrent.futures
import logging
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

from search import search

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"

NUM_WORKERS = 5


def search_concurrent(files, word, logger):
    with concurrent.futures.ThreadPoolExecutor(max_workers=NUM_WORKERS) as executor:
        results = list(
            executor.map(
                search,
                files,
                [word for _ in range(len(files))],
                [logger for _ in range(len(files))],
            )
        )

    result_dict = {}
    for file, result in zip(files, results):
        result_dict[file] = result
    return result_dict


if __name__ == "__main__":
    logger = logging.getLogger("Concurrent logger")
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(threadName)s - %(levelname)s - %(message)s"
    )

    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setLevel(logging.DEBUG)
    stream_handler.setFormatter(formatter)

    logs_dir = PROJECT_ROOT / "logs"
    logs_dir.mkdir(parents=True, exist_ok=True)

    tz = timezone(timedelta(hours=2))  # GMT+2
    timestamp = datetime.now(tz=tz).strftime("%Y%m%d_%H%M%S")
    log_filename = logs_dir / f"search_{timestamp}.log"
    file_handler = logging.FileHandler(log_filename)
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)

    logger.setLevel(logging.DEBUG)
    logger.addHandler(stream_handler)
    logger.addHandler(file_handler)

    files = [file_path for file_path in DATA_DIR.iterdir() if file_path.is_file()]

    word = "she"

    logger.info("Starting")

    results = search_concurrent(files, word, logger)
    for k, v in results.items():
        logger.debug("File: %s, result: %s", k, v)
