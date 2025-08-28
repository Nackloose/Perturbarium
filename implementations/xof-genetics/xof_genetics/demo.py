#!/usr/bin/env python3
"""
Unified Demo module for XOF-Genetics framework.

This module provides comprehensive demonstrations of all features of the
unified XOF-Genetics framework, including different organism modes,
evolution strategies, and hash functions.
"""

import random
import time
from typing import List

from .organism import (
    Organism, OrganismConfig, OrganismMode, ReproductionMethod,
    create_basic_config, create_dual_encoded_config, create_meta_config
)
from .evolution import (
    EvolutionConfig, EvolutionMode, PairingStrategy, AutoPopulationConfig,
    evolutionary_loop, analyze_population_strategies,
    create_tournament_config, create_simple_config, create_omni_config,
    create_dual_encoded_config as create_dual_encoded_evolution_config
)


def simple_sum_fitness(organism: Organism) -> float:
    """Simple fitness function based on the sum of genome bytes."""
    genome_sum = sum(organism.genome)
    variation = (hash(organism.genome) % 1000) / 10.0
    return genome_sum + variation


def pattern_matching_fitness(organism: Organism) -> float:
    """Fitness function that rewards organisms with specific byte patterns."""
    fitness = 0.0
    
    # Reward for having alternating high/low bytes
    for i in range(0, len(organism.genome) - 1, 2):
        if organism.genome[i] > 128 and organism.genome[i + 1] < 128:
            fitness += 10.0
    
    # Reward for having specific byte values at certain positions
    if organism.genome[0] == 255:
        fitness += 50.0
    if organism.genome[-1] == 0:
        fitness += 50.0
    
    # Reward for having a balanced distribution of byte values
    high_bytes = sum(1 for b in organism.genome if b > 128)
    low_bytes = len(organism.genome) - high_bytes
    balance_score = 1.0 - abs(high_bytes - low_bytes) / len(organism.genome)
    fitness += balance_score * 100.0
    
    return fitness


def create_initial_population(size: int, config: OrganismConfig) -> List[Organism]:
    """Creates an initial population of organisms from random seeds."""
    population = []
    for i in range(size):
        seed = f"organism_{i}_{random.randint(0, 10000)}".encode()
        organism = Organism.from_seed(seed, config)
        population.append(organism)
    return population


def run_basic_organism_demo():
    """Demonstrate basic organism mode with different configurations."""
    print("=== BASIC ORGANISM MODE DEMO ===")
    print("Demonstrating basic organisms with different configurations")
    print()
    
    # Create different basic configurations
    configs = [
        ("Basic with BLAKE3", create_basic_config(hash_function="blake3")),
        ("Basic with SHA256", create_basic_config(hash_function="sha256")),
        ("Basic with custom methods", create_basic_config(
            hash_function="blake3",
            enabled_methods=[ReproductionMethod.DIRECT_ASEXUAL, 
                           ReproductionMethod.SEXUAL, 
                           ReproductionMethod.MUTATION]
        )),
        ("Basic with all methods", create_basic_config(
            hash_function="blake3",
            enabled_methods=list(ReproductionMethod)
        ))
    ]
    
    for name, config in configs:
        print(f"\n--- {name} ---")
        
        # Create population
        population = create_initial_population(10, config)
        print(f"Created population of {len(population)} organisms")
        
        # Show reproduction strategy
        org = population[0]
        print(f"Reproduction strategy: {org.get_reproduction_summary()}")
        
        # Test reproduction
        if len(population) >= 2:
            parent1, parent2 = population[0], population[1]
            children = parent1.reproduce(parent2)
            print(f"Reproduction produced {len(children)} children")
            
            # Test asexual reproduction
            asexual_children = parent1.reproduce()
            print(f"Asexual reproduction produced {len(asexual_children)} children")


def run_dual_encoded_organism_demo():
    """Demonstrate dual-encoded organism mode."""
    print("\n=== DUAL-ENCODED ORGANISM MODE DEMO ===")
    print("Demonstrating organisms that encode their own reproduction strategies")
    print()
    
    # Create dual-encoded configuration
    config = create_dual_encoded_config(genome_length=256)
    print(f"Created dual-encoded configuration with genome length {config.genome_length}")
    
    # Create population
    population = create_initial_population(10, config)
    print(f"Created population of {len(population)} dual-encoded organisms")
    
    # Show reproduction strategy for a few organisms
    for i, org in enumerate(population[:3]):
        print(f"\nOrganism {i} reproduction strategy:")
        print(f"  {org.get_reproduction_summary()}")
    
    # Test reproduction between dual-encoded organisms
    if len(population) >= 2:
        parent1, parent2 = population[0], population[1]
        children = parent1.reproduce(parent2)
        print(f"\nDual-encoded reproduction produced {len(children)} children")
        
        # Show that children inherit combined strategies
        if children:
            child = children[0]
            print(f"Child reproduction strategy:")
            print(f"  {child.get_reproduction_summary()}")
    
    print("\nDual-encoded organisms can evolve their own reproduction strategies!")
    print("Each organism's genome encodes which reproduction methods to use,")
    print("how to combine them, and what parameters to use for each method.")


def run_evolution_modes_demo():
    """Demonstrate different evolution modes."""
    print("\n=== EVOLUTION MODES DEMO ===")
    print("Demonstrating different evolution modes with the same organism configuration")
    print()
    
    # Create basic organism configuration
    org_config = create_basic_config(
        hash_function="blake3",
        enabled_methods=[ReproductionMethod.DIRECT_ASEXUAL, 
                        ReproductionMethod.SEXUAL, 
                        ReproductionMethod.MUTATION]
    )
    
    # Create different evolution configurations
    evolution_configs = [
        ("Tournament Evolution", create_tournament_config(
            pairing_strategy=PairingStrategy.ELITE_VS_CHALLENGER,
            max_generations=5,
            verbose=False
        )),
        ("Simple Evolution", create_simple_config(
            max_generations=5,
            selection_pressure=0.3,
            verbose=False
        )),
        ("Omni Evolution", create_omni_config(
            max_generations=3,  # Reduced due to exponential growth
            verbose=False
        ))
    ]
    
    for name, evo_config in evolution_configs:
        print(f"\n--- {name} ---")
        
        # Create population
        population = create_initial_population(20, org_config)
        print(f"Starting with {len(population)} organisms")
        
        # Run evolution
        start_time = time.time()
        final_population = evolutionary_loop(population, simple_sum_fitness, evo_config)
        end_time = time.time()
        
        print(f"Evolution completed in {end_time - start_time:.2f} seconds")
        print(f"Final population size: {len(final_population)}")
        
        if final_population:
            best_organism = max(final_population, key=lambda x: x.fitness)
            print(f"Best fitness: {best_organism.fitness:.4f}")


def run_hash_function_comparison_demo():
    """Compare different hash functions."""
    print("\n=== HASH FUNCTION COMPARISON DEMO ===")
    print("Comparing BLAKE3 vs SHA256 hash functions")
    print()
    
    # Create configurations with different hash functions
    blake3_config = create_basic_config(hash_function="blake3")
    sha256_config = create_basic_config(hash_function="sha256")
    
    configs = [("BLAKE3", blake3_config), ("SHA256", sha256_config)]
    
    for name, config in configs:
        print(f"\n--- {name} Hash Function ---")
        
        # Create population
        population = create_initial_population(10, config)
        
        # Test reproduction speed
        start_time = time.time()
        for _ in range(100):
            if len(population) >= 2:
                parent1, parent2 = population[0], population[1]
                children = parent1.reproduce_sexually(parent2)
        end_time = time.time()
        
        print(f"100 sexual reproductions took {end_time - start_time:.4f} seconds")
        
        # Show genome examples
        org = population[0]
        print(f"Sample genome: {org.genome[:16].hex()}")


def run_dual_encoded_evolution_demo():
    """Demonstrate dual-encoded evolution."""
    print("\n=== DUAL-ENCODED EVOLUTION DEMO ===")
    print("Demonstrating evolution of reproduction strategies through dual-encoded genomes")
    print()
    
    # Create dual-encoded organism configuration
    org_config = create_dual_encoded_config(hash_function="blake3")
    
    # Create dual-encoded evolution configuration
    evo_config = EvolutionConfig(
        mode=EvolutionMode.TOURNAMENT,
        pairing_strategy=PairingStrategy.COMPLEMENTARY,
        max_generations=6,
        verbose=True,
        track_strategy_history=True
    )
    
    # Create population
    population = create_initial_population(20, org_config)
    print(f"Created population of {len(population)} dual-encoded organisms")
    
    # Run evolution
    start_time = time.time()
    result = evolutionary_loop(population, simple_sum_fitness, evo_config)
    end_time = time.time()
    
    # Handle result
    if isinstance(result, tuple):
        final_population, strategy_history = result
    else:
        final_population = result
        strategy_history = []
    
    print(f"\nDual-encoded evolution completed in {end_time - start_time:.2f} seconds")
    print(f"Final population size: {len(final_population)}")
    
    if final_population:
        best_organism = max(final_population, key=lambda x: x.fitness)
        print(f"Best fitness: {best_organism.fitness:.4f}")
        print(f"Best organism strategy: {best_organism.get_reproduction_summary()}")


def run_dual_encoding_and_reciprocal_demo():
    """Demonstrate dual encoding and reciprocal reproduction configuration options."""
    print("\n=== DUAL ENCODING & RECIPROCAL REPRODUCTION CONFIG DEMO ===")
    print("Demonstrating boolean configuration options for dual encoding and reciprocal reproduction")
    print()
    
    # Create different configurations
    configs = [
        ("Basic with dual encoding enabled", create_basic_config(
            hash_function="blake3",
            enable_dual_encoding=True,
            enable_reciprocal_reproduction=True
        )),
        ("Basic with dual encoding disabled", create_basic_config(
            hash_function="blake3",
            enable_dual_encoding=False,
            enable_reciprocal_reproduction=True
        )),
        ("Basic with reciprocal reproduction disabled", create_basic_config(
            hash_function="blake3",
            enable_dual_encoding=False,
            enable_reciprocal_reproduction=False
        )),
        ("Basic with both disabled", create_basic_config(
            hash_function="blake3",
            enable_dual_encoding=False,
            enable_reciprocal_reproduction=False
        ))
    ]
    
    for name, config in configs:
        print(f"\n--- {name} ---")
        
        # Create population
        population = create_initial_population(8, config)
        print(f"Created population of {len(population)} organisms")
        
        # Show reproduction strategy
        org = population[0]
        print(f"Reproduction strategy: {org.get_reproduction_summary()}")
        print(f"Dual encoding enabled: {config.enable_dual_encoding}")
        print(f"Reciprocal reproduction enabled: {config.enable_reciprocal_reproduction}")
        
        # Test reproduction
        if len(population) >= 2:
            parent1, parent2 = population[0], population[1]
            
            # Test sexual reproduction
            sexual_children = parent1.reproduce_sexually(parent2)
            print(f"Sexual reproduction produced {len(sexual_children)} children")
            
            # Test general reproduction
            children = parent1.reproduce(parent2)
            print(f"General reproduction produced {len(children)} children")
            
            # Test asexual reproduction
            asexual_children = parent1.reproduce()
            print(f"Asexual reproduction produced {len(asexual_children)} children")


def run_custom_configuration_demo():
    """Demonstrate custom configurations."""
    print("\n=== CUSTOM CONFIGURATION DEMO ===")
    print("Demonstrating custom organism and evolution configurations")
    print()
    
    # Create custom organism configuration
    custom_org_config = OrganismConfig(
        genome_length=128,  # Smaller genome
        hash_function="sha256",
        mode=OrganismMode.BASIC,
        enabled_methods=[ReproductionMethod.SEXUAL, ReproductionMethod.MUTATION],
        combination_strategy="random",
        mutation_masks=[
            bytes([1] * 128),  # Light mutation
            bytes([255] * 128),  # Heavy mutation
        ],
        rotation_positions=[1, -1, 64],
        permutation_maps=[
            list(range(128))[::-1],  # Reverse
            list(range(0, 128, 2)) + list(range(1, 128, 2)),  # Interleave
        ],
        enable_dual_encoding=True,  # Enable dual encoding
        enable_reciprocal_reproduction=False  # Disable reciprocal reproduction
    )
    
    # Create custom evolution configuration
    custom_evo_config = EvolutionConfig(
        mode=EvolutionMode.TOURNAMENT,
        pairing_strategy=PairingStrategy.COMPLEMENTARY,
        max_generations=4,
        population_cap=1000,
        elite_fraction=0.2,
        verbose=True
    )
    
    print("Custom organism configuration:")
    print(f"  Genome length: {custom_org_config.genome_length}")
    print(f"  Hash function: SHA256")
    print(f"  Enabled methods: {[m.value for m in custom_org_config.enabled_methods]}")
    print(f"  Combination strategy: {custom_org_config.combination_strategy}")
    print(f"  Dual encoding enabled: {custom_org_config.enable_dual_encoding}")
    print(f"  Reciprocal reproduction enabled: {custom_org_config.enable_reciprocal_reproduction}")
    
    print("\nCustom evolution configuration:")
    print(f"  Mode: {custom_evo_config.mode.value}")
    print(f"  Pairing strategy: {custom_evo_config.pairing_strategy.value}")
    print(f"  Max generations: {custom_evo_config.max_generations}")
    print(f"  Population cap: {custom_evo_config.population_cap}")
    
    # Test the custom configuration
    population = create_initial_population(15, custom_org_config)
    print(f"\nCreated population of {len(population)} organisms with custom config")
    
    # Run evolution
    start_time = time.time()
    final_population = evolutionary_loop(population, simple_sum_fitness, custom_evo_config)
    end_time = time.time()
    
    print(f"Custom evolution completed in {end_time - start_time:.2f} seconds")
    print(f"Final population size: {len(final_population)}")
    
    if final_population:
        best_organism = max(final_population, key=lambda x: x.fitness)
        print(f"Best fitness: {best_organism.fitness:.4f}")


def run_threading_and_auto_population_demo():
    """Run a demo showcasing threading and auto-population features."""
    print("\n=== Threading and Auto-Population Demo ===")
    
    # Get system info
    import psutil
    cpu_count = psutil.cpu_count()
    memory_gb = psutil.virtual_memory().total / (1024**3)
    
    print(f"System: {cpu_count} CPUs, {memory_gb:.1f}GB RAM")
    
    # Create auto-population configuration
    auto_config = AutoPopulationConfig(
        enabled=True,
        generation_time_target=0.1,  # Target 0.1 seconds per generation for demo
        min_population_size=10,
        max_population_size=1000,
        cull_factor=0.8
    )
    
    # Create configuration with threading and auto-population
    org_config = create_basic_config(genome_length=128)
    evo_config = create_tournament_config(
        max_generations=10,
        population_cap="auto",  # Enable auto-population
        verbose=True,
        thread_count=cpu_count,  # Use all available cores
        auto_population=auto_config
    )
    
    # Create initial population
    population = [
        Organism.from_seed(f"threaded_seed_{i}".encode(), org_config)
        for i in range(50)
    ]
    
    # Generation callback to monitor performance
    def generation_callback(state):
        generation = state['generation']
        population = state['population']
        generation_time = state.get('generation_time', 0)
        thread_count = state['thread_count']
        
        print(f"  Callback: Gen {generation}, Pop {len(population)}, "
              f"Time {generation_time:.2f}s, Threads {thread_count}")
    
    # Run evolution
    start_time = time.time()
    final_population = evolutionary_loop(
        population, 
        simple_sum_fitness, 
        evo_config,
        generation_callback=generation_callback
    )
    total_time = time.time() - start_time
    
    print(f"Total evolution time: {total_time:.2f}s")
    print(f"Final population size: {len(final_population)}")
    if final_population:
        best_fitness = max(org.fitness for org in final_population)
        print(f"Best fitness: {best_fitness:.4f}")
    print()


def main():
    """Main demo function that runs all demonstrations."""
    print("XOF-Genetics Unified Framework Demo")
    print("=" * 60)
    print()
    
    # Set random seed for reproducible results
    random.seed(42)
    
    try:
        # Run all demos
        run_basic_organism_demo()
        run_dual_encoded_organism_demo()
        run_evolution_modes_demo()
        run_hash_function_comparison_demo()
        run_dual_encoded_evolution_demo()
        run_dual_encoding_and_reciprocal_demo()
        run_custom_configuration_demo()
        run_threading_and_auto_population_demo()
        
        print("\n" + "=" * 60)
        print("UNIFIED FRAMEWORK DEMO COMPLETED!")
        print("\nKey features demonstrated:")
        print("- Single unified Organism class with configurable modes")
        print("- Hash-agnostic design supporting BLAKE3 and SHA256")
        print("- Configurable reproduction strategies and methods")
        print("- Multiple evolution modes through configuration")
        print("- Dual-encoded and meta-evolutionary capabilities")
        print("- Boolean flags for dual encoding and reciprocal reproduction")
        print("- Custom configurations for specialized use cases")
        print("\nThe framework now provides a single, configurable interface")
        print("that consolidates all the disparate features into one unified system.")
        
    except Exception as e:
        print(f"Error during demo: {e}")
        print("Make sure you have the required dependencies installed:")
        print("pip install blake3")


if __name__ == "__main__":
    main() 