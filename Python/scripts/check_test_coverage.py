#!/usr/bin/env python3
"""
Check that new C++ commands have corresponding tests.

This script is run as a pre-commit hook to ensure every new MCP command
has proper test coverage before it can be committed.
"""

import sys
import re
import os
from pathlib import Path
from typing import Set, Dict, List


def extract_commands_from_cpp(filepath: str) -> Set[str]:
    """Extract command names from C++ command handler files."""
    commands = set()
    
    with open(filepath, 'r') as f:
        content = f.read()
    
    # Pattern to find command comparisons in C++
    # Matches: CommandType == TEXT("command_name")
    pattern = r'CommandType\s*==\s*TEXT\s*\(\s*"([^"]+)"\s*\)'
    matches = re.findall(pattern, content)
    commands.update(matches)
    
    # Also check for command handlers in new command classes
    # Matches: if (CommandType == TEXT("command_name"))
    pattern2 = r'if\s*\([^)]*CommandType\s*==\s*TEXT\s*\(\s*"([^"]+)"\s*\)'
    matches2 = re.findall(pattern2, content)
    commands.update(matches2)
    
    return commands


def find_test_for_command(command: str, test_dir: Path) -> List[str]:
    """Find test files that test a specific command."""
    test_files = []
    
    # Search for test files containing the command
    for test_file in test_dir.rglob("test_*.py"):
        if test_file.is_file():
            with open(test_file, 'r') as f:
                content = f.read()
                # Look for the command in test files
                if f'"{command}"' in content or f"'{command}'" in content:
                    # More specific check - look for send_command calls
                    if f'send_command("{command}"' in content or f"send_command('{command}'" in content:
                        test_files.append(str(test_file.relative_to(test_dir.parent)))
    
    return test_files


def check_test_requirements(test_file: str, command: str) -> Dict[str, bool]:
    """Check if a test file has all 5 required test types for a command."""
    requirements = {
        'basic': False,
        'error_handling': False,
        'edge_cases': False,
        'performance': False,
        'cleanup': False
    }
    
    with open(test_file, 'r') as f:
        content = f.read()
    
    # Check for required test methods
    if re.search(rf'test_{command}_basic|test_{command}\b', content):
        requirements['basic'] = True
    
    if re.search(rf'test_{command}_error|test_{command}_invalid', content):
        requirements['error_handling'] = True
    
    if re.search(rf'test_{command}_edge|test_{command}_boundary', content):
        requirements['edge_cases'] = True
    
    if re.search(rf'test_{command}_performance|test_{command}_perf', content):
        requirements['performance'] = True
    
    if re.search(rf'test_{command}_cleanup|test_{command}_resource', content):
        requirements['cleanup'] = True
    
    return requirements


def main(files: List[str]) -> int:
    """Main function to check test coverage."""
    # Get the project root
    project_root = Path(__file__).parent.parent.parent
    test_dir = project_root / "Python" / "tests"
    
    all_commands = set()
    missing_tests = []
    incomplete_tests = []
    
    # Extract commands from modified C++ files
    for filepath in files:
        if filepath.endswith('.cpp'):
            commands = extract_commands_from_cpp(filepath)
            all_commands.update(commands)
    
    # Check each command for test coverage
    for command in all_commands:
        test_files = find_test_for_command(command, test_dir)
        
        if not test_files:
            missing_tests.append(command)
        else:
            # Check if tests have all required types
            for test_file in test_files:
                full_path = project_root / "Python" / test_file
                if full_path.exists():
                    requirements = check_test_requirements(str(full_path), command)
                    missing_reqs = [req for req, present in requirements.items() if not present]
                    
                    if missing_reqs:
                        incomplete_tests.append({
                            'command': command,
                            'test_file': test_file,
                            'missing': missing_reqs
                        })
    
    # Report results
    if missing_tests or incomplete_tests:
        print("\n" + "="*60)
        print("❌ TEST COVERAGE CHECK FAILED")
        print("="*60)
        
        if missing_tests:
            print("\n⚠️  Commands without ANY tests:")
            for cmd in missing_tests:
                print(f"  - {cmd}")
            print(f"\n  Total: {len(missing_tests)} commands need tests")
        
        if incomplete_tests:
            print("\n⚠️  Commands with INCOMPLETE tests:")
            for item in incomplete_tests:
                print(f"\n  Command: {item['command']}")
                print(f"  Test file: {item['test_file']}")
                print(f"  Missing test types: {', '.join(item['missing'])}")
        
        print("\n📋 Required test types for EVERY command:")
        print("  1. Basic functionality test")
        print("  2. Error handling test")
        print("  3. Edge cases test")
        print("  4. Performance test")
        print("  5. Cleanup/resource test")
        
        print("\n💡 Solution:")
        print("  1. Copy tests/templates/command_test_template.py")
        print("  2. Implement all 5 required test types")
        print("  3. Place in appropriate test directory")
        print("\n" + "="*60)
        
        return 1
    
    print("✅ Test coverage check passed - all commands have tests")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))