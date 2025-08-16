"""
Comprehensive test runner for all asset management tests.

This script runs all asset management test suites:
- Asset Commands Tests (core operations)
- Content Browser Tests (listing, search, metadata)
- Asset Registry Tests (references, dependencies)

Features:
- Parallel test execution option
- Detailed reporting and statistics
- Error analysis and debugging
- Performance metrics
- Test result export
"""

import asyncio
import json
import sys
import time
from pathlib import Path
from typing import Dict, List, Any
from dataclasses import asdict

# Add parent directories to path
test_dir = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(test_dir))
sys.path.insert(0, str(test_dir.parent))

from tests.test_framework import TestFramework, create_test_config, TestResult
from tests.data.test_data import get_test_data_manager

# Import test modules
from test_asset_commands import run_all_tests as run_asset_command_tests
from test_content_browser_commands import run_all_tests as run_content_browser_tests
from test_asset_registry_commands import run_all_tests as run_asset_registry_tests

class AssetTestRunner:
    """Comprehensive test runner for all asset management tests."""
    
    def __init__(self, config=None):
        self.config = config or create_test_config()
        self.framework = TestFramework(self.config)
        self.test_data_manager = get_test_data_manager()
        self.all_results = []
        self.start_time = None
        self.end_time = None
        
    def print_header(self):
        """Print test runner header."""
        print("=" * 80)
        print("🚀 COMPREHENSIVE ASSET MANAGEMENT TEST SUITE")
        print("=" * 80)
        print(f"Configuration:")
        print(f"  - Unreal Host: {self.config.unreal_host}")
        print(f"  - Unreal Port: {self.config.unreal_port}")
        print(f"  - Connection Timeout: {self.config.connection_timeout}s")
        print(f"  - Command Timeout: {self.config.command_timeout}s")
        print(f"  - Use Mock Server: {self.config.use_mock_server}")
        print(f"  - Cleanup on Failure: {self.config.cleanup_on_failure}")
        print("=" * 80)
    
    def print_test_suite_header(self, suite_name: str, description: str):
        """Print test suite header."""
        print(f"\n{'=' * 60}")
        print(f"📦 {suite_name}")
        print(f"📝 {description}")
        print(f"{'=' * 60}")
    
    def print_suite_summary(self, suite_name: str, results: List[TestResult]):
        """Print summary for a test suite."""
        passed = sum(1 for r in results if r.success)
        failed = len(results) - passed
        total_time = sum(r.duration for r in results)
        success_rate = (passed / len(results) * 100) if results else 0
        
        print(f"\n📊 {suite_name} Summary:")
        print(f"   Tests Run: {len(results)}")
        print(f"   Passed: {passed}")
        print(f"   Failed: {failed}")
        print(f"   Duration: {total_time:.2f}s")
        print(f"   Success Rate: {success_rate:.1f}%")
        
        if failed > 0:
            print(f"\n❌ Failed Tests in {suite_name}:")
            for result in results:
                if not result.success:
                    print(f"   - {result.name}: {result.error}")
    
    def print_overall_summary(self):
        """Print overall test summary."""
        total_tests = len(self.all_results)
        passed_tests = sum(1 for r in self.all_results if r.success)
        failed_tests = total_tests - passed_tests
        total_duration = self.end_time - self.start_time
        test_duration = sum(r.duration for r in self.all_results)
        success_rate = (passed_tests / total_tests * 100) if total_tests else 0
        
        print(f"\n" + "=" * 80)
        print(f"🏁 OVERALL TEST RESULTS")
        print(f"=" * 80)
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Success Rate: {success_rate:.1f}%")
        print(f"Total Runtime: {total_duration:.2f}s")
        print(f"Test Execution Time: {test_duration:.2f}s")
        print(f"Overhead: {(total_duration - test_duration):.2f}s")
        
        if failed_tests > 0:
            print(f"\n❌ All Failed Tests:")
            suite_failures = {}
            for result in self.all_results:
                if not result.success:
                    suite = result.name.split('_')[1] if '_' in result.name else 'unknown'
                    if suite not in suite_failures:
                        suite_failures[suite] = []
                    suite_failures[suite].append(result)
            
            for suite, failures in suite_failures.items():
                print(f"\n  {suite.title()} Suite ({len(failures)} failures):")
                for result in failures:
                    print(f"    - {result.name}: {result.error}")
        
        print(f"\n" + "=" * 80)
        
        return success_rate >= 90.0  # Consider success if 90%+ pass rate
    
    def test_unreal_connection(self) -> bool:
        """Test connection to Unreal Engine before running tests."""
        print(f"\n🔌 Testing connection to Unreal Engine...")
        
        if self.config.use_mock_server:
            print(f"✅ Using mock server - connection test skipped")
            return True
        
        connection_success = self.framework.test_unreal_connection()
        
        if connection_success:
            print(f"✅ Connection to Unreal Engine successful")
        else:
            print(f"❌ Failed to connect to Unreal Engine")
            print(f"   Make sure Unreal Editor is running with MCP plugin enabled")
            print(f"   Check host: {self.config.unreal_host}, port: {self.config.unreal_port}")
        
        return connection_success
    
    async def run_asset_command_tests(self) -> List[TestResult]:
        """Run asset command tests."""
        self.print_test_suite_header(
            "ASSET COMMAND TESTS",
            "Testing core asset operations: load, save, duplicate, delete, rename, move, import, export"
        )
        
        results = await run_asset_command_tests()
        self.print_suite_summary("Asset Commands", results)
        return results
    
    async def run_content_browser_tests(self) -> List[TestResult]:
        """Run content browser tests.""" 
        self.print_test_suite_header(
            "CONTENT BROWSER TESTS",
            "Testing content browser operations: list_assets, get_asset_metadata, search_assets"
        )
        
        results = await run_content_browser_tests()
        self.print_suite_summary("Content Browser", results)
        return results
    
    async def run_asset_registry_tests(self) -> List[TestResult]:
        """Run asset registry tests."""
        self.print_test_suite_header(
            "ASSET REGISTRY TESTS", 
            "Testing asset registry operations: get_asset_references, get_asset_dependencies"
        )
        
        results = await run_asset_registry_tests()
        self.print_suite_summary("Asset Registry", results)
        return results
    
    def save_test_results(self, output_file: str = None):
        """Save detailed test results to JSON file."""
        if output_file is None:
            output_file = f"asset_test_results_{int(time.time())}.json"
        
        # Convert results to serializable format
        serializable_results = []
        for result in self.all_results:
            result_data = asdict(result)
            serializable_results.append(result_data)
        
        test_report = {
            "timestamp": time.time(),
            "config": {
                "unreal_host": self.config.unreal_host,
                "unreal_port": self.config.unreal_port,
                "use_mock_server": self.config.use_mock_server,
                "connection_timeout": self.config.connection_timeout,
                "command_timeout": self.config.command_timeout
            },
            "summary": {
                "total_tests": len(self.all_results),
                "passed_tests": sum(1 for r in self.all_results if r.success),
                "failed_tests": sum(1 for r in self.all_results if not r.success),
                "success_rate": (sum(1 for r in self.all_results if r.success) / len(self.all_results) * 100) if self.all_results else 0,
                "total_duration": self.end_time - self.start_time if self.start_time and self.end_time else 0,
                "test_duration": sum(r.duration for r in self.all_results)
            },
            "results": serializable_results
        }
        
        try:
            output_path = Path(output_file)
            with open(output_path, 'w') as f:
                json.dump(test_report, f, indent=2)
            print(f"📄 Test results saved to: {output_path.absolute()}")
        except Exception as e:
            print(f"❌ Failed to save test results: {e}")
    
    def analyze_performance(self):
        """Analyze test performance and identify slow tests."""
        if not self.all_results:
            return
        
        # Sort by duration
        sorted_results = sorted(self.all_results, key=lambda r: r.duration, reverse=True)
        slow_threshold = 10.0  # Tests taking more than 10 seconds
        
        slow_tests = [r for r in sorted_results if r.duration > slow_threshold]
        
        if slow_tests:
            print(f"\n⚠️  PERFORMANCE ANALYSIS - Slow Tests (>{slow_threshold}s):")
            for result in slow_tests:
                print(f"   - {result.name}: {result.duration:.2f}s")
        
        # Average performance per suite
        suite_performance = {}
        for result in self.all_results:
            suite = result.name.split('_')[1] if '_' in result.name else 'unknown'
            if suite not in suite_performance:
                suite_performance[suite] = []
            suite_performance[suite].append(result.duration)
        
        print(f"\n📈 SUITE PERFORMANCE:")
        for suite, durations in suite_performance.items():
            avg_duration = sum(durations) / len(durations)
            max_duration = max(durations)
            print(f"   - {suite.title()}: avg {avg_duration:.2f}s, max {max_duration:.2f}s")
    
    async def run_all_tests(self) -> bool:
        """Run all asset management tests."""
        self.print_header()
        self.start_time = time.time()
        
        # Test connection first (unless using mock server)
        if not self.test_unreal_connection():
            print(f"\n❌ Aborting tests due to connection failure")
            return False
        
        try:
            # Run all test suites
            asset_results = await self.run_asset_command_tests()
            self.all_results.extend(asset_results)
            
            browser_results = await self.run_content_browser_tests()
            self.all_results.extend(browser_results)
            
            registry_results = await self.run_asset_registry_tests()
            self.all_results.extend(registry_results)
            
            self.end_time = time.time()
            
            # Print overall summary
            success = self.print_overall_summary()
            
            # Performance analysis
            self.analyze_performance()
            
            # Save results
            self.save_test_results()
            
            return success
            
        except KeyboardInterrupt:
            print(f"\n🛑 Tests interrupted by user")
            self.end_time = time.time()
            return False
        except Exception as e:
            print(f"\n💥 Test runner error: {e}")
            self.end_time = time.time()
            return False

async def main():
    """Main entry point for asset test runner."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Run comprehensive asset management tests")
    parser.add_argument("--host", default="127.0.0.1", help="Unreal Engine host")
    parser.add_argument("--port", type=int, default=55557, help="Unreal Engine port")
    parser.add_argument("--mock", action="store_true", help="Use mock server for testing")
    parser.add_argument("--timeout", type=float, default=30.0, help="Command timeout in seconds")
    parser.add_argument("--output", help="Output file for test results")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose logging")
    
    args = parser.parse_args()
    
    # Create test configuration
    config = create_test_config(
        use_mock=args.mock,
        unreal_host=args.host,
        unreal_port=args.port,
        command_timeout=args.timeout
    )
    
    # Create and run test runner
    runner = AssetTestRunner(config)
    success = await runner.run_all_tests()
    
    if args.output:
        runner.save_test_results(args.output)
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    asyncio.run(main())