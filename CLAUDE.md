# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Automated tax filing system for Paraguay that interacts with the official tax portal (marangatu.set.gov.py). Files VAT forms (211), receipt summaries (955), and handles profile updates programmatically.

## Commands

```bash
# Run the script (choose one)
poetry run python file_taxes.py
./venv/bin/python file_taxes.py

# With options
python file_taxes.py -v              # verbose
python file_taxes.py -d              # debug
python file_taxes.py -u USER -p PASS # override credentials
python file_taxes.py -ca API_KEY     # use Capsolver for captcha
python file_taxes.py --mockup        # test with mock data (no real server)

# Testing & Pre-Commit
python -m pytest tests/ -v           # run all tests
python -m pytest tests/test_form_211.py -v  # run specific test file
./.githooks/pre-commit               # manually run pre-commit hook

# Installation
./install.sh                         # creates venv or uses Poetry
```

## Architecture

### Entry Point

`file_taxes.py` orchestrates the workflow:

1. Load config (CLI args > .env.local > .env)
2. Initialize HTTP client with cookie persistence
3. Check session / perform login (handles captcha)
4. Fetch profile data via encrypted API token
5. Check for required profile updates → route to profile handlers
6. Check for pending tax forms → route to form handlers
7. Send notifications on success/failure

### Plugin System

Form handlers follow a registry pattern in `forms/__init__.py`:

```python
FORM_HANDLERS = {
    '211': Form211Handler,      # VAT form
    '955': Form955Handler       # Receipt summary
}
PROFILE_HANDLERS = {
    'registro_de_contribuyentes': RegistroHandler,     # Taxpayer registration
    'porcentajes_actividades': PorcentajesHandler      # Income percentages
}
```

All handlers inherit from `FormHandler` base class in `forms/base.py`.

### Key Modules

- `config.py` - Config loading with shell-style .env parsing
- `http_client.py` - Stateful HTTP client with cookies, user-agent rotation, random delays
- `crypto.py` - AES-128-CBC encryption for API tokens (hardcoded key/IV from original Bash impl)
- `captcha_solver.py` - NopeCHA (free) / Capsolver (paid) for reCAPTCHA v2
- `notifications.py` - Pushover/Signal/Email notifiers with factory pattern
- `utils.py` - AnimatedWaitContext and utility functions for operation feedback

### API Token Encryption

Requests use encrypted `t3` parameter: JSON → AES-128-CBC → base64 → URL encode. The key/IV in `crypto.py` are hardcoded and must not be changed.

### HTTP Client Behavior

- Cookies persisted to `cookies.txt` (Mozilla format)
- Random user-agent from `user-agents.txt` on each request
- 1-4 second random delays between requests
- SSL verification disabled by default

## Adding New Form Handlers

1. Create handler class in `forms/form_XXX.py` inheriting from `FormHandler`
2. Implement `process(period_or_link: str) -> bool` method with `AnimatedWaitContext` around network calls
3. Use `self.get_menu_url(...)`, validate page text, call encrypted endpoints, parse responses
4. Handle errors with `debug_error_detail(...)` and notify with `self.send_message(...)`
5. Register in `forms/__init__.py` FORM_HANDLERS dict with tax code as key

Examples:

- `forms/form_211.py` - Simple encrypted endpoint + HTML form parsing
- `forms/form_955.py` - Receipt summary with operation type selection
- `forms/registro.py` - Multi-step taxpayer registration workflow
- `forms/porcentajes.py` - Multi-step income percentages update workflow

## Configuration

Required env vars: `USERNAME`, `PASSWORD` (Marangatu credentials)

Optional: `CAPSOLVER_API_KEY`, `NOTIFICATION_SERVICE` (pushover|signal|email), notification-specific vars

See `.env.example` for all options.

## Testing & Debugging

- **Mockup mode**: `--mockup` redirects HTTP reads to `__mockup__/` directory; see `__mockup__/README.md` for layout
- **Debug mode**: `--debug` logs request URLs and payload snippets for troubleshooting
- **Pre-commit hook**: `.githooks/pre-commit` automatically runs all tests before each commit; blocks commit if tests fail (`core.hooksPath` is configured by `install.sh --dev`)
- **Session issues**: Check `cookies.txt` (Mozilla format) and test with `--mockup -v` to isolate portal vs. parsing problems

## Limitations

- Form 211 only supports 0 VAT filing (not actual VAT amounts)
- NopeCHA free tier: 5 reCAPTCHA solves/day (sufficient for monthly tax filing)
