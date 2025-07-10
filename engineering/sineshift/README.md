# **SineShift Module**
## Advanced Binary Data Scrambling Using Sine Wave-Based Permutation Technology

**Version:** 1.0.0  
**Date:** July 9, 2025  
**Authors:** N Lisowski

---

The SineShift module provides advanced binary data scrambling capabilities using sine wave-based permutation technology. This module can consistently rearrange any binary data in a deterministic, reversible manner based on a continuous swap parameter. Only those with the exact swap parameter can correctly descramble the data, providing a theoretically infinite key space for data obfuscation.

## Features

### Core Functionality
- **Binary Data Scrambling**: Scramble any binary data using continuous swap parameters
- **Deterministic Permutation**: Consistent rearrangement based on sine wave scoring
- **Infinite Key Space**: Theoretically infinite number of possible swap parameters
- **Perfect Restoration**: Only exact swap parameter can correctly descramble data
- **Universal Applicability**: Works with audio, text, numerical, and any binary data
- **FFT Analysis**: Comprehensive frequency domain analysis with permutation technology
- **Spectral Analysis**: Advanced spectral analysis including harmonic content and entropy

### Permutation Technology Integration
The module adapts the permutation technology from `licensee/permutation.py` for universal binary data processing:
- Sine wave-based scoring system for permutation generation
- Bidirectional permutation (scramble/descramble) for any binary data
- Configurable data sizes and parameters
- Comprehensive analysis of permutation effects
- Theoretically infinite key space through continuous swap parameters

## Module Structure

```
sineshift/
├── __init__.py              # Module exports and version info
├── sine_generator.py        # Sine wave generation functions
├── fft_analyzer.py         # FFT analysis with permutation integration
├── mutator.py              # Data mutation using permutation technology
├── plot_data.py            # Data structuring and intersection analysis
├── test_sineshift.py       # Comprehensive test suite
└── README.md               # This documentation
```

## Quick Start

### Basic Usage

```python
from sineshift import SineShiftMutator

# Create a mutator for binary data processing
mutator = SineShiftMutator(frame_count=100000)

# Scramble any binary data
scrambled_data = mutator.mutate_data(binary_data, 0.7)

# Descramble data (only works with exact swap parameter)
restored_data = mutator.unmute_data(scrambled_data, 0.7)

# Different swap parameters create different scrambling patterns
scrambled_data_2 = mutator.mutate_data(binary_data, 0.42)
```

### Advanced Usage

```python
from sineshift import (
    generate_complex_sine_pattern,
    analyze_permutation_fft,
    create_spectral_report
)

# Generate complex sine pattern with harmonics
complex_pattern = generate_complex_sine_pattern(0.6, harmonics=5)

# Analyze FFT with permutation technology
analysis = analyze_permutation_fft(sine_wave, 0.8)

# Create comprehensive spectral report
report = create_spectral_report(sine_wave, 0.9)

# Test different swap parameters for collision analysis
for swap_param in [0.1, 0.2, 0.3, 0.42, 0.5, 0.7, 0.9]:
    scrambled = mutator.mutate_data(data, swap_param)
    # Each swap_param creates a unique scrambling pattern
```

## API Reference

### Sine Wave Generation

#### `generate_sine_wave(swap_param: float) -> np.ndarray`
Generate a basic sine wave influenced by the swap parameter.

**Parameters:**
- `swap_param`: Float controlling frequency scaling (can be any real value)

**Returns:**
- `np.ndarray`: Sine wave with FRAME_COUNT samples

#### `generate_permutation_sine_wave(swap_param: float, frame_count: int = FRAME_COUNT) -> Tuple[np.ndarray, np.ndarray]`
Generate a sine wave and its permutation map using permutation technology.

**Parameters:**
- `swap_param`: Float (can be any real value for infinite key space)
- `frame_count`: Number of frames to generate

**Returns:**
- `Tuple[np.ndarray, np.ndarray]`: Sine wave and permutation map

#### `generate_complex_sine_pattern(swap_param: float, harmonics: int = 3) -> np.ndarray`
Generate a complex sine pattern with multiple harmonics using permutation technology.

**Parameters:**
- `swap_param`: Float (can be any real value for infinite key space)
- `harmonics`: Number of harmonics to add

**Returns:**
- `np.ndarray`: Complex sine wave pattern

### Data Mutation

#### `SineShiftMutator(frame_count: int = 100000)`
Main class for binary data scrambling using permutation technology.

**Methods:**
- `generate_permutation_map(swap_param: float) -> List[int]`: Generate permutation map
- `mutate_data(binary_data: np.ndarray, swap_param: float) -> np.ndarray`: Scramble binary data
- `unmute_data(scrambled_data: np.ndarray, swap_param: float) -> np.ndarray`: Descramble binary data

### FFT Analysis

#### `analyze_fft(sine_wave: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]`
Perform basic FFT analysis on a sine wave.

**Returns:**
- `tuple`: (frequencies, magnitudes, phases)

#### `analyze_permutation_fft(sine_wave: np.ndarray, swap_param: float) -> Dict[str, Any]`
Perform FFT analysis with permutation technology integration.

**Returns:**
- `Dict`: Comprehensive analysis including original and permuted spectra

#### `create_spectral_report(sine_wave: np.ndarray, swap_param: float) -> Dict[str, Any]`
Create a comprehensive spectral analysis report.

**Returns:**
- `Dict`: Complete spectral analysis with statistics and metadata

### Plot Data and Visualization

#### `create_permutation_fft_columns(fft_result: np.ndarray, swap_param: float) -> Dict[str, np.ndarray]`
Create FFT columns with permutation technology integration.

#### `find_permutation_intersections(fft_result: np.ndarray, swap_param: float) -> Dict[str, List[Tuple[int, str]]]`
Find intersection points with permutation technology integration.

#### `generate_permutation_comparison_report(fft_result: np.ndarray, swap_param: float) -> Dict[str, Any]`
Generate a comprehensive comparison report using permutation technology.

## Permutation Technology

The module uses a sophisticated permutation algorithm based on sine wave scoring:

1. **Scoring System**: Each data element is scored using `sin(swap_param * 100.0 + i * 0.2) * 1000.0 + i`
2. **Permutation Map**: Data elements are reordered based on their scores
3. **Bidirectional**: The same algorithm can scramble and descramble any binary data
4. **Infinite Key Space**: Continuous swap parameters provide theoretically infinite keys
5. **Deterministic**: Same swap parameter always produces identical scrambling pattern

### Key Features:
- **Deterministic**: Same swap_param always produces the same permutation
- **Reversible**: Permutation can be undone using the inverse map
- **Universal**: Works with any binary data type (audio, text, numerical, etc.)
- **Infinite Keys**: Theoretically infinite number of possible swap parameters
- **Collision Research**: Potential for frequency collisions between different keys (unresearched)
- **Analysis-Ready**: Includes comprehensive analysis tools

## Testing

Run the comprehensive test suite:

```bash
cd src/sineshift
python test_sineshift.py
```

The test suite covers:
- Basic sine wave generation
- Permutation technology integration
- FFT analysis with permutation
- Complex pattern generation
- Spectral report generation
- Intersection analysis
- Comparison report generation

## Dependencies

- `numpy`: For numerical operations and FFT
- `matplotlib`: For plotting (optional, used in tests)

## Integration with EPStudio

The SineShift module is designed to integrate with the EPStudio data processing pipeline:

1. **Binary Data Processing**: Use mutators for any binary data transformation
2. **Data Obfuscation**: Scramble data for secure storage and transmission
3. **Analysis**: Generate comprehensive spectral and permutation reports
4. **Research**: Advanced permutation technology for data security research
5. **Key Management**: Manage infinite key space for data access control

## Version History

- **1.0.0**: Initial implementation with permutation technology integration
  - Complete binary data scrambling suite
  - FFT analysis with permutation integration
  - Universal data mutation capabilities
  - Comprehensive testing framework
  - Infinite key space implementation

## Research and Documentation

### Whitepaper
For in-depth technical details, security analysis, and ongoing research, refer to:
- `sineshift_whitepaper.md` — Full technical whitepaper

### Research Areas
- **Continuous-Seeded RNG**: Exploration of lightweight, continuously-seeded random number generators for permutation and entropy applications.
- **Entropy Generation**: Methods for extracting or amplifying entropy from continuous parameter spaces, enabling robust data scrambling and unpredictability.
- **True Matrix Grid**: Investigation into multi-dimensional ("true matrix") grid-based permutation and entropy mapping, extending beyond 1D data streams.
- **Collision Analysis**: Study of potential frequency or permutation collisions between different continuous seeds.
- **Key Space Analysis**: Characterization of the infinite, continuous key space and its implications for security and uniqueness.
- **Security Research**: Analysis of attack surfaces, resistance to brute-force and statistical attacks, and mitigation strategies.
- **Performance Optimization**: Enhancements for algorithmic speed, memory efficiency, and hardware acceleration.