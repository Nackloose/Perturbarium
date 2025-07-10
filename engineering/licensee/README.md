# **Licensee Algorithm**
## A Sophisticated Mathematical Framework for Generating and Validating Tamper-Resistant Software License Keys

**Version:** 1.0.0  
**Date:** July 9, 2025  
**Authors:** N Lisowski

---

## Overview

The Licensee Algorithm is a comprehensive mathematical solution for software licensing that employs multiple layers of cryptographic protection, custom encoding schemes, and mathematical permutation functions to ensure license integrity and prevent unauthorized use.

## Features

- **Dual Mode Operation**: Supports both included and hardcoded swap parameters
- **Version Locking**: Ability to lock licenses to specific application versions
- **Flexible Duration**: Configurable license durations from days to years
- **Group Management**: Support for different license holder groups
- **Tamper Resistance**: Multiple layers of cryptographic protection
- **Mathematical Elegance**: Sophisticated permutation and encoding algorithms

## Quick Start

### Installation

```bash
# Install dependencies
pip install cryptography PySide6

# Run the key generation UI
python src/licensee/keygen_ui.py
```

### Basic Usage

```python
from licensee.license_manager import generate_license_key, validate_license_key
from licensee.crypto import generate_rsa_key_pair

# Generate RSA key pair
private_key, public_key = generate_rsa_key_pair()

# Generate a license key
license_key = generate_license_key(
    private_key=private_key,
    license_plan=2,
    duration_days=365,
    key_holder_group=10,
    unique_license_id=12345,
    version_lock=1,
    use_included_swap_param=True
)

# Validate a license key
license_data = validate_license_key(
    license_key_string=license_key,
    current_app_version=1,
    hardcoded_swap_param=None
)
```

## Algorithm Architecture

```
license_manager.py    # Core license generation and validation
├── license_data.py   # Data structures and bit-level encoding
├── encoding.py       # Custom Base32-like encoding
├── permutation.py    # Sine-based permutation algorithm
└── crypto.py        # RSA cryptographic operations

keygen_ui.py         # Qt-based GUI for license generation
```

## Documentation

- **[Algorithm Specification](LICENSING_ALGORITHM_SPECIFICATION.md)**: Detailed mathematical specification
- **[Whitepaper](WHITEPAPER.md)**: Comprehensive algorithm overview and analysis

## Security Features

### Multi-Layer Protection

1. **Cryptographic Signatures**: RSA-2048 prevents tampering
2. **Data Integrity**: Checksum validation
3. **Mathematical Obfuscation**: Sine-based permutation
4. **Parameter Hiding**: Swap parameter embedded in key
5. **Version Control**: Version locking mechanism
6. **Time Expiry**: Automatic license expiration

### Attack Resistance

- **Tampering**: Detected by signature verification
- **Brute Force**: Requires knowledge of swap parameter
- **Replay**: Prevented by unique license IDs
- **Sharing**: Limited by unique identifiers
- **Version Bypass**: Blocked by version locking

## License Key Format

```
AAAAA-BBBBB-CCCCC-DDDDD-EEEEE-FFFFF-GGGGG...
```

- **Total Length**: 440 characters
- **Segments**: 88 segments of 5 characters each
- **Content**: Permuted license data + RSA-2048 signature

## Data Structure

The algorithm uses a 150-bit license data structure containing:

| Field | Bits | Description |
|-------|------|-------------|
| mode_flag | 1 | Swap parameter mode |
| swap_param | 8 | Permutation parameter |
| issue_date | 14 | Days since epoch |
| license_plan | 4 | License plan type |
| duration_expiry | 10 | Duration in days |
| key_holder_group | 8 | Group identifier |
| unique_license_id | 32 | Unique license ID |
| version_lock | 8 | Version lock number |
| simple_checksum | 5 | Data integrity check |
| entropy | Variable | Random entropy |

## Usage Patterns

### License Generation

```python
# Generate license with included swap parameter
key = generate_license_key(
    private_key=private_key,
    license_plan=2,
    duration_days=365,
    key_holder_group=10,
    unique_license_id=12345,
    version_lock=1,
    use_included_swap_param=True
)

# Generate license with hardcoded swap parameter
key = generate_license_key(
    private_key=private_key,
    license_plan=1,
    duration_days=30,
    key_holder_group=1,
    unique_license_id=67890,
    version_lock=0,
    use_included_swap_param=False,
    fixed_swap_param=0.75
)
```

### License Validation

```python
# Validate with included swap parameter
license_data = validate_license_key(
    license_key_string=key,
    current_app_version=1,
    hardcoded_swap_param=None
)

# Validate with hardcoded swap parameter
license_data = validate_license_key(
    license_key_string=key,
    current_app_version=1,
    hardcoded_swap_param=0.75
)
```

## Key Management

### Private Key Security

- Store in secure location
- Use strong encryption
- Limit access to authorized personnel
- Regular key rotation

### Public Key Distribution

- Bundle with application
- Verify integrity
- Version control
- Backup procedures

## Dependencies

```python
# Core Dependencies
cryptography >= 3.4.8
PySide6 >= 6.0.0
typing-extensions >= 4.0.0

# Development Dependencies
pytest >= 7.0.0
black >= 22.0.0
flake8 >= 4.0.0
mypy >= 0.950
```

## System Requirements

- **CPU**: 1 GHz or faster
- **RAM**: 512 MB minimum, 2 GB recommended
- **Storage**: 100 MB available space
- **OS**: Windows 10/11, macOS 10.15+, Linux (Ubuntu 20.04+)

## Performance

- **License Generation**: < 100ms
- **License Validation**: < 50ms
- **Key Pair Generation**: < 1000ms
- **Throughput**: 1000+ keys/second generation, 2000+ validations/second

## Error Handling

The algorithm includes comprehensive error handling for:

- Invalid license formats
- Signature verification failures
- Expired licenses
- Version lock mismatches
- Checksum validation failures
- Invalid swap parameters

## Testing

```bash
# Run unit tests
pytest src/licensee/

# Run performance tests
pytest src/licensee/ -m performance

# Run security tests
pytest src/licensee/ -m security
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

## Security Considerations

### Best Practices

1. **Secure Key Storage**: Encrypted private key storage
2. **Regular Updates**: Key rotation and algorithm updates
3. **Audit Logging**: License generation and validation logs
4. **Backup Procedures**: Secure backup of cryptographic materials
5. **Access Control**: Limited access to key generation systems

### Attack Vectors

1. **Key Extraction**: Protected by obfuscation and signatures
2. **Replay Attacks**: Prevented by unique identifiers
3. **Time Manipulation**: Limited by server-side validation
4. **Version Bypass**: Blocked by version locking
5. **Brute Force**: Resistant due to permutation complexity

## Future Enhancements

- Elliptic Curve Cryptography (ECDSA)
- Hardware Security Module (HSM) integration
- Online license validation
- License revocation capabilities
- Analytics integration
- Multi-platform support

## License

This algorithm is proprietary. All rights reserved.

---

**Version**: 1.0  
**Date**: 2024  
**Algorithm**: Licensee 