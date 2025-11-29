class Reader:

    def reader(path, search_queue, num_workers, lines_per_block=100):
        """
        Loads a file from the specified path, divides its contents into blocks, and places them
        in the task queue.
        :param search_queue: Path to file
        :param num_workers: number of threads
        :param search_queue: Task queue
        :param lines_per_block: Optional number of lines
        :return: None
        """
        try:
            with open(path, "r", encoding="utf-8") as f:
                lines = f.readlines()
        except FileNotFoundError:
            print(f"Soubor {path} nebyl nalezen.")
            return

        n = len(lines)
        id = 0
        block_index = 0
        while id < n:
            block = lines[id: id + lines_per_block]
            search_queue.put((block_index, block))
            block_index += 1
            id += lines_per_block

        for i in range(num_workers):
            search_queue.put(StopIteration)
