"""
SineScramble Cipher Implementation

This module contains the core SineScramble cipher implementation with support
for both Multi-Round Mode (high security) and Segmented Mode (high performance).
"""

import math
import numpy as np
from enum import Enum
from typing import List, Tuple, Union
import concurrent.futures
import threading


class OperationMode(Enum):
    """Operation modes for SineScramble cipher"""
    MULTI_ROUND = "multi_round"
    SEGMENTED = "segmented"


class SineScrambleCipher:
    """
    SineScramble symmetric cipher implementation
    
    A flexible cipher that can operate in two modes:
    - Multi-Round Mode: High security through iterative transformations
    - Segmented Mode: High performance through parallel processing
    """
    
    def __init__(self, key: List[float], mode: OperationMode, 
                 amplitude: float = 100.0, frequency: float = 0.1, 
                 phase: float = 1.0):
        """
        Initialize SineScramble cipher
        
        Args:
            key: Multi-dimensional key vector (k1, k2, ..., kn)
            mode: Operation mode (MULTI_ROUND or SEGMENTED)
            amplitude: Amplitude parameter A for scoring function
            frequency: Frequency parameter ω for scoring function  
            phase: Phase parameter γ for scoring function
        """
        if not key or len(key) == 0:
            raise ValueError("Key must be a non-empty list of floats")
        
        self.key = np.array(key, dtype=np.float64)
        self.mode = mode
        self.n = len(key)
        
        # Scoring function parameters
        self.amplitude = amplitude
        self.frequency = frequency
        self.phase = phase
        
        # Thread lock for parallel processing
        self._lock = threading.Lock()
    
    def _scoring_function(self, key_component: float, indices: np.ndarray) -> np.ndarray:
        """
        Core scoring function: score_j(i) = A * sin(k_j * γ + i * ω) + i
        
        Args:
            key_component: Key component k_j
            indices: Array of indices i
            
        Returns:
            Array of scores for each index
        """
        sine_term = self.amplitude * np.sin(key_component * self.phase + indices * self.frequency)
        return sine_term + indices
    
    def _generate_permutation_map(self, key_component: float, data_size: int) -> np.ndarray:
        """
        Generate permutation map from scores
        
        Args:
            key_component: Key component to use for scoring
            data_size: Size of data to permute
            
        Returns:
            Permutation array where output[i] = original_index
        """
        indices = np.arange(data_size)
        scores = self._scoring_function(key_component, indices)
        
        # Sort indices by scores to create permutation map
        permutation_map = np.argsort(scores)
        return permutation_map
    
    def _generate_substitution_mask(self, key_component: float, data_size: int) -> np.ndarray:
        """
        Generate substitution mask from scores
        
        Args:
            key_component: Key component to use for scoring
            data_size: Size of data for substitution
            
        Returns:
            Boolean mask indicating which bits to flip
        """
        indices = np.arange(data_size)
        scores = self._scoring_function(key_component, indices)
        
        # Use fractional part of scores to determine substitution
        # If fractional part > 0.5, flip the bit
        fractional_scores = scores - np.floor(scores)
        substitution_mask = fractional_scores > 0.5
        return substitution_mask
    
    def _permute_data(self, data: np.ndarray, permutation_map: np.ndarray, inverse: bool = False) -> np.ndarray:
        """
        Apply permutation to data
        
        Args:
            data: Data to permute
            permutation_map: Permutation mapping
            inverse: If True, apply inverse permutation
            
        Returns:
            Permuted data
        """
        if inverse:
            # Create inverse permutation
            inverse_map = np.empty_like(permutation_map)
            inverse_map[permutation_map] = np.arange(len(permutation_map))
            return data[inverse_map]
        else:
            return data[permutation_map]
    
    def _substitute_data(self, data: np.ndarray, substitution_mask: np.ndarray) -> np.ndarray:
        """
        Apply substitution (XOR) to data
        
        Args:
            data: Data to substitute
            substitution_mask: Boolean mask for substitution
            
        Returns:
            Substituted data
        """
        # Convert mask to same dtype as data for XOR operation
        mask_values = substitution_mask.astype(data.dtype)
        return data ^ mask_values
    
    def _transform_round(self, data: np.ndarray, key_component: float, inverse: bool = False) -> np.ndarray:
        """
        Apply one round of transformation (permutation + substitution)
        
        Args:
            data: Data to transform
            key_component: Key component for this round
            inverse: If True, apply inverse transformation
            
        Returns:
            Transformed data
        """
        data_size = len(data)
        permutation_map = self._generate_permutation_map(key_component, data_size)
        substitution_mask = self._generate_substitution_mask(key_component, data_size)
        
        if inverse:
            # For decryption: inverse substitution then inverse permutation
            data = self._substitute_data(data, substitution_mask)
            data = self._permute_data(data, permutation_map, inverse=True)
        else:
            # For encryption: permutation then substitution
            data = self._permute_data(data, permutation_map, inverse=False)
            data = self._substitute_data(data, substitution_mask)
        
        return data
    
    def _encrypt_multi_round(self, data: np.ndarray) -> np.ndarray:
        """
        Encrypt using Multi-Round Mode
        
        Args:
            data: Plaintext data
            
        Returns:
            Encrypted data
        """
        current_data = data.copy()
        
        # Apply n rounds sequentially
        for i in range(self.n):
            current_data = self._transform_round(current_data, self.key[i], inverse=False)
        
        return current_data
    
    def _decrypt_multi_round(self, data: np.ndarray) -> np.ndarray:
        """
        Decrypt using Multi-Round Mode
        
        Args:
            data: Encrypted data
            
        Returns:
            Decrypted data
        """
        current_data = data.copy()
        
        # Apply inverse rounds in reverse order
        for i in range(self.n - 1, -1, -1):
            current_data = self._transform_round(current_data, self.key[i], inverse=True)
        
        return current_data
    
    def _process_segment(self, args: Tuple[np.ndarray, float, bool]) -> np.ndarray:
        """
        Process a single segment (for parallel processing)
        
        Args:
            args: Tuple of (segment_data, key_component, inverse)
            
        Returns:
            Processed segment
        """
        segment_data, key_component, inverse = args
        return self._transform_round(segment_data, key_component, inverse=inverse)
    
    def _encrypt_segmented(self, data: np.ndarray) -> np.ndarray:
        """
        Encrypt using Segmented Mode
        
        Args:
            data: Plaintext data
            
        Returns:
            Encrypted data
        """
        data_size = len(data)
        segment_size = data_size // self.n
        
        if segment_size == 0:
            raise ValueError(f"Data too small for {self.n} segments")
        
        segments = []
        
        # Prepare segments and arguments for parallel processing
        segment_args = []
        for i in range(self.n):
            start_idx = i * segment_size
            if i == self.n - 1:  # Last segment gets remainder
                end_idx = data_size
            else:
                end_idx = (i + 1) * segment_size
            
            segment = data[start_idx:end_idx]
            segment_args.append((segment, self.key[i], False))
        
        # Process segments in parallel
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.n) as executor:
            processed_segments = list(executor.map(self._process_segment, segment_args))
        
        # Concatenate processed segments
        return np.concatenate(processed_segments)
    
    def _decrypt_segmented(self, data: np.ndarray) -> np.ndarray:
        """
        Decrypt using Segmented Mode
        
        Args:
            data: Encrypted data
            
        Returns:
            Decrypted data
        """
        data_size = len(data)
        segment_size = data_size // self.n
        
        if segment_size == 0:
            raise ValueError(f"Data too small for {self.n} segments")
        
        # Prepare segments and arguments for parallel processing
        segment_args = []
        for i in range(self.n):
            start_idx = i * segment_size
            if i == self.n - 1:  # Last segment gets remainder
                end_idx = data_size
            else:
                end_idx = (i + 1) * segment_size
            
            segment = data[start_idx:end_idx]
            segment_args.append((segment, self.key[i], True))
        
        # Process segments in parallel
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.n) as executor:
            processed_segments = list(executor.map(self._process_segment, segment_args))
        
        # Concatenate processed segments
        return np.concatenate(processed_segments)
    
    def encrypt(self, data: Union[bytes, bytearray, str]) -> bytes:
        """
        Encrypt data using the configured mode
        
        Args:
            data: Data to encrypt (bytes, bytearray, or string)
            
        Returns:
            Encrypted data as bytes
        """
        # Convert input to numpy array
        if isinstance(data, str):
            data_bytes = data.encode('utf-8')
        else:
            data_bytes = bytes(data)
        
        data_array = np.frombuffer(data_bytes, dtype=np.uint8)
        
        # Encrypt based on mode
        if self.mode == OperationMode.MULTI_ROUND:
            encrypted_array = self._encrypt_multi_round(data_array)
        elif self.mode == OperationMode.SEGMENTED:
            encrypted_array = self._encrypt_segmented(data_array)
        else:
            raise ValueError(f"Unsupported operation mode: {self.mode}")
        
        return encrypted_array.tobytes()
    
    def decrypt(self, data: bytes) -> bytes:
        """
        Decrypt data using the configured mode
        
        Args:
            data: Encrypted data as bytes
            
        Returns:
            Decrypted data as bytes
        """
        data_array = np.frombuffer(data, dtype=np.uint8)
        
        # Decrypt based on mode
        if self.mode == OperationMode.MULTI_ROUND:
            decrypted_array = self._decrypt_multi_round(data_array)
        elif self.mode == OperationMode.SEGMENTED:
            decrypted_array = self._decrypt_segmented(data_array)
        else:
            raise ValueError(f"Unsupported operation mode: {self.mode}")
        
        return decrypted_array.tobytes()
    
    def encrypt_file(self, input_path: str, output_path: str) -> None:
        """
        Encrypt a file
        
        Args:
            input_path: Path to input file
            output_path: Path to output encrypted file
        """
        with open(input_path, 'rb') as f:
            data = f.read()
        
        encrypted_data = self.encrypt(data)
        
        with open(output_path, 'wb') as f:
            f.write(encrypted_data)
    
    def decrypt_file(self, input_path: str, output_path: str) -> None:
        """
        Decrypt a file
        
        Args:
            input_path: Path to encrypted file
            output_path: Path to output decrypted file
        """
        with open(input_path, 'rb') as f:
            encrypted_data = f.read()
        
        decrypted_data = self.decrypt(encrypted_data)
        
        with open(output_path, 'wb') as f:
            f.write(decrypted_data) 