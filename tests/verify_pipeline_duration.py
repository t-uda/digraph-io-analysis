from digraph_inout_analysis.core import run_analysis_pipeline
import os

def test_pipeline_with_duration():
    # Use a small subset or a fake file if needed, but let's try the real file
    # and just see if it runs and shows the reduction message.
    tsv_path = "tsv/14000_cots.csv"
    output_gexf = "test_duration.gexf"
    
    if not os.path.exists(tsv_path):
        print(f"File {tsv_path} not found, skipping test.")
        return

    print("--- Test n=1 (Default) ---")
    run_analysis_pipeline(
        tsv_path, 
        output_gexf, 
        column_name='loc_cot', 
        min_duration=1,
        verbose=True
    )

    print("\n--- Test n=2 (Filtering) ---")
    run_analysis_pipeline(
        tsv_path, 
        output_gexf, 
        column_name='loc_cot', 
        min_duration=2,
        verbose=True
    )

    if os.path.exists(output_gexf):
        os.remove(output_gexf)

if __name__ == "__main__":
    test_pipeline_with_duration()
