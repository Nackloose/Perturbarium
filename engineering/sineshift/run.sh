#!/bin/bash

# SineShift Module Runner Script
# Auto-manages virtual environment and dependencies

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$SCRIPT_DIR/venv"
PYTHON_VERSION="python3"

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
    if ! command -v $PYTHON_VERSION &> /dev/null; then
        print_error "Python 3 is not installed or not in PATH"
        print_error "Please install Python 3 and try again"
        exit 1
    fi
    print_success "Python 3 found: $(which $PYTHON_VERSION)"
}

# Create virtual environment if it doesn't exist
create_venv() {
    if [ ! -d "$VENV_DIR" ]; then
        print_status "Creating virtual environment..."
        $PYTHON_VERSION -m venv "$VENV_DIR"
        print_success "Virtual environment created at $VENV_DIR"
    else
        print_status "Virtual environment already exists at $VENV_DIR"
    fi
}

# Activate virtual environment
activate_venv() {
    print_status "Activating virtual environment..."
    source "$VENV_DIR/bin/activate"
    print_success "Virtual environment activated"
}

# Install dependencies
install_dependencies() {
    print_status "Installing dependencies..."
    
    # Upgrade pip first
    pip install --upgrade pip
    
    # Install required packages
    pip install numpy matplotlib
    
    print_success "Dependencies installed successfully"
}

# Check if dependencies are installed
check_dependencies() {
    print_status "Checking dependencies..."
    
    if ! python -c "import numpy" 2>/dev/null; then
        print_warning "NumPy not found, will install..."
        return 1
    fi
    
    if ! python -c "import matplotlib" 2>/dev/null; then
        print_warning "Matplotlib not found, will install..."
        return 1
    fi
    
    print_success "All dependencies are installed"
    return 0
}



# Main execution
main() {
    echo -e "${BLUE}================================${NC}"
    echo -e "${BLUE}    SineShift Module Runner${NC}"
    echo -e "${BLUE}================================${NC}"
    echo
    
    # Check Python installation
    check_python
    
    # Create virtual environment
    create_venv
    
    # Activate virtual environment
    activate_venv
    
    # Check and install dependencies
    if ! check_dependencies; then
        install_dependencies
    fi
    
    echo
    print_success "Environment setup complete!"
    echo
    echo -e "${YELLOW}Available commands:${NC}"
    echo -e "  ${GREEN}python test_sineshift.py${NC} - Run the test suite"
    echo -e "  ${GREEN}python test_sineshift_fullspectrum.py${NC} - Run the full spectrum benchmark suite"
    echo -e "  ${GREEN}python -c \"from sineshift import *; print('Module imported successfully')\"${NC} - Test module import"
    echo -e "  ${GREEN}python${NC} - Start Python interpreter with module available"
    echo
    
    # Interactive prompt for test selection
    echo -e "${YELLOW}Which test suite would you like to run?${NC}"
    echo -e "  1) Basic (test_sineshift.py)"
    echo -e "  2) Full Spectrum (test_sineshift_fullspectrum.py)"
    echo -e "  3) Both"
    echo -e "  4) None (just activate environment)"
    read -p "Enter choice [1-4]: " suite_choice
    echo
    # Ask if plotting should be enabled
    echo -e "${YELLOW}Enable matplotlib plotting? (y/n)${NC}"
    read -r plot_choice
    plot_flag=""
    if [[ "$plot_choice" =~ ^[Yy]$ ]]; then
        plot_flag="--plot"
    fi
    case "$suite_choice" in
        1)
            print_status "Running basic test suite..."
            python test_sineshift.py $plot_flag
            ;;
        2)
            print_status "Running full spectrum benchmark suite..."
            python test_sineshift_fullspectrum.py $plot_flag
            ;;
        3)
            print_status "Running both test suites..."
            python test_sineshift.py $plot_flag
            python test_sineshift_fullspectrum.py $plot_flag
            ;;
        4)
            print_status "No test suite selected. Environment is ready."
            ;;
        *)
            print_warning "Invalid choice. No test suite will be run."
            ;;
    esac
    echo
    print_status "Virtual environment is active. You can now run Python commands."
    print_status "To deactivate, run: deactivate"
    echo
}

# Handle command line arguments
case "${1:-}" in
    "test")
        check_python
        create_venv
        activate_venv
        if ! check_dependencies; then
            install_dependencies
        fi
        # Forward remaining arguments to the test script
        shift
        print_status "Running tests with arguments: $*"
        python test_sineshift.py "$@"
        ;;
    "test-plot")
        check_python
        create_venv
        activate_venv
        if ! check_dependencies; then
            install_dependencies
        fi
        print_status "Running tests with plotting enabled..."
        # Forward remaining arguments to the test script
        shift
        python test_sineshift.py --plot "$@"
        ;;
    "test-fullspectrum")
        check_python
        create_venv
        activate_venv
        if ! check_dependencies; then
            install_dependencies
        fi
        print_status "Running full spectrum benchmark tests..."
        # Forward remaining arguments to the test script
        shift
        python test_sineshift_fullspectrum.py "$@"
        ;;
    "install")
        check_python
        create_venv
        activate_venv
        install_dependencies
        ;;
    "clean")
        if [ -d "$VENV_DIR" ]; then
            print_status "Removing virtual environment..."
            rm -rf "$VENV_DIR"
            print_success "Virtual environment removed"
        else
            print_warning "No virtual environment found to remove"
        fi
        ;;
    "help"|"-h"|"--help")
        echo "SineShift Module Runner"
        echo
        echo "Usage: $0 [command] [options]"
        echo
        echo "Commands:"
        echo "  (no args)  - Setup environment and prompt for test suite selection"
        echo "  test       - Setup environment and run tests"
        echo "  test-plot  - Setup environment and run tests with plotting"
        echo "  test-fullspectrum - Setup environment and run full spectrum benchmarks"
        echo "  install    - Setup environment and install dependencies"
        echo "  clean      - Remove virtual environment"
        echo "  help       - Show this help message"
        echo
        echo "Test Options:"
        echo "  --plot, -p  - Enable matplotlib plotting (when using 'test' or 'test-fullspectrum' command)"
        echo "  --help, -h  - Show test script help"
        echo
        echo "Full Spectrum Test Options:"
        echo "  --fast, -f  - Run with reduced iterations for faster testing"
        echo "  --size N    - Number of iterations for consistency tests"
        echo "  --output FILE - Save results to JSON file"
        echo
        echo "Examples:"
        echo "  $0                   # Interactive prompt for test suite selection"
        echo "  $0 test              # Run tests normally"
        echo "  $0 test --plot       # Run tests with plotting"
        echo "  $0 test-plot         # Run tests with plotting (alternative)"
        echo "  $0 test-fullspectrum # Run full spectrum benchmarks"
        echo "  $0 test-fullspectrum --fast # Run fast benchmarks"
        echo "  $0 test-fullspectrum --plot # Run full spectrum with plotting"
        echo "  $0 test-fullspectrum --output results.json # Save results"
        echo "  $0 test --help       # Show test script help"
        echo
        ;;
    "")
        main
        ;;
    *)
        print_error "Unknown command: $1"
        echo "Use '$0 help' for usage information"
        exit 1
        ;;
esac 