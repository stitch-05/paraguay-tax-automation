# Testing

## Test Suite Documentation

For complete testing documentation, see **[tests/README.md](tests/README.md)**.

## Quick Start

```bash
# Run all tests
python -m pytest tests/ -v

# Run with coverage
python -m pytest tests/ --cov=forms --cov=config -v
```

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

- ✅ Config → HTTPClient workflow
- ✅ Authenticate request
- ✅ Form 211 (VAT) complete workflow
- ✅ Form 955 (Receipts) complete workflow

Unit tests for Registro and Porcentajes use mocked HTTP responses. Integration tests for these handlers are pending actual API response data.
