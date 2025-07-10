# White Paper: SineScramble
## A Multi-Mode Symmetric Cipher Combining Sine-Wave-Based Permutation and Substitution

**Version:** 2.1.0  
**Date:** July 10, 2025  
**Author:** N Lisowski

---

## Abstract

This paper introduces SineScramble, a novel and flexible symmetric encryption algorithm designed to address the classic cryptographic trade-off between security and performance. It can be configured to operate in two distinct modes: a high-security Multi-Round Mode and a high-performance Segmented Mode. The algorithm leverages a sine-wave-based scoring function, seeded by a multi-dimensional secret key (a vector of continuous values), to deterministically control both data permutation (diffusion) and substitution (confusion).

In Multi-Round Mode, the entire data block undergoes multiple iterative transformations, maximizing cryptographic diffusion to provide robust protection suitable for data-at-rest. In Segmented Mode, the data block is partitioned, with each segment being transformed in parallel by a unique component of the key vector, maximizing throughput for low-latency stream processing. This dual-mode architecture, founded on a deterministic yet non-linear engine, allows SineScramble to be adapted for a wide range of modern applications, from secure file storage to real-time encrypted communications.

---

## 1. Introduction

The design of secure and practical cryptographic systems requires a delicate balance between the principles of confusion and diffusion, and the performance constraints of the target environment. While multi-round block ciphers like AES have become the gold standard for security, their iterative nature and fixed block sizes can introduce latency or computational overhead that is prohibitive for certain applications, such as IoT devices or high-frequency data streams. This creates an ongoing need for novel cipher designs that offer greater architectural flexibility.

This work evolves the SineScramble cipher by introducing a flexible architecture that supports two distinct operational modes, addressing this security-versus-performance dilemma. The design originates from SineShift, a permutation-only obfuscation technique vulnerable to Known-Plaintext Attacks (KPA). SineScramble was conceived to solve this vulnerability by integrating a substitution phase, transforming it into a true cipher. This paper formalizes its most advanced iteration, which features a dual-mode architecture driven by a multi-dimensional key vector, $K = (k_1, k_2, ..., k_n)$.

The Multi-Round Mode is formalized as the high-security option, where the key vector drives $n$ sequential transformation rounds over an entire data block. This iterative process ensures the cryptographic property of diffusion is maximized. In contrast, the Segmented Mode is introduced as a high-performance alternative. In this mode, the data block is divided into $n$ segments, and the $n$ key components are used to process all segments in a single, parallelizable pass. This approach significantly reduces computational overhead and latency, making it suitable for scenarios where throughput is the primary concern. This dual-mode design makes SineScramble a versatile cryptographic tool, capable of being tailored to specific security and performance requirements.

---

## 2. The SineScramble Algorithm

SineScramble operates as a symmetric block cipher. Its core is a unified scoring engine that translates a multi-dimensional key into deterministic instructions. The interpretation of these instructions depends on the selected operational mode, allowing the cipher's behavior to be fundamentally altered without changing its core mathematical engine.

### 2.1. The Key Schedule

The secret key $K$ is defined as a vector of $n$ continuous real numbers:

$$K = (k_1, k_2, ..., k_n)$$

The dimension $n$ of the key is a critical, user-defined security parameter. It dictates either the number of iterative rounds (in Multi-Round Mode) or the number of parallel segments (in Segmented Mode). This approach treats the key not as a simple password, but as a set of precise mathematical parameters that seed the transformation engine, with higher dimensionality generally corresponding to a more complex and secure transformation.

### 2.2. The Unified Scoring Engine

The foundation of the cipher is a scoring function that generates a unique, deterministic score for each index $i$. This function is invoked using a key component $k_j$ and is the mathematical heart of the entire system:

$$\text{score}_j(i) = A \cdot \sin(k_j \cdot \gamma + i \cdot \omega) + i$$

Where $j$ corresponds to either the current round or the current segment. The role of each parameter is as follows:

- **$A$ (Amplitude):** Controls the influence of the chaotic sine component. A higher amplitude increases the non-linearity of the scores.
- **$\omega$ (Frequency):** Controls the granularity of the permutation, determining how rapidly the sine wave oscillates across the data indices.
- **$\gamma$ (Phase):** Adjusts the starting point of the sine function, ensuring different keys produce unique wave patterns.
- **$+ i$ (Linear Term):** This crucial component ensures the scoring function is monotonic in expectation, which dramatically reduces the probability of score collisions and is essential for generating a valid, one-to-one permutation map.

The use of a sine wave is deliberate: it is a non-linear, deterministic, and continuous function, allowing a continuous key input to generate a complex and unpredictable, yet perfectly repeatable, set of scores. These scores drive both permutation and substitution.

### 2.3. Modes of Operation

The transformation process is dictated by one of two modes selected during initialization.

#### 2.3.1. Multi-Round Mode (High Security)

This mode maximizes security by applying $n$ sequential transformation rounds to the entire data block, prioritizing diffusion. Let $\text{Data}_0$ be the initial plaintext. For each round $j$ from 1 to $n$:

1. A permutation map $P_j$ and a set of substitution instructions are generated from the scores derived using $k_j$.
2. The entire block $\text{Data}_{j-1}$ is first permuted according to $P_j$. This shuffles the data thoroughly.
3. The permuted data is then subjected to substitution, where bits are inverted based on the score-driven instructions. This produces $\text{Data}_j$.

The final ciphertext is the output of the last round, $\text{Data}_n$. This iterative process creates a powerful avalanche effect: a change to a single bit in the plaintext is diffused across the block in the first round, and in subsequent rounds, those changes are further permuted and substituted, rapidly causing every bit of the ciphertext to depend on every bit of the plaintext and the key.

#### 2.3.2. Segmented Mode (High Performance)

This mode maximizes throughput by processing the data in a single, parallelizable pass.

1. The data block of size $N$ is partitioned into $n$ contiguous segments, $S_1, S_2, ..., S_n$, each of size $N/n$. For example, a 1MB file and a 10-dimensional key would yield ten 100KB segments.
2. For each segment $S_j$, a single transformation round (permutation and substitution) is applied using the corresponding key component $k_j$.
3. Because the processing of each segment is independent of the others, this operation can be executed in parallel on multi-core processors, offering significant speed advantages.
4. The resulting transformed segments are concatenated to form the final ciphertext. This process avoids the iterative latency of the Multi-Round mode, making it ideal for real-time encryption of data streams where low latency is critical.

### 2.4. Encryption and Decryption Process

The workflows are perfectly symmetric. The chosen mode and key vector $K$ must be identical for both encryption and decryption.

**Encryption:**
- **Multi-Round:** $\text{Ciphertext} = \text{Round}_n(...\text{Round}_2(\text{Round}_1(\text{Plaintext}, k_1), k_2)..., k_n)$
- **Segmented:** $\text{Ciphertext} = \text{Concat}(\text{Round}(S_1, k_1), \text{Round}(S_2, k_2), ..., \text{Round}(S_n, k_n))$

**Decryption:**
Decryption involves applying the inverse Round operations (inverse substitution followed by inverse permutation) in the reverse order for the respective mode. For Multi-Round, rounds are processed from $n$ down to 1. For Segmented, each segment is decrypted with its corresponding key component.

---

## 3. Security Analysis

The security profile of SineScramble is a direct function of the chosen operational mode, representing a user-controlled balance between strength and speed.

### 3.1. Key Space and Strength

In both modes, the theoretical key space is approximately $(2^{64})^n$, where $n$ is the number of key components. This allows for a configurable and exceptionally large key space, rendering brute-force attacks computationally infeasible. The use of floating-point numbers as key material provides a vast parameter space for the sine-wave engine.

### 3.2. Resistance to Known-Plaintext Attack (KPA)

Both modes provide strong resistance to KPA, a critical measure of a modern cipher's strength.

- **In Multi-Round Mode,** resistance is profound. An attacker would need to deconstruct the complex, nested composition of $n$ full-block transformations. This is equivalent to solving a large system of non-linear equations, a problem considered computationally intractable.

- **In Segmented Mode,** an attacker's task is partitioned. A KPA would allow them to potentially solve for the transformation of a single segment, $S_j$. However, this provides no information about the transformation of any other segment, $S_{k \neq j}$, as each is encrypted with a different, independent key component. This "firewalling" between segments contains the damage of any potential localized break.

### 3.3. Confusion and Diffusion

**Confusion:** Both modes offer strong confusion. The substitution phase, where the decision to invert bits is based on a non-linear sine function of the key, creates a highly complex statistical relationship between the key and the ciphertext values, obscuring patterns.

**Diffusion:** This is the primary trade-off.

- **Multi-Round Mode** is designed to provide excellent diffusion across the entire data block. After a sufficient number of rounds, the cipher is expected to satisfy the Strict Avalanche Criterion (SAC), where changing a single input bit flips approximately 50% of the output bits. This is the gold standard for a secure block cipher.

- **Segmented Mode** provides excellent diffusion within each segment but, by design, provides zero inter-segment diffusion. A change in a bit in segment $S_j$ will never affect the output of segment $S_{j+1}$. This is a deliberate architectural trade-off, making it suitable for stream cipher applications but less ideal for use cases requiring holistic data integrity, like hashing or data-at-rest disk encryption.

### 3.4. Requirement for Formal Cryptanalysis

While architecturally robust, SineScramble remains a theoretical cipher. To be validated as secure, both operational modes must undergo rigorous, public cryptanalysis by the professional community. This process must include testing for vulnerabilities to a wide range of attacks, including differential and linear cryptanalysis (which analyze how differences propagate through the cipher), slide attacks (which target weaknesses in round-based structures), and timing or other side-channel attacks that could leak key information through implementation details.

---

## 4. Conclusion

SineScramble (v2.1) is designed as a flexible and powerful symmetric cipher, offering two distinct operational modes to directly address the perennial trade-off between security and performance. The Multi-Round Mode provides maximum security through iterative, full-block transformations, making it suitable for robust encryption of data-at-rest. The Segmented Mode provides high throughput and low latency by processing data segments in a single, parallelizable pass, making it ideal for real-time communications and streaming applications.

By leveraging a multi-dimensional key to drive its core permutation-substitution engine, SineScramble offers a versatile framework adaptable to diverse cryptographic challenges. Future work must focus on creating reference implementations, performance benchmarking against established ciphers, and submitting both modes to the cryptographic community for formal security validation.
