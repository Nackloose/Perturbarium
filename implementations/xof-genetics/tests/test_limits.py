import pytest
import time
import psutil
import gc
import os
from xof_genetics import (
    Organism, create_basic_config, create_tournament_config, create_omni_config, evolutionary_loop, AutoPopulationConfig
)

def fitness(organism):
    """Dynamic fitness function that creates more interesting evolution."""
    genome = organism.genome
    genome_length = len(genome)
    
    # Multiple fitness components for complex landscape
    base_sum = sum(genome)
    base_fitness = base_sum / genome_length
    
    # Pattern matching - reward specific byte patterns
    pattern_score = 0
    for i in range(genome_length - 3):
        # Reward ascending sequences
        if genome[i] < genome[i+1] < genome[i+2] < genome[i+3]:
            pattern_score += 1
        # Reward alternating patterns
        if genome[i] == genome[i+2] and genome[i+1] == genome[i+3]:
            pattern_score += 0.5
    
    # Position-based scoring - different positions have different weights
    position_weights = [1.0 + (i % 10) / 10.0 for i in range(genome_length)]
    weighted_sum = sum(genome[i] * position_weights[i] for i in range(genome_length))
    weighted_fitness = weighted_sum / sum(position_weights)
    
    # Entropy bonus - reward diverse genomes
    unique_bytes = len(set(genome))
    diversity_bonus = unique_bytes / genome_length
    
    # Combine all components
    total_fitness = (base_fitness * 0.3 + 
                    pattern_score * 0.3 + 
                    weighted_fitness * 0.3 + 
                    diversity_bonus * 0.1)
    
    return total_fitness

@pytest.mark.limit
def test_large_population():
    """Test with a large population and moderate generations."""
    org_config = create_basic_config(genome_length=256)
    evo_config = create_tournament_config(max_generations=5, population_cap=5000)
    population = [Organism.from_seed(f"seed_{i}".encode(), org_config) for i in range(5000)]
    start = time.time()
    final_population = evolutionary_loop(population, fitness, evo_config)
    elapsed = time.time() - start
    assert len(final_population) > 0
    print(f"Large population test completed in {elapsed:.2f} seconds")

@pytest.mark.limit
def test_limit_genome_size():
    """Test with a very large genome size."""
    org_config = create_basic_config(genome_length=4096)
    evo_config = create_tournament_config(max_generations=3, population_cap=100)
    population = [Organism.from_seed(f"seed_{i}".encode(), org_config) for i in range(100)]
    start = time.time()
    final_population = evolutionary_loop(population, fitness, evo_config)
    elapsed = time.time() - start
    assert len(final_population) > 0
    print(f"Large genome test completed in {elapsed:.2f} seconds")

@pytest.mark.limit
def test_limit_generations():
    """Test with a high number of generations."""
    org_config = create_basic_config(genome_length=128)
    evo_config = create_tournament_config(max_generations=100, population_cap=200)
    population = [Organism.from_seed(f"seed_{i}".encode(), org_config) for i in range(200)]
    start = time.time()
    final_population = evolutionary_loop(population, fitness, evo_config)
    elapsed = time.time() - start
    assert len(final_population) > 0
    print(f"High generation test completed in {elapsed:.2f} seconds")

@pytest.mark.full_loop
def test_full_loop_soak():
    """Full loop soak test: very large population, genome, and generations."""
    org_config = create_basic_config(genome_length=1024)
    evo_config = create_tournament_config(max_generations=200, population_cap=2000)
    population = [Organism.from_seed(f"seed_{i}".encode(), org_config) for i in range(2000)]
    start = time.time()
    final_population = evolutionary_loop(population, fitness, evo_config)
    elapsed = time.time() - start
    assert len(final_population) > 0
    print(f"Full loop soak test completed in {elapsed:.2f} seconds")

import concurrent.futures

@pytest.mark.extreme
def test_extreme_server_load():
    """
    Extreme test designed for dedicated server hardware.
    This test will consume significant amounts of memory and CPU.
    Now threaded to take advantage of server cores with auto-population.
    """
    print("Starting extreme server load test...")

    # Get system info
    process = psutil.Process()
    memory_gb = psutil.virtual_memory().total / (1024**3)
    cpu_count = psutil.cpu_count()

    print(f"System: {memory_gb:.1f}GB RAM, {cpu_count} CPUs")

    # Extreme parameters - start with just 2 organisms and let omni-reproduction explode
    genome_length = min(2048, int(memory_gb * 50))  # Max 2048 bytes, scale with memory
    population_size = 2  # Start with just 2 organisms
    max_generations = min(100, int(cpu_count * 5))  # Max 100 generations, scale with CPU

    print(f"Parameters: genome={genome_length}, pop={population_size}, gens={max_generations}")

    # Create smart auto-population configuration with tracking
    auto_config = AutoPopulationConfig(
        enabled=True,
        generation_time_target=2.0,  # Target 2.0 seconds per generation
        min_population_size=2,  # Allow down to 2 organisms
        max_population_size=int(memory_gb * 1000),  # Allow massive growth
        cull_factor=0.05  # Cull 95% of population when over target time
        # Smart tracking fields will be automatically initialized
    )

    # Create extreme configuration with threading and auto-population
    org_config = create_basic_config(genome_length=genome_length)
    evo_config = create_omni_config(
        max_generations=max_generations,
        population_cap="auto",  # Enable auto-population
        verbose=True,
        thread_count=cpu_count,  # Use all available cores
        auto_population=auto_config
    )

    # Create massive population in parallel
    print(f"Creating population of {population_size} organisms...")

    def create_organism(i):
        if i % 2000 == 0 and i != 0:
            print(f"  Created {i}/{population_size} organisms")
        return Organism.from_seed(f"extreme_seed_{i}".encode(), org_config)

    population = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=cpu_count) as executor:
        # Use list to force evaluation and progress reporting
        futures = {executor.submit(create_organism, i): i for i in range(population_size)}
        for idx, future in enumerate(concurrent.futures.as_completed(futures)):
            organism = future.result()
            population.append(organism)
            # Print progress every 2000
            if (idx + 1) % 2000 == 0:
                print(f"  Created {idx + 1}/{population_size} organisms")

    # Monitor memory usage
    initial_memory = process.memory_info().rss / (1024**3)
    print(f"Initial memory usage: {initial_memory:.2f}GB")

    # Define a generation callback to print information every generation
    def generation_callback(state):
        # Print generation number and best fitness
        generation = state['generation']
        population = state['population']
        generation_time = state.get('generation_time', 0)
        thread_count = state['thread_count']
        
        if population:
            best_fitness = max(org.fitness for org in population)
            avg_fitness = sum(org.fitness for org in population) / len(population)
            fitness_range = max(org.fitness for org in population) - min(org.fitness for org in population)
            
            print(f"  Generation {generation}: pop={len(population)}, best={best_fitness:.4f}, "
                  f"avg={avg_fitness:.4f}, range={fitness_range:.4f}, "
                  f"time={generation_time:.2f}s, threads={thread_count}")

    # Run extreme evolution
    print("Starting extreme evolution...")
    start_time = time.time()

    try:
        # Pass the generation_callback to evolutionary_loop
        final_population = evolutionary_loop(
            population, 
            fitness, 
            evo_config,
            generation_callback=generation_callback
        )
        elapsed_time = time.time() - start_time

        final_memory = process.memory_info().rss / (1024**3)
        memory_used = final_memory - initial_memory

        print(f"Extreme test completed!")
        print(f"  Time: {elapsed_time:.2f} seconds")
        print(f"  Memory used: {memory_used:.2f}GB")
        print(f"  Final population: {len(final_population)}")
        print(f"  Operations/second: {(population_size * max_generations) / elapsed_time:.0f}")

        assert len(final_population) > 0
        assert elapsed_time > 0

    except MemoryError:
        print("Memory limit reached during extreme test")
        raise
    except Exception as e:
        print(f"Extreme test failed: {e}")
        raise


@pytest.mark.fill_resources
def test_fill_resources_scale_to_limit():
    """
    Scale up test parameters until hitting memory or CPU limits,
    then run the test loop 100 times with threading and auto-population.
    """
    print("Starting resource fill test...")
    
    process = psutil.Process()
    initial_memory = process.memory_info().rss / (1024**3)
    memory_gb = psutil.virtual_memory().total / (1024**3)
    cpu_count = psutil.cpu_count()
    
    print(f"System: {memory_gb:.1f}GB RAM, {cpu_count} CPUs")
    print(f"Initial memory: {initial_memory:.2f}GB")
    
    # Start with small parameters and let omni-reproduction explode
    base_genome_length = 256
    base_population_size = 2  # Start with just 2 organisms
    base_generations = 5
    
    # Scale up until we hit limits (more conservative scaling)
    scale_factor = 1
    max_scale_factor = int(min(memory_gb * 2, cpu_count * 20))  # More conservative upper bound
    
    print("Scaling up parameters to find system limits...")
    
    while scale_factor <= max_scale_factor:
        genome_length = min(2048, base_genome_length * scale_factor)  # Max 2048 bytes
        population_size = base_population_size * scale_factor
        generations = min(100, base_generations * scale_factor)  # Max 100 generations
        
        print(f"  Testing scale factor {scale_factor}: genome={genome_length}, pop={population_size}, gens={generations}")
        
        try:
            # Test if we can create the population
            org_config = create_basic_config(genome_length=genome_length)
            test_population = []
            
            # Try to create a small test population first
            for i in range(min(100, population_size)):
                test_population.append(Organism.from_seed(f"test_seed_{i}".encode(), org_config))
            
            # Check memory usage
            current_memory = process.memory_info().rss / (1024**3)
            memory_used = current_memory - initial_memory
            
            # If we're using more than 70% of available memory, stop scaling
            if memory_used > memory_gb * 0.7:
                print(f"  Memory limit reached at scale factor {scale_factor}")
                break
            
            # Create auto-population configuration for testing with aggressive culling
            auto_config = AutoPopulationConfig(
                enabled=True,
                generation_time_target=2.0,  # Target 2.0 seconds per generation
                min_population_size=2,  # Allow down to 2 organisms
                max_population_size=population_size * 10,  # Allow massive growth
                cull_factor=0.05  # Cull 95% of population when over target time
            )
            
            # Try a quick evolution test with threading and auto-population
            evo_config = create_omni_config(
                max_generations=min(3, generations),
                population_cap="auto",
                verbose=False,
                thread_count=cpu_count,
                auto_population=auto_config
            )
            
            test_result = evolutionary_loop(test_population, fitness, evo_config)
            
            # If successful, continue scaling
            scale_factor += 1
            
            # Clean up test population
            del test_population
            del test_result
            gc.collect()
            
        except MemoryError:
            print(f"  Memory limit reached at scale factor {scale_factor}")
            break
        except Exception as e:
            print(f"  Other limit reached at scale factor {scale_factor}: {e}")
            break
    
    # Use the last successful scale factor
    final_scale_factor = max(1, scale_factor - 1)
    final_genome_length = min(2048, base_genome_length * final_scale_factor)
    final_population_size = base_population_size * final_scale_factor
    final_generations = min(100, base_generations * final_scale_factor)
    
    print(f"Final parameters: genome={final_genome_length}, pop={final_population_size}, gens={final_generations}")
    
    # Create final auto-population configuration with aggressive culling
    final_auto_config = AutoPopulationConfig(
        enabled=True,
        generation_time_target=2.0,  # Target 2.0 seconds per generation
        min_population_size=2,  # Allow down to 2 organisms
        max_population_size=final_population_size * 10,  # Allow massive growth
        cull_factor=0.05  # Cull 95% of population when over target time
    )
    
    # Run the test loop 100 times
    print("Running test loop 100 times with threading and auto-population...")
    
    total_time = 0
    total_memory_used = 0
    successful_runs = 0
    
    for run in range(100):
        try:
            # Create fresh population for each run
            org_config = create_basic_config(genome_length=final_genome_length)
            population = []
            
            for i in range(final_population_size):
                population.append(Organism.from_seed(f"run_{run}_seed_{i}".encode(), org_config))
            
            # Monitor memory
            run_start_memory = process.memory_info().rss / (1024**3)
            run_start_time = time.time()
            
            # Run evolution with threading and auto-population
            evo_config = create_omni_config(
                max_generations=final_generations,
                population_cap="auto",
                verbose=False,
                thread_count=cpu_count,
                auto_population=final_auto_config
            )
            
            final_population = evolutionary_loop(population, fitness, evo_config)
            
            run_end_time = time.time()
            run_end_memory = process.memory_info().rss / (1024**3)
            
            run_time = run_end_time - run_start_time
            run_memory = run_end_memory - run_start_memory
            
            total_time += run_time
            total_memory_used += run_memory
            successful_runs += 1
            
            if run % 10 == 0:
                print(f"  Run {run+1}/100: {run_time:.2f}s, {run_memory:.2f}GB, final_pop={len(final_population)}")
            
            # Clean up
            del population
            del final_population
            gc.collect()
            
        except Exception as e:
            print(f"  Run {run+1} failed: {e}")
            break
    
    # Report results
    print(f"Resource fill test completed!")
    print(f"  Successful runs: {successful_runs}/100")
    print(f"  Average time per run: {total_time/successful_runs:.2f}s")
    print(f"  Average memory per run: {total_memory_used/successful_runs:.2f}GB")
    print(f"  Total time: {total_time:.2f}s")
    print(f"  Total memory used: {total_memory_used:.2f}GB")
    
    assert successful_runs > 0
    assert total_time > 0

@pytest.mark.extreme
def test_memory_stress_test():
    """
    Memory stress test that creates and destroys large populations rapidly.
    Now with threading and auto-population.
    """
    print("Starting memory stress test...")
    
    process = psutil.Process()
    memory_gb = psutil.virtual_memory().total / (1024**3)
    cpu_count = psutil.cpu_count()
    
    # Create smart auto-population configuration with tracking
    auto_config = AutoPopulationConfig(
        enabled=True,
        generation_time_target=2.0,  # Target 2.0 seconds per generation
        min_population_size=2,  # Allow down to 2 organisms
        max_population_size=int(memory_gb * 1000),  # Allow massive growth
        cull_factor=0.05  # Cull 95% of population when over target time
        # Smart tracking fields will be automatically initialized
    )
    
    # Create large populations and destroy them rapidly
    for cycle in range(20):  # Reduced from 50 cycles
        print(f"Memory stress cycle {cycle+1}/20")
        
        # Create large population with more reasonable parameters
        genome_length = min(2048, int(memory_gb * 20))  # Max 2048 bytes, scale with memory
        population_size = int(memory_gb * 50)  # More reasonable population size
        
        org_config = create_basic_config(genome_length=genome_length)
        population = []
        
        for i in range(population_size):
            population.append(Organism.from_seed(f"stress_seed_{cycle}_{i}".encode(), org_config))
        
        # Run quick evolution with threading and auto-population
        evo_config = create_omni_config(
            max_generations=2, 
            population_cap="auto",
            verbose=False,
            thread_count=cpu_count,
            auto_population=auto_config
        )
        final_population = evolutionary_loop(population, fitness, evo_config)
        
        # Force garbage collection
        del population
        del final_population
        gc.collect()
        
        # Check memory usage
        current_memory = process.memory_info().rss / (1024**3)
        print(f"  Cycle {cycle+1} memory: {current_memory:.2f}GB")
        
        # If memory usage is too high, break
        if current_memory > memory_gb * 0.8:
            print(f"  Memory limit reached at cycle {cycle+1}")
            break
    
    print("Memory stress test completed!") 