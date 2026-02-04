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
FORM_HANDLERS = {'211': Form211Handler, '955': Form955Handler}
PROFILE_HANDLERS = {'registro_de_contribuyentes': RegistroHandler, ...}
```

All handlers inherit from `FormHandler` base class in `forms/base.py`.

### Key Modules
- `config.py` - Config loading with shell-style .env parsing
- `http_client.py` - Stateful HTTP client with cookies, user-agent rotation, random delays
- `crypto.py` - AES-128-CBC encryption for API tokens (hardcoded key/IV from original Bash impl)
- `captcha_solver.py` - NopeCHA (free) / Capsolver (paid) for reCAPTCHA v2
- `notifications.py` - Pushover/Signal/Email notifiers with factory pattern

### API Token Encryption
Requests use encrypted `t3` parameter: JSON → AES-128-CBC → base64 → URL encode. The key/IV in `crypto.py` are hardcoded and must not be changed.

### HTTP Client Behavior
- Cookies persisted to `cookies.txt` (Mozilla format)
- Random user-agent from `user-agents.txt` on each request
- 1-4 second random delays between requests
- SSL verification disabled by default

## Adding New Form Handlers

1. Create handler class in `forms/form_XXX.py` inheriting from `FormHandler`
2. Implement `process(period)` method
3. Register in `forms/__init__.py` FORM_HANDLERS dict with tax code as key

## Configuration

Required env vars: `USERNAME`, `PASSWORD` (Marangatu credentials)

Optional: `CAPSOLVER_API_KEY`, `NOTIFICATION_SERVICE` (pushover|signal|email), notification-specific vars

See `.env.example` for all options.

## Limitations

- Form 211 only supports 0 VAT filing (not actual VAT amounts)
- NopeCHA free tier: 5 reCAPTCHA solves/day (sufficient for monthly tax filing)
