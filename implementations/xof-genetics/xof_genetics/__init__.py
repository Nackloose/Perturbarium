"""
XOF-Genetics: A unified, hash-agnostic genetic algorithm framework.

This package provides a single, configurable interface for genetic algorithms
that supports multiple hash functions, reproduction strategies, and evolution modes.
"""

__version__ = "2.1.0"

# Core classes
from .organism import (
    Organism, OrganismConfig, OrganismMode, ReproductionMethod,
    HashFunction, Blake3Hash, SHA256Hash
)

from .evolution import (
    EvolutionConfig, EvolutionMode, PairingStrategy, AutoPopulationConfig,
    evolutionary_loop, intergenerational_tournament, pair_organisms,
    analyze_population_strategies
)

# Convenience functions for organism configuration
from .organism import (
    create_basic_config, create_dual_encoded_config, create_meta_config
)

# Convenience functions for evolution configuration
from .evolution import (
    create_tournament_config, create_simple_config, create_omni_config,
    create_dual_encoded_config as create_dual_encoded_evolution_config
)

# Legacy functions for backward compatibility
from .evolution import (
    simple_evolutionary_loop, omni_evolutionary_loop
)

__all__ = [
    # Core classes
    'Organism', 'OrganismConfig', 'OrganismMode', 'ReproductionMethod',
    'HashFunction', 'Blake3Hash', 'SHA256Hash',
    'EvolutionConfig', 'EvolutionMode', 'PairingStrategy', 'AutoPopulationConfig',
    
    # Main functions
    'evolutionary_loop', 'intergenerational_tournament', 'pair_organisms',
    'analyze_population_strategies',
    
    # Convenience functions
    'create_basic_config', 'create_dual_encoded_config', 'create_meta_config',
    'create_tournament_config', 'create_simple_config', 'create_omni_config',
    'create_dual_encoded_evolution_config',
    
    # Legacy functions
    'simple_evolutionary_loop', 'omni_evolutionary_loop',
] 