from digraph_inout_analysis.core import run_analysis_pipeline
import os

def test_custom_column():
    input_csv = "tsv/14000_cots.csv"
    output_gexf = "14000_cots_loc.gexf"
    
    print(f"Testing analysis with {input_csv} using column 'loc_cot'...")
    
    try:
        G, min_e, max_e, mean_e = run_analysis_pipeline(
            input_csv, 
            output_gexf, 
            column_name='loc_cot',
            verbose=True,
            debug=True
        )
        
        print("\nAnalysis successful!")
        print(f"Nodes: {G.number_of_nodes()}")
        print(f"Edges: {G.number_of_edges()}")
        print(f"Min Entropy: {min_e:.4f}")
        print(f"Max Entropy: {max_e:.4f}")
        print(f"Mean Entropy: {mean_e:.4f}")
        
        if os.path.exists(output_gexf):
            print(f"Output GEXF created: {output_gexf}")
        else:
            print("Error: Output GEXF not found.")
            
    except Exception as e:
        print(f"Analysis failed: {e}")

def test_original_format():
    input_tsv = "tsv/Re_14000_20k_snapshot_1_0.0005.tsv"
    output_gexf = "original_test.gexf"
    
    print(f"\nTesting analysis with {input_tsv} (original format)...")
    
    try:
        G, min_e, max_e, mean_e = run_analysis_pipeline(
            input_tsv, 
            output_gexf, 
            verbose=True
        )
        print("Original format still works!")
    except Exception as e:
        print(f"Original format analysis failed: {e}")

if __name__ == "__main__":
    if not os.path.exists("tsv"):
        print("Run this from the project root directory.")
    else:
        test_custom_column()
        test_original_format()
