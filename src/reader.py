class Reader:
    @staticmethod
    def reader(paths: list[str], search_queue, num_workers, lines_per_block):
        """
        Loads files from the specified paths, divides their contents into blocks, and places them
        in the task queue.
        :param paths: List of paths to files
        :param num_workers: number of threads
        :param search_queue: Task queue
        :return: None
        """
        for path in paths:
            try:
                with open(path, "r", encoding="utf-8") as f:
                    lines = f.readlines()
            except FileNotFoundError:
                continue

            n = len(lines)
            id = 0
            block_index = 0
            while id < n:
                block = lines[id: id + lines_per_block]
                search_queue.put((path, block_index, block))
                block_index += 1
                id += lines_per_block

        for i in range(num_workers):
            search_queue.put(StopIteration)