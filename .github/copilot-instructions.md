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
- Implement `process(period_or_link: str) -> bool` and use `AnimatedWaitContext` around network phases.
- Read menu URL via `self.get_menu_url(...)`, validate expected page text, call encrypted endpoints, parse JSON, then notify via `self.send_message(...)`.
- Register handler in `forms/__init__.py`; routing is key-based (`'211'`, `'955'`, `'registro_de_contribuyentes'`, etc.).
- Follow existing examples: `forms/form_211.py` (HTML input parsing + submit) and `forms/registro.py` (multi-step recover/verify/save/document accept).

## Dev Workflows

- Install: `./install.sh` (Poetry if present, otherwise `venv` + `requirements.txt`).
- Run: `poetry run python file_taxes.py` or `./venv/bin/python file_taxes.py`.
- Useful flags: `--mockup`, `-v/--verbose`, `-d/--debug`, `-u/-p`, `-nc` (NopeCHA), `-ca` (Capsolver), `--no-verify-ssl`.

## Mockup and Debugging

- `--mockup` redirects HTTP reads to `__mockup__/` with URL-path mirroring (tries `.json`, `.html`, then index files); query params are ignored for file lookup.
- Use `--debug` to inspect request URLs/payload snippets and parser failures; handlers call `debug_error_detail(...)` for extra context.
- For session issues, check `cookies.txt` behavior before changing login logic.

## Integration Notes

- External services: Marangatu portal (`https://marangatu.set.gov.py`), NopeCHA/Capsolver APIs, optional Pushover/Signal/SMTP notifiers.
- `notifications.py` uses a factory (`get_notifier`) and falls back to `NoopNotifier`; keep new notifier integrations behind this interface.
- `verify_ssl` is configurable and may be disabled for portal compatibility; do not hard-force SSL validation changes without need.
