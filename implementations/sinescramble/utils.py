"""
Utility functions for SineScramble cipher
"""

import random
import json
import base64
import hashlib
from typing import List


def generate_random_key(dimension: int, seed: int = None) -> List[float]:
    """
    Generate a random key vector of specified dimension
    
    Args:
        dimension: Number of key components (n)
        seed: Random seed for reproducible keys
        
    Returns:
        List of random float values
    """
    if dimension <= 0:
        raise ValueError("Dimension must be positive")
    
    if seed is not None:
        random.seed(seed)
    
    # Generate random floats in range [-1000, 1000] for good variety
    key = [random.uniform(-1000.0, 1000.0) for _ in range(dimension)]
    return key


def key_from_password(password: str, dimension: int) -> List[float]:
    """
    Derive a key vector from a password using cryptographic hashing
    
    Args:
        password: Password string
        dimension: Number of key components needed
        
    Returns:
        Deterministic key vector derived from password
    """
    if dimension <= 0:
        raise ValueError("Dimension must be positive")
    
    # Use SHA-256 to create deterministic seed from password
    password_hash = hashlib.sha256(password.encode('utf-8')).digest()
    
    # Convert hash to integer seed
    seed = int.from_bytes(password_hash[:8], byteorder='big')
    
    # Generate deterministic key using the seed
    random.seed(seed)
    key = [random.uniform(-1000.0, 1000.0) for _ in range(dimension)]
    
    return key


def key_to_string(key: List[float]) -> str:
    """
    Convert key vector to base64 encoded string for storage/transmission
    
    Args:
        key: Key vector
        
    Returns:
        Base64 encoded string representation
    """
    key_json = json.dumps(key)
    key_bytes = key_json.encode('utf-8')
    return base64.b64encode(key_bytes).decode('ascii')


def string_to_key(key_string: str) -> List[float]:
    """
    Convert base64 encoded string back to key vector
    
    Args:
        key_string: Base64 encoded key string
        
    Returns:
        Key vector
    """
    try:
        key_bytes = base64.b64decode(key_string.encode('ascii'))
        key_json = key_bytes.decode('utf-8')
        key = json.loads(key_json)
        
        if not isinstance(key, list) or not all(isinstance(x, (int, float)) for x in key):
            raise ValueError("Invalid key format")
        
        return [float(x) for x in key]
    except Exception as e:
        raise ValueError(f"Failed to decode key string: {e}")


def validate_key(key: List[float]) -> bool:
    """
    Validate that a key is properly formatted
    
    Args:
        key: Key vector to validate
        
    Returns:
        True if key is valid, False otherwise
    """
    if not isinstance(key, list):
        return False
    
    if len(key) == 0:
        return False
    
    return all(isinstance(x, (int, float)) and not (isinstance(x, bool)) for x in key)


def estimate_security_level(key_dimension: int) -> str:
    """
    Estimate security level based on key dimension
    
    Args:
        key_dimension: Number of key components
        
    Returns:
        Security level description
    """
    if key_dimension < 2:
        return "Very Low (Not recommended)"
    elif key_dimension < 4:
        return "Low"
    elif key_dimension < 8:
        return "Medium"
    elif key_dimension < 16:
        return "High"
    else:
        return "Very High"


def recommend_mode_for_use_case(use_case: str) -> str:
    """
    Recommend operation mode based on use case
    
    Args:
        use_case: Description of intended use
        
    Returns:
        Recommended mode
    """
    use_case_lower = use_case.lower()
    
    if any(keyword in use_case_lower for keyword in 
           ['stream', 'real-time', 'live', 'fast', 'performance', 'latency']):
        return "SEGMENTED (High Performance)"
    elif any(keyword in use_case_lower for keyword in 
             ['storage', 'archive', 'file', 'disk', 'secure', 'security']):
        return "MULTI_ROUND (High Security)"
    else:
        return "MULTI_ROUND (Default - High Security)" 