#!/bin/bash

# SineScramble Comprehensive Test Suite
# Tests all three variants: Original, Optimized, and Turbo

set -e

echo "🚀 SineScramble Comprehensive Test Suite"
echo "========================================"
echo "Testing: Original, Optimized, and Turbo variants"
echo "========================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Python 3 is available
if ! command -v python3 &> /dev/null; then
    print_error "Python 3 is required but not installed."
    exit 1
fi

print_status "Python 3 found: $(python3 --version)"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    print_status "Creating virtual environment..."
    python3 -m venv venv
    print_success "Virtual environment created"
else
    print_status "Using existing virtual environment"
fi

# Activate virtual environment
print_status "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
print_status "Upgrading pip..."
pip install --upgrade pip

# Install dependencies
print_status "Installing dependencies..."
pip install -r requirements.txt
print_success "Dependencies installed"

# Run comprehensive test suite (functional + performance + visualizations)
echo ""
print_status "Running comprehensive test suite (functional + performance + visualizations)..."
python3 test_sinescramble.py
print_success "Comprehensive test suite completed"

# Run demo
echo ""
print_status "Running demonstration..."
python3 demo.py
print_success "Demonstration completed"

echo ""
echo "🏆 ALL TESTS COMPLETED SUCCESSFULLY!"
echo "====================================="
echo ""
echo "📊 SUMMARY OF VARIANTS:"
echo "  • Turbo: ⚡ RECOMMENDED for high-performance, large data, and streaming (default)"
echo "  • Original: Best for Multi-Round (high-security) mode and as a reference"
echo "  • Optimized: For experimental JIT research only"
echo ""
echo "📈 VISUALIZATIONS:"
echo "  • Performance comparison graphs saved as 'sinescramble_performance_comparison.png'"
echo "  • Includes throughput, stability, and scalability analysis"
echo ""
echo "🎯 RECOMMENDATIONS:"
echo "  • Use TurboSineScrambleCipher (or FastSineScrambleCipher) for high-performance and large data (default)"
echo "  • Use SineScrambleCipher for Multi-Round (high-security) and as a reference"
echo "  • Use OptimizedSineScrambleCipher for experimental JIT testing"
echo ""
echo "📚 USAGE EXAMPLES:"
echo "  from sinescramble import FastSineScrambleCipher, OperationMode"
echo "  cipher = FastSineScrambleCipher(key, OperationMode.SEGMENTED)"
echo "  encrypted = cipher.encrypt(data)"
echo "  decrypted = cipher.decrypt(encrypted)"
echo ""

# Deactivate virtual environment
deactivate

print_success "Test suite completed successfully!"
print_status "Virtual environment deactivated"
print_status "To reactivate: source venv/bin/activate" 