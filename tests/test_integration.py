import unittest
import os
import pandas as pd
import networkx as nx
from digraph_inout_analysis.core import run_analysis_pipeline
import tempfile
import shutil

class TestIntegration(unittest.TestCase):
    def setUp(self):
        # Create a temporary directory and a dummy TSV file
        self.test_dir = tempfile.mkdtemp()
        self.tsv_path = os.path.join(self.test_dir, 'test_data.tsv')
        self.output_gexf = os.path.join(self.test_dir, 'output.gexf')
        
        # Create dummy data: Time, cot, error, loc_cot
        # A -> B -> B -> C (error) -> A
        data = {
            'time': [1, 2, 3, 4, 5, 6],
            'sub_cot': ['A', 'B', 'B', 'error', 'C', 'A'],
            'loc_cot': ['X', 'Y', 'Y', 'Z', 'Z', 'X']
        }
        df = pd.DataFrame(data)
        df.to_csv(self.tsv_path, sep='\t', index=False)

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_pipeline_basic(self):
        # Test basic run
        # Sequence: A, B, B, C, A (error is skipped, but C is kept? 'error' row is skipped.)
        # Rows: 
        # 1: A
        # 2: B
        # 3: B
        # 4: error (skipped)
        # 5: C
        # 6: A
        # Sequence: A, B, B, C, A
        G, min_e, max_e, mean_e = run_analysis_pipeline(
            self.tsv_path, 
            self.output_gexf, 
            column_name='sub_cot',
            verbose=False
        )
        self.assertTrue(os.path.exists(self.output_gexf))
        self.assertIsInstance(G, nx.DiGraph)
        # A->B, B->B, B->C, C->A
        self.assertTrue(G.has_edge('A', 'B'))
        self.assertTrue(G.has_edge('B', 'B'))

    def test_custom_column(self):
        # Test with 'loc_cot'
        # X, Y, Y, Z, Z, X (error row was skipped based on sub_cot check? 
        # Wait, load_data_from_tsv checks the *target column* for 'error'.
        # In row 4, sub_cot is 'error', but loc_cot is 'Z'.
        # If I use column_name='loc_cot', it checks 'loc_cot' for 'error'.
        # So row 4 'Z' is valid.
        # Sequence: X, Y, Y, Z, Z, X
        
        G, _, _, _ = run_analysis_pipeline(
            self.tsv_path, 
            self.output_gexf, 
            column_name='loc_cot',
            verbose=False
        )
        self.assertTrue(G.has_edge('X', 'Y'))
        self.assertTrue(G.has_edge('Z', 'Z')) # Row 4 Z -> Row 5 Z
        
    def test_step_size(self):
        # Sequence: A, B, B, C, A
        # step=2: A, B, A
        G, _, _, _ = run_analysis_pipeline(
            self.tsv_path, 
            self.output_gexf, 
            column_name='sub_cot',
            step_size=2,
            verbose=False
        )
        # A -> B -> A
        self.assertTrue(G.has_edge('A', 'B'))
        self.assertTrue(G.has_edge('B', 'A'))
        self.assertFalse(G.has_edge('B', 'B')) # Skipped

    def test_duration_filtering_integration(self):
        # Sequence: A, B, B, C, A
        # min_duration=2 -> B, B
        # Result: B->B only? Or just single B?
        # A (1), B (2), C (1), A (1) -> Only B is kept.
        # Sequence: B, B
        G, _, _, _ = run_analysis_pipeline(
            self.tsv_path, 
            self.output_gexf, 
            column_name='sub_cot',
            min_duration=2,
            verbose=False
        )
        # Sequence is [B, B]. Edge B->B.
        self.assertTrue(G.has_edge('B', 'B'))
        self.assertEqual(G.number_of_nodes(), 1)

if __name__ == "__main__":
    unittest.main()
