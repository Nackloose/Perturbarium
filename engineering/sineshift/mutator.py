# Mutation/shuffling logic based on sine wave permutation technology

import numpy as np
import math
from typing import List, Tuple, Optional


class SineShiftMutator:
    """A mutator that uses sine wave-based permutation technology for audio manipulation."""
    
    def __init__(self, frame_count: int = 100000):
        self.frame_count = frame_count
        self.base_frequency = 10.0
        self.scale_factor = 1000.0
        self.offset_factor = 0.2
    
    def generate_permutation_map(self, swap_param: float) -> List[int]:
        """Generates a permutation map based on the swap_param and sine function.
        
        This is adapted from the permutation.py technology for audio frame manipulation.
        Supports the full spectrum of swap parameters from 0.0 to any positive value.
        
        Args:
            swap_param: A float value (can be any positive value for infinite key space).
            
        Returns:
            A list representing the permutation map for audio frames.
        """
        if swap_param < 0.0:
            raise ValueError("swap_param must be non-negative")
        
        scored_indices = []
        for i in range(self.frame_count):
            # Calculate a score influenced by the sine wave and swap_param
            # Using the same formula as permutation.py but adapted for audio frames
            # Normalize large swap parameters to prevent overflow
            normalized_param = swap_param % (2 * math.pi) if swap_param > 2 * math.pi else swap_param
            score = math.sin(normalized_param * 100.0 + i * self.offset_factor) * self.scale_factor + i
            scored_indices.append((score, i))
        
        # Sort based on the score. This determines the new order of original indices.
        scored_indices.sort()
        
        # Create the permutation map: original_index -> new_index
        permutation_map = [0] * self.frame_count
        for new_pos, (score, original_pos) in enumerate(scored_indices):
            permutation_map[original_pos] = new_pos
        
        return permutation_map
    
    def get_inverse_permutation_map(self, permutation_map: List[int]) -> List[int]:
        """Generates the inverse permutation map.
        
        Args:
            permutation_map: The original permutation map (original_index -> new_index).
            
        Returns:
            A list representing the inverse permutation map (new_index -> original_index).
        """
        inverse_map = [0] * self.frame_count
        for original_pos, new_pos in enumerate(permutation_map):
            inverse_map[new_pos] = original_pos
        return inverse_map
    
    def apply_permutation(self, audio_data: np.ndarray, permutation_map: List[int]) -> np.ndarray:
        """Applies a permutation to audio data.
        
        Args:
            audio_data: The audio data to permute (should match frame_count).
            permutation_map: The map defining the permutation (original_index -> new_index).
            
        Returns:
            The permuted audio data.
            
        Raises:
            ValueError: If the input data length is incorrect or map is invalid.
        """
        if len(audio_data) != self.frame_count:
            raise ValueError(
                f"Expected {self.frame_count} frames but got {len(audio_data)}"
            )
        if len(permutation_map) != self.frame_count:
            raise ValueError(
                f"Expected permutation map of size {self.frame_count} but got {len(permutation_map)}"
            )
        
        # Create a new array to build the permuted audio data
        permuted_audio = np.zeros_like(audio_data)
        # Apply the permutation: sample at original_pos moves to new_pos
        for original_pos, new_pos in enumerate(permutation_map):
            permuted_audio[new_pos] = audio_data[original_pos]
        
        return permuted_audio
    
    def apply_inverse_permutation(self, audio_data: np.ndarray, inverse_permutation_map: List[int]) -> np.ndarray:
        """Applies an inverse permutation to audio data.
        
        Args:
            audio_data: The audio data to un-permute (should match frame_count).
            inverse_permutation_map: The map defining the inverse permutation (new_index -> original_index).
            
        Returns:
            The un-permuted audio data.
            
        Raises:
            ValueError: If the input data length is incorrect or map is invalid.
        """
        if len(audio_data) != self.frame_count:
            raise ValueError(
                f"Expected {self.frame_count} frames but got {len(audio_data)}"
            )
        if len(inverse_permutation_map) != self.frame_count:
            raise ValueError(
                f"Expected inverse permutation map of size {self.frame_count} but got {len(inverse_permutation_map)}"
            )
        
        # Create a new array to build the un-permuted audio data
        original_audio = np.zeros_like(audio_data)
        # Apply the inverse permutation: sample at new_pos moves to original_pos
        for new_pos, original_pos in enumerate(inverse_permutation_map):
            original_audio[original_pos] = audio_data[new_pos]
        
        return original_audio
    
    def mutate_data(self, data: np.ndarray, swap_param: float) -> np.ndarray:
        """Mutates binary data using sine wave permutation technology.
        
        Args:
            data: The binary data to mutate.
            swap_param: A float value controlling the mutation.
            
        Returns:
            The mutated binary data.
        """
        # Ensure data matches expected frame count
        if len(data) != self.frame_count:
            # Resize data to match frame count
            if len(data) > self.frame_count:
                data = data[:self.frame_count]
            else:
                # Pad with zeros if shorter
                padded_data = np.zeros(self.frame_count)
                padded_data[:len(data)] = data
                data = padded_data
        
        # Generate permutation map
        permutation_map = self.generate_permutation_map(swap_param)
        
        # Apply permutation
        return self.apply_permutation(data, permutation_map)
    
    def unmute_data(self, data: np.ndarray, swap_param: float) -> np.ndarray:
        """Un-mutates binary data using sine wave permutation technology.
        
        Args:
            data: The mutated binary data to restore.
            swap_param: A float value (must match original mutation).
            
        Returns:
            The restored binary data.
        """
        # Ensure data matches expected frame count
        if len(data) != self.frame_count:
            # Resize data to match frame count
            if len(data) > self.frame_count:
                data = data[:self.frame_count]
            else:
                # Pad with zeros if shorter
                padded_data = np.zeros(self.frame_count)
                padded_data[:len(data)] = data
                data = padded_data
        
        # Generate permutation map
        permutation_map = self.generate_permutation_map(swap_param)
        
        # Generate inverse map
        inverse_permutation_map = self.get_inverse_permutation_map(permutation_map)
        
        # Apply inverse permutation
        return self.apply_inverse_permutation(data, inverse_permutation_map)


def create_mutator(frame_count: int = 100000) -> SineShiftMutator:
    """Factory function to create a SineShiftMutator instance.
    
    Args:
        frame_count: The number of frames to work with.
        
    Returns:
        A configured SineShiftMutator instance.
    """
    return SineShiftMutator(frame_count)
