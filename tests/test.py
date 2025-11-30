import unittest
import queue
from unittest.mock import mock_open, patch
from src.aggregator import Aggregator
from src.worker import Worker
from src.reader import Reader


class TestProjectComponents(unittest.TestCase):
    @patch('builtins.open', new_callable=mock_open, read_data="Line 1\nLine 2\nLine 3\nLine 4\nLine 5\n")
    def test_reader_divides_file_into_blocks(self, mock_file):
        """Tests whether Reader correctly splits a fictitious file into blocks and adds StopIteration"""

        search_queue = queue.Queue()
        num_workers = 2
        lines_per_block = 2
        input_path = "fiktivni_log.txt"

        Reader.reader(input_path, search_queue, num_workers, lines_per_block)
        self.assertEqual(search_queue.qsize(), 5)

        self.assertEqual(search_queue.get(), (0, ["Line 1\n", "Line 2\n"]))
        self.assertEqual(search_queue.get(), (1, ["Line 3\n", "Line 4\n"]))
        self.assertEqual(search_queue.get(), (2, ["Line 5\n"]))
        self.assertEqual(search_queue.get(), StopIteration)
        self.assertEqual(search_queue.get(), StopIteration)

    def test_worker_finds_matches_and_calculates_line_number(self):
        """Tests whether Worker correctly finds matches and calculates the global row number."""

        search_queue = queue.Queue()
        result_queue = queue.Queue()
        patterns = [r'err', r'fail']

        block_index = 1
        lines = [
            "OK.",
            "An error 123 occurred.",
            "This will fail soon.",
            "Final line."
        ]

        expected_matches = [
            {'block': 1, 'line': 6, 'pattern': 'err', 'match': 'error'},
            {'block': 1, 'line': 7, 'pattern': 'fail', 'match': 'fail'}
        ]

        search_queue.put((block_index, lines))
        search_queue.put(StopIteration)

        Worker.search_worker

if __name__ == '__main__':
    unittest.main()