# **White Paper: SineShift**
## A Framework for Deterministic Data Permutation via Sine-Wave-Based Scrambling

**Version:** 1.0.0  
**Date: July 9, 2025**
**Authors:** N Lisowski

---

### **Abstract**

This paper presents SineShift, a novel method for binary data scrambling that employs a sine-wave-based permutation algorithm. The technique deterministically and reversibly permutes any binary data sequence based on a continuous-valued key parameter. This approach provides a theoretically infinite key space, creating a robust mechanism for data obfuscation where the original data can only be recovered by users possessing the exact key. This white paper details the theoretical foundations of the SineShift algorithm, its reference architecture, a comprehensive security analysis, and directions for future research.

### **1. Introduction**

#### **1.1 The Problem Domain**

While traditional cryptographic algorithms provide high levels of security, they often involve significant computational overhead and rely on discrete mathematical problems that may be subject to future cryptanalytic advances. There exists a need for complementary data protection methods, particularly in the domain of obfuscation, that are characterized by the following properties:

* **Deterministic and Reversible:** The transformation must be repeatable and perfectly invertible.
* **Computationally Efficient:** The algorithm should have a low time and space complexity, suitable for real-time applications.
* **Continuous Parameter Space:** The keying mechanism should not be limited to a finite set, making exhaustive searches impractical.
* **Data Agnostic:** The method should be applicable to arbitrary binary data, regardless of its type or size.

#### **1.2 Proposed Solution: SineShift**

SineShift is a permutation-based scrambling framework designed to meet these requirements. It utilizes a sine function to generate a unique permutation map for a given data block, seeded by a continuous floating-point parameter. This parameter acts as a secret key; without it, the scrambled data remains unintelligible. SineShift is positioned not as a replacement for encryption but as a highly efficient and flexible tool for data obfuscation and access control in various applications.

### **2. Theoretical Foundations**

#### **2.1 The Sine-Wave Permutation Algorithm**

The core of SineShift is the generation of a permutation map derived from a scoring function applied to the index of each element in a data array. For a data block of size $N$, the score for the element at index $i$ (where $i \in \{0, 1, ..., N-1\}$) is calculated as:

$$\text{score}(i) = A \cdot \sin(k \cdot \gamma + i \cdot \omega) + i$$

Where:
* $i$ is the zero-based index of the data element.
* $k$ is the **key parameter**, a continuous real number that seeds the permutation.
* $\omega$ is a **frequency factor** that controls the periodicity of the sine wave across the data indices.
* $\gamma$ is a **phase shift factor** that adjusts the starting point of the sine function.
* $A$ is an **amplitude factor** that scales the influence of the sine function relative to the index.

The linear addition of the index $i$ is crucial for ensuring that, in the vast majority of cases, no two elements are assigned the same score, which is essential for generating a valid permutation.

#### **2.2 Permutation Generation Process**

The scrambling and descrambling processes are based on a four-phase procedure:

1.  **Score Generation:** For a data block of size $N$ and a given key parameter $k$, a score is calculated for each index $i$ from $0$ to $N-1$.
2.  **Index Sorting:** An array of indices $[0, 1, ..., N-1]$ is sorted based on their corresponding scores. The resulting sorted array of indices forms the **permutation map**.
3.  **Permutation Map Construction:** The permutation map, $P$, is an array where $P[i]$ contains the new position for the element originally at index $i$. An inverse map, $P^{-1}$, can be trivially constructed for reversal.
4.  **Data Transformation:** The data is rearranged according to the permutation map. To descramble the data, the inverse map is applied.

#### **2.3 Mathematical Properties**

* **Determinism:** For a fixed data length $N$ and a given key parameter $k$, the scoring and sorting process will always produce the exact same permutation map.
* **Reversibility:** As the permutation map is a one-to-one mapping of indices, a unique inverse map always exists, guaranteeing perfect data restoration.
* **Continuous Parameter Space:** The key parameter $k$ is a real number, offering a theoretically infinite key space. The practical key space is bounded only by the precision of floating-point number representation (e.g., IEEE 754 double-precision).

#### **2.4 Three-Column Signal Processing Architecture**

SineShift implements an advanced signal processing architecture that decomposes signals into three distinct analytical columns, each representing different aspects of the signal's spectral characteristics. This approach provides comprehensive analysis capabilities and enables sophisticated permutation-based transformations.

##### **2.4.1 Column Decomposition Process**

The three-column architecture operates on the Fast Fourier Transform (FFT) of the input signal, decomposing it into three distinct time-domain representations:

**Column 1: Original Signal Reconstruction**
* **Definition:** $\text{col}_1 = \Re\{\text{IFFT}(\text{FFT}(\text{signal}))\}$
* **Purpose:** Represents the original signal reconstructed from its FFT
* **Characteristics:** Identical to the input signal (within numerical precision)
* **Mathematical Basis:** Inverse FFT of the complete complex spectrum

**Column 2: Magnitude-Only Reconstruction**
* **Definition:** $\text{col}_2 = \Re\{\text{IFFT}(|\text{FFT}(\text{signal})| \cdot e^{j \cdot 0})\}$
* **Purpose:** Represents the signal reconstructed using only magnitude information
* **Characteristics:** Preserves amplitude envelope but loses phase relationships
* **Mathematical Basis:** Inverse FFT of magnitude spectrum with zero phase

**Column 3: Phase-Only Reconstruction**
* **Definition:** $\text{col}_3 = \Re\{\text{IFFT}(1 \cdot e^{j \cdot \angle(\text{FFT}(\text{signal}))})\}$
* **Purpose:** Represents the signal reconstructed using only phase information
* **Characteristics:** Preserves timing relationships but loses amplitude information
* **Mathematical Basis:** Inverse FFT of unit magnitude with original phases

##### **2.4.2 Mathematical Formulation**

For a signal $x[n]$ with FFT $X[k] = |X[k]| \cdot e^{j \phi[k]}$:

$$\begin{align}
\text{col}_1[n] &= \Re\left\{\frac{1}{N} \sum_{k=0}^{N-1} X[k] \cdot e^{j \frac{2\pi kn}{N}}\right\} \\
\text{col}_2[n] &= \Re\left\{\frac{1}{N} \sum_{k=0}^{N-1} |X[k]| \cdot e^{j \frac{2\pi kn}{N}}\right\} \\
\text{col}_3[n] &= \Re\left\{\frac{1}{N} \sum_{k=0}^{N-1} e^{j \phi[k]} \cdot e^{j \frac{2\pi kn}{N}}\right\}
\end{align}$$

Where:
* $N$ is the signal length
* $|X[k]|$ is the magnitude spectrum
* $\phi[k]$ is the phase spectrum
* $\Re\{\cdot\}$ denotes the real part

##### **2.4.3 Intersection Analysis**

The three-column architecture enables sophisticated intersection analysis, identifying points where different spectral representations cross:

**Intersection Detection Algorithm:**
1. **Difference Calculation:** Compute pairwise differences between columns
   * $\Delta_{12}[n] = \text{col}_1[n] - \text{col}_2[n]$
   * $\Delta_{13}[n] = \text{col}_1[n] - \text{col}_3[n]$
   * $\Delta_{23}[n] = \text{col}_2[n] - \text{col}_3[n]$

2. **Zero-Crossing Detection:** Find indices where sign changes occur
   * $\text{intersection}_{ij} = \{n : \text{sign}(\Delta_{ij}[n]) \neq \text{sign}(\Delta_{ij}[n+1])\}$

3. **Classification:** Categorize intersections by column pairs
   * Type 1: $\text{col}_1 \leftrightarrow \text{col}_2$ intersections
   * Type 2: $\text{col}_1 \leftrightarrow \text{col}_3$ intersections  
   * Type 3: $\text{col}_2 \leftrightarrow \text{col}_3$ intersections

##### **2.4.4 Permutation Integration**

The three-column architecture integrates seamlessly with the permutation technology:

**Permuted Column Generation:**
* **Original Columns:** $\{\text{col}_1, \text{col}_2, \text{col}_3\}$
* **Permuted Columns:** $\{P(\text{col}_1), P(\text{col}_2), P(\text{col}_3)\}$
* **Permutation Map:** $P$ generated using the sine-wave scoring algorithm

**Analysis Capabilities:**
* **Spectral Correlation:** Measure correlation between original and permuted columns
* **Intersection Pattern Analysis:** Compare intersection distributions before/after permutation
* **Statistical Characterization:** Analyze changes in column statistics under permutation
* **Timing Pattern Analysis:** Examine intersection timing patterns and intervals

##### **2.4.5 Advanced Analysis Features**

**Intersection Density Analysis:**
* **Definition:** $\rho = \frac{\text{number of intersections}}{\text{signal length}}$
* **Purpose:** Quantify the complexity of spectral relationships
* **Permutation Effect:** Measure how permutation alters intersection density

**Timing Pattern Analysis:**
* **Interval Statistics:** Mean, standard deviation, min/max intervals between intersections
* **Pattern Classification:** Identify periodic, random, or clustered intersection patterns
* **Permutation Impact:** Analyze how permutation affects timing characteristics

**Correlation Analysis:**
* **Column Correlations:** Measure linear correlation between original and permuted columns
* **Cross-Column Correlations:** Analyze relationships between different column pairs
* **Permutation Strength:** Quantify the degree of transformation achieved

##### **2.4.6 Implementation Architecture**

The three-column processing is implemented through a modular architecture:

**Core Functions:**
* `create_fft_columns()`: Generates the three basic columns from FFT
* `find_intersections()`: Detects intersection points between columns
* `create_permutation_fft_columns()`: Applies permutation to all columns
* `find_permutation_intersections()`: Analyzes intersections with permutation
* `analyze_intersection_patterns()`: Comprehensive pattern analysis
* `generate_permutation_comparison_report()`: Complete analysis report

**Data Flow:**
1. **Input Signal** → **FFT** → **Three Columns**
2. **Columns** → **Intersection Detection** → **Pattern Analysis**
3. **Columns** → **Permutation** → **Permuted Columns**
4. **Permuted Columns** → **Intersection Detection** → **Comparison Analysis**
5. **All Data** → **Statistical Analysis** → **Comprehensive Report**

This architecture provides a powerful framework for understanding how permutation technology affects different aspects of signal characteristics, enabling sophisticated analysis of the transformation's impact on spectral properties, timing relationships, and statistical distributions.

### **3. Implementation Architecture**

#### **3.1 Core Components**

A reference implementation of SineShift is encapsulated within a logical `SineShiftMutator` module, which exposes three primary functions:
* `generate_permutation_map(key, size)`: Creates the forward and inverse permutation maps for a given key and data size.
* `mutate_data(data, key)`: Scrambles the input data using the specified key.
* `unmute_data(data, key)`: Restores the original data using the same key.

The architecture is designed to be data-agnostic, capable of processing audio frames, byte arrays, character arrays, and numerical arrays with equal efficacy.

#### **3.2 Key Architectural Features**

* **Bidirectional Operation:** The system is inherently symmetrical, with mutation (scrambling) and unmutation (descrambling) being inverse operations controlled by the same key.
* **Configurable Parameters:** The sine function's coefficients (frequency, amplitude, phase) are configurable, allowing the permutation characteristics to be tuned for different applications.
* **Robust Error Handling:** The implementation includes validation for input parameters (e.g., key bounds) and data integrity checks to ensure successful restoration.

### **4. Security Analysis**

It is critical to state that **SineShift is a data obfuscation tool, not a cryptographically secure encryption algorithm.** It is vulnerable to attacks that traditional ciphers are designed to resist.

#### **4.1 Key Space and Collision Analysis**

* **Key Space Cardinality:** While theoretically infinite, the practical key space is limited by floating-point precision. An IEEE 754 double-precision float offers approximately $2^{64}$ possible values, providing substantial resistance to brute-force attacks that attempt to iterate through all possible keys.
* **The Collision Problem:** A significant area of research is the analysis of key collisions, which occur when two distinct key parameters, $k_1$ and $k_2$, produce the identical permutation map for a given data size $N$. The periodic nature of the sine function makes such collisions theoretically possible. The probability of collisions must be analyzed to determine the *effective* key space.

#### **4.2 Principal Attack Vectors**

* **Brute-Force Attack:** Impractical due to the vastness of the floating-point key space. However, if an attacker has a reasonable assumption about the *range* of the key, the search space could be reduced.
* **Known-Plaintext Attack:** This is the most significant vulnerability. If an attacker possesses a sample of original data and its corresponding scrambled version, they can trivially derive the permutation map for that data size. While this does not reveal the key parameter $k$, it completely compromises all other data scrambled with the same map.
* **Statistical Analysis:** The permutation process rearranges data but does not alter its statistical properties. For example, the histogram (the frequency of each byte value) of the scrambled data is identical to that of the original data. This makes it vulnerable to frequency analysis, a classic cryptanalytic technique.

#### **4.3 Summary of Security Profile**

* **Advantages:**
    * **Deterministic and Reversible:** Guarantees data integrity upon reversal.
    * **Efficient:** The primary computational cost is sorting, resulting in an efficient $O(N \log N)$ time complexity.
    * **Flexible:** Applicable to any form of binary data.
* **Limitations:**
    * **Not Cryptographically Secure:** Does not provide semantic security and is vulnerable to known-plaintext attacks.
    * **Pattern Preservation:** Preserves statistical distributions of the source data.
    * **Collision Potential:** The theoretical possibility of key collisions reduces the effective key space.

### **5. Use Cases and Applications**

SineShift is suitable for applications where high-performance obfuscation is required, but the threat model does not include sophisticated cryptanalytic attacks.

* **Real-time Media Obfuscation:** Scrambling audio or video frames for proprietary transmission, preventing trivial interception and playback.
* **Static Data Obfuscation:** Protecting non-critical files on storage media or in backups, where access is controlled by possession of the key.
* **Digital Watermarking:** Embedding hidden information by applying subtle permutations to data in a way that is imperceptible but algorithmically detectable.
* **Layered Security:** Using SineShift as an initial, computationally inexpensive scrambling layer before applying traditional encryption, adding complexity for potential attackers.

### **6. Future Research and Development**

Further research is required to fully characterize the properties of SineShift and enhance its capabilities.

#### **6.1 Security and Collision Analysis**
* **Empirical Collision Studies:** Conduct large-scale computational experiments to measure the frequency of key collisions across various data sizes and parameter settings.
* **Formal Collision Modeling:** Develop a mathematical model to predict collision probability based on the algorithm's parameters.
* **Formal Security Proofs:** Analyze the algorithm against established cryptographic principles to formally define its security boundaries.

#### **6.2 Algorithmic Enhancements**
* **Advanced Scoring Functions:** Investigate the use of multi-frequency sine waves, other periodic functions (e.g., tangent, sawtooth), or non-linear transformations to improve permutation complexity and reduce collisions.
* **Multi-Dimensional Permutations:** Extend the algorithm to operate on multi-dimensional data (e.g., images, volumetric data) by applying permutations along multiple axes.
* **Data-Dependent Permutations:** Explore techniques where the permutation map is influenced by the content of the data itself, mitigating the risk of known-plaintext attacks.

#### **6.3 Performance Optimization**
* **Hardware Acceleration:** Develop GPU-based or FPGA implementations to leverage massive parallelism for scoring and sorting operations on very large datasets.
* **Algorithmic Improvements:** Investigate faster sorting algorithms or alternative permutation generation schemes that may offer better performance characteristics.

### **7. Conclusion**

SineShift offers a novel and efficient framework for deterministic data scrambling. Its core strength lies in its simplicity, speed, and the use of a continuous parameter space that provides a theoretically infinite key space for obfuscation. While it is not a substitute for formal encryption, it serves as a valuable tool for a wide range of applications requiring high-performance, key-dependent data transformation.

The primary contributions of this work are the introduction of a sine-wave-based permutation algorithm, a framework for its application, and the identification of its security characteristics. The technology opens new avenues for research into data obfuscation, the properties of continuous key spaces, and specialized applications in signal processing and digital security. Future work will focus on rigorous collision analysis, security enhancements through algorithmic evolution, and performance optimization.