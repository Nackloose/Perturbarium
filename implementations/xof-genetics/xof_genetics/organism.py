"""
Unified Organism class for XOF-Genetics framework.

This module provides a single Organism class that can operate in different modes
(basic, dual-encoded, meta) through configuration, eliminating the need for
separate organism classes.
"""

import hashlib
import random
from typing import Dict, Any, Optional, Callable, Union, List
from enum import Enum
from abc import ABC, abstractmethod

try:
    import blake3
    BLAKE3_AVAILABLE = True
except ImportError:
    BLAKE3_AVAILABLE = False


class ReproductionMethod(Enum):
    """Available reproduction methods that can be configured."""
    DIRECT_ASEXUAL = "direct_asexual"
    SELF_REPRODUCTION = "self_reproduction"
    SEXUAL = "sexual"
    MUTATION = "mutation"
    ROTATION = "rotation"
    PERMUTATION = "permutation"
    COMBINED_TRANSFORMATIONS = "combined_transformations"
    ENHANCED_SEXUAL = "enhanced_sexual"


class OrganismMode(Enum):
    """Different organism modes for reproduction strategy encoding."""
    BASIC = "basic"  # Fixed reproduction methods
    DUAL_ENCODED = "dual_encoded"  # Genome encodes reproduction strategy


class HashFunction(ABC):
    """Abstract base class for hash functions."""
    
    @abstractmethod
    def hash(self, data: bytes, length: int) -> bytes:
        """Hash data to specified length."""
        pass


class Blake3Hash(HashFunction):
    """BLAKE3 hash function implementation."""
    
    def __init__(self):
        if not BLAKE3_AVAILABLE:
            raise ImportError("blake3 package required for Blake3Hash")
    
    def hash(self, data: bytes, length: int) -> bytes:
        return blake3.blake3(data).digest(length=length)


class SHA256Hash(HashFunction):
    """SHA-256 hash function implementation."""
    
    def hash(self, data: bytes, length: int) -> bytes:
        # Use SHA-256 and truncate/extend as needed
        hash_obj = hashlib.sha256(data)
        result = hash_obj.digest()
        if length <= len(result):
            return result[:length]
        else:
            # Extend by hashing the hash
            extended = result
            while len(extended) < length:
                extended += hashlib.sha256(extended).digest()
            return extended[:length]


class OrganismConfig:
    """Configuration class for organism behavior."""
    
    def __init__(self,
                 genome_length: int = 256,
                 hash_function: Union[str, HashFunction] = "blake3",
                 mode: OrganismMode = OrganismMode.BASIC,
                 enabled_methods: Optional[List[ReproductionMethod]] = None,
                 combination_strategy: str = "all",  # "all", "random", "weighted"
                 mutation_masks: Optional[List[bytes]] = None,
                 rotation_positions: Optional[List[int]] = None,
                 permutation_maps: Optional[List[List[int]]] = None,
                 method_weights: Optional[Dict[ReproductionMethod, float]] = None,
                 meta_genome_length: Optional[int] = None,
                 enable_dual_encoding: bool = False,
                 enable_reciprocal_reproduction: bool = True):
        """
        Initialize organism configuration.
        
        Args:
            genome_length: Length of genome in bytes
            hash_function: Hash function to use ("blake3", "sha256", or custom HashFunction)
            mode: Organism mode (basic, dual_encoded, meta)
            enabled_methods: List of enabled reproduction methods
            combination_strategy: How to combine methods ("all", "random", "weighted")
            mutation_masks: List of mutation masks to use
            rotation_positions: List of rotation positions to use
            permutation_maps: List of permutation maps to use
            method_weights: Weights for weighted method selection
            meta_genome_length: Length of meta-genome (for meta mode)
            enable_dual_encoding: Whether to enable dual encoding (genome encodes reproduction strategy)
            enable_reciprocal_reproduction: Whether sexual reproduction produces two reciprocal children
        """
        self.genome_length = genome_length
        self.mode = mode
        self.combination_strategy = combination_strategy
        self.enable_dual_encoding = enable_dual_encoding
        self.enable_reciprocal_reproduction = enable_reciprocal_reproduction
        
        # Set up hash function
        if isinstance(hash_function, str):
            if hash_function.lower() == "blake3":
                self.hash_function = Blake3Hash()
            elif hash_function.lower() == "sha256":
                self.hash_function = SHA256Hash()
            else:
                raise ValueError(f"Unknown hash function: {hash_function}")
        else:
            self.hash_function = hash_function
        
        # Set up reproduction methods
        if enabled_methods is None:
            self.enabled_methods = [
                ReproductionMethod.DIRECT_ASEXUAL,
                ReproductionMethod.SELF_REPRODUCTION,
                ReproductionMethod.SEXUAL,
                ReproductionMethod.MUTATION,
                ReproductionMethod.ROTATION,
                ReproductionMethod.PERMUTATION,
                ReproductionMethod.COMBINED_TRANSFORMATIONS,
                ReproductionMethod.ENHANCED_SEXUAL
            ]
        else:
            self.enabled_methods = enabled_methods
        
        # Set up mutation masks
        if mutation_masks is None:
            self.mutation_masks = [
                bytes([1] * genome_length),  # Light mutation
                bytes([255] * genome_length),  # Heavy mutation
                bytes([i % 255 for i in range(genome_length)]),  # Pattern mutation
                bytes([i * 2 % 255 for i in range(genome_length)]),  # Alternating pattern
                bytes([i * 3 % 255 for i in range(genome_length)]),  # Triple pattern
                bytes([i * 5 % 255 for i in range(genome_length)]),  # Quintuple pattern
                bytes([i * 7 % 255 for i in range(genome_length)]),  # Septuple pattern
                bytes([i * 11 % 255 for i in range(genome_length)]),  # Prime pattern
            ]
        else:
            self.mutation_masks = mutation_masks
        
        # Set up rotation positions
        if rotation_positions is None:
            self.rotation_positions = [
                1, -1, genome_length // 2, genome_length // 4,
                genome_length // 8, genome_length // 16, genome_length // 32,
                genome_length // 3, genome_length // 5, genome_length // 7
            ]
        else:
            self.rotation_positions = rotation_positions
        
        # Set up permutation maps
        if permutation_maps is None:
            base_perm = list(range(genome_length))
            self.permutation_maps = [
                base_perm[::-1],  # Reverse
                base_perm[::2] + base_perm[1::2],  # Interleave
                random.sample(base_perm, len(base_perm)),  # Random shuffle
                base_perm[::3] + base_perm[1::3] + base_perm[2::3],  # Triple interleave
                base_perm[::4] + base_perm[1::4] + base_perm[2::4] + base_perm[3::4],  # Quad interleave
                base_perm[genome_length//2:] + base_perm[:genome_length//2],  # Half swap
                base_perm[genome_length//4:] + base_perm[:genome_length//4],  # Quarter swap
                base_perm[genome_length//8:] + base_perm[:genome_length//8],  # Eighth swap
            ]
        else:
            self.permutation_maps = permutation_maps
        
        # Set up method weights
        if method_weights is None:
            self.method_weights = {method: 1.0 for method in ReproductionMethod}
        else:
            self.method_weights = method_weights
        
        # Set up meta-genome length
        if meta_genome_length is None:
            self.meta_genome_length = genome_length
        else:
            self.meta_genome_length = meta_genome_length
    
    def copy(self) -> 'OrganismConfig':
        """Create a copy of this configuration."""
        return OrganismConfig(
            genome_length=self.genome_length,
            hash_function=self.hash_function,
            mode=self.mode,
            enabled_methods=self.enabled_methods.copy(),
            combination_strategy=self.combination_strategy,
            mutation_masks=self.mutation_masks.copy(),
            rotation_positions=self.rotation_positions.copy(),
            permutation_maps=[pm.copy() for pm in self.permutation_maps],
            method_weights=self.method_weights.copy(),
            meta_genome_length=self.meta_genome_length,
            enable_dual_encoding=self.enable_dual_encoding,
            enable_reciprocal_reproduction=self.enable_reciprocal_reproduction
        )


class Organism:
    """
    Unified organism class supporting all reproduction strategies and modes.
    
    This class consolidates all the disparate organism types into a single
    configurable system that can operate in different modes based on configuration.
    """
    
    def __init__(self, genome: bytes, config: OrganismConfig, 
                 meta_genome: Optional[bytes] = None):
        """
        Initialize an organism.
        
        Args:
            genome: Byte sequence representing the organism's genetic material
            config: Configuration object defining organism behavior
            meta_genome: Meta-genome for meta mode (optional)
        
        Raises:
            ValueError: If genome length doesn't match config
        """
        if len(genome) != config.genome_length:
            raise ValueError(f"Genome must be {config.genome_length} bytes long")
        
        self.genome = genome
        self.config = config
        self.fitness = 0.0
        self.generation = 0
        
        # Set up meta-genome for meta mode
        if config.mode == OrganismMode.DUAL_ENCODED:
            if meta_genome is None:
                raise ValueError("Meta-genome required for dual-encoded mode")
            if len(meta_genome) != config.meta_genome_length:
                raise ValueError(f"Meta-genome must be {config.meta_genome_length} bytes long")
            self.meta_genome = meta_genome
        else:
            self.meta_genome = None
        
        # Parse reproduction strategy based on mode
        self.reproduction_strategy = self._parse_reproduction_strategy()
    
    def __eq__(self, other):
        if not isinstance(other, Organism):
            return False
        return self.genome == other.genome and getattr(self, 'meta_genome', None) == getattr(other, 'meta_genome', None)

    def __hash__(self):
        return hash((self.genome, getattr(self, 'meta_genome', None)))

    def _parse_reproduction_strategy(self) -> Dict[str, Any]:
        """Parse reproduction strategy from genome or meta-genome based on mode."""
        strategy = {
            'enabled_methods': set(),
            'mutation_masks': [],
            'rotation_positions': [],
            'permutation_maps': [],
            'method_weights': {},
            'combination_strategy': 'all',
        }
        
        if self.config.mode == OrganismMode.BASIC:
            # Use configuration directly
            strategy['enabled_methods'] = set(self.config.enabled_methods)
            strategy['mutation_masks'] = self.config.mutation_masks.copy()
            strategy['rotation_positions'] = self.config.rotation_positions.copy()
            strategy['permutation_maps'] = [pm.copy() for pm in self.config.permutation_maps]
            strategy['method_weights'] = self.config.method_weights.copy()
            strategy['combination_strategy'] = self.config.combination_strategy
        
        elif self.config.mode == OrganismMode.DUAL_ENCODED or self.config.enable_dual_encoding:
            # Parse from genome
            strategy = self._parse_genome_strategy(self.genome)
        
        elif self.config.mode == OrganismMode.DUAL_ENCODED:
            # Parse from meta-genome
            strategy = self._parse_genome_strategy(self.meta_genome)
        
        return strategy
    
    def _parse_genome_strategy(self, genome: bytes) -> Dict[str, Any]:
        """Parse reproduction strategy from a genome."""
        strategy = {
            'enabled_methods': set(),
            'mutation_masks': [],
            'rotation_positions': [],
            'permutation_maps': [],
            'method_weights': {},
            'combination_strategy': 'all',
        }
        
        # Use first 8 bytes to determine which methods are enabled
        method_flags = genome[0]
        if method_flags & 1:  # Bit 0
            strategy['enabled_methods'].add(ReproductionMethod.DIRECT_ASEXUAL)
        if method_flags & 2:  # Bit 1
            strategy['enabled_methods'].add(ReproductionMethod.SELF_REPRODUCTION)
        if method_flags & 4:  # Bit 2
            strategy['enabled_methods'].add(ReproductionMethod.SEXUAL)
        if method_flags & 8:  # Bit 3
            strategy['enabled_methods'].add(ReproductionMethod.MUTATION)
        if method_flags & 16:  # Bit 4
            strategy['enabled_methods'].add(ReproductionMethod.ROTATION)
        if method_flags & 32:  # Bit 5
            strategy['enabled_methods'].add(ReproductionMethod.PERMUTATION)
        if method_flags & 64:  # Bit 6
            strategy['enabled_methods'].add(ReproductionMethod.COMBINED_TRANSFORMATIONS)
        if method_flags & 128:  # Bit 7
            strategy['enabled_methods'].add(ReproductionMethod.ENHANCED_SEXUAL)
        
        # Use next byte for combination strategy
        strategy['combination_strategy'] = ['all', 'random', 'weighted'][genome[1] % 3]
        
        # Generate mutation masks from genome
        for i in range(3):
            mask_start = 2 + i * 32
            mask_bytes = genome[mask_start:mask_start + 32]
            # Extend to full genome length
            if len(mask_bytes) == 0:
                # Fallback: use a simple pattern
                mask = bytes([i % 256 for i in range(self.config.genome_length)])
            else:
                mask = bytes([mask_bytes[i % len(mask_bytes)] for i in range(self.config.genome_length)])
            strategy['mutation_masks'].append(mask)
        
        # Generate rotation positions
        for i in range(4):
            pos_start = 98 + i * 2
            pos_bytes = genome[pos_start:pos_start + 2]
            pos = int.from_bytes(pos_bytes, 'big') % self.config.genome_length
            strategy['rotation_positions'].append(pos)
        
        # Generate permutation maps
        for i in range(3):
            perm_start = 106 + i * 32
            perm_bytes = genome[perm_start:perm_start + 32]
            # Create permutation map from bytes
            perm_map = list(range(self.config.genome_length))
            for j, byte in enumerate(perm_bytes):
                if j < len(perm_map):
                    swap_idx = (j + byte) % len(perm_map)
                    perm_map[j], perm_map[swap_idx] = perm_map[swap_idx], perm_map[j]
            strategy['permutation_maps'].append(perm_map)
        
        # Generate method weights
        weight_start = 202
        for i, method in enumerate(ReproductionMethod):
            if i < 8 and weight_start + i < len(genome):
                weight = genome[weight_start + i] / 255.0
                strategy['method_weights'][method] = weight
            else:
                strategy['method_weights'][method] = 0.5  # Default weight
        
        return strategy
    
    @staticmethod
    def from_seed(seed_data: bytes, config: OrganismConfig) -> 'Organism':
        """
        Create an organism from seed data.
        
        Args:
            seed_data: Arbitrary byte sequence to seed the genome generation
            config: Configuration object
        
        Returns:
            A new Organism instance
        """
        genome = config.hash_function.hash(seed_data, config.genome_length)
        
        if config.mode == OrganismMode.DUAL_ENCODED:
            # Create meta-genome from seed
            meta_genome = config.hash_function.hash(seed_data + b"_meta", config.meta_genome_length)
            return Organism(genome, config, meta_genome)
        else:
            return Organism(genome, config)
    
    def reproduce(self, partner: Optional['Organism'] = None) -> List['Organism']:
        """
        Reproduce using the configured strategy.
        
        Args:
            partner: Partner organism (optional for asexual reproduction)
        
        Returns:
            List of offspring organisms
        """
        if self.config.mode == OrganismMode.BASIC:
            if partner is None:
                return self._basic_asexual_reproduction()
            else:
                return self._basic_sexual_reproduction(partner)
        
        elif self.config.mode == OrganismMode.DUAL_ENCODED or self.config.enable_dual_encoding:
            if partner is None:
                return self._dual_encoded_self_reproduction()
            else:
                return self._dual_encoded_reproduction(partner)
        
        elif self.config.mode == OrganismMode.DUAL_ENCODED:
            if partner is None:
                return self._dual_encoded_self_reproduction()
            else:
                return self._dual_encoded_reproduction(partner)
        
        else:
            raise ValueError(f"Unknown organism mode: {self.config.mode}")
    
    def _basic_asexual_reproduction(self) -> List['Organism']:
        """Basic asexual reproduction."""
        children = []
        
        if ReproductionMethod.DIRECT_ASEXUAL in self.reproduction_strategy['enabled_methods']:
            children.extend(self.direct_asexual_reproduction())
        
        if ReproductionMethod.SELF_REPRODUCTION in self.reproduction_strategy['enabled_methods']:
            children.extend(self.asexual_self_reproduction())
        
        return children
    
    def _basic_sexual_reproduction(self, partner: 'Organism') -> List['Organism']:
        """Basic sexual reproduction."""
        children = []
        
        if ReproductionMethod.SEXUAL in self.reproduction_strategy['enabled_methods']:
            children.extend(self.reproduce_sexually(partner))
        
        return children
    
    def _dual_encoded_self_reproduction(self) -> List['Organism']:
        """Dual-encoded self-reproduction."""
        return self._dual_encoded_reproduction(self)
    
    def _dual_encoded_reproduction(self, partner: 'Organism') -> List['Organism']:
        """Dual-encoded reproduction using combined strategies."""
        children = []
        
        # Combine strategies from both organisms
        combined_strategy = self._combine_strategies(partner)
        
        # Determine which methods to use
        methods_to_use = self._select_methods(combined_strategy)
        
        # Apply each selected method
        for method in methods_to_use:
            method_children = self._apply_reproduction_method(method, partner, combined_strategy)
            children.extend(method_children)
        
        # Ensure all children have the same generation increment
        target_generation = max(self.generation, partner.generation) + 1
        for child in children:
            child.generation = target_generation
        
        return children
    
    def _combine_strategies(self, partner: 'Organism') -> Dict[str, Any]:
        """Combine reproduction strategies from both organisms."""
        combined = {
            'enabled_methods': set(),
            'mutation_masks': [],
            'rotation_positions': [],
            'permutation_maps': [],
            'method_weights': {},
            'combination_strategy': 'all',
        }
        
        # Union of enabled methods
        combined['enabled_methods'] = (
            self.reproduction_strategy['enabled_methods'] | 
            partner.reproduction_strategy['enabled_methods']
        )
        
        # Combine other parameters
        combined['mutation_masks'] = (
            self.reproduction_strategy['mutation_masks'] + 
            partner.reproduction_strategy['mutation_masks']
        )
        
        combined['rotation_positions'] = (
            self.reproduction_strategy['rotation_positions'] + 
            partner.reproduction_strategy['rotation_positions']
        )
        
        combined['permutation_maps'] = (
            self.reproduction_strategy['permutation_maps'] + 
            partner.reproduction_strategy['permutation_maps']
        )
        
        # Average method weights
        for method in ReproductionMethod:
            weight1 = self.reproduction_strategy['method_weights'].get(method, 0.5)
            weight2 = partner.reproduction_strategy['method_weights'].get(method, 0.5)
            combined['method_weights'][method] = (weight1 + weight2) / 2
        
        # Use more complex combination strategy
        strategies = ['all', 'random', 'weighted']
        idx1 = strategies.index(self.reproduction_strategy['combination_strategy'])
        idx2 = strategies.index(partner.reproduction_strategy['combination_strategy'])
        combined['combination_strategy'] = strategies[max(idx1, idx2)]
        
        return combined
    
    def _select_methods(self, strategy: Optional[Dict[str, Any]] = None) -> List[ReproductionMethod]:
        """Select which reproduction methods to use."""
        if strategy is None:
            strategy = self.reproduction_strategy
        
        enabled_methods = list(strategy['enabled_methods'])
        
        if not enabled_methods:
            enabled_methods = [ReproductionMethod.DIRECT_ASEXUAL]
        
        combination_strategy = strategy['combination_strategy']
        
        if combination_strategy == 'all':
            return enabled_methods
        elif combination_strategy == 'random':
            num_methods = random.randint(1, min(3, len(enabled_methods)))
            return random.sample(enabled_methods, num_methods)
        elif combination_strategy == 'weighted':
            weights = [strategy['method_weights'].get(method, 0.5) 
                      for method in enabled_methods]
            total_weight = sum(weights)
            if total_weight > 0:
                weights = [w / total_weight for w in weights]
                return random.choices(enabled_methods, weights=weights, k=random.randint(1, 3))
            else:
                return random.sample(enabled_methods, min(3, len(enabled_methods)))
        
        return enabled_methods
    
    def _apply_reproduction_method(self, method: ReproductionMethod, 
                                 partner: 'Organism',
                                 strategy: Optional[Dict[str, Any]] = None) -> List['Organism']:
        """Apply a specific reproduction method."""
        if strategy is None:
            strategy = self.reproduction_strategy
        
        children = []
        
        if method == ReproductionMethod.DIRECT_ASEXUAL:
            children.extend(self.direct_asexual_reproduction())
            if partner is not None and partner != self:
                children.extend(partner.direct_asexual_reproduction())
        
        elif method == ReproductionMethod.SELF_REPRODUCTION:
            children.extend(self.asexual_self_reproduction())
            if partner is not None and partner != self:
                children.extend(partner.asexual_self_reproduction())
        
        elif method == ReproductionMethod.SEXUAL:
            if partner is not None:
                children.extend(self.reproduce_sexually(partner))
        
        elif method == ReproductionMethod.MUTATION:
            for mask in strategy['mutation_masks']:
                children.extend(self.mutate(mask))
                if partner is not None and partner != self:
                    children.extend(partner.mutate(mask))
        
        elif method == ReproductionMethod.ROTATION:
            for pos in strategy['rotation_positions']:
                children.extend(self.rotate(pos))
                if partner is not None and partner != self:
                    children.extend(partner.rotate(pos))
        
        elif method == ReproductionMethod.PERMUTATION:
            for perm_map in strategy['permutation_maps']:
                children.extend(self.permute(perm_map))
                if partner is not None and partner != self:
                    children.extend(partner.permute(perm_map))
        
        elif method == ReproductionMethod.COMBINED_TRANSFORMATIONS:
            for mask in strategy['mutation_masks'][:2]:
                for pos in strategy['rotation_positions'][:2]:
                    mutated_children = self.mutate(mask)
                    for mutated in mutated_children:
                        children.extend(mutated.rotate(pos))
                    if partner is not None and partner != self:
                        mutated_partner_children = partner.mutate(mask)
                        for mutated_partner in mutated_partner_children:
                            children.extend(mutated_partner.rotate(pos))
        
        elif method == ReproductionMethod.ENHANCED_SEXUAL:
            if partner is not None:
                sexual_children = self.reproduce_sexually(partner)
                for child in sexual_children:
                    for mask in strategy['mutation_masks'][:2]:
                        children.extend(child.mutate(mask))
        
        return children
    
    def direct_asexual_reproduction(self) -> List['Organism']:
        """Direct asexual reproduction by re-hashing the genome."""
        child_genome = self.config.hash_function.hash(self.genome, self.config.genome_length)
        child = Organism(child_genome, self.config, self.meta_genome)
        child.generation = self.generation + 1
        return [child]
    
    def asexual_self_reproduction(self) -> List['Organism']:
        """Asexual self-reproduction with sexual recombination."""
        # Create two children using different reproduction methods
        child1_list = self.direct_asexual_reproduction()
        child1 = child1_list[0]  # Extract the single child from the list
        
        # Create child2 using a different method - avoid double generation increment
        if ReproductionMethod.SEXUAL in self.config.enabled_methods:
            # Use sexual reproduction logic directly to avoid double increment
            split_point = self.config.genome_length // 2
            pre_image = self.genome[:split_point] + self.genome[split_point:]
            child2_genome = self.config.hash_function.hash(pre_image, self.config.genome_length)
            child2 = Organism(child2_genome, self.config, self.meta_genome)
            child2.generation = self.generation + 1
        else:
            # Use mutation if sexual is not available
            child2_list = self.mutate(random.choice(self.config.mutation_masks))
            child2 = child2_list[0]  # Extract the single child from the list
        
        return [child1, child2]
    
    def reproduce_sexually(self, partner: 'Organism') -> List['Organism']:
        """Produces children using single-point crossover."""
        split_point = self.config.genome_length // 2
        
        if self.config.enable_reciprocal_reproduction:
            # Produce two reciprocal children
            # Child 1: First half of self, second half of partner
            pre_image1 = self.genome[:split_point] + partner.genome[split_point:]
            child1_genome = self.config.hash_function.hash(pre_image1, self.config.genome_length)
            
            # Child 2: First half of partner, second half of self
            pre_image2 = partner.genome[:split_point] + self.genome[split_point:]
            child2_genome = self.config.hash_function.hash(pre_image2, self.config.genome_length)
            
            child1 = Organism(child1_genome, self.config, self.meta_genome)
            child2 = Organism(child2_genome, self.config, self.meta_genome)
            child1.generation = max(self.generation, partner.generation) + 1
            child2.generation = max(self.generation, partner.generation) + 1
            
            return [child1, child2]
        else:
            # Produce only one child (randomly choose which parent contributes first half)
            if random.choice([True, False]):
                # First half from self, second half from partner
                pre_image = self.genome[:split_point] + partner.genome[split_point:]
            else:
                # First half from partner, second half from self
                pre_image = partner.genome[:split_point] + self.genome[split_point:]
            
            child_genome = self.config.hash_function.hash(pre_image, self.config.genome_length)
            child = Organism(child_genome, self.config, self.meta_genome)
            child.generation = max(self.generation, partner.generation) + 1
            
            return [child]
    
    def mutate(self, mutation_mask: bytes) -> List['Organism']:
        """Creates a mutated version of the organism."""
        if len(mutation_mask) != self.config.genome_length:
            raise ValueError(f"Mutation mask must be {self.config.genome_length} bytes long")
        
        # Apply mutation using XOR
        mutated_genome = bytes(a ^ b for a, b in zip(self.genome, mutation_mask))
        
        # Hash the mutated genome to produce final offspring
        child_genome = self.config.hash_function.hash(mutated_genome, self.config.genome_length)
        child = Organism(child_genome, self.config, self.meta_genome)
        child.generation = self.generation + 1
        return [child]
    
    def rotate(self, positions: int) -> List['Organism']:
        """Creates a rotated version of the organism's genome."""
        # Normalize positions to be within genome length
        positions = positions % self.config.genome_length
        
        # Rotate the genome
        rotated_genome = self.genome[positions:] + self.genome[:positions]
        
        # Hash the rotated genome to produce final offspring
        child_genome = self.config.hash_function.hash(rotated_genome, self.config.genome_length)
        child = Organism(child_genome, self.config, self.meta_genome)
        child.generation = self.generation + 1
        return [child]
    
    def permute(self, permutation_map: List[int]) -> List['Organism']:
        """Creates a permuted version of the organism's genome."""
        if len(permutation_map) != self.config.genome_length:
            raise ValueError(f"Permutation map must be {self.config.genome_length} elements long")
        
        if set(permutation_map) != set(range(self.config.genome_length)):
            raise ValueError("Permutation map must be a valid permutation")
        
        # Apply permutation
        permuted_genome = bytes(self.genome[i] for i in permutation_map)
        
        # Hash the permuted genome to produce final offspring
        child_genome = self.config.hash_function.hash(permuted_genome, self.config.genome_length)
        child = Organism(child_genome, self.config, self.meta_genome)
        child.generation = self.generation + 1
        return [child]
    
    def omni_reproduce(self, partner: Optional['Organism'] = None) -> List['Organism']:
        """
        Comprehensive omni-reproduction that generates 50-100+ offspring using ALL methods.
        This implements the full omni-reproduction concept from the specification.
        """
        children = []
        
        if partner is None:
            # Self-reproduction: use all available methods on self
            partner = self
        
        # 1. Asexual reproduction from both parents
        children.extend(self.direct_asexual_reproduction())
        children.extend(partner.direct_asexual_reproduction())
        
        # 2. Asexual self-reproduction from both parents (2 children each)
        children.extend(self.asexual_self_reproduction())
        children.extend(partner.asexual_self_reproduction())
        
        # 3. Sexual reproduction between parents (2 children)
        children.extend(self.reproduce_sexually(partner))
        
        # 4. Mutated versions of both parents using different mutation masks
        for mask in self.config.mutation_masks[:5]:  # Use up to 5 different masks
            children.extend(self.mutate(mask))
            children.extend(partner.mutate(mask))
        
        # 5. Rotated versions of both parents using different rotation positions
        for pos in self.config.rotation_positions[:5]:  # Use up to 5 different positions
            children.extend(self.rotate(pos))
            children.extend(partner.rotate(pos))
        
        # 6. Permuted versions of both parents using different permutation maps
        for perm_map in self.config.permutation_maps[:5]:  # Use up to 5 different maps
            children.extend(self.permute(perm_map))
            children.extend(partner.permute(perm_map))
        
        # 7. Combined transformations: mutated and rotated versions
        for mask in self.config.mutation_masks[:3]:
            for pos in self.config.rotation_positions[:3]:
                mutated_self = self.mutate(mask)[0]  # Get the single child
                children.extend(mutated_self.rotate(pos))
                mutated_partner = partner.mutate(mask)[0]
                children.extend(mutated_partner.rotate(pos))
        
        # 8. Enhanced sexual offspring: sexual children that are further mutated
        sexual_children = self.reproduce_sexually(partner)
        for child in sexual_children:
            for mask in self.config.mutation_masks[:3]:
                children.extend(child.mutate(mask))
        
        return children
    
    def get_reproduction_summary(self) -> str:
        """Get a human-readable summary of the reproduction strategy."""
        enabled = list(self.reproduction_strategy['enabled_methods'])
        strategy = self.reproduction_strategy['combination_strategy']
        
        return f"Enabled: {len(enabled)} methods ({', '.join([m.value for m in enabled])}), Strategy: {strategy}"
    
    def __repr__(self) -> str:
        """String representation of the organism."""
        mode_str = f", mode={self.config.mode.value}" if self.config.mode != OrganismMode.BASIC else ""
        return f"Organism(genome={self.genome[:8].hex()}..., fitness={self.fitness:.4f}, generation={self.generation}{mode_str})"


# Convenience functions for creating common configurations
def create_basic_config(genome_length: int = 256, 
                       hash_function: str = "blake3",
                       enabled_methods: Optional[List[ReproductionMethod]] = None,
                       enable_dual_encoding: bool = False,
                       enable_reciprocal_reproduction: bool = True) -> OrganismConfig:
    """Create a basic organism configuration."""
    return OrganismConfig(
        genome_length=genome_length,
        hash_function=hash_function,
        mode=OrganismMode.BASIC,
        enabled_methods=enabled_methods,
        enable_dual_encoding=enable_dual_encoding,
        enable_reciprocal_reproduction=enable_reciprocal_reproduction
    )


def create_dual_encoded_config(genome_length: int = 256,
                              hash_function: str = "blake3",
                              enable_reciprocal_reproduction: bool = True) -> OrganismConfig:
    """Create a dual-encoded organism configuration."""
    return OrganismConfig(
        genome_length=genome_length,
        hash_function=hash_function,
        mode=OrganismMode.DUAL_ENCODED,
        enable_reciprocal_reproduction=enable_reciprocal_reproduction
    )


def create_meta_config(genome_length: int = 256,
                      meta_genome_length: int = 256,
                      hash_function: str = "blake3",
                      enable_reciprocal_reproduction: bool = True) -> OrganismConfig:
    """Create a dual-encoded configuration (alias for create_dual_encoded_config)."""
    return create_dual_encoded_config(
        genome_length=genome_length,
        hash_function=hash_function,
        enable_reciprocal_reproduction=enable_reciprocal_reproduction
    ) 