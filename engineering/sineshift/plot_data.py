# Plot data structuring and intersection finding with permutation technology integration

import numpy as np
from numpy.fft import ifft
from typing import List, Tuple, Dict, Any, Optional
from mutator import SineShiftMutator


def create_fft_columns(
    fft_result: np.ndarray,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Creates three time-series 'columns' from the FFT result using IFFT.

    Args:
        fft_result: The complex result of the FFT.

    Returns:
        tuple[np.ndarray, np.ndarray, np.ndarray]: Three numpy arrays, each of the
            same length as the input FFT result, representing the three columns.
            Column 1: Real part of IFFT(FFT_result)
            Column 2: IFFT of magnitude spectrum (phase set to 0)
            Column 3: IFFT of phase spectrum (magnitude set to 1)
    """
    FRAME_COUNT = len(fft_result)

    # Column 1: Essentially the original signal (real part of IFFT)
    col1 = np.real(ifft(fft_result))

    # Calculate magnitude and phase spectra
    magnitudes = np.abs(fft_result)
    phases = np.angle(fft_result)

    # Column 2: IFFT of magnitude spectrum (phase set to 0)
    # Create a complex spectrum with original magnitudes and zero phase
    magnitude_spectrum_only = magnitudes * np.exp(1j * np.zeros(FRAME_COUNT))
    col2 = np.real(
        ifft(magnitude_spectrum_only)
    )  # Take real part as result should be real

    # Column 3: IFFT of phase spectrum (magnitude set to 1)
    # Create a complex spectrum with magnitude 1 and original phases
    phase_spectrum_only = 1 * np.exp(1j * phases)
    col3 = np.real(ifft(phase_spectrum_only))  # Take real part as result should be real

    return col1, col2, col3


def find_intersections(
    col1: np.ndarray, col2: np.ndarray, col3: np.ndarray
) -> list[tuple[int, str]]:
    """Finds intersection points between the three columns.

    Args:
        col1, col2, col3: The three time-series numpy arrays.

    Returns:
        list[tuple[int, str]]: A list of intersection points. Each element is a
            tuple containing the frame index (int) and a string indicating the
            intersecting column pair (str, e.g., 'col1_col2').
    """
    FRAME_COUNT = len(col1)
    intersections = []

    # Find intersections between col1 and col2
    diff12 = col1 - col2
    # Look for sign changes in the difference array
    # The indices where diff12[i] and diff12[i+1] have different signs
    # np.diff returns the difference between consecutive elements
    # We check where diff12[i] * diff12[i+1] is negative or where one is zero and the other is not.
    crossings12_indices = np.where(np.diff(np.sign(diff12)))[0]
    for i in crossings12_indices:
        # The crossing happens between i and i+1, use i as the approximate frame index
        intersections.append((i, "col1_col2"))

    # Find intersections between col1 and col3
    diff13 = col1 - col3
    crossings13_indices = np.where(np.diff(np.sign(diff13)))[0]
    for i in crossings13_indices:
        intersections.append((i, "col1_col3"))

    # Find intersections between col2 and col3
    diff23 = col2 - col3
    crossings23_indices = np.where(np.diff(np.sign(diff23)))[0]
    for i in crossings23_indices:
        intersections.append((i, "col2_col3"))

    # Sort intersections by frame index
    intersections.sort(key=lambda x: x[0])

    return intersections


def create_permutation_fft_columns(
    fft_result: np.ndarray, swap_param: float
) -> Dict[str, np.ndarray]:
    """Creates FFT columns with permutation technology integration.
    
    Args:
        fft_result: The complex result of the FFT.
        swap_param: A float value between 0.0 and 1.0.
        
    Returns:
        Dictionary containing original and permuted FFT columns.
    """
    # Create original columns
    col1, col2, col3 = create_fft_columns(fft_result)
    
    # Create mutator for permutation
    mutator = SineShiftMutator(len(fft_result))
    
    # Apply permutation to each column
    permuted_col1 = mutator.mutate_data(col1, swap_param)
    permuted_col2 = mutator.mutate_data(col2, swap_param)
    permuted_col3 = mutator.mutate_data(col3, swap_param)
    
    return {
        'original': {
            'col1': col1,
            'col2': col2,
            'col3': col3
        },
        'permuted': {
            'col1': permuted_col1,
            'col2': permuted_col2,
            'col3': permuted_col3
        },
        'swap_param': swap_param
    }


def find_permutation_intersections(
    fft_result: np.ndarray, swap_param: float
) -> Dict[str, List[Tuple[int, str]]]:
    """Finds intersection points with permutation technology integration.
    
    Args:
        fft_result: The complex result of the FFT.
        swap_param: A float value between 0.0 and 1.0.
        
    Returns:
        Dictionary containing original and permuted intersection points.
    """
    # Create FFT columns with permutation
    columns_data = create_permutation_fft_columns(fft_result, swap_param)
    
    # Find intersections for original columns
    original_intersections = find_intersections(
        columns_data['original']['col1'],
        columns_data['original']['col2'],
        columns_data['original']['col3']
    )
    
    # Find intersections for permuted columns
    permuted_intersections = find_intersections(
        columns_data['permuted']['col1'],
        columns_data['permuted']['col2'],
        columns_data['permuted']['col3']
    )
    
    return {
        'original_intersections': original_intersections,
        'permuted_intersections': permuted_intersections,
        'intersection_count_original': len(original_intersections),
        'intersection_count_permuted': len(permuted_intersections),
        'swap_param': swap_param
    }


def analyze_intersection_patterns(
    fft_result: np.ndarray, swap_param: float
) -> Dict[str, Any]:
    """Analyzes intersection patterns with permutation technology.
    
    Args:
        fft_result: The complex result of the FFT.
        swap_param: A float value between 0.0 and 1.0.
        
    Returns:
        Dictionary containing intersection pattern analysis.
    """
    # Get intersection data
    intersection_data = find_permutation_intersections(fft_result, swap_param)
    
    # Analyze intersection patterns
    def analyze_intersection_types(intersections):
        type_counts = {}
        for _, intersection_type in intersections:
            type_counts[intersection_type] = type_counts.get(intersection_type, 0) + 1
        return type_counts
    
    original_type_counts = analyze_intersection_types(intersection_data['original_intersections'])
    permuted_type_counts = analyze_intersection_types(intersection_data['permuted_intersections'])
    
    # Calculate intersection density
    signal_length = len(fft_result)
    original_density = len(intersection_data['original_intersections']) / signal_length
    permuted_density = len(intersection_data['permuted_intersections']) / signal_length
    
    # Analyze intersection timing patterns
    def analyze_timing_patterns(intersections):
        if len(intersections) < 2:
            return {'avg_interval': 0, 'std_interval': 0, 'min_interval': 0, 'max_interval': 0}
        
        intervals = []
        for i in range(1, len(intersections)):
            interval = intersections[i][0] - intersections[i-1][0]
            intervals.append(interval)
        
        return {
            'avg_interval': np.mean(intervals),
            'std_interval': np.std(intervals),
            'min_interval': np.min(intervals),
            'max_interval': np.max(intervals)
        }
    
    original_timing = analyze_timing_patterns(intersection_data['original_intersections'])
    permuted_timing = analyze_timing_patterns(intersection_data['permuted_intersections'])
    
    return {
        'intersection_counts': {
            'original': len(intersection_data['original_intersections']),
            'permuted': len(intersection_data['permuted_intersections'])
        },
        'intersection_density': {
            'original': original_density,
            'permuted': permuted_density,
            'density_change': permuted_density - original_density
        },
        'type_distribution': {
            'original': original_type_counts,
            'permuted': permuted_type_counts
        },
        'timing_patterns': {
            'original': original_timing,
            'permuted': permuted_timing
        },
        'swap_param': swap_param
    }


def create_spectral_visualization_data(
    fft_result: np.ndarray, swap_param: float
) -> Dict[str, Any]:
    """Creates comprehensive visualization data using permutation technology.
    
    Args:
        fft_result: The complex result of the FFT.
        swap_param: A float value between 0.0 and 1.0.
        
    Returns:
        Dictionary containing visualization data for plotting.
    """
    # Create FFT columns with permutation
    columns_data = create_permutation_fft_columns(fft_result, swap_param)
    
    # Get intersection data
    intersection_data = find_permutation_intersections(fft_result, swap_param)
    
    # Create time axis
    time_axis = np.arange(len(fft_result))
    
    # Prepare visualization data
    viz_data = {
        'time_axis': time_axis,
        'original_columns': {
            'col1': columns_data['original']['col1'],
            'col2': columns_data['original']['col2'],
            'col3': columns_data['original']['col3']
        },
        'permuted_columns': {
            'col1': columns_data['permuted']['col1'],
            'col2': columns_data['permuted']['col2'],
            'col3': columns_data['permuted']['col3']
        },
        'intersections': {
            'original': intersection_data['original_intersections'],
            'permuted': intersection_data['permuted_intersections']
        },
        'metadata': {
            'swap_param': swap_param,
            'signal_length': len(fft_result),
            'intersection_count_original': intersection_data['intersection_count_original'],
            'intersection_count_permuted': intersection_data['intersection_count_permuted']
        }
    }
    
    return viz_data


def generate_permutation_comparison_report(
    fft_result: np.ndarray, swap_param: float
) -> Dict[str, Any]:
    """Generates a comprehensive comparison report using permutation technology.
    
    Args:
        fft_result: The complex result of the FFT.
        swap_param: A float value between 0.0 and 1.0.
        
    Returns:
        Dictionary containing comprehensive comparison report.
    """
    # Get all analysis data
    columns_data = create_permutation_fft_columns(fft_result, swap_param)
    intersection_data = find_permutation_intersections(fft_result, swap_param)
    pattern_analysis = analyze_intersection_patterns(fft_result, swap_param)
    viz_data = create_spectral_visualization_data(fft_result, swap_param)
    
    # Calculate additional statistics
    def calculate_column_statistics(columns):
        stats = {}
        for col_name, col_data in columns.items():
            stats[col_name] = {
                'mean': np.mean(col_data),
                'std': np.std(col_data),
                'min': np.min(col_data),
                'max': np.max(col_data),
                'rms': np.sqrt(np.mean(col_data**2))
            }
        return stats
    
    original_stats = calculate_column_statistics(columns_data['original'])
    permuted_stats = calculate_column_statistics(columns_data['permuted'])
    
    # Calculate correlation between original and permuted columns
    correlations = {}
    for col_name in ['col1', 'col2', 'col3']:
        original_col = columns_data['original'][col_name]
        permuted_col = columns_data['permuted'][col_name]
        correlation = np.corrcoef(original_col, permuted_col)[0, 1]
        correlations[col_name] = correlation
    
    return {
        'column_statistics': {
            'original': original_stats,
            'permuted': permuted_stats
        },
        'correlations': correlations,
        'intersection_analysis': pattern_analysis,
        'visualization_data': viz_data,
        'metadata': {
            'swap_param': swap_param,
            'signal_length': len(fft_result),
            'analysis_timestamp': np.datetime64('now')
        }
    }
