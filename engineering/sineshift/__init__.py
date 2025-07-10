# SineShift module with permutation technology integration
# 
# This module provides sine wave generation, FFT analysis, and audio mutation
# capabilities using sine wave-based permutation technology adapted from
# the licensee/permutation.py algorithm.

from .sine_generator import (
    generate_sine_wave,
    generate_permutation_sine_wave,
    generate_complex_sine_pattern,
    generate_permutation_test_signal,
    generate_frequency_sweep_sine,
    generate_modulated_sine_wave,
    FRAME_COUNT,
    BASE_FREQUENCY
)

from .fft_analyzer import (
    analyze_fft,
    analyze_permutation_fft,
    analyze_harmonic_content,
    analyze_spectral_entropy,
    create_spectral_report
)

from .mutator import (
    SineShiftMutator,
    create_mutator
)

from .plot_data import (
    create_fft_columns,
    find_intersections,
    create_permutation_fft_columns,
    find_permutation_intersections,
    analyze_intersection_patterns,
    create_spectral_visualization_data,
    generate_permutation_comparison_report
)

__version__ = "1.0.0"
__author__ = "EPStudio Team"

# Main classes and functions for easy access
__all__ = [
    # Sine wave generation
    'generate_sine_wave',
    'generate_permutation_sine_wave',
    'generate_complex_sine_pattern',
    'generate_permutation_test_signal',
    'generate_frequency_sweep_sine',
    'generate_modulated_sine_wave',
    'FRAME_COUNT',
    'BASE_FREQUENCY',
    
    # FFT analysis
    'analyze_fft',
    'analyze_permutation_fft',
    'analyze_harmonic_content',
    'analyze_spectral_entropy',
    'create_spectral_report',
    
    # Mutation/shuffling
    'SineShiftMutator',
    'create_mutator',
    
    # Plot data and visualization
    'create_fft_columns',
    'find_intersections',
    'create_permutation_fft_columns',
    'find_permutation_intersections',
    'analyze_intersection_patterns',
    'create_spectral_visualization_data',
    'generate_permutation_comparison_report'
]
