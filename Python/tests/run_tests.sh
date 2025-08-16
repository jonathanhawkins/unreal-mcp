#!/bin/bash

# Unreal MCP Test Runner Shell Script
#
# This script provides a convenient interface for running Unreal MCP tests
# from the command line or CI/CD systems. It handles environment setup,
# dependency checking, and test execution.
#
# Usage: ./run_tests.sh [OPTIONS]
#
# Examples:
#   ./run_tests.sh                              # Run all tests with defaults
#   ./run_tests.sh --mock --parallel            # Use mock server with parallel execution
#   ./run_tests.sh --integration-only           # Run only integration tests
#   ./run_tests.sh --unreal-host 192.168.1.100 # Connect to remote Unreal instance
#   ./run_tests.sh --ci                         # CI-optimized execution

set -euo pipefail  # Exit on error, undefined vars, pipe failures

# Script configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "${SCRIPT_DIR}/../.." && pwd)"
PYTHON_DIR="${PROJECT_DIR}/Python"

# Default configuration
DEFAULT_PYTHON="python3"
DEFAULT_UNREAL_HOST="127.0.0.1"
DEFAULT_UNREAL_PORT="55557"
DEFAULT_TIMEOUT="30"
DEFAULT_OUTPUT_DIR="test_output"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Help function
show_help() {
    cat << EOF
Unreal MCP Test Runner

Usage: $0 [OPTIONS]

Test Execution Options:
    --use-pytest                Use pytest instead of custom framework
    --test-connection           Test Unreal connection only
    --generate-sample-reports   Generate sample test reports

Test Filtering Options:
    --integration-only          Run only integration tests
    --unit-only                 Run only unit tests  
    --validation-only           Run only validation tests
    --modules MODULE...         Run tests from specific modules
    --patterns PATTERN...       Run tests matching patterns

Connection Options:
    --unreal-host HOST          Unreal Engine host (default: $DEFAULT_UNREAL_HOST)
    --unreal-port PORT          Unreal Engine port (default: $DEFAULT_UNREAL_PORT)
    --mock                      Use mock Unreal server
    --timeout SECONDS           Test timeout in seconds (default: $DEFAULT_TIMEOUT)

Execution Options:
    --parallel                  Run tests in parallel
    --max-workers N             Maximum parallel workers (default: 4)
    --python PYTHON             Python command to use (default: $DEFAULT_PYTHON)

Output Options:
    --verbose                   Verbose output
    --quiet                     Quiet output
    --generate-reports          Generate detailed test reports
    --output-dir DIR            Output directory (default: $DEFAULT_OUTPUT_DIR)

Environment Options:
    --ci                        CI-optimized execution
    --setup-env                 Set up test environment
    --cleanup                   Clean up test artifacts

Examples:
    $0 --mock --parallel                        # All tests with mock server
    $0 --integration-only --unreal-host server  # Integration tests on remote host  
    $0 --use-pytest --verbose                   # Use pytest with verbose output
    $0 --ci --generate-reports                  # CI execution with reports
    $0 --test-connection                        # Test connection only

EOF
}

# Environment setup
setup_environment() {
    log_info "Setting up test environment..."
    
    cd "$PYTHON_DIR"
    
    # Check if uv is available
    if command -v uv &> /dev/null; then
        log_info "Using uv for dependency management"
        uv sync --dev
    elif command -v pip &> /dev/null; then
        log_info "Using pip for dependency management"
        pip install -e .
    else
        log_error "Neither uv nor pip found. Please install Python package manager."
        exit 1
    fi
    
    log_success "Environment setup complete"
}

# Dependency checking
check_dependencies() {
    log_info "Checking dependencies..."
    
    # Check Python
    if ! command -v "$PYTHON_CMD" &> /dev/null; then
        log_error "Python command '$PYTHON_CMD' not found"
        return 1
    fi
    
    # Check Python version
    PYTHON_VERSION=$($PYTHON_CMD --version 2>&1 | cut -d' ' -f2)
    log_info "Using Python $PYTHON_VERSION"
    
    # Check if we're in the right directory
    if [[ ! -f "$PYTHON_DIR/unreal_mcp_server.py" ]]; then
        log_error "unreal_mcp_server.py not found in $PYTHON_DIR"
        log_error "Please run this script from the correct directory"
        return 1
    fi
    
    # Check Python imports
    cd "$PYTHON_DIR"
    if ! $PYTHON_CMD -c "import mcp; import pytest" 2>/dev/null; then
        log_warning "Some dependencies missing. Run with --setup-env to install."
        if [[ "$AUTO_SETUP" == "true" ]]; then
            setup_environment
        else
            return 1
        fi
    fi
    
    log_success "Dependencies check passed"
    return 0
}

# Cleanup function
cleanup_artifacts() {
    log_info "Cleaning up test artifacts..."
    
    cd "$PYTHON_DIR"
    
    # Remove test output directories
    rm -rf test_output/ comprehensive_test_output/ sample_test_output/
    rm -f pytest_execution.log test_execution.log unreal_mcp.log
    rm -rf .pytest_cache/ __pycache__/
    find . -name "*.pyc" -delete
    find . -name "*.pyo" -delete
    
    log_success "Cleanup complete"
}

# Test connection function
test_connection() {
    log_info "Testing connection to Unreal Engine..."
    
    cd "$PYTHON_DIR"
    
    local test_args=("--test-connection")
    
    if [[ "$USE_MOCK" == "true" ]]; then
        test_args+=("--mock")
    fi
    
    test_args+=("--unreal-host" "$UNREAL_HOST")
    test_args+=("--unreal-port" "$UNREAL_PORT")
    
    if [[ "$VERBOSE" == "true" ]]; then
        test_args+=("--verbose")
    fi
    
    $PYTHON_CMD tests/run_tests.py "${test_args[@]}"
    return $?
}

# Main test execution function
run_tests() {
    log_info "Starting test execution..."
    
    cd "$PYTHON_DIR"
    
    local test_args=()
    
    # Framework selection
    if [[ "$USE_PYTEST" == "true" ]]; then
        test_args+=("--use-pytest")
    fi
    
    # Test filtering
    if [[ "$INTEGRATION_ONLY" == "true" ]]; then
        test_args+=("--integration-only")
    elif [[ "$UNIT_ONLY" == "true" ]]; then
        test_args+=("--unit-only")
    elif [[ "$VALIDATION_ONLY" == "true" ]]; then
        test_args+=("--validation-only")
    fi
    
    # Connection options
    if [[ "$USE_MOCK" == "true" ]]; then
        test_args+=("--mock")
    fi
    
    test_args+=("--unreal-host" "$UNREAL_HOST")
    test_args+=("--unreal-port" "$UNREAL_PORT")
    test_args+=("--timeout" "$TIMEOUT")
    
    # Execution options
    if [[ "$PARALLEL" == "true" ]]; then
        test_args+=("--parallel")
    fi
    
    if [[ -n "$MAX_WORKERS" ]]; then
        test_args+=("--max-workers" "$MAX_WORKERS")
    fi
    
    # Output options
    if [[ "$VERBOSE" == "true" ]]; then
        test_args+=("--verbose")
    elif [[ "$QUIET" == "true" ]]; then
        test_args+=("--quiet")
    fi
    
    if [[ "$GENERATE_REPORTS" == "true" ]]; then
        test_args+=("--generate-reports")
    fi
    
    if [[ -n "$OUTPUT_DIR" ]]; then
        test_args+=("--output-dir" "$OUTPUT_DIR")
    fi
    
    # Add modules if specified
    if [[ ${#MODULES[@]} -gt 0 ]]; then
        test_args+=("--modules" "${MODULES[@]}")
    fi
    
    # Add patterns if specified
    if [[ ${#PATTERNS[@]} -gt 0 ]]; then
        test_args+=("--patterns" "${PATTERNS[@]}")
    fi
    
    log_info "Running: $PYTHON_CMD tests/run_tests.py ${test_args[*]}"
    
    # Execute tests
    local start_time=$(date +%s)
    
    if $PYTHON_CMD tests/run_tests.py "${test_args[@]}"; then
        local end_time=$(date +%s)
        local duration=$((end_time - start_time))
        log_success "Tests completed successfully in ${duration}s"
        return 0
    else
        local end_time=$(date +%s)
        local duration=$((end_time - start_time))
        log_error "Tests failed after ${duration}s"
        return 1
    fi
}

# CI-optimized execution
run_ci_tests() {
    log_info "Running CI-optimized tests..."
    
    # Set CI-specific defaults
    USE_MOCK="true"
    PARALLEL="true"
    GENERATE_REPORTS="true"
    QUIET="true"
    
    # Set environment variables for CI
    export CI=true
    export TEST_USE_MOCK=true
    export TEST_PARALLEL=true
    
    # Run tests
    run_tests
    local result=$?
    
    # Generate additional CI outputs
    if [[ "$result" -eq 0 ]]; then
        log_success "CI tests passed"
        
        # Create CI-specific outputs
        cd "$PYTHON_DIR"
        if [[ -d "$OUTPUT_DIR" ]]; then
            # Create test summary for CI
            echo "TEST_STATUS=passed" >> "${OUTPUT_DIR}/ci_summary.txt"
            echo "TEST_TIMESTAMP=$(date -Iseconds)" >> "${OUTPUT_DIR}/ci_summary.txt"
        fi
    else
        log_error "CI tests failed"
        
        # Create failure summary
        cd "$PYTHON_DIR"
        if [[ -d "$OUTPUT_DIR" ]]; then
            echo "TEST_STATUS=failed" >> "${OUTPUT_DIR}/ci_summary.txt"
            echo "TEST_TIMESTAMP=$(date -Iseconds)" >> "${OUTPUT_DIR}/ci_summary.txt"
        fi
    fi
    
    return $result
}

# Parse command line arguments
PYTHON_CMD="$DEFAULT_PYTHON"
UNREAL_HOST="$DEFAULT_UNREAL_HOST"
UNREAL_PORT="$DEFAULT_UNREAL_PORT"
TIMEOUT="$DEFAULT_TIMEOUT"
OUTPUT_DIR="$DEFAULT_OUTPUT_DIR"

USE_PYTEST="false"
TEST_CONNECTION_ONLY="false"
GENERATE_SAMPLE_REPORTS="false"
INTEGRATION_ONLY="false"
UNIT_ONLY="false"
VALIDATION_ONLY="false"
USE_MOCK="false"
PARALLEL="false"
MAX_WORKERS=""
VERBOSE="false"
QUIET="false"
GENERATE_REPORTS="false"
CI_MODE="false"
SETUP_ENV="false"
CLEANUP="false"
AUTO_SETUP="false"

MODULES=()
PATTERNS=()

while [[ $# -gt 0 ]]; do
    case $1 in
        --help|-h)
            show_help
            exit 0
            ;;
        --use-pytest)
            USE_PYTEST="true"
            shift
            ;;
        --test-connection)
            TEST_CONNECTION_ONLY="true"
            shift
            ;;
        --generate-sample-reports)
            GENERATE_SAMPLE_REPORTS="true"
            shift
            ;;
        --integration-only)
            INTEGRATION_ONLY="true"
            shift
            ;;
        --unit-only)
            UNIT_ONLY="true"
            shift
            ;;
        --validation-only)
            VALIDATION_ONLY="true"
            shift
            ;;
        --modules)
            shift
            while [[ $# -gt 0 && $1 != --* ]]; do
                MODULES+=("$1")
                shift
            done
            ;;
        --patterns)
            shift
            while [[ $# -gt 0 && $1 != --* ]]; do
                PATTERNS+=("$1")
                shift
            done
            ;;
        --unreal-host)
            UNREAL_HOST="$2"
            shift 2
            ;;
        --unreal-port)
            UNREAL_PORT="$2"
            shift 2
            ;;
        --mock)
            USE_MOCK="true"
            shift
            ;;
        --timeout)
            TIMEOUT="$2"
            shift 2
            ;;
        --parallel)
            PARALLEL="true"
            shift
            ;;
        --max-workers)
            MAX_WORKERS="$2"
            shift 2
            ;;
        --python)
            PYTHON_CMD="$2"
            shift 2
            ;;
        --verbose)
            VERBOSE="true"
            shift
            ;;
        --quiet)
            QUIET="true"
            shift
            ;;
        --generate-reports)
            GENERATE_REPORTS="true"
            shift
            ;;
        --output-dir)
            OUTPUT_DIR="$2"
            shift 2
            ;;
        --ci)
            CI_MODE="true"
            AUTO_SETUP="true"
            shift
            ;;
        --setup-env)
            SETUP_ENV="true"
            shift
            ;;
        --cleanup)
            CLEANUP="true"
            shift
            ;;
        *)
            log_error "Unknown option: $1"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

# Main execution
main() {
    log_info "Unreal MCP Test Runner starting..."
    
    # Handle cleanup request
    if [[ "$CLEANUP" == "true" ]]; then
        cleanup_artifacts
        exit 0
    fi
    
    # Handle environment setup
    if [[ "$SETUP_ENV" == "true" ]]; then
        setup_environment
        exit 0
    fi
    
    # Check dependencies
    if ! check_dependencies; then
        log_error "Dependency check failed"
        exit 1
    fi
    
    # Handle special modes
    if [[ "$TEST_CONNECTION_ONLY" == "true" ]]; then
        test_connection
        exit $?
    fi
    
    if [[ "$GENERATE_SAMPLE_REPORTS" == "true" ]]; then
        cd "$PYTHON_DIR"
        $PYTHON_CMD tests/run_tests.py --generate-sample-reports --output-dir "$OUTPUT_DIR"
        exit $?
    fi
    
    # Validate exclusive options
    local exclusive_count=0
    [[ "$INTEGRATION_ONLY" == "true" ]] && ((exclusive_count++))
    [[ "$UNIT_ONLY" == "true" ]] && ((exclusive_count++))
    [[ "$VALIDATION_ONLY" == "true" ]] && ((exclusive_count++))
    
    if [[ $exclusive_count -gt 1 ]]; then
        log_error "Only one of --integration-only, --unit-only, --validation-only can be specified"
        exit 1
    fi
    
    # Run tests
    if [[ "$CI_MODE" == "true" ]]; then
        run_ci_tests
    else
        run_tests
    fi
    
    local result=$?
    
    if [[ $result -eq 0 ]]; then
        log_success "Test execution completed successfully"
    else
        log_error "Test execution failed"
    fi
    
    exit $result
}

# Execute main function
main "$@"