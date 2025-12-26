import pandas as pd
import networkx as nx
import numpy as np
from scipy.stats import entropy
import os

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
    Build a directed graph where edges represent transitions between words.
    Edges store the count of transitions.
    """
    G = nx.DiGraph()
    
    for i in range(len(word_sequence) - 1):
        u = word_sequence[i]
        v = word_sequence[i+1]
        
        if G.has_edge(u, v):
            G[u][v]['weight'] += 1
        else:
            G.add_edge(u, v, weight=1)
            
    return G

def calculate_io_entropy(G):
    """
    Calculate Shannon entropy for each edge based on transition probabilities.
    
    For each node B, compute P(C|B) = weight(B,C) / total_in_weight(B),
    then calculate Shannon entropy H(B) = -Σ P(C|B) log₂ P(C|B).
    The entropy value is assigned to all incoming edges (A->B).
    """
    node_entropies = {}
    for node in G.nodes():
        total_in_weight = sum(data['weight'] for u, v, data in G.in_edges(node, data=True))
        
        if total_in_weight == 0:
            node_entropies[node] = 0.0
            continue
            
        out_weights = [data['weight'] for u, v, data in G.out_edges(node, data=True)]
        
        if not out_weights:
            node_entropies[node] = 0.0
            continue
            
        probs = [w / total_in_weight for w in out_weights]
        node_entropies[node] = entropy(probs, base=2)
        
    for u, v, data in G.edges(data=True):
        data['entropy'] = node_entropies[v]
        
    return G

def export_to_gephi(G, output_path):
    """
    Export the graph to GEXF format which is compatible with Gephi.
    """
    nx.write_gexf(G, output_path)
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
