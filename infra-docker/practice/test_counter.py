from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from app import increment, read_count


class CounterTest(unittest.TestCase):
    def test_value_persists_in_directory(self):
        with TemporaryDirectory() as temp:
            self.assertEqual(read_count(Path(temp)), 0)
            self.assertEqual(increment(Path(temp)), 1)
            self.assertEqual(increment(Path(temp)), 2)
            self.assertEqual(read_count(Path(temp)), 2)
            self.assertEqual((Path(temp) / "count.txt").read_text(), "2")
