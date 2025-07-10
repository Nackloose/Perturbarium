"""
Turbo SineScramble Cipher Implementation

Ultra-high-performance version with aggressive optimizations for bare metal speed.
"""

import numpy as np
from numba import jit, prange
import math

# Import the enum from the original module
try:
    from .cipher import OperationMode
except ImportError:
    from cipher import OperationMode


# Pre-compiled ultra-fast core functions
@jit(nopython=True, cache=True, fastmath=True, inline='always')
def _turbo_scoring_function(key_component, indices, amplitude, frequency, phase):
    """Ultra-fast scoring function with aggressive optimizations"""
    # Use fast math approximations
    sine_arg = key_component * phase + indices * frequency
    return amplitude * np.sin(sine_arg) + indices


@jit(nopython=True, cache=True, fastmath=True, parallel=True)
def _turbo_permute_and_substitute(data, key_component, amplitude, frequency, phase, inverse=False):
    """Combined permute and substitute in single pass for maximum efficiency"""
    data_size = len(data)
    
    # Pre-allocate all arrays at once
    indices = np.arange(data_size, dtype=np.float64)
    scores = _turbo_scoring_function(key_component, indices, amplitude, frequency, phase)
    
    # Generate permutation map
    permutation_map = np.argsort(scores).astype(np.int64)
    
    # Generate substitution mask
    fractional_scores = scores - np.floor(scores)
    substitution_mask = (fractional_scores > 0.5).astype(data.dtype)
    
    # Create result array
    result = np.empty_like(data)
    
    if inverse:
        # Inverse: substitute then inverse permute
        temp = data ^ substitution_mask
        # Inverse permutation
        for i in prange(data_size):
            result[permutation_map[i]] = temp[i]
    else:
        # Forward: permute then substitute
        for i in prange(data_size):
            result[i] = data[permutation_map[i]]
        result = result ^ substitution_mask
    
    return result


@jit(nopython=True, cache=True, fastmath=True)
def _turbo_multi_round(data, key, amplitude, frequency, phase, inverse=False):
    """Ultra-fast multi-round transformation"""
    current_data = data.copy()
    n = len(key)
    
    if inverse:
        for i in range(n - 1, -1, -1):
            current_data = _turbo_permute_and_substitute(
                current_data, key[i], amplitude, frequency, phase, True
            )
    else:
        for i in range(n):
            current_data = _turbo_permute_and_substitute(
                current_data, key[i], amplitude, frequency, phase, False
            )
    
    return current_data


@jit(nopython=True, cache=True, fastmath=True, parallel=True)
def _turbo_segmented(data, key, amplitude, frequency, phase, inverse=False):
    """Ultra-fast segmented transformation with optimal parallelization"""
    n = len(key)
    data_size = len(data)
    segment_size = data_size // n
    
    result = np.empty_like(data)
    
    # Process all segments in parallel
    for i in prange(n):
        start_idx = i * segment_size
        if i == n - 1:  # Last segment gets remainder
            end_idx = data_size
        else:
            end_idx = (i + 1) * segment_size
        
        segment = data[start_idx:end_idx]
        transformed = _turbo_permute_and_substitute(
            segment, key[i], amplitude, frequency, phase, inverse
        )
        result[start_idx:end_idx] = transformed
    
    return result


class TurboSineScrambleCipher:
    """
    Turbo SineScramble cipher - Ultimate performance implementation
    
    Extreme optimizations:
    - Minimal function call overhead
    - Aggressive JIT compilation
    - Optimized memory access patterns
    - Combined operations for cache efficiency
    - Parallel processing at lowest level
    """
    
    def __init__(self, key, mode, amplitude=100.0, frequency=0.1, phase=1.0):
        """Initialize turbo cipher"""
        self.key_array = np.array(key, dtype=np.float64)
        self.mode = mode
        self.amplitude = float(amplitude)
        self.frequency = float(frequency)
        self.phase = float(phase)
        
        # Force JIT compilation
        self._warm_turbo()
    
    def _warm_turbo(self):
        """Warm up all JIT functions"""
        dummy_data = np.array([1, 2, 3, 4, 5, 6, 7, 8], dtype=np.uint8)
        dummy_key = self.key_array[:min(2, len(self.key_array))]
        
        try:
            # Warm up all functions
            _turbo_multi_round(dummy_data, dummy_key, self.amplitude, self.frequency, self.phase)
            if len(dummy_data) >= len(self.key_array):
                _turbo_segmented(dummy_data, self.key_array, self.amplitude, self.frequency, self.phase)
        except:
            pass
    
    def encrypt(self, data):
        """Turbo-speed encryption"""
        # Convert to numpy array with zero-copy when possible
        if isinstance(data, str):
            data_bytes = data.encode('utf-8')
        else:
            data_bytes = bytes(data)
        
        data_array = np.frombuffer(data_bytes, dtype=np.uint8)
        
        # Choose optimized path based on mode
        if self.mode == OperationMode.MULTI_ROUND:
            result = _turbo_multi_round(
                data_array, self.key_array, self.amplitude, self.frequency, self.phase, False
            )
        elif self.mode == OperationMode.SEGMENTED:
            if len(data_array) < len(self.key_array):
                raise ValueError(f"Data too small for {len(self.key_array)} segments")
            result = _turbo_segmented(
                data_array, self.key_array, self.amplitude, self.frequency, self.phase, False
            )
        else:
            raise ValueError(f"Unsupported mode: {self.mode}")
        
        return result.tobytes()
    
    def decrypt(self, data):
        """Turbo-speed decryption"""
        data_array = np.frombuffer(data, dtype=np.uint8)
        
        # Choose optimized path based on mode
        if self.mode == OperationMode.MULTI_ROUND:
            result = _turbo_multi_round(
                data_array, self.key_array, self.amplitude, self.frequency, self.phase, True
            )
        elif self.mode == OperationMode.SEGMENTED:
            if len(data_array) < len(self.key_array):
                raise ValueError(f"Data too small for {len(self.key_array)} segments")
            result = _turbo_segmented(
                data_array, self.key_array, self.amplitude, self.frequency, self.phase, True
            )
        else:
            raise ValueError(f"Unsupported mode: {self.mode}")
        
        return result.tobytes()


# Utility function for maximum performance measurement
@jit(nopython=True, cache=True, fastmath=True)
def benchmark_raw_throughput(data_size, iterations):
    """Benchmark raw computational throughput"""
    data = np.random.randint(0, 256, size=data_size, dtype=np.uint8)
    key = np.array([1.5, 2.5, 3.5, 4.5], dtype=np.float64)
    
    total_ops = 0
    for _ in range(iterations):
        result = _turbo_segmented(data, key, 100.0, 0.1, 1.0, False)
        total_ops += len(result)
    
    return total_ops


def ultra_performance_test():
    """Test ultra-high performance capabilities"""
    import time
    
    print("🏎️  TURBO PERFORMANCE TEST")
    print("=" * 40)
    
    from utils import generate_random_key
    
    key = generate_random_key(4, seed=42)
    
    # Test with large data
    test_sizes = [
        100 * 1024 * 1024,   # 100MB
        200 * 1024 * 1024,   # 200MB
    ]
    
    cipher = TurboSineScrambleCipher(key, OperationMode.SEGMENTED)
    
    for size in test_sizes:
        mb_size = size // (1024 * 1024)
        print(f"\n🚀 Testing {mb_size}MB...")
        
        test_data = np.random.randint(0, 256, size=size, dtype=np.uint8).tobytes()
        
        # Measure encryption
        start = time.perf_counter()
        encrypted = cipher.encrypt(test_data)
        encrypt_time = time.perf_counter() - start
        
        # Measure decryption
        start = time.perf_counter()
        decrypted = cipher.decrypt(encrypted)
        decrypt_time = time.perf_counter() - start
        
        encrypt_mbps = mb_size / encrypt_time
        decrypt_mbps = mb_size / decrypt_time
        
        print(f"  Encrypt: {encrypt_time:.3f}s → {encrypt_mbps:.1f} MB/s")
        print(f"  Decrypt: {decrypt_time:.3f}s → {decrypt_mbps:.1f} MB/s")
        print(f"  Correct: {test_data == decrypted}")


if __name__ == "__main__":
    ultra_performance_test()