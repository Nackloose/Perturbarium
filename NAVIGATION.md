# Navigation Guide

## Quick Reference

### 🧠 Theoretical Papers (`theory/`)
- **`blake3-genetics.md`** - Genetic algorithms using cryptographic hash functions
- **`gdiff.md`** - Machine-readable diff format specification  
- **`Reverse-Publickey-Identity-Verification[RPIV].md`** - Inverted asymmetric cryptography

### 📋 Technical Specifications (`specifications/`)
- **`SineScramble.md`** - Dual-mode symmetric cipher (security vs performance)
- **`SineShift.md`** - Deterministic permutation algorithm
- **`Licensee.md`** - Multi-layered software licensing system
- **`Instamaster.md`** - Automated audio mastering pipeline

### 📖 Development Guides (`guides/`)
- **`Coders-Guide-to-'Good'.md`** - Comprehensive software craftsmanship framework

### 🔧 Working Implementations (`implementations/`)
- **`sinescramble/`** - Complete cipher implementation with performance tools
- **`sineshift/`** - Permutation algorithm with analysis tools
- **`licensee/`** - Full licensing system with UI
- **`instamaster/`** - Audio processing pipeline

## Finding What You Need

### I want to learn about...
- **Cryptography**: Start with `theory/` for novel approaches, then `specifications/` for detailed algorithms
- **Audio Processing**: Check `specifications/Instamaster.md` and `implementations/instamaster/`
- **Software Licensing**: See `specifications/Licensee.md` and `implementations/licensee/`
- **Data Permutation**: Review `specifications/SineShift.md` and `implementations/sineshift/`
- **Coding Best Practices**: Read `guides/Coders-Guide-to-'Good'.md`

### I want to run something...
- **Cipher Demo**: `implementations/sinescramble/demo.py`
- **Audio Mastering**: `implementations/instamaster/instamaster.py`
- **License Generator**: `implementations/licensee/keygen_ui.py`
- **Permutation Analysis**: `implementations/sineshift/run.sh`

### I want to understand the theory...
- **Evolutionary Algorithms**: `theory/blake3-genetics.md`
- **Diff Formats**: `theory/gdiff.md`
- **Identity Verification**: `theory/Reverse-Publickey-Identity-Verification[RPIV].md`

## Project Relationships

```
SineShift (permutation) 
    ↓ used by
SineScramble (cipher)
    ↓ used by  
Licensee (licensing)
    ↓ independent
Instamaster (audio)
```

Each implementation has corresponding documentation that explains the theory, design decisions, and usage patterns. 