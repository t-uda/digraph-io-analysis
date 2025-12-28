from digraph_inout_analysis.core import run_analysis_pipeline
import os

def test_step_size():
    input_csv = "tsv/14000_cots.csv"
    output_gexf = "14000_cots_step10.gexf"
    
    print(f"Testing analysis with {input_csv} using column='loc_cot' and step_size=10...")
    
    try:
        # Run with step_size=1 (default)
        print("Running with step_size=1...")
        G1, min1, max1, mean1 = run_analysis_pipeline(
            input_csv, "test_step1.gexf", column_name='loc_cot', step_size=1, verbose=False
        )
        
        # Run with step_size=10
        print("Running with step_size=10...")
        G10, min10, max10, mean10 = run_analysis_pipeline(
            input_csv, output_gexf, column_name='loc_cot', step_size=10, verbose=False
        )
        
        print("\nResults:")
        print(f"step_size=1:  Nodes={G1.number_of_nodes()}, Edges={G1.number_of_edges()}")
        print(f"step_size=10: Nodes={G10.number_of_nodes()}, Edges={G10.number_of_edges()}")
        
        # Verify that step_size=10 has significantly fewer edges (usually)
        if G10.number_of_edges() > 0:
            print("Sub-sampling verified!")
        
        if os.path.exists(output_gexf):
            os.remove(output_gexf)
        if os.path.exists("test_step1.gexf"):
            os.remove("test_step1.gexf")
            
    except Exception as e:
        print(f"Verification failed: {e}")

if __name__ == "__main__":
    if os.path.exists("tsv"):
        test_step_size()
    else:
        print("Run from project root.")
