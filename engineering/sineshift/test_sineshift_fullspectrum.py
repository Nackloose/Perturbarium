#!/usr/bin/env python3
"""
Full Spectrum SineShift Test Suite - Benchmark and Stress Testing

This script performs comprehensive testing of the SineShift module across the full
spectrum of swap parameters (0.0 to 120,000.0), including:
- Speed benchmarking
- 1k test sets for consistency verification
- Error-free operation validation
- Performance metrics across different parameter ranges
"""

import numpy as np
import time
import statistics
import argparse
import sys
import os
from typing import Dict, List, Tuple, Any
from collections import defaultdict
import matplotlib.pyplot as plt

# Import from the current directory
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import the module components directly
from sine_generator import (
    generate_sine_wave,
    generate_permutation_sine_wave,
    generate_complex_sine_pattern,
    BASE_FREQUENCY,
    FRAME_COUNT
)

from mutator import (
    SineShiftMutator
)

from fft_analyzer import (
    analyze_fft,
    analyze_permutation_fft,
    create_spectral_report
)


class FullSpectrumTester:
    """Comprehensive tester for the full spectrum of swap parameters."""
    
    def __init__(self, test_size: int = 1000, frame_count: int = 10000):
        self.test_size = test_size
        self.frame_count = frame_count
        self.results = defaultdict(list)
        self.benchmarks = {}
        self.errors = []
        
    def benchmark_function(self, func, *args, iterations: int = 100) -> Dict[str, float]:
        """Benchmark a function's execution time."""
        times = []
        
        for _ in range(iterations):
            start_time = time.perf_counter()
            result = func(*args)
            end_time = time.perf_counter()
            times.append(end_time - start_time)
        
        return {
            'mean_time': statistics.mean(times),
            'median_time': statistics.median(times),
            'min_time': min(times),
            'max_time': max(times),
            'std_dev': statistics.stdev(times) if len(times) > 1 else 0.0,
            'total_time': sum(times)
        }
    
    def test_sine_generation_spectrum(self) -> Dict[str, Any]:
        """Test sine wave generation across the full parameter spectrum."""
        print("=== Testing Sine Wave Generation Across Full Spectrum ===")
        
        # Define test ranges with whole number iterations
        test_ranges = [
            (0, 1, "Near Zero"),
            (1, 10, "Low Range"),
            (10, 100, "Medium Range"),
            (100, 1000, "High Range"),
            (1000, 10000, "Very High Range"),
            (10000, 100000, "Extreme Range"),
            (100000, 120000, "Ultra Extreme Range")
        ]
        
        results = {}
        
        for min_val, max_val, range_name in test_ranges:
            print(f"\n--- Testing {range_name} ({min_val} to {max_val}) ---")
            
            # Test every whole number in the range
            swap_params = list(range(min_val, max_val + 1))
            range_results = {
                'success_count': 0,
                'error_count': 0,
                'times': [],
                'amplitudes': [],
                'frequencies': [],
                'swap_params': swap_params
            }
            
            for swap_param in swap_params:
                try:
                    start_time = time.perf_counter()
                    sine_wave = generate_sine_wave(swap_param)
                    end_time = time.perf_counter()
                    
                    execution_time = end_time - start_time
                    rms_amplitude = np.sqrt(np.mean(sine_wave**2))
                    frequency = BASE_FREQUENCY * swap_param
                    
                    range_results['success_count'] += 1
                    range_results['times'].append(execution_time)
                    range_results['amplitudes'].append(rms_amplitude)
                    range_results['frequencies'].append(frequency)
                    
                except Exception as e:
                    range_results['error_count'] += 1
                    self.errors.append(f"Sine generation error at {swap_param}: {e}")
            
            # Calculate statistics for this range
            if range_results['times']:
                range_results['avg_time'] = statistics.mean(range_results['times'])
                range_results['avg_amplitude'] = statistics.mean(range_results['amplitudes'])
                range_results['avg_frequency'] = statistics.mean(range_results['frequencies'])
                range_results['min_time'] = min(range_results['times'])
                range_results['max_time'] = max(range_results['times'])
            
            results[range_name] = range_results
            
            print(f"  Success: {range_results['success_count']}/{len(swap_params)}")
            print(f"  Errors: {range_results['error_count']}")
            if range_results['times']:
                print(f"  Avg time: {range_results['avg_time']:.6f}s")
                print(f"  Avg amplitude: {range_results['avg_amplitude']:.4f}")
                print(f"  Avg frequency: {range_results['avg_frequency']:.2f} Hz")
        
        return results

    def test_harmonics_spectrum(self) -> Dict[str, Any]:
        """Test harmonic generation across the full parameter spectrum with sliding harmonics."""
        print("\n=== Testing Harmonic Generation Across Full Spectrum ===")
        
        # Define test ranges with whole number iterations
        test_ranges = [
            (0, 1, "Near Zero"),
            (1, 10, "Low Range"),
            (10, 100, "Medium Range"),
            (100, 1000, "High Range"),
            (1000, 10000, "Very High Range"),
            (10000, 100000, "Extreme Range"),
            (100000, 120000, "Ultra Extreme Range")
        ]
        
        # Harmonic size (number of harmonics to generate)
        HARMONIC_SIZE = 5
        
        results = {}
        
        for min_val, max_val, range_name in test_ranges:
            print(f"\n--- Testing Harmonics {range_name} ({min_val} to {max_val}) ---")
            
            # Test every whole number in the range
            swap_params = list(range(min_val, max_val + 1))
            range_results = {
                'success_count': 0,
                'error_count': 0,
                'times': [],
                'amplitudes': [],
                'frequencies': [],
                'harmonic_counts': [],
                'swap_params': swap_params
            }
            
            for swap_param in swap_params:
                try:
                    start_time = time.perf_counter()
                    
                    # Generate sliding harmonics: start with swap_param, then shift up
                    harmonics_list = []
                    current_base = swap_param
                    
                    for i in range(HARMONIC_SIZE):
                        harmonic_freq = current_base + (i * swap_param)
                        harmonic_wave = generate_sine_wave(harmonic_freq)
                        harmonics_list.append(harmonic_wave)
                        current_base += swap_param
                    
                    # Combine all harmonics
                    combined_harmonics = np.sum(harmonics_list, axis=0)
                    
                    end_time = time.perf_counter()
                    
                    execution_time = end_time - start_time
                    rms_amplitude = np.sqrt(np.mean(combined_harmonics**2))
                    frequency = BASE_FREQUENCY * swap_param
                    harmonic_count = HARMONIC_SIZE
                    
                    range_results['success_count'] += 1
                    range_results['times'].append(execution_time)
                    range_results['amplitudes'].append(rms_amplitude)
                    range_results['frequencies'].append(frequency)
                    range_results['harmonic_counts'].append(harmonic_count)
                    
                except Exception as e:
                    range_results['error_count'] += 1
                    self.errors.append(f"Harmonic generation error at {swap_param}: {e}")
            
            # Calculate statistics for this range
            if range_results['times']:
                range_results['avg_time'] = statistics.mean(range_results['times'])
                range_results['avg_amplitude'] = statistics.mean(range_results['amplitudes'])
                range_results['avg_frequency'] = statistics.mean(range_results['frequencies'])
                range_results['avg_harmonic_count'] = statistics.mean(range_results['harmonic_counts'])
                range_results['min_time'] = min(range_results['times'])
                range_results['max_time'] = max(range_results['times'])
            
            results[range_name] = range_results
            
            print(f"  Success: {range_results['success_count']}/{len(swap_params)}")
            print(f"  Errors: {range_results['error_count']}")
            if range_results['times']:
                print(f"  Avg time: {range_results['avg_time']:.6f}s")
                print(f"  Avg amplitude: {range_results['avg_amplitude']:.4f}")
                print(f"  Avg frequency: {range_results['avg_frequency']:.2f} Hz")
                print(f"  Avg harmonic count: {range_results['avg_harmonic_count']:.1f}")
        
        return results

    def test_entropy_spectrum(self) -> Dict[str, Any]:
        """Test entropy analysis across the full parameter spectrum."""
        print("\n=== Testing Entropy Analysis Across Full Spectrum ===")
        
        # Define test ranges with whole number iterations
        test_ranges = [
            (0, 1, "Near Zero"),
            (1, 10, "Low Range"),
            (10, 100, "Medium Range"),
            (100, 1000, "High Range"),
            (1000, 10000, "Very High Range"),
            (10000, 100000, "Extreme Range"),
            (100000, 120000, "Ultra Extreme Range")
        ]
        
        results = {
            'entropy_data': {},
            'entropy_changes': [],
            'swap_params': [],
            'original_entropies': [],
            'permuted_entropies': [],
            'entropy_ratios': [],
            'execution_times': []
        }
        
        # Generate a consistent test signal
        test_signal = generate_sine_wave(0.5)
        
        for min_val, max_val, range_name in test_ranges:
            print(f"\n--- Testing Entropy {range_name} ({min_val} to {max_val}) ---")
            
            # Test every whole number in the range
            swap_params = list(range(min_val, max_val + 1))
            range_success = 0
            range_errors = 0
            
            for swap_param in swap_params:
                try:
                    # Create spectral report for entropy analysis
                    start_time = time.perf_counter()
                    report = create_spectral_report(test_signal, swap_param)
                    end_time = time.perf_counter()
                    
                    execution_time = end_time - start_time
                    
                    entropy_data = {
                        'original_entropy': report['entropy_analysis']['original_entropy'],
                        'permuted_entropy': report['entropy_analysis']['permuted_entropy'],
                        'entropy_change': report['entropy_analysis']['entropy_change'],
                        'entropy_ratio': report['entropy_analysis']['entropy_ratio'],
                        'execution_time': execution_time
                    }
                    
                    results['entropy_data'][swap_param] = entropy_data
                    results['entropy_changes'].append(entropy_data['entropy_change'])
                    results['swap_params'].append(swap_param)
                    results['original_entropies'].append(entropy_data['original_entropy'])
                    results['permuted_entropies'].append(entropy_data['permuted_entropy'])
                    results['entropy_ratios'].append(entropy_data['entropy_ratio'])
                    results['execution_times'].append(execution_time)
                    
                    range_success += 1
                    
                except Exception as e:
                    self.errors.append(f"Entropy analysis error at {swap_param}: {e}")
                    range_errors += 1
            
            print(f"  Success: {range_success}/{len(swap_params)}")
            print(f"  Errors: {range_errors}")
            if range_success > 0:
                avg_time = statistics.mean([results['entropy_data'][p]['execution_time'] 
                                         for p in swap_params if p in results['entropy_data']])
                print(f"  Avg execution time: {avg_time:.6f}s")
        
        return results
    
    def test_permutation_consistency(self, iterations: int = 1000) -> Dict[str, Any]:
        """Test permutation consistency with 1k iterations."""
        print(f"\n=== Testing Permutation Consistency ({iterations} iterations) ===")
        
        # Test different swap parameters
        test_params = [0.1, 0.5, 1.0, 10.0, 100.0, 1000.0, 10000.0, 100000.0]
        
        consistency_results = {}
        
        for swap_param in test_params:
            print(f"\n--- Testing swap_param {swap_param} ---")
            
            # Create test data
            test_data = np.random.rand(self.frame_count)
            mutator = SineShiftMutator(self.frame_count)
            
            # Test consistency
            permuted_results = []
            restoration_errors = []
            times = []
            
            for i in range(iterations):
                try:
                    start_time = time.perf_counter()
                    
                    # Permute and restore
                    permuted = mutator.mutate_data(test_data, swap_param)
                    restored = mutator.unmute_data(permuted, swap_param)
                    
                    end_time = time.perf_counter()
                    
                    # Check restoration accuracy
                    error = np.mean(np.abs(test_data - restored))
                    restoration_errors.append(error)
                    
                    # Store first few results for consistency check
                    if i < 10:
                        permuted_results.append(permuted.copy())
                    
                    times.append(end_time - start_time)
                    
                except Exception as e:
                    self.errors.append(f"Permutation error at iteration {i}, swap_param {swap_param}: {e}")
            
            # Calculate consistency metrics
            if permuted_results:
                # Check if first 10 results are identical (deterministic)
                first_result = permuted_results[0]
                deterministic = all(np.array_equal(first_result, result) for result in permuted_results[1:])
                
                consistency_results[swap_param] = {
                    'success_count': len(times),
                    'avg_time': statistics.mean(times),
                    'avg_restoration_error': statistics.mean(restoration_errors),
                    'max_restoration_error': max(restoration_errors),
                    'deterministic': deterministic,
                    'min_time': min(times),
                    'max_time': max(times)
                }
                
                print(f"  Success: {len(times)}/{iterations}")
                print(f"  Avg time: {statistics.mean(times):.6f}s")
                print(f"  Avg restoration error: {statistics.mean(restoration_errors):.2e}")
                print(f"  Deterministic: {deterministic}")
        
        return consistency_results
    
    def benchmark_full_spectrum(self) -> Dict[str, Any]:
        """Benchmark operations across the full parameter spectrum."""
        print("\n=== Full Spectrum Benchmarking ===")
        
        # Define benchmark ranges
        benchmark_ranges = [
            (0.0, 1.0, "Near Zero"),
            (1.0, 10.0, "Low Range"),
            (10.0, 100.0, "Medium Range"),
            (100.0, 1000.0, "High Range"),
            (1000.0, 10000.0, "Very High Range"),
            (10000.0, 100000.0, "Extreme Range"),
            (100000.0, 120000.0, "Ultra Extreme Range")
        ]
        
        benchmark_results = {}
        
        for min_val, max_val, range_name in benchmark_ranges:
            print(f"\n--- Benchmarking {range_name} ---")
            
            # Test parameters in this range
            test_params = np.linspace(min_val, max_val, 10)
            
            range_benchmarks = {}
            
            # Benchmark sine generation
            print("  Benchmarking sine generation...")
            sine_times = []
            for param in test_params:
                benchmark = self.benchmark_function(generate_sine_wave, param, iterations=50)
                sine_times.append(benchmark['mean_time'])
            
            range_benchmarks['sine_generation'] = {
                'avg_time': statistics.mean(sine_times),
                'min_time': min(sine_times),
                'max_time': max(sine_times)
            }
            
            # Benchmark permutation operations
            print("  Benchmarking permutation operations...")
            test_data = np.random.rand(self.frame_count)
            mutator = SineShiftMutator(self.frame_count)
            
            permute_times = []
            restore_times = []
            
            for param in test_params:
                # Benchmark permutation
                permute_benchmark = self.benchmark_function(
                    mutator.mutate_data, test_data, param, iterations=20
                )
                permute_times.append(permute_benchmark['mean_time'])
                
                # Benchmark restoration
                permuted_data = mutator.mutate_data(test_data, param)
                restore_benchmark = self.benchmark_function(
                    mutator.unmute_data, permuted_data, param, iterations=20
                )
                restore_times.append(restore_benchmark['mean_time'])
            
            range_benchmarks['permutation'] = {
                'avg_permute_time': statistics.mean(permute_times),
                'avg_restore_time': statistics.mean(restore_times),
                'min_permute_time': min(permute_times),
                'max_permute_time': max(permute_times)
            }
            
            # Benchmark FFT analysis
            print("  Benchmarking FFT analysis...")
            test_signal = generate_sine_wave(test_params[0])
            fft_benchmark = self.benchmark_function(
                analyze_permutation_fft, test_signal, test_params[0], iterations=10
            )
            range_benchmarks['fft_analysis'] = fft_benchmark
            
            benchmark_results[range_name] = range_benchmarks
            
            print(f"  Sine generation: {statistics.mean(sine_times):.6f}s avg")
            print(f"  Permutation: {statistics.mean(permute_times):.6f}s avg")
            print(f"  FFT analysis: {fft_benchmark['mean_time']:.6f}s avg")
        
        return benchmark_results
    
    def stress_test_extreme_values(self) -> Dict[str, Any]:
        """Stress test with extreme swap parameter values."""
        print("\n=== Stress Testing Extreme Values ===")
        
        # Test extremely large values
        extreme_values = [
            1e6, 1e7, 1e8, 1e9, 1e10, 1e11, 1e12,
            float('inf'), float('-inf'), float('nan')
        ]
        
        stress_results = {
            'successful_tests': 0,
            'failed_tests': 0,
            'errors': []
        }
        
        for value in extreme_values:
            try:
                print(f"  Testing swap_param: {value}")
                
                # Test sine generation
                sine_wave = generate_sine_wave(value)
                
                # Test permutation
                test_data = np.random.rand(1000)
                mutator = SineShiftMutator(1000)
                permuted = mutator.mutate_data(test_data, value)
                restored = mutator.unmute_data(permuted, value)
                
                # Check restoration
                error = np.mean(np.abs(test_data - restored))
                
                if error < 1e-10:  # Very small tolerance
                    stress_results['successful_tests'] += 1
                    print(f"    ✓ Success (error: {error:.2e})")
                else:
                    stress_results['failed_tests'] += 1
                    print(f"    ✗ Failed (error: {error:.2e})")
                
            except Exception as e:
                stress_results['failed_tests'] += 1
                stress_results['errors'].append(f"Error with {value}: {e}")
                print(f"    ✗ Exception: {e}")
        
        return stress_results
    
    def run_comprehensive_test(self) -> Dict[str, Any]:
        """Run the complete comprehensive test suite."""
        print("Full Spectrum SineShift Test Suite")
        print("=" * 60)
        print(f"Test Size: {self.test_size}")
        print(f"Frame Count: {self.frame_count}")
        print(f"Base Frequency: {BASE_FREQUENCY} Hz")
        print("=" * 60)
        
        start_time = time.perf_counter()
        
        # Run all tests
        results = {
            'sine_generation': self.test_sine_generation_spectrum(),
            'harmonics_spectrum': self.test_harmonics_spectrum(),
            'entropy_spectrum': self.test_entropy_spectrum(),
            'permutation_consistency': self.test_permutation_consistency(),
            'benchmarks': self.benchmark_full_spectrum(),
            'stress_test': self.stress_test_extreme_values(),
            'errors': self.errors,
            'total_time': 0
        }
        
        end_time = time.perf_counter()
        results['total_time'] = end_time - start_time
        
        # Print summary
        self.print_summary(results)
        
        return results
    
    def print_summary(self, results: Dict[str, Any]):
        """Print a comprehensive summary of test results."""
        print("\n" + "=" * 60)
        print("COMPREHENSIVE TEST SUMMARY")
        print("=" * 60)
        
        print(f"\nTotal Test Time: {results['total_time']:.2f} seconds")
        print(f"Total Errors: {len(results['errors'])}")
        
        if results['errors']:
            print("\nErrors encountered:")
            for error in results['errors'][:10]:  # Show first 10 errors
                print(f"  - {error}")
            if len(results['errors']) > 10:
                print(f"  ... and {len(results['errors']) - 10} more errors")
        
        # Sine generation summary
        print("\nSine Generation Results:")
        total_success = 0
        total_tests = 0
        for range_name, range_data in results['sine_generation'].items():
            success = range_data['success_count']
            total = success + range_data['error_count']
            total_success += success
            total_tests += total
            print(f"  {range_name}: {success}/{total} successful")
        
        print(f"  Overall: {total_success}/{total_tests} successful ({total_success/total_tests*100:.1f}%)")
        
        # Harmonics summary
        if 'harmonics_spectrum' in results:
            print("\nHarmonics Generation Results:")
            total_harmonic_success = 0
            total_harmonic_tests = 0
            for range_name, range_data in results['harmonics_spectrum'].items():
                success = range_data['success_count']
                total = success + range_data['error_count']
                total_harmonic_success += success
                total_harmonic_tests += total
                print(f"  {range_name}: {success}/{total} successful")
            
            print(f"  Overall: {total_harmonic_success}/{total_harmonic_tests} successful ({total_harmonic_success/total_harmonic_tests*100:.1f}%)")
        
        # Entropy summary
        if 'entropy_spectrum' in results:
            print("\nEntropy Analysis Results:")
            entropy_data = results['entropy_spectrum']
            for swap_param in entropy_data['swap_params']:
                if swap_param in entropy_data['entropy_data']:
                    data = entropy_data['entropy_data'][swap_param]
                    print(f"  swap_param {swap_param}:")
                    print(f"    Original entropy: {data['original_entropy']:.4f}")
                    print(f"    Permuted entropy: {data['permuted_entropy']:.4f}")
                    print(f"    Entropy change: {data['entropy_change']:.4f}")
                    print(f"    Entropy ratio: {data['entropy_ratio']:.4f}")
        
        # Permutation consistency summary
        print("\nPermutation Consistency Results:")
        for swap_param, data in results['permutation_consistency'].items():
            print(f"  swap_param {swap_param}: {data['success_count']} successful, "
                  f"avg error: {data['avg_restoration_error']:.2e}, "
                  f"deterministic: {data['deterministic']}")
        
        # Stress test summary
        stress = results['stress_test']
        print(f"\nStress Test Results:")
        print(f"  Successful: {stress['successful_tests']}")
        print(f"  Failed: {stress['failed_tests']}")
        
        # Performance summary
        print("\nPerformance Summary (Average Times):")
        for range_name, benchmarks in results['benchmarks'].items():
            print(f"  {range_name}:")
            print(f"    Sine generation: {benchmarks['sine_generation']['avg_time']:.6f}s")
            print(f"    Permutation: {benchmarks['permutation']['avg_permute_time']:.6f}s")
            print(f"    FFT analysis: {benchmarks['fft_analysis']['mean_time']:.6f}s")
        
        print("\n" + "=" * 60)


def plot_fullspectrum_results(results: Dict[str, Any]):
    """Plot comprehensive results from the full spectrum test."""
    
    # 1. Sine generation timing
    sine_labels = []
    sine_avg_times = []
    for range_name, data in results['sine_generation'].items():
        sine_labels.append(range_name)
        sine_avg_times.append(data.get('avg_time', 0))
    plt.figure(figsize=(12, 6))
    plt.bar(sine_labels, sine_avg_times, color='skyblue')
    plt.ylabel('Avg Sine Generation Time (s)')
    plt.title('Sine Generation Speed by Swap Param Range')
    plt.xticks(rotation=30)
    plt.tight_layout()
    plt.show()

    # 2. Harmonics analysis
    if 'harmonics_spectrum' in results:
        harmonics_data = results['harmonics_spectrum']
        range_names = list(harmonics_data.keys())
        avg_harmonic_times = []
        avg_amplitudes = []
        avg_frequencies = []
        
        for range_name in range_names:
            data = harmonics_data[range_name]
            if data.get('times'):
                avg_harmonic_times.append(data.get('avg_time', 0))
                avg_amplitudes.append(data.get('avg_amplitude', 0))
                avg_frequencies.append(data.get('avg_frequency', 0))
            else:
                avg_harmonic_times.append(0)
                avg_amplitudes.append(0)
                avg_frequencies.append(0)
        
        # Harmonic generation time
        plt.figure(figsize=(12, 6))
        plt.bar(range_names, avg_harmonic_times, color='lightgreen')
        plt.ylabel('Avg Harmonic Generation Time (s)')
        plt.title('Harmonic Generation Speed by Range')
        plt.xticks(rotation=30)
        plt.tight_layout()
        plt.show()
        
        # Harmonic amplitude vs frequency
        plt.figure(figsize=(12, 6))
        plt.scatter(avg_frequencies, avg_amplitudes, s=100, alpha=0.7, color='orange')
        plt.xlabel('Average Frequency (Hz)')
        plt.ylabel('Average RMS Amplitude')
        plt.title('Harmonic Amplitude vs Frequency Across Ranges')
        plt.grid(True)
        plt.tight_layout()
        plt.show()

    # 3. Entropy analysis
    if 'entropy_spectrum' in results:
        entropy_data = results['entropy_spectrum']
        swap_params = entropy_data['swap_params']
        entropy_changes = entropy_data['entropy_changes']
        original_entropies = entropy_data['original_entropies']
        permuted_entropies = entropy_data['permuted_entropies']
        entropy_ratios = entropy_data['entropy_ratios']
        execution_times = entropy_data['execution_times']
        
        # Full Spectrum Entropy Analysis Window
        plt.figure(figsize=(16, 12))
        plt.suptitle('Full Spectrum Entropy Analysis', fontsize=16, fontweight='bold')
        
        # Entropy change plot
        plt.subplot(2, 3, 1)
        plt.plot(swap_params, entropy_changes, 'ro-', linewidth=1, markersize=3, alpha=0.7)
        plt.xlabel('Swap Parameter')
        plt.ylabel('Entropy Change')
        plt.title('Entropy Change vs Swap Parameter')
        plt.grid(True, alpha=0.3)
        
        # Original vs Permuted entropy
        plt.subplot(2, 3, 2)
        plt.plot(swap_params, original_entropies, 'bo-', label='Original Entropy', linewidth=1, markersize=3, alpha=0.7)
        plt.plot(swap_params, permuted_entropies, 'ro-', label='Permuted Entropy', linewidth=1, markersize=3, alpha=0.7)
        plt.xlabel('Swap Parameter')
        plt.ylabel('Entropy')
        plt.title('Original vs Permuted Entropy')
        plt.legend()
        plt.grid(True, alpha=0.3)
        
        # Entropy ratio
        plt.subplot(2, 3, 3)
        plt.plot(swap_params, entropy_ratios, 'go-', linewidth=1, markersize=3, alpha=0.7)
        plt.xlabel('Swap Parameter')
        plt.ylabel('Entropy Ratio (Permuted/Original)')
        plt.title('Entropy Ratio vs Swap Parameter')
        plt.grid(True, alpha=0.3)
        
        # Execution time for entropy analysis
        plt.subplot(2, 3, 4)
        plt.plot(swap_params, execution_times, 'mo-', linewidth=1, markersize=3, alpha=0.7)
        plt.xlabel('Swap Parameter')
        plt.ylabel('Execution Time (s)')
        plt.title('Entropy Analysis Execution Time')
        plt.grid(True, alpha=0.3)
        
        # Entropy change distribution
        plt.subplot(2, 3, 5)
        plt.hist(entropy_changes, bins=50, color='skyblue', alpha=0.7, edgecolor='black')
        plt.xlabel('Entropy Change')
        plt.ylabel('Frequency')
        plt.title('Distribution of Entropy Changes')
        plt.grid(True, alpha=0.3)
        
        # Entropy ratio distribution
        plt.subplot(2, 3, 6)
        plt.hist(entropy_ratios, bins=50, color='lightgreen', alpha=0.7, edgecolor='black')
        plt.xlabel('Entropy Ratio')
        plt.ylabel('Frequency')
        plt.title('Distribution of Entropy Ratios')
        plt.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.show()
        
        # Summary statistics
        print(f"\n=== Full Spectrum Entropy Analysis Summary ===")
        print(f"Total data points: {len(swap_params)}")
        print(f"Average entropy change: {statistics.mean(entropy_changes):.4f}")
        print(f"Average entropy ratio: {statistics.mean(entropy_ratios):.4f}")
        print(f"Average execution time: {statistics.mean(execution_times):.6f}s")
        print(f"Min entropy change: {min(entropy_changes):.4f}")
        print(f"Max entropy change: {max(entropy_changes):.4f}")
        print(f"Min entropy ratio: {min(entropy_ratios):.4f}")
        print(f"Max entropy ratio: {max(entropy_ratios):.4f}")

    # 4. Permutation consistency: error and determinism
    swap_params = list(results['permutation_consistency'].keys())
    avg_errors = [results['permutation_consistency'][p]['avg_restoration_error'] for p in swap_params]
    deterministic = [results['permutation_consistency'][p]['deterministic'] for p in swap_params]
    
    plt.figure(figsize=(12, 5))
    plt.subplot(1, 2, 1)
    plt.plot(swap_params, avg_errors, 'o-', label='Avg Restoration Error', linewidth=2, markersize=8)
    plt.xlabel('Swap Param')
    plt.ylabel('Avg Restoration Error')
    plt.title('Restoration Error vs Swap Param')
    plt.grid(True)
    
    plt.subplot(1, 2, 2)
    plt.plot(swap_params, deterministic, 'gs', label='Deterministic (1=True, 0=False)', markersize=10)
    plt.xlabel('Swap Param')
    plt.ylabel('Deterministic')
    plt.title('Determinism vs Swap Param')
    plt.yticks([0, 1])
    plt.grid(True)
    plt.tight_layout()
    plt.show()

    # 5. Performance summary
    bench_labels = []
    permute_times = []
    fft_times = []
    for range_name, b in results['benchmarks'].items():
        bench_labels.append(range_name)
        permute_times.append(b['permutation']['avg_permute_time'])
        fft_times.append(b['fft_analysis']['mean_time'])
    
    plt.figure(figsize=(12, 5))
    plt.subplot(1, 2, 1)
    plt.bar(bench_labels, permute_times, color='orange')
    plt.ylabel('Avg Permutation Time (s)')
    plt.title('Permutation Speed by Swap Param Range')
    plt.xticks(rotation=30)
    
    plt.subplot(1, 2, 2)
    plt.bar(bench_labels, fft_times, color='purple')
    plt.ylabel('Avg FFT Analysis Time (s)')
    plt.title('FFT Analysis Speed by Swap Param Range')
    plt.xticks(rotation=30)
    plt.tight_layout()
    plt.show()

    # 6. Frequency spectrum analysis
    if 'sine_generation' in results:
        all_frequencies = []
        all_amplitudes = []
        for range_name, data in results['sine_generation'].items():
            all_frequencies.extend(data.get('frequencies', []))
            all_amplitudes.extend(data.get('amplitudes', []))
        
        if all_frequencies:
            plt.figure(figsize=(12, 6))
            plt.scatter(all_frequencies, all_amplitudes, alpha=0.6, s=20)
            plt.xlabel('Frequency (Hz)')
            plt.ylabel('RMS Amplitude')
            plt.title('Frequency vs Amplitude Across Full Spectrum')
            plt.grid(True)
            plt.tight_layout()
            plt.show()


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Full Spectrum SineShift Test Suite - Benchmark and Stress Testing",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python test_sineshift_fullspectrum.py              # Run full test suite
  python test_sineshift_fullspectrum.py --fast       # Run with reduced iterations
  python test_sineshift_fullspectrum.py --size 500   # Custom test size
  python test_sineshift_fullspectrum.py --plot       # Show plots after test
        """
    )
    
    parser.add_argument(
        '--fast', '-f',
        action='store_true',
        help='Run with reduced iterations for faster testing'
    )
    parser.add_argument(
        '--plot', '-p',
        action='store_true',
        help='Show matplotlib plots after test'
    )
    parser.add_argument(
        '--size', '-s',
        type=int,
        default=1000,
        help='Number of iterations for consistency tests (default: 1000)'
    )
    parser.add_argument(
        '--frame-count', '-fc',
        type=int,
        default=10000,
        help='Frame count for tests (default: 10000)'
    )
    parser.add_argument(
        '--output', '-o',
        type=str,
        help='Save results to JSON file'
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_arguments()
    
    # Adjust test parameters for fast mode
    test_size = args.size // 10 if args.fast else args.size
    frame_count = args.frame_count // 10 if args.fast else args.frame_count
    
    print(f"Running Full Spectrum Test Suite")
    print(f"Test Size: {test_size}")
    print(f"Frame Count: {frame_count}")
    print(f"Fast Mode: {args.fast}")
    
    # Create and run tester
    tester = FullSpectrumTester(test_size=test_size, frame_count=frame_count)
    results = tester.run_comprehensive_test()
    
    # Generate plots if requested
    if args.plot:
        print("\nGenerating plots...")
        plot_fullspectrum_results(results)
        print("Plotting completed!")
    
    # Save results if requested
    if args.output:
        import json
        # Convert numpy types to native Python types for JSON serialization
        def convert_numpy(obj):
            if isinstance(obj, np.ndarray):
                return obj.tolist()
            elif isinstance(obj, np.integer):
                return int(obj)
            elif isinstance(obj, np.floating):
                return float(obj)
            elif isinstance(obj, dict):
                return {k: convert_numpy(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [convert_numpy(item) for item in obj]
            return obj
        
        results_json = convert_numpy(results)
        
        with open(args.output, 'w') as f:
            json.dump(results_json, f, indent=2)
        
        print(f"\nResults saved to: {args.output}")
    
    # Exit with error code if there were errors
    if results['errors']:
        print(f"\nExiting with error code due to {len(results['errors'])} errors")
        sys.exit(1)
    else:
        print("\nAll tests completed successfully!")
        sys.exit(0) 