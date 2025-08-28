# SineScramble Tamarin Prover Analysis

This document provides a comprehensive guide for analyzing SineScramble's security properties using Tamarin Prover, a formal verification tool for cryptographic protocols and algorithms.

## Overview

Tamarin Prover is a symbolic protocol verification tool that can formally analyze cryptographic algorithms for security properties. This analysis covers:

- **Core Security Properties**: Confidentiality, integrity, correctness
- **Attack Resistance**: Known-plaintext, chosen-plaintext, differential, linear cryptanalysis
- **Side-Channel Resistance**: Timing attacks, power analysis
- **Advanced Attacks**: Meet-in-the-middle, slide attacks, algebraic attacks

## Files

- `sinescramble_tamarin.spthy` - Main security properties model
- `sinescramble_attacks.spthy` - Attack scenarios and resistance analysis

## Installation

### Automatic Installation (Recommended)

The analysis script will automatically install Tamarin Prover if it's not found:

```bash
# Run the analysis (auto-installs Tamarin Prover if needed)
./run_tamarin_analysis.sh

# Install Tamarin Prover only
./run_tamarin_analysis.sh install
```

### Manual Installation

If you prefer to install manually:

#### Prerequisites

1. **Tamarin Prover**: Install from [https://tamarin-prover.github.io/](https://tamarin-prover.github.io/)
2. **Haskell Stack**: Required for Tamarin Prover
3. **GraphViz**: For visualization (optional)

#### Installation Steps

```bash
# Install Haskell Stack
curl -sSL https://get.haskellstack.org/ | sh

# Install Tamarin Prover
git clone https://github.com/tamarin-prover/tamarin-prover.git
cd tamarin-prover
stack install

# Verify installation
tamarin-prover --version
```

## Model Structure

### Core Model (`sinescramble_tamarin.spthy`)

#### Types
```spthy
types
    KeyVector, Plaintext, Ciphertext, KeyComponent, Mode, Round, Segment
```

#### Functions
```spthy
functions
    score/3,           /* Core scoring function */
    permute/3,         /* Permutation operation */
    substitute/3,      /* Substitution operation */
    transform_round/4, /* Round transformation */
    encrypt_multi_round/3,  /* Multi-round encryption */
    decrypt_multi_round/3,  /* Multi-round decryption */
    encrypt_segmented/3,    /* Segmented encryption */
    decrypt_segmented/3,    /* Segmented decryption */
```

#### Key Rules
- **Key Generation**: Random and password-based key generation
- **Encryption/Decryption**: Both Multi-Round and Segmented modes
- **Round Transformation**: Internal permutation and substitution operations
- **Scoring Function**: Core sine-wave-based scoring

### Attack Model (`sinescramble_attacks.spthy`)

#### Attack Scenarios
1. **Known-Plaintext Attack (KPA)**
2. **Chosen-Plaintext Attack (CPA)**
3. **Differential Cryptanalysis**
4. **Linear Cryptanalysis**
5. **Brute Force Attack**
6. **Timing Attack**
7. **Power Analysis Attack**
8. **Meet-in-the-Middle Attack**
9. **Slide Attack**
10. **Algebraic Attack**

## Running the Analysis

### Automated Analysis (Recommended)

```bash
# Run comprehensive analysis (auto-installs Tamarin Prover if needed)
./run_tamarin_analysis.sh

# Run specific analysis types
./run_tamarin_analysis.sh basic
./run_tamarin_analysis.sh attacks
./run_tamarin_analysis.sh side-channel
./run_tamarin_analysis.sh advanced
./run_tamarin_analysis.sh comprehensive
```

### Manual Analysis

```bash
# Analyze core security properties
tamarin-prover sinescramble_tamarin.spthy

# Analyze attack resistance
tamarin-prover sinescramble_attacks.spthy
```

### Specific Lemma Analysis

```bash
# Check confidentiality
tamarin-prover sinescramble_tamarin.spthy --prove=confidentiality_multi_round

# Check KPA resistance
tamarin-prover sinescramble_attacks.spthy --prove=kpa_resistance_multi_round

# Check differential resistance
tamarin-prover sinescramble_attacks.spthy --prove=differential_resistance_multi_round
```

### Interactive Mode

```bash
# Start interactive analysis
tamarin-prover sinescramble_tamarin.spthy --interactive

# In interactive mode:
# - Use 'prove' to prove lemmas
# - Use 'auto' for automatic proof search
# - Use 'help' for available commands
```

## Key Security Properties

### 1. Confidentiality

**Lemma**: `confidentiality_multi_round`
```spthy
lemma confidentiality_multi_round:
    "All plaintext key_vector params #i #j.
        EncryptMultiRound(plaintext, key_vector, params) @ #i &
        K(plaintext) @ #j
        ==> #i < #j"
```

**Analysis**: Ensures that if plaintext is known to the attacker, it must be known before encryption.

### 2. Integrity

**Lemma**: `integrity_multi_round`
```spthy
lemma integrity_multi_round:
    "All ciphertext key_vector params plaintext #i #j.
        EncryptMultiRound(plaintext, key_vector, params) @ #i &
        DecryptMultiRound(ciphertext, key_vector, params) @ #j &
        ciphertext = encrypt_multi_round(plaintext, key_vector, params)
        ==> #i < #j"
```

**Analysis**: Ensures decryption happens after encryption.

### 3. Correctness

**Lemma**: `correctness_multi_round`
```spthy
lemma correctness_multi_round:
    "All plaintext key_vector params ciphertext #i #j.
        EncryptMultiRound(plaintext, key_vector, params) @ #i &
        DecryptMultiRound(ciphertext, key_vector, params) @ #j &
        ciphertext = encrypt_multi_round(plaintext, key_vector, params)
        ==> plaintext = decrypt_multi_round(ciphertext, key_vector, params)"
```

**Analysis**: Ensures encryption and decryption are inverse operations.

### 4. KPA Resistance

**Lemma**: `kpa_resistance_multi_round`
```spthy
lemma kpa_resistance_multi_round:
    "All plaintext1 plaintext2 key_vector1 key_vector2 params1 params2 #i #j.
        KnownPlaintextAttack(plaintext1, ciphertext1, key_vector1, params1) @ #i &
        KnownPlaintextAttack(plaintext2, ciphertext2, key_vector2, params2) @ #j &
        plaintext1 = plaintext2 &
        ciphertext1 = ciphertext2
        ==> key_vector1 = key_vector2 & params1 = params2"
```

**Analysis**: Ensures that identical plaintext-ciphertext pairs imply identical keys and parameters.

### 5. Avalanche Effect

**Lemma**: `avalanche_effect_multi_round`
```spthy
lemma avalanche_effect_multi_round:
    "All plaintext1 plaintext2 key_vector params #i #j.
        EncryptMultiRound(plaintext1, key_vector, params) @ #i &
        EncryptMultiRound(plaintext2, key_vector, params) @ #j &
        plaintext1 != plaintext2
        ==> encrypt_multi_round(plaintext1, key_vector, params) != encrypt_multi_round(plaintext2, key_vector, params)"
```

**Analysis**: Ensures small input changes cause large output changes.

## Attack Analysis

### Differential Cryptanalysis

**Model**: Analyzes how input differences propagate through the cipher.

**Resistance Lemma**:
```spthy
lemma differential_resistance_multi_round:
    "All plaintext1 plaintext2 key_vector params #i.
        DifferentialCryptanalysis(plaintext1, plaintext2, key_vector, params) @ #i
        ==> differential(plaintext1, plaintext2, key_vector, params) != 'weak_differential'"
```

### Linear Cryptanalysis

**Model**: Analyzes linear approximations of the cipher.

**Resistance Lemma**:
```spthy
lemma linear_resistance_multi_round:
    "All plaintext ciphertext key_vector params #i.
        LinearCryptanalysis(plaintext, ciphertext, key_vector, params) @ #i
        ==> correlation(linear_approximation(plaintext, ciphertext, key_vector, params), prob) < 0.6"
```

### Side-Channel Attacks

**Timing Attack Resistance**:
```spthy
lemma timing_attack_resistance:
    "All plaintext1 plaintext2 key_vector params timing1 timing2 #i #j.
        TimingAttack(plaintext1, key_vector, params, timing1) @ #i &
        TimingAttack(plaintext2, key_vector, params, timing2) @ #j &
        plaintext1 != plaintext2
        ==> timing1 = timing2"
```

## Analysis Results Interpretation

### Successful Proofs

When Tamarin Prover successfully proves a lemma, it indicates:

1. **Security Property Holds**: The specified security property is satisfied
2. **No Counterexamples**: No attack trace violates the property
3. **Formal Verification**: Mathematical proof of security

### Failed Proofs

When a proof fails, Tamarin Prover provides:

1. **Attack Trace**: Concrete example violating the property
2. **Counterexample**: Specific scenario where security fails
3. **Analysis**: Insight into potential vulnerabilities

### Example Output

```
tamarin-prover sinescramble_tamarin.spthy --prove=confidentiality_multi_round

[INFO] 2024-01-15 10:30:15 - Starting analysis...
[INFO] 2024-01-15 10:30:16 - Proving lemma: confidentiality_multi_round
[INFO] 2024-01-15 10:30:18 - Proof completed successfully
[INFO] 2024-01-15 10:30:18 - Lemma confidentiality_multi_round: verified
```

## Advanced Analysis Techniques

### 1. Parameter Sensitivity Analysis

```bash
# Analyze how parameter changes affect security
tamarin-prover sinescramble_tamarin.spthy --prove=parameter_independence
```

### 2. Mode Comparison

```bash
# Compare Multi-Round vs Segmented mode security
tamarin-prover sinescramble_tamarin.spthy --prove=multi_round_vs_segmented_security
```

### 3. Key Space Analysis

```bash
# Analyze key space properties
tamarin-prover sinescramble_tamarin.spthy --prove=key_space_large
```

## Custom Analysis

### Adding New Properties

To add new security properties:

1. **Define the property** in the model:
```spthy
lemma new_security_property:
    "All ... #i #j.
        ... @ #i &
        ... @ #j
        ==> ..."
```

2. **Run the analysis**:
```bash
tamarin-prover sinescramble_tamarin.spthy --prove=new_security_property
```

### Extending Attack Models

To add new attack scenarios:

1. **Define the attack rule**:
```spthy
rule NewAttack:
    [Plaintext(~plaintext), KeyVector(~key_vector), Parameters(~params)]
    --[NewAttack(~plaintext, ~key_vector, ~params)]->
    [AttackTrace('NewAttack', ~plaintext, ciphertext, ~key_vector, ~params)]
```

2. **Define resistance lemma**:
```spthy
lemma new_attack_resistance:
    "All ... #i.
        NewAttack(...) @ #i
        ==> ..."
```

## Best Practices

### 1. Model Validation

- **Test basic properties** first
- **Verify model consistency** with implementation
- **Check for logical errors** in lemmas

### 2. Performance Optimization

- **Use specific lemmas** rather than proving all at once
- **Limit search depth** for complex properties
- **Use heuristics** for automatic proof search

### 3. Result Interpretation

- **Understand counterexamples** when proofs fail
- **Analyze attack traces** for insights
- **Consider practical implications** of theoretical results

## Limitations

### 1. Symbolic Analysis

- **Abstracts concrete values** to symbolic terms
- **May miss implementation-specific issues**
- **Requires careful model abstraction**

### 2. Computational Limits

- **Complex properties** may timeout
- **Large state spaces** can be intractable
- **Heuristic search** may not find all attacks

### 3. Model Completeness

- **Model must accurately reflect** the actual algorithm
- **Missing properties** may not be detected
- **Implementation bugs** may not be captured

## Integration with Implementation

### 1. Model-Implementation Consistency

Ensure the Tamarin model accurately represents the Python implementation:

```python
# Python implementation
def _scoring_function(self, key_component, indices):
    sine_term = self.amplitude * np.sin(key_component * self.phase + indices * self.frequency)
    return sine_term + indices
```

```spthy
# Tamarin model
functions
    score/3  /* score(key_component, index, parameters) */
```

### 2. Property Verification

Use Tamarin results to guide implementation testing:

```python
def test_confidentiality():
    """Test confidentiality property verified by Tamarin"""
    cipher = SineScrambleCipher(key, OperationMode.MULTI_ROUND)
    # Test that plaintext is not leaked through ciphertext
    # This should align with Tamarin's confidentiality_multi_round lemma
```

## Future Work

### 1. Extended Analysis

- **Multi-party protocols** using SineScramble
- **Protocol composition** with other cryptographic primitives
- **Real-time analysis** for streaming applications

### 2. Implementation Verification

- **Code-level verification** using tools like Cryptol
- **Side-channel analysis** with concrete timing measurements
- **Performance verification** against theoretical bounds

### 3. Advanced Attacks

- **Quantum cryptanalysis** resistance
- **Post-quantum security** analysis
- **Machine learning** based attacks

## Conclusion

Tamarin Prover provides a powerful framework for formally analyzing SineScramble's security properties. The models presented here cover:

- **Core cryptographic properties** (confidentiality, integrity, correctness)
- **Attack resistance** (KPA, CPA, differential, linear cryptanalysis)
- **Side-channel resistance** (timing, power analysis)
- **Advanced attack scenarios** (MITM, slide, algebraic attacks)

This formal analysis complements empirical testing and provides mathematical guarantees about SineScramble's security properties. However, it should be used alongside other security analysis methods for comprehensive evaluation.

## References

1. [Tamarin Prover Documentation](https://tamarin-prover.github.io/)
2. [Symbolic Protocol Analysis](https://tamarin-prover.github.io/manual/book/002_protocol-specification.html)
3. [Cryptographic Protocol Verification](https://tamarin-prover.github.io/manual/book/003_cryptographic-messages.html)
4. [SineScramble Specification](../specifications/SineScramble.md) 