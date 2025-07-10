# **White Paper: Instamaster**
## A Specification for the Signal-Centric Automated Mastering Pipeline

**Version:** 1.0.0  
**Date:** July 9, 2025  
**Authors:** N Lisowski

---

## **Abstract**
This document provides a detailed technical specification for Instamaster, a programmatic audio processing system designed to perform a complete, sequential mastering chain on a digital audio track. The system architecture is defined by the `MasteringPipeline` class, which encapsulates a series of digital signal processing (DSP) modules. These modules include corrective equalization, multiband dynamics compression, harmonic enhancement, stereo imaging, and brickwall limiting. Instamaster operates with a fixed set of parameters derived from common mastering practices, providing a consistent and repeatable process. This paper outlines the workflow, the underlying algorithms of each processing stage, and the operational parameters, concluding with potential avenues for future development.

***

## **1.0 Introduction**
Audio mastering is the final step in post-production, preparing a mixed audio track for distribution. It is a critical process that involves subtle adjustments to optimize playback quality across all systems and formats. Traditionally a highly skilled, manual craft, the advent of sophisticated DSP allows for the automation of this process.

### **1.1 Purpose and Scope**
The purpose of this document is to specify the design and functionality of Instamaster's `MasteringPipeline`. It is intended for developers, audio engineers, and stakeholders to understand the system's internal workings. The scope is limited to the functionality implemented within the provided Python code, which represents a single, complete mastering chain.

### **1.2 System Philosophy**
Instamaster is designed as a deterministic, sequential process. It applies a series of well-established mastering techniques in a predefined order. While it accepts a reference track for comparison purposes, the core processing parameters are currently fixed and do not adapt based on input audio analysis. This ensures predictable results and serves as a foundational model for a general-purpose automated mastering solution.

***

## **2.0 System Architecture and Workflow**
The system is built around the `MasteringPipeline` class, which manages the audio data and orchestrates the application of DSP modules.

### **2.1 Core Component**
The `MasteringPipeline` class holds the state of the audio data (`self.audio`), its sample rate (`self.sr`), and a log of all operations performed (`self.notes`). It exposes a primary method, `run_mastering_pipeline`, which executes the entire workflow.

### **2.2 Processing Workflow**
The mastering process in Instamaster follows a strict, sequential order to ensure logical signal flow:

1.  **Audio Ingestion & Preparation:** Load main and optional reference audio from byte streams. Convert mono sources to dual-mono to ensure stereo compatibility. Analyze initial peak headroom.
2.  **Critical Listening (Simulated):** A placeholder step to acknowledge the importance of manual listening in a real-world scenario.
3.  **Corrective & Enhancement Equalization:** Apply a multi-stage parametric EQ to shape the tonal balance.
4.  **Dynamics Processing (Multiband Compression):** Control the dynamic range across three frequency bands (Low, Mid, High).
5.  **Sonic Enhancement:** Introduce subtle harmonic saturation and adjust the stereo width.
6.  **Loudness Maximization (Brickwall Limiting):** Increase the overall loudness to commercial levels while preventing clipping.
7.  **Finalization & Export:** Apply dither for bit-depth reduction and export the final track to a `.wav` file.

***

## **3.0 Detailed Specification of Processing Modules**
Each step in the workflow corresponds to a distinct DSP module with specific algorithms and parameters.

### **3.1 Module 1: Audio Ingestion and Preparation**
This module handles the initial loading and validation of the audio data.
* **Input:** Audio data is loaded from a byte stream (e.g., from an uploaded file).
* **Format:** Instamaster uses `soundfile` to support standard formats like WAV and FLAC, internally converting the data to 32-bit floating-point format.
* **Channel Processing:** Instamaster is designed for stereo signals. If a mono file is loaded, it is converted to a dual-mono (two identical channels) stereo file to ensure compatibility with stereo-dependent modules like the widener. The internal data representation is `(number_of_channels, number_of_samples)`.
* **Initial Analysis:** The initial peak level of the input track is measured in dBFS (decibels relative to full scale). A warning is logged if the peak exceeds -3.0 dBFS, as this indicates insufficient headroom for mastering.

### **3.2 Module 2: Corrective and Enhancement Equalization**
This module utilizes a series of cascaded Infinite Impulse Response (IIR) biquad filters to apply parametric equalization. Each filter stage is processed sequentially using `scipy.signal.lfilter`. The transfer function for a biquad filter is given by:

$$H(z) = \frac{b_0 + b_1z^{-1} + b_2z^{-2}}{a_0 + a_1z^{-1} + a_2z^{-2}}$$

Instamaster implements the following fixed EQ chain:
| Filter Type | Frequency (Hz) | Q-Factor | Gain (dB) | Purpose |
| :--- | :--- | :--- | :--- | :--- |
| **High-Shelf** | 8000 | 0.707 | +1.0 | Adds "air" and brightness. |
| **Peaking** | 3000 | 1.5 | +0.7 | Increases presence and clarity. |
| **Peaking** | 7000 | 3.0 | -0.5 | Tames potential harshness. |
| **Peaking** | 250 | 1.8 | -0.8 | Reduces low-mid "mud." |
| **Low-Shelf** | 100 | 0.707 | +1.2 | Boosts low-end weight. |

*Note: The implementation contains a placeholder for a lowshelf filter but uses biquad calculations for peaking and highshelf types.*

### **3.3 Module 3: Dynamics Processing (Multiband Compression)**
The compressor module is designed to control dynamics independently in three frequency bands.
* **Crossover Network:** The audio signal is split into three bands using 4th-order Butterworth IIR filters, creating a Linkwitz-Riley-style crossover network.
    * **Low Band:** < 150 Hz
    * **Mid Band:** 150 Hz - 2000 Hz
    * **High Band:** > 2000 Hz
* **Compressor Algorithm:** Each band is processed by a simple feed-forward digital compressor with the following logic:
    1.  A gain envelope is calculated sample-by-sample.
    2.  If the input signal's absolute level exceeds the threshold, a target gain reduction is calculated based on the ratio.
    3.  The `current_gain` smoothly transitions towards the `target_gain_reduction` based on separate attack and release coefficients, which are derived from their respective times in milliseconds.
* **Fixed Parameters:**
| Band | Threshold (dBFS) | Ratio | Attack (ms) | Release (ms) | Makeup Gain (dB) |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Low** | -20.0 | 2.5 : 1 | 10.0 | 150.0 | +1.0 |
| **Mid** | -18.0 | 3.0 : 1 | 5.0 | 100.0 | +0.5 |
| **High** | -15.0 | 2.0 : 1 | 2.0 | 80.0 | +0.0 |

### **3.4 Module 4: Sonic Enhancement**
This module applies two distinct effects: tape saturation and stereo widening.

#### **3.4.1 Tape Saturation**
A subtle harmonic distortion is introduced to emulate the sound of analog tape.
* **Algorithm:** The signal is passed through a hyperbolic tangent (`tanh`) waveshaping function. This function soft-clips the waveform, adding odd harmonics that can be perceived as warmth and fullness.
* **Parameters:** A `drive` parameter controls the intensity, and the final signal is a dry/wet mix. The effect is intentionally subtle, with a fixed `saturation_amount` of 3%.

#### **3.4.2 Stereo Imaging**
The stereo width is manipulated using Mid/Side (M/S) processing.
* **M/S Decomposition:** The Left/Right signal is converted to Mid ($M = 0.5 \times (L+R)$) and Side ($S = 0.5 \times (L-R)$).
* **Widening:** The Side channel's gain is increased by a `widening_factor` of 1.10 (a 10% increase), enhancing the perceived stereo width. The signal is then converted back to L/R.
* **Mono Bass Preservation:** To avoid phase issues and maintain a solid low-end foundation, frequencies below 120 Hz are made mono. This is achieved by filtering the Mid signal with a 2nd-order low-pass filter and filtering the widened L/R signals with a 2nd-order high-pass filter at 120 Hz. The final output combines the mono low-end with the stereo high-end.

### **3.5 Module 5: Loudness Maximization (Brickwall Limiting)**
The final dynamics processing stage is a brickwall limiter, designed to increase loudness without allowing the signal to exceed a predefined ceiling.
* **Algorithm:** The limiter functions similarly to the compressor but with an infinite ratio. It calculates a gain envelope to ensure the output signal never exceeds the ceiling.
* **Look-ahead (Simulated):** The implementation is a sample-by-sample processor without a look-ahead buffer. The attack and release parameters are crucial for controlling transients and minimizing distortion.
* **Parameters:**
    * **Ceiling:** -0.3 dBFS. This is the maximum permissible peak level for the output file.
    * **Attack:** 1.5 ms.
    * **Release:** 75.0 ms.

### **3.6 Module 6: Finalization and Export**
This module prepares the final audio for delivery.
* **Bit-Depth Reduction:** The internal 32-bit float signal must be converted to the target integer format (e.g., 24-bit or 16-bit). This quantization process introduces errors that are perceived as noise.
* **Dithering:** To mitigate quantization distortion, dither is applied. Dither is a low-level noise that decorrelates the quantization error from the signal, replacing harmonic distortion with a less perceptible, constant noise floor.
    * **Algorithm:** Instamaster implements a basic Triangular Probability Density Function (TPDF) dither by adding two samples of uniformly distributed random noise.
    * **Noise Shaping (Conceptual):** Options for "POW-r" dither are simulated by filtering the dither noise with high-pass filters (`butter`) before it is added to the signal. This pushes the noise energy into higher, less audible frequency ranges.
        * **POW-r 2:** Moderate shaping with a 2nd-order filter.
        * **POW-r 3:** Aggressive shaping with a 4th-order filter.
* **Export:** The final processed audio is written to a `.wav` file using the specified bit depth (e.g., `PCM_24`).

***

## **4.0 Conclusion and Future Work**
Instamaster provides a robust and well-defined framework for automated audio mastering. By chaining together fundamental DSP modules, it offers a complete, one-step solution for enhancing audio tracks. The fixed-parameter approach ensures consistency, though it lacks the adaptability of more advanced systems.

Future work could focus on several key areas:
* **Adaptive Processing:** Implement logic to analyze the input audio (and reference track, if provided) to dynamically adjust EQ, compression, and other parameters. This could involve machine learning models trained on professionally mastered tracks.
* **Advanced DSP:** Incorporate more sophisticated algorithms, such as linear phase EQs, dynamic EQs, and true look-ahead limiters for improved transparency.
* **User Configuration:** Expose internal module parameters (e.g., EQ frequencies, compressor ratios) through a configuration interface to give users more granular control.
* **Modular Architecture:** Refactor Instamaster to allow users to re-order or disable specific modules, offering greater flexibility.