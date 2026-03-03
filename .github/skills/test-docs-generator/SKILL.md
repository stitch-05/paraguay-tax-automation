````skill
---
name: test-docs-generator
description: Automatically scan test files and update TESTING.md and tests/README.md with current test counts, coverage stats, and test case documentation.
---

# Test Documentation Generator Skill

## When to use

Use this skill whenever asked to:

- Update test documentation
- Keep test counts in sync with actual tests
- Regenerate test coverage summaries
- Update test case listings in documentation
- Ensure TESTING.md and tests/README.md are current

## Instructions

Follow these exact steps to generate and update test documentation:

### 1. **Scan Test Files and Extract Metadata**

Analyze all test files in `tests/` directory (e.g., `test_form_211.py`, `test_form_955.py`, etc.):

```bash
# List all test files
find tests/ -name "test_*.py" -type f
```

For each test file, extract:
- **Test class names** (e.g., `TestForm211Handler`)
- **Test method names** (e.g., `test_form211_process_success`)
- **Docstrings** - Use first line of docstring as test description
- **Total count** - Number of test functions/methods

### 2. **Run Tests with Coverage**

Execute pytest with coverage to gather metrics:

```bash
python -m pytest tests/ -v --cov=forms --cov=config --cov=http_client --cov-report=term-missing 2>&1
```

Extract:
- **Total test count** (sum of all tests)
- **Pass/fail counts**
- **Execution time**
- **Coverage percentages** per module (forms, config, http_client)
- **Number of unit vs integration tests**

### 3. **Categorize Tests**

Classify tests into categories:

- **Unit Tests** - Tests that mock HTTP responses (no real mockup files accessed). Tests like `test_form211_menu_url_not_found`, `test_form955_operations_invalid_json`
- **Integration Tests** - Tests using real mockup files from `__mockup__/` directory. Tests with "mockup" or "integration" in name
- **By Handler** - Group by handler: Form211Handler, Form955Handler, RegistroHandler, PorcentajesHandler

### 4. **Extract Test Descriptions**

For each test, read its docstring and create a one-line description:

Pattern:
```python
def test_form211_process_success(test_http_client, ...):
    """Full successful VAT form filing workflow"""
```

Result:
```
✓ `test_form211_process_success` - Full successful VAT form filing workflow
```

### 5. **Update TESTING.md**

Update `/Users/mariodian/Source/Scripts/paraguay-tax-automation/TESTING.md` with:

- **Test Suite Summary section**: Update test count, pass rate, execution time
- **Section for each category**: Unit Tests, Integration Tests
- **Coverage metrics**: Show coverage % for forms, config, http_client
- **Link to tests/README.md** for complete documentation

Keep existing structure but update numbers. Example:

```markdown
## Test Suite Summary

- **31 tests** (27 unit + 4 integration)
- **100% pass rate**
- **~0.3 second** execution time
- **Zero external dependencies** (uses mockup mode)

### Test Coverage

**Unit Tests:**

- ✅ Form 211 (VAT) - 7 tests
- ✅ Form 955 (Receipts) - 9 tests
- ✅ Registro (Taxpayer registration) - 5 tests
- ✅ Porcentajes (Income percentages) - 6 tests

**Integration Tests** (using real mockup files):

- ✅ [specific integration tests listed]
```

### 6. **Update tests/README.md**

Update `/Users/mariodian/Source/Scripts/paraguay-tax-automation/tests/README.md` sections:

- **Test Coverage section**: Update per-handler test counts and test names

  For each handler, list all tests with format:
  ```markdown
  ### Form211Handler (7 tests)

  ✓ `test_form211_process_success` - Full successful VAT form filing workflow
  ✓ `test_form211_menu_url_not_found` - Handles missing menu URL
  ...
  ```

- **Test Files section**: Update test file descriptions and counts

- Keep all existing structure, best practices, and strategy sections intact

### 7. **Verification Checklist**

Before finalizing, verify:

- [ ] Total test count matches `pytest --collect-only -q | wc -l`
- [ ] Unit vs integration split is correct (check for "mockup" in test names)
- [ ] All test descriptions extracted from docstrings are present and accurate
- [ ] Coverage percentages reflect actual pytest output
- [ ] Files are formatted consistently with existing markdown structure
- [ ] All checkmarks (✓) and badges display correctly

### 8. **Commit Changes**

If updates were made, commit with:

```
git add TESTING.md tests/README.md
git commit -m "docs: update test documentation with current metrics"
```

## Example Workflow

1. Run: `python -m pytest tests/ -v --cov=forms --cov=config`
2. Get output showing:
   - `31 passed in 0.32s`
   - Coverage: `forms: 95%`, `config: 88%`
3. Scan `test_form_211.py` and extract 7 test cases with docstrings
4. Scan `test_form_955.py` and extract 9 test cases with docstrings
5. Update TESTING.md: "31 tests (27 unit + 4 integration)"
6. Update tests/README.md: Add all test descriptions under each handler section
7. Commit changes

## Tips

- **Accuracy**: Always run pytest to get real metrics, don't estimate
- **Consistency**: Match existing formatting style in both files
- **Descriptions**: Extract directly from test docstrings; rewrite if unclear
- **Coverage**: Focus on forms module; other modules are secondary
- **No Overwrite**: Preserve all existing documentation sections that aren't test counts/descriptions
- **Chronological**: Keep tests listed in order they appear in source files

## Files Modified

- `TESTING.md` - Test suite summary and coverage overview
- `tests/README.md` - Comprehensive test documentation with full test listings

## Files Read (No Changes)

- `tests/test_form_211.py` - Extract test metadata
- `tests/test_form_955.py` - Extract test metadata
- `tests/test_registro.py` - Extract test metadata
- `tests/test_porcentajes.py` - Extract test metadata
- `tests/test_integration_mockup.py` - Extract test metadata

````
