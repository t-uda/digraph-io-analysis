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
    
    print("="*60)
    print("Analysis WITH self-loops (default)")
    print("="*60)
    G, min_ent, max_ent, mean_ent = run_analysis_pipeline(
        tsv_path, 
        output_gexf,
        verbose=True,
        debug=True,
        output_graph_plot_path='transition_graph.png',
        output_bar_chart_path='node_entropy_bars.png'
    )
    
    print("\nAnalysis Summary:")
    print(f"Nodes: {G.number_of_nodes()}")
    print(f"Edges: {G.number_of_edges()}")
    print(f"Entropy - Min: {min_ent:.4f}, Max: {max_ent:.4f}, Mean: {mean_ent:.4f}")
    
    print("\nSample edges with entropy values:")
    sorted_edges = sorted(G.edges(data=True), key=lambda x: x[2].get('entropy', 0), reverse=True)
    for u, v, data in sorted_edges[:5]:
        next_counts = data.get('next_counts', {})
        print(f"  {u} -> {v}: weight={data['weight']}, entropy={data['entropy']:.4f}, next_counts={next_counts}")
    
    print("\n" + "="*60)
    print("Analysis WITHOUT self-loops")
    print("="*60)
    output_gexf_no_loops = 'transition_digraph_no_self_loops.gexf'
    G_no_loops, min_ent_nl, max_ent_nl, mean_ent_nl, entropy_vals = run_analysis_pipeline(
        tsv_path,
        output_gexf_no_loops,
        ignore_self_loops=True,
        verbose=True,
        debug=True,
        include_raw_entropy_values=True
    )
    
    print("\nAnalysis Summary (no self-loops):")
    print(f"Nodes: {G_no_loops.number_of_nodes()}")
    print(f"Edges: {G_no_loops.number_of_edges()}")
    print(f"Entropy - Min: {min_ent_nl:.4f}, Max: {max_ent_nl:.4f}, Mean: {mean_ent_nl:.4f}")
    print(f"Total entropy values collected: {len(entropy_vals)}")
    
    print("\nSample edges with entropy values (no self-loops):")
    sorted_edges_nl = sorted(G_no_loops.edges(data=True), key=lambda x: x[2].get('entropy', 0), reverse=True)
    for u, v, data in sorted_edges_nl[:5]:
        next_counts = data.get('next_counts', {})
        print(f"  {u} -> {v}: weight={data['weight']}, entropy={data['entropy']:.4f}, next_counts={next_counts}")
    
    print("\n" + "="*60)
    print("Comparison")
    print("="*60)
    print(f"Edge count difference: {G.number_of_edges() - G_no_loops.number_of_edges()} edges removed")
    print(f"Mean entropy change: {mean_ent:.4f} -> {mean_ent_nl:.4f} (Δ = {mean_ent_nl - mean_ent:+.4f})")

if __name__ == "__main__":
    main()
