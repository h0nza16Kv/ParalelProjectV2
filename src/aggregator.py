import json
class Aggregator:
    def aggregator(result_queue, output_path, num_workers, STOP):
        """
        Collects search results from all worker threads.
        This function reads matches from result_queue until it receives a termination signal
        from each worker thread, and then writes all matches to a JSON file.

        :param result_queue: Entrance queue
        :param output_path: Path to the output file
        :param num_workers: Number of workers
        :param STOP: Signal for ending the loop
        :return: None
        """
        all_matches = []
        stop_count = 0

        while True:
            item = result_queue.get()
            if item is StopIteration:
                stop_count += 1
                result_queue.task_done()
                if stop_count == num_workers:
                    break
                continue

            all_matches.extend(item)
            result_queue.task_done()

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(all_matches, f, indent=2, ensure_ascii=False)