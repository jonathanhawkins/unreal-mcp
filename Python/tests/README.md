# Unreal MCP Testing Documentation

## 📋 **MANDATORY TESTING REQUIREMENTS**

**EVERY new MCP command MUST have tests before merging. NO EXCEPTIONS.**

### Minimum Test Coverage Per Command
Each new command requires:
1. ✅ **Basic functionality test** (happy path)
2. ✅ **Error handling test** (invalid inputs)
3. ✅ **Edge case test** (boundary conditions)
4. ✅ **Performance test** (< 1 second for single operations)
5. ✅ **Cleanup verification** (no resource leaks)

## 🏗️ Project Structure

```
tests/
├── README.md                    # This file - DO NOT IGNORE
├── integration/                 # Integration tests (REQUIRED for all commands)
│   ├── core/                   # Core functionality (ping, basic commands)
│   ├── editor/                 # Editor-specific commands
│   │   ├── asset_tools/        # Asset management
│   │   ├── level_editor/       # Level operations
│   │   └── landscape/          # Terrain operations
│   ├── blueprint/              # Blueprint creation and manipulation
│   ├── umg/                    # UI/Widget commands
│   ├── project/                # Project-level settings
│   └── engine/                 # Runtime engine operations
├── unit/                       # Unit tests for Python code
├── performance/                # Performance benchmarks
├── validation/                 # Input validation tests
└── templates/                  # Test templates (USE THESE!)
    ├── command_test_template.py
    └── test_checklist.md
```

## 🚀 Adding Tests for New Commands

### Step 1: Determine Test Location

| Command Type | Test Directory | Example |
|-------------|---------------|---------|
| Actor manipulation | `integration/editor/` | spawn_actor, delete_actor |
| Asset operations | `integration/editor/asset_tools/` | load_asset, save_asset |
| Blueprint operations | `integration/blueprint/` | create_blueprint, compile_blueprint |
| UI/Widget operations | `integration/umg/` | create_widget, add_button |
| Level operations | `integration/editor/level_editor/` | create_level, save_level |
| Project settings | `integration/project/` | create_input_mapping |
| Core/System | `integration/core/` | ping, shutdown |

### Step 2: Use the Test Template

**ALWAYS start with the template:**

```python
# Copy from: tests/templates/command_test_template.py
"""
Integration tests for [COMMAND_NAME] command.

Command: [command_name]
Category: [Editor/Blueprint/Asset/etc]
Added by: [Your Name]
Date: [YYYY-MM-DD]
"""

import pytest
import asyncio
from typing import Dict, Any
from Python.unreal_mcp_client import UnrealMCPClient


class Test[CommandName]Command:
    """Test suite for [command_name] command."""
    
    @pytest.fixture
    async def mcp_client(self):
        """Create an MCP client for testing."""
        client = UnrealMCPClient()
        await client.connect()
        yield client
        await client.disconnect()
    
    async def test_[command_name]_basic(self, mcp_client: UnrealMCPClient):
        """Test basic functionality of [command_name]."""
        # REQUIRED: Test happy path
        response = await mcp_client.send_command("[command_name]", {
            # Add required parameters
        })
        
        assert response["success"] is True
        # Add specific assertions for your command
    
    async def test_[command_name]_error_handling(self, mcp_client: UnrealMCPClient):
        """Test error handling for [command_name]."""
        # REQUIRED: Test with invalid parameters
        response = await mcp_client.send_command("[command_name]", {
            # Add invalid parameters
        })
        
        assert response["success"] is False
        assert "error" in response
    
    async def test_[command_name]_edge_cases(self, mcp_client: UnrealMCPClient):
        """Test edge cases for [command_name]."""
        # REQUIRED: Test boundary conditions
        pass
    
    async def test_[command_name]_performance(self, mcp_client: UnrealMCPClient):
        """Test performance of [command_name]."""
        import time
        
        start_time = time.time()
        response = await mcp_client.send_command("[command_name]", {})
        elapsed = time.time() - start_time
        
        assert elapsed < 1.0  # Should complete in under 1 second
        assert response["success"] is True
    
    async def test_[command_name]_cleanup(self, mcp_client: UnrealMCPClient):
        """Verify [command_name] cleans up properly."""
        # REQUIRED: Ensure no resource leaks
        # Create resources, then verify they're cleaned up
        pass
```

### Step 3: Follow the Checklist

**Before submitting your PR, verify:**

- [ ] Test file in correct directory
- [ ] All 5 required test types implemented
- [ ] Test passes locally (`pytest tests/integration/your_test.py -v`)
- [ ] No hardcoded paths or values
- [ ] Cleanup code in place
- [ ] Docstrings for all test methods
- [ ] Performance assertion (< 1 second)
- [ ] Error messages are validated

## 📝 Test Naming Conventions

### File Names
- **Pattern**: `test_[command_category]_[specific_feature].py`
- **Examples**: 
  - `test_asset_commands.py`
  - `test_blueprint_creation.py`
  - `test_level_commands.py`

### Test Method Names
- **Pattern**: `test_[command_name]_[scenario]`
- **Examples**:
  - `test_spawn_actor_basic`
  - `test_spawn_actor_with_mesh`
  - `test_spawn_actor_invalid_location`
  - `test_spawn_actor_performance`

### Test Class Names
- **Pattern**: `Test[CommandCategory]Commands`
- **Examples**:
  - `TestAssetCommands`
  - `TestBlueprintCommands`
  - `TestLevelCommands`

## 🔴 PROHIBITED PRACTICES

**The following will result in PR rejection:**

1. ❌ **No test file for new command**
2. ❌ **Tests in wrong directory**
3. ❌ **Missing any of the 5 required test types**
4. ❌ **Hardcoded file paths** (use fixtures or parameters)
5. ❌ **No cleanup code** (resource leaks)
6. ❌ **Tests that modify engine assets** (only user-created assets)
7. ❌ **Tests taking > 10 seconds** (use smaller data sets)
8. ❌ **Console output/print statements** (use logging)
9. ❌ **Duplicate test names**
10. ❌ **Tests depending on other tests** (each test must be independent)

## ✅ BEST PRACTICES

### 1. Use Fixtures for Common Setup
```python
@pytest.fixture
async def test_blueprint(self, mcp_client):
    """Create a test blueprint for reuse."""
    response = await mcp_client.send_command("create_blueprint", {
        "blueprint_name": "BP_Test",
        "parent_class": "/Script/Engine.Actor"
    })
    yield response["blueprint_path"]
    # Cleanup
    await mcp_client.send_command("delete_asset", {
        "asset_path": response["blueprint_path"]
    })
```

### 2. Group Related Tests
```python
class TestAssetCommands:
    """All asset-related command tests."""
    
    async def test_load_asset_basic(self, mcp_client):
        pass
    
    async def test_save_asset_basic(self, mcp_client):
        pass
    
    async def test_duplicate_asset_basic(self, mcp_client):
        pass
```

### 3. Use Parametrized Tests for Multiple Scenarios
```python
@pytest.mark.parametrize("actor_type,expected", [
    ("StaticMeshActor", True),
    ("DirectionalLight", True),
    ("InvalidActor", False)
])
async def test_spawn_actor_types(self, mcp_client, actor_type, expected):
    response = await mcp_client.send_command("spawn_actor", {
        "actor_type": actor_type
    })
    assert response["success"] is expected
```

### 4. Always Clean Up Resources
```python
async def test_create_level(self, mcp_client):
    level_path = None
    try:
        response = await mcp_client.send_command("create_level", {
            "level_name": "TestLevel"
        })
        level_path = response["level_path"]
        # ... test logic ...
    finally:
        if level_path:
            await mcp_client.send_command("delete_asset", {
                "asset_path": level_path
            })
```

## 🧪 Running Tests

### Run All Tests
```bash
cd Python
python run_all_tests.py
```

### Run Specific Category
```bash
python -m pytest tests/integration/editor/ -v
```

### Run Single Test File
```bash
python -m pytest tests/integration/core/test_core_commands.py -v
```

### Run with Coverage
```bash
python -m pytest tests/ --cov=. --cov-report=html
```

### Run in Parallel
```bash
python -m pytest tests/ -n auto -v
```

## 📊 Test Coverage Requirements

### Per-Command Requirements
- **Minimum**: 5 tests per command (the required types)
- **Target**: 8-10 tests per command (including variations)
- **Complex Commands**: 10+ tests (blueprint nodes, complex operations)

### Overall Project Requirements
- **Command Coverage**: 100% (every command must have tests)
- **Line Coverage**: 80% minimum
- **Branch Coverage**: 70% minimum
- **Error Path Coverage**: 100% (all error conditions tested)

## 🔄 CI/CD Integration

All tests run automatically on:
- Every push to main
- Every pull request
- Nightly builds

**PR Merge Requirements:**
1. All tests passing
2. No decrease in coverage
3. New commands have all 5 required test types
4. Performance tests pass (< 1 second)

## 📚 Additional Resources

- [Test Template](templates/command_test_template.py)
- [Test Checklist](templates/test_checklist.md)
- [Coverage Report](../TEST_COVERAGE_REPORT.md)
- [Testing Strategy](../TESTING_STRATEGY.md)

## ⚠️ FINAL WARNING

**If you add a command without proper tests:**
1. Your PR will be rejected
2. You'll be asked to add all 5 required test types
3. The PR won't be reviewed until tests are complete

**Quality > Speed. Always.**

---

*Last Updated: 2024-01-14*
*Maintained by: Unreal MCP Team*