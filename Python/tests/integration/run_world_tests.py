"""
Comprehensive test runner for all World/Level Management tests.

Runs all world and level management tests including:
- Level Editor operations (create, save, load, streaming, visibility)
- Landscape operations (create, modify, paint, query)
- World Runtime operations (get level info)

Provides detailed reporting, performance metrics, and cleanup.
"""

import asyncio
import json
import os
import sys
import time
from pathlib import Path
from typing import Dict, Any, List, Optional
from dataclasses import asdict

# Add parent directories to path for imports
test_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(test_dir))
sys.path.insert(0, str(test_dir.parent))

from tests.test_framework import TestFramework, create_test_config, TestResult
from tests.data.test_data import get_test_data_manager
from tests.integration.world_test_utils import WorldTestUtils, create_world_test_utils

# Import test modules
from tests.integration.editor.level_editor.test_level_commands import TestLevelCommands, run_all_tests as run_level_tests
from tests.integration.editor.landscape.test_landscape_commands import TestLandscapeCommands, run_all_tests as run_landscape_tests  
from tests.integration.engine.world.test_world_commands import TestWorldCommands, run_all_tests as run_world_tests

class WorldTestRunner:
    """Main test runner for all World/Level Management tests."""
    
    def __init__(self, config_overrides: Dict[str, Any] = None):
        """Initialize the test runner."""
        self.config = create_test_config(**(config_overrides or {}))
        self.framework = TestFramework(self.config)
        self.test_data_manager = get_test_data_manager()
        self.world_utils = create_world_test_utils(self.framework)
        
        # Test results tracking
        self.all_results: List[TestResult] = []
        self.test_suite_results: Dict[str, List[TestResult]] = {}
        self.performance_metrics: Dict[str, Dict[str, float]] = {}
        self.start_time: Optional[float] = None
        self.end_time: Optional[float] = None
        
        # Test configuration
        self.test_suites = [
            {
                "name": "Level Editor Commands",
                "module": "level_commands",
                "runner": run_level_tests,
                "description": "Level creation, loading, saving, streaming, and visibility operations"
            },
            {
                "name": "Landscape Commands", 
                "module": "landscape_commands",
                "runner": run_landscape_tests,
                "description": "Landscape creation, modification, painting, and information queries"
            },
            {
                "name": "World Runtime Commands",
                "module": "world_commands", 
                "runner": run_world_tests,
                "description": "Runtime world and level information queries"
            }
        ]
    
    def setup_test_environment(self):
        """Set up the test environment."""
        print(f"\n🔧 Setting up World/Level Management test environment...")
        
        # Test connection to Unreal Engine
        connection_success = self.framework.test_unreal_connection()
        if not connection_success:
            print(f"⚠️ Warning: Could not establish connection to Unreal Engine")
            print(f"   Tests will run but may fail if Unreal Engine is not running")
        else:
            print(f"✅ Successfully connected to Unreal Engine")
        
        # Capture initial world state
        initial_state = self.world_utils.capture_world_state()
        print(f"📸 Captured initial world state:")
        print(f"   Level: {initial_state.current_level_name or 'Unknown'}")
        print(f"   Actors: {initial_state.total_actors}")
        print(f"   Landscapes: {initial_state.total_landscapes}")
        
        # Setup logging
        self.framework.setup_logging()
        
        print(f"✅ Test environment setup complete\n")
    
    def teardown_test_environment(self):
        """Clean up the test environment."""
        print(f"\n🧹 Cleaning up test environment...")
        
        # Cleanup world test utilities
        cleanup_summary = self.world_utils.get_cleanup_summary()
        if any(cleanup_summary.values()):
            print(f"📋 Cleanup summary:")
            for item_type, count in cleanup_summary.items():
                if count > 0:
                    print(f"   {item_type.title()}: {count}")
        
        self.world_utils.cleanup_all_contexts()
        
        # Capture final world state
        final_state = self.world_utils.capture_world_state()
        print(f"📸 Final world state:")
        print(f"   Level: {final_state.current_level_name or 'Unknown'}")
        print(f"   Actors: {final_state.total_actors}")
        print(f"   Landscapes: {final_state.total_landscapes}")
        
        print(f"✅ Test environment cleanup complete")
    
    async def run_test_suite(self, suite_info: Dict[str, Any]) -> List[TestResult]:
        """Run a single test suite."""
        suite_name = suite_info["name"]
        suite_runner = suite_info["runner"]
        suite_description = suite_info["description"]
        
        print(f"\n🚀 Running {suite_name}")
        print(f"📝 {suite_description}")
        print(f"{'=' * 60}")
        
        start_time = time.time()
        
        try:
            # Run the test suite
            results = await suite_runner()
            
            duration = time.time() - start_time
            
            # Process results
            passed = sum(1 for r in results if r.success)
            failed = len(results) - passed
            
            print(f"\n📊 {suite_name} Summary:")
            print(f"   Total Tests: {len(results)}")
            print(f"   Passed: {passed}")
            print(f"   Failed: {failed}")
            print(f"   Duration: {duration:.2f}s")
            print(f"   Success Rate: {(passed/len(results)*100):.1f}%")
            
            # Store results
            self.test_suite_results[suite_name] = results
            self.all_results.extend(results)
            
            # Store performance metrics
            self.performance_metrics[suite_name] = {
                "total_duration": duration,
                "test_count": len(results),
                "avg_test_duration": duration / len(results) if results else 0.0,
                "success_rate": passed / len(results) if results else 0.0
            }
            
            if failed > 0:
                print(f"\n❌ Failed Tests in {suite_name}:")
                for result in results:
                    if not result.success:
                        print(f"   - {result.name}: {result.error}")
            
            return results
            
        except Exception as e:
            duration = time.time() - start_time
            error_result = TestResult(
                name=f"{suite_name}_suite_error",
                success=False,
                error=f"Test suite failed to run: {str(e)}",
                duration=duration
            )
            
            print(f"\n💥 {suite_name} failed to run: {e}")
            
            self.test_suite_results[suite_name] = [error_result]
            self.all_results.append(error_result)
            
            return [error_result]
    
    async def run_all_tests(self) -> Dict[str, Any]:
        """Run all world/level management tests."""
        self.start_time = time.time()
        
        print(f"🌍 World/Level Management Test Suite")
        print(f"{'=' * 50}")
        print(f"Test Suites: {len(self.test_suites)}")
        print(f"Configuration:")
        print(f"   Host: {self.config.unreal_host}")
        print(f"   Port: {self.config.unreal_port}")
        print(f"   Connection Timeout: {self.config.connection_timeout}s")
        print(f"   Command Timeout: {self.config.command_timeout}s")
        print(f"   Use Mock Server: {self.config.use_mock_server}")
        
        # Setup environment
        self.setup_test_environment()
        
        try:
            # Run all test suites
            for suite_info in self.test_suites:
                await self.run_test_suite(suite_info)
                
                # Brief pause between suites
                await asyncio.sleep(0.5)
        
        finally:
            # Cleanup environment
            self.teardown_test_environment()
        
        self.end_time = time.time()
        
        # Generate final report
        return self.generate_final_report()
    
    def generate_final_report(self) -> Dict[str, Any]:
        """Generate comprehensive final test report."""
        if not self.start_time or not self.end_time:
            return {}
        
        total_duration = self.end_time - self.start_time
        total_tests = len(self.all_results)
        total_passed = sum(1 for r in self.all_results if r.success)
        total_failed = total_tests - total_passed
        overall_success_rate = total_passed / total_tests if total_tests > 0 else 0.0
        
        # Calculate performance statistics
        test_durations = [r.duration for r in self.all_results if r.duration > 0]
        avg_test_duration = sum(test_durations) / len(test_durations) if test_durations else 0.0
        min_test_duration = min(test_durations) if test_durations else 0.0
        max_test_duration = max(test_durations) if test_durations else 0.0
        
        # Print comprehensive report
        print(f"\n" + "="*80)
        print(f"🏁 WORLD/LEVEL MANAGEMENT TESTS COMPLETE")
        print(f"="*80)
        
        print(f"\n📈 OVERALL SUMMARY:")
        print(f"   Total Duration: {total_duration:.2f}s")
        print(f"   Total Test Suites: {len(self.test_suites)}")
        print(f"   Total Tests: {total_tests}")
        print(f"   Passed: {total_passed}")
        print(f"   Failed: {total_failed}")
        print(f"   Success Rate: {overall_success_rate:.1%}")
        
        print(f"\n⏱️ PERFORMANCE METRICS:")
        print(f"   Average Test Duration: {avg_test_duration:.3f}s")
        print(f"   Fastest Test: {min_test_duration:.3f}s")
        print(f"   Slowest Test: {max_test_duration:.3f}s")
        
        print(f"\n📋 DETAILED BREAKDOWN:")
        for suite_name, metrics in self.performance_metrics.items():
            print(f"   {suite_name}:")
            print(f"     Tests: {int(metrics['test_count'])}")
            print(f"     Duration: {metrics['total_duration']:.2f}s")
            print(f"     Average: {metrics['avg_test_duration']:.3f}s per test")
            print(f"     Success Rate: {metrics['success_rate']:.1%}")
        
        if total_failed > 0:
            print(f"\n❌ FAILED TESTS BY CATEGORY:")
            for suite_name, results in self.test_suite_results.items():
                failed_tests = [r for r in results if not r.success]
                if failed_tests:
                    print(f"   {suite_name} ({len(failed_tests)} failed):")
                    for test in failed_tests:
                        print(f"     - {test.name}: {test.error}")
        
        # Performance warnings
        print(f"\n⚠️ PERFORMANCE ANALYSIS:")
        slow_tests = [r for r in self.all_results if r.duration > 10.0]
        if slow_tests:
            print(f"   Slow Tests (>10s): {len(slow_tests)}")
            for test in slow_tests[:5]:  # Show top 5 slowest
                print(f"     - {test.name}: {test.duration:.2f}s")
        else:
            print(f"   ✅ No unusually slow tests detected")
        
        failed_suites = [name for name, metrics in self.performance_metrics.items() if metrics['success_rate'] < 0.8]
        if failed_suites:
            print(f"   Low Success Rate Suites (<80%): {failed_suites}")
        else:
            print(f"   ✅ All test suites have good success rates")
        
        # Test quality assessment
        print(f"\n🎯 QUALITY ASSESSMENT:")
        if overall_success_rate >= 0.95:
            print(f"   ✅ EXCELLENT - {overall_success_rate:.1%} success rate")
        elif overall_success_rate >= 0.85:
            print(f"   ✅ GOOD - {overall_success_rate:.1%} success rate")
        elif overall_success_rate >= 0.70:
            print(f"   ⚠️ NEEDS IMPROVEMENT - {overall_success_rate:.1%} success rate")
        else:
            print(f"   ❌ POOR - {overall_success_rate:.1%} success rate")
        
        if avg_test_duration < 1.0:
            print(f"   ✅ FAST - Average test duration {avg_test_duration:.3f}s")
        elif avg_test_duration < 3.0:
            print(f"   ✅ REASONABLE - Average test duration {avg_test_duration:.3f}s")
        else:
            print(f"   ⚠️ SLOW - Average test duration {avg_test_duration:.3f}s")
        
        print(f"\n" + "="*80)
        
        # Return structured report
        report = {
            "summary": {
                "total_duration": total_duration,
                "total_test_suites": len(self.test_suites),
                "total_tests": total_tests,
                "passed": total_passed,
                "failed": total_failed,
                "success_rate": overall_success_rate
            },
            "performance": {
                "avg_test_duration": avg_test_duration,
                "min_test_duration": min_test_duration,
                "max_test_duration": max_test_duration,
                "slow_tests_count": len(slow_tests)
            },
            "suites": {
                name: {
                    "results": len(results),
                    "passed": sum(1 for r in results if r.success),
                    "failed": sum(1 for r in results if not r.success),
                    "duration": self.performance_metrics[name]["total_duration"],
                    "success_rate": self.performance_metrics[name]["success_rate"]
                }
                for name, results in self.test_suite_results.items()
            },
            "failed_tests": [
                {
                    "name": r.name,
                    "error": r.error,
                    "duration": r.duration
                }
                for r in self.all_results if not r.success
            ],
            "test_results": [asdict(r) for r in self.all_results]
        }
        
        return report
    
    def save_report(self, report: Dict[str, Any], output_file: str = "world_test_results.json"):
        """Save test report to file."""
        try:
            output_path = Path(output_file)
            with open(output_path, 'w') as f:
                json.dump(report, f, indent=2)
            print(f"📄 Test report saved to: {output_path.absolute()}")
        except Exception as e:
            print(f"⚠️ Failed to save report: {e}")

async def run_world_management_tests(config_overrides: Dict[str, Any] = None,
                                   save_results: bool = True,
                                   output_file: str = "world_test_results.json") -> Dict[str, Any]:
    """Run all World/Level Management tests with configuration options."""
    
    # Create and run test runner
    runner = WorldTestRunner(config_overrides)
    report = await runner.run_all_tests()
    
    # Save results if requested
    if save_results:
        runner.save_report(report, output_file)
    
    return report

def main():
    """Main entry point for running tests."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Run World/Level Management Tests")
    parser.add_argument("--host", default="127.0.0.1", help="Unreal Engine host")
    parser.add_argument("--port", type=int, default=55557, help="Unreal Engine port")
    parser.add_argument("--timeout", type=float, default=30.0, help="Command timeout")
    parser.add_argument("--mock", action="store_true", help="Use mock server")
    parser.add_argument("--output", default="world_test_results.json", help="Output file")
    parser.add_argument("--no-save", action="store_true", help="Don't save results to file")
    
    args = parser.parse_args()
    
    # Prepare configuration overrides
    config_overrides = {
        "unreal_host": args.host,
        "unreal_port": args.port,
        "command_timeout": args.timeout,
        "use_mock_server": args.mock
    }
    
    try:
        # Run tests
        report = asyncio.run(run_world_management_tests(
            config_overrides=config_overrides,
            save_results=not args.no_save,
            output_file=args.output
        ))
        
        # Exit with appropriate code
        success_rate = report.get("summary", {}).get("success_rate", 0.0)
        exit_code = 0 if success_rate >= 0.8 else 1
        sys.exit(exit_code)
        
    except KeyboardInterrupt:
        print(f"\n⚠️ Tests interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"\n💥 Test runner error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()