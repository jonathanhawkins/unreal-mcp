#!/usr/bin/env python3
"""
Main test execution script for Unreal MCP tools.

This script provides a unified interface for running tests with various
configurations and options. It supports both the custom test framework
and pytest integration.

Usage:
    python run_tests.py [OPTIONS]
    
Examples:
    # Run all tests with mock server
    python run_tests.py --mock --parallel
    
    # Run only integration tests
    python run_tests.py --integration-only --unreal-host 192.168.1.100
    
    # Run specific test modules
    python run_tests.py --modules actor_tests blueprint_tests
    
    # Run with pytest
    python run_tests.py --use-pytest --verbose
    
    # Generate comprehensive reports
    python run_tests.py --generate-reports --output-dir ./test_results
"""

import argparse
import logging
import os
import sys
import time
from pathlib import Path
from typing import Optional, List

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from test_framework import TestFramework, TestConfig, create_test_config
from test_runner import ParallelTestRunner, TestFilter, run_filtered_tests
from test_results import TestResultReporter, create_sample_results

def setup_logging(verbose: bool = False, log_file: str = None):
    """Setup logging configuration."""
    level = logging.DEBUG if verbose else logging.INFO
    handlers = [logging.StreamHandler(sys.stdout)]
    
    if log_file:
        handlers.append(logging.FileHandler(log_file))
    
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=handlers
    )

def check_dependencies():
    """Check if required dependencies are available."""
    try:
        import pytest
        import mcp
    except ImportError as e:
        print(f"Error: Missing required dependency: {e}")
        print("Please install dependencies with: uv pip install -e .")
        return False
    return True

def run_with_pytest(args) -> int:
    """Run tests using pytest."""
    import subprocess
    
    pytest_args = ["python", "-m", "pytest", "tests/"]
    
    # Add pytest-specific arguments
    if args.verbose:
        pytest_args.extend(["-v", "-s"])
    
    if args.integration_only:
        pytest_args.append("--integration-only")
    elif args.unit_only:
        pytest_args.append("--unit-only")
    elif args.validation_only:
        pytest_args.append("--validation-only")
    
    if args.mock:
        pytest_args.append("--use-mock")
    
    if args.unreal_host != "127.0.0.1":
        pytest_args.extend(["--unreal-host", args.unreal_host])
    
    if args.unreal_port != 55557:
        pytest_args.extend(["--unreal-port", str(args.unreal_port)])
    
    if args.parallel and not args.integration_only:
        pytest_args.extend(["-n", str(args.max_workers)])
    
    if args.timeout:
        pytest_args.extend(["--test-timeout", str(args.timeout)])
    
    # Output options
    if args.generate_reports:
        pytest_args.extend([
            "--html=test_output/pytest_report.html",
            "--json-report", "--json-report-file=test_output/pytest_results.json"
        ])
    
    print(f"Running pytest with args: {' '.join(pytest_args[2:])}")
    result = subprocess.run(pytest_args, cwd=os.path.dirname(__file__))
    return result.returncode

def run_with_custom_framework(args) -> int:
    """Run tests using the custom test framework."""
    # Create test filter
    filter_criteria = TestFilter(
        integration_only=args.integration_only,
        unit_only=args.unit_only,
        validation_only=args.validation_only,
        modules=args.modules,
        patterns=args.patterns,
        exclude_modules=args.exclude_modules,
        exclude_patterns=args.exclude_patterns
    )
    
    # Create test configuration
    config = create_test_config(
        use_mock=args.mock,
        unreal_host=args.unreal_host,
        unreal_port=args.unreal_port,
        connection_timeout=args.connection_timeout,
        command_timeout=args.timeout,
        parallel_execution=args.parallel,
        max_workers=args.max_workers,
        cleanup_on_failure=args.cleanup_on_failure,
        retry_failed_connections=args.retry_connections,
        max_connection_retries=args.max_retries
    )
    
    # Run tests
    print("Starting Unreal MCP test execution...")
    print(f"Configuration: Mock={config.use_mock_server}, Parallel={config.parallel_execution}")
    print(f"Host: {config.unreal_host}:{config.unreal_port}")
    
    try:
        stats = run_filtered_tests(filter_criteria, config, args.parallel)
        
        # Generate reports if requested
        if args.generate_reports:
            # Create sample results for demonstration
            # In real usage, this would be the actual test results
            from test_results import TestResultCollector
            
            # For demo purposes, create results based on stats
            collector = TestResultCollector()
            collector.start_test_run(config.__dict__)
            
            # Add sample results (in real usage, this would be collected during test execution)
            collector.start_suite("integration", "integration")
            for i in range(stats.passed):
                collector.add_test_result(f"test_integration_{i}", True, 1.0)
            for i in range(stats.failed):
                collector.add_test_result(f"test_failed_{i}", False, 0.5, "Test failed")
            collector.complete_suite()
            
            results = collector.complete_test_run()
            reporter = TestResultReporter(results)
            
            output_dir = args.output_dir or "test_output"
            reporter.save_reports(output_dir)
            print(f"\nTest reports saved to {output_dir}/")
        
        # Print summary
        print(f"\n{'='*60}")
        print(f"TEST EXECUTION SUMMARY")
        print(f"{'='*60}")
        print(f"Total Tests: {stats.total_tests}")
        print(f"Passed: {stats.passed}")
        print(f"Failed: {stats.failed}")
        print(f"Errors: {stats.errors}")
        print(f"Skipped: {stats.skipped}")
        print(f"Success Rate: {stats.success_rate:.1%}")
        print(f"Duration: {stats.total_duration:.2f}s")
        
        # Return appropriate exit code
        if stats.failed > 0 or stats.errors > 0:
            return 1
        else:
            return 0
            
    except KeyboardInterrupt:
        print("\nTest execution interrupted by user")
        return 130
    except Exception as e:
        print(f"Error during test execution: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1

def run_connection_test(args) -> bool:
    """Test connection to Unreal Engine."""
    config = create_test_config(
        use_mock=args.mock,
        unreal_host=args.unreal_host,
        unreal_port=args.unreal_port,
        connection_timeout=args.connection_timeout
    )
    
    framework = TestFramework(config)
    
    print(f"Testing connection to Unreal Engine at {config.unreal_host}:{config.unreal_port}")
    
    if config.use_mock_server:
        print("Using mock server mode")
        return True
    
    success = framework.test_unreal_connection()
    
    if success:
        print("✅ Connection successful")
        return True
    else:
        print("❌ Connection failed")
        return False

def generate_sample_reports(args):
    """Generate sample test reports for demonstration."""
    print("Generating sample test reports...")
    
    results = create_sample_results()
    reporter = TestResultReporter(results)
    
    output_dir = args.output_dir or "sample_test_output"
    reporter.save_reports(output_dir)
    
    print(f"Sample reports generated in {output_dir}/")
    print(f"  - Console report: {output_dir}/test_report.txt")
    print(f"  - HTML report: {output_dir}/test_report.html")
    print(f"  - JSON results: {output_dir}/test_results.json")
    print(f"  - JUnit XML: {output_dir}/test_results.xml")

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Unreal MCP Test Runner",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --mock --parallel                          # Run all tests with mock server
  %(prog)s --integration-only --unreal-host 192.168.1.100  # Integration tests on remote host
  %(prog)s --modules actor_tests --patterns test_spawn     # Run specific tests
  %(prog)s --use-pytest --verbose                          # Use pytest with verbose output
  %(prog)s --test-connection                               # Test Unreal connection only
  %(prog)s --generate-sample-reports                       # Generate sample reports
        """
    )
    
    # Test execution options
    test_group = parser.add_argument_group("Test Execution")
    test_group.add_argument("--use-pytest", action="store_true", 
                           help="Use pytest instead of custom framework")
    test_group.add_argument("--test-connection", action="store_true",
                           help="Test Unreal connection only")
    test_group.add_argument("--generate-sample-reports", action="store_true",
                           help="Generate sample test reports")
    
    # Test filtering options
    filter_group = parser.add_argument_group("Test Filtering")
    filter_group.add_argument("--integration-only", action="store_true",
                             help="Run only integration tests")
    filter_group.add_argument("--unit-only", action="store_true", 
                             help="Run only unit tests")
    filter_group.add_argument("--validation-only", action="store_true",
                             help="Run only validation tests")
    filter_group.add_argument("--modules", nargs="*", metavar="MODULE",
                             help="Run tests from specific modules")
    filter_group.add_argument("--patterns", nargs="*", metavar="PATTERN",
                             help="Run tests matching patterns")
    filter_group.add_argument("--exclude-modules", nargs="*", metavar="MODULE",
                             help="Exclude tests from specific modules")
    filter_group.add_argument("--exclude-patterns", nargs="*", metavar="PATTERN",
                             help="Exclude tests matching patterns")
    
    # Connection options
    conn_group = parser.add_argument_group("Connection Options")
    conn_group.add_argument("--unreal-host", default="127.0.0.1", metavar="HOST",
                           help="Unreal Engine host address (default: 127.0.0.1)")
    conn_group.add_argument("--unreal-port", type=int, default=55557, metavar="PORT",
                           help="Unreal Engine port number (default: 55557)")
    conn_group.add_argument("--mock", action="store_true",
                           help="Use mock Unreal server for testing")
    conn_group.add_argument("--connection-timeout", type=float, default=10.0, metavar="SECONDS",
                           help="Connection timeout in seconds (default: 10)")
    conn_group.add_argument("--timeout", type=float, default=30.0, metavar="SECONDS",
                           help="Individual test timeout in seconds (default: 30)")
    conn_group.add_argument("--retry-connections", action="store_true", default=True,
                           help="Retry failed connections (default: True)")
    conn_group.add_argument("--max-retries", type=int, default=3, metavar="N",
                           help="Maximum connection retries (default: 3)")
    
    # Execution options
    exec_group = parser.add_argument_group("Execution Options")
    exec_group.add_argument("--parallel", action="store_true", default=True,
                           help="Run tests in parallel (default: True)")
    exec_group.add_argument("--max-workers", type=int, default=4, metavar="N",
                           help="Maximum parallel workers (default: 4)")
    exec_group.add_argument("--cleanup-on-failure", action="store_true", default=True,
                           help="Clean up resources on test failure (default: True)")
    
    # Output options
    output_group = parser.add_argument_group("Output Options")
    output_group.add_argument("--verbose", "-v", action="store_true",
                             help="Verbose output")
    output_group.add_argument("--quiet", "-q", action="store_true",
                             help="Quiet output")
    output_group.add_argument("--generate-reports", action="store_true",
                             help="Generate detailed test reports")
    output_group.add_argument("--output-dir", metavar="DIR",
                             help="Output directory for reports (default: test_output)")
    output_group.add_argument("--log-file", metavar="FILE",
                             help="Log file path")
    
    args = parser.parse_args()
    
    # Setup logging
    if not args.quiet:
        setup_logging(args.verbose, args.log_file)
    
    # Check dependencies
    if not check_dependencies():
        return 1
    
    # Handle special modes
    if args.test_connection:
        success = run_connection_test(args)
        return 0 if success else 1
    
    if args.generate_sample_reports:
        generate_sample_reports(args)
        return 0
    
    # Validate arguments
    exclusive_filters = sum([args.integration_only, args.unit_only, args.validation_only])
    if exclusive_filters > 1:
        print("Error: Only one of --integration-only, --unit-only, --validation-only can be specified")
        return 1
    
    # Run tests
    try:
        if args.use_pytest:
            return run_with_pytest(args)
        else:
            return run_with_custom_framework(args)
    except KeyboardInterrupt:
        print("\nTest execution interrupted")
        return 130
    except Exception as e:
        print(f"Fatal error: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)