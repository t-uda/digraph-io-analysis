import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import matplotlib.colors as mcolors
import numpy as np
from typing import Optional

def assign_node_colors(G: nx.DiGraph, colormap_name: str = 'viridis') -> nx.DiGraph:
    """
    Assign 'viz' color attributes to nodes based on 'in_entropy_sum'.
    This is for Gephi GEXF export compatibility.
    """
    # Get entropy values
    entropies = [G.nodes[n].get('in_entropy_sum', 0.0) for n in G.nodes()]
    
    if not entropies:
        return G
        
    min_ent = min(entropies)
    max_ent = max(entropies)
    
    # Normalize and map to color
    cmap = plt.get_cmap(colormap_name)
    norm = mcolors.Normalize(vmin=min_ent, vmax=max_ent)
    
    for n in G.nodes():
        ent = G.nodes[n].get('in_entropy_sum', 0.0)
        # Get RGBA from colormap
        rgba = cmap(norm(ent))
        # Convert to 0-255 range for Gephi (r, g, b, a)
        # Note: GEXF writer in NetworkX expects 'viz': {'color': {'r': ..., 'g': ..., 'b': ..., 'a': ...}}
        color_dict = {
            'r': int(rgba[0] * 255),
            'g': int(rgba[1] * 255),
            'b': int(rgba[2] * 255),
            'a': float(rgba[3])
        }
        
        # Initialize 'viz' if not present
        if 'viz' not in G.nodes[n]:
            G.nodes[n]['viz'] = {}
            
        G.nodes[n]['viz']['color'] = color_dict
        
    return G

def plot_graph_with_entropy(G: nx.DiGraph, output_path: str, colormap_name: str = 'viridis'):
    """
    Draw the graph using NetworkX and Matplotlib, coloring nodes by in_entropy_sum.
    """
    plt.figure(figsize=(12, 10))
    
    pos = nx.spring_layout(G, k=0.15, iterations=20)
    
    entropies = [G.nodes[n].get('in_entropy_sum', 0.0) for n in G.nodes()]
    
    # Draw nodes
    nodes = nx.draw_networkx_nodes(
        G, pos, 
        node_color=entropies, 
        cmap=plt.get_cmap(colormap_name), 
        node_size=500,
        alpha=0.9
    )
    
    # Draw edges
    nx.draw_networkx_edges(G, pos, edge_color='gray', alpha=0.3, arrows=True)
    
    # Draw labels
    nx.draw_networkx_labels(G, pos, font_size=8, font_color='black')
    
    # Add colorbar
    if nodes:
        plt.colorbar(nodes, label='Node In-Entropy Sum')
        
    plt.title("Transition Graph (Color = In-Entropy Sum)")
    plt.axis('off')
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=300)
    plt.close()
    print(f"Graph plot saved to {output_path}")

def plot_node_entropy_bars(G: nx.DiGraph, output_path: str):
    """
    Create a bar chart of Node vs In-Entropy Sum.
    Nodes are sorted by entropy in descending order.
    """
    # Extract data
    node_data = []
    for n in G.nodes():
        node_data.append((n, G.nodes[n].get('in_entropy_sum', 0.0)))
        
    # Sort by entropy descending
    node_data.sort(key=lambda x: x[1], reverse=True)
    
    if not node_data:
        print("No data to plot.")
        return

    labels = [str(x[0]) for x in node_data]
    values = [x[1] for x in node_data]
    
    # Create plot
    # Adjust figure width based on number of nodes
    width = max(10, len(node_data) * 0.3)
    plt.figure(figsize=(width, 6))
    
    bars = plt.bar(labels, values, color='skyblue')
    
    plt.xlabel('Node')
    plt.ylabel('In-Entropy Sum')
    plt.title('In-Entropy Sum per Node')
    plt.xticks(rotation=90)
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=300)
    plt.close()
    print(f"Bar chart saved to {output_path}")
