# Navigation Guide

## 📋 Quick Reference

### 🧠 Theoretical Papers (`theory/`)
- **`gdiff.md`** - Machine-readable diff format specification  
- **`Reverse-Publickey-Identity-Verification[RPIV].md`** - Inverted asymmetric cryptography
- **`xof-genetics.md`** - Genetic algorithms using cryptographic hash functions

### 📋 Technical Specifications (`specifications/`)
- **`SineScramble.md`** - Dual-mode symmetric cipher (security vs performance)
- **`SineShift.md`** - Deterministic permutation algorithm
- **`Licensee.md`** - Multi-layered software licensing system
- **`Instamaster.md`** - Automated audio mastering pipeline

### 📖 Development Guides (`guides/`)
- **`Coders-Guide-to-'Good'.md`** - Comprehensive software craftsmanship framework
- **`Evolution-Axia.md`** - The evolution and philosophy of Axia itself

### 🔧 Working Implementations (`implementations/`)
- **`sinescramble/`** - Complete cipher implementation with performance tools and Tamarin Prover analysis
- **`sineshift/`** - Permutation algorithm with analysis tools and visualization
- **`licensee/`** - Full licensing system with UI and key generation
- **`instamaster/`** - Audio processing pipeline with automated mastering
- **`xof-genetics/`** - Genetic algorithm implementation using cryptographic hash functions
- **`claude-agents/`** - AI agent frameworks for various development tasks

### 💭 Creative Workspace (`inkspill/`)
- **`assembly-tracer.md`** - Assembly-level execution tracing and analysis framework
- **`assembly-tracer.spec.md`** - Detailed specification for assembly tracing system
- **`fft_compression_concept.md`** - FFT-based data compression concepts and experiments
- **`react-mono.md`** - React monorepo architecture and patterns
- **`slots.html`** - Interactive slots game implementation
- **`notes/`** - Raw thoughts, outlines, observations, and experimental fragments

## 🎯 Finding What You Need

### I want to learn about...
- **Cryptography**: Start with `theory/` for novel approaches, then `specifications/` for detailed algorithms
- **Audio Processing**: Check `specifications/Instamaster.md` and `implementations/instamaster/`
- **Software Licensing**: See `specifications/Licensee.md` and `implementations/licensee/`
- **Data Permutation**: Review `specifications/SineShift.md` and `implementations/sineshift/`
- **Coding Best Practices**: Read `guides/Coders-Guide-to-'Good'.md`
- **Evolutionary Algorithms**: Explore `theory/xof-genetics.md` and `implementations/xof-genetics/`
- **AI Development**: Check `implementations/claude-agents/`

### I want to run something...
- **Cipher Demo**: `implementations/sinescramble/demo.py`
- **Audio Mastering**: `implementations/instamaster/instamaster.py`
- **License Generator**: `implementations/licensee/keygen_ui.py`
- **Permutation Analysis**: `implementations/sineshift/run.sh`
- **Genetic Algorithm**: `implementations/xof-genetics/`
- **Interactive Game**: `inkspill/slots.html`

### I want to understand the theory...
- **Evolutionary Algorithms**: `theory/xof-genetics.md`
- **Diff Formats**: `theory/gdiff.md`
- **Identity Verification**: `theory/Reverse-Publickey-Identity-Verification[RPIV].md`
- **Cipher Design**: `specifications/SineScramble.md`
- **Permutation Theory**: `specifications/SineShift.md`

## 🔗 Project Relationships

```
SineShift (permutation) 
    ↓ used by
SineScramble (cipher)
    ↓ used by  
Licensee (licensing)
    ↓ independent
Instamaster (audio)
    ↓ independent
XOF-Genetics (evolution)
    ↓ independent
Claude-Agents (AI automation)
```

## 📁 Directory Structure

```
Axia/
├── theory/                    # Theoretical foundations
│   ├── gdiff.md              # Machine-readable diff format
│   ├── xof-genetics.md       # Genetic algorithms with crypto
│   └── RPIV.md               # Reverse public key identity
├── specifications/            # Technical specifications
│   ├── SineScramble.md       # Cipher specification
│   ├── SineShift.md          # Permutation algorithm
│   ├── Licensee.md           # Licensing system
│   └── Instamaster.md        # Audio mastering
├── guides/                    # Best practices and philosophy
│   ├── Coders-Guide-to-'Good'.md
│   └── Evolution-Axia.md
├── implementations/           # Working code
│   ├── sinescramble/         # Cipher implementation
│   ├── sineshift/            # Permutation tools
│   ├── licensee/             # Licensing system
│   ├── instamaster/          # Audio processing
│   ├── xof-genetics/         # Genetic algorithms
│   └── claude-agents/        # AI frameworks
├── inkspill/                  # Creative workspace
│   ├── assembly-tracer.md    # Assembly analysis
│   ├── react-mono.md         # React architecture
│   ├── slots.html            # Interactive game
│   └── notes/                # Raw thoughts
└── NAVIGATION.md             # This file
```

## 🚀 Quick Commands

### Setup and Run
```bash
# Cipher demo
cd implementations/sinescramble && python demo.py

# Audio mastering
cd implementations/instamaster && python instamaster.py

# License generation
cd implementations/licensee && python keygen_ui.py

# Permutation analysis
cd implementations/sineshift && ./run.sh

# Genetic algorithm
cd implementations/xof-genetics && python -m xof_genetics.demo
```

### Development
```bash
# Install dependencies for a project
cd implementations/[project] && pip install -r requirements.txt

# Run tests
cd implementations/[project] && python -m pytest

# View documentation
cd specifications && cat [project].md
```

## 📚 Learning Paths

### Cryptography Enthusiast
1. `theory/Reverse-Publickey-Identity-Verification[RPIV].md`
2. `specifications/SineShift.md`
3. `specifications/SineScramble.md`
4. `implementations/sineshift/`
5. `implementations/sinescramble/`

### Audio Engineer
1. `specifications/Instamaster.md`
2. `implementations/instamaster/`
3. `inkspill/fft_compression_concept.md`

### Software Architect
1. `guides/Coders-Guide-to-'Good'.md`
2. `theory/gdiff.md`
3. `inkspill/react-mono.md`
4. `implementations/claude-agents/`

### Algorithm Designer
1. `theory/xof-genetics.md`
2. `implementations/xof-genetics/`
3. `specifications/SineShift.md`
4. `specifications/SineScramble.md`

Each implementation has corresponding documentation that explains the theory, design decisions, and usage patterns. 