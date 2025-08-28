"""
Tests for the Organism class and related functionality.
"""

import pytest
import random
from typing import List

from xof_genetics.organism import (
    Organism, OrganismConfig, OrganismMode, ReproductionMethod,
    HashFunction, Blake3Hash, SHA256Hash,
    create_basic_config, create_dual_encoded_config, create_meta_config
)


class TestOrganismConfig:
    """Test OrganismConfig class."""
    
    def test_basic_config_creation(self):
        """Test creating a basic organism configuration."""
        config = OrganismConfig()
        assert config.genome_length == 256
        assert config.mode == OrganismMode.BASIC
        assert config.combination_strategy == "all"
        assert config.enable_dual_encoding is False
        assert config.enable_reciprocal_reproduction is True
        assert len(config.enabled_methods) > 0
        assert len(config.mutation_masks) > 0
        assert len(config.rotation_positions) > 0
        assert len(config.permutation_maps) > 0
    
    def test_custom_config_creation(self):
        """Test creating a custom organism configuration."""
        config = OrganismConfig(
            genome_length=128,
            hash_function="sha256",
            mode=OrganismMode.DUAL_ENCODED,
            enable_dual_encoding=True,
            enable_reciprocal_reproduction=False
        )
        assert config.genome_length == 128
        assert config.mode == OrganismMode.DUAL_ENCODED
        assert config.enable_dual_encoding is True
        assert config.enable_reciprocal_reproduction is False
        assert isinstance(config.hash_function, SHA256Hash)
    
    def test_config_copy(self):
        """Test copying a configuration."""
        config = OrganismConfig(genome_length=64)
        config_copy = config.copy()
        assert config_copy.genome_length == 64
        assert config_copy is not config
        assert config_copy.enabled_methods is not config.enabled_methods
    
    def test_invalid_hash_function(self):
        """Test that invalid hash function raises error."""
        with pytest.raises(ValueError, match="Unknown hash function"):
            OrganismConfig(hash_function="invalid_hash")


class TestHashFunctions:
    """Test hash function implementations."""
    
    def test_sha256_hash(self):
        """Test SHA256 hash function."""
        hash_func = SHA256Hash()
        data = b"test data"
        result = hash_func.hash(data, 32)
        assert len(result) == 32
        assert isinstance(result, bytes)
        # Same input should produce same output
        result2 = hash_func.hash(data, 32)
        assert result == result2
    
    def test_blake3_hash(self):
        """Test BLAKE3 hash function."""
        try:
            hash_func = Blake3Hash()
            data = b"test data"
            result = hash_func.hash(data, 32)
            assert len(result) == 32
            assert isinstance(result, bytes)
            # Same input should produce same output
            result2 = hash_func.hash(data, 32)
            assert result == result2
        except ImportError:
            pytest.skip("blake3 not available")
    
    def test_hash_function_interface(self):
        """Test that hash functions implement the interface correctly."""
        hash_func = SHA256Hash()
        assert hasattr(hash_func, 'hash')
        assert callable(hash_func.hash)


class TestOrganism:
    """Test Organism class."""
    
    def test_organism_creation(self):
        """Test creating an organism."""
        config = create_basic_config()
        organism = Organism.from_seed(b"test_seed", config)
        assert organism.genome is not None
        assert len(organism.genome) == config.genome_length
        assert organism.config == config
        assert organism.generation == 0
        assert organism.fitness == 0.0
    
    def test_organism_creation_with_meta_genome(self):
        """Test creating an organism with meta-genome."""
        config = create_meta_config()
        organism = Organism.from_seed(b"test_seed", config)
        assert organism.genome is not None
        assert organism.meta_genome is not None
        assert len(organism.meta_genome) == config.meta_genome_length
    
    def test_organism_repr(self):
        """Test organism string representation."""
        config = create_basic_config()
        organism = Organism.from_seed(b"test_seed", config)
        repr_str = repr(organism)
        assert "Organism" in repr_str
        assert str(organism.generation) in repr_str
    
    def test_organism_equality(self):
        """Test organism equality."""
        config = create_basic_config()
        org1 = Organism.from_seed(b"seed1", config)
        org2 = Organism.from_seed(b"seed2", config)
        org3 = Organism.from_seed(b"seed1", config)
        
        assert org1 != org2
        assert org1 == org3
    
    def test_organism_hash(self):
        """Test organism hashability."""
        config = create_basic_config()
        org1 = Organism.from_seed(b"seed1", config)
        org2 = Organism.from_seed(b"seed2", config)
        
        # Should be able to use as dict key
        org_dict = {org1: "org1", org2: "org2"}
        assert org_dict[org1] == "org1"
        assert org_dict[org2] == "org2"


class TestBasicReproduction:
    """Test basic reproduction methods."""
    
    def test_direct_asexual_reproduction(self):
        """Test direct asexual reproduction."""
        parent = Organism.from_seed(b"test_seed", create_basic_config())
        children = parent.direct_asexual_reproduction()
        
        assert len(children) == 1
        child = children[0]
        assert child is not parent
        assert child.genome != parent.genome
        assert child.generation == parent.generation + 1
    
    def test_asexual_self_reproduction(self):
        """Test asexual self-reproduction."""
        parent = Organism.from_seed(b"test_seed", create_basic_config())
        children = parent.asexual_self_reproduction()
        
        assert len(children) == 2
        assert all(isinstance(child, Organism) for child in children)
        assert all(child.genome != parent.genome for child in children)
        assert all(child.generation == parent.generation + 1 for child in children)
    
    def test_sexual_reproduction_reciprocal(self):
        """Test sexual reproduction with reciprocal children."""
        config = create_basic_config(enable_reciprocal_reproduction=True)
        parent1 = Organism.from_seed(b"parent1", config)
        parent2 = Organism.from_seed(b"parent2", config)
        
        children = parent1.reproduce_sexually(parent2)
        assert len(children) == 2
        
        child1, child2 = children
        assert child1.genome != child2.genome
        assert child1.generation == parent1.generation + 1
        assert child2.generation == parent2.generation + 1
    
    def test_sexual_reproduction_single(self):
        """Test sexual reproduction with single child."""
        config = create_basic_config(enable_reciprocal_reproduction=False)
        parent1 = Organism.from_seed(b"parent1", config)
        parent2 = Organism.from_seed(b"parent2", config)
        
        children = parent1.reproduce_sexually(parent2)
        assert len(children) == 1
        
        child = children[0]
        assert child.generation == max(parent1.generation, parent2.generation) + 1
    
    def test_mutation(self):
        """Test mutation reproduction."""
        config = create_basic_config()
        parent = Organism.from_seed(b"parent_seed", config)
        mutation_mask = bytes([1] * config.genome_length)
        children = parent.mutate(mutation_mask)
        
        assert len(children) == 1
        child = children[0]
        assert child is not parent
        assert child.genome != parent.genome
        assert child.generation == parent.generation + 1
    
    def test_rotation(self):
        """Test rotation reproduction."""
        config = create_basic_config()
        parent = Organism.from_seed(b"parent_seed", config)
        children = parent.rotate(1)
        
        assert len(children) == 1
        child = children[0]
        assert child is not parent
        assert child.genome != parent.genome
        assert child.generation == parent.generation + 1
    
    def test_permutation(self):
        """Test permutation reproduction."""
        config = create_basic_config()
        parent = Organism.from_seed(b"parent_seed", config)
        perm_map = list(range(config.genome_length))
        children = parent.permute(perm_map)
        
        assert len(children) == 1
        child = children[0]
        assert child is not parent
        assert child.genome != parent.genome
        assert child.generation == parent.generation + 1


class TestDualEncodedReproduction:
    """Test dual-encoded reproduction methods."""
    
    def test_dual_encoded_self_reproduction(self):
        """Test dual-encoded self reproduction."""
        config = create_dual_encoded_config()
        parent = Organism.from_seed(b"parent_seed", config)
        
        children = parent.reproduce()
        assert len(children) > 0
        
        for child in children:
            assert child is not parent
            assert child.generation == parent.generation + 1
    
    def test_dual_encoded_reproduction_with_partner(self):
        """Test dual-encoded reproduction with partner."""
        config = create_dual_encoded_config()
        parent1 = Organism.from_seed(b"parent1", config)
        parent2 = Organism.from_seed(b"parent2", config)
        
        children = parent1.reproduce(parent2)
        assert len(children) > 0
        
        for child in children:
            assert child.generation == max(parent1.generation, parent2.generation) + 1
    
    def test_basic_with_dual_encoding_enabled(self):
        """Test basic mode with dual encoding enabled."""
        config = create_basic_config(enable_dual_encoding=True)
        parent = Organism.from_seed(b"parent_seed", config)
        
        children = parent.reproduce()
        assert len(children) > 0


class TestOmniReproduction:
    """Test omni reproduction functionality."""
    
    def test_omni_reproduction(self):
        """Test omni reproduction."""
        config = create_basic_config()
        parent1 = Organism.from_seed(b"parent1", config)
        parent2 = Organism.from_seed(b"parent2", config)
        
        children = parent1.omni_reproduce(parent2)
        assert len(children) > 0
        assert all(isinstance(child, Organism) for child in children)
        assert all(child.genome != parent1.genome for child in children)


class TestReproductionStrategy:
    """Test reproduction strategy parsing and selection."""
    
    def test_parse_reproduction_strategy_basic(self):
        """Test parsing reproduction strategy in basic mode."""
        config = create_basic_config()
        organism = Organism.from_seed(b"test_seed", config)
        
        strategy = organism._parse_reproduction_strategy()
        assert 'enabled_methods' in strategy
        assert 'combination_strategy' in strategy
    
    def test_parse_reproduction_strategy_dual_encoded(self):
        """Test parsing reproduction strategy in dual-encoded mode."""
        config = create_dual_encoded_config()
        organism = Organism.from_seed(b"test_seed", config)
        
        strategy = organism._parse_reproduction_strategy()
        assert 'enabled_methods' in strategy
        assert 'combination_strategy' in strategy
    
    def test_parse_reproduction_strategy_dual_encoded(self):
        """Test parsing reproduction strategy in dual-encoded mode."""
        config = create_dual_encoded_config()
        organism = Organism.from_seed(b"test_seed", config)
        
        strategy = organism._parse_reproduction_strategy()
        assert 'enabled_methods' in strategy
        assert 'combination_strategy' in strategy
    
    def test_get_reproduction_summary(self):
        """Test getting reproduction summary."""
        config = create_basic_config()
        organism = Organism.from_seed(b"test_seed", config)
        
        summary = organism.get_reproduction_summary()
        assert isinstance(summary, str)
        assert len(summary) > 0


class TestConvenienceFunctions:
    """Test convenience functions for creating configurations."""
    
    def test_create_basic_config(self):
        """Test create_basic_config function."""
        config = create_basic_config(genome_length=64, hash_function="sha256")
        assert config.genome_length == 64
        assert config.mode == OrganismMode.BASIC
        assert isinstance(config.hash_function, SHA256Hash)
    
    def test_create_dual_encoded_config(self):
        """Test create_dual_encoded_config function."""
        config = create_dual_encoded_config(genome_length=128)
        assert config.genome_length == 128
        assert config.mode == OrganismMode.DUAL_ENCODED
    
    def test_create_meta_config(self):
        """Test create_meta_config function (alias for dual-encoded)."""
        config = create_meta_config(genome_length=64, meta_genome_length=32)
        assert config.genome_length == 64
        assert config.mode == OrganismMode.DUAL_ENCODED


class TestOrganismIntegration:
    """Integration tests for organism functionality."""
    
    def test_full_reproduction_cycle(self):
        """Test a full reproduction cycle with different methods."""
        config = create_basic_config()
        parent = Organism.from_seed(b"parent_seed", config)
        
        # Test all reproduction methods
        children = []
        
        # Direct asexual
        children.extend(parent.direct_asexual_reproduction())
        
        # Asexual self
        children.extend(parent.asexual_self_reproduction())
        
        # Mutation
        mutation_mask = bytes([1] * config.genome_length)
        children.extend(parent.mutate(mutation_mask))
        
        # Rotation
        children.extend(parent.rotate(1))
        
        # Permutation - use a non-identity permutation
        perm_map = list(range(config.genome_length))
        perm_map[0], perm_map[1] = perm_map[1], perm_map[0]  # Swap first two elements
        children.extend(parent.permute(perm_map))
        
        # Omni - use a partner to ensure sexual reproduction is included
        partner = Organism.from_seed(b"partner_seed", config)
        children.extend(parent.omni_reproduce(partner))
        
        # Verify we have children (some duplicates are expected with omni_reproduce)
        assert len(children) > 0
        
        # Verify all children are valid organisms
        for child in children:
            assert isinstance(child, Organism)
            assert child.genome != parent.genome  # Should be different from parent
            assert child.generation >= parent.generation  # Should have same or higher generation
    
    def test_sexual_reproduction_with_different_configs(self):
        """Test sexual reproduction with different configurations."""
        config1 = create_basic_config(enable_reciprocal_reproduction=True)
        config2 = create_basic_config(enable_reciprocal_reproduction=False)
        
        parent1 = Organism.from_seed(b"parent1", config1)
        parent2 = Organism.from_seed(b"parent2", config1)
        
        children1 = parent1.reproduce_sexually(parent2)
        assert len(children1) == 2
        
        parent3 = Organism.from_seed(b"parent3", config2)
        parent4 = Organism.from_seed(b"parent4", config2)
        
        children2 = parent3.reproduce_sexually(parent4)
        assert len(children2) == 1 