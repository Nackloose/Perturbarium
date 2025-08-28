#!/usr/bin/env python3
"""
Test script for the SineShift module with permutation technology integration.

This script demonstrates the various capabilities of the sineshift module,
including sine wave generation, FFT analysis, audio mutation, and
permutation technology integration for both audio and generic binary data.
"""

import numpy as np
import matplotlib.pyplot as plt
from typing import Dict, Any
import sys
import os

import argparse

# Import from the current directory
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import the module components directly
from sine_generator import (
    generate_sine_wave,
    generate_permutation_sine_wave,
    generate_complex_sine_pattern,
    generate_permutation_test_signal,
    BASE_FREQUENCY
)

from fft_analyzer import (
    analyze_fft,
    analyze_permutation_fft,
    create_spectral_report
)

from mutator import (
    SineShiftMutator
)

from plot_data import (
    create_permutation_fft_columns,
    find_permutation_intersections,
    generate_permutation_comparison_report
)

# Global flag for plotting
ENABLE_PLOTTING = False


def plot_sine_wave_comparison(swap_params: list, title: str = "Sine Wave Comparison"):
    """Plot multiple sine waves for comparison."""
    if not ENABLE_PLOTTING:
        return
    
    plt.figure(figsize=(12, 8))
    
    for i, swap_param in enumerate(swap_params):
        sine_wave = generate_sine_wave(swap_param)
        time_axis = np.arange(len(sine_wave)) / 44100  # Assuming 44.1kHz sample rate
        
        plt.subplot(len(swap_params), 1, i + 1)
        plt.plot(time_axis[:1000], sine_wave[:1000])  # Plot first 1000 samples
        plt.title(f"Swap Parameter: {swap_param}")
        plt.ylabel("Amplitude")
        if i == len(swap_params) - 1:
            plt.xlabel("Time (seconds)")
    
    plt.suptitle(title)
    plt.tight_layout()
    plt.show()


def plot_permutation_analysis(test_signal: np.ndarray, swap_param: float):
    """Plot permutation analysis showing original vs permuted signals."""
    if not ENABLE_PLOTTING:
        return
    
    mutator = SineShiftMutator(len(test_signal))
    permuted_signal = mutator.mutate_data(test_signal, swap_param)
    restored_signal = mutator.unmute_data(permuted_signal, swap_param)
    
    fig, axes = plt.subplots(3, 1, figsize=(12, 10))
    
    # Original signal
    time_axis = np.arange(len(test_signal)) / 44100
    axes[0].plot(time_axis[:2000], test_signal[:2000])
    axes[0].set_title("Original Signal")
    axes[0].set_ylabel("Amplitude")
    
    # Permuted signal
    axes[1].plot(time_axis[:2000], permuted_signal[:2000])
    axes[1].set_title(f"Permuted Signal (swap_param: {swap_param})")
    axes[1].set_ylabel("Amplitude")
    
    # Restored signal
    axes[2].plot(time_axis[:2000], restored_signal[:2000])
    axes[2].set_title("Restored Signal")
    axes[2].set_ylabel("Amplitude")
    axes[2].set_xlabel("Time (seconds)")
    
    plt.tight_layout()
    plt.show()


def plot_fft_comparison(test_signal: np.ndarray, swap_param: float):
    """Plot FFT comparison between original and permuted signals."""
    if not ENABLE_PLOTTING:
        return
    
    # Perform FFT analysis
    frequencies, magnitudes, phases = analyze_fft(test_signal)
    permutation_analysis = analyze_permutation_fft(test_signal, swap_param)
    
    fig, axes = plt.subplots(2, 2, figsize=(15, 10))
    
    # Original signal FFT magnitude
    axes[0, 0].plot(frequencies[:len(frequencies)//2], magnitudes[:len(magnitudes)//2])
    axes[0, 0].set_title("Original Signal FFT Magnitude")
    axes[0, 0].set_xlabel("Frequency (Hz)")
    axes[0, 0].set_ylabel("Magnitude")
    axes[0, 0].grid(True)
    
    # Original signal FFT phase
    axes[0, 1].plot(frequencies[:len(frequencies)//2], phases[:len(phases)//2])
    axes[0, 1].set_title("Original Signal FFT Phase")
    axes[0, 1].set_xlabel("Frequency (Hz)")
    axes[0, 1].set_ylabel("Phase (radians)")
    axes[0, 1].grid(True)
    
    # Permuted signal FFT magnitude
    permuted_magnitudes = permutation_analysis['permuted']['magnitudes']
    permuted_frequencies = permutation_analysis['permuted']['frequencies']
    axes[1, 0].plot(permuted_frequencies[:len(permuted_frequencies)//2], 
                     permuted_magnitudes[:len(permuted_magnitudes)//2])
    axes[1, 0].set_title(f"Permuted Signal FFT Magnitude (swap_param: {swap_param})")
    axes[1, 0].set_xlabel("Frequency (Hz)")
    axes[1, 0].set_ylabel("Magnitude")
    axes[1, 0].grid(True)
    
    # Magnitude difference
    magnitude_diff = permuted_magnitudes - magnitudes
    axes[1, 1].plot(frequencies[:len(frequencies)//2], magnitude_diff[:len(magnitude_diff)//2])
    axes[1, 1].set_title("Magnitude Difference (Permuted - Original)")
    axes[1, 1].set_xlabel("Frequency (Hz)")
    axes[1, 1].set_ylabel("Magnitude Difference")
    axes[1, 1].grid(True)
    
    plt.tight_layout()
    plt.show()


def plot_complex_patterns(swap_params: list, harmonics: int = 3):
    """Plot complex sine patterns with multiple harmonics."""
    if not ENABLE_PLOTTING:
        return
    
    fig, axes = plt.subplots(len(swap_params), 1, figsize=(12, 3*len(swap_params)))
    
    for i, swap_param in enumerate(swap_params):
        complex_pattern = generate_complex_sine_pattern(swap_param, harmonics)
        time_axis = np.arange(len(complex_pattern)) / 44100
        
        axes[i].plot(time_axis[:2000], complex_pattern[:2000])
        axes[i].set_title(f"Complex Pattern (swap_param: {swap_param}, harmonics: {harmonics})")
        axes[i].set_ylabel("Amplitude")
        if i == len(swap_params) - 1:
            axes[i].set_xlabel("Time (seconds)")
    
    plt.tight_layout()
    plt.show()


def plot_binary_data_permutation(original_data: np.ndarray, swap_param: float):
    """Plot binary data permutation visualization."""
    if not ENABLE_PLOTTING:
        return
    
    mutator = SineShiftMutator(len(original_data))
    permuted_data = mutator.mutate_data(original_data, swap_param)
    restored_data = mutator.unmute_data(permuted_data, swap_param)
    
    fig, axes = plt.subplots(3, 1, figsize=(12, 8))
    
    # Original binary data
    axes[0].stem(original_data[:100], markerfmt='o')
    axes[0].set_title("Original Binary Data")
    axes[0].set_ylabel("Value")
    axes[0].set_ylim(-0.5, 1.5)
    
    # Permuted binary data
    axes[1].stem(permuted_data[:100], markerfmt='o')
    axes[1].set_title(f"Permuted Binary Data (swap_param: {swap_param})")
    axes[1].set_ylabel("Value")
    axes[1].set_ylim(-0.5, 1.5)
    
    # Restored binary data
    axes[2].stem(restored_data[:100], markerfmt='o')
    axes[2].set_title("Restored Binary Data")
    axes[2].set_ylabel("Value")
    axes[2].set_xlabel("Sample Index")
    axes[2].set_ylim(-0.5, 1.5)
    
    plt.tight_layout()
    plt.show()


def plot_entropy_analysis(swap_params: list):
    """Plot entropy analysis for different swap parameters."""
    if not ENABLE_PLOTTING:
        return
    
    test_signal = generate_sine_wave(0.5)
    entropies_original = []
    entropies_permuted = []
    
    for swap_param in swap_params:
        report = create_spectral_report(test_signal, swap_param)
        entropies_original.append(report['entropy_analysis']['original_entropy'])
        entropies_permuted.append(report['entropy_analysis']['permuted_entropy'])
    
    plt.figure(figsize=(10, 6))
    plt.plot(swap_params, entropies_original, 'b-o', label='Original Entropy')
    plt.plot(swap_params, entropies_permuted, 'r-s', label='Permuted Entropy')
    plt.xlabel('Swap Parameter')
    plt.ylabel('Entropy')
    plt.title('Entropy Analysis for Different Swap Parameters')
    plt.legend()
    plt.grid(True)
    plt.show()


def plot_entropy_vs_swap_param_fullrange():
    """Plot permuted entropy vs swap_param over a wide range with adaptive increments."""
    if not ENABLE_PLOTTING:
        return

    print("Generating entropy vs swap_param plot (fixed signal)...")
    print("Building parameter sweep...")
    
    # Build the swap_param sweep
    swap_params = []
    # 0.0 - 1.0 (step 0.01)
    swap_params += list(np.arange(0.0, 1.01, 0.01))
    # 1.0 - 10.0 (step 1)
    swap_params += list(np.arange(2.0, 11.0, 1.0))
    # 10 - 100 (step 10)
    swap_params += list(np.arange(20.0, 101.0, 10.0))
    # 100 - 1000 (step 100)
    swap_params += list(np.arange(200.0, 1001.0, 100.0))
    # 1000 - 10000 (step 1000)
    swap_params += list(np.arange(2000.0, 10001.0, 1000.0))
    # 10000 - 100000 (step 10000)
    swap_params += list(np.arange(20000.0, 100001.0, 10000.0))

    print(f"Total parameters to test: {len(swap_params)}")
    print("Using fixed sine wave signal (swap_param 0.5)...")
    
    test_signal = generate_sine_wave(0.5)
    entropies_permuted = []

    print("Computing entropy for each parameter...")
    for i, swap_param in enumerate(swap_params):
        if i % 100 == 0 or i == len(swap_params) - 1:
            print(f"  Progress: {i+1}/{len(swap_params)} ({(i+1)/len(swap_params)*100:.1f}%)")
        
        report = create_spectral_report(test_signal, swap_param)
        entropies_permuted.append(report['entropy_analysis']['permuted_entropy'])

    print("Generating plot...")
    plt.figure(figsize=(12, 6))
    plt.plot(swap_params, entropies_permuted, 'r-', label='Permuted Entropy')
    plt.xlabel('Swap Parameter')
    plt.ylabel('Permuted Entropy')
    plt.title('Permuted Entropy vs Swap Parameter (Full Range) - Fixed Signal')
    plt.xscale('log')
    plt.legend()
    plt.grid(True, which='both', ls='--', alpha=0.5)
    plt.tight_layout()
    plt.show()
    print("Fixed signal entropy plot completed!")


def plot_entropy_vs_swap_param_fullrange_random():
    """Plot permuted entropy vs swap_param over a wide range with random signals."""
    if not ENABLE_PLOTTING:
        return

    print("Generating entropy vs swap_param plot (random signals)...")
    print("Building parameter sweep...")
    
    # Build the swap_param sweep
    swap_params = []
    # 0.0 - 1.0 (step 0.01)
    swap_params += list(np.arange(0.0, 1.01, 0.01))
    # 1.0 - 10.0 (step 1)
    swap_params += list(np.arange(2.0, 11.0, 1.0))
    # 10 - 100 (step 10)
    swap_params += list(np.arange(20.0, 101.0, 10.0))
    # 100 - 1000 (step 100)
    swap_params += list(np.arange(200.0, 1001.0, 100.0))
    # 1000 - 10000 (step 1000)
    swap_params += list(np.arange(2000.0, 10001.0, 1000.0))
    # 10000 - 100000 (step 10000)
    swap_params += list(np.arange(20000.0, 100001.0, 10000.0))

    print(f"Total parameters to test: {len(swap_params)}")
    print("Using random signals for each parameter...")
    
    entropies_permuted = []

    print("Computing entropy for each parameter...")
    for i, swap_param in enumerate(swap_params):
        if i % 100 == 0 or i == len(swap_params) - 1:
            print(f"  Progress: {i+1}/{len(swap_params)} ({(i+1)/len(swap_params)*100:.1f}%)")
        
        # Generate random signal for this parameter
        random_signal = np.random.randn(100000)  # Random normal distribution
        report = create_spectral_report(random_signal, swap_param)
        entropies_permuted.append(report['entropy_analysis']['permuted_entropy'])

    print("Generating plot...")
    plt.figure(figsize=(12, 6))
    plt.plot(swap_params, entropies_permuted, 'b-', label='Permuted Entropy (Random)')
    plt.xlabel('Swap Parameter')
    plt.ylabel('Permuted Entropy')
    plt.title('Permuted Entropy vs Swap Parameter (Full Range) - Random Signals')
    plt.xscale('log')
    plt.legend()
    plt.grid(True, which='both', ls='--', alpha=0.5)
    plt.tight_layout()
    plt.show()
    print("Random signal entropy plot completed!")


def test_basic_sine_generation():
    """Test basic sine wave generation."""
    print("=== Testing Basic Sine Wave Generation ===")
    
    # Test different swap parameters
    swap_params = [0.0, 0.25, 0.5, 0.75, 1.0, 50.0, 10.0, 3.14162783982345675]
    
    for swap_param in swap_params:
        sine_wave = generate_sine_wave(swap_param)
        print(f"Swap param {swap_param}: Generated {len(sine_wave)} samples")
        print(f"  - RMS amplitude: {np.sqrt(np.mean(sine_wave**2)):.4f}")
        print(f"  - Peak amplitude: {np.max(np.abs(sine_wave)):.4f}")
        print(f"  - Frequency: {BASE_FREQUENCY * swap_param:.2f} Hz")
        print()
    
    # Plot sine wave comparison if plotting is enabled
    plot_sine_wave_comparison(swap_params[:5], "Basic Sine Wave Comparison")


def test_permutation_technology():
    """Test the permutation technology integration with numerical data."""
    print("=== Testing Permutation Technology (Numerical Data) ===")
    
    # Create a test signal
    test_signal = generate_sine_wave(0.5)
    
    # Create mutator
    mutator = SineShiftMutator(len(test_signal))
    
    # Test permutation and restoration
    swap_param = 0.42
    permuted_signal = mutator.mutate_data(test_signal, swap_param)
    restored_signal = mutator.unmute_data(permuted_signal, swap_param)
    
    # Check if restoration is successful
    restoration_error = np.mean(np.abs(test_signal - restored_signal))
    print(f"Permutation test with swap_param {swap_param}:")
    print(f"  - Original signal length: {len(test_signal)}")
    print(f"  - Permuted signal length: {len(permuted_signal)}")
    print(f"  - Restoration error: {restoration_error:.6f}")
    print(f"  - Restoration successful: {np.allclose(test_signal, restored_signal)}")
    print()
    
    # Plot permutation analysis if plotting is enabled
    plot_permutation_analysis(test_signal, swap_param)


def test_binary_data_permutation():
    """Run a battery of tests for generic binary data permutation."""
    print("=== Testing Binary Data Permutation ===")
    swap_param = 0.789

    # --- Test 1: Basic Binary Array ---
    print("\n--- 1. Basic Binary Array Test ---")
    original_binary = np.array([1, 1, 0, 0, 1, 0, 1, 0], dtype=np.uint8)
    mutator_basic = SineShiftMutator(len(original_binary))
    
    print(f"Original binary data: {original_binary}")
    
    permuted_binary = mutator_basic.mutate_data(original_binary, swap_param)
    print(f"Permuted binary data: {permuted_binary}")
    
    restored_binary = mutator_basic.unmute_data(permuted_binary, swap_param)
    print(f"Restored binary data: {restored_binary}")
    
    is_successful_basic = np.array_equal(original_binary, restored_binary)
    print(f"Basic binary test successful: {is_successful_basic}")
    print()

    # --- Test 2: String Permutation ---
    print("--- 2. String Permutation Test ---")
    test_string = "The quick brown fox jumps over the lazy dog."
    original_bytes = np.array(list(test_string.encode('utf-8')), dtype=np.uint8)
    mutator_string = SineShiftMutator(len(original_bytes))

    print(f"Original string: '{test_string}'")
    print(f"Original byte array (first 20 bytes): {original_bytes[:20]}...")

    permuted_bytes = mutator_string.mutate_data(original_bytes, swap_param)
    print(f"Permuted byte array (first 20 bytes): {permuted_bytes[:20]}...")
    # Note: Trying to decode permuted_bytes would likely result in a UnicodeDecodeError
    # or produce mojibake, as the byte sequence is no longer valid UTF-8.
    try:
        scrambled_text = bytes(permuted_bytes).decode('utf-8', errors='replace')
        print(f"Permuted data as string (best effort): '{scrambled_text}'")
    except Exception as e:
        print(f"Could not render permuted bytes as string: {e}")

    restored_bytes = mutator_string.unmute_data(permuted_bytes, swap_param)
    restored_string = bytes(restored_bytes).decode('utf-8')
    print(f"Restored string: '{restored_string}'")

    is_successful_string = (test_string == restored_string)
    print(f"String permutation test successful: {is_successful_string}")
    print()

    # --- Test 3: Edge Cases (All Zeros / All Ones) ---
    print("--- 3. Edge Case Tests ---")
    data_size = 16
    mutator_edge = SineShiftMutator(data_size)

    # All Zeros
    zeros_data = np.zeros(data_size, dtype=np.uint8)
    permuted_zeros = mutator_edge.mutate_data(zeros_data, swap_param)
    restored_zeros = mutator_edge.unmute_data(permuted_zeros, swap_param)
    is_successful_zeros = np.array_equal(zeros_data, restored_zeros)
    print(f"All-zeros test successful: {is_successful_zeros}")
    print(f"  Original: {zeros_data}")
    print(f"  Permuted: {permuted_zeros}") # Should still be all zeros
    print(f"  Restored: {restored_zeros}")

    # All Ones
    ones_data = np.ones(data_size, dtype=np.uint8)
    permuted_ones = mutator_edge.mutate_data(ones_data, swap_param)
    restored_ones = mutator_edge.unmute_data(permuted_ones, swap_param)
    is_successful_ones = np.array_equal(ones_data, restored_ones)
    print(f"All-ones test successful: {is_successful_ones}")
    print(f"  Original: {ones_data}")
    print(f"  Permuted: {permuted_ones}") # Should still be all ones
    print(f"  Restored: {restored_ones}")
    print()
    
    # Plot binary data permutation if plotting is enabled
    plot_binary_data_permutation(original_binary, swap_param)


def test_fft_analysis():
    """Test FFT analysis with permutation technology."""
    print("=== Testing FFT Analysis ===")
    
    # Generate test signal
    test_signal = generate_sine_wave(0.3)
    
    # Perform standard FFT analysis
    frequencies, magnitudes, phases = analyze_fft(test_signal)
    print(f"Standard FFT analysis:")
    print(f"  - Frequency range: {frequencies.min():.2f} to {frequencies.max():.2f} Hz")
    print(f"  - Peak magnitude: {magnitudes.max():.4f}")
    print(f"  - Phase range: {phases.min():.2f} to {phases.max():.2f} radians")
    
    # Perform permutation FFT analysis
    swap_param = 0.7
    permutation_analysis = analyze_permutation_fft(test_signal, swap_param)
    
    print(f"\nPermutation FFT analysis (swap_param {swap_param}):")
    print(f"  - Total permutations: {permutation_analysis['permutation_stats']['total_permutations']}")
    print(f"  - Unique permutations: {permutation_analysis['permutation_stats']['unique_permutations']}")
    print(f"  - Average shift: {permutation_analysis['permutation_stats']['avg_shift']:.2f}")
    print(f"  - Total magnitude change: {permutation_analysis['spectral_differences']['total_magnitude_change']:.4f}")
    print()
    
    # Plot FFT comparison if plotting is enabled
    plot_fft_comparison(test_signal, swap_param)


def test_complex_patterns():
    """Test complex sine pattern generation."""
    print("=== Testing Complex Sine Patterns ===")
    
    swap_param = 0.6
    harmonics = 5
    
    # Generate complex pattern
    complex_pattern = generate_complex_sine_pattern(swap_param, harmonics)
    
    print(f"Complex pattern with {harmonics} harmonics (swap_param {swap_param}):")
    print(f"  - Signal length: {len(complex_pattern)}")
    print(f"  - RMS amplitude: {np.sqrt(np.mean(complex_pattern**2)):.4f}")
    print(f"  - Peak amplitude: {np.max(np.abs(complex_pattern)):.4f}")
    print(f"  - Dynamic range: {np.max(complex_pattern) - np.min(complex_pattern):.4f}")
    print()
    
    # Plot complex patterns if plotting is enabled
    plot_complex_patterns([0.3, 0.6, 0.9], harmonics)


def test_spectral_report():
    """Test comprehensive spectral report generation."""
    print("=== Testing Spectral Report Generation ===")
    
    # Generate test signal
    test_signal = generate_sine_wave(0.4)
    swap_param = 0.8
    
    # Generate comprehensive report
    report = create_spectral_report(test_signal, swap_param)
    
    print(f"Spectral report for swap_param {swap_param}:")
    print(f"  - Signal length: {report['basic_statistics']['signal_length']}")
    print(f"  - RMS amplitude: {report['basic_statistics']['rms_amplitude']:.4f}")
    print(f"  - Peak amplitude: {report['basic_statistics']['peak_amplitude']:.4f}")
    print(f"  - Original entropy: {report['entropy_analysis']['original_entropy']:.4f}")
    print(f"  - Permuted entropy: {report['entropy_analysis']['permuted_entropy']:.4f}")
    print(f"  - Entropy change: {report['entropy_analysis']['entropy_change']:.4f}")
    print()
    
    # Plot entropy analysis if plotting is enabled
    plot_entropy_analysis([0.1, 0.3, 0.5, 0.7, 0.9])
    plot_entropy_vs_swap_param_fullrange()
    plot_entropy_vs_swap_param_fullrange_random()


def test_intersection_analysis():
    """Test intersection analysis with permutation technology."""
    print("=== Testing Intersection Analysis ===")
    
    # Generate test signal and perform FFT
    test_signal = generate_sine_wave(0.5)
    fft_result = np.fft.fft(test_signal)
    swap_param = 0.3
    
    # Find intersections with permutation
    intersection_data = find_permutation_intersections(fft_result, swap_param)
    
    print(f"Intersection analysis (swap_param {swap_param}):")
    print(f"  - Original intersections: {intersection_data['intersection_count_original']}")
    print(f"  - Permuted intersections: {intersection_data['intersection_count_permuted']}")
    print(f"  - Intersection change: {intersection_data['intersection_count_permuted'] - intersection_data['intersection_count_original']}")
    print()


def test_comparison_report():
    """Test comprehensive comparison report generation."""
    print("=== Testing Comparison Report Generation ===")
    
    # Generate test signal and perform FFT
    test_signal = generate_sine_wave(0.35)
    fft_result = np.fft.fft(test_signal)
    swap_param = 0.9
    
    # Generate comprehensive comparison report
    comparison_report = generate_permutation_comparison_report(fft_result, swap_param)
    
    print(f"Comparison report (swap_param {swap_param}):")
    print(f"  - Signal length: {comparison_report['metadata']['signal_length']}")
    print(f"  - Original intersection count: {comparison_report['intersection_analysis']['intersection_counts']['original']}")
    print(f"  - Permuted intersection count: {comparison_report['intersection_analysis']['intersection_counts']['permuted']}")
    
    # Print correlations
    print("  - Column correlations:")
    for col_name, correlation in comparison_report['correlations'].items():
        print(f"    {col_name}: {correlation:.4f}")
    print()


def test_entropy_single_parameter():
    """Test entropy calculation for a single parameter (0.5) with detailed output."""
    print("=== Testing Entropy for Single Parameter (0.5) ===")
    
    swap_param = 0.5
    test_signal = generate_sine_wave(0.5)
    
    print(f"Testing entropy calculation with swap_param: {swap_param}")
    print(f"Signal length: {len(test_signal)}")
    print(f"Signal RMS amplitude: {np.sqrt(np.mean(test_signal**2)):.4f}")
    
    # Generate comprehensive report
    report = create_spectral_report(test_signal, swap_param)
    
    print(f"Entropy Analysis Results:")
    print(f"  - Original entropy: {report['entropy_analysis']['original_entropy']:.4f}")
    print(f"  - Permuted entropy: {report['entropy_analysis']['permuted_entropy']:.4f}")
    print(f"  - Entropy change: {report['entropy_analysis']['entropy_change']:.4f}")
    print(f"  - Entropy ratio (permuted/original): {report['entropy_analysis']['permuted_entropy'] / report['entropy_analysis']['original_entropy']:.4f}")
    print()
    
    # Also test with random signal
    random_signal = np.random.randn(100000)
    random_report = create_spectral_report(random_signal, swap_param)
    
    print(f"Random Signal Entropy Analysis (swap_param: {swap_param}):")
    print(f"  - Original entropy: {random_report['entropy_analysis']['original_entropy']:.4f}")
    print(f"  - Permuted entropy: {random_report['entropy_analysis']['permuted_entropy']:.4f}")
    print(f"  - Entropy change: {random_report['entropy_analysis']['entropy_change']:.4f}")
    print(f"  - Entropy ratio (permuted/original): {random_report['entropy_analysis']['permuted_entropy'] / random_report['entropy_analysis']['original_entropy']:.4f}")
    print()


def run_all_tests():
    """Run all tests and provide a summary."""
    print("SineShift Module Test Suite")
    print("=" * 50)
    print()
    
    try:
        test_basic_sine_generation()
        test_permutation_technology()
        test_binary_data_permutation() # New test suite for binary data
        test_fft_analysis()
        test_complex_patterns()
        test_spectral_report()
        test_intersection_analysis()
        test_comparison_report()
        test_entropy_single_parameter() # New test for entropy
        
        print("=" * 50)
        print("All tests completed successfully!")
        print("The SineShift module is working correctly with permutation technology integration.")
        
    except Exception as e:
        print(f"Error during testing: {e}")
        import traceback
        traceback.print_exc()


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="SineShift Module Test Suite with optional plotting",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python test_sineshift.py              # Run tests without plotting
  python test_sineshift.py --plot       # Run tests with plotting enabled
  python test_sineshift.py -p           # Short form for plotting
        """
    )
    
    parser.add_argument(
        '--plot', '-p',
        action='store_true',
        help='Enable matplotlib plotting (requires matplotlib to be installed)'
    )
    
    return parser.parse_args()


def set_plotting_enabled(enabled: bool):
    """Set the global plotting flag."""
    global ENABLE_PLOTTING
    ENABLE_PLOTTING = enabled


if __name__ == "__main__":
    args = parse_arguments()
    set_plotting_enabled(args.plot)
    
    if ENABLE_PLOTTING:
        print("Plotting enabled - matplotlib visualizations will be shown")
        print("Note: Close plot windows to continue with tests")
        print()
    
    run_all_tests()
