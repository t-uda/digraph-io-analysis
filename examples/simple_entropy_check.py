
import networkx as nx
from digraph_inout_analysis.core import calculate_io_entropy

def print_graph_entropy(G, name):
    print(f"\n--- {name} ---")
    calculate_io_entropy(G)
    for u, v, data in G.edges(data=True):
        print(f"{u} -> {v}: weight={data.get('weight')}, entropy={data.get('entropy'):.4f}")

def main():
    # Case 1: Simple chain
    # A -> B (10) -> C (5)
    #             -> D (5)
    G1 = nx.DiGraph()
    G1.add_edge('A', 'B', weight=10)
    G1.add_edge('B', 'C', weight=5)
    G1.add_edge('B', 'D', weight=5)
    print_graph_entropy(G1, "Case 1: Simple Chain")

    # Case 2: Multiple Inputs with Different Weights
    # X -> B (2) -> C (5)
    #            -> D (5)
    # Y -> B (8) -> ...
    G2 = nx.DiGraph()
    G2.add_edge('X', 'B', weight=2)
    G2.add_edge('Y', 'B', weight=8)
    G2.add_edge('B', 'C', weight=5)
    G2.add_edge('B', 'D', weight=5) 
    print_graph_entropy(G2, "Case 2: Multiple Inputs")

if __name__ == "__main__":
    main()
