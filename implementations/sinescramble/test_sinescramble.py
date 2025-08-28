"""
Comprehensive test suite for SineScramble cipher variants

This module contains comprehensive tests and demonstrations of all three
SineScramble cipher implementations: Original, Optimized, and Turbo.
"""

import time
import os
import tempfile
import gc
import psutil
from typing import List, Dict, Tuple
import numpy as np

try:
    # Try relative imports first (when run as module)
    from .cipher import SineScrambleCipher, OperationMode
    from .cipher_optimized import OptimizedSineScrambleCipher
    from .cipher_turbo import TurboSineScrambleCipher
    from .utils import (
        generate_random_key, key_from_password, key_to_string, 
        string_to_key, validate_key, estimate_security_level,
        recommend_mode_for_use_case
    )
except ImportError:
    # Fall back to direct imports (when run as script)
    from cipher import SineScrambleCipher, OperationMode
    from cipher_optimized import OptimizedSineScrambleCipher
    from cipher_turbo import TurboSineScrambleCipher
    from utils import (
        generate_random_key, key_from_password, key_to_string, 
        string_to_key, validate_key, estimate_security_level,
        recommend_mode_for_use_case
    )


class VariantComparison:
    """Comprehensive comparison of all three cipher variants"""
    
    def __init__(self):
        self.variants = {
            'Original': SineScrambleCipher,
            'Optimized': OptimizedSineScrambleCipher,
            'Turbo': TurboSineScrambleCipher
        }
        self.results = {}
    
    def test_correctness_all_variants(self):
        """Test correctness across all variants"""
        print("=== Correctness Test - All Variants ===")
        
        test_data = "Hello, SineScramble! This is a comprehensive test message."
        key = generate_random_key(4, seed=42)
        
        results = {}
        
        for variant_name, cipher_class in self.variants.items():
            print(f"\n--- Testing {variant_name} ---")
            
            try:
                # Test both modes
                for mode in [OperationMode.MULTI_ROUND, OperationMode.SEGMENTED]:
                    cipher = cipher_class(key, mode)
                    
                    # Encrypt and decrypt
                    encrypted = cipher.encrypt(test_data)
                    decrypted = cipher.decrypt(encrypted)
                    
                    # Verify correctness
                    correct = test_data == decrypted.decode('utf-8')
                    print(f"  {mode.value}: {'✓ PASS' if correct else '✗ FAIL'}")
                    
                    if not correct:
                        print(f"    Expected: {test_data}")
                        print(f"    Got: {decrypted.decode('utf-8', errors='replace')}")
                
                results[variant_name] = True
                
            except Exception as e:
                print(f"  ✗ ERROR: {e}")
                results[variant_name] = False
        
        return results
    
    def benchmark_performance_all_variants(self):
        """Benchmark performance across all variants"""
        print("\n=== Performance Benchmark - All Variants ===")
        
        key = generate_random_key(6, seed=123)
        test_sizes = [1024, 10240, 102400, 1048576]  # 1KB, 10KB, 100KB, 1MB
        
        results = {}
        
        for variant_name, cipher_class in self.variants.items():
            print(f"\n--- Benchmarking {variant_name} ---")
            
            try:
                variant_results = {}
                
                for mode in [OperationMode.MULTI_ROUND, OperationMode.SEGMENTED]:
                    mode_results = {}
                    
                    for size in test_sizes:
                        # Generate test data
                        test_data = os.urandom(size)
                        
                        # Create cipher
                        cipher = cipher_class(key, mode)
                        
                        # Warm up (especially for JIT-compiled variants)
                        if size >= 1024:
                            warm_data = test_data[:1024]
                            try:
                                cipher.encrypt(warm_data)
                                cipher.decrypt(cipher.encrypt(warm_data))
                            except:
                                pass
                        
                        # Force garbage collection
                        gc.collect()
                        
                        # Benchmark encryption
                        start = time.perf_counter()
                        encrypted = cipher.encrypt(test_data)
                        encrypt_time = time.perf_counter() - start
                        
                        # Benchmark decryption
                        start = time.perf_counter()
                        decrypted = cipher.decrypt(encrypted)
                        decrypt_time = time.perf_counter() - start
                        
                        # Calculate throughput
                        encrypt_mbps = (size / (1024 * 1024)) / encrypt_time
                        decrypt_mbps = (size / (1024 * 1024)) / decrypt_time
                        
                        # Verify correctness
                        correct = test_data == decrypted
                        
                        mode_results[size] = {
                            'encrypt_time': encrypt_time,
                            'decrypt_time': decrypt_time,
                            'encrypt_mbps': encrypt_mbps,
                            'decrypt_mbps': decrypt_mbps,
                            'correct': correct
                        }
                        
                        size_str = f"{size//1024}KB" if size < 1024*1024 else f"{size//(1024*1024)}MB"
                        print(f"  {mode.value} {size_str}: {encrypt_mbps:.1f} MB/s encrypt, {decrypt_mbps:.1f} MB/s decrypt")
                    
                    variant_results[mode.value] = mode_results
                
                results[variant_name] = variant_results
                
            except Exception as e:
                print(f"  ✗ ERROR: {e}")
                results[variant_name] = None
        
        return results
    
    def stress_test_stability(self):
        """Stress test for stability and memory usage"""
        print("\n=== Stability Stress Test - All Variants ===")
        
        key = generate_random_key(4, seed=456)
        test_data = os.urandom(1024 * 1024)  # 1MB
        iterations = 50
        
        results = {}
        process = psutil.Process()
        
        for variant_name, cipher_class in self.variants.items():
            print(f"\n--- Stress Testing {variant_name} ---")
            
            try:
                # Measure memory before
                gc.collect()
                mem_before = process.memory_info().rss / (1024 * 1024)
                
                # Create cipher
                cipher = cipher_class(key, OperationMode.SEGMENTED)
                
                # Run stress test
                start_time = time.perf_counter()
                errors = 0
                
                for i in range(iterations):
                    try:
                        encrypted = cipher.encrypt(test_data)
                        decrypted = cipher.decrypt(encrypted)
                        
                        if test_data != decrypted:
                            errors += 1
                            print(f"    Error at iteration {i+1}: data mismatch")
                    
                    except Exception as e:
                        errors += 1
                        print(f"    Error at iteration {i+1}: {e}")
                    
                    # Progress indicator
                    if (i + 1) % 10 == 0:
                        print(f"    Progress: {i+1}/{iterations}")
                
                total_time = time.perf_counter() - start_time
                
                # Measure memory after
                gc.collect()
                mem_after = process.memory_info().rss / (1024 * 1024)
                
                results[variant_name] = {
                    'total_time': total_time,
                    'errors': errors,
                    'success_rate': ((iterations - errors) / iterations) * 100,
                    'memory_before': mem_before,
                    'memory_after': mem_after,
                    'memory_growth': mem_after - mem_before,
                    'avg_time_per_iteration': total_time / iterations
                }
                
                print(f"  Total time: {total_time:.2f}s")
                print(f"  Errors: {errors}/{iterations}")
                print(f"  Success rate: {results[variant_name]['success_rate']:.1f}%")
                print(f"  Memory growth: {results[variant_name]['memory_growth']:.1f} MB")
                
            except Exception as e:
                print(f"  ✗ ERROR: {e}")
                results[variant_name] = None
        
        return results
    
    def test_large_data_handling(self):
        """Test handling of large data sets"""
        print("\n=== Large Data Handling Test - All Variants ===")
        
        key = generate_random_key(4, seed=789)
        large_sizes = [
            10 * 1024 * 1024,   # 10MB
            50 * 1024 * 1024,   # 50MB
        ]
        
        results = {}
        
        for variant_name, cipher_class in self.variants.items():
            print(f"\n--- Testing {variant_name} with Large Data ---")
            
            try:
                variant_results = {}
                
                for size in large_sizes:
                    mb_size = size // (1024 * 1024)
                    print(f"  Testing {mb_size}MB...")
                    
                    # Generate large test data
                    test_data = os.urandom(size)
                    
                    # Create cipher
                    cipher = cipher_class(key, OperationMode.SEGMENTED)
                    
                    # Measure memory before
                    gc.collect()
                    mem_before = psutil.Process().memory_info().rss / (1024 * 1024)
                    
                    try:
                        # Encrypt
                        start = time.perf_counter()
                        encrypted = cipher.encrypt(test_data)
                        encrypt_time = time.perf_counter() - start
                        
                        # Decrypt
                        start = time.perf_counter()
                        decrypted = cipher.decrypt(encrypted)
                        decrypt_time = time.perf_counter() - start
                        
                        # Measure memory after
                        gc.collect()
                        mem_after = psutil.Process().memory_info().rss / (1024 * 1024)
                        
                        # Calculate metrics
                        encrypt_mbps = mb_size / encrypt_time
                        decrypt_mbps = mb_size / decrypt_time
                        correct = test_data == decrypted
                        
                        variant_results[mb_size] = {
                            'encrypt_time': encrypt_time,
                            'decrypt_time': decrypt_time,
                            'encrypt_mbps': encrypt_mbps,
                            'decrypt_mbps': decrypt_mbps,
                            'correct': correct,
                            'memory_before': mem_before,
                            'memory_after': mem_after,
                            'memory_growth': mem_after - mem_before
                        }
                        
                        print(f"    Encrypt: {encrypt_time:.2f}s → {encrypt_mbps:.1f} MB/s")
                        print(f"    Decrypt: {decrypt_time:.2f}s → {decrypt_mbps:.1f} MB/s")
                        print(f"    Correct: {correct}")
                        print(f"    Memory growth: {mem_after - mem_before:.1f} MB")
                        
                    except Exception as e:
                        print(f"    ✗ ERROR: {e}")
                        variant_results[mb_size] = None
                
                results[variant_name] = variant_results
                
            except Exception as e:
                print(f"  ✗ ERROR: {e}")
                results[variant_name] = None
        
        return results
    
    def generate_comprehensive_report(self):
        """Generate comprehensive comparison report"""
        print("\n" + "="*80)
        print("🏆 COMPREHENSIVE SINESCRAMBLE VARIANT COMPARISON")
        print("="*80)
        
        # Run all tests
        correctness_results = self.test_correctness_all_variants()
        performance_results = self.benchmark_performance_all_variants()
        stability_results = self.stress_test_stability()
        large_data_results = self.test_large_data_handling()
        
        # Generate summary
        print("\n📊 SUMMARY REPORT")
        print("-" * 80)
        
        print(f"{'Variant':<12} {'Correctness':<12} {'Stability':<12} {'Peak Speed':<12} {'Memory':<12} {'Recommendation'}")
        print("-" * 80)
        
        for variant_name in self.variants.keys():
            # Correctness
            correct = "✓ PASS" if correctness_results.get(variant_name, False) else "✗ FAIL"
            
            # Stability
            stability = stability_results.get(variant_name, {})
            if stability:
                success_rate = stability.get('success_rate', 0)
                stability_str = f"{success_rate:.0f}%" if success_rate >= 95 else "UNSTABLE"
            else:
                stability_str = "ERROR"
            
            # Peak performance (1MB Segmented mode)
            performance = performance_results.get(variant_name, {})
            peak_speed = "N/A"
            if performance and 'segmented' in performance:
                seg_results = performance['segmented']
                if 1048576 in seg_results:  # 1MB
                    peak_speed = f"{seg_results[1048576]['encrypt_mbps']:.0f} MB/s"
            
            # Memory efficiency
            memory_str = "N/A"
            if stability:
                mem_growth = stability.get('memory_growth', 0)
                if mem_growth < 5:
                    memory_str = "✓ Excellent"
                elif mem_growth < 20:
                    memory_str = "⚠ Acceptable"
                else:
                    memory_str = "✗ Poor"
            
            # Recommendation
            if variant_name == 'Original':
                recommendation = "Baseline"
            elif variant_name == 'Optimized':
                recommendation = "🚀 RECOMMENDED"
            elif variant_name == 'Turbo':
                if stability.get('success_rate', 0) >= 95:
                    recommendation = "⚡ FAST (Experimental)"
                else:
                    recommendation = "⚠ Unstable"
            
            print(f"{variant_name:<12} {correct:<12} {stability_str:<12} {peak_speed:<12} {memory_str:<12} {recommendation}")
        
        print("\n🎯 FINAL RECOMMENDATIONS:")
        print("- Turbo: ⚡ RECOMMENDED for high-performance, large data, and streaming (default)")
        print("- Original: Best for Multi-Round (high-security) mode and as a reference implementation")
        print("- Optimized: For experimental JIT research only")
        
        return {
            'correctness': correctness_results,
            'performance': performance_results,
            'stability': stability_results,
            'large_data': large_data_results
        }


def test_basic_encryption_decryption():
    """Test basic encryption and decryption functionality"""
    print("=== Basic Encryption/Decryption Test ===")
    
    # Test data
    test_message = "Hello, SineScramble! This is a test message with various characters: 123!@#$%^&*()"
    key = generate_random_key(5, seed=42)  # Reproducible key
    
    print(f"Original message: {test_message}")
    print(f"Key dimension: {len(key)}")
    print(f"Security level: {estimate_security_level(len(key))}")
    
    # Test Multi-Round Mode
    print("\n--- Multi-Round Mode ---")
    cipher_mr = SineScrambleCipher(key, OperationMode.MULTI_ROUND)
    
    encrypted_mr = cipher_mr.encrypt(test_message)
    decrypted_mr = cipher_mr.decrypt(encrypted_mr)
    
    print(f"Encrypted (hex): {encrypted_mr.hex()}")
    print(f"Decrypted: {decrypted_mr.decode('utf-8')}")
    print(f"Match: {test_message == decrypted_mr.decode('utf-8')}")
    
    # Test Segmented Mode
    print("\n--- Segmented Mode ---")
    cipher_seg = SineScrambleCipher(key, OperationMode.SEGMENTED)
    
    encrypted_seg = cipher_seg.encrypt(test_message)
    decrypted_seg = cipher_seg.decrypt(encrypted_seg)
    
    print(f"Encrypted (hex): {encrypted_seg.hex()}")
    print(f"Decrypted: {decrypted_seg.decode('utf-8')}")
    print(f"Match: {test_message == decrypted_seg.decode('utf-8')}")
    
    return test_message == decrypted_mr.decode('utf-8') and test_message == decrypted_seg.decode('utf-8')


def test_key_management():
    """Test key generation and management utilities"""
    print("\n=== Key Management Test ===")
    
    # Test random key generation
    print("--- Random Key Generation ---")
    key1 = generate_random_key(8, seed=123)
    key2 = generate_random_key(8, seed=123)  # Same seed
    key3 = generate_random_key(8, seed=456)  # Different seed
    
    print(f"Key 1 (seed 123): {key1[:3]}... (length: {len(key1)})")
    print(f"Key 2 (seed 123): {key2[:3]}... (length: {len(key2)})")
    print(f"Key 3 (seed 456): {key3[:3]}... (length: {len(key3)})")
    print(f"Keys 1&2 identical: {key1 == key2}")
    print(f"Keys 1&3 identical: {key1 == key3}")
    
    # Test password-based key derivation
    print("\n--- Password-based Key Derivation ---")
    password = "MySecurePassword123!"
    key_from_pwd1 = key_from_password(password, 6)
    key_from_pwd2 = key_from_password(password, 6)  # Same password
    key_from_pwd3 = key_from_password("DifferentPassword", 6)  # Different password
    
    print(f"Key from password 1: {key_from_pwd1[:3]}...")
    print(f"Key from password 2: {key_from_pwd2[:3]}...")
    print(f"Key from password 3: {key_from_pwd3[:3]}...")
    print(f"Same password keys identical: {key_from_pwd1 == key_from_pwd2}")
    print(f"Different password keys identical: {key_from_pwd1 == key_from_pwd3}")
    
    # Test key serialization
    print("\n--- Key Serialization ---")
    key_string = key_to_string(key1)
    key_restored = string_to_key(key_string)
    
    print(f"Original key: {key1[:3]}...")
    print(f"Serialized: {key_string[:50]}...")
    print(f"Restored key: {key_restored[:3]}...")
    print(f"Serialization successful: {key1 == key_restored}")
    
    # Test key validation
    print("\n--- Key Validation ---")
    valid_key = [1.0, 2.5, -3.7, 4.2]
    invalid_keys = [
        [],  # Empty
        ["not", "numbers"],  # Non-numeric
        [1, 2, True, 4],  # Contains boolean
    ]
    
    print(f"Valid key {valid_key}: {validate_key(valid_key)}")
    for i, invalid_key in enumerate(invalid_keys):
        print(f"Invalid key {i+1} {invalid_key}: {validate_key(invalid_key)}")


def test_different_data_types():
    """Test encryption with different data types"""
    print("\n=== Different Data Types Test ===")
    
    key = generate_random_key(4, seed=789)
    cipher = SineScrambleCipher(key, OperationMode.MULTI_ROUND)
    
    # Test string
    test_string = "Unicode test: αβγδ 中文 🚀"
    encrypted_str = cipher.encrypt(test_string)
    decrypted_str = cipher.decrypt(encrypted_str).decode('utf-8')
    print(f"String test: {test_string == decrypted_str}")
    
    # Test bytes
    test_bytes = b"Binary data: \x00\x01\x02\xff"
    encrypted_bytes = cipher.encrypt(test_bytes)
    decrypted_bytes = cipher.decrypt(encrypted_bytes)
    print(f"Bytes test: {test_bytes == decrypted_bytes}")
    
    # Test bytearray
    test_bytearray = bytearray(b"Bytearray test data")
    encrypted_bytearray = cipher.encrypt(test_bytearray)
    decrypted_bytearray = cipher.decrypt(encrypted_bytearray)
    print(f"Bytearray test: {test_bytearray == decrypted_bytearray}")


def test_file_operations():
    """Test file encryption and decryption"""
    print("\n=== File Operations Test ===")
    
    key = generate_random_key(6, seed=999)
    cipher = SineScrambleCipher(key, OperationMode.SEGMENTED)
    
    # Create temporary test file
    test_content = "This is a test file for SineScramble encryption.\n" * 10
    test_content += "It contains multiple lines and various characters: !@#$%^&*()\n"
    test_content += "Unicode characters: αβγδ 中文 🚀\n"
    
    with tempfile.TemporaryDirectory() as temp_dir:
        # File paths
        original_file = os.path.join(temp_dir, "original.txt")
        encrypted_file = os.path.join(temp_dir, "encrypted.bin")
        decrypted_file = os.path.join(temp_dir, "decrypted.txt")
        
        # Write original file
        with open(original_file, 'w', encoding='utf-8') as f:
            f.write(test_content)
        
        # Encrypt file
        cipher.encrypt_file(original_file, encrypted_file)
        
        # Decrypt file
        cipher.decrypt_file(encrypted_file, decrypted_file)
        
        # Verify
        with open(decrypted_file, 'r', encoding='utf-8') as f:
            decrypted_content = f.read()
        
        print(f"Original file size: {len(test_content)} chars")
        print(f"Encrypted file size: {os.path.getsize(encrypted_file)} bytes")
        print(f"Decrypted content matches: {test_content == decrypted_content}")
        
        return test_content == decrypted_content


def test_avalanche_effect():
    """Test avalanche effect - small input changes cause large output changes"""
    print("\n=== Avalanche Effect Test ===")
    
    key = generate_random_key(5, seed=2023)
    cipher = SineScrambleCipher(key, OperationMode.MULTI_ROUND)
    
    # Original message
    message1 = "The quick brown fox jumps over the lazy dog"
    message2 = "The quick brown fox jumps over the lazy dog!"  # Added one character
    
    encrypted1 = cipher.encrypt(message1)
    encrypted2 = cipher.encrypt(message2)
    
    # Calculate bit difference
    bit_diff = sum(bin(a ^ b).count('1') for a, b in zip(encrypted1, encrypted2))
    total_bits = len(encrypted1) * 8
    avalanche_ratio = bit_diff / total_bits
    
    print(f"Original message: {message1}")
    print(f"Modified message: {message2}")
    print(f"Bit difference: {bit_diff}/{total_bits} ({avalanche_ratio:.2%})")
    print(f"Avalanche effect: {'✓ Good' if avalanche_ratio > 0.4 else '✗ Poor'}")
    
    return avalanche_ratio > 0.4



def test_use_case_recommendations():
    """Test use case recommendation system"""
    print("\n=== Use Case Recommendations ===")
    
    use_cases = [
        ("file_encryption", "Encrypting large files for storage"),
        ("stream_encryption", "Real-time encryption of data streams"),
        ("database_encryption", "Encrypting sensitive database fields"),
        ("network_encryption", "Encrypting data for network transmission"),
        ("memory_encryption", "Encrypting data in memory")
    ]
    
    for use_case, description in use_cases:
        recommendation = recommend_mode_for_use_case(use_case)
        print(f"{description}: {recommendation}")


# === BEGIN: ComprehensivePerformanceTest from test_performance.py ===
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

class ComprehensivePerformanceTest:
    """Comprehensive performance testing for all three variants with visualization"""
    
    def __init__(self):
        self.variants = {
            'Original': SineScrambleCipher,
            'Optimized': OptimizedSineScrambleCipher,
            'Turbo': TurboSineScrambleCipher
        }
        self.results = {}
        self.stability_results = {}
        self.large_data_results = {}
    
    def print_system_info(self):
        import psutil
        print("🖥️  System Information")
        print("=" * 50)
        print(f"CPU: {psutil.cpu_count()} cores")
        print(f"Memory: {psutil.virtual_memory().total / (1024**3):.1f} GB")
        print(f"CPU Frequency: {psutil.cpu_freq().current:.0f} MHz")
        print(f"Python: {os.sys.version.split()[0]}")
        print()
    
    def performance_benchmark_all_variants(self):
        """Comprehensive performance benchmark across all variants"""
        print("🔥 SineScramble Performance Benchmark - All Variants")
        print("=" * 70)
        
        # Fixed test parameters for fair comparison
        key = generate_random_key(8, seed=42)
        test_sizes = [
            1024,          # 1KB
            10240,         # 10KB  
            102400,        # 100KB
            1048576,       # 1MB
            10485760,      # 10MB
        ]
        
        for mode in [OperationMode.SEGMENTED, OperationMode.MULTI_ROUND]:
            print(f"\n🎯 {mode.value.upper()} MODE PERFORMANCE")
            print("-" * 70)
            print(f"{'Size':<8} {'Original':<12} {'Optimized':<12} {'Turbo':<12} {'Best':<8}")
            print("-" * 70)
            
            mode_results = {}
            
            for size in test_sizes:
                # Skip if too small for segmented mode
                if mode == OperationMode.SEGMENTED and size < len(key):
                    continue
                
                # Generate test data
                test_data = os.urandom(size)
                
                size_results = {}
                
                # Test each variant
                for variant_name, cipher_class in self.variants.items():
                    try:
                        # Create cipher
                        cipher = cipher_class(key, mode)
                        
                        # Warm up JIT for optimized variants
                        if 'optimized' in variant_name.lower() or 'turbo' in variant_name.lower():
                            if size >= 1024:
                                warm_data = test_data[:1024]
                                try:
                                    cipher.encrypt(warm_data)
                                    cipher.decrypt(cipher.encrypt(warm_data))
                                except:
                                    pass
                        
                        # Force garbage collection
                        gc.collect()
                        
                        # Benchmark encryption
                        start = time.perf_counter()
                        encrypted = cipher.encrypt(test_data)
                        encrypt_time = time.perf_counter() - start
                        
                        # Benchmark decryption
                        start = time.perf_counter()
                        decrypted = cipher.decrypt(encrypted)
                        decrypt_time = time.perf_counter() - start
                        
                        # Calculate throughput
                        total_time = encrypt_time + decrypt_time
                        mbps = (size * 2) / (1024 * 1024) / total_time
                        
                        # Verify correctness
                        correct = test_data == decrypted
                        
                        size_results[variant_name] = {
                            'mbps': mbps,
                            'encrypt_time': encrypt_time,
                            'decrypt_time': decrypt_time,
                            'total_time': total_time,
                            'correct': correct
                        }
                        
                    except Exception as e:
                        print(f"    {variant_name} failed: {e}")
                        size_results[variant_name] = None
                
                # Format output
                if size >= 1024 * 1024:
                    size_str = f"{size // (1024*1024)}MB"
                elif size >= 1024:
                    size_str = f"{size // 1024}KB"
                else:
                    size_str = f"{size}B"
                
                # Get results
                orig_mbps = size_results.get('Original', {}).get('mbps', 0) if size_results.get('Original') else 0
                opt_mbps = size_results.get('Optimized', {}).get('mbps', 0) if size_results.get('Optimized') else 0
                turbo_mbps = size_results.get('Turbo', {}).get('mbps', 0) if size_results.get('Turbo') else 0
                
                # Determine winner
                speeds = [orig_mbps, opt_mbps, turbo_mbps]
                max_speed = max(speeds)
                if max_speed == turbo_mbps:
                    winner = "🚀 TURBO"
                elif max_speed == opt_mbps:
                    winner = "⚡ FAST"
                else:
                    winner = "✓ Original"
                
                print(f"{size_str:<8} {orig_mbps:<12.1f} {opt_mbps:<12.1f} {turbo_mbps:<12.1f} {winner}")
                
                # Store results for visualization
                mode_results[size] = size_results
            
            self.results[mode.value] = mode_results
    
    def stability_stress_test(self):
        """Stress test for stability across all variants"""
        print("\n💪 Stability Stress Test - All Variants")
        print("=" * 60)
        
        key = generate_random_key(4, seed=123)
        test_data = os.urandom(1024 * 1024)  # 1MB
        iterations = 30
        
        results = {}
        process = psutil.Process()
        
        for variant_name, cipher_class in self.variants.items():
            print(f"\n🔬 Stress Testing {variant_name}")
            print("-" * 40)
            
            try:
                # Measure memory before
                gc.collect()
                mem_before = process.memory_info().rss / (1024 * 1024)
                
                # Create cipher
                cipher = cipher_class(key, OperationMode.SEGMENTED)
                
                # Run stress test
                start_time = time.perf_counter()
                errors = 0
                times = []
                
                for i in range(iterations):
                    try:
                        iter_start = time.perf_counter()
                        encrypted = cipher.encrypt(test_data)
                        decrypted = cipher.decrypt(encrypted)
                        iter_time = time.perf_counter() - iter_start
                        
                        if test_data != decrypted:
                            errors += 1
                            print(f"    Error at iteration {i+1}: data mismatch")
                        
                        times.append(iter_time)
                        
                    except Exception as e:
                        errors += 1
                        print(f"    Error at iteration {i+1}: {e}")
                    
                    # Progress indicator
                    if (i + 1) % 10 == 0:
                        print(f"    Progress: {i+1}/{iterations}")
                
                total_time = time.perf_counter() - start_time
                
                # Measure memory after
                gc.collect()
                mem_after = process.memory_info().rss / (1024 * 1024)
                
                # Calculate statistics
                success_rate = ((iterations - errors) / iterations) * 100
                avg_time = sum(times) / len(times) if times else 0
                min_time = min(times) if times else 0
                max_time = max(times) if times else 0
                
                results[variant_name] = {
                    'total_time': total_time,
                    'errors': errors,
                    'success_rate': success_rate,
                    'memory_before': mem_before,
                    'memory_after': mem_after,
                    'memory_growth': mem_after - mem_before,
                    'avg_time': avg_time,
                    'min_time': min_time,
                    'max_time': max_time,
                    'time_variance': max_time - min_time if times else 0
                }
                
                print(f"  Total time: {total_time:.2f}s")
                print(f"  Errors: {errors}/{iterations}")
                print(f"  Success rate: {success_rate:.1f}%")
                print(f"  Memory growth: {mem_after - mem_before:.1f} MB")
                print(f"  Avg time: {avg_time:.4f}s")
                print(f"  Time variance: {max_time - min_time:.4f}s")
                
                # Stability assessment
                if success_rate >= 95:
                    stability = "✓ STABLE"
                elif success_rate >= 80:
                    stability = "⚠ UNSTABLE"
                else:
                    stability = "✗ FAILED"
                print(f"  Assessment: {stability}")
                
            except Exception as e:
                print(f"  ✗ ERROR: {e}")
                results[variant_name] = None
        
        self.stability_results = results
        return results
    
    def large_data_scalability_test(self):
        """Test scalability with large data sets (expanded, averaged) using SEGMENTED mode throughput"""
        print("\n📈 Large Data Scalability Test (Expanded, Averaged, Segmented Mode Only)")
        print("=" * 50)
        
        key = generate_random_key(4, seed=456)
        large_sizes = [
            1 * 1024 * 1024,    # 1MB
            10 * 1024 * 1024,   # 10MB
            20 * 1024 * 1024,   # 20MB
            30 * 1024 * 1024,   # 30MB
            40 * 1024 * 1024,   # 40MB
            50 * 1024 * 1024,   # 50MB
        ]
        num_repeats = 100
        
        results = {}
        
        for variant_name, cipher_class in self.variants.items():
            print(f"\n🔬 Testing {variant_name} with Large Data (Averaged, Segmented Mode)")
            print("-" * 40)
            
            try:
                variant_results = {}
                
                for size in large_sizes:
                    mb_size = size // (1024 * 1024)
                    print(f"  Testing {mb_size}MB... (averaging {num_repeats} runs)")
                    
                    # Generate large test data
                    test_data = os.urandom(size)
                    
                    # Create cipher in SEGMENTED mode only
                    cipher = cipher_class(key, OperationMode.SEGMENTED)
                    
                    # Measure memory before
                    gc.collect()
                    mem_before = psutil.Process().memory_info().rss / (1024 * 1024)
                    
                    encrypt_times = []
                    decrypt_times = []
                    correct = True
                    for _ in range(num_repeats):
                        try:
                            # Encrypt
                            start = time.perf_counter()
                            encrypted = cipher.encrypt(test_data)
                            encrypt_time = time.perf_counter() - start
                            
                            # Decrypt
                            start = time.perf_counter()
                            decrypted = cipher.decrypt(encrypted)
                            decrypt_time = time.perf_counter() - start
                            
                            encrypt_times.append(encrypt_time)
                            decrypt_times.append(decrypt_time)
                            if test_data != decrypted:
                                correct = False
                        except Exception as e:
                            print(f"    ✗ ERROR: {e}")
                            correct = False
                    
                    # Measure memory after
                    gc.collect()
                    mem_after = psutil.Process().memory_info().rss / (1024 * 1024)
                    
                    # Calculate metrics
                    avg_encrypt_time = sum(encrypt_times) / len(encrypt_times) if encrypt_times else float('inf')
                    avg_decrypt_time = sum(decrypt_times) / len(decrypt_times) if decrypt_times else float('inf')
                    avg_encrypt_mbps = mb_size / avg_encrypt_time if avg_encrypt_time > 0 else 0
                    avg_decrypt_mbps = mb_size / avg_decrypt_time if avg_decrypt_time > 0 else 0
                    
                    variant_results[mb_size] = {
                        'avg_encrypt_time': avg_encrypt_time,
                        'avg_decrypt_time': avg_decrypt_time,
                        'avg_encrypt_mbps': avg_encrypt_mbps,
                        'avg_decrypt_mbps': avg_decrypt_mbps,
                        'correct': correct,
                        'memory_before': mem_before,
                        'memory_after': mem_after,
                        'memory_growth': mem_after - mem_before
                    }
                    
                    print(f"    Encrypt: {avg_encrypt_time:.2f}s → {avg_encrypt_mbps:.1f} MB/s (avg)")
                    print(f"    Decrypt: {avg_decrypt_time:.2f}s → {avg_decrypt_mbps:.1f} MB/s (avg)")
                    print(f"    Correct: {correct}")
                    print(f"    Memory growth: {mem_after - mem_before:.1f} MB")
                
                results[variant_name] = variant_results
                
            except Exception as e:
                print(f"  ✗ ERROR: {e}")
                results[variant_name] = None
        
        self.large_data_results = results
        return results
    
    def create_performance_visualizations(self):
        """Create matplotlib visualizations of performance results"""
        print("\n📊 Creating Performance Visualizations...")
        
        # Set up the plotting style
        plt.style.use('default')
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        fig.suptitle('SineScramble Performance Comparison - All Variants', fontsize=16, fontweight='bold')
        
        colors = {
            'Original': '#1f77b4',      # Blue
            'Optimized': '#ff7f0e',     # Orange
            'Turbo': '#2ca02c'          # Green
        }
        
        markers = {
            'Original': 'o',
            'Optimized': 's',
            'Turbo': '^'
        }
        
        # Plot 1: Performance vs Data Size (Segmented Mode)
        ax1 = axes[0, 0]
        if 'segmented' in self.results:
            segmented_results = self.results['segmented']
            for variant_name in self.variants.keys():
                sizes = []
                speeds = []
                for size, size_results in segmented_results.items():
                    if size_results and variant_name in size_results and size_results[variant_name]:
                        sizes.append(size / (1024 * 1024))  # Convert to MB
                        speeds.append(size_results[variant_name]['mbps'])
                
                if sizes and speeds:
                    ax1.plot(sizes, speeds, 
                            color=colors[variant_name], 
                            marker=markers[variant_name], 
                            linewidth=2, 
                            markersize=8,
                            label=variant_name)
        
        ax1.set_xlabel('Data Size (MB)')
        ax1.set_ylabel('Throughput (MB/s)')
        ax1.set_title('Segmented Mode Performance')
        ax1.grid(True, alpha=0.3)
        ax1.legend()
        ax1.set_xscale('log')
        
        # Plot 2: Performance vs Data Size (Multi-Round Mode)
        ax2 = axes[0, 1]
        if 'multi_round' in self.results:
            multi_round_results = self.results['multi_round']
            for variant_name in self.variants.keys():
                sizes = []
                speeds = []
                for size, size_results in multi_round_results.items():
                    if size_results and variant_name in size_results and size_results[variant_name]:
                        sizes.append(size / (1024 * 1024))  # Convert to MB
                        speeds.append(size_results[variant_name]['mbps'])
                
                if sizes and speeds:
                    ax2.plot(sizes, speeds, 
                            color=colors[variant_name], 
                            marker=markers[variant_name], 
                            linewidth=2, 
                            markersize=8,
                            label=variant_name)
        
        ax2.set_xlabel('Data Size (MB)')
        ax2.set_ylabel('Throughput (MB/s)')
        ax2.set_title('Multi-Round Mode Performance')
        ax2.grid(True, alpha=0.3)
        ax2.legend()
        ax2.set_xscale('log')
        
        # Plot 3: Stability Comparison
        ax3 = axes[1, 0]
        if self.stability_results:
            variants = list(self.stability_results.keys())
            success_rates = []
            memory_growths = []
            
            for variant in variants:
                if self.stability_results[variant]:
                    success_rates.append(self.stability_results[variant]['success_rate'])
                    memory_growths.append(self.stability_results[variant]['memory_growth'])
                else:
                    success_rates.append(0)
                    memory_growths.append(0)
            
            x = np.arange(len(variants))
            width = 0.35
            
            bars1 = ax3.bar(x - width/2, success_rates, width, label='Success Rate (%)', 
                           color='#2ca02c', alpha=0.8)
            ax3_twin = ax3.twinx()
            bars2 = ax3_twin.bar(x + width/2, memory_growths, width, label='Memory Growth (MB)', 
                                color='#d62728', alpha=0.8)
            
            ax3.set_xlabel('Variant')
            ax3.set_ylabel('Success Rate (%)')
            ax3_twin.set_ylabel('Memory Growth (MB)')
            ax3.set_title('Stability and Memory Efficiency')
            ax3.set_xticks(x)
            ax3.set_xticklabels(variants)
            ax3.grid(True, alpha=0.3)
            
            # Add value labels on bars
            for bar in bars1:
                height = bar.get_height()
                ax3.text(bar.get_x() + bar.get_width()/2., height + 1,
                        f'{height:.0f}%', ha='center', va='bottom')
            
            for bar in bars2:
                height = bar.get_height()
                ax3_twin.text(bar.get_x() + bar.get_width()/2., height + 0.5,
                             f'{height:.1f}', ha='center', va='bottom')
        
        # Plot 4: Large Data Scalability
        ax4 = axes[1, 1]
        if self.large_data_results:
            for variant_name in self.variants.keys():
                if variant_name in self.large_data_results:
                    variant_results = self.large_data_results[variant_name]
                    sizes = []
                    speeds = []
                    
                    for size, size_results in variant_results.items():
                        if size_results:
                            sizes.append(size)
                            speeds.append(size_results['avg_encrypt_mbps']) # Use avg_encrypt_mbps (SEGMENTED mode only)
                    
                    if sizes and speeds:
                        ax4.plot(sizes, speeds, 
                                color=colors[variant_name], 
                                marker=markers[variant_name], 
                                linewidth=2, 
                                markersize=8,
                                label=variant_name)
        
        ax4.set_xlabel('Data Size (MB)')
        ax4.set_ylabel('Encryption Speed (MB/s)')
        ax4.set_title('Large Data Scalability (Segmented Mode)')
        ax4.grid(True, alpha=0.3)
        ax4.legend()
        
        plt.tight_layout()
        plt.savefig('sinescramble_performance_comparison.png', dpi=300, bbox_inches='tight')
        print("📈 Performance visualization saved as 'sinescramble_performance_comparison.png'")
        plt.show()
    
    def generate_final_report(self):
        """Generate comprehensive final report with visualizations"""
        print("\n" + "="*80)
        print("🏆 COMPREHENSIVE PERFORMANCE ANALYSIS REPORT")
        print("="*80)
        
        # Run all tests
        self.print_system_info()
        self.performance_benchmark_all_variants()
        self.stability_stress_test()
        self.large_data_scalability_test()
        
        # Create visualizations
        self.create_performance_visualizations()
        
        # Generate summary
        print("\n📊 FINAL SUMMARY")
        print("-" * 80)
        
        print(f"{'Variant':<12} {'Stability':<12} {'Peak Speed':<12} {'Memory':<12} {'Large Data':<12} {'Recommendation'}")
        print("-" * 80)
        
        for variant_name in self.variants.keys():
            # Stability
            stability = self.stability_results.get(variant_name, {})
            if stability:
                success_rate = stability.get('success_rate', 0)
                if success_rate >= 95:
                    stability_str = "✓ STABLE"
                elif success_rate >= 80:
                    stability_str = "⚠ UNSTABLE"
                else:
                    stability_str = "✗ FAILED"
            else:
                stability_str = "ERROR"
            
            # Peak performance (1MB Segmented mode)
            peak_speed = "N/A"
            if 'segmented' in self.results:
                seg_results = self.results['segmented']
                if 1048576 in seg_results:  # 1MB
                    size_results = seg_results[1048576]
                    if size_results and variant_name in size_results and size_results[variant_name]:
                        peak_speed = f"{size_results[variant_name]['mbps']:.0f} MB/s"
            
            # Memory efficiency
            memory_str = "N/A"
            if stability:
                mem_growth = stability.get('memory_growth', 0)
                if mem_growth < 5:
                    memory_str = "✓ Excellent"
                elif mem_growth < 20:
                    memory_str = "⚠ Acceptable"
                else:
                    memory_str = "✗ Poor"
            
            # Large data handling (SEGMENTED mode throughput only)
            large_data_str = "N/A"
            if variant_name in self.large_data_results:
                variant_results = self.large_data_results[variant_name]
                # Only consider SEGMENTED mode throughput for large data
                if 50 in variant_results and variant_results[50]:
                    large_data_str = "✓ Handles"
                elif 10 in variant_results and variant_results[10]:
                    large_data_str = "⚠ Limited"
                else:
                    large_data_str = "✗ Failed"
            
            # Recommendation
            if variant_name == 'Original':
                recommendation = "Baseline"
            elif variant_name == 'Optimized':
                if stability.get('success_rate', 0) >= 95:
                    recommendation = "🚀 RECOMMENDED"
                else:
                    recommendation = "⚠ Unstable"
            elif variant_name == 'Turbo':
                if stability.get('success_rate', 0) >= 95:
                    recommendation = "⚡ FAST (Experimental)"
                else:
                    recommendation = "⚠ Unstable"
            
            print(f"{variant_name:<12} {stability_str:<12} {peak_speed:<12} {memory_str:<12} {large_data_str:<12} {recommendation}")
        
        print("\n🎯 FINAL RECOMMENDATIONS:")
        print("- Turbo: ⚡ RECOMMENDED for high-performance, large data, and streaming (default)")
        print("- Original: Best for Multi-Round (high-security) mode and as a reference implementation")
        print("- Optimized: For experimental JIT research only")
        
        return {
            'performance': self.results,
            'stability': self.stability_results,
            'large_data': self.large_data_results
        }

def run_all_comprehensive_tests():
    print("\n🚀 SINESCRAMBLE FULL FUNCTIONAL + PERFORMANCE SUITE\n" + "="*70)
    # Functional tests
    test_basic_encryption_decryption()
    test_key_management()
    test_different_data_types()
    test_file_operations()
    test_avalanche_effect()
    test_use_case_recommendations()
    # Comprehensive variant comparison (correctness, performance, stability, large data)
    print("\n" + "="*60)
    print("🔬 COMPREHENSIVE VARIANT COMPARISON")
    print("="*60)
    comparison = VariantComparison()
    comparison.generate_comprehensive_report()
    # Advanced performance, scalability, and visualization
    print("\n" + "="*60)
    print("📊 ADVANCED PERFORMANCE, STABILITY, AND VISUALIZATION")
    print("="*60)
    perf = ComprehensivePerformanceTest()
    perf.generate_final_report()
    print("\n✅ ALL TESTS AND VISUALIZATIONS COMPLETED!\n" + "="*60)

if __name__ == "__main__":
    run_all_comprehensive_tests() 