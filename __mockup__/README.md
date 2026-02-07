# Mockup Mode

This directory contains mockup data files that simulate server responses for testing and development purposes.

## Quick Reference

### Enable Mockup Mode

```bash
# CLI
python file_taxes.py --mockup

# Environment variable (.env)
export MOCKUP_MODE="true"
```

### How It Works

```
Real Request:
https://marangatu.set.gov.py/eset/perfil/vencimientos?t3=xxx
                                ↓
Mockup File:
__mockup__/eset/perfil/vencimientos.json
```

### File Organization

```
__mockup__/
├── README.md
└── eset/
    └── perfil/
        └── vencimientos.json  ← Maps to /eset/perfil/vencimientos
```

### Extension Priority

1. `.json` (for JSON responses)
2. `.html` (for HTML pages)
3. No extension (raw files)

### Debug Output

```bash
python file_taxes.py --mockup --debug

# Output:
MOCKUP: GET https://marangatu.set.gov.py/eset/perfil/vencimientos?t3=xxx
Loading mockup from: __mockup__/eset/perfil/vencimientos.json
```

### Testing

```bash
# Run tests
python3 test_mockup.py
python3 test_integration_mockup.py
```

### Common Use Cases

- **Development without authentication**: Test code without logging in
- **Offline work**: Develop without internet connection
- **Response structure analysis**: Examine API responses
- **CI/CD testing**: Automated tests without hitting real server

## Usage

Enable mockup mode by using the `--mockup` flag:

```bash
python file_taxes.py --mockup --verbose
```

Or set it in your `.env` file:

```bash
MOCKUP_MODE=true
```

## Directory Structure

The directory structure mirrors the URL path structure of the server:

```
__mockup__/
└── eset/
    └── perfil/
        └── vencimientos.json
```

## URL Mapping

URLs are mapped to files as follows:

- `https://marangatu.set.gov.py/eset/perfil/vencimientos?t3=xxx` → `__mockup__/eset/perfil/vencimientos.json`
- Query parameters are ignored for file lookup
- The system tries `.json` extension first, then `.html`, then without extension

## File Format

- **JSON responses**: Use `.json` extension
- **HTML responses**: Use `.html` extension
- Files should contain the exact response body expected from the server

## Example

Given URL:

```
https://marangatu.set.gov.py/eset/perfil/vencimientos?t3=xxx
```

The mockup file should be located at:

```
__mockup__/eset/perfil/vencimientos.json
```

## Benefits

- **Offline Development**: Develop and test without server access
- **Faster Testing**: No network delays or rate limiting
- **Reproducible Tests**: Consistent responses for testing
- **API Exploration**: Examine server responses without authentication
