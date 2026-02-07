# AI Coding Agent Instructions - Paraguay Tax Automation

## Project Overview

Automated tax filing system for Paraguay's official tax portal (marangatu.set.gov.py). The system files VAT forms (Form 211), receipt summaries (Form 955), and updates profile information programmatically.

## Architecture Overview

### Execution Flow

1. **Configuration Loading** (`config.py`) - Priority: CLI args → `.env.local` → `.env`
2. **Session Management** (`http_client.py`) - Maintains cookies, rotates user-agents, enforces random delays
3. **Authentication** - Handles login with automatic captcha solving (NopeCHA free/paid, Capsolver)
4. **Data Retrieval** - Fetches profile via encrypted API token (AES-128-CBC)
5. **Form/Profile Routing** - Dispatches to appropriate handlers based on requirements
6. **Notifications** - Sends results via Pushover/Signal/Email (factory pattern)

### Core Components

#### 1. **HTTP Client** (`http_client.py`)

- Stateful client with Mozilla-format cookie persistence (`cookies.txt`)
- User-agent rotation from `user-agents.txt` on each request
- Random 1-4 second delays between requests to avoid detection
- SSL verification disabled by default (portal uses self-signed certs)
- **Critical**: Do not modify delay or user-agent logic without understanding rate-limiting implications

#### 2. **Form Handler Registry** (`forms/__init__.py`)

```python
FORM_HANDLERS = {'211': Form211Handler, '955': Form955Handler}
PROFILE_HANDLERS = {'registro_de_contribuyentes': RegistroHandler, ...}
```

All handlers inherit from `FormHandler` base class with common patterns:

- Parse HTML via custom `InputParser` and `DivAttributeParser` classes
- Extract embedded Angular.js data from `data-ng-init` attributes
- Send encrypted API requests using `crypto.py` utilities

#### 3. **Encryption** (`crypto.py`)

- Uses AES-128-CBC with hardcoded key/IV (matches original Bash implementation)
- **CRITICAL**: Key/IV must NEVER be changed - they're validated by the server
- Encryption flow: JSON → AES-128-CBC → base64 → URL encode

#### 4. **Captcha Handling** (`captcha_solver.py`)

- Primary: NopeCHA free tier (5 solves/day without API key)
- Fallback: Capsolver (paid alternative)
- Extracts `data-sitekey` from HTML for reCAPTCHA v2
- Falls back to manual browser-based solving if automated solutions fail

## Development Patterns

### Adding New Form Handlers

1. Create `forms/form_XXX.py` inheriting from `FormHandler`
2. Implement `process(period: str)` method that returns tuple: `(success: bool, message: str)`
3. Register in `forms/__init__.py`: `FORM_HANDLERS['code'] = YourHandler`
4. Handler subclasses use `self.http` for requests, `self.config` for settings, `self.notify()` for messages

Example pattern from `Form211Handler`:

```python
def process(self, period: str) -> Tuple[bool, str]:
    # Fetch data
    # Parse HTML (using InputParser for form fields)
    # Extract encrypted token via DivAttributeParser
    # POST with encrypted payload: encrypt_json(data) → base64
    # Return (success_bool, result_message)
```

### Configuration & Credentials

- Credentials required: `USERNAME`, `PASSWORD` (Marangatu RUC + password)
- Optional: Captcha API keys, notification settings
- See `.env.example` for all options
- CLI args override .env values: `-u USERNAME -p PASSWORD -ca CAPSOLVER_KEY`

### Logging & Debugging

- `--verbose (-v)` flag: HTTP requests/responses, cookie management
- `--debug (-d)` flag: Full HTML responses, form parsing details
- Use `notify()` method (from base class) for user-visible messages - respects notification config

## Known Limitations & Constraints

- **Form 211**: Only supports 0 VAT filing - cannot submit actual VAT amounts (portal limitation)
- **NopeCHA rate limit**: 5 reCAPTCHA solves/day without API key
- **Cookie persistence**: Cookies automatically saved/loaded from `cookies.txt` - manual clearing required if session expires
- **SSL verification disabled**: Portal uses self-signed certs (intentional)
- **Portal structure**: Relies on parsing AngularJS `data-ng-init` attributes - HTML changes require handler updates

## Testing & Running

```bash
# Installation
./install.sh  # Creates venv or uses Poetry

# Run with Poetry
poetry run python file_taxes.py

# With venv
./venv/bin/python file_taxes.py -v

# With custom credentials
python file_taxes.py -u RUC -p PASSWORD

# With Capsolver (paid captcha service)
python file_taxes.py -ca YOUR_KEY

# Automated (cron)
0 6 1 * * /path/to/venv/bin/python /path/to/file_taxes.py
```

## File Structure Reference

- `file_taxes.py` - Main orchestrator, entry point
- `config.py` - Configuration loading with CLI arg parsing
- `http_client.py` - Session management, cookie/user-agent handling
- `crypto.py` - AES encryption for API tokens (do not modify key/IV)
- `captcha_solver.py` - NopeCHA/Capsolver integration
- `forms/` - Form and profile handlers (plugin system)
- `forms/base.py` - Abstract base with common HTML parsing utilities
- `utils.py` - Helpers like `AnimatedWaitContext`
- `notifications.py` - Multi-service notifier factory (Pushover/Signal/Email)
- `user-agents.txt` - List for user-agent rotation
- `.env.example` - Configuration template

## Common Tasks for AI Agents

### Debugging Issues

- Enable `--debug` flag to inspect HTML parsing
- Check `cookies.txt` exists and is readable (cookie persistence)
- Verify encryption/decryption in `crypto.py` matches request payloads
- Use `--verbose` to trace HTTP client delays and user-agent changes

### Adding Form Support

1. Check portal HTML structure for form fields and `data-ng-init` pattern
2. Inspect encryption format: `POST` parameter should contain base64-encoded AES-128-CBC data
3. Implement handler following `Form211Handler` pattern
4. Test with `python file_taxes.py -d` to debug form parsing

### Notification Integration

- Factory pattern: `get_notifier(config)` returns appropriate service handler
- All notifiers inherit base interface: `send(title, message)`
- Add new service: Create handler in `notifications.py`, update `get_notifier()` factory

### Error Handling

- Captcha failures: Script retries with manual browser prompt
- Cookie expiration: Delete `cookies.txt` and re-run for fresh login
- Portal timeouts: HTTP client includes random delays - increase if needed
- HTML parsing failures: Check if `data-ng-init` structure changed in portal update
