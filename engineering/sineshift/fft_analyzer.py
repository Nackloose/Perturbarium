# FFT analysis with permutation technology integration

import numpy as np
from numpy.fft import fft, ifft
from typing import Tuple, List, Dict, Any
from mutator import SineShiftMutator


def analyze_fft(sine_wave: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Performs FFT on the sine wave and returns frequency magnitudes and phases.

    Returns:
        tuple[np.ndarray, np.ndarray, np.ndarray]: A tuple containing:
            - frequencies: The array of sample frequencies.
            - magnitudes: The array of FFT magnitudes.
            - phases: The array of FFT phases in radians.
    """
    # Perform FFT
    fft_result = fft(sine_wave)

    # Calculate frequencies corresponding to the FFT output
    # The Nyquist frequency is at index FRAME_COUNT // 2
    # We are interested in the positive frequencies (first half of the spectrum)
    FRAME_COUNT = len(sine_wave)
    sample_rate = 1  # Assuming a sample rate of 1 for simplicity for now
    frequencies = np.fft.fftfreq(FRAME_COUNT, d=1 / sample_rate)

    # Calculate magnitudes and phases
    magnitudes = np.abs(fft_result)
    phases = np.angle(fft_result)

    # We typically only look at the positive frequencies for magnitude/phase spectrum plots
    # However, the full fft_result is needed if we want to do IFFT later.
    # Let's return the full arrays for now.
    return frequencies, magnitudes, phases


def analyze_permutation_fft(sine_wave: np.ndarray, swap_param: float) -> Dict[str, Any]:
    """Performs FFT analysis with permutation technology integration.
    
    Args:
        sine_wave: The sine wave to analyze.
        swap_param: A float value between 0.0 and 1.0.
        
    Returns:
        Dictionary containing FFT analysis results with permutation data.
    """
    # Perform standard FFT analysis
    frequencies, magnitudes, phases = analyze_fft(sine_wave)
    
    # Create mutator for permutation analysis
    mutator = SineShiftMutator(len(sine_wave))
    
    # Generate permutation map
    permutation_map = mutator.generate_permutation_map(swap_param)
    
    # Apply permutation to the sine wave
    permuted_wave = mutator.mutate_data(sine_wave, swap_param)
    
    # Analyze permuted wave
    permuted_frequencies, permuted_magnitudes, permuted_phases = analyze_fft(permuted_wave)
    
    # Calculate permutation statistics
    permutation_stats = {
        'total_permutations': len(permutation_map),
        'unique_permutations': len(set(permutation_map)),
        'max_shift': max(permutation_map),
        'min_shift': min(permutation_map),
        'avg_shift': np.mean(permutation_map)
    }
    
    # Calculate spectral differences
    magnitude_diff = np.abs(magnitudes - permuted_magnitudes)
    phase_diff = np.abs(phases - permuted_phases)
    
    return {
        'original': {
            'frequencies': frequencies,
            'magnitudes': magnitudes,
            'phases': phases
        },
        'permuted': {
            'frequencies': permuted_frequencies,
            'magnitudes': permuted_magnitudes,
            'phases': permuted_phases
        },
        'permutation_map': permutation_map,
        'permutation_stats': permutation_stats,
        'spectral_differences': {
            'magnitude_diff': magnitude_diff,
            'phase_diff': phase_diff,
            'total_magnitude_change': np.sum(magnitude_diff),
            'total_phase_change': np.sum(phase_diff)
        }
    }


def analyze_harmonic_content(sine_wave: np.ndarray, swap_param: float, max_harmonics: int = 10) -> Dict[str, Any]:
    """Analyzes harmonic content using permutation technology.
    
    Args:
        sine_wave: The sine wave to analyze.
        swap_param: A float value between 0.0 and 1.0.
        max_harmonics: Maximum number of harmonics to analyze.
        
    Returns:
        Dictionary containing harmonic analysis results.
    """
    # Perform FFT analysis
    frequencies, magnitudes, phases = analyze_fft(sine_wave)
    
    # Find fundamental frequency (highest magnitude in positive frequencies)
    positive_freq_mask = frequencies > 0
    positive_magnitudes = magnitudes[positive_freq_mask]
    positive_frequencies = frequencies[positive_freq_mask]
    
    if len(positive_magnitudes) == 0:
        return {'error': 'No positive frequencies found'}
    
    fundamental_idx = np.argmax(positive_magnitudes)
    fundamental_freq = positive_frequencies[fundamental_idx]
    
    # Create mutator for permutation analysis
    mutator = SineShiftMutator(len(sine_wave))
    
    # Generate permuted wave
    permuted_wave = mutator.mutate_data(sine_wave, swap_param)
    permuted_frequencies, permuted_magnitudes, permuted_phases = analyze_fft(permuted_wave)
    
    # Analyze harmonics
    harmonics = []
    permuted_harmonics = []
    
    for i in range(1, max_harmonics + 1):
        harmonic_freq = fundamental_freq * i
        
        # Find closest frequency in original spectrum
        freq_diff = np.abs(positive_frequencies - harmonic_freq)
        closest_idx = np.argmin(freq_diff)
        
        if freq_diff[closest_idx] < fundamental_freq * 0.1:  # Within 10% of expected frequency
            harmonic_magnitude = positive_magnitudes[closest_idx]
            harmonic_phase = phases[positive_freq_mask][closest_idx]
            harmonics.append({
                'harmonic_number': i,
                'frequency': positive_frequencies[closest_idx],
                'magnitude': harmonic_magnitude,
                'phase': harmonic_phase
            })
        
        # Find closest frequency in permuted spectrum
        permuted_positive_mask = permuted_frequencies > 0
        permuted_positive_freqs = permuted_frequencies[permuted_positive_mask]
        permuted_positive_mags = permuted_magnitudes[permuted_positive_mask]
        permuted_positive_phases = permuted_phases[permuted_positive_mask]
        
        if len(permuted_positive_freqs) > 0:
            permuted_freq_diff = np.abs(permuted_positive_freqs - harmonic_freq)
            permuted_closest_idx = np.argmin(permuted_freq_diff)
            
            if permuted_freq_diff[permuted_closest_idx] < fundamental_freq * 0.1:
                permuted_harmonics.append({
                    'harmonic_number': i,
                    'frequency': permuted_positive_freqs[permuted_closest_idx],
                    'magnitude': permuted_positive_mags[permuted_closest_idx],
                    'phase': permuted_positive_phases[permuted_closest_idx]
                })
    
    return {
        'fundamental_frequency': fundamental_freq,
        'original_harmonics': harmonics,
        'permuted_harmonics': permuted_harmonics,
        'harmonic_count': len(harmonics),
        'permuted_harmonic_count': len(permuted_harmonics),
        'swap_param': swap_param
    }


def analyze_spectral_entropy(sine_wave: np.ndarray, swap_param: float) -> Dict[str, float]:
    """Analyzes spectral entropy before and after permutation.
    
    Args:
        sine_wave: The sine wave to analyze.
        swap_param: A float value between 0.0 and 1.0.
        
    Returns:
        Dictionary containing entropy analysis results.
    """
    # Perform FFT analysis
    frequencies, magnitudes, phases = analyze_fft(sine_wave)
    
    # Create mutator
    mutator = SineShiftMutator(len(sine_wave))
    
    # Generate permuted wave
    permuted_wave = mutator.mutate_data(sine_wave, swap_param)
    permuted_frequencies, permuted_magnitudes, permuted_phases = analyze_fft(permuted_wave)
    
    # Calculate spectral entropy
    def calculate_spectral_entropy(magnitudes):
        # Normalize magnitudes to create probability distribution
        total_power = np.sum(magnitudes)
        if total_power == 0:
            return 0.0
        
        probabilities = magnitudes / total_power
        # Remove zero probabilities to avoid log(0)
        probabilities = probabilities[probabilities > 0]
        
        # Calculate entropy: -sum(p * log2(p))
        entropy = -np.sum(probabilities * np.log2(probabilities))
        return entropy
    
    original_entropy = calculate_spectral_entropy(magnitudes)
    permuted_entropy = calculate_spectral_entropy(permuted_magnitudes)
    
    return {
        'original_entropy': original_entropy,
        'permuted_entropy': permuted_entropy,
        'entropy_change': permuted_entropy - original_entropy,
        'entropy_ratio': permuted_entropy / original_entropy if original_entropy > 0 else 0.0
    }


def create_spectral_report(sine_wave: np.ndarray, swap_param: float) -> Dict[str, Any]:
    """Creates a comprehensive spectral analysis report using permutation technology.
    
    Args:
        sine_wave: The sine wave to analyze.
        swap_param: A float value between 0.0 and 1.0.
        
    Returns:
        Dictionary containing comprehensive spectral analysis report.
    """
    # Perform all analyses
    permutation_analysis = analyze_permutation_fft(sine_wave, swap_param)
    harmonic_analysis = analyze_harmonic_content(sine_wave, swap_param)
    entropy_analysis = analyze_spectral_entropy(sine_wave, swap_param)
    
    # Basic statistics
    basic_stats = {
        'signal_length': len(sine_wave),
        'sample_rate': 1.0,  # Assuming 1 Hz for simplicity
        'duration_seconds': len(sine_wave),
        'rms_amplitude': np.sqrt(np.mean(sine_wave**2)),
        'peak_amplitude': np.max(np.abs(sine_wave)),
        'dynamic_range': np.max(sine_wave) - np.min(sine_wave)
    }
    
    return {
        'basic_statistics': basic_stats,
        'permutation_analysis': permutation_analysis,
        'harmonic_analysis': harmonic_analysis,
        'entropy_analysis': entropy_analysis,
        'swap_parameter': swap_param,
        'analysis_timestamp': np.datetime64('now')
    }
