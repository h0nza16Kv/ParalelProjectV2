import threading
import queue
from reader import Reader
from worker import Worker
from aggregator import Aggregator

search_queue = queue.Queue()
result_queue = queue.Queue()

NUM_WORKERS = 4
STOP = object()

PATTERNS = [r'error', r'warning', r'failed', r'exception']


def main(input_path: str, output_path: str):
    t_reader = threading.Thread(target=Reader.reader, args=(input_path, search_queue, NUM_WORKERS), name="reader")

    workers = [
        threading.Thread(target=Worker.search_worker, args=(search_queue, result_queue, STOP, PATTERNS), name=f"worker-{i}")
        for i in range(NUM_WORKERS)
    ]

    t_agg = threading.Thread(target=Aggregator.aggregator, args=(result_queue, output_path, NUM_WORKERS, STOP), name="aggregator")

    t_reader.start()
    for w in workers:
        w.start()
    t_agg.start()

    t_reader.join()
    for _ in range(NUM_WORKERS):
        search_queue.join()
    for _ in range(NUM_WORKERS):
        result_queue.join()
    t_agg.join()


if __name__ == "__main__":
    main("input.txt", "results.json")