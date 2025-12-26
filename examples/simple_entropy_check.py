
from digraph_inout_analysis.core import build_transition_digraph, calculate_io_entropy

def print_graph_entropy(G, name):
    print(f"\n--- {name} ---")
    calculate_io_entropy(G)
    for u, v, data in G.edges(data=True):
        print(f"{u} -> {v}: weight={data.get('weight')}, entropy={data.get('entropy'):.4f}")

def main():
    # Case 1: Simple chain
    # Sequence: A -> B -> C -> A ... (loop)
    # A -> B -> C
    # But to test entropy, we need B to branch.
    # Let's say B branches to C and D.
    
    # 1st Order would see B->C and B->D mixed.
    # 2nd Order checks history.
    
    # Scenario:
    # Pattern 1: A -> B -> C
    # Pattern 2: X -> B -> D
    # If we feed a sequence mixing these, the graph (1st order) sees B->C and B->D.
    # But 2nd order (A->B) should only see C. (X->B) should only see D.
    
    # Sequence: A, B, C, X, B, D, A, B, C, X, B, D ...
    seq = ['A', 'B', 'C', 'X', 'B', 'D'] * 10
    
    print("\n[Input Sequence]")
    print(f"Repeating: A -> B -> C, X -> B -> D")
    
    G = build_transition_digraph(seq)
    print_graph_entropy(G, "Conditional Entropy Verification")
    
    # Expectation:
    # A->B and X->B should have entropy 0.0 because history uniquely determines the next step.
    # (Old logic would give 1.0 bit due to mixed out-edges from B).

if __name__ == "__main__":
    main()
