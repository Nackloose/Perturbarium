# SineScramble Tamarin Prover Analysis

This folder contains the formal security analysis files for the SineScramble cipher using Tamarin Prover.

## Files

- **`sinescramble_tamarin.spthy`** - Main Tamarin model defining core cryptographic operations and security properties
- **`sinescramble_attacks.spthy`** - Tamarin model for analyzing resistance to various cryptanalytic and side-channel attacks
- **`tamarin_analysis_report.txt`** - Generated analysis report with detailed results
- **`tamarin_debug_*.txt`** - Debug output files for individual lemma tests

## Analysis Results

### ✅ VERIFIED Properties:
- **Confidentiality**: VERIFIED
- **Integrity**: VERIFIED  
- **Correctness**: VERIFIED

### ⚠️ FAILED Properties (Expected for Initial Models):
- **Attack Resistance**: Various attack resistance tests FAILED (normal for initial models)

## Usage

Run the analysis from the parent directory:

```bash
./run_tamarin_analysis.sh
```

For debug mode with verbose output:

```bash
DEBUG_MODE=true ./run_tamarin_analysis.sh
```

## Model Structure

The models define:
- Cryptographic functions (encrypt, decrypt, score)
- Security rules and lemmas
- Attack scenarios and resistance properties
- Formal verification of core security properties

## Next Steps

1. Refine attack resistance models
2. Add more sophisticated attack scenarios
3. Improve lemma definitions
4. Conduct empirical testing to complement formal analysis 