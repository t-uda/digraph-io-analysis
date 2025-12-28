from itertools import groupby
from typing import List

def filter_sequence_by_duration(sequence: List[str], min_duration: int) -> List[str]:
    """
    Filter out states that persist for fewer than min_duration steps.
    
    Args:
        sequence: List of states.
        min_duration: Minimum number of consecutive steps a state must persist to be kept.
        
    Returns:
        Filtered list of states.
    """
    if min_duration <= 1:
        return sequence
    
    filtered_sequence = []
    for state, group in groupby(sequence):
        chunk = list(group)
        if len(chunk) >= min_duration:
            filtered_sequence.extend(chunk)
            
    return filtered_sequence

def test_filtering():
    # User example: A->A->B->C->C->C with n=2
    # Should become A->A->C->C->C
    seq = ['A', 'A', 'B', 'C', 'C', 'C']
    min_dur = 2
    filtered = filter_sequence_by_duration(seq, min_dur)
    print(f"Original: {seq}")
    print(f"Filtered (n={min_dur}): {filtered}")
    expected = ['A', 'A', 'C', 'C', 'C']
    assert filtered == expected, f"Expected {expected}, got {filtered}"

    # Another example
    seq2 = ['X', 'Y', 'Y', 'Z', 'Z', 'Z', 'W']
    # n=2 -> Y, Y, Z, Z, Z
    filtered2 = filter_sequence_by_duration(seq2, 2)
    print(f"Original: {seq2}")
    print(f"Filtered (n=2): {filtered2}")
    expected2 = ['Y', 'Y', 'Z', 'Z', 'Z']
    assert filtered2 == expected2, f"Expected {expected2}, got {filtered2}"
    
    # n=3 -> Z, Z, Z
    filtered3 = filter_sequence_by_duration(seq2, 3)
    print(f"Filtered (n=3): {filtered3}")
    expected3 = ['Z', 'Z', 'Z']
    assert filtered3 == expected3

    print("All tests passed!")

if __name__ == "__main__":
    test_filtering()
