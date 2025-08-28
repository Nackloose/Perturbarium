# XOF-Genetics

A unified, hash-agnostic genetic algorithm framework with configurable reproduction strategies.

## Overview

XOF-Genetics provides a single, configurable interface for genetic algorithms that supports multiple hash functions, reproduction strategies, and evolution modes. The framework consolidates all features into a unified system rather than separate classes and functions.

## Key Features

- **Unified Interface**: Single `Organism` class that supports all modes through configuration
- **Hash-Agnostic Design**: Pluggable hash functions (BLAKE3, SHA256, custom)
- **Configurable Reproduction**: 8 different reproduction methods with flexible combination strategies
- **Multiple Evolution Modes**: Tournament, Simple, Omni, Dual-Encoded, and Meta evolution
- **Boolean Configuration**: Enable/disable dual encoding and reciprocal reproduction
- **Full Threading Support**: Parallel fitness evaluation, reproduction, and all operations
- **Auto-Population Sizing**: Automatic population size adjustment based on generation time targets
- **Generation Callbacks**: Real-time monitoring and control of evolution progress
- **Comprehensive Testing**: Full test suite with pytest
- **Modern Packaging**: Proper Python packaging with pyproject.toml

## Installation

### From Source

```bash
git clone <repository-url>
cd xof-genetics
pip install -e .
```

### Development Installation

```bash
pip install -e ".[dev]"
```

## Quick Start

```python
from xof_genetics import (
    Organism, create_basic_config, create_tournament_config,
    evolutionary_loop
)

# Create configuration
org_config = create_basic_config(genome_length=64)
evo_config = create_tournament_config(max_generations=10)

# Create initial population
population = [
    Organism.from_seed(f"seed_{i}".encode(), org_config)
    for i in range(20)
]

# Define fitness function
def fitness(organism):
    return sum(organism.genome) / len(organism.genome)

# Run evolution
final_population = evolutionary_loop(population, fitness, evo_config)
```

## Advanced Features

### Threading and Performance

The framework supports full threading for maximum performance:

```python
from xof_genetics import create_tournament_config, AutoPopulationConfig

# Create configuration with threading
evo_config = create_tournament_config(
    max_generations=10,
    thread_count=8,  # Use 8 threads for all operations
    verbose=True
)

# Run evolution with threading
final_population = evolutionary_loop(population, fitness, evo_config)
```

### Smart Auto-Population Sizing

Intelligently manages population size by tracking optimal sizes and preventing slow generations:

```python
# Create smart auto-population configuration
auto_config = AutoPopulationConfig(
    enabled=True,
    generation_time_target=1.5,  # Target 1.5 seconds per generation
    min_population_size=10,
    max_population_size=10000,
    cull_factor=0.8  # Reduce population by 20% when over target
    # Smart tracking fields are automatically initialized:
    # - optimal_population_size: Best size found so far
    # - optimal_generation_time: Time for optimal size
    # - initial_population_time: Time for initial population
    # - max_safe_population: Largest population that stayed under target
)

# Use auto-population
evo_config = create_tournament_config(
    max_generations=10,
    population_cap="auto",  # Enable auto-population
    auto_population=auto_config
)
```

**Smart Features:**
- **Tracks Initial Time**: Records how long the initial population takes
- **Finds Optimal Size**: Identifies the population size with fastest generation time
- **Tracks Safe Limits**: Remembers the largest population that stayed under target time
- **Smart Culling**: Uses known safe sizes to avoid waiting for slow generations
- **Preemptive Culling**: Culls before generation if population is growing too fast

### Generation Callbacks

Monitor evolution progress in real-time:

```python
def generation_callback(state):
    generation = state['generation']
    population = state['population']
    generation_time = state.get('generation_time', 0)
    thread_count = state['thread_count']
    
    print(f"Generation {generation}: {len(population)} organisms, "
          f"{generation_time:.2f}s, {thread_count} threads")

# Run evolution with callback
final_population = evolutionary_loop(
    population, 
    fitness, 
    evo_config,
    generation_callback=generation_callback
)
```

## Configuration Options

### Organism Configuration

```python
from xof_genetics import OrganismConfig, OrganismMode, ReproductionMethod

# Basic configuration
config = OrganismConfig(
    genome_length=256,                    # Genome size in bytes
    hash_function="blake3",               # "blake3", "sha256", or custom
    mode=OrganismMode.BASIC,              # BASIC, DUAL_ENCODED, META
    enabled_methods=[                     # Which reproduction methods to use
        ReproductionMethod.SEXUAL,
        ReproductionMethod.MUTATION
    ],
    combination_strategy="all",           # "all", "random", "weighted"
    enable_dual_encoding=False,           # Enable dual encoding
    enable_reciprocal_reproduction=True   # Produce 1 or 2 children in sexual reproduction
)
```

### Evolution Configuration

```python
from xof_genetics import EvolutionConfig, EvolutionMode, PairingStrategy, AutoPopulationConfig

# Evolution configuration
evo_config = EvolutionConfig(
    mode=EvolutionMode.TOURNAMENT,        # TOURNAMENT, SIMPLE, OMNI, DUAL_ENCODED, META
    pairing_strategy=PairingStrategy.RANDOM,  # RANDOM, ELITE_VS_ELITE, etc.
    max_generations=10,                   # Maximum generations
    population_cap=1000,                  # Maximum population size (or "auto" for auto-sizing)
    elite_fraction=0.1,                   # Fraction to preserve as elite
    selection_pressure=0.5,               # Selection pressure for tournaments
    verbose=False,                        # Print progress
    track_strategy_history=False,         # Track evolution history
    thread_count=1,                       # Number of threads for all operations
    auto_population=None                  # Auto-population configuration
)
```

## Reproduction Methods

The framework supports 8 different reproduction methods:

1. **Direct Asexual**: Simple cloning with hash-based variation
2. **Asexual Self**: Self-reproduction using organism's strategy
3. **Sexual**: Crossover between two parents
4. **Mutation**: XOR-based mutation with configurable masks
5. **Rotation**: Circular rotation of genome
6. **Permutation**: Reordering of genome bytes
7. **Combined Transformations**: Multiple transformations applied
8. **Enhanced Sexual**: Advanced sexual reproduction with multiple strategies

## Evolution Modes

- **Tournament**: Intergenerational tournament selection
- **Simple**: Basic selection and reproduction
- **Omni**: Uses omni-reproduction method
- **Dual-Encoded**: Organisms encode their reproduction strategy
- **Meta**: Separate meta-genome encodes reproduction strategy

## Hash Functions

### Built-in Hash Functions

```python
from xof_genetics import Blake3Hash, SHA256Hash

# SHA256 (always available)
sha256_hash = SHA256Hash()

# BLAKE3 (requires blake3 package)
try:
    blake3_hash = Blake3Hash()
except ImportError:
    print("BLAKE3 not available, install with: pip install blake3")
```

### Custom Hash Functions

```python
from xof_genetics import HashFunction

class CustomHash(HashFunction):
    def hash(self, data: bytes, length: int) -> bytes:
        # Your custom hash implementation
        return your_hash_function(data, length)

# Use in configuration
config = OrganismConfig(hash_function=CustomHash())
```

## Convenience Functions

```python
from xof_genetics import (
    create_basic_config, create_dual_encoded_config, create_meta_config,
    create_tournament_config, create_simple_config, create_omni_config
)

# Organism configurations
basic_config = create_basic_config(genome_length=64)
dual_config = create_dual_encoded_config(genome_length=128)
meta_config = create_meta_config(genome_length=64, meta_genome_length=32)

# Evolution configurations
tournament_config = create_tournament_config(max_generations=10)
simple_config = create_simple_config(max_generations=5)
omni_config = create_omni_config(max_generations=8)
```

## Boolean Configuration Flags

### Dual Encoding Flag

```python
# Enable dual encoding in basic mode
config = create_basic_config(enable_dual_encoding=True)
organism = Organism.from_seed(b"seed", config)
children = organism.reproduce()  # Uses dual-encoded logic
```

### Reciprocal Reproduction Flag

```python
# Disable reciprocal reproduction (produce only 1 child)
config = create_basic_config(enable_reciprocal_reproduction=False)
parent1 = Organism.from_seed(b"parent1", config)
parent2 = Organism.from_seed(b"parent2", config)
children = parent1.reproduce_sexually(parent2)  # Returns 1 child instead of 2
```

## Testing

The framework includes comprehensive tests that validate compliance with the XOF-Genetics specification:

### Test Categories

```bash
# Run all regular tests (fast)
pytest tests/ -v

# Run limit tests (large scale but manageable)
pytest -m "limit"

# Run full loop/soak tests (long-running)
pytest -m "full_loop"

# Run extreme tests (for dedicated hardware)
pytest -m "extreme"

# Run resource scaling tests
pytest -m "fill_resources"

# Run all extreme tests together
pytest -m "limit or extreme or fill_resources or full_loop"

# Run with coverage
pytest --cov=xof_genetics --cov-report=html

# Run fast tests only
pytest -m "not slow"

# Run specific test file
pytest tests/test_organism.py
```

### Test Parameters

The extreme tests use realistic parameters:
- **Maximum genome size**: 2048 bytes
- **Maximum generations**: 100
- **Population scaling**: Based on available system memory
- **Resource limits**: 70-80% of available memory/CPU

### Specification Compliance

The test suite includes `test_specification_compliance.py` which validates:
- Hash-genome system compliance (G = H(D, L) formula)
- Evolutionary operators (asexual, sexual, mutation)
- Dual Offspring Principle
- Dual-Encoded Self-Evolving Organisms
- Intergenerational Tournament Selection
- Determinism and replayability
- Competitive co-evolution dynamics
- Hash function agnosticism
- Phenotype agnosticism

## Development

### Setup Development Environment

```bash
# Install with development dependencies
pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install

# Run all checks
make check
```

### Available Make Commands

```bash
make help          # Show all available commands
make install       # Install in development mode
make test          # Run tests
make test-cov      # Run tests with coverage
make lint          # Run linting
make format        # Format code
make clean         # Clean build artifacts
make build         # Build package
make demo          # Run demo
```

## Examples

### Basic Evolution

```python
from xof_genetics import *

# Create configurations
org_config = create_basic_config(genome_length=64)
evo_config = create_tournament_config(max_generations=10)

# Create population
population = [Organism.from_seed(f"seed_{i}".encode(), org_config) for i in range(20)]

# Define fitness function
def fitness(organism):
    return sum(organism.genome) / len(organism.genome)

# Run evolution
final_population = evolutionary_loop(population, fitness, evo_config)
```

### Dual-Encoded Evolution

```python
# Dual-encoded configuration
org_config = create_dual_encoded_config(genome_length=64)
evo_config = create_dual_encoded_evolution_config(max_generations=10)

population = [Organism.from_seed(f"seed_{i}".encode(), org_config) for i in range(20)]
final_population = evolutionary_loop(population, fitness, evo_config)
```

### Meta Evolution

```python
# Meta configuration
org_config = create_meta_config(genome_length=64, meta_genome_length=32)
evo_config = create_meta_evolution_config(max_generations=10)

population = [Organism.from_seed(f"seed_{i}".encode(), org_config) for i in range(20)]
final_population = evolutionary_loop(population, fitness, evo_config)
```

### Custom Configuration

```python
# Custom organism configuration
org_config = OrganismConfig(
    genome_length=128,
    hash_function="sha256",
    mode=OrganismMode.BASIC,
    enabled_methods=[ReproductionMethod.SEXUAL, ReproductionMethod.MUTATION],
    combination_strategy="weighted",
    enable_dual_encoding=True,
    enable_reciprocal_reproduction=False
)

# Custom evolution configuration
evo_config = EvolutionConfig(
    mode=EvolutionMode.TOURNAMENT,
    pairing_strategy=PairingStrategy.COMPLEMENTARY,
    max_generations=15,
    population_cap=500,
    elite_fraction=0.2,
    verbose=True,
    track_strategy_history=True
)
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Run the test suite: `make test`
6. Run linting: `make lint`
7. Format code: `make format`
8. Submit a pull request

## License

MIT License - see LICENSE file for details.

## Version History

- **2.0.0**: Unified framework with configurable interface
- **1.x.x**: Original fragmented implementation (deprecated) 