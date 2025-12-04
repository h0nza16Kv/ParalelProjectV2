import threading
import queue
from reader import Reader
from worker import Worker
from aggregator import Aggregator
from config import NUM_WORKERS, PATTERNS, INPUT_PATHS, OUTPUT_PATH

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
    t_reader = threading.Thread(target=Reader.reader, args=(input_paths, search_queue, num_workers), name="reader")

    workers = [
        threading.Thread(target=Worker.search_worker, args=(search_queue, result_queue, patterns), name=f"worker-{i}")
        for i in range(num_workers)
    ]

    t_agg = threading.Thread(target=Aggregator.aggregator, args=(result_queue, output_path, num_workers),name="aggregator")

    t_reader.start()
    for w in workers:
        w.start()
    t_agg.start()

    t_reader.join()
    for i in range(num_workers):
        search_queue.join()
    for i in range(num_workers):
        result_queue.join()
    t_agg.join()

    print(f"\nProcessing complete. Results written to {output_path}")


if __name__ == "__main__":
    main(INPUT_PATHS, OUTPUT_PATH, NUM_WORKERS, PATTERNS)