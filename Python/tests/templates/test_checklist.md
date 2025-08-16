# Test Checklist for New MCP Commands

**Command Name:** ___________________  
**PR Number:** #___________________  
**Developer:** ___________________  
**Date:** ___________________

## 📋 Pre-Submission Checklist

### 1. Test File Location
- [ ] Test file is in the correct directory based on command type
- [ ] File follows naming convention: `test_[category]_[feature].py`
- [ ] File is not in the root `tests/` directory

### 2. Required Test Coverage (ALL 5 MUST BE CHECKED)
- [ ] ✅ **Basic Functionality Test** - Happy path with valid parameters
- [ ] ✅ **Error Handling Test** - At least 4 error scenarios tested
- [ ] ✅ **Edge Cases Test** - Boundary conditions and special values
- [ ] ✅ **Performance Test** - Verifies < 1 second execution
- [ ] ✅ **Cleanup Test** - Ensures no resource leaks

### 3. Code Quality
- [ ] All test methods have descriptive docstrings
- [ ] No hardcoded paths (use parameters or fixtures)
- [ ] No print statements (use logging if needed)
- [ ] Each test is independent (no test dependencies)
- [ ] Proper assertions with failure messages

### 4. Test Execution
- [ ] Tests pass locally: `pytest [your_test_file] -v`
- [ ] No warnings during test execution
- [ ] Tests run in < 10 seconds total
- [ ] Tests work with both empty and populated Unreal projects

### 5. Resource Management
- [ ] All created resources are cleaned up in finally blocks
- [ ] Fixtures have proper teardown
- [ ] No modifications to engine assets
- [ ] Temporary files are deleted

### 6. Error Scenarios Tested
- [ ] Missing required parameters
- [ ] Invalid parameter types
- [ ] Invalid parameter values
- [ ] Non-existent resource references
- [ ] Empty strings and null values
- [ ] Special characters in strings
- [ ] Extremely large values
- [ ] Concurrent execution (if applicable)

### 7. Documentation
- [ ] Command category documented in test file header
- [ ] Author and date included
- [ ] PR number referenced
- [ ] Test purpose clearly explained in docstrings

### 8. Integration
- [ ] Test added to appropriate test suite class
- [ ] Test discoverable by pytest
- [ ] Compatible with parallel test execution
- [ ] Works with CI/CD pipeline

## 🔍 Review Criteria

### Automated Checks (CI/CD)
- [ ] All tests pass in CI environment
- [ ] Coverage hasn't decreased
- [ ] Performance benchmarks met
- [ ] No test flakiness detected

### Manual Review
- [ ] Test actually validates the command functionality
- [ ] Edge cases are meaningful (not arbitrary)
- [ ] Error messages are validated, not just presence
- [ ] Cleanup is thorough

## 📊 Test Metrics

Fill in after running tests:

- **Number of test methods:** _____
- **Number of assertions:** _____
- **Execution time:** _____ seconds
- **Lines of test code:** _____
- **Coverage of command code:** _____%

## 🚫 Common Rejection Reasons

Avoid these to prevent PR rejection:

1. ❌ Missing any of the 5 required test types
2. ❌ Tests in wrong directory structure
3. ❌ No cleanup code for created resources
4. ❌ Hardcoded file paths or values
5. ❌ Tests that depend on each other
6. ❌ Missing error handling tests
7. ❌ Performance test missing or > 1 second
8. ❌ No docstrings on test methods
9. ❌ Modifying engine/built-in assets
10. ❌ Print statements instead of assertions

## 📝 Additional Notes

Space for any additional context or explanations:

```
[Add any special considerations, known limitations, or explanations here]
```

## ✅ Final Confirmation

**By checking this box, I confirm that:**

- [ ] I have completed ALL items in this checklist
- [ ] My tests follow the project's testing standards
- [ ] I have used the provided test template
- [ ] I understand my PR will be rejected if tests are incomplete

---

**Signature:** ___________________  
**Date:** ___________________

---

*This checklist must be included in your PR description with all items checked.*