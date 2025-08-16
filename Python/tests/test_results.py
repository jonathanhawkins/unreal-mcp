"""
Test result collection and reporting system for Unreal MCP tools.

Provides comprehensive test result management including:
- Detailed result collection and aggregation
- Multiple output formats (JSON, XML, HTML, console)
- Historical test data tracking
- Performance metrics and trends
- CI/CD integration support
- Failure analysis and debugging information
"""

import json
import os
import time
import uuid
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
from xml.etree.ElementTree import Element, SubElement, tostring
import logging

logger = logging.getLogger(__name__)

@dataclass
class TestMetrics:
    """Performance and resource metrics for a test."""
    cpu_usage_percent: Optional[float] = None
    memory_usage_mb: Optional[float] = None
    tcp_connections: Optional[int] = None
    network_latency_ms: Optional[float] = None
    unreal_response_time_ms: Optional[float] = None

@dataclass 
class TestEnvironment:
    """Information about the test execution environment."""
    os_name: str = ""
    os_version: str = ""
    python_version: str = ""
    unreal_version: str = ""
    hostname: str = ""
    test_runner_version: str = "1.0.0"
    environment_variables: Dict[str, str] = field(default_factory=dict)
    
@dataclass
class DetailedTestResult:
    """Extended test result with comprehensive information."""
    # Basic test information
    id: str
    name: str
    suite: str
    category: str  # integration, unit, validation
    success: bool
    duration: float
    
    # Execution details
    start_time: datetime
    end_time: datetime
    error: Optional[str] = None
    error_type: Optional[str] = None
    traceback: Optional[str] = None
    
    # Test metadata
    tags: List[str] = field(default_factory=list)
    description: Optional[str] = None
    test_data: Dict[str, Any] = field(default_factory=dict)
    
    # Status flags
    skipped: bool = False
    skip_reason: Optional[str] = None
    retry_count: int = 0
    timeout: bool = False
    
    # Performance metrics
    metrics: Optional[TestMetrics] = None
    
    # Output capture
    stdout: List[str] = field(default_factory=list)
    stderr: List[str] = field(default_factory=list)
    logs: List[str] = field(default_factory=list)
    
    # Unreal-specific data
    unreal_commands: List[Dict[str, Any]] = field(default_factory=list)
    unreal_responses: List[Dict[str, Any]] = field(default_factory=list)
    actors_created: List[str] = field(default_factory=list)
    actors_deleted: List[str] = field(default_factory=list)
    
    @property
    def status(self) -> str:
        """Get test status string."""
        if self.skipped:
            return "skipped"
        elif self.success:
            return "passed"
        elif self.timeout:
            return "timeout"
        elif self.error:
            return "failed" if "assertion" in self.error.lower() else "error"
        else:
            return "error"
            
    @property
    def status_emoji(self) -> str:
        """Get emoji representation of status."""
        status_map = {
            "passed": "✅",
            "failed": "❌", 
            "error": "💥",
            "timeout": "⏰",
            "skipped": "⏭️"
        }
        return status_map.get(self.status, "❓")

@dataclass
class TestSuiteResults:
    """Results for an entire test suite."""
    name: str
    category: str
    tests: List[DetailedTestResult] = field(default_factory=list)
    setup_duration: float = 0.0
    teardown_duration: float = 0.0
    total_duration: float = 0.0
    
    @property
    def test_count(self) -> int:
        return len(self.tests)
        
    @property
    def passed_count(self) -> int:
        return sum(1 for test in self.tests if test.success)
        
    @property
    def failed_count(self) -> int:
        return sum(1 for test in self.tests if not test.success and not test.skipped and "assertion" in (test.error or "").lower())
        
    @property
    def error_count(self) -> int:
        return sum(1 for test in self.tests if not test.success and not test.skipped and "assertion" not in (test.error or "").lower())
        
    @property
    def skipped_count(self) -> int:
        return sum(1 for test in self.tests if test.skipped)
        
    @property
    def success_rate(self) -> float:
        return self.passed_count / max(self.test_count, 1)

@dataclass
class TestRunResults:
    """Complete results for a test run."""
    run_id: str
    start_time: datetime
    end_time: datetime
    environment: TestEnvironment
    suites: List[TestSuiteResults] = field(default_factory=list)
    configuration: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def total_duration(self) -> float:
        return (self.end_time - self.start_time).total_seconds()
        
    @property
    def total_tests(self) -> int:
        return sum(suite.test_count for suite in self.suites)
        
    @property
    def total_passed(self) -> int:
        return sum(suite.passed_count for suite in self.suites)
        
    @property
    def total_failed(self) -> int:
        return sum(suite.failed_count for suite in self.suites)
        
    @property
    def total_errors(self) -> int:
        return sum(suite.error_count for suite in self.suites)
        
    @property
    def total_skipped(self) -> int:
        return sum(suite.skipped_count for suite in self.suites)
        
    @property
    def success_rate(self) -> float:
        return self.total_passed / max(self.total_tests, 1)
        
    @property
    def all_tests(self) -> List[DetailedTestResult]:
        """Get all tests from all suites."""
        tests = []
        for suite in self.suites:
            tests.extend(suite.tests)
        return tests

class TestResultCollector:
    """Collect and aggregate test results during execution."""
    
    def __init__(self):
        self.run_id = str(uuid.uuid4())
        self.start_time = datetime.now(timezone.utc)
        self.current_suite = None
        self.current_suite_results = None
        self.suite_results = []
        self.environment = self._collect_environment()
        self.configuration = {}
        
    def start_test_run(self, configuration: Dict[str, Any] = None):
        """Start collecting results for a test run."""
        self.configuration = configuration or {}
        self.start_time = datetime.now(timezone.utc)
        logger.info(f"Started test run {self.run_id}")
        
    def start_suite(self, suite_name: str, category: str):
        """Start collecting results for a test suite."""
        if self.current_suite_results:
            # Complete previous suite
            self.complete_suite()
            
        self.current_suite = suite_name
        self.current_suite_results = TestSuiteResults(
            name=suite_name,
            category=category
        )
        logger.debug(f"Started suite {suite_name}")
        
    def add_test_result(self, 
                       test_name: str,
                       success: bool,
                       duration: float,
                       error: str = None,
                       **kwargs) -> DetailedTestResult:
        """Add a test result to the current suite."""
        if not self.current_suite_results:
            raise RuntimeError("No active test suite. Call start_suite() first.")
            
        result = DetailedTestResult(
            id=str(uuid.uuid4()),
            name=test_name,
            suite=self.current_suite,
            category=self.current_suite_results.category,
            success=success,
            duration=duration,
            start_time=datetime.now(timezone.utc) - timedelta(seconds=duration),
            end_time=datetime.now(timezone.utc),
            error=error,
            **kwargs
        )
        
        self.current_suite_results.tests.append(result)
        logger.debug(f"Added test result: {test_name} - {result.status}")
        return result
        
    def complete_suite(self):
        """Complete the current test suite."""
        if self.current_suite_results:
            self.current_suite_results.total_duration = sum(
                test.duration for test in self.current_suite_results.tests
            )
            self.suite_results.append(self.current_suite_results)
            logger.debug(f"Completed suite {self.current_suite}")
            self.current_suite_results = None
            self.current_suite = None
            
    def complete_test_run(self) -> TestRunResults:
        """Complete the test run and return final results."""
        if self.current_suite_results:
            self.complete_suite()
            
        end_time = datetime.now(timezone.utc)
        
        results = TestRunResults(
            run_id=self.run_id,
            start_time=self.start_time,
            end_time=end_time,
            environment=self.environment,
            suites=self.suite_results,
            configuration=self.configuration
        )
        
        logger.info(f"Completed test run {self.run_id}: "
                   f"{results.total_tests} tests, "
                   f"{results.total_passed} passed, "
                   f"{results.total_failed} failed, "
                   f"{results.total_errors} errors, "
                   f"{results.total_skipped} skipped")
                   
        return results
        
    def _collect_environment(self) -> TestEnvironment:
        """Collect information about the test environment."""
        import platform
        import sys
        import socket
        
        return TestEnvironment(
            os_name=platform.system(),
            os_version=platform.version(),
            python_version=sys.version,
            hostname=socket.gethostname(),
            environment_variables={
                k: v for k, v in os.environ.items() 
                if k.startswith(('UNREAL_', 'TEST_', 'CI_', 'GITHUB_'))
            }
        )

class TestResultReporter:
    """Generate reports in various formats from test results."""
    
    def __init__(self, results: TestRunResults):
        self.results = results
        
    def generate_console_report(self, verbose: bool = False) -> str:
        """Generate a console-friendly report."""
        lines = []
        lines.append("=" * 80)
        lines.append(f"TEST RUN SUMMARY - {self.results.run_id}")
        lines.append("=" * 80)
        lines.append(f"Started: {self.results.start_time.strftime('%Y-%m-%d %H:%M:%S UTC')}")
        lines.append(f"Duration: {self.results.total_duration:.2f}s")
        lines.append(f"Environment: {self.results.environment.os_name} {self.results.environment.os_version}")
        lines.append("")
        
        # Overall statistics
        lines.append("OVERALL RESULTS:")
        lines.append(f"  Total Tests: {self.results.total_tests}")
        lines.append(f"  Passed: {self.results.total_passed} ✅")
        lines.append(f"  Failed: {self.results.total_failed} ❌")
        lines.append(f"  Errors: {self.results.total_errors} 💥")
        lines.append(f"  Skipped: {self.results.total_skipped} ⏭️")
        lines.append(f"  Success Rate: {self.results.success_rate:.1%}")
        lines.append("")
        
        # Suite breakdown
        lines.append("SUITE BREAKDOWN:")
        for suite in self.results.suites:
            lines.append(f"  {suite.name} ({suite.category}):")
            lines.append(f"    Tests: {suite.test_count}, "
                        f"Passed: {suite.passed_count}, "
                        f"Failed: {suite.failed_count}, "
                        f"Errors: {suite.error_count}, "
                        f"Skipped: {suite.skipped_count}")
            lines.append(f"    Duration: {suite.total_duration:.2f}s, "
                        f"Success Rate: {suite.success_rate:.1%}")
            lines.append("")
            
        # Failed/error tests
        failed_tests = [test for test in self.results.all_tests if not test.success and not test.skipped]
        if failed_tests:
            lines.append("FAILED TESTS:")
            for test in failed_tests:
                lines.append(f"  {test.status_emoji} {test.name}")
                lines.append(f"    Error: {test.error}")
                if verbose and test.traceback:
                    lines.append(f"    Traceback: {test.traceback}")
                lines.append("")
                
        # Performance summary
        all_durations = [test.duration for test in self.results.all_tests if not test.skipped]
        if all_durations:
            lines.append("PERFORMANCE SUMMARY:")
            lines.append(f"  Average Test Duration: {sum(all_durations) / len(all_durations):.3f}s")
            lines.append(f"  Fastest Test: {min(all_durations):.3f}s")
            lines.append(f"  Slowest Test: {max(all_durations):.3f}s")
            lines.append("")
        
        lines.append("=" * 80)
        
        return "\n".join(lines)
        
    def generate_json_report(self, indent: int = 2) -> str:
        """Generate a JSON report."""
        def datetime_serializer(obj):
            if isinstance(obj, datetime):
                return obj.isoformat()
            raise TypeError(f"Object {obj} is not JSON serializable")
            
        return json.dumps(asdict(self.results), indent=indent, default=datetime_serializer)
        
    def generate_junit_xml(self) -> str:
        """Generate JUnit XML format for CI/CD integration."""
        testsuites = Element('testsuites')
        testsuites.set('name', f"UnrealMCP-{self.results.run_id}")
        testsuites.set('tests', str(self.results.total_tests))
        testsuites.set('failures', str(self.results.total_failed))
        testsuites.set('errors', str(self.results.total_errors))
        testsuites.set('skipped', str(self.results.total_skipped))
        testsuites.set('time', f"{self.results.total_duration:.3f}")
        testsuites.set('timestamp', self.results.start_time.isoformat())
        
        for suite in self.results.suites:
            testsuite = SubElement(testsuites, 'testsuite')
            testsuite.set('name', suite.name)
            testsuite.set('tests', str(suite.test_count))
            testsuite.set('failures', str(suite.failed_count))
            testsuite.set('errors', str(suite.error_count))
            testsuite.set('skipped', str(suite.skipped_count))
            testsuite.set('time', f"{suite.total_duration:.3f}")
            
            for test in suite.tests:
                testcase = SubElement(testsuite, 'testcase')
                testcase.set('name', test.name)
                testcase.set('classname', f"{suite.name}.{test.name}")
                testcase.set('time', f"{test.duration:.3f}")
                
                if test.skipped:
                    skipped = SubElement(testcase, 'skipped')
                    skipped.set('message', test.skip_reason or 'Test skipped')
                elif not test.success:
                    if "assertion" in (test.error or "").lower():
                        failure = SubElement(testcase, 'failure')
                        failure.set('message', test.error or 'Test failed')
                        if test.traceback:
                            failure.text = test.traceback
                    else:
                        error = SubElement(testcase, 'error')
                        error.set('message', test.error or 'Test error')
                        if test.traceback:
                            error.text = test.traceback
                            
                # Add stdout/stderr
                if test.stdout:
                    stdout = SubElement(testcase, 'system-out')
                    stdout.text = '\n'.join(test.stdout)
                if test.stderr:
                    stderr = SubElement(testcase, 'system-err')
                    stderr.text = '\n'.join(test.stderr)
        
        return tostring(testsuites, encoding='unicode')
        
    def generate_html_report(self) -> str:
        """Generate an HTML report."""
        html_template = """
<!DOCTYPE html>
<html>
<head>
    <title>Unreal MCP Test Results</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .summary { background: #f5f5f5; padding: 20px; border-radius: 5px; margin-bottom: 20px; }
        .suite { border: 1px solid #ddd; margin-bottom: 20px; border-radius: 5px; }
        .suite-header { background: #e9e9e9; padding: 15px; font-weight: bold; }
        .test-list { padding: 15px; }
        .test { margin-bottom: 10px; padding: 10px; border-left: 4px solid #ddd; }
        .test.passed { border-left-color: #28a745; background: #f8fff9; }
        .test.failed { border-left-color: #dc3545; background: #fff8f8; }
        .test.error { border-left-color: #fd7e14; background: #fff9f5; }
        .test.skipped { border-left-color: #6c757d; background: #f8f9fa; }
        .metrics { font-size: 0.9em; color: #666; }
        .error-detail { margin-top: 10px; padding: 10px; background: #f8d7da; border-radius: 3px; }
    </style>
</head>
<body>
    <h1>Unreal MCP Test Results</h1>
    
    <div class="summary">
        <h2>Summary</h2>
        <p><strong>Run ID:</strong> {run_id}</p>
        <p><strong>Started:</strong> {start_time}</p>
        <p><strong>Duration:</strong> {duration:.2f}s</p>
        <p><strong>Environment:</strong> {environment}</p>
        
        <h3>Results</h3>
        <p>
            <span style="color: #28a745;">✅ Passed: {passed}</span> | 
            <span style="color: #dc3545;">❌ Failed: {failed}</span> | 
            <span style="color: #fd7e14;">💥 Errors: {errors}</span> | 
            <span style="color: #6c757d;">⏭️ Skipped: {skipped}</span>
        </p>
        <p><strong>Success Rate:</strong> {success_rate:.1%}</p>
    </div>
    
    {suites_html}
</body>
</html>
        """
        
        suites_html = ""
        for suite in self.results.suites:
            suite_html = f"""
    <div class="suite">
        <div class="suite-header">
            {suite.name} ({suite.category}) - {suite.test_count} tests, {suite.success_rate:.1%} success rate
        </div>
        <div class="test-list">
            {self._generate_suite_tests_html(suite)}
        </div>
    </div>
            """
            suites_html += suite_html
            
        return html_template.format(
            run_id=self.results.run_id,
            start_time=self.results.start_time.strftime('%Y-%m-%d %H:%M:%S UTC'),
            duration=self.results.total_duration,
            environment=f"{self.results.environment.os_name} {self.results.environment.os_version}",
            passed=self.results.total_passed,
            failed=self.results.total_failed,
            errors=self.results.total_errors,
            skipped=self.results.total_skipped,
            success_rate=self.results.success_rate,
            suites_html=suites_html
        )
        
    def _generate_suite_tests_html(self, suite: TestSuiteResults) -> str:
        """Generate HTML for tests in a suite."""
        tests_html = ""
        for test in suite.tests:
            error_html = ""
            if test.error:
                error_html = f'<div class="error-detail"><strong>Error:</strong> {test.error}</div>'
                
            test_html = f"""
            <div class="test {test.status}">
                <div><strong>{test.status_emoji} {test.name}</strong></div>
                <div class="metrics">Duration: {test.duration:.3f}s</div>
                {error_html}
            </div>
            """
            tests_html += test_html
            
        return tests_html
        
    def save_reports(self, output_dir: str):
        """Save all report formats to the specified directory."""
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        # Console report
        console_report = self.generate_console_report(verbose=True)
        (output_path / "test_report.txt").write_text(console_report)
        
        # JSON report
        json_report = self.generate_json_report()
        (output_path / "test_results.json").write_text(json_report)
        
        # JUnit XML report  
        junit_xml = self.generate_junit_xml()
        (output_path / "test_results.xml").write_text(junit_xml)
        
        # HTML report
        html_report = self.generate_html_report()
        (output_path / "test_report.html").write_text(html_report)
        
        logger.info(f"Test reports saved to {output_path}")

# Add missing import
from datetime import timedelta

def create_sample_results() -> TestRunResults:
    """Create sample test results for testing the reporting system."""
    from datetime import timedelta
    
    collector = TestResultCollector()
    collector.start_test_run({"parallel": True, "use_mock": False})
    
    # Integration suite
    collector.start_suite("integration", "integration")
    collector.add_test_result("test_actor_creation", True, 1.2)
    collector.add_test_result("test_blueprint_compilation", True, 2.5)
    collector.add_test_result("test_connection_failure", False, 0.8, "Connection timeout")
    collector.complete_suite()
    
    # Unit suite
    collector.start_suite("unit", "unit")
    collector.add_test_result("test_command_parsing", True, 0.1)
    collector.add_test_result("test_response_validation", True, 0.05)
    collector.add_test_result("test_error_handling", False, 0.2, "AssertionError: Expected error not raised")
    collector.complete_suite()
    
    return collector.complete_test_run()

if __name__ == "__main__":
    # Generate sample reports
    results = create_sample_results()
    reporter = TestResultReporter(results)
    
    print("Console Report:")
    print(reporter.generate_console_report())
    
    print("\nSaving all report formats...")
    reporter.save_reports("test_output")
    print("Reports saved to test_output/")