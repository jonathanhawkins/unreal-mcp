"""
Parallel test execution system for Unreal MCP tools.

Provides capabilities for:
- Parallel test execution with worker management
- Test discovery and filtering
- Load balancing across test categories
- Progress tracking and real-time reporting
- Error handling and recovery
"""

import asyncio
import concurrent.futures
import os
import sys
import time
import traceback
import importlib.util
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Dict, Any, Optional, Callable, Set, Tuple
import threading
import queue
import logging
from collections import defaultdict

from test_framework import TestFramework, TestResult, TestConfig

logger = logging.getLogger(__name__)

@dataclass
class TestFilter:
    """Filter criteria for test selection."""
    modules: Optional[List[str]] = None  # Module names to include
    patterns: Optional[List[str]] = None  # Name patterns to match
    tags: Optional[List[str]] = None     # Test tags to include
    exclude_modules: Optional[List[str]] = None
    exclude_patterns: Optional[List[str]] = None
    exclude_tags: Optional[List[str]] = None
    integration_only: bool = False
    unit_only: bool = False
    validation_only: bool = False

@dataclass
class TestSuite:
    """A collection of tests to execute."""
    name: str
    test_functions: List[Tuple[Callable, str]]  # (function, test_name)
    setup_functions: List[Callable] = field(default_factory=list)
    teardown_functions: List[Callable] = field(default_factory=list)
    config: Optional[TestConfig] = None
    parallel_safe: bool = True  # Whether tests can run in parallel
    timeout: Optional[float] = None  # Suite-specific timeout
    
@dataclass
class TestExecutionStats:
    """Statistics for test execution."""
    total_tests: int = 0
    passed: int = 0
    failed: int = 0
    skipped: int = 0
    errors: int = 0
    total_duration: float = 0.0
    start_time: Optional[float] = None
    end_time: Optional[float] = None
    
    @property
    def success_rate(self) -> float:
        """Calculate success rate."""
        if self.total_tests == 0:
            return 0.0
        return self.passed / self.total_tests
        
    @property
    def completion_rate(self) -> float:
        """Calculate completion rate (non-skipped tests)."""
        if self.total_tests == 0:
            return 0.0
        return (self.passed + self.failed + self.errors) / self.total_tests

class TestDiscovery:
    """Discover and load test functions from the test directory."""
    
    def __init__(self, test_directory: str):
        self.test_directory = Path(test_directory)
        self.discovered_tests = {}
        
    def discover_tests(self, filter_criteria: Optional[TestFilter] = None) -> Dict[str, TestSuite]:
        """Discover all test functions in the test directory."""
        test_suites = {}
        
        # Discover integration tests
        integration_dir = self.test_directory / "integration"
        if integration_dir.exists():
            integration_tests = self._discover_in_directory(integration_dir, "integration")
            if integration_tests:
                test_suites["integration"] = TestSuite(
                    name="integration",
                    test_functions=integration_tests,
                    parallel_safe=False,  # Integration tests might conflict
                    timeout=300.0  # 5 minutes for integration tests
                )
        
        # Discover unit tests
        unit_dir = self.test_directory / "unit"
        if unit_dir.exists():
            unit_tests = self._discover_in_directory(unit_dir, "unit")
            if unit_tests:
                test_suites["unit"] = TestSuite(
                    name="unit",
                    test_functions=unit_tests,
                    parallel_safe=True,  # Unit tests should be independent
                    timeout=60.0  # 1 minute for unit tests
                )
        
        # Discover validation tests
        validation_dir = self.test_directory / "validation"
        if validation_dir.exists():
            validation_tests = self._discover_in_directory(validation_dir, "validation")
            if validation_tests:
                test_suites["validation"] = TestSuite(
                    name="validation",
                    test_functions=validation_tests,
                    parallel_safe=True,
                    timeout=120.0  # 2 minutes for validation tests
                )
        
        # Apply filters
        if filter_criteria:
            test_suites = self._apply_filters(test_suites, filter_criteria)
            
        return test_suites
        
    def _discover_in_directory(self, directory: Path, category: str) -> List[Tuple[Callable, str]]:
        """Discover test functions in a specific directory."""
        test_functions = []
        
        for py_file in directory.rglob("test_*.py"):
            try:
                module_name = f"tests.{category}.{py_file.stem}"
                spec = importlib.util.spec_from_file_location(module_name, py_file)
                if spec and spec.loader:
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)
                    
                    # Find test functions
                    for attr_name in dir(module):
                        if attr_name.startswith("test_"):
                            attr = getattr(module, attr_name)
                            if callable(attr):
                                test_name = f"{py_file.stem}.{attr_name}"
                                test_functions.append((attr, test_name))
                                
            except Exception as e:
                logger.error(f"Failed to load test module {py_file}: {e}")
                
        return test_functions
        
    def _apply_filters(self, test_suites: Dict[str, TestSuite], filter_criteria: TestFilter) -> Dict[str, TestSuite]:
        """Apply filter criteria to test suites."""
        filtered_suites = {}
        
        for suite_name, suite in test_suites.items():
            # Apply suite-level filters
            if filter_criteria.integration_only and suite_name != "integration":
                continue
            if filter_criteria.unit_only and suite_name != "unit":
                continue
            if filter_criteria.validation_only and suite_name != "validation":
                continue
                
            # Filter test functions within suite
            filtered_functions = []
            for test_func, test_name in suite.test_functions:
                if self._should_include_test(test_name, filter_criteria):
                    filtered_functions.append((test_func, test_name))
                    
            if filtered_functions:
                filtered_suite = TestSuite(
                    name=suite.name,
                    test_functions=filtered_functions,
                    setup_functions=suite.setup_functions,
                    teardown_functions=suite.teardown_functions,
                    config=suite.config,
                    parallel_safe=suite.parallel_safe,
                    timeout=suite.timeout
                )
                filtered_suites[suite_name] = filtered_suite
                
        return filtered_suites
        
    def _should_include_test(self, test_name: str, filter_criteria: TestFilter) -> bool:
        """Check if a test should be included based on filter criteria."""
        # Check module filters
        if filter_criteria.modules:
            if not any(module in test_name for module in filter_criteria.modules):
                return False
                
        if filter_criteria.exclude_modules:
            if any(module in test_name for module in filter_criteria.exclude_modules):
                return False
                
        # Check pattern filters
        if filter_criteria.patterns:
            if not any(pattern in test_name for pattern in filter_criteria.patterns):
                return False
                
        if filter_criteria.exclude_patterns:
            if any(pattern in test_name for pattern in filter_criteria.exclude_patterns):
                return False
                
        return True

class TestProgressReporter:
    """Report test progress in real-time."""
    
    def __init__(self, enable_live_updates: bool = True):
        self.enable_live_updates = enable_live_updates
        self.stats = TestExecutionStats()
        self.current_suite = None
        self.current_test = None
        self.progress_lock = threading.Lock()
        self.completed_tests = []
        
    def start_execution(self, total_tests: int):
        """Start test execution tracking."""
        with self.progress_lock:
            self.stats = TestExecutionStats(total_tests=total_tests)
            self.stats.start_time = time.time()
            
        logger.info(f"Starting execution of {total_tests} tests")
        
    def start_suite(self, suite_name: str):
        """Start tracking a test suite."""
        with self.progress_lock:
            self.current_suite = suite_name
            
        if self.enable_live_updates:
            print(f"\n=== Starting {suite_name} tests ===")
            
    def start_test(self, test_name: str):
        """Start tracking a single test."""
        with self.progress_lock:
            self.current_test = test_name
            
        if self.enable_live_updates:
            print(f"Running: {test_name}", end="", flush=True)
            
    def complete_test(self, result: TestResult):
        """Complete tracking of a test."""
        with self.progress_lock:
            self.completed_tests.append(result)
            if result.success:
                self.stats.passed += 1
                status = "PASS"
            elif result.skipped:
                self.stats.skipped += 1
                status = f"SKIP ({result.skip_reason})"
            elif result.error:
                if "assertion" in result.error.lower():
                    self.stats.failed += 1
                    status = "FAIL"
                else:
                    self.stats.errors += 1
                    status = "ERROR"
            else:
                self.stats.errors += 1
                status = "ERROR"
                
            self.stats.total_duration += result.duration
            
        if self.enable_live_updates:
            duration_str = f" ({result.duration:.2f}s)"
            print(f" - {status}{duration_str}")
            if result.error:
                print(f"  Error: {result.error}")
                
        # Progress summary
        completed = self.stats.passed + self.stats.failed + self.stats.skipped + self.stats.errors
        if self.enable_live_updates and completed % 5 == 0:  # Every 5 tests
            self._print_progress_summary(completed)
            
    def complete_execution(self):
        """Complete test execution tracking."""
        with self.progress_lock:
            self.stats.end_time = time.time()
            
        self._print_final_summary()
        
    def _print_progress_summary(self, completed: int):
        """Print a progress summary."""
        total = self.stats.total_tests
        percentage = (completed / total) * 100 if total > 0 else 0
        print(f"\nProgress: {completed}/{total} ({percentage:.1f}%) - "
              f"Pass: {self.stats.passed}, Fail: {self.stats.failed}, "
              f"Skip: {self.stats.skipped}, Error: {self.stats.errors}")
        
    def _print_final_summary(self):
        """Print final execution summary."""
        stats = self.stats
        duration = (stats.end_time - stats.start_time) if stats.start_time and stats.end_time else 0
        
        print("\n" + "="*60)
        print(f"Test Execution Summary")
        print("="*60)
        print(f"Total Tests: {stats.total_tests}")
        print(f"Passed: {stats.passed}")
        print(f"Failed: {stats.failed}")
        print(f"Skipped: {stats.skipped}")
        print(f"Errors: {stats.errors}")
        print(f"Success Rate: {stats.success_rate:.1%}")
        print(f"Total Duration: {duration:.2f}s")
        print(f"Average Test Duration: {stats.total_duration / max(stats.total_tests, 1):.2f}s")
        
        if stats.failed > 0 or stats.errors > 0:
            print("\nFailed/Error Tests:")
            for result in self.completed_tests:
                if not result.success and not result.skipped:
                    print(f"  - {result.name}: {result.error}")

class ParallelTestRunner:
    """Execute tests in parallel with load balancing and error handling."""
    
    def __init__(self, config: TestConfig = None):
        self.config = config or TestConfig()
        self.discovery = TestDiscovery(os.path.join(os.path.dirname(__file__)))
        self.reporter = TestProgressReporter()
        
    def run_tests(self, filter_criteria: Optional[TestFilter] = None) -> TestExecutionStats:
        """Run all discovered tests matching the filter criteria."""
        # Discover tests
        test_suites = self.discovery.discover_tests(filter_criteria)
        if not test_suites:
            logger.warning("No tests found matching filter criteria")
            return TestExecutionStats()
            
        # Calculate total test count
        total_tests = sum(len(suite.test_functions) for suite in test_suites.values())
        self.reporter.start_execution(total_tests)
        
        try:
            # Execute test suites
            for suite_name, suite in test_suites.items():
                self.reporter.start_suite(suite_name)
                self._run_test_suite(suite)
                
        finally:
            self.reporter.complete_execution()
            
        return self.reporter.stats
        
    def _run_test_suite(self, suite: TestSuite):
        """Run a single test suite."""
        if suite.parallel_safe and self.config.parallel_execution and len(suite.test_functions) > 1:
            self._run_suite_parallel(suite)
        else:
            self._run_suite_sequential(suite)
            
    def _run_suite_sequential(self, suite: TestSuite):
        """Run a test suite sequentially."""
        framework = TestFramework(suite.config or self.config)
        
        # Run setup functions
        for setup_func in suite.setup_functions:
            try:
                setup_func()
            except Exception as e:
                logger.error(f"Suite setup failed: {e}")
                # Mark all tests as skipped
                for test_func, test_name in suite.test_functions:
                    result = framework.skip_test(test_name, f"Setup failed: {e}")
                    self.reporter.complete_test(result)
                return
                
        # Run tests
        for test_func, test_name in suite.test_functions:
            self.reporter.start_test(test_name)
            try:
                result = asyncio.run(framework.run_test(test_func, test_name))
            except Exception as e:
                result = TestResult(
                    name=test_name,
                    success=False,
                    error=f"Test execution error: {str(e)}"
                )
            self.reporter.complete_test(result)
            
        # Run teardown functions
        for teardown_func in suite.teardown_functions:
            try:
                teardown_func()
            except Exception as e:
                logger.error(f"Suite teardown failed: {e}")
                
    def _run_suite_parallel(self, suite: TestSuite):
        """Run a test suite in parallel."""
        max_workers = min(self.config.max_workers, len(suite.test_functions))
        
        # Run setup functions first (sequential)
        for setup_func in suite.setup_functions:
            try:
                setup_func()
            except Exception as e:
                logger.error(f"Suite setup failed: {e}")
                # Mark all tests as skipped
                for test_func, test_name in suite.test_functions:
                    framework = TestFramework(suite.config or self.config)
                    result = framework.skip_test(test_name, f"Setup failed: {e}")
                    self.reporter.complete_test(result)
                return
        
        # Run tests in parallel
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_test = {}
            
            for test_func, test_name in suite.test_functions:
                future = executor.submit(self._run_single_test, test_func, test_name, suite.config or self.config)
                future_to_test[future] = test_name
                
            # Collect results as they complete
            for future in as_completed(future_to_test):
                test_name = future_to_test[future]
                try:
                    result = future.result(timeout=suite.timeout)
                    self.reporter.complete_test(result)
                except concurrent.futures.TimeoutError:
                    result = TestResult(
                        name=test_name,
                        success=False,
                        error="Test execution timeout"
                    )
                    self.reporter.complete_test(result)
                except Exception as e:
                    result = TestResult(
                        name=test_name,
                        success=False,
                        error=f"Test execution error: {str(e)}"
                    )
                    self.reporter.complete_test(result)
        
        # Run teardown functions (sequential)
        for teardown_func in suite.teardown_functions:
            try:
                teardown_func()
            except Exception as e:
                logger.error(f"Suite teardown failed: {e}")
                
    def _run_single_test(self, test_func: Callable, test_name: str, config: TestConfig) -> TestResult:
        """Run a single test function with its own framework instance."""
        framework = TestFramework(config)
        self.reporter.start_test(test_name)
        
        try:
            # Use asyncio.run for each test in its own thread
            return asyncio.run(framework.run_test(test_func, test_name))
        except Exception as e:
            return TestResult(
                name=test_name,
                success=False,
                error=f"Test execution error: {str(e)}"
            )

def run_test_discovery(test_dir: str = None) -> Dict[str, TestSuite]:
    """Run test discovery and return discovered test suites."""
    if test_dir is None:
        test_dir = os.path.dirname(__file__)
        
    discovery = TestDiscovery(test_dir)
    return discovery.discover_tests()

def run_filtered_tests(
    filter_criteria: Optional[TestFilter] = None,
    config: Optional[TestConfig] = None,
    parallel: bool = True
) -> TestExecutionStats:
    """Run tests with specified filters and configuration."""
    if config is None:
        config = TestConfig(parallel_execution=parallel)
    else:
        config.parallel_execution = parallel
        
    runner = ParallelTestRunner(config)
    return runner.run_tests(filter_criteria)

if __name__ == "__main__":
    # Example usage
    import argparse
    
    parser = argparse.ArgumentParser(description="Run Unreal MCP tests")
    parser.add_argument("--parallel", action="store_true", help="Run tests in parallel")
    parser.add_argument("--integration-only", action="store_true", help="Run only integration tests")
    parser.add_argument("--unit-only", action="store_true", help="Run only unit tests")
    parser.add_argument("--validation-only", action="store_true", help="Run only validation tests")
    parser.add_argument("--mock", action="store_true", help="Use mock Unreal server")
    parser.add_argument("--modules", nargs="*", help="Run only tests from specified modules")
    parser.add_argument("--patterns", nargs="*", help="Run only tests matching patterns")
    
    args = parser.parse_args()
    
    # Create filter
    filter_criteria = TestFilter(
        integration_only=args.integration_only,
        unit_only=args.unit_only,
        validation_only=args.validation_only,
        modules=args.modules,
        patterns=args.patterns
    )
    
    # Create config
    config = TestConfig(
        use_mock_server=args.mock,
        parallel_execution=args.parallel
    )
    
    # Run tests
    stats = run_filtered_tests(filter_criteria, config, args.parallel)
    
    # Exit with error code if tests failed
    if stats.failed > 0 or stats.errors > 0:
        sys.exit(1)
    else:
        sys.exit(0)