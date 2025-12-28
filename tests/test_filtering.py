import unittest
from digraph_inout_analysis.core import filter_sequence_by_duration

class TestFiltering(unittest.TestCase):
    def test_basic_filtering(self):
        # User example: A->A->B->C->C->C with n=2
        # Should become A->A->C->C->C
        seq = ['A', 'A', 'B', 'C', 'C', 'C']
        min_dur = 2
        filtered = filter_sequence_by_duration(seq, min_dur)
        expected = ['A', 'A', 'C', 'C', 'C']
        self.assertEqual(filtered, expected)

    def test_another_case(self):
        seq = ['X', 'Y', 'Y', 'Z', 'Z', 'Z', 'W']
        # n=2 -> Y, Y, Z, Z, Z
        filtered = filter_sequence_by_duration(seq, 2)
        expected = ['Y', 'Y', 'Z', 'Z', 'Z']
        self.assertEqual(filtered, expected)
        
        # n=3 -> Z, Z, Z
        filtered = filter_sequence_by_duration(seq, 3)
        expected = ['Z', 'Z', 'Z']
        self.assertEqual(filtered, expected)

    def test_no_filtering(self):
        seq = ['A', 'B', 'C']
        filtered = filter_sequence_by_duration(seq, 1)
        self.assertEqual(filtered, seq)

if __name__ == "__main__":
    unittest.main()
