import re
class Worker:
    def search_worker(search_queue, result_queue, STOP, patterns):
        """
        Search worker running in a thread for parallel processing
        :param search_queue: Entrance queue
        :param result_queue: Output queue
        :param STOP: Signal for ending the loop
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

            block_index, lines = item
            matches = []
            for lineno, line in enumerate(lines):
                for pat in compiled:
                    for m in pat.finditer(line):
                        matches.append({
                            'block':  block_index+ 1,
                            'line': lineno + 1 + block_index * len(lines),
                            'pattern': pat.pattern,
                            'match': m.group()
                        })
            print("Matches added to json file")
            result_queue.put(matches)
            search_queue.task_done()