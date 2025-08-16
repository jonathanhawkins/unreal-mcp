#!/usr/bin/env python3
"""
Validate that test files follow the required structure and standards.

This script ensures all test files follow the project's testing conventions
and include all required components.
"""

import sys
import re
import ast
from pathlib import Path
from typing import List, Dict, Set


class TestStructureValidator:
    """Validates test file structure and content."""
    
    def __init__(self):
        self.errors = []
        self.warnings = []
    
    def validate_file(self, filepath: str) -> bool:
        """Validate a single test file."""
        self.errors = []
        self.warnings = []
        
        with open(filepath, 'r') as f:
            content = f.read()
        
        # Check file structure
        self._check_imports(content)
        self._check_class_structure(content, filepath)
        self._check_docstrings(content)
        self._check_fixtures(content)
        self._check_assertions(content)
        self._check_cleanup(content)
        self._check_no_hardcoded_paths(content)
        self._check_no_print_statements(content)
        self._check_test_independence(content)
        self._check_naming_conventions(filepath, content)
        
        return len(self.errors) == 0
    
    def _check_imports(self, content: str):
        """Check required imports are present."""
        required_imports = [
            'pytest',
            'UnrealMCPClient'
        ]
        
        for imp in required_imports:
            if imp not in content:
                self.errors.append(f"Missing required import: {imp}")
    
    def _check_class_structure(self, content: str, filepath: str):
        """Check test class follows naming conventions."""
        # Parse the AST
        try:
            tree = ast.parse(content)
        except SyntaxError as e:
            self.errors.append(f"Syntax error: {e}")
            return
        
        # Find test classes
        test_classes = [node for node in ast.walk(tree) 
                       if isinstance(node, ast.ClassDef) and node.name.startswith('Test')]
        
        if not test_classes:
            self.errors.append("No test class found (should start with 'Test')")
            return
        
        for cls in test_classes:
            # Check for required fixture
            has_mcp_client = False
            for node in cls.body:
                if isinstance(node, ast.AsyncFunctionDef):
                    if node.name == 'mcp_client':
                        has_mcp_client = True
            
            if not has_mcp_client:
                self.warnings.append(f"Class {cls.name} missing mcp_client fixture")
    
    def _check_docstrings(self, content: str):
        """Check all test methods have docstrings."""
        try:
            tree = ast.parse(content)
        except:
            return
        
        for node in ast.walk(tree):
            if isinstance(node, ast.AsyncFunctionDef) and node.name.startswith('test_'):
                docstring = ast.get_docstring(node)
                if not docstring:
                    self.errors.append(f"Test method '{node.name}' missing docstring")
                elif len(docstring) < 20:
                    self.warnings.append(f"Test method '{node.name}' has very short docstring")
    
    def _check_fixtures(self, content: str):
        """Check fixtures have proper setup and teardown."""
        fixture_pattern = r'@pytest\.fixture.*?\n.*?async def (\w+)\(.*?\):(.*?)(?=\n(?:async )?def|\Z)'
        fixtures = re.findall(fixture_pattern, content, re.DOTALL)
        
        for fixture_name, fixture_body in fixtures:
            if 'yield' in fixture_body:
                # Check for cleanup after yield
                parts = fixture_body.split('yield')
                if len(parts) > 1:
                    cleanup_part = parts[1]
                    if len(cleanup_part.strip()) < 10:
                        self.warnings.append(f"Fixture '{fixture_name}' may have insufficient cleanup")
    
    def _check_assertions(self, content: str):
        """Check assertions have meaningful messages."""
        # Find assertions without messages
        simple_assert_pattern = r'assert\s+[^,\n]+\s*$'
        matches = re.findall(simple_assert_pattern, content, re.MULTILINE)
        
        # Filter out assertions that are probably fine
        problematic = []
        for match in matches:
            if 'is True' not in match and 'is False' not in match and '==' not in match:
                problematic.append(match.strip())
        
        if problematic:
            self.warnings.append(f"Found {len(problematic)} assertions without messages")
    
    def _check_cleanup(self, content: str):
        """Check for resource cleanup patterns."""
        # Look for resource creation without cleanup
        creation_patterns = [
            r'create_blueprint',
            r'spawn_actor',
            r'create_level',
            r'create_widget'
        ]
        
        cleanup_patterns = [
            r'delete_asset',
            r'delete_actor',
            r'finally:',
            r'cleanup'
        ]
        
        has_creation = any(re.search(pattern, content) for pattern in creation_patterns)
        has_cleanup = any(re.search(pattern, content) for pattern in cleanup_patterns)
        
        if has_creation and not has_cleanup:
            self.errors.append("Test creates resources but missing cleanup code")
    
    def _check_no_hardcoded_paths(self, content: str):
        """Check for hardcoded paths."""
        # Look for absolute paths
        hardcoded_patterns = [
            r'[A-Z]:\\\\',  # Windows paths
            r'/Users/',     # Mac paths
            r'/home/',      # Linux paths
            r'/mnt/c/',     # WSL paths
        ]
        
        for pattern in hardcoded_patterns:
            if re.search(pattern, content):
                self.errors.append(f"Hardcoded path detected (pattern: {pattern})")
    
    def _check_no_print_statements(self, content: str):
        """Check for print statements in tests."""
        # Exclude template files
        if 'template' in content.lower():
            return
        
        print_count = len(re.findall(r'\bprint\s*\(', content))
        if print_count > 0:
            self.errors.append(f"Found {print_count} print statement(s) - use assertions instead")
    
    def _check_test_independence(self, content: str):
        """Check tests don't depend on each other."""
        # Look for class-level state that might indicate dependencies
        class_vars_pattern = r'class\s+\w+:.*?\n\s{4}[^@\s]\w+\s*='
        if re.search(class_vars_pattern, content, re.DOTALL):
            self.warnings.append("Class-level variables detected - ensure tests are independent")
    
    def _check_naming_conventions(self, filepath: str, content: str):
        """Check naming conventions are followed."""
        filename = Path(filepath).name
        
        # File should start with test_
        if not filename.startswith('test_'):
            self.errors.append(f"Test file should start with 'test_', got: {filename}")
        
        # Test methods should start with test_
        methods = re.findall(r'async def (\w+)\(', content)
        for method in methods:
            if not method.startswith('test_') and method not in ['setUp', 'tearDown', 'mcp_client']:
                if not method.startswith('_'):
                    self.warnings.append(f"Method '{method}' should start with 'test_' or '_'")


def main(files: List[str]) -> int:
    """Main function to validate test structure."""
    validator = TestStructureValidator()
    failed_files = []
    
    for filepath in files:
        # Skip template files
        if 'template' in filepath.lower():
            continue
        
        if not validator.validate_file(filepath):
            failed_files.append(filepath)
            
            print(f"\n❌ Validation failed for: {filepath}")
            
            if validator.errors:
                print("\nErrors (must fix):")
                for error in validator.errors:
                    print(f"  - {error}")
            
            if validator.warnings:
                print("\nWarnings (should fix):")
                for warning in validator.warnings:
                    print(f"  - {warning}")
    
    if failed_files:
        print("\n" + "="*60)
        print("❌ TEST STRUCTURE VALIDATION FAILED")
        print("="*60)
        print(f"\nFailed files: {len(failed_files)}")
        print("\n💡 Use the test template: tests/templates/command_test_template.py")
        print("📋 Follow the checklist: tests/templates/test_checklist.md")
        return 1
    
    print("✅ Test structure validation passed")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))