"""
High-Performance SineScramble Cipher Implementation

This module contains an optimized SineScramble cipher implementation designed for
maximum performance using JIT compilation, vectorization, and memory optimization.
"""

import math
import time
import numpy as np
from typing import List, Tuple, Union
import concurrent.futures
import threading
from numba import jit, prange, types
from numba.typed import Dict

# Import the enum from the original module to ensure compatibility
try:
    from .cipher import OperationMode
except ImportError:
    from cipher import OperationMode


# JIT-compiled core functions for maximum performance
@jit(nopython=True, cache=True, fastmath=True)
def _scoring_function_jit(key_component: float, indices: np.ndarray, 
                         amplitude: float, frequency: float, phase: float) -> np.ndarray:
    """
    JIT-compiled scoring function for maximum performance
    score_j(i) = A * sin(k_j * γ + i * ω) + i
    """
    sine_arg = key_component * phase + indices * frequency
    return amplitude * np.sin(sine_arg) + indices


@jit(nopython=True, cache=True)
def _generate_permutation_map_jit(key_component: float, data_size: int,
                                 amplitude: float, frequency: float, phase: float) -> np.ndarray:
    """JIT-compiled permutation map generation"""
    indices = np.arange(data_size, dtype=np.float64)
    scores = _scoring_function_jit(key_component, indices, amplitude, frequency, phase)
    return np.argsort(scores).astype(np.int64)


@jit(nopython=True, cache=True, fastmath=True)
def _generate_substitution_mask_jit(key_component: float, data_size: int,
                                   amplitude: float, frequency: float, phase: float) -> np.ndarray:
    """JIT-compiled substitution mask generation"""
    indices = np.arange(data_size, dtype=np.float64)
    scores = _scoring_function_jit(key_component, indices, amplitude, frequency, phase)
    fractional_scores = scores - np.floor(scores)
    return fractional_scores > 0.5


@jit(nopython=True, cache=True)
def _permute_data_jit(data: np.ndarray, permutation_map: np.ndarray, inverse: bool = False) -> np.ndarray:
    """JIT-compiled data permutation"""
    if inverse:
        # Create inverse permutation in-place
        inverse_map = np.empty(len(permutation_map), dtype=np.int64)
        for i in range(len(permutation_map)):
            inverse_map[permutation_map[i]] = i
        return data[inverse_map]
    else:
        return data[permutation_map]


@jit(nopython=True, cache=True)
def _substitute_data_jit(data: np.ndarray, substitution_mask: np.ndarray) -> np.ndarray:
    """JIT-compiled data substitution using XOR"""
    mask_values = substitution_mask.astype(data.dtype)
    return data ^ mask_values


@jit(nopython=True, cache=True)
def _transform_round_jit(data: np.ndarray, key_component: float, inverse: bool,
                        amplitude: float, frequency: float, phase: float) -> np.ndarray:
    """JIT-compiled single round transformation"""
    data_size = len(data)
    permutation_map = _generate_permutation_map_jit(key_component, data_size, amplitude, frequency, phase)
    substitution_mask = _generate_substitution_mask_jit(key_component, data_size, amplitude, frequency, phase)
    
    if inverse:
        # For decryption: inverse substitution then inverse permutation
        result = _substitute_data_jit(data, substitution_mask)
        result = _permute_data_jit(result, permutation_map, inverse=True)
    else:
        # For encryption: permutation then substitution
        result = _permute_data_jit(data, permutation_map, inverse=False)
        result = _substitute_data_jit(result, substitution_mask)
    
    return result


@jit(nopython=True, cache=True)
def _encrypt_multi_round_jit(data: np.ndarray, key: np.ndarray,
                           amplitude: float, frequency: float, phase: float) -> np.ndarray:
    """JIT-compiled multi-round encryption"""
    current_data = data.copy()
    n = len(key)
    
    for i in range(n):
        current_data = _transform_round_jit(current_data, key[i], False, amplitude, frequency, phase)
    
    return current_data


@jit(nopython=True, cache=True)
def _decrypt_multi_round_jit(data: np.ndarray, key: np.ndarray,
                           amplitude: float, frequency: float, phase: float) -> np.ndarray:
    """JIT-compiled multi-round decryption"""
    current_data = data.copy()
    n = len(key)
    
    for i in range(n - 1, -1, -1):
        current_data = _transform_round_jit(current_data, key[i], True, amplitude, frequency, phase)
    
    return current_data


@jit(nopython=True, cache=True, parallel=True)
def _encrypt_segmented_jit(data: np.ndarray, key: np.ndarray,
                          amplitude: float, frequency: float, phase: float) -> np.ndarray:
    """JIT-compiled segmented encryption with parallel processing"""
    n = len(key)
    data_size = len(data)
    segment_size = data_size // n
    
    result = np.empty_like(data)
    
    # Process segments in parallel
    for i in prange(n):
        start_idx = i * segment_size
        if i == n - 1:  # Last segment gets remainder
            end_idx = data_size
        else:
            end_idx = (i + 1) * segment_size
        
        segment = data[start_idx:end_idx]
        transformed = _transform_round_jit(segment, key[i], False, amplitude, frequency, phase)
        result[start_idx:end_idx] = transformed
    
    return result


@jit(nopython=True, cache=True, parallel=True)
def _decrypt_segmented_jit(data: np.ndarray, key: np.ndarray,
                          amplitude: float, frequency: float, phase: float) -> np.ndarray:
    """JIT-compiled segmented decryption with parallel processing"""
    n = len(key)
    data_size = len(data)
    segment_size = data_size // n
    
    result = np.empty_like(data)
    
    # Process segments in parallel
    for i in prange(n):
        start_idx = i * segment_size
        if i == n - 1:  # Last segment gets remainder
            end_idx = data_size
        else:
            end_idx = (i + 1) * segment_size
        
        segment = data[start_idx:end_idx]
        transformed = _transform_round_jit(segment, key[i], True, amplitude, frequency, phase)
        result[start_idx:end_idx] = transformed
    
    return result


class OptimizedSineScrambleCipher:
    """
    High-performance SineScramble symmetric cipher implementation
    
    Optimized for maximum speed using JIT compilation, vectorization,
    and memory optimization techniques.
    """
    
    def __init__(self, key: List[float], mode: OperationMode, 
                 amplitude: float = 100.0, frequency: float = 0.1, 
                 phase: float = 1.0):
        """
        Initialize optimized SineScramble cipher
        
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
        self.amplitude = float(amplitude)
        self.frequency = float(frequency)
        self.phase = float(phase)
        
        # Pre-warm JIT compilation by running dummy operations
        self._warm_jit()
    
    def _warm_jit(self):
        """Pre-warm JIT compilation with small dummy data"""
        dummy_data = np.array([1, 2, 3, 4], dtype=np.uint8)
        dummy_key = self.key[:min(2, len(self.key))]
        
        try:
            # Warm up all JIT functions
            _encrypt_multi_round_jit(dummy_data, dummy_key, self.amplitude, self.frequency, self.phase)
            _decrypt_multi_round_jit(dummy_data, dummy_key, self.amplitude, self.frequency, self.phase)
            if len(dummy_data) >= self.n:
                _encrypt_segmented_jit(dummy_data, dummy_key, self.amplitude, self.frequency, self.phase)
                _decrypt_segmented_jit(dummy_data, dummy_key, self.amplitude, self.frequency, self.phase)
        except:
            pass  # JIT warming may fail with very small data
    
    def encrypt(self, data: Union[bytes, bytearray, str]) -> bytes:
        """
        Encrypt data using the configured mode with maximum performance
        
        Args:
            data: Data to encrypt (bytes, bytearray, or string)
            
        Returns:
            Encrypted data as bytes
        """
        # Convert input to numpy array efficiently
        if isinstance(data, str):
            data_bytes = data.encode('utf-8')
        else:
            data_bytes = bytes(data)
        
        # Use numpy frombuffer for zero-copy conversion
        data_array = np.frombuffer(data_bytes, dtype=np.uint8)
        
        # Encrypt based on mode using JIT-compiled functions
        if self.mode == OperationMode.MULTI_ROUND:
            encrypted_array = _encrypt_multi_round_jit(
                data_array, self.key, self.amplitude, self.frequency, self.phase
            )
        elif self.mode == OperationMode.SEGMENTED:
            if len(data_array) < self.n:
                raise ValueError(f"Data too small for {self.n} segments")
            encrypted_array = _encrypt_segmented_jit(
                data_array, self.key, self.amplitude, self.frequency, self.phase
            )
        else:
            raise ValueError(f"Unsupported operation mode: {self.mode}")
        
        return encrypted_array.tobytes()
    
    def decrypt(self, data: bytes) -> bytes:
        """
        Decrypt data using the configured mode with maximum performance
        
        Args:
            data: Encrypted data as bytes
            
        Returns:
            Decrypted data as bytes
        """
        # Use numpy frombuffer for zero-copy conversion
        data_array = np.frombuffer(data, dtype=np.uint8)
        
        # Decrypt based on mode using JIT-compiled functions
        if self.mode == OperationMode.MULTI_ROUND:
            decrypted_array = _decrypt_multi_round_jit(
                data_array, self.key, self.amplitude, self.frequency, self.phase
            )
        elif self.mode == OperationMode.SEGMENTED:
            if len(data_array) < self.n:
                raise ValueError(f"Data too small for {self.n} segments")
            decrypted_array = _decrypt_segmented_jit(
                data_array, self.key, self.amplitude, self.frequency, self.phase
            )
        else:
            raise ValueError(f"Unsupported operation mode: {self.mode}")
        
        return decrypted_array.tobytes()
    
    def encrypt_file(self, input_path: str, output_path: str, chunk_size: int = 64 * 1024 * 1024) -> None:
        """
        Encrypt a file with streaming processing for large files
        
        Args:
            input_path: Path to input file
            output_path: Path to output encrypted file
            chunk_size: Size of chunks to process (default: 64MB)
        """
        with open(input_path, 'rb') as infile, open(output_path, 'wb') as outfile:
            while True:
                chunk = infile.read(chunk_size)
                if not chunk:
                    break
                
                # Ensure chunk size is compatible with segmented mode
                if self.mode == OperationMode.SEGMENTED and len(chunk) < self.n:
                    # Pad small chunks to minimum size
                    padding_needed = self.n - len(chunk)
                    chunk += b'\x00' * padding_needed
                    # Note: This is a simplified approach; production code would need proper padding handling
                
                encrypted_chunk = self.encrypt(chunk)
                outfile.write(encrypted_chunk)
    
    def decrypt_file(self, input_path: str, output_path: str, chunk_size: int = 64 * 1024 * 1024) -> None:
        """
        Decrypt a file with streaming processing for large files
        
        Args:
            input_path: Path to encrypted file
            output_path: Path to output decrypted file
            chunk_size: Size of chunks to process (default: 64MB)
        """
        with open(input_path, 'rb') as infile, open(output_path, 'wb') as outfile:
            while True:
                chunk = infile.read(chunk_size)
                if not chunk:
                    break
                
                decrypted_chunk = self.decrypt(chunk)
                outfile.write(decrypted_chunk)


# Additional performance utilities
def benchmark_scoring_function(key_component: float, data_size: int, iterations: int,
                             amplitude: float = 100.0, frequency: float = 0.1, phase: float = 1.0) -> float:
    """Benchmark the scoring function performance"""
    indices = np.arange(data_size, dtype=np.float64)
    
    start_time = time.time()
    for _ in range(iterations):
        scores = _scoring_function_jit(key_component, indices, amplitude, frequency, phase)
    end_time = time.time()
    
    return end_time - start_time


def get_optimal_chunk_size(data_size: int, available_memory_mb: int = 1024) -> int:
    """Calculate optimal chunk size based on available memory"""
    max_chunk_size = available_memory_mb * 1024 * 1024
    
    # Use power of 2 sizes for better memory alignment
    optimal_size = min(max_chunk_size, data_size)
    
    # Round down to nearest power of 2
    optimal_size = 2 ** int(math.log2(optimal_size))
    
    # Ensure minimum chunk size
    return max(optimal_size, 1024)


def profile_cipher_performance(cipher, data_sizes: List[int], iterations: int = 10) -> dict:
    """Profile cipher performance across different data sizes"""
    import time
    
    results = {}
    
    for size in data_sizes:
        test_data = np.random.randint(0, 256, size, dtype=np.uint8).tobytes()
        
        # Measure encryption
        encrypt_times = []
        for _ in range(iterations):
            start = time.perf_counter()
            encrypted = cipher.encrypt(test_data)
            end = time.perf_counter()
            encrypt_times.append(end - start)
        
        # Measure decryption
        decrypt_times = []
        for _ in range(iterations):
            start = time.perf_counter()
            decrypted = cipher.decrypt(encrypted)
            end = time.perf_counter()
            decrypt_times.append(end - start)
        
        avg_encrypt_time = sum(encrypt_times) / len(encrypt_times)
        avg_decrypt_time = sum(decrypt_times) / len(decrypt_times)
        
        results[size] = {
            'encrypt_time': avg_encrypt_time,
            'decrypt_time': avg_decrypt_time,
            'encrypt_throughput_mbps': (size / (1024 * 1024)) / avg_encrypt_time,
            'decrypt_throughput_mbps': (size / (1024 * 1024)) / avg_decrypt_time,
            'correctness': test_data == decrypted
        }
    
    return results 