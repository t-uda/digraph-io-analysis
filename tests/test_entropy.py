import unittest
from digraph_inout_analysis.core import build_transition_digraph, calculate_io_entropy

class TestEntropy(unittest.TestCase):
    def test_conditional_entropy(self):
        # Sequence: A, B, C, X, B, D, A, B, C, X, B, D ...
        # Pattern 1: A -> B -> C
        # Pattern 2: X -> B -> D
        # If we feed a sequence mixing these:
        # 1st order (Markov) sees B -> C (50%) and B -> D (50%). Entropy = 1 bit.
        # 2nd order (Contextual) sees A->B followed by C (100%), X->B followed by D (100%). Entropy = 0 bit.
        
        seq = ['A', 'B', 'C', 'X', 'B', 'D'] * 10
        
        G = build_transition_digraph(seq)
        calculate_io_entropy(G)
        
        # Check edge A->B
        if G.has_edge('A', 'B'):
            entropy_val = G['A']['B'].get('entropy')
            self.assertAlmostEqual(entropy_val, 0.0, places=4, msg="Entropy for A->B should be 0 (deterministic context)")

        # Check edge X->B
        if G.has_edge('X', 'B'):
            entropy_val = G['X']['B'].get('entropy')
            self.assertAlmostEqual(entropy_val, 0.0, places=4, msg="Entropy for X->B should be 0 (deterministic context)")

        # Check edge B->C (Wait, B->C is followed by X or A? No.)
        # The sequence is ... C, X ... and ... D, A ...
        # C -> X
        # D -> A
        # These are also deterministic in this repeating sequence.

if __name__ == "__main__":
    unittest.main()
