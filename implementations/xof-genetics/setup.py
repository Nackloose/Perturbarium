#!/usr/bin/env python3
"""
Setup script for xof-genetics library.
"""

from setuptools import setup, find_packages
import os

# Read the README file
def read_readme():
    readme_path = os.path.join(os.path.dirname(__file__), 'README.md')
    if os.path.exists(readme_path):
        with open(readme_path, 'r', encoding='utf-8') as f:
            return f.read()
    return "XOF-Genetics: A unified, hash-agnostic genetic algorithm framework"

# Read requirements
def read_requirements():
    requirements_path = os.path.join(os.path.dirname(__file__), 'requirements.txt')
    if os.path.exists(requirements_path):
        with open(requirements_path, 'r', encoding='utf-8') as f:
            return [line.strip() for line in f if line.strip() and not line.startswith('#')]
    return []

setup(
    name="xof-genetics",
    version="2.0.0",
    author="Axia Project",
    author_email="",
    description="A unified, hash-agnostic genetic algorithm framework with configurable reproduction strategies",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/axia-project/xof-genetics",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.7",
    install_requires=read_requirements(),
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
            "black>=21.0",
            "flake8>=3.8",
            "mypy>=0.800",
        ],
        "docs": [
            "sphinx>=4.0",
            "sphinx-rtd-theme>=1.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "xof-genetics-demo=xof_genetics.demo:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
    keywords="genetic algorithm, hash function, evolution, optimization, bio-inspired",
    project_urls={
        "Bug Reports": "https://github.com/axia-project/xof-genetics/issues",
        "Source": "https://github.com/axia-project/xof-genetics",
        "Documentation": "https://xof-genetics.readthedocs.io/",
    },
) 