# src/licensee/permutation.py

import math
from typing import List

# Define the total number of characters to be permuted
TOTAL_CHARS_TO_PERMUTE = 440


def get_permutation_map(swap_param: float) -> List[int]:
    """Generates a permutation map based on the swap_param and sine function.

    The map is a list where the index is the original position (0-29)
    and the value is the new position (0-29).

    Args:
        swap_param: A float value between 0.0 and 1.0.

    Returns:
        A list representing the permutation map.
    """
    if not 0.0 <= swap_param <= 1.0:
        raise ValueError("swap_param must be between 0.0 and 1.0")

    scored_indices = []
    for i in range(TOTAL_CHARS_TO_PERMUTE):
        # Calculate a score influenced by the sine wave and swap_param
        # Using constants K1, K2 to spread values and add sensitivity
        # The addition of 'i * small_number' helps in differentiating scores
        # for different indices even with similar sine values.
        score = math.sin(swap_param * 100.0 + i * 0.2) * 1000.0 + i
        scored_indices.append((score, i))

    # Sort based on the score. This determines the new order of original indices.
    scored_indices.sort()

    # Create the permutation map: original_index -> new_index
    permutation_map = [0] * TOTAL_CHARS_TO_PERMUTE
    for new_pos, (score, original_pos) in enumerate(scored_indices):
        permutation_map[original_pos] = new_pos

    return permutation_map


def get_inverse_permutation_map(permutation_map: List[int]) -> List[int]:
    """Generates the inverse permutation map.

    Args:
        permutation_map: The original permutation map (original_index -> new_index).

    Returns:
        A list representing the inverse permutation map (new_index -> original_index).
    """
    inverse_map = [0] * TOTAL_CHARS_TO_PERMUTE
    for original_pos, new_pos in enumerate(permutation_map):
        inverse_map[new_pos] = original_pos
    return inverse_map


def apply_permutation(input_chars: str, permutation_map: List[int]) -> str:
    """Applies a permutation to a string of characters.

    Args:
        input_chars: The 30-character string to permute.
        permutation_map: The map defining the permutation (original_index -> new_index).

    Returns:
        The permuted 30-character string.

    Raises:
        ValueError: If the input string length is incorrect or map is invalid.
    """
    if len(input_chars) != TOTAL_CHARS_TO_PERMUTE:
        raise ValueError(
            f"Expected {TOTAL_CHARS_TO_PERMUTE} characters but got {len(input_chars)}"
        )
    if len(permutation_map) != TOTAL_CHARS_TO_PERMUTE:
        raise ValueError(
            f"Expected permutation map of size {TOTAL_CHARS_TO_PERMUTE} but got {len(permutation_map)}"
        )

    # Create a list to build the permuted string
    permuted_chars = [""] * TOTAL_CHARS_TO_PERMUTE
    # Apply the permutation: character at original_pos moves to new_pos
    for original_pos, new_pos in enumerate(permutation_map):
        permuted_chars[new_pos] = input_chars[original_pos]

    return "".join(permuted_chars)


def apply_inverse_permutation(
    input_chars: str, inverse_permutation_map: List[int]
) -> str:
    """Applies an inverse permutation to a string of characters.

    Args:
        input_chars: The 30-character string to un-permute.
        inverse_permutation_map: The map defining the inverse permutation (new_index -> original_index).

    Returns:
        The un-permuted 30-character string.

    Raises:
        ValueError: If the input string length is incorrect or map is invalid.
    """
    if len(input_chars) != TOTAL_CHARS_TO_PERMUTE:
        raise ValueError(
            f"Expected {TOTAL_CHARS_TO_PERMUTE} characters but got {len(input_chars)}"
        )
    if len(inverse_permutation_map) != TOTAL_CHARS_TO_PERMUTE:
        raise ValueError(
            f"Expected inverse permutation map of size {TOTAL_CHARS_TO_PERMUTE} but got {len(inverse_permutation_map)}"
        )

    # Create a list to build the un-permuted string
    original_chars = [""] * TOTAL_CHARS_TO_PERMUTE
    # Apply the inverse permutation: character at new_pos moves to original_pos
    for new_pos, original_pos in enumerate(inverse_permutation_map):
        original_chars[original_pos] = input_chars[new_pos]

    return "".join(original_chars)


# Example Usage (within permutation.py)
if __name__ == "__main__":
    test_string = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123"
    test_swap_param = 0.42

    print(f"Original string: {test_string}")
    print(f"Swap parameter: {test_swap_param}")

    # Generate permutation map
    perm_map = get_permutation_map(test_swap_param)
    print(f"Permutation map: {perm_map}")

    # Apply permutation
    permuted_string = apply_permutation(test_string, perm_map)
    print(f"Permuted string: {permuted_string}")

    # Generate inverse map
    inv_perm_map = get_inverse_permutation_map(perm_map)
    print(f"Inverse permutation map: {inv_perm_map}")

    # Apply inverse permutation to un-permute
    unpermuted_string = apply_inverse_permutation(permuted_string, inv_perm_map)
    print(f"Un-permuted string: {unpermuted_string}")

    assert test_string == unpermuted_string, "Permutation round trip failed!"
    print("Permutation round trip successful.")
