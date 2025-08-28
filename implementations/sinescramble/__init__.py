"""
SineScramble: A Multi-Mode Symmetric Cipher

A novel symmetric encryption algorithm that combines sine-wave-based 
permutation and substitution, supporting both high-security Multi-Round Mode
and high-performance Segmented Mode.

Three implementations are available:
- Turbo: ⚡ RECOMMENDED for high-performance, large data, and streaming (default)
- Original: Best for Multi-Round (high-security) mode and as a reference
- Optimized: For experimental JIT research only

Version: 2.1.0
Author: N Lisowski
"""

from .cipher import SineScrambleCipher, OperationMode
from .cipher_optimized import OptimizedSineScrambleCipher
from .cipher_turbo import TurboSineScrambleCipher
from .utils import generate_random_key, key_from_password, key_to_string, string_to_key

# Turbo is now the recommended default for high-performance and large data
FastSineScrambleCipher = TurboSineScrambleCipher

__version__ = "2.1.0"
__author__ = "N Lisowski"

__all__ = [
    "TurboSineScrambleCipher",      # Ultra-fast version (RECOMMENDED default)
    "SineScrambleCipher",           # Original implementation (best for Multi-Round)
    "OptimizedSineScrambleCipher",  # JIT-compiled version (experimental)
    "FastSineScrambleCipher",       # Alias for turbo (recommended default)
    "OperationMode", 
    "generate_random_key",
    "key_from_password",
    "key_to_string",
    "string_to_key"
] 