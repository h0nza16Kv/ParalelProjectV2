import unittest
import queue
import threading
from unittest.mock import mock_open, patch
from src.worker import Worker
from src.reader import Reader
from src.aggregator import Aggregator


class TestProjectComponents(unittest.TestCase):
    @patch('builtins.open', new_callable=mock_open, read_data="Line 1\nLine 2\nLine 3\nLine 4\nLine 5\n")
    def test_reader_divides_file_into_blocks(self, mock_file):
        """Tests whether Reader correctly splits a fictitious file into blocks and adds StopIteration"""

        search_queue = queue.Queue()
        num_workers = 2
        lines_per_block = 2
        input_path = ["fiktivni_log.txt"]

        with patch('src.reader.LINES_PER_BLOCK', lines_per_block):
            Reader.reader(input_path, search_queue, num_workers)

        self.assertEqual(search_queue.qsize(), 5)

        self.assertEqual(search_queue.get(), ("fiktivni_log.txt", 0, ["Line 1\n", "Line 2\n"]))
        self.assertEqual(search_queue.get(), ("fiktivni_log.txt", 1, ["Line 3\n", "Line 4\n"]))
        self.assertEqual(search_queue.get(), ("fiktivni_log.txt", 2, ["Line 5\n"]))
        self.assertEqual(search_queue.get(), StopIteration)
        self.assertEqual(search_queue.get(), StopIteration)

        for _ in range(5):
            search_queue.task_done()

    @patch('src.worker.LINES_PER_BLOCK', 5)
    def test_worker_finds_matches_and_calculates_line_number(self):
        """Tests whether Worker correctly finds matches and calculates the global row number."""

        search_queue = queue.Queue()
        result_queue = queue.Queue()
        patterns = [r'error', r'fail']

        file_path = "fiktivni_log.txt"
        block_index = 1
        lines = [
            "OK.",
            "An error 123 occurred.",
            "This will fail soon.",
            "Final line."
        ]

        expected_matches = [
            {'file': file_path, 'block': 2, 'line': 7, 'pattern': 'error', 'match': 'error'},
            {'file': file_path, 'block': 2, 'line': 8, 'pattern': 'fail', 'match': 'fail'}
        ]

        search_queue.put((file_path, block_index, lines))
        search_queue.put(StopIteration)

        worker_thread = threading.Thread(target=Worker.search_worker, args=(search_queue, result_queue, patterns))
        worker_thread.start()

        search_queue.join()
        worker_thread.join()

        matches = result_queue.get()
        stop_signal = result_queue.get()

        matches.sort(key=lambda x: x['line'])
        expected_matches.sort(key=lambda x: x['line'])

        self.assertEqual(matches, expected_matches)
        self.assertEqual(stop_signal, StopIteration)

        result_queue.task_done()
        result_queue.task_done()

    @patch('builtins.open', new_callable=mock_open)
    @patch('json.dump')
    def test_aggregator_collects_and_writes_to_json(self, mock_json_dump, mock_file):
        """Tests whether Aggregator correctly collects matches from multiple workers and calls json.dump."""

        result_queue = queue.Queue()
        output_path = "output.json"
        num_workers = 3

        matches_w1 = [{'file': 'a.txt', 'line': 1, 'pattern': 'e', 'match': 'E'}]
        matches_w2 = [{'file': 'b.txt', 'line': 5, 'pattern': 'w', 'match': 'W'},
                      {'file': 'b.txt', 'line': 6, 'pattern': 'w', 'match': 'W'}]
        matches_w3 = []

        result_queue.put(matches_w1)
        result_queue.put(matches_w2)
        result_queue.put(matches_w3)
        result_queue.put(StopIteration)
        result_queue.put(StopIteration)
        result_queue.put(StopIteration)

        agg_thread = threading.Thread(target=Aggregator.aggregator, args=(result_queue, output_path, num_workers))
        agg_thread.start()
        agg_thread.join()

        expected_all_matches = matches_w1 + matches_w2 + matches_w3

        mock_json_dump.assert_called_once()

        called_args, called_kwargs = mock_json_dump.call_args
        actual_matches_written = called_args[0]

        self.assertEqual(actual_matches_written, expected_all_matches)

        self.assertTrue(result_queue.empty())

    @patch('src.worker.LINES_PER_BLOCK', 1)
    def test_worker_multiple_matches_and_case_insensitivity(self):
        """Tests if Worker finds multiple matches on one line and handles case insensitivity (using re.IGNORECASE)."""

        search_queue = queue.Queue()
        result_queue = queue.Queue()
        patterns = [r'warning', r'fail']

        file_path = "log_file_2.txt"
        block_index = 0
        lines = [
            "WARNING: System Warning and another fail. FAIL!"
        ]

        expected_matches = [
            {'file': file_path, 'block': 1, 'line': 1, 'pattern': 'warning', 'match': 'WARNING'},
            {'file': file_path, 'block': 1, 'line': 1, 'pattern': 'warning', 'match': 'Warning'},
            {'file': file_path, 'block': 1, 'line': 1, 'pattern': 'fail', 'match': 'fail'},
            {'file': file_path, 'block': 1, 'line': 1, 'pattern': 'fail', 'match': 'FAIL'}
        ]

        search_queue.put((file_path, block_index, lines))
        search_queue.put(StopIteration)

        worker_thread = threading.Thread(target=Worker.search_worker, args=(search_queue, result_queue, patterns))
        worker_thread.start()

        search_queue.join()
        worker_thread.join()

        matches = result_queue.get()
        stop_signal = result_queue.get()

        matches.sort(key=lambda x: (x['pattern'], x['match']))
        expected_matches.sort(key=lambda x: (x['pattern'], x['match']))

        self.assertEqual(matches, expected_matches)
        self.assertEqual(stop_signal, StopIteration)

        result_queue.task_done()
        result_queue.task_done()


if __name__ == '__main__':
    unittest.main()