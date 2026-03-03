# AI Coding Agent Instructions - Paraguay Tax Automation

## Big Picture

- Entry point is `file_taxes.py`; it orchestrates config load, session/login, profile fetch, profile-update routing, pending-form routing, and notifications.
- Runtime flow depends on encrypted `t3` query payloads (`crypto.encrypt`): JSON → AES-128-CBC → base64 → URL-encoded token.
- `forms/__init__.py` is the plugin boundary (`FORM_HANDLERS` and `PROFILE_HANDLERS`); new automation features are usually added as new handlers.

## Critical Components

- `http_client.py`: stateful client with cookie persistence (`cookies.txt`), random user-agent selected at client init from `user-agents.txt`, and shared request path in `_make_request`.
- `config.py`: config precedence is CLI args > `.env.local` > `.env`; `.env` parser supports shell-style `export KEY="value"` lines.
- `forms/base.py`: shared primitives (`FormHandler`, `InputParser`, `DivAttributeParser`) used across all form/profile handlers.
- `crypto.py`: hardcoded AES key/IV must stay unchanged (server compatibility).
- `captcha_solver.py`: default path prefers NopeCHA (works without key, limited free credits), then Capsolver if configured.

## Handler Pattern (Project Convention)

- Implement new handlers in `forms/form_XXX.py` (tax) or `forms/<feature>.py` (profile), subclassing `FormHandler`.
- Implement `process(period_or_link: str) -> bool` and use `AnimatedWaitContext` around network phases (pass `.config.is_verbose`, `.config.is_debug`, `.config.mockup_mode`).
- Typical handler flow: get menu URL → validate page text → call encrypted endpoint → parse JSON → handle errors with `debug_error_detail(...)` → notify with `self.send_message(...)`.
- Register handler in `forms/__init__.py` (`FORM_HANDLERS` for tax forms, `PROFILE_HANDLERS` for profile updates); routing is key-based (`'211'`, `'955'`, `'registro_de_contribuyentes'`, etc.).
- Reuse `InputParser` for form input extraction and `DivAttributeParser` for Angular ng-init data extraction (see `forms/base.py`).
- Follow existing examples: `forms/form_211.py` (simple encrypted endpoint + HTML form parsing) and `forms/registro.py` (multi-step workflow with recovery/verify/save).

## Dev Workflows

- Install: `./install.sh` (Poetry if present, otherwise `venv` + `requirements.txt`); add `--dev` flag for test dependencies (pytest, pytest-cov).
- Update: `./update.sh` (auto-detects Poetry/venv; add `--dev` to preserve test dependencies).
- Run: `poetry run python file_taxes.py` or `./venv/bin/python file_taxes.py`.
- Useful flags: `--mockup`, `-v/--verbose`, `-d/--debug`, `-u/-p`, `-nc` (NopeCHA), `-ca` (Capsolver), `--no-verify-ssl`.
- Tests: `python -m pytest tests/ -v`; target a file with `python -m pytest tests/test_form_211.py -v`.
- **Pre-commit hook**: `.githooks/pre-commit` automatically runs all tests before each commit and blocks if tests fail (after `core.hooksPath` setup by `./install.sh --dev`); run manually with `./.githooks/pre-commit`.

## Mockup and Debugging

- `--mockup` mode redirects HTTP reads to `__mockup__/` with URL-path mirroring; file lookup tries `.json`, `.html`, then index files (query params ignored); see `__mockup__/README.md` for layout.
- Use `--debug` to inspect request URLs, payload snippets, and parser failures; handlers call `debug_error_detail(...)` for structured error logging.
- For session/login issues, check `cookies.txt` (Mozilla format, persistent) and test with `--mockup -v` first to isolate portal vs. parsing issues.
- AnimatedWaitContext provides user feedback for long operations; wrap with `with AnimatedWaitContext('message', is_verbose, is_debug, mockup_mode):` around network calls.

## Integration Notes

- External services: Marangatu portal (`https://marangatu.set.gov.py`), NopeCHA/Capsolver APIs, optional Pushover/Signal/SMTP notifiers.
- `notifications.py` uses a factory (`get_notifier`) and falls back to `NoopNotifier`; keep new notifier integrations behind this interface.
- `verify_ssl` is configurable and may be disabled for portal compatibility; do not hard-force SSL validation changes without need.
