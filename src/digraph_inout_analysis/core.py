import pandas as pd
import networkx as nx
import numpy as np
from scipy.stats import entropy

def load_data_from_tsv(file_path):
    """
    Load data from TSV and handle error skipping logic.
    If sub_cot is "error" or NaN, skip it and connect the previous valid state to the next valid state.
    """
    df = pd.read_csv(file_path, sep='\t')
    
    # Check for required columns
    required_columns = ['time', 'sub_cot']
    for col in required_columns:
        if col not in df.columns:
            raise ValueError(f"Required column '{col}' missing from TSV.")

    # Drop rows where sub_cot is "error" or NaN
    valid_data = df[df['sub_cot'] != 'error'].copy()
    valid_data = valid_data.dropna(subset=['sub_cot'])
    
    return valid_data['sub_cot'].tolist()

def build_transition_digraph(word_sequence):
    """
    Build a directed graph where edges store:
    - 'weight': Total count of A->B transitions.
    - 'next_counts': {C: count} tracking A->B->C occurrences.
    """
    G = nx.DiGraph()
    if len(word_sequence) < 2:
        return G

    # Build edges and weights
    for i in range(len(word_sequence) - 1):
        u, v = word_sequence[i], word_sequence[i+1]
        if G.has_edge(u, v):
            G[u][v]['weight'] += 1
        else:
            G.add_edge(u, v, weight=1, next_counts={})

    # Track transitions to the next state
    for i in range(len(word_sequence) - 2):
        u, v, w = word_sequence[i], word_sequence[i+1], word_sequence[i+2]
        G[u][v]['next_counts'][w] = G[u][v]['next_counts'].get(w, 0) + 1
            
    return G

def calculate_io_entropy(G):
    """
    Calculate conditional Shannon entropy H(Next | Current, Previous) for each edge.
    """
    for u, v, data in G.edges(data=True):
        next_counts = data.get('next_counts', {})
        if not next_counts:
            data['entropy'] = 0.0
            continue
            
        counts = list(next_counts.values())
        data['entropy'] = entropy(counts, base=2)
        
    return G

def export_to_gephi(G, output_path):
    """
    Export the graph to GEXF format which is compatible with Gephi.
    Note: next_counts is excluded as GEXF doesn't support nested dict attributes.
    """
    G_export = G.copy()
    for u, v in G_export.edges():
        if 'next_counts' in G_export[u][v]:
            del G_export[u][v]['next_counts']
    
    nx.write_gexf(G_export, output_path)
    print(f"Graph exported to {output_path}")

def run_analysis_pipeline(tsv_path, output_gexf_path):
    """
    Complete pipeline from TSV to GEXF.
    """
    print(f"Loading data from {tsv_path}...")
    word_sequence = load_data_from_tsv(tsv_path)
    
    print(f"Building digraph with {len(word_sequence)} transitions...")
    G = build_transition_digraph(word_sequence)
    
    print("Calculating I/O entropy...")
    G = calculate_io_entropy(G)
    
    # Add labels and degrees as attributes for Gephi
    for node in G.nodes():
        G.nodes[node]['label'] = str(node)
        G.nodes[node]['in_degree'] = G.in_degree(node, weight='weight')
        G.nodes[node]['out_degree'] = G.out_degree(node, weight='weight')
        
    export_to_gephi(G, output_gexf_path)
    return G
