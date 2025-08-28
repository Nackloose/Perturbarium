"""
Unified Evolution module for XOF-Genetics framework.

This module provides a single evolutionary_loop function that can operate in
different modes (tournament, simple, omni, dual-encoded, meta) through
configuration, eliminating the need for separate evolution functions.

Features:
- Full threading support for all operations (hashing, pairing, mating)
- Auto population sizing with time targets
- Generation callbacks for monitoring and control
- Parallel fitness evaluation and reproduction
"""

import random
import time
import threading
from typing import List, Callable, Optional, Dict, Any, Union, Tuple
from enum import Enum
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass

from .organism import Organism, OrganismConfig, OrganismMode


class PairingStrategy(Enum):
    """Strategies for pairing organisms for reproduction."""
    RANDOM = "random"
    ELITE_VS_ELITE = "elite_vs_elite"
    ELITE_VS_CHALLENGER = "elite_vs_challenger"
    COMPLEMENTARY = "complementary"


class EvolutionMode(Enum):
    """Different evolution modes."""
    TOURNAMENT = "tournament"  # Intergenerational tournaments
    SIMPLE = "simple"  # Simple selection and reproduction
    OMNI = "omni"  # Omni-reproduction for maximum diversity
    DUAL_ENCODED = "dual_encoded"  # Dual-encoded evolution


@dataclass
class AutoPopulationConfig:
    """Configuration for auto population sizing."""
    enabled: bool = False
    generation_time_target: float = 1.5  # Target time per generation in seconds
    min_population_size: int = 10
    max_population_size: int = 100000
    cull_factor: float = 0.8  # Reduce population by this factor when over target time
    
    # Smart tracking for optimal population size
    optimal_population_size: Optional[int] = None  # Best size found so far
    optimal_generation_time: Optional[float] = None  # Time for optimal size
    initial_population_time: Optional[float] = None  # Time for initial population
    max_safe_population: Optional[int] = None  # Largest population that stayed under target
    
    # Binary search state for finding sweet spot
    ceiling_population: Optional[int] = None  # First size that exceeded target time
    binary_search_low: Optional[int] = None  # Lower bound for binary search
    binary_search_high: Optional[int] = None  # Upper bound for binary search
    binary_search_mid: Optional[int] = None  # Current test point in binary search
    binary_search_phase: str = "explore"  # "explore", "binary_search", "adapt", "fine_tune", "locked"
    
    # Oscillation detection for fine-tuning
    oscillation_history: List[int] = None  # Track recent population sizes
    oscillation_threshold: int = 3  # Number of oscillations before fine-tuning
    fine_tune_low: Optional[int] = None  # Lower bound for fine-tuning
    fine_tune_high: Optional[int] = None  # Upper bound for fine-tuning
    
    def __post_init__(self):
        if self.oscillation_history is None:
            self.oscillation_history = []


class EvolutionConfig:
    """Configuration class for evolution behavior."""
    
    def __init__(self,
                 mode: EvolutionMode = EvolutionMode.TOURNAMENT,
                 pairing_strategy: PairingStrategy = PairingStrategy.RANDOM,
                 max_generations: int = 10,
                 population_cap: Union[int, str] = 1000,
                 elite_fraction: float = 0.1,
                 selection_pressure: float = 0.5,
                 verbose: bool = False,
                 track_strategy_history: bool = False,
                 thread_count: int = 1,
                 auto_population: Optional[AutoPopulationConfig] = None):
        """
        Initialize evolution configuration.
        
        Args:
            mode: Evolution mode to use
            pairing_strategy: Strategy for pairing organisms
            max_generations: Maximum number of generations
            population_cap: Maximum population size before culling (or "auto" for auto-sizing)
            elite_fraction: Fraction of population to keep when culling
            selection_pressure: Selection pressure for simple evolution
            verbose: Whether to print progress information
            track_strategy_history: Whether to track strategy evolution (for dual/meta modes)
            thread_count: Number of threads to use for all operations
            auto_population: Auto population sizing configuration
        """
        self.mode = mode
        self.pairing_strategy = pairing_strategy
        self.max_generations = max_generations
        self.population_cap = population_cap
        self.elite_fraction = elite_fraction
        self.selection_pressure = selection_pressure
        self.verbose = verbose
        self.track_strategy_history = track_strategy_history
        self.thread_count = max(1, thread_count)
        
        # Auto population configuration
        if auto_population is None:
            auto_population = AutoPopulationConfig()
        self.auto_population = auto_population
        
        # If population_cap is "auto", enable auto population sizing
        if population_cap == "auto":
            self.auto_population.enabled = True
            self.population_cap = auto_population.max_population_size
    
    def copy(self) -> 'EvolutionConfig':
        """Create a copy of this configuration."""
        return EvolutionConfig(
            mode=self.mode,
            pairing_strategy=self.pairing_strategy,
            max_generations=self.max_generations,
            population_cap=self.population_cap,
            elite_fraction=self.elite_fraction,
            selection_pressure=self.selection_pressure,
            verbose=self.verbose,
            track_strategy_history=self.track_strategy_history,
            thread_count=self.thread_count,
            auto_population=self.auto_population
        )


def threaded_fitness_evaluation(population: List[Organism], 
                              fitness_func: Callable[[Organism], float],
                              thread_count: int) -> None:
    """Evaluate fitness for all organisms in parallel."""
    if thread_count == 1 or len(population) < 2:
        for organism in population:
            organism.fitness = fitness_func(organism)
    else:
        def set_fitness(org):
            org.fitness = fitness_func(org)
            return org

        with ThreadPoolExecutor(max_workers=thread_count) as executor:
            futures = {executor.submit(set_fitness, org): org for org in population}
            for future in as_completed(futures):
                future.result()  # Ensures exceptions are raised if any


def threaded_intergenerational_tournament(parent1: Organism, parent2: Organism, 
                                        fitness_func: Callable[[Organism], float]) -> List[Organism]:
    """Threaded version of intergenerational tournament."""
    return intergenerational_tournament(parent1, parent2, fitness_func)


def intergenerational_tournament(parent1: Organism, parent2: Organism, 
                               fitness_func: Callable[[Organism], float]) -> List[Organism]:
    """
    Conducts an intergenerational tournament between parents and their offspring.
    
    This tournament creates direct competitive dynamics between parents and their
    offspring, driving rapid evolutionary improvement through generational pressure.
    
    Args:
        parent1: First parent organism
        parent2: Second parent organism
        fitness_func: Function to evaluate organism fitness
    
    Returns:
        List of surviving organisms from the tournament
    """
    
    # Generate child pair
    children = parent1.reproduce_sexually(parent2)
    if len(children) == 2:
        child1, child2 = children[0], children[1]
    elif len(children) == 1:
        child1 = children[0]
        child2 = None
    else:
        child1 = child2 = None
    
    # Evaluate fitness for all participants
    parent1.fitness = fitness_func(parent1)
    parent2.fitness = fitness_func(parent2)
    if child1:
        child1.fitness = fitness_func(child1)
    if child2:
        child2.fitness = fitness_func(child2)
    
    # Sibling combat - determine champion child
    champion_child = None
    if child1 and child2:
        champion_child = child1 if child1.fitness > child2.fitness else child2
    elif child1:
        champion_child = child1
    elif child2:
        champion_child = child2

    # Parent-child challenges - parents survive if they beat the champion child
    parent1_survives = parent1.fitness > (champion_child.fitness if champion_child else float('-inf'))
    parent2_survives = parent2.fitness > (champion_child.fitness if champion_child else float('-inf'))

    # Return survivors - this allows population growth when children are better
    survivors = []
    if parent1_survives:
        survivors.append(parent1)
    if parent2_survives:
        survivors.append(parent2)
    if champion_child:
        survivors.append(champion_child)  # Champion child always survives
    return survivors


def threaded_pair_organisms(organisms: List[Organism], 
                          strategy: PairingStrategy,
                          thread_count: int) -> List[Tuple[Organism, Organism]]:
    """Threaded version of organism pairing."""
    return pair_organisms(organisms, strategy)


def pair_organisms(organisms: List[Organism], strategy: PairingStrategy) -> List[Tuple[Organism, Organism]]:
    """
    Pairs organisms according to the specified strategy.
    
    Args:
        organisms: List of organisms to pair
        strategy: Pairing strategy to use
    
    Returns:
        List of organism pairs for reproduction
    """
    if len(organisms) < 2:
        return []
    
    organisms_copy = organisms.copy()
    
    if strategy == PairingStrategy.RANDOM:
        random.shuffle(organisms_copy)
        pairs = []
        for i in range(0, len(organisms_copy) - 1, 2):
            pairs.append((organisms_copy[i], organisms_copy[i + 1]))
        return pairs
    
    elif strategy == PairingStrategy.ELITE_VS_ELITE:
        # Sort by fitness (descending) and pair top with top
        organisms_copy.sort(key=lambda x: x.fitness, reverse=True)
        pairs = []
        for i in range(0, len(organisms_copy) - 1, 2):
            pairs.append((organisms_copy[i], organisms_copy[i + 1]))
        return pairs
    
    elif strategy == PairingStrategy.ELITE_VS_CHALLENGER:
        # Sort by fitness and pair top with bottom
        organisms_copy.sort(key=lambda x: x.fitness, reverse=True)
        pairs = []
        mid = len(organisms_copy) // 2
        for i in range(mid):
            if i + mid < len(organisms_copy):
                pairs.append((organisms_copy[i], organisms_copy[i + mid]))
        return pairs
    
    elif strategy == PairingStrategy.COMPLEMENTARY:
        # Sort by fitness and pair 1st with last, 2nd with second-to-last, etc.
        organisms_copy.sort(key=lambda x: x.fitness, reverse=True)
        pairs = []
        for i in range(len(organisms_copy) // 2):
            pairs.append((organisms_copy[i], organisms_copy[-(i + 1)]))
        return pairs
    
    return []


def threaded_handle_odd_organism(organism: Organism, thread_count: int) -> List[Organism]:
    """Threaded version of handling odd organisms."""
    return handle_odd_organism(organism)


def handle_odd_organism(organism: Organism) -> List[Organism]:
    """
    Handles an unpaired organism through asexual self-reproduction.
    
    This ensures that valuable genetic material is not lost while maintaining
    the dual offspring principle.
    
    Args:
        organism: The unpaired organism
    
    Returns:
        List of children from asexual self-reproduction
    """
    return organism.asexual_self_reproduction()


def threaded_analyze_population_strategies(population: List[Organism], 
                                         thread_count: int) -> Dict[str, Any]:
    """Threaded version of population strategy analysis."""
    return analyze_population_strategies(population)


def analyze_population_strategies(population: List[Organism]) -> Dict[str, Any]:
    """
    Analyze the reproduction strategies in the current population.
    
    Args:
        population: List of organisms
    
    Returns:
        Dictionary containing strategy analysis
    """
    analysis = {
        'total_organisms': len(population),
        'strategy_counts': {},
        'method_usage': {},
        'diversity': 0.0,
        'avg_methods_enabled': 0.0,
        'genome_variation': 0.0,
    }
    
    if not population:
        return analysis
    
    # Count different strategies
    strategies = []
    method_counts = {}
    total_methods = 0
    
    for organism in population:
        strategy = organism.reproduction_strategy
        strategy_key = f"{strategy['combination_strategy']}_{len(strategy['enabled_methods'])}"
        strategies.append(strategy_key)
        
        # Count method usage
        for method in strategy['enabled_methods']:
            method_name = method.value
            method_counts[method_name] = method_counts.get(method_name, 0) + 1
            total_methods += 1
    
    # Count strategy frequencies
    strategy_counts = {}
    for strategy in strategies:
        strategy_counts[strategy] = strategy_counts.get(strategy, 0) + 1
    
    analysis['strategy_counts'] = strategy_counts
    analysis['method_usage'] = method_counts
    analysis['avg_methods_enabled'] = total_methods / len(population) if population else 0
    
    # Calculate diversity (count of unique strategies)
    if strategy_counts:
        analysis['diversity'] = len(strategy_counts)
    else:
        analysis['diversity'] = 0
    
    # Calculate genome variation (how different genomes are)
    if len(population) > 1:
        genome_hashes = [hash(org.genome) for org in population]
        unique_hashes = len(set(genome_hashes))
        analysis['genome_variation'] = unique_hashes / len(population)
    
    return analysis


def adjust_population_size(current_size: int, generation_time: float, 
                          config: EvolutionConfig, pre_reproduction_size: Optional[int] = None) -> int:
    """
    Smart population size adjustment using binary search to find the sweet spot.
    
    Args:
        current_size: Current population size (after reproduction)
        generation_time: Time taken for the last generation
        config: Evolution configuration
        pre_reproduction_size: Population size before reproduction (for tracking safe sizes)
    
    Returns:
        New target population size
    """
    if not config.auto_population.enabled:
        return current_size
    
    auto_config = config.auto_population
    target_time = auto_config.generation_time_target
    min_size = auto_config.min_population_size
    
    # Use pre-reproduction size for tracking if available, otherwise use current size
    tracking_size = pre_reproduction_size if pre_reproduction_size is not None else current_size
    
    # Track initial population time if not set
    if auto_config.initial_population_time is None:
        auto_config.initial_population_time = generation_time
        if config.verbose:
            print(f"  Auto-population: Initial population time set to {generation_time:.2f}s")
    
    # Track optimal population size (fastest generation time)
    if (auto_config.optimal_generation_time is None or 
        generation_time < auto_config.optimal_generation_time):
        auto_config.optimal_population_size = tracking_size
        auto_config.optimal_generation_time = generation_time
        if config.verbose:
            print(f"  Auto-population: New optimal size {tracking_size} with time {generation_time:.2f}s")
    
    # Phase 1: Exploration - find the ceiling (first size that exceeds target time)
    if auto_config.binary_search_phase == "explore":
        if generation_time <= target_time:
            # Still under target, can grow more
            if (auto_config.max_safe_population is None or 
                tracking_size > auto_config.max_safe_population):
                auto_config.max_safe_population = tracking_size
                if config.verbose:
                    print(f"  Auto-population: Exploration - new safe size {tracking_size} with time {generation_time:.2f}s")
            
            # Try to grow by 50% for next generation
            growth_factor = 1.5
            new_size = min(auto_config.max_population_size, int(tracking_size * growth_factor))
            if config.verbose:
                print(f"  Auto-population: Exploration - growing from {tracking_size} to {new_size}")
            return new_size
        else:
            # Found the ceiling! Start binary search
            auto_config.ceiling_population = tracking_size
            auto_config.binary_search_low = auto_config.max_safe_population or min_size
            auto_config.binary_search_high = tracking_size
            auto_config.binary_search_phase = "binary_search"
            
            if config.verbose:
                print(f"  Auto-population: Found ceiling at {tracking_size} (time: {generation_time:.2f}s)")
                print(f"  Auto-population: Starting binary search between {auto_config.binary_search_low} and {auto_config.binary_search_high}")
            
            # Start binary search at midpoint
            auto_config.binary_search_mid = (auto_config.binary_search_low + auto_config.binary_search_high) // 2
            return auto_config.binary_search_mid
    
    # Phase 2: Binary search - find the sweet spot between safe and ceiling
    elif auto_config.binary_search_phase == "binary_search":
        if generation_time <= target_time:
            # Current size is safe, move low bound up
            auto_config.binary_search_low = tracking_size
            if (auto_config.max_safe_population is None or 
                tracking_size > auto_config.max_safe_population):
                auto_config.max_safe_population = tracking_size
                if config.verbose:
                    print(f"  Auto-population: Binary search - new safe size {tracking_size}")
        else:
            # Current size is too slow, move high bound down
            auto_config.binary_search_high = tracking_size
            if config.verbose:
                print(f"  Auto-population: Binary search - {tracking_size} too slow ({generation_time:.2f}s)")
        
        # Check if binary search is complete (converged)
        if auto_config.binary_search_high - auto_config.binary_search_low <= 1:
            # Binary search complete, use the safe size
            auto_config.binary_search_phase = "adapt"
            sweet_spot = auto_config.max_safe_population or auto_config.binary_search_low
            if config.verbose:
                print(f"  Auto-population: Binary search complete! Sweet spot: {sweet_spot}")
            return sweet_spot
        
        # Continue binary search
        auto_config.binary_search_mid = (auto_config.binary_search_low + auto_config.binary_search_high) // 2
        if config.verbose:
            print(f"  Auto-population: Binary search - testing {auto_config.binary_search_mid} (range: {auto_config.binary_search_low}-{auto_config.binary_search_high})")
        return auto_config.binary_search_mid
    
    # Phase 3: Adaptation - adjust based on performance
    elif auto_config.binary_search_phase == "adapt":
        # Track oscillation history
        auto_config.oscillation_history.append(tracking_size)
        
        # Keep only recent history (last 10 entries)
        if len(auto_config.oscillation_history) > 10:
            auto_config.oscillation_history = auto_config.oscillation_history[-10:]
        
        # Check for oscillation pattern (alternating between two values)
        if len(auto_config.oscillation_history) >= 6:
            recent = auto_config.oscillation_history[-6:]
            unique_values = list(set(recent))
            if len(unique_values) == 2 and recent.count(unique_values[0]) >= 2 and recent.count(unique_values[1]) >= 2:
                # Oscillation detected! Start fine-tuning
                auto_config.fine_tune_low = min(unique_values)
                auto_config.fine_tune_high = max(unique_values)
                auto_config.binary_search_phase = "fine_tune"
                
                if config.verbose:
                    print(f"  Auto-population: Oscillation detected between {auto_config.fine_tune_low} and {auto_config.fine_tune_high}")
                    print(f"  Auto-population: Starting fine-tuning binary search")
                
                # Start fine-tuning at midpoint
                fine_tune_mid = (auto_config.fine_tune_low + auto_config.fine_tune_high) // 2
                return fine_tune_mid
        
        if generation_time <= target_time:
            # Performance is good, can try to grow slightly
            if auto_config.max_safe_population is not None:
                # Calculate how much headroom we have
                headroom = target_time - generation_time
                headroom_percent = headroom / target_time
                
                # If we have significant headroom (>10%), try growing more aggressively
                if headroom_percent > 0.1:
                    # Try growing by 20% from current safe size
                    growth_factor = 1.2
                    new_size = min(auto_config.max_population_size, int(auto_config.max_safe_population * growth_factor))
                    if config.verbose:
                        print(f"  Auto-population: Adaptation - significant headroom ({headroom_percent:.1%}), growing from {tracking_size} to {new_size}")
                    return new_size
                else:
                    # Small headroom, try growing by 5%
                    growth_factor = 1.05
                    new_size = min(auto_config.max_population_size, int(auto_config.max_safe_population * growth_factor))
                    if config.verbose:
                        print(f"  Auto-population: Adaptation - small headroom ({headroom_percent:.1%}), growing from {tracking_size} to {new_size}")
                    return new_size
            else:
                return tracking_size
        else:
            # Performance degraded, fall back to safe size
            safe_size = auto_config.max_safe_population or min_size
            if config.verbose:
                print(f"  Auto-population: Adaptation - performance degraded, falling back to safe size {safe_size}")
            return safe_size
    
    # Phase 4: Fine-tuning - binary search in oscillation range
    elif auto_config.binary_search_phase == "fine_tune":
        if generation_time <= target_time:
            # Current size is safe, move low bound up
            auto_config.fine_tune_low = tracking_size
            if (auto_config.max_safe_population is None or 
                tracking_size > auto_config.max_safe_population):
                auto_config.max_safe_population = tracking_size
                if config.verbose:
                    print(f"  Auto-population: Fine-tuning - new safe size {tracking_size} (time: {generation_time:.2f}s)")
        else:
            # Current size is too slow, move high bound down
            auto_config.fine_tune_high = tracking_size
            if config.verbose:
                print(f"  Auto-population: Fine-tuning - {tracking_size} too slow ({generation_time:.2f}s)")
        
        # Check if fine-tuning is complete (converged)
        if auto_config.fine_tune_high - auto_config.fine_tune_low <= 1:
            # Fine-tuning complete, transition to locked phase
            auto_config.binary_search_phase = "locked"
            optimal_size = auto_config.max_safe_population or auto_config.fine_tune_low
            if config.verbose:
                print(f"  Auto-population: Fine-tuning complete! Optimal size locked at {optimal_size}")
                print(f"  Auto-population: Entering locked phase with performance monitoring")
            return optimal_size
        
        # Continue fine-tuning binary search
        fine_tune_mid = (auto_config.fine_tune_low + auto_config.fine_tune_high) // 2
        if config.verbose:
            print(f"  Auto-population: Fine-tuning - testing {fine_tune_mid} (range: {auto_config.fine_tune_low}-{auto_config.fine_tune_high})")
        return fine_tune_mid
    
    # Phase 5: Locked - maintain optimal size with performance monitoring
    elif auto_config.binary_search_phase == "locked":
        if generation_time > target_time:
            # Performance degraded, fall back to safe size
            safe_size = auto_config.max_safe_population or min_size
            if config.verbose:
                print(f"  Auto-population: Locked - performance degraded, falling back to safe size {safe_size}")
            return safe_size
        else:
            # Calculate how much headroom we have
            headroom = target_time - generation_time
            headroom_percent = headroom / target_time
            
            # If we have significant headroom (>15%), try growing more
            if headroom_percent > 0.15:
                # Try growing by 10% from current size
                growth_factor = 1.1
                new_size = min(auto_config.max_population_size, int(tracking_size * growth_factor))
                if config.verbose:
                    print(f"  Auto-population: Locked - significant headroom ({headroom_percent:.1%}), trying {new_size}")
                return new_size
            else:
                # Performance is good, maintain current size
                if config.verbose:
                    print(f"  Auto-population: Locked - optimal performance ({headroom_percent:.1%} headroom)")
                return tracking_size
    
    # Fallback
    return current_size


def evolutionary_loop(
    initial_population: List[Organism], 
    fitness_func: Callable[[Organism], float],
    config: Optional[EvolutionConfig] = None,
    generation_callback: Optional[Callable[[Dict[str, Any]], None]] = None
) -> Union[List[Organism], Tuple[List[Organism], List[Dict[str, Any]]]]:
    """
    Unified evolutionary loop supporting all evolution modes with full threading support.
    Supports a generation_callback called with the current state every generation.

    Args:
        initial_population: Starting population of organisms
        fitness_func: Function to evaluate organism fitness
        config: Evolution configuration (optional, uses defaults if not provided)
        generation_callback: Optional callback called each generation with a dict containing
            {
                'generation': int,
                'population': List[Organism],
                'history_entry': Dict[str, Any],
                'history': List[Dict[str, Any]],
                'config': EvolutionConfig,
                'generation_time': float,
                'thread_count': int,
            }

    Returns:
        Final population after evolution, and optionally strategy history
    """

    if config is None:
        config = EvolutionConfig()

    population = initial_population.copy()
    best_organism_ever = None
    best_fitness_ever = float('-inf')
    history = []
    thread_count = config.thread_count

    for generation in range(1, config.max_generations + 1):
        generation_start_time = time.time()
        
        if config.verbose:
            print(f"Generation {generation}: Population size = {len(population)}")

        # Evaluate fitness for all organisms in parallel
        threaded_fitness_evaluation(population, fitness_func, thread_count)

        # Track the best organism ever seen
        current_best = max(population, key=lambda x: x.fitness)
        if current_best.fitness > best_fitness_ever:
            best_fitness_ever = current_best.fitness
            best_organism_ever = current_best

        # Analyze population characteristics if tracking strategy history
        # Always append a history entry with required keys
        best_fitness = max(org.fitness for org in population)
        avg_fitness = sum(org.fitness for org in population) / len(population)
        history_entry = {
            'generation': generation,
            'population_size': len(population),
            'best_fitness': best_fitness,
            'avg_fitness': avg_fitness,
        }
        # Optionally add more keys if strategy tracking is enabled
        if config.track_strategy_history:
            analysis = threaded_analyze_population_strategies(population, thread_count)
            history_entry.update(analysis)
        history.append(history_entry)

        if config.verbose:
            if config.track_strategy_history:
                print(f"  Population diversity: {analysis['diversity']:.2f}")
                print(f"  Genome variation: {analysis['genome_variation']:.2f}")
            else:
                print(f"  Population size: {len(population)}")
                print(f"  Best fitness: {best_fitness:.4f}")

        # Call generation_callback if provided (after fitness evaluation, before reproduction)
        if generation_callback is not None:
            callback_state = {
                'generation': generation,
                'population': population,  # Current population with evaluated fitness values
                'history_entry': history_entry,
                'history': history,
                'config': config,
                'thread_count': thread_count,
            }
            generation_callback(callback_state)

        # Track population size BEFORE reproduction for smart auto-population
        pre_reproduction_size = len(population)

        # Conduct reproduction based on evolution mode (all threaded)
        new_population = []

        if config.mode == EvolutionMode.TOURNAMENT:
            new_population = threaded_tournament_reproduction(population, fitness_func, config)

        elif config.mode == EvolutionMode.SIMPLE:
            new_population = threaded_simple_reproduction(population, config)

        elif config.mode == EvolutionMode.OMNI:
            new_population = threaded_omni_reproduction(population, config)

        elif config.mode == EvolutionMode.DUAL_ENCODED:
            new_population = threaded_dual_encoded_reproduction(population, config)

        else:
            raise ValueError(f"Unknown evolution mode: {config.mode}")

        # Ensure the best organism ever is always in the population (elitism)
        if best_organism_ever and best_organism_ever not in new_population:
            # Add the best organism ever to the population (don't replace, add)
            new_population.append(best_organism_ever)

        # Update population
        population = new_population

        # Check if population needs to be capped AFTER reproduction
        if len(population) > config.population_cap:
            if config.verbose:
                print(f"  Population cap reached ({len(population)} > {config.population_cap}), keeping top {int(len(population) * config.elite_fraction)}")

            # Sort by fitness and keep top elite fraction
            population.sort(key=lambda x: x.fitness, reverse=True)
            elite_size = max(1, int(len(population) * config.elite_fraction))
            population = population[:elite_size]

            if config.verbose:
                print(f"  Population reduced to {len(population)} elite organisms")

        # Calculate generation time and adjust population size if auto-sizing is enabled
        generation_time = time.time() - generation_start_time
        history_entry['generation_time'] = generation_time
        
        if config.auto_population.enabled:
            target_size = adjust_population_size(len(population), generation_time, config, pre_reproduction_size)
            if target_size != len(population):
                # Adjust population to target size
                if target_size < len(population):
                    # Cull population to target size
                    population.sort(key=lambda x: x.fitness, reverse=True)
                    population = population[:target_size]
                    if config.verbose:
                        print(f"  Auto-culled population to {len(population)} organisms")
                else:
                    # Grow population to target size (add copies of best organisms)
                    population.sort(key=lambda x: x.fitness, reverse=True)
                    while len(population) < target_size:
                        # Add copies of the best organisms
                        best_organism = population[0]
                        population.append(best_organism.copy())
                    if config.verbose:
                        print(f"  Auto-grown population to {len(population)} organisms")

        # Print best fitness
        if population and config.verbose:
            best_fitness = max(org.fitness for org in population)
            print(f"  Best fitness: {best_fitness:.4f} (Generation time: {generation_time:.2f}s)")

    # Return appropriate result based on whether strategy history was tracked
    if config.track_strategy_history:
        return population, history
    else:
        return population


def threaded_tournament_reproduction(population: List[Organism], 
                                   fitness_func: Callable[[Organism], float],
                                   config: EvolutionConfig) -> List[Organism]:
    """Threaded tournament-based reproduction."""
    new_population = []
    thread_count = config.thread_count
    
    # Pair organisms for reproduction
    pairs = threaded_pair_organisms(population, config.pairing_strategy, thread_count)
    
    # Conduct intergenerational tournaments in parallel
    if thread_count == 1 or len(pairs) < 2:
        for parent1, parent2 in pairs:
            survivors = threaded_intergenerational_tournament(parent1, parent2, fitness_func)
            new_population.extend(survivors)
    else:
        def tournament_worker(pair):
            parent1, parent2 = pair
            return threaded_intergenerational_tournament(parent1, parent2, fitness_func)
        
        with ThreadPoolExecutor(max_workers=thread_count) as executor:
            futures = {executor.submit(tournament_worker, pair): pair for pair in pairs}
            for future in as_completed(futures):
                survivors = future.result()
                new_population.extend(survivors)
    
    # Handle any unpaired organisms in parallel
    paired_indices = set()
    for parent1, parent2 in pairs:
        paired_indices.add(population.index(parent1))
        paired_indices.add(population.index(parent2))
    
    unpaired_organisms = [organism for i, organism in enumerate(population) if i not in paired_indices]
    
    if unpaired_organisms:
        if thread_count == 1 or len(unpaired_organisms) < 2:
            for organism in unpaired_organisms:
                children = threaded_handle_odd_organism(organism, thread_count)
                new_population.extend(children)
        else:
            def odd_organism_worker(organism):
                return threaded_handle_odd_organism(organism, thread_count)
            
            with ThreadPoolExecutor(max_workers=thread_count) as executor:
                futures = {executor.submit(odd_organism_worker, org): org for org in unpaired_organisms}
                for future in as_completed(futures):
                    children = future.result()
                    new_population.extend(children)
    
    return new_population


def threaded_simple_reproduction(population: List[Organism], config: EvolutionConfig) -> List[Organism]:
    """Threaded simple selection and reproduction."""
    new_population = []
    thread_count = config.thread_count
    
    # Sort by fitness
    population.sort(key=lambda x: x.fitness, reverse=True)
    
    # Select top performers for reproduction
    num_parents = max(2, int(len(population) * config.selection_pressure))
    parents = population[:num_parents]
    
    # Generate new population through sexual reproduction in parallel
    target_size = len(population)
    
    def reproduction_worker():
        children = []
        while len(children) < target_size // thread_count + 1:
            # Randomly select two parents
            parent1, parent2 = random.sample(parents, 2)
            child_batch = parent1.reproduce_sexually(parent2)
            children.extend(child_batch)
        return children
    
    if thread_count == 1:
        new_population = reproduction_worker()
    else:
        with ThreadPoolExecutor(max_workers=thread_count) as executor:
            futures = [executor.submit(reproduction_worker) for _ in range(thread_count)]
            for future in as_completed(futures):
                children = future.result()
                new_population.extend(children)
    
    # Trim to target size
    if len(new_population) > target_size:
        new_population = new_population[:target_size]
    
    return new_population


def threaded_omni_reproduction(population: List[Organism], config: EvolutionConfig) -> List[Organism]:
    """Threaded omni-reproduction for maximum genetic diversity."""
    new_population = []
    thread_count = config.thread_count
    
    # Pair organisms for reproduction
    pairs = threaded_pair_organisms(population, config.pairing_strategy, thread_count)
    
    # Conduct omni-reproduction for each pair in parallel
    if thread_count == 1 or len(pairs) < 2:
        for parent1, parent2 in pairs:
            # Use omni_reproduce to generate comprehensive offspring
            children = parent1.omni_reproduce(parent2)
            new_population.extend(children)
    else:
        def omni_reproduction_worker(pair):
            parent1, parent2 = pair
            return parent1.omni_reproduce(parent2)
        
        with ThreadPoolExecutor(max_workers=thread_count) as executor:
            futures = {executor.submit(omni_reproduction_worker, pair): pair for pair in pairs}
            for future in as_completed(futures):
                children = future.result()
                new_population.extend(children)
    
    # Handle any unpaired organisms in parallel
    paired_indices = set()
    for parent1, parent2 in pairs:
        paired_indices.add(population.index(parent1))
        paired_indices.add(population.index(parent2))
    
    unpaired_organisms = [organism for i, organism in enumerate(population) if i not in paired_indices]
    
    if unpaired_organisms:
        if thread_count == 1 or len(unpaired_organisms) < 2:
            for organism in unpaired_organisms:
                children = organism.omni_reproduce(organism)
                new_population.extend(children)
        else:
            def unpaired_omni_worker(organism):
                return organism.omni_reproduce(organism)
            
            with ThreadPoolExecutor(max_workers=thread_count) as executor:
                futures = {executor.submit(unpaired_omni_worker, org): org for org in unpaired_organisms}
                for future in as_completed(futures):
                    children = future.result()
                    new_population.extend(children)
    
    return new_population


def threaded_dual_encoded_reproduction(population: List[Organism], config: EvolutionConfig) -> List[Organism]:
    """Threaded dual-encoded reproduction."""
    new_population = []
    thread_count = config.thread_count
    
    # Pair organisms for reproduction
    pairs = threaded_pair_organisms(population, config.pairing_strategy, thread_count)
    
    # Conduct dual-encoded reproduction for each pair in parallel
    if thread_count == 1 or len(pairs) < 2:
        for parent1, parent2 in pairs:
            # Use reproduce method which will use dual-encoded strategy
            children = parent1.reproduce(parent2)
            new_population.extend(children)
    else:
        def dual_encoded_reproduction_worker(pair):
            parent1, parent2 = pair
            return parent1.reproduce(parent2)
        
        with ThreadPoolExecutor(max_workers=thread_count) as executor:
            futures = {executor.submit(dual_encoded_reproduction_worker, pair): pair for pair in pairs}
            for future in as_completed(futures):
                children = future.result()
                new_population.extend(children)
    
    # Handle any unpaired organisms in parallel
    paired_indices = set()
    for parent1, parent2 in pairs:
        paired_indices.add(population.index(parent1))
        paired_indices.add(population.index(parent2))
    
    unpaired_organisms = [organism for i, organism in enumerate(population) if i not in paired_indices]
    
    if unpaired_organisms:
        if thread_count == 1 or len(unpaired_organisms) < 2:
            for organism in unpaired_organisms:
                children = organism.reproduce()  # No partner = self-reproduction
                new_population.extend(children)
        else:
            def unpaired_dual_encoded_worker(organism):
                return organism.reproduce()  # No partner = self-reproduction
            
            with ThreadPoolExecutor(max_workers=thread_count) as executor:
                futures = {executor.submit(unpaired_dual_encoded_worker, org): org for org in unpaired_organisms}
                for future in as_completed(futures):
                    children = future.result()
                    new_population.extend(children)
    
    return new_population


# Convenience functions for creating common evolution configurations
def create_tournament_config(pairing_strategy: PairingStrategy = PairingStrategy.RANDOM,
                           max_generations: int = 10,
                           population_cap: Union[int, str] = 1000,
                           elite_fraction: float = 0.1,
                           verbose: bool = False,
                           thread_count: int = 1,
                           auto_population: Optional[AutoPopulationConfig] = None,
                           **kwargs) -> EvolutionConfig:
    """Create a tournament evolution configuration."""
    return EvolutionConfig(
        mode=EvolutionMode.TOURNAMENT,
        pairing_strategy=pairing_strategy,
        max_generations=max_generations,
        population_cap=population_cap,
        elite_fraction=elite_fraction,
        verbose=verbose,
        thread_count=thread_count,
        auto_population=auto_population,
        **kwargs
    )


def create_simple_config(pairing_strategy: PairingStrategy = PairingStrategy.RANDOM,
                        max_generations: int = 10,
                        selection_pressure: float = 0.5,
                        verbose: bool = False,
                        thread_count: int = 1,
                        auto_population: Optional[AutoPopulationConfig] = None,
                        **kwargs) -> EvolutionConfig:
    """Create a simple evolution configuration."""
    return EvolutionConfig(
        mode=EvolutionMode.SIMPLE,
        pairing_strategy=pairing_strategy,
        max_generations=max_generations,
        selection_pressure=selection_pressure,
        verbose=verbose,
        thread_count=thread_count,
        auto_population=auto_population,
        **kwargs
    )


def create_omni_config(pairing_strategy: PairingStrategy = PairingStrategy.RANDOM,
                      max_generations: int = 10,
                      population_cap: Union[int, str] = 1000,
                      elite_fraction: float = 0.1,
                      verbose: bool = False,
                      thread_count: int = 1,
                      auto_population: Optional[AutoPopulationConfig] = None,
                      **kwargs) -> EvolutionConfig:
    """Create an omni-reproduction evolution configuration."""
    return EvolutionConfig(
        mode=EvolutionMode.OMNI,
        pairing_strategy=pairing_strategy,
        max_generations=max_generations,
        population_cap=population_cap,
        elite_fraction=elite_fraction,
        verbose=verbose,
        thread_count=thread_count,
        auto_population=auto_population,
        **kwargs
    )


def create_dual_encoded_config(pairing_strategy: PairingStrategy = PairingStrategy.RANDOM,
                              max_generations: int = 10,
                              population_cap: Union[int, str] = 1000,
                              elite_fraction: float = 0.1,
                              verbose: bool = False,
                              track_strategy_history: bool = True,
                              thread_count: int = 1,
                              auto_population: Optional[AutoPopulationConfig] = None,
                              **kwargs) -> EvolutionConfig:
    """Create a dual-encoded evolution configuration."""
    return EvolutionConfig(
        mode=EvolutionMode.DUAL_ENCODED,
        pairing_strategy=pairing_strategy,
        max_generations=max_generations,
        population_cap=population_cap,
        elite_fraction=elite_fraction,
        verbose=verbose,
        track_strategy_history=track_strategy_history,
        thread_count=thread_count,
        auto_population=auto_population,
        **kwargs
    )


# Legacy function names for backward compatibility
def simple_evolutionary_loop(initial_population: List[Organism],
                           fitness_func: Callable[[Organism], float],
                           selection_pressure: float = 0.5,
                           max_generations: int = 100,
                           verbose: bool = True) -> List[Organism]:
    """Legacy simple evolutionary loop for backward compatibility."""
    config = create_simple_config(
        max_generations=max_generations,
        selection_pressure=selection_pressure,
        verbose=verbose
    )
    return evolutionary_loop(initial_population, fitness_func, config)


def omni_evolutionary_loop(initial_population: List[Organism], 
                          fitness_func: Callable[[Organism], float],
                          pairing_strategy: PairingStrategy = PairingStrategy.RANDOM,
                          max_generations: int = 100,
                          verbose: bool = True) -> List[Organism]:
    """Legacy omni evolutionary loop for backward compatibility."""
    config = create_omni_config(
        pairing_strategy=pairing_strategy,
        max_generations=max_generations,
        verbose=verbose
    )
    return evolutionary_loop(initial_population, fitness_func, config) 