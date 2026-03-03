# Test Suite for Paraguay Tax Automation

This directory contains the pytest test suite for the Paraguay tax automation project.

## Prerequisites

To run tests, you need to install development dependencies:

```bash
./install.sh --dev
```

Or if you already have the environment set up:

```bash
./update.sh --dev
```

This installs `pytest` and `pytest-cov` from `requirements-dev.txt` (or Poetry dev dependencies).

## Quick Start

### Run All Tests

```bash
source venv/bin/activate
python -m pytest tests/ -v
```

### Run Specific Test File

```bash
python -m pytest tests/test_form_211.py -v
python -m pytest tests/test_form_955.py -v
python -m pytest tests/test_integration_mockup.py -v
python -m pytest tests/test_registro.py -v
python -m pytest tests/test_porcentajes.py -v
```

### Run Specific Test

```bash
python -m pytest tests/test_form_211.py::TestForm211Handler::test_form211_menu_url_not_found -v
```

### Run with Coverage

```bash
python -m pytest tests/ --cov=forms --cov=config --cov=http_client -v
```

### Run Tests Matching Pattern

```bash
python -m pytest tests/ -k "form211" -v
python -m pytest tests/ -k "success" -v
```

## Test Organization

### Test Files

- **test_form_211.py** - Unit tests for Form211Handler (VAT form filing)
- **test_form_955.py** - Unit tests for Form955Handler (Receipt management form filing)
- **test_integration_mockup.py** - Integration tests using real `__mockup__` files (Form 211 & 955)
- **test_registro.py** - Unit tests for RegistroHandler (Taxpayer registration profile updates)
- **test_porcentajes.py** - Unit tests for PorcentajesHandler (Activity income percentages updates)

### Testing Approach

All tests use **mockup mode** - no real network calls are made. The tests mock HTTP responses using:

1. **Fixtures in conftest.py** - Reusable test setup:
   - `test_config` - Config object in mockup mode
   - `test_http_client` - HTTPClient with mockup mode enabled
   - `test_profile` - Mock taxpayer profile with RUC 8765432
   - `test_menu` - Mock menu with form application codes
   - `test_notifier_mock` - Mock notification object
   - Mockup response fixtures for each endpoint

2. **Mock HTTP Methods** - Tests override `http_client.get()` and `http_client.post_json()` to return controlled responses

3. **Assertion Patterns** - Tests verify:
   - Handler returns `True` on success and `False` on failure
   - Correct error messages are sent for failures
   - Form data is correctly extracted and submitted

## Testing Strategy: Unit vs Integration

### When to Use Unit Tests (Mocked HTTP)

**Use for:**

- Testing specific error branches (invalid JSON, missing fields, permission denied)
- Testing validation logic (page text checks, operation ID lookups)
- Testing message formatting and notifier behavior
- Fast, focused tests for individual handler methods

**Pattern:**

```python
def test_form955_operations_invalid_json(test_http_client, ...):
    def mock_get(url):
        if url.endswith('/eset/gdi/index.do'):
            return '<html>Menu</html>'
        return 'not valid json'  # Controlled error case

    test_http_client.get = mock_get
    handler = Form955Handler(...)
    assert handler.process('202401') is False
```

**Benefits:**

- Precise control over error conditions
- Fast execution (no file I/O)
- Easy to test edge cases
- Clear assertion failures

### When to Use Integration Tests (`__mockup__`)

**Use for:**

- End-to-end workflow validation (menu → operations → form submission)
- Testing HTTPClient URL mapping and query parameter handling
- Validating that real mockup files match handler expectations
- Ensuring handlers work with actual portal response structure

**Pattern:**

```python
def test_form955_mockup_end_to_end_success(test_http_client, ...):
    # Load real menu from __mockup__/eset/perfil/menu.json
    menu_response = test_http_client.get(
        'https://marangatu.set.gov.py/eset/perfil/menu?t3=test'
    )
    menu = json.loads(menu_response)

    # Let handler make real mockup requests
    handler = Form955Handler(http_client=test_http_client, menu=menu, ...)
    assert handler.process('202401') is True
```

**Benefits:**

- Validates actual file-backed mockup chain
- Catches URL mapping bugs in HTTPClient
- Detects payload shape drift between handler expectations and mockup files
- More realistic integration testing

### Recommended Balance

- **Unit tests: 80-90%** - Fast, precise branch coverage with mocked HTTP responses
- **Integration tests: 10-20%** - Key happy paths using real `__mockup__` files

### Examples in This Suite

**Unit tests with mocked HTTP:**

- `tests/test_form_955.py` (9 tests) - All handler branches with controlled responses
- `tests/test_form_211.py` (7 tests) - VAT form edge cases
- `tests/test_registro.py` (5 tests) - Profile update error handling

**Integration tests with `__mockup__`:**

- `tests/test_form_955_integration_mockup.py` (1 test) - End-to-end Form 955 with real mockup URLs
- Can be extended for other handlers as needed

## Test Coverage

### Form211Handler (7 tests)

✓ `test_form211_process_success` - Full successful VAT form filing workflow
✓ `test_form211_menu_url_not_found` - Handles missing menu URL
✓ `test_form211_menu_page_validation_fails` - Validates menu page contains required text
✓ `test_form211_permit_response_invalid_json` - Handles invalid JSON in permission response
✓ `test_form211_permit_denied` - Handles denied form filing permission
✓ `test_form211_submission_failure` - Handles form submission errors
✓ `test_form211_extraction_of_cyp_token` - Correctly extracts token from permit URL

### Form955Handler (9 tests)

✓ `test_form955_process_success_uses_expected_endpoints` - Full successful workflow with URL validation
✓ `test_form955_menu_url_not_found` - Handles missing menu URL
✓ `test_form955_menu_validation_fails` - Validates menu page
✓ `test_form955_operations_invalid_json` - Handles invalid JSON in operations response
✓ `test_form955_operations_without_confirm_access` - Handles missing operation id 6
✓ `test_form955_receipt_forms_validation_fails` - Validates receipt forms page text
✓ `test_form955_talon_invalid_json` - Handles invalid JSON in talon response
✓ `test_form955_talon_failure` - Handles receipt submission failures with exito=false
✓ `test_form955_empty_operations_list` - Handles empty operations list

### Form955Handler Integration (1 test)

✓ `test_form955_mockup_end_to_end_success` - End-to-end workflow using real `__mockup__` files

### RegistroHandler (5 tests)

✓ `test_registro_process_success` - Full successful taxpayer update workflow
✓ `test_registro_page_validation_fails` - Validates form page
✓ `test_registro_recovery_invalid_json` - Handles invalid recovery response
✓ `test_registro_submission_failure` - Handles submission errors
✓ `test_registro_recovery_data_structure` - Verifies form data extraction

### PorcentajesHandler (6 tests)

✓ `test_porcentajes_process_success` - Full successful percentages update workflow
✓ `test_porcentajes_page_validation_fails` - Validates form page
✓ `test_porcentajes_recovery_invalid_json` - Handles invalid recovery response
✓ `test_porcentajes_submission_failure` - Handles submission errors
✓ `test_porcentajes_recovery_data_parsing` - Verifies activity data parsing
✓ `test_porcentajes_encryption_token_generation` - Verifies encryption token generation

## Configuration

### test_config Fixture

The test config runs in mockup mode with:

- `mockup_mode = True` - No real HTTP requests
- `verbose = False` - Disables animated wait contexts
- `debug = False` - Disables debug output
- `verify_ssl = False` - Matches production settings

### test_http_client Fixture

HTTPClient with:

- Mockup mode enabled
- Mockup directory pointing to `__mockup__/`
- No SSL verification
- User-agent rotation disabled in tests (uses mocks instead)

## Mockup Files

The tests use real mockup response files from `__mockup__/` directory when needed:

- `__mockup__/eset/declaracion/permite.json` - Form 211 permission responses
- `__mockup__/eset/presentar.json` - Form 211 submission responses
- `__mockup__/eset/gdi/di/gestion/listarTiposOperaciones.json` - Form 955 operations
- `__mockup__/eset/gdi/di/talonresumen/procesarTalon.json` - Receipt submission responses
- Plus mockup HTML pages for menu navigation

## Best Practices for Adding Tests

1. **Use fixtures for common setup** - Reuse `test_config`, `test_http_client`, `test_profile`
2. **Mock HTTP responses** - Override `test_http_client.get()` and `post_json()` with controlled responses
3. **Test both success and failure** - Include tests for happy path and error scenarios
4. **Clear assertions** - Use descriptive assertion error messages
5. **Document test purpose** - Docstrings explain what each test validates

## Debugging Tests

### Verbose Output

```bash
python -m pytest tests/test_form_211.py -vv
```

### Show Captured Output

```bash
python -m pytest tests/test_form_211.py -vv -s
```

### Full Traceback

```bash
python -m pytest tests/test_form_211.py --tb=long
```

### Stop on First Failure

```bash
python -m pytest tests/ -x
```

### Specific Test Markers

```bash
# Count how many tests exist
python -m pytest tests/ --collect-only -q
```

## Dependencies

- `pytest` >=7.0.0
- `pytest-cov` >=4.0.0
- Project dependencies: `pycryptodome`

Install with:

```bash
pip install pytest pytest-cov pycryptodome
```

Or in the venv:

```bash
source venv/bin/activate
pip install -r requirements.txt  # If available
```

## CI/CD Integration

Tests are designed to run in CI/CD pipelines:

- No external dependencies required (mockup mode)
- No real credentials needed
- Fast execution (< 1 second per test on average)
- Deterministic results (no flakiness)

## Future Enhancements

Potential additions to test coverage:

- Unit tests for `crypto.py` encryption/decryption
- Unit tests for HTML parsing utilities (`InputParser`, `DivAttributeParser`)
- Unit tests for `config.py` configuration loading
- Integration tests combining multiple handlers
- Performance benchmarks
- Error recovery scenarios (authentication failures, network timeouts, etc.)
