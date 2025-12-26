import os
import sys

# Add src to path if needed
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from digraph_inout_analysis.core import run_analysis_pipeline

def main():
    # Find the TSV file in tsv/ directory
    tsv_dir = 'tsv'
    tsv_files = [f for f in os.listdir(tsv_dir) if f.endswith('.tsv')]
    
    if not tsv_files:
        print("No TSV files found in tsv/ directory.")
        return
        
    tsv_path = os.path.join(tsv_dir, tsv_files[0])
    output_gexf = 'transition_digraph.gexf'
    
    print(f"Starting analysis for {tsv_path}...")
    G = run_analysis_pipeline(tsv_path, output_gexf)
    
    print("\nAnalysis Summary:")
    print(f"Nodes: {G.number_of_nodes()}")
    print(f"Edges: {G.number_of_edges()}")
    
    print("\nSample edges with entropy values:")
    sorted_edges = sorted(G.edges(data=True), key=lambda x: x[2].get('entropy', 0), reverse=True)
    for u, v, data in sorted_edges[:10]:
        next_counts = data.get('next_counts', {})
        print(f"  {u} -> {v}: weight={data['weight']}, entropy={data['entropy']:.4f}, next_counts={next_counts}")

if __name__ == "__main__":
    main()
