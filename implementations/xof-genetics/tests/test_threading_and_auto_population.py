"""
Tests for threading and auto-population features.
"""

import pytest
import time
import psutil
from xof_genetics import (
    Organism, create_basic_config, create_tournament_config,
    AutoPopulationConfig, evolutionary_loop
)


def simple_fitness(organism):
    """Simple fitness function for testing."""
    return sum(organism.genome) / len(organism.genome)


class TestThreadingFeatures:
    """Test threading functionality."""
    
    def test_threaded_fitness_evaluation(self):
        """Test that fitness evaluation works with multiple threads."""
        org_config = create_basic_config(genome_length=64)
        evo_config = create_tournament_config(
            max_generations=3,
            thread_count=4,
            verbose=False
        )
        
        population = [
            Organism.from_seed(f"thread_test_{i}".encode(), org_config)
            for i in range(20)
        ]
        
        # Run evolution with threading
        final_population = evolutionary_loop(population, simple_fitness, evo_config)
        
        assert len(final_population) > 0
        # All organisms should have fitness values
        for org in final_population:
            assert hasattr(org, 'fitness')
            assert isinstance(org.fitness, (int, float))
    
    def test_threaded_reproduction(self):
        """Test that reproduction works with multiple threads."""
        org_config = create_basic_config(genome_length=64)
        evo_config = create_tournament_config(
            max_generations=2,
            thread_count=2,
            verbose=False
        )
        
        population = [
            Organism.from_seed(f"repro_test_{i}".encode(), org_config)
            for i in range(10)
        ]
        
        # Run evolution with threaded reproduction
        final_population = evolutionary_loop(population, simple_fitness, evo_config)
        
        assert len(final_population) > 0
    
    def test_thread_count_validation(self):
        """Test that thread count is properly validated."""
        org_config = create_basic_config(genome_length=64)
        
        # Test with zero threads (should default to 1)
        evo_config = create_tournament_config(thread_count=0)
        assert evo_config.thread_count == 1
        
        # Test with negative threads (should default to 1)
        evo_config = create_tournament_config(thread_count=-1)
        assert evo_config.thread_count == 1
        
        # Test with valid thread count
        evo_config = create_tournament_config(thread_count=4)
        assert evo_config.thread_count == 4


class TestAutoPopulationFeatures:
    """Test auto-population sizing functionality."""
    
    def test_auto_population_config_creation(self):
        """Test auto-population configuration creation."""
        auto_config = AutoPopulationConfig(
            enabled=True,
            generation_time_target=1.0,
            min_population_size=5,
            max_population_size=1000,
            cull_factor=0.7
        )
        
        assert auto_config.enabled is True
        assert auto_config.generation_time_target == 1.0
        assert auto_config.min_population_size == 5
        assert auto_config.max_population_size == 1000
        assert auto_config.cull_factor == 0.7
    
    def test_auto_population_default_values(self):
        """Test that auto-population has correct default values."""
        auto_config = AutoPopulationConfig()
        
        assert auto_config.enabled is False
        assert auto_config.generation_time_target == 1.5  # Default should be 1.5 seconds
        assert auto_config.min_population_size == 10
        assert auto_config.max_population_size == 100000
        assert auto_config.cull_factor == 0.8
    
    def test_auto_population_string_config(self):
        """Test that 'auto' population_cap enables auto-population."""
        org_config = create_basic_config(genome_length=64)
        evo_config = create_tournament_config(
            max_generations=3,
            population_cap="auto",
            verbose=False
        )
        
        assert evo_config.auto_population.enabled is True
        assert evo_config.population_cap == evo_config.auto_population.max_population_size
    
    def test_auto_population_disabled_by_default(self):
        """Test that auto-population is disabled by default."""
        evo_config = create_tournament_config()
        assert evo_config.auto_population.enabled is False
    
    def test_auto_population_with_custom_config(self):
        """Test auto-population with custom configuration."""
        auto_config = AutoPopulationConfig(
            enabled=True,
            generation_time_target=0.1,  # Very short target (0.1 seconds) to trigger culling
            min_population_size=5,
            max_population_size=100,
            cull_factor=0.5
        )
        
        org_config = create_basic_config(genome_length=64)
        evo_config = create_tournament_config(
            max_generations=3,
            verbose=False,
            auto_population=auto_config
        )
        
        population = [
            Organism.from_seed(f"auto_test_{i}".encode(), org_config)
            for i in range(20)
        ]
        
        # Run evolution - should trigger auto-population culling
        final_population = evolutionary_loop(population, simple_fitness, evo_config)
        
        assert len(final_population) > 0
        # Population should be within auto-population bounds
        assert len(final_population) >= auto_config.min_population_size
        assert len(final_population) <= auto_config.max_population_size


class TestGenerationCallback:
    """Test generation callback functionality."""
    
    def test_generation_callback_called(self):
        """Test that generation callback is called with correct data."""
        callback_called = False
        callback_data = {}
        
        def generation_callback(state):
            nonlocal callback_called, callback_data
            callback_called = True
            callback_data = state
        
        org_config = create_basic_config(genome_length=64)
        evo_config = create_tournament_config(
            max_generations=2,
            verbose=False
        )
        
        population = [
            Organism.from_seed(f"callback_test_{i}".encode(), org_config)
            for i in range(10)
        ]
        
        evolutionary_loop(population, simple_fitness, evo_config, generation_callback)
        
        assert callback_called is True
        assert 'generation' in callback_data
        assert 'population' in callback_data
        assert 'config' in callback_data
        assert 'thread_count' in callback_data
    
    def test_generation_callback_with_threading(self):
        """Test generation callback with threading enabled."""
        callback_count = 0
        
        def generation_callback(state):
            nonlocal callback_count
            callback_count += 1
            assert 'thread_count' in state
            assert state['thread_count'] == 2
        
        org_config = create_basic_config(genome_length=64)
        evo_config = create_tournament_config(
            max_generations=3,
            thread_count=2,
            verbose=False
        )
        
        population = [
            Organism.from_seed(f"callback_thread_test_{i}".encode(), org_config)
            for i in range(10)
        ]
        
        evolutionary_loop(population, simple_fitness, evo_config, generation_callback)
        
        # Should be called once per generation
        assert callback_count == 3


class TestPerformanceFeatures:
    """Test performance-related features."""
    
    def test_generation_time_tracking(self):
        """Test that generation time is tracked in history."""
        org_config = create_basic_config(genome_length=64)
        evo_config = create_tournament_config(
            max_generations=2,
            track_strategy_history=True,
            verbose=False
        )
        
        population = [
            Organism.from_seed(f"time_test_{i}".encode(), org_config)
            for i in range(10)
        ]
        
        final_population, history = evolutionary_loop(population, simple_fitness, evo_config)
        
        assert len(history) == 2
        for entry in history:
            assert 'generation_time' in entry
            assert isinstance(entry['generation_time'], float)
            assert entry['generation_time'] >= 0
    
    def test_auto_population_performance_adaptation(self):
        """Test that auto-population adapts based on performance."""
        auto_config = AutoPopulationConfig(
            enabled=True,
            generation_time_target=0.05,  # Very short target (0.05 seconds)
            min_population_size=3,
            max_population_size=50,
            cull_factor=0.5
        )
        
        org_config = create_basic_config(genome_length=128)  # Larger genome for slower processing
        evo_config = create_tournament_config(
            max_generations=3,
            verbose=True,  # Enable verbose to see auto-population messages
            auto_population=auto_config
        )
        
        population = [
            Organism.from_seed(f"perf_test_{i}".encode(), org_config)
            for i in range(20)
        ]
        
        final_population = evolutionary_loop(population, simple_fitness, evo_config)
        
        assert len(final_population) > 0
        # Population should be within bounds
        assert len(final_population) >= auto_config.min_population_size
        assert len(final_population) <= auto_config.max_population_size


@pytest.mark.limit
def test_large_scale_threading():
    """Test threading with larger populations."""
    cpu_count = psutil.cpu_count()
    
    org_config = create_basic_config(genome_length=256)
    evo_config = create_tournament_config(
        max_generations=3,
        thread_count=cpu_count,
        verbose=False
    )
    
    population = [
        Organism.from_seed(f"large_thread_{i}".encode(), org_config)
        for i in range(100)
    ]
    
    start_time = time.time()
    final_population = evolutionary_loop(population, simple_fitness, evo_config)
    elapsed_time = time.time() - start_time
    
    assert len(final_population) > 0
    print(f"Large scale threading test: {elapsed_time:.2f}s with {cpu_count} threads") 