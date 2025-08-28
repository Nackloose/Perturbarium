# Sine wave generation with permutation technology integration

import numpy as np
import math
from typing import Tuple, Optional
from mutator import SineShiftMutator

FRAME_COUNT = 100000
BASE_FREQUENCY = 10  # Example base frequency


def generate_sine_wave(swap_param: float) -> np.ndarray:
    """Generates a sine wave of FRAME_COUNT frames influenced by swap_param."""
    # Ensure swap_param is within the expected range [0, 1]
    scaled_param = np.clip(swap_param, 0.0, 1.0)

    # Scale the base frequency by the swap_param
    frequency = BASE_FREQUENCY * scaled_param

    # Generate the time array
    t = np.linspace(0, 1, FRAME_COUNT, endpoint=False)

    # Generate the sine wave
    sine_wave = np.sin(2 * np.pi * frequency * t)

    return sine_wave


def generate_permutation_sine_wave(swap_param: float, frame_count: int = FRAME_COUNT) -> Tuple[np.ndarray, np.ndarray]:
    """Generates a sine wave and its permutation map using the permutation technology.
    
    Args:
        swap_param: A float value between 0.0 and 1.0.
        frame_count: The number of frames to generate.
        
    Returns:
        Tuple containing the sine wave and its permutation map.
    """
    # Generate the base sine wave
    sine_wave = generate_sine_wave(swap_param)
    
    # Create a mutator to generate the permutation map
    mutator = SineShiftMutator(frame_count)
    permutation_map = mutator.generate_permutation_map(swap_param)
    
    return sine_wave, permutation_map


def generate_complex_sine_pattern(swap_param: float, harmonics: int = 3) -> np.ndarray:
    """Generates a complex sine pattern with multiple harmonics using permutation technology.
    
    Args:
        swap_param: A float value between 0.0 and 1.0.
        harmonics: Number of harmonics to add.
        
    Returns:
        Complex sine wave pattern.
    """
    # Generate base sine wave
    base_wave = generate_sine_wave(swap_param)
    
    # Create mutator for permutation
    mutator = SineShiftMutator(FRAME_COUNT)
    
    # Generate complex pattern by adding harmonics and applying permutation
    complex_pattern = base_wave.copy()
    
    for i in range(2, harmonics + 1):
        # Generate harmonic with frequency multiplied by harmonic number
        harmonic_freq = BASE_FREQUENCY * swap_param * i
        t = np.linspace(0, 1, FRAME_COUNT, endpoint=False)
        harmonic = np.sin(2 * np.pi * harmonic_freq * t) / i  # Reduce amplitude for higher harmonics
        
        # Apply permutation to harmonic
        permuted_harmonic = mutator.mutate_data(harmonic, swap_param)
        
        # Add to complex pattern
        complex_pattern += permuted_harmonic
    
    return complex_pattern


def generate_permutation_test_signal(swap_param: float) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Generates a test signal that demonstrates the permutation technology.
    
    Args:
        swap_param: A float value between 0.0 and 1.0.
        
    Returns:
        Tuple containing original signal, permuted signal, and restored signal.
    """
    # Generate original sine wave
    original_signal = generate_sine_wave(swap_param)
    
    # Create mutator
    mutator = SineShiftMutator(FRAME_COUNT)
    
    # Apply permutation
    permuted_signal = mutator.mutate_data(original_signal, swap_param)
    
    # Restore signal
    restored_signal = mutator.unmute_data(permuted_signal, swap_param)
    
    return original_signal, permuted_signal, restored_signal


def generate_frequency_sweep_sine(swap_param: float, start_freq: float = 1.0, end_freq: float = 100.0) -> np.ndarray:
    """Generates a frequency sweep sine wave influenced by swap_param.
    
    Args:
        swap_param: A float value between 0.0 and 1.0.
        start_freq: Starting frequency in Hz.
        end_freq: Ending frequency in Hz.
        
    Returns:
        Frequency sweep sine wave.
    """
    # Calculate frequency range based on swap_param
    freq_range = end_freq - start_freq
    current_freq = start_freq + (freq_range * swap_param)
    
    # Generate time array
    t = np.linspace(0, 1, FRAME_COUNT, endpoint=False)
    
    # Generate frequency sweep
    sweep_wave = np.sin(2 * np.pi * current_freq * t)
    
    return sweep_wave


def generate_modulated_sine_wave(swap_param: float, modulation_depth: float = 0.5) -> np.ndarray:
    """Generates a frequency-modulated sine wave using permutation technology.
    
    Args:
        swap_param: A float value between 0.0 and 1.0.
        modulation_depth: Depth of frequency modulation (0.0 to 1.0).
        
    Returns:
        Frequency-modulated sine wave.
    """
    # Generate base sine wave
    base_wave = generate_sine_wave(swap_param)
    
    # Create mutator for modulation
    mutator = SineShiftMutator(FRAME_COUNT)
    
    # Generate modulation signal using permutation
    modulation_signal = mutator.mutate_data(base_wave, swap_param * modulation_depth)
    
    # Apply frequency modulation
    t = np.linspace(0, 1, FRAME_COUNT, endpoint=False)
    carrier_freq = BASE_FREQUENCY * swap_param
    mod_freq = BASE_FREQUENCY * 0.1  # Modulation frequency
    
    # Create modulated signal
    modulated_wave = np.sin(2 * np.pi * carrier_freq * t + modulation_depth * modulation_signal)
    
    return modulated_wave
