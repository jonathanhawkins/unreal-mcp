"""
Unreal MCP Testing Framework

A comprehensive testing framework for Unreal Engine Model Context Protocol (MCP) tools.

This package provides:
- Integration tests for Unreal Engine MCP tools
- Unit tests for Python tool functions  
- Validation tests for data handling and error conditions
- Mock server capabilities for offline testing
- Parallel test execution with load balancing
- Comprehensive result reporting in multiple formats
- CI/CD integration support

Test Categories:
- integration/: Tests that interact with actual Unreal Engine via TCP
- unit/: Tests for Python code logic without Unreal dependency
- validation/: Tests for data validation, error handling, edge cases
- fixtures/: Shared test fixtures and utilities
- data/: Test data sets and sample assets
- mocks/: Mock implementations for testing

Usage:
    # Run all tests
    python -m pytest tests/
    
    # Run specific category
    python -m pytest tests/integration/
    
    # Run with custom framework
    python tests/run_tests.py --parallel --integration-only
    
    # Use mock server
    python -m pytest tests/ --use-mock
"""

__version__ = "1.0.0"
__author__ = "Unreal MCP Framework"

# Import test utilities only if they exist
try:
    from .test_framework import TestFramework, TestConfig, create_test_config
except ImportError:
    pass

try:
    from .test_runner import ParallelTestRunner, TestFilter, run_filtered_tests
except ImportError:
    pass

try:
    from .test_results import TestResultCollector, TestResultReporter, DetailedTestResult
except ImportError:
    pass

__all__ = [
    'TestFramework',
    'TestConfig', 
    'create_test_config',
    'ParallelTestRunner',
    'TestFilter',
    'run_filtered_tests',
    'TestResultCollector',
    'TestResultReporter', 
    'DetailedTestResult'
]