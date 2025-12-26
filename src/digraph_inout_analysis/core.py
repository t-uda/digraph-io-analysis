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
    Calculate Shannon entropy for each transition based on in-degree and out-degree.
    For each word B, we look at where we came from (in-degree) and where we are going (out-degree).
    The request says: "B に入ってくる有向辺の度数毎に，B から出て行く有向辺の度数を調べます．"
    Wait, the request says: "B への in-degree を分母として，各 out-degree を分子として割ることで，
    「B の次の状態」の確率 (0 以上 1 以下) の値が対応します．"
    
    Wait, let's re-read carefully:
    "A から B への有向辺の本数をカウントします．
    B に入ってくる有向辺の度数毎に，B から出て行く有向辺の度数を調べます．
    目的は，in-degree vs out-degree の「揺らぎ」をエントロピーを用いて解析することです．
    B への in-degree を分母として，各 out-degree を分子として割ることで，
    「B の次の状態」の確率 (0 以上 1 以下) の値が対応します．"
    
    This sounds like for each edge (A, B), we look at B's total out-degree (sum of weights of outgoing edges)
    and calculate entropy based on the distribution of those weights.
    However, the "denominator" is "B への in-degree".
    Actually, usually transition probability from B to C is weight(B, C) / sum(weight(B, X) for all X).
    The text says "B への in-degree を分母として". This is a bit unusual if it's strictly in-degree.
    Let me re-read: "B への in-degree を分母として，各 out-degree を分子として割ることで".
    If someone arrives at B, the total number of times we arrived at B is in_degree(B).
    The number of times we then go to C is weight(B, C).
    So transition probability P(C|B) = weight(B, C) / total_in_weight(B).
    Since total_in_weight(B) *usually* equals total_out_weight(B) (except for the start/end of sequence),
    this is almost the same as standard transition entropy.
    
    "これにより，各有向辺 A->B に Shanon entropy の値を割り当てます．"
    The entropy is naturally a property of the node B (uncertainty of next state after B).
    But the request asks to assign it to the edge A->B.
    
    Let's implement:
    1. For each node n, calculate total_in_weight = sum of weights of edges (*, n).
    2. For each node n, calculate out_probabilities = [weight(n, m) / total_in_weight for m in targets].
    3. Calculate entropy(n) from out_probabilities.
    4. For each edge (A, B), assign edge_entropy = entropy(B).
    """
    
    # Pre-calculate node entropies
    node_entropies = {}
    for node in G.nodes():
        # Total weight of edges coming into current node
        total_in_weight = sum(data['weight'] for u, v, data in G.in_edges(node, data=True))
        
        if total_in_weight == 0:
            node_entropies[node] = 0.0
            continue
            
        # Weights of edges going out of current node
        out_weights = [data['weight'] for u, v, data in G.out_edges(node, data=True)]
        
        if not out_weights:
            node_entropies[node] = 0.0
            continue
            
        # Probabilities: out_weight / total_in_weight
        # Note: if total_in_weight != total_out_weight, sum(probs) != 1.
        # But the request says "B への in-degree を分母として".
        probs = [w / total_in_weight for w in out_weights]
        
        # Shannon entropy: -sum(p * log2(p))
        # scipy.stats.entropy uses natural log by default, we should use base 2 for Shannon.
        node_entropies[node] = entropy(probs, base=2)
        
    # Assign entropy to edges
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
