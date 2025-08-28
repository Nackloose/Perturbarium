# 🧪 Tests

> *"Tests are the guardians of truth in code — they tell us not just what works, but what we can trust."*

This directory contains the comprehensive test suite for the XOF-Genetics implementation, covering all aspects of the genetic algorithm system.

## 📋 Navigation

- **[`test_organism.py`](test_organism.py)** — Tests for individual organism behavior and genetics
- **[`test_evolution.py`](test_evolution.py)** — Tests for evolutionary processes and population dynamics
- **[`test_integration.py`](test_integration.py)** — Integration tests for system-wide functionality
- **[`test_specification_compliance.py`](test_specification_compliance.py)** — Tests ensuring compliance with theoretical specifications
- **[`test_threading_and_auto_population.py`](test_threading_and_auto_population.py)** — Tests for concurrent execution and automatic population management
- **[`test_limits.py`](test_limits.py)** — Tests for edge cases, limits, and boundary conditions

## 🎯 Purpose

This test suite validates:
- Individual organism behavior and genetics
- Evolutionary algorithm correctness
- System integration and interoperability
- Specification compliance
- Threading and concurrency safety
- Edge cases and boundary conditions
- Performance characteristics

## 🚀 Running Tests

```bash
# Run all tests
python -m pytest

# Run specific test file
python -m pytest test_organism.py

# Run with verbose output
python -m pytest -v

# Run with coverage
python -m pytest --cov=xof_genetics
```

## 🔗 Related Resources

- **Main Implementation**: Check [`../`](../) for the main XOF-Genetics implementation
- **Theory**: See [`../../theory/xof-genetics.md`](../../theory/xof-genetics.md) for theoretical foundations
- **Documentation**: Visit [`../README.md`](../README.md) for implementation overview

## 💡 Test Philosophy

These tests follow the principle that:
- Tests should be comprehensive and thorough
- Edge cases and boundary conditions are critical
- Performance characteristics should be validated
- Threading and concurrency must be tested
- Specification compliance is non-negotiable

> *"Good tests don't just verify that code works — they verify that code works correctly under all conditions."*
