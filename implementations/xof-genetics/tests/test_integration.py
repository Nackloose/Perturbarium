"""
Integration tests for the complete XOF-Genetics framework.
"""

import pytest
import random
from typing import List

from xof_genetics import (
    Organism, OrganismConfig, OrganismMode, ReproductionMethod,
    EvolutionConfig, EvolutionMode, PairingStrategy,
    evolutionary_loop, analyze_population_strategies,
    create_basic_config, create_dual_encoded_config, create_meta_config,
    create_tournament_config, create_simple_config, create_omni_config,
    create_dual_encoded_config as create_dual_encoded_evolution_config,
    Blake3Hash, SHA256Hash
)


def simple_fitness(organism: Organism) -> float:
    """Simple fitness function for testing."""
    return sum(organism.genome) / len(organism.genome)


def target_fitness(organism: Organism) -> float:
    """Fitness function that rewards organisms closer to a target."""
    target = bytes([128] * len(organism.genome))
    diff = sum(abs(a - b) for a, b in zip(organism.genome, target))
    return 255 * len(organism.genome) - diff


class TestFrameworkIntegration:
    """Test the complete framework integration."""
    
    def test_basic_workflow(self):
        """Test the basic workflow from organism creation to evolution."""
        # Create configuration
        org_config = create_basic_config(genome_length=64)
        evo_config = create_tournament_config(max_generations=5)
        
        # Create initial population
        population = [
            Organism.from_seed(f"seed_{i}".encode(), org_config)
            for i in range(20)
        ]
        
        # Run evolution
        result = evolutionary_loop(population, simple_fitness, evo_config)
        if isinstance(result, tuple):
            final_population, history = result
        else:
            final_population = result
        
        # Verify results
        assert len(final_population) > 0
        assert all(isinstance(org, Organism) for org in final_population)
        # Note: Some organisms might have generation 0 if they're from the initial population
        assert all(org.generation >= 0 for org in final_population)
    
    def test_dual_encoded_workflow(self):
        """Test the dual-encoded workflow."""
        org_config = create_dual_encoded_config(genome_length=64)
        evo_config = EvolutionConfig(
            mode=EvolutionMode.DUAL_ENCODED,
            max_generations=5
        )
        
        population = [
            Organism.from_seed(f"seed_{i}".encode(), org_config)
            for i in range(20)
        ]
        
        result = evolutionary_loop(population, simple_fitness, evo_config)
        if isinstance(result, tuple):
            final_population, history = result
        else:
            final_population = result
        
        assert len(final_population) > 0
        assert all(isinstance(org, Organism) for org in final_population)


class TestHashFunctionIntegration:
    """Test integration with different hash functions."""
    
    def test_sha256_integration(self):
        """Test complete workflow with SHA256."""
        org_config = create_basic_config(hash_function="sha256")
        evo_config = create_tournament_config(max_generations=3)
        
        population = [
            Organism.from_seed(f"seed_{i}".encode(), org_config)
            for i in range(15)
        ]
        
        final_population = evolutionary_loop(population, simple_fitness, evo_config)
        assert len(final_population) > 0
    
    def test_blake3_integration(self):
        """Test complete workflow with BLAKE3."""
        try:
            org_config = create_basic_config(hash_function="blake3")
            evo_config = create_tournament_config(max_generations=3)
            
            population = [
                Organism.from_seed(f"seed_{i}".encode(), org_config)
                for i in range(15)
            ]
            
            final_population = evolutionary_loop(population, simple_fitness, evo_config)
            assert len(final_population) > 0
        except ImportError:
            pytest.skip("blake3 not available")
    
    def test_custom_hash_function_integration(self):
        """Test integration with custom hash function."""
        class CustomHash(SHA256Hash):
            def hash(self, data: bytes, length: int) -> bytes:
                # Custom hash that adds some variation
                base_hash = super().hash(data, length)
                return bytes((b + 1) % 256 for b in base_hash)
        
        org_config = OrganismConfig(hash_function=CustomHash())
        evo_config = create_tournament_config(max_generations=3)
        
        population = [
            Organism.from_seed(f"seed_{i}".encode(), org_config)
            for i in range(15)
        ]
        
        final_population = evolutionary_loop(population, simple_fitness, evo_config)
        assert len(final_population) > 0


class TestConfigurationIntegration:
    """Test integration with different configuration options."""
    
    def test_dual_encoding_flag_integration(self):
        """Test integration with dual encoding flag."""
        # Basic mode with dual encoding enabled
        org_config = create_basic_config(enable_dual_encoding=True)
        evo_config = create_tournament_config(max_generations=3)
        
        population = [
            Organism.from_seed(f"seed_{i}".encode(), org_config)
            for i in range(15)
        ]
        
        final_population = evolutionary_loop(population, simple_fitness, evo_config)
        assert len(final_population) > 0
    
    def test_reciprocal_reproduction_flag_integration(self):
        """Test integration with reciprocal reproduction flag."""
        # Test with reciprocal reproduction disabled
        org_config = create_basic_config(enable_reciprocal_reproduction=False)
        evo_config = create_tournament_config(max_generations=3)
        
        population = [
            Organism.from_seed(f"seed_{i}".encode(), org_config)
            for i in range(15)
        ]
        
        final_population = evolutionary_loop(population, simple_fitness, evo_config)
        assert len(final_population) > 0
    
    def test_custom_reproduction_methods_integration(self):
        """Test integration with custom reproduction methods."""
        org_config = create_basic_config(
            enabled_methods=[ReproductionMethod.SEXUAL, ReproductionMethod.MUTATION]
        )
        evo_config = create_tournament_config(max_generations=3)
        
        population = [
            Organism.from_seed(f"seed_{i}".encode(), org_config)
            for i in range(15)
        ]
        
        final_population = evolutionary_loop(population, simple_fitness, evo_config)
        assert len(final_population) > 0


class TestEvolutionModesIntegration:
    """Test integration with different evolution modes."""
    
    def test_all_evolution_modes(self):
        """Test all evolution modes with the same organism configuration."""
        org_config = create_basic_config()
        
        for mode in EvolutionMode:
            evo_config = EvolutionConfig(mode=mode, max_generations=3)
            
            population = [
                Organism.from_seed(f"seed_{i}".encode(), org_config)
                for i in range(15)
            ]
            
            final_population = evolutionary_loop(population, simple_fitness, evo_config)
            assert len(final_population) > 0
    
    def test_all_pairing_strategies(self):
        """Test all pairing strategies."""
        org_config = create_basic_config()
        
        for strategy in PairingStrategy:
            evo_config = EvolutionConfig(
                pairing_strategy=strategy,
                max_generations=3
            )
            
            population = [
                Organism.from_seed(f"seed_{i}".encode(), org_config)
                for i in range(15)
            ]
            
            final_population = evolutionary_loop(population, simple_fitness, evo_config)
            assert len(final_population) > 0


class TestPopulationAnalysisIntegration:
    """Test population analysis integration."""
    
    def test_population_analysis_with_evolution(self):
        """Test population analysis during evolution."""
        org_config = create_basic_config()
        evo_config = EvolutionConfig(
            max_generations=3,
            track_strategy_history=True
        )
        
        population = [
            Organism.from_seed(f"seed_{i}".encode(), org_config)
            for i in range(20)
        ]
        
        final_population, history = evolutionary_loop(population, simple_fitness, evo_config)
        
        # Analyze final population
        analysis = analyze_population_strategies(final_population)
        assert analysis['total_organisms'] == len(final_population)
        assert 'strategy_counts' in analysis
        assert 'genome_variation' in analysis
    
    def test_population_analysis_different_modes(self):
        """Test population analysis with different organism modes."""
        for mode in OrganismMode:
            if mode == OrganismMode.BASIC:
                org_config = create_basic_config()
            elif mode == OrganismMode.DUAL_ENCODED:
                org_config = create_dual_encoded_config()
            elif mode == OrganismMode.META:
                org_config = create_meta_config()
            
            population = [
                Organism.from_seed(f"seed_{i}".encode(), org_config)
                for i in range(15)
            ]
            
            analysis = analyze_population_strategies(population)
            assert analysis['total_organisms'] == len(population)


class TestFitnessFunctionIntegration:
    """Test integration with different fitness functions."""
    
    def test_different_fitness_functions(self):
        """Test evolution with different fitness functions."""
        org_config = create_basic_config()
        evo_config = create_tournament_config(max_generations=3)
        
        fitness_functions = [simple_fitness, target_fitness]
        
        for fitness_func in fitness_functions:
            population = [
                Organism.from_seed(f"seed_{i}".encode(), org_config)
                for i in range(15)
            ]
            
            final_population = evolutionary_loop(population, fitness_func, evo_config)
            assert len(final_population) > 0
    
    def test_fitness_improvement_tracking(self):
        """Test tracking fitness improvement over generations."""
        org_config = create_basic_config()
        evo_config = EvolutionConfig(
            max_generations=5,
            track_strategy_history=True
        )
        
        population = [
            Organism.from_seed(f"seed_{i}".encode(), org_config)
            for i in range(20)
        ]
        
        final_population, history = evolutionary_loop(population, target_fitness, evo_config)
        
        # Verify history structure
        assert len(history) > 0
        for entry in history:
            assert 'generation' in entry
            assert 'population_size' in entry
            assert 'best_fitness' in entry
            assert 'avg_fitness' in entry


class TestErrorHandlingIntegration:
    """Test error handling in the integrated framework."""
    
    def test_invalid_fitness_function(self):
        """Test handling of invalid fitness function."""
        org_config = create_basic_config()
        evo_config = create_tournament_config(max_generations=3)
        
        population = [
            Organism.from_seed(f"seed_{i}".encode(), org_config)
            for i in range(10)
        ]
        
        def invalid_fitness(organism):
            raise ValueError("Invalid fitness function")
        
        with pytest.raises(ValueError):
            evolutionary_loop(population, invalid_fitness, evo_config)
    
    def test_empty_population(self):
        """Test handling of empty population."""
        org_config = create_basic_config()
        evo_config = create_tournament_config(max_generations=3)
        
        population = []
        
        with pytest.raises(ValueError):
            evolutionary_loop(population, simple_fitness, evo_config)
    
    def test_single_organism_population(self):
        """Test handling of single organism population."""
        org_config = create_basic_config()
        evo_config = create_tournament_config(max_generations=3)
        
        population = [Organism.from_seed(b"single_seed", org_config)]
        
        final_population = evolutionary_loop(population, simple_fitness, evo_config)
        assert len(final_population) > 0


class TestPerformanceIntegration:
    """Test performance characteristics of the integrated framework."""
    
    @pytest.mark.slow
    def test_large_population_performance(self):
        """Test performance with large population."""
        org_config = create_basic_config(genome_length=128)
        evo_config = EvolutionConfig(
            max_generations=5,
            population_cap=100
        )
        
        population = [
            Organism.from_seed(f"seed_{i}".encode(), org_config)
            for i in range(100)
        ]
        
        final_population = evolutionary_loop(population, simple_fitness, evo_config)
        assert len(final_population) > 0
    
    @pytest.mark.slow
    def test_long_evolution_performance(self):
        """Test performance with long evolution."""
        org_config = create_basic_config()
        evo_config = EvolutionConfig(
            max_generations=10,
            population_cap=50
        )
        
        population = [
            Organism.from_seed(f"seed_{i}".encode(), org_config)
            for i in range(50)
        ]
        
        final_population = evolutionary_loop(population, simple_fitness, evo_config)
        assert len(final_population) > 0 