#!/bin/bash

# InstaMaster Auto-Setup and Run Script
# This script automatically sets up a virtual environment, installs dependencies,
# and runs the InstaMaster audio mastering pipeline.

set -e  # Exit on any error

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
check_python() {
    if ! command -v python3 &> /dev/null; then
        print_error "Python 3 is not installed or not in PATH"
        print_status "Please install Python 3.8 or higher"
        exit 1
    fi
    
    PYTHON_VERSION=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
    print_success "Found Python $PYTHON_VERSION"
}

# Check if pip is available
check_pip() {
    if ! command -v pip3 &> /dev/null; then
        print_error "pip3 is not installed or not in PATH"
        print_status "Please install pip3"
        exit 1
    fi
    print_success "Found pip3"
}

# Setup virtual environment
setup_venv() {
    VENV_DIR="venv"
    
    if [ -d "$VENV_DIR" ]; then
        print_status "Virtual environment already exists"
    else
        print_status "Creating virtual environment..."
        python3 -m venv "$VENV_DIR"
        print_success "Virtual environment created"
    fi
    
    # Activate virtual environment
    print_status "Activating virtual environment..."
    source "$VENV_DIR/bin/activate"
    print_success "Virtual environment activated"
}

# Install requirements
install_requirements() {
    print_status "Installing requirements..."
    
    # Upgrade pip first
    pip install --upgrade pip
    
    # Install requirements
    if [ -f "requirements.txt" ]; then
        pip install -r requirements.txt
        print_success "Requirements installed successfully"
    else
        print_error "requirements.txt not found"
        exit 1
    fi
}

# Run the application
run_application() {
    print_status "Starting InstaMaster..."
    
    # Check if instamaster.py exists
    if [ ! -f "instamaster.py" ]; then
        print_error "instamaster.py not found"
        exit 1
    fi
    
    # Run the application
    python3 instamaster.py "$@"
}

# Main execution
main() {
    echo "=========================================="
    echo "    InstaMaster Audio Mastering Pipeline"
    echo "=========================================="
    echo ""
    
    # Check prerequisites
    print_status "Checking prerequisites..."
    check_python
    check_pip
    
    # Setup environment
    print_status "Setting up environment..."
    setup_venv
    install_requirements
    
    # Run the application
    print_status "Launching InstaMaster..."
    run_application "$@"
}

# Handle script arguments
case "${1:-}" in
    --help|-h)
        echo "Usage: $0 [OPTIONS]"
        echo ""
        echo "Options:"
        echo "  --help, -h     Show this help message"
        echo "  --clean         Remove virtual environment and reinstall"
        echo "  --test          Run in test mode"
        echo ""
        echo "Examples:"
        echo "  $0                    # Run normally"
        echo "  $0 --clean            # Clean install"
        echo "  $0 --test             # Run in test mode"
        exit 0
        ;;
    --clean)
        print_status "Cleaning virtual environment..."
        rm -rf venv
        print_success "Virtual environment removed"
        ;;
    --test)
        print_status "Running in test mode..."
        export INSTAMASTER_TEST_MODE=1
        ;;
esac

# Run main function
main "$@" 