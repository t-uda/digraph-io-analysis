import pandas as pd
import networkx as nx
import numpy as np
from scipy.stats import entropy
from typing import Union, List, Tuple

def load_data_from_tsv(file_path: str, column_name: str = 'sub_cot') -> List[str]:
    """
    Load data from TSV/CSV and handle error skipping logic.
    If column_name is "error" or NaN, skip it and connect the previous valid state to the next valid state.
    
    Args:
        file_path: Path to the data file.
        column_name: Name of the column representing the dynamics (default: 'sub_cot').
    """
    # Use sep=None with engine='python' for automatic delimiter detection
    df = pd.read_csv(file_path, sep=None, engine='python')
    
    # Check for required columns
    required_columns = ['time', column_name]
    for col in required_columns:
        if col not in df.columns:
            raise ValueError(f"Required column '{col}' missing from data file.")

    # Convert to string and drop rows where it is "error" or NaN
    # We use copy() to avoid SettingWithCopyWarning
    df[column_name] = df[column_name].astype(str)
    valid_data = df[df[column_name] != 'error'].copy()
    valid_data = valid_data[valid_data[column_name] != 'nan']
    
    return valid_data[column_name].tolist()

def build_transition_digraph(word_sequence: List[str], ignore_self_loops: bool = False) -> nx.DiGraph:
    """
    Build a directed graph where edges store:
    - 'weight': Total count of A->B transitions.
    - 'next_counts': {C: count} tracking A->B->C occurrences.
    
    Args:
        word_sequence: List of state words representing the trajectory.
        ignore_self_loops: If True, exclude self-loop transitions (A->A) from the graph.
    
    Returns:
        NetworkX DiGraph with transition counts and next-state distributions.
    """
    G = nx.DiGraph()
    if len(word_sequence) < 2:
        return G

    # Build edges and weights
    for i in range(len(word_sequence) - 1):
        u, v = word_sequence[i], word_sequence[i+1]
        
        # Skip self-loops if requested
        if ignore_self_loops and u == v:
            continue
            
        if G.has_edge(u, v):
            G[u][v]['weight'] += 1
        else:
            G.add_edge(u, v, weight=1, next_counts={})

    # Track transitions to the next state
    for i in range(len(word_sequence) - 2):
        u, v, w = word_sequence[i], word_sequence[i+1], word_sequence[i+2]
        
        # Skip if the current transition is a self-loop (when ignore_self_loops is True)
        if ignore_self_loops and u == v:
            continue
            
        # Only track next state if the edge exists (it might have been skipped)
        if G.has_edge(u, v):
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

def run_analysis_pipeline(
    tsv_path: str,
    output_gexf_path: str,
    column_name: str = 'sub_cot',
    step_size: int = 1,
    ignore_self_loops: bool = False,
    verbose: bool = True,
    debug: bool = False,
    include_raw_entropy_values: bool = False
) -> Union[Tuple[nx.DiGraph, float, float, float], Tuple[nx.DiGraph, float, float, float, List[float]]]:
    """
    Complete pipeline from TSV/CSV to GEXF with entropy analysis.
    
    Args:
        tsv_path: Path to the input data file.
        output_gexf_path: Path for the output GEXF file.
        column_name: Name of the column to analyze (default: 'sub_cot').
        step_size: Sub-sample the sequence by taking every N-th step (default: 1).
        ignore_self_loops: If True, exclude self-loop transitions from analysis.
        verbose: If True, print progress messages.
        debug: If True, print debug information.
        include_raw_entropy_values: If True, include list of all edge entropy values in return.
    
    Returns:
        If include_raw_entropy_values is False:
            (G, min_entropy, max_entropy, mean_entropy)
        If include_raw_entropy_values is True:
            (G, min_entropy, max_entropy, mean_entropy, entropy_values)
    """
    if verbose:
        print(f"Loading data from {tsv_path} (column='{column_name}', step_size={step_size})...")
    word_sequence = load_data_from_tsv(tsv_path, column_name=column_name)
    
    # Apply sub-sampling
    if step_size > 1:
        word_sequence = word_sequence[::step_size]
    
    if verbose:
        print(f"Building digraph with {len(word_sequence)} states...")
    
    # Count self-loops for debug output
    if debug:
        self_loop_count = sum(1 for i in range(len(word_sequence) - 1) 
                             if word_sequence[i] == word_sequence[i+1])
        print(f"[DEBUG] Self-loops detected: {self_loop_count}")
        if ignore_self_loops:
            print(f"[DEBUG] Self-loops will be excluded from graph construction")
    
    G = build_transition_digraph(word_sequence, ignore_self_loops=ignore_self_loops)
    
    if verbose:
        print(f"Graph built: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges")
    
    if verbose:
        print("Calculating I/O entropy...")
    G = calculate_io_entropy(G)
    
    # Extract entropy values and calculate statistics
    entropy_values = [data['entropy'] for u, v, data in G.edges(data=True)]
    
    if len(entropy_values) > 0:
        min_entropy = float(np.min(entropy_values))
        max_entropy = float(np.max(entropy_values))
        mean_entropy = float(np.mean(entropy_values))
    else:
        min_entropy = max_entropy = mean_entropy = 0.0
    
    if debug:
        print(f"[DEBUG] Entropy statistics:")
        print(f"[DEBUG]   Min:  {min_entropy:.4f}")
        print(f"[DEBUG]   Max:  {max_entropy:.4f}")
        print(f"[DEBUG]   Mean: {mean_entropy:.4f}")
        print(f"[DEBUG]   Total edges with entropy: {len(entropy_values)}")
    
    # Add labels and degrees as attributes for Gephi
    for node in G.nodes():
        G.nodes[node]['label'] = str(node)
        G.nodes[node]['in_degree'] = G.in_degree(node, weight='weight')
        G.nodes[node]['out_degree'] = G.out_degree(node, weight='weight')
    
    if verbose:
        print(f"Exporting to {output_gexf_path}...")
    export_to_gephi(G, output_gexf_path)
    
    if include_raw_entropy_values:
        return G, min_entropy, max_entropy, mean_entropy, entropy_values
    else:
        return G, min_entropy, max_entropy, mean_entropy
