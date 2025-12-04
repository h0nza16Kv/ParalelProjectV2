import re
from config import LINES_PER_BLOCK

class Worker:
    def search_worker(search_queue, result_queue, patterns):
        """
        Search worker running in a thread for parallel processing
        :param search_queue: Entrance queue
        :param result_queue: Output queue
        :param patterns: Regular expression search list
        :return: None. The output is via result_queue
        """
        compiled = [re.compile(p, re.IGNORECASE) for p in patterns]

        while True:
            item = search_queue.get()
            if item is StopIteration:
                result_queue.put(StopIteration)
                search_queue.task_done()
                break

            file_path, block_index, lines = item
            matches = []
            for lineno, line in enumerate(lines):
                for pat in compiled:
                    for m in pat.finditer(line):
                        matches.append({
                            'file': file_path,
                            'block':  block_index+ 1,
                            'line': lineno + 1 + block_index * LINES_PER_BLOCK,
                            'pattern': pat.pattern,
                            'match': m.group()
                        })
            print(f"Matches added to json file from {file_path}, block {block_index + 1}")
            result_queue.put(matches)
            search_queue.task_done()