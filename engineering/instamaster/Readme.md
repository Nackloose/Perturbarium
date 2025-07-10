# **InstaMaster**
## Automated Audio Mastering Pipeline for Professional-Quality Results

**Version:** 1.0.0  
**Date:** July 9, 2025  
**Authors:** N Lisowski

---

This module provides a fully self-contained, step-by-step audio mastering pipeline in Python, designed for both local and cloud (e.g., Google Colab) environments. It is intended for musicians, producers, and developers who want to automate the mastering process for stereo audio tracks, with optional reference track support.

---

## Features

- **Stereo Audio Support**: Handles mono-to-stereo conversion automatically.
- **Reference Track Comparison**: Optionally load a reference track for level and tonal comparison.
- **Stepwise Mastering Pipeline**:
  1. **Track Preparation**: Checks headroom and logs initial levels.
  2. **Critical Listening (Simulated)**: Prompts for manual note-taking (no interactive input).
  3. **Master EQ**: Multi-band parametric EQ using IIR biquad filters.
  4. **Master Compression**: Multi-band compression with configurable parameters.
  5. **Enhancement**: Subtle tape saturation and stereo widening with mono bass preservation.
  6. **Limiting**: Brickwall limiter with configurable attack/release and ceiling.
  7. **Export**: Output to WAV with selectable bit depth and conceptual dithering (POW-r 1/2/3).

- **Logging**: Each step logs actions and warnings for transparency and troubleshooting.
- **Colab-Friendly**: Byte stream loading and export, with print statements for user guidance.

---

## Installation

### Prerequisites

```bash
pip install numpy scipy librosa soundfile
```

### Quick Start (Recommended)

```bash
# Clone the repository
git clone <repository-url>
cd engineering/instamaster

# Run the auto-setup script
./run.sh input.wav
```

The `run.sh` script will automatically:
- Check for Python 3 and pip
- Create a virtual environment
- Install all required dependencies
- Run the mastering pipeline

### Manual Installation

```bash
git clone <repository-url>
cd engineering/instamaster
python instamaster.py
```

---

## Usage

### Command Line Interface (Recommended)

The easiest way to use InstaMaster is through the command line:

```bash
# Basic mastering
./run.sh input.wav

# Specify output file
./run.sh input.wav -o mastered.wav

# With reference track
./run.sh input.wav -r reference.wav

# 16-bit output
./run.sh input.wav --bit-depth 16

# Test mode
./run.sh --test
```

### Python API

### 1. Import and Initialize

```python
# Import the InstaMaster class directly from the file
from instamaster import InstaMaster

# Initialize the mastering pipeline
master = InstaMaster()
```

### 2. Load Audio Files

```python
# Load your mix (supports WAV, MP3, FLAC, etc.)
master.load_mix("path/to/your/mix.wav")

# Optionally load a reference track
master.load_reference("path/to/reference.wav")
```

### 3. Configure Settings (Optional)

```python
# Customize mastering parameters
master.configure(
    target_lufs=-14.0,          # Target loudness
    true_peak_limit=-1.0,       # True peak limit in dB
    eq_enabled=True,            # Enable/disable EQ
    compression_enabled=True,    # Enable/disable compression
    enhancement_enabled=True,    # Enable/disable enhancement
    limiting_enabled=True        # Enable/disable limiting
)
```

### 4. Run the Mastering Pipeline

```python
# Execute the complete mastering process
mastered_audio = master.master()
```

### 5. Export Results

```python
# Export the mastered audio
master.export("path/to/output/mastered.wav", bit_depth=24)

# Get analysis results
analysis = master.get_analysis()
print(f"Final LUFS: {analysis['final_lufs']}")
print(f"True Peak: {analysis['true_peak']}")
```

---

## Run Script Options

The `run.sh` script provides several options:

```bash
./run.sh --help          # Show help and usage
./run.sh --clean         # Remove virtual environment and reinstall
./run.sh --test          # Run in test mode
./run.sh input.wav       # Process an audio file
```

### Script Features

- **Auto Environment Setup**: Automatically creates and manages a Python virtual environment
- **Dependency Management**: Installs all required packages from `requirements.txt`
- **Error Handling**: Provides clear error messages and status updates
- **Cross-Platform**: Works on Linux, macOS, and Windows (with WSL)

---

## Advanced Usage

### Custom EQ Settings

```python
# Define custom EQ bands
eq_settings = {
    'low_shelf': {'freq': 80, 'gain': 2.0, 'q': 0.7},
    'mid_peak': {'freq': 2500, 'gain': -1.5, 'q': 1.0},
    'high_shelf': {'freq': 8000, 'gain': 1.0, 'q': 0.7}
}

master.set_eq_settings(eq_settings)
```

### Custom Compression Settings

```python
# Configure multi-band compression
comp_settings = {
    'low_band': {'threshold': -20, 'ratio': 2.0, 'attack': 0.005, 'release': 0.1},
    'mid_band': {'threshold': -18, 'ratio': 1.5, 'attack': 0.010, 'release': 0.05},
    'high_band': {'threshold': -22, 'ratio': 1.8, 'attack': 0.008, 'release': 0.08}
}

master.set_compression_settings(comp_settings)
```

### Batch Processing

```python
import os

# Process multiple files
input_dir = "path/to/mixes/"
output_dir = "path/to/mastered/"

for file in os.listdir(input_dir):
    if file.endswith(('.wav', '.mp3', '.flac')):
        master.load_mix(os.path.join(input_dir, file))
        mastered = master.master()
        output_path = os.path.join(output_dir, f"mastered_{file}")
        master.export(output_path)
```

---

## API Reference

### InstaMaster Class

#### Methods

- `load_mix(file_path)`: Load the mix to be mastered
- `load_reference(file_path)`: Load a reference track for comparison
- `configure(**kwargs)`: Configure mastering parameters
- `master()`: Execute the complete mastering pipeline
- `export(file_path, bit_depth=24)`: Export the mastered audio
- `get_analysis()`: Get detailed analysis of the mastered audio
- `set_eq_settings(settings)`: Configure custom EQ settings
- `set_compression_settings(settings)`: Configure custom compression settings

#### Configuration Parameters

- `target_lufs`: Target loudness in LUFS (default: -14.0)
- `true_peak_limit`: True peak limit in dB (default: -1.0)
- `eq_enabled`: Enable/disable EQ processing (default: True)
- `compression_enabled`: Enable/disable compression (default: True)
- `enhancement_enabled`: Enable/disable enhancement (default: True)
- `limiting_enabled`: Enable/disable limiting (default: True)

---

## Google Colab Integration

InstaMaster is designed to work seamlessly in Google Colab environments:

```python
# Upload your audio files to Colab
from google.colab import files
uploaded = files.upload()

# Load and process
from instamaster import InstaMaster
master = InstaMaster()
master.load_mix(list(uploaded.keys())[0])
mastered_audio = master.master()

# Download the result
master.export("mastered_output.wav")
files.download("mastered_output.wav")
```

---

## Troubleshooting

### Common Issues

1. **Audio Quality Issues**
   - Ensure input files are high quality (24-bit WAV recommended)
   - Check that input levels are not clipping
   - Verify sample rate consistency

2. **Performance Issues**
   - For large files, consider processing in chunks
   - Use appropriate bit depth settings for your needs

3. **Reference Track Issues**
   - Ensure reference track is in the same key/tempo range
   - Reference track should be professionally mastered

### Logging

InstaMaster provides detailed logging for troubleshooting:

```python
import logging
logging.basicConfig(level=logging.INFO)
```

---

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

---

## Acknowledgments

- Built with NumPy, SciPy, and Librosa
- Inspired by professional mastering workflows
- Designed for accessibility and ease of use

---

## Version History

- **v1.0.0**: Initial release with basic mastering pipeline
- **v1.1.0**: Added reference track support
- **v1.2.0**: Enhanced EQ and compression algorithms
- **v1.3.0**: Added Google Colab integration features
- **v1.4.0**: Updated to standalone instamaster.py file structure

