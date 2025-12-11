import threading
import queue
from reader import Reader
from worker import Worker
from aggregator import Aggregator
import configparser
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.abspath(os.path.join(BASE_DIR, "..", "config", "config.ini"))
config = configparser.ConfigParser()
config.read(CONFIG_PATH)

NUM_WORKERS = config["Settings"].getint("NUM_WORKERS")
LINES_PER_BLOCK = config["Settings"].getint("LINES_PER_BLOCK")
PATTERNS = [p.strip() for p in config["Settings"]["PATTERNS"].split(",")]
INPUT_PATHS = [p.strip() for p in config["Settings"]["INPUT_PATHS"].split(",")]
OUTPUT_PATH = config["Settings"]["OUTPUT_PATH"]

search_queue = queue.Queue()
result_queue = queue.Queue()


def main(input_paths: list[str], output_path: str, num_workers: int, patterns: list[str]):
    """
    Main orchestration function for the parallel search system.
    Initializes queues, threads (Reader, Workers, Aggregator), and manages their lifecycle.

    :param input_paths: List of file paths to process.
    :param output_path: Path to the output JSON file.
    :param num_workers: Number of worker threads to use.
    :param patterns: List of regex patterns for searching.
    """
    t_reader = threading.Thread(target=Reader.reader, args=(input_paths, search_queue, num_workers, LINES_PER_BLOCK ), name="reader")

    workers = [
        threading.Thread(target=Worker.search_worker, args=(search_queue, result_queue, patterns, LINES_PER_BLOCK ), name=f"worker-{i}")
        for i in range(num_workers)
    ]

    t_agg = threading.Thread(target=Aggregator.aggregator, args=(result_queue, output_path, num_workers),name="aggregator")

    t_reader.start()
    for w in workers:
        w.start()
    t_agg.start()

    t_reader.join()

    search_queue.join()
    result_queue.join()

    t_agg.join()


if __name__ == "__main__":
    main(INPUT_PATHS, OUTPUT_PATH, NUM_WORKERS, PATTERNS)