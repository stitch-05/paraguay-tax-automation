# File Taxes Paraguay

Automated tax filing system for Paraguay tax residents. Interacts with Paraguay's official tax portal (marangatu.set.gov.py) to file:

- VAT forms (Form 211) - monthly filings
- Receipt summary forms (Form 955)
- Profile information updates (taxpayer registration)

## Installation

```bash
git clone https://github.com/stitch-05/paraguay-tax-automation.git
cd paraguay-tax-automation
./install.sh
```

The install script will:

1. Create a virtual environment (or use Poetry if available)
2. Install dependencies
3. Create `.env` from `.env.example`
4. Configure Git hooks (`core.hooksPath=.githooks`) when `--dev` is used

## Update

To update to the latest version and refresh dependencies:

```bash
./update.sh
```

## Configuration

Edit `.env` and add your Marangatu credentials:

```bash
export USERNAME="your_ruc_number"
export PASSWORD="your_password"
```

### Automatic Captcha Solving

The script uses [NopeCHA](https://nopecha.com/) for automatic captcha solving.

**To use the free tier** (5 reCAPTCHA v2 solves per day):

1. Uncomment the `NOPECHA_API_KEY` line in `.env`
2. Leave it empty: `export NOPECHA_API_KEY=""`

**For higher limits**, get an API key at [nopecha.com](https://nopecha.com/) and set it:

```bash
export NOPECHA_API_KEY="your_nopecha_api_key"
```

When a captcha is required during login, the script will automatically:

- Detect the captcha type (reCAPTCHA v2)
- Submit the captcha to NopeCHA for solving
- Retry login with the solved captcha response

If NopeCHA fails, you'll be prompted to solve the captcha manually in a browser.

#### Alternative: Capsolver (paid service)

```bash
export CAPSOLVER_API_KEY="your_capsolver_api_key"
```

### Optional: Notifications

You can configure notifications via Pushover, Signal, or Email. See `.env.example` for all options.

## Usage

```bash
# With Poetry
poetry run python file_taxes.py

# With venv
./venv/bin/python file_taxes.py

# Or activate venv first
source venv/bin/activate
python file_taxes.py
```

### Command Line Options

```bash
python file_taxes.py --help

# Override credentials
python file_taxes.py -u USERNAME -p PASSWORD

# Use NopeCHA with API key (higher limits than free tier)
python file_taxes.py -nc YOUR_NOPECHA_API_KEY

# Or use Capsolver (paid)
python file_taxes.py -ca YOUR_CAPSOLVER_API_KEY

# Verbose/debug mode
python file_taxes.py -v    # verbose
python file_taxes.py -d    # debug
```

### Run automatically via cron

Add a cron job to run the script at your desired schedule. For example, to run it every day at 3:00 AM:

#### Using Poetry

```cron
0 3 * * * cd /path/to/paraguay-tax-automation && /path/to/poetry run python file_taxes.py >/dev/null 2>&1
```

#### Using venv

```cron
0 3 * * * /path/to/paraguay-tax-automation/venv/bin/python /path/to/paraguay-tax-automation/file_taxes.py >/dev/null 2>&1
```

Adjust the paths and schedule as needed.

To find the poetry path, run `which poetry` in your terminal.

To log output to a file instead of discarding it, replace `>/dev/null 2>&1` with `>> /path/to/logfile.log 2>&1` e.g.:

```cron
0 3 * * * cd /path/to/paraguay-tax-automation && /path/to/poetry run python file_taxes.py >> /home/<user>/taxes.log 2>&1
```

## Requirements

- Python 3.8+
- pycryptodomex

## Known Limitations

- Form 211 only supports 0 VAT filing
- NopeCHA free tier allows 5 reCAPTCHA solves/day (enough for monthly tax filing)

## Development

This section contains information for developers who want to contribute, test, or modify the code.

### Development Installation

To install with development dependencies (for running tests):

```bash
./install.sh --dev
```

### Updating

```bash
./update.sh
```

The update script automatically detects which environment you're using (Poetry or venv) and whether dev dependencies are installed, keeping everything in sync.

### Advanced Options

By default, the scripts use Poetry if it's available on your system. Otherwise, they use pip/venv.

**Force pip/venv instead of Poetry:**

```bash
./install.sh --pip          # use pip/venv even if Poetry is available
./install.sh --pip --dev    # with dev dependencies
./update.sh --pip           # update using pip/venv
```

**Clean reinstall:**

```bash
./install.sh --force        # removes all environments and reinstalls
./install.sh --force --dev  # clean install with dev dependencies
```

### Mockup Mode

For development and testing without making real server requests:

```bash
python file_taxes.py --mockup --verbose
```

In mockup mode, the HTTP client reads responses from local files in the `__mockup__/` directory instead of making network requests. This is useful for:

- Offline development and testing
- Avoiding rate limits during development
- Examining server response structures
- Testing error handling

See [`__mockup__/README.md`](__mockup__/README.md) for details on the directory structure and URL mapping.

### Running Tests

After installing with `--dev` flag:

```bash
# With Poetry
poetry run python -m pytest tests/ -v

# With venv
source venv/bin/activate
python -m pytest tests/ -v
```

See [`tests/README.md`](tests/README.md) for detailed testing documentation.

### Continuous Integration (CI)

GitHub Actions CI runs automatically on every pull request and on pushes to `main` using Python 3.8 and 3.11.

Workflow file: [`.github/workflows/ci.yml`](.github/workflows/ci.yml)

To run the same check locally:

```bash
python -m pytest tests/ -v
```

### Pre-commit Hook

This repository tracks Git hooks in [`.githooks/`](.githooks/). The install script configures your local clone automatically:

```bash
./install.sh --dev
```

Manual setup (if needed):

```bash
git config core.hooksPath .githooks
chmod +x .githooks/pre-commit
```

After setup, the pre-commit hook automatically runs tests before every `git commit`.

### Project Structure

- `file_taxes.py` - Main entry point
- `forms/` - Form handler plugins (211, 955, registro, etc.)
- `http_client.py` - HTTP client with session management
- `config.py` - Configuration loader
- `crypto.py` - AES encryption for API tokens
- `captcha_solver.py` - Captcha solving integration
- `notifications.py` - Notification service handlers
- `tests/` - Test suite
- `__mockup__/` - Mock data for testing

For AI-assisted development, see the prompts and guidelines in [`CLAUDE.md`](CLAUDE.md) (Claude) and [`.github/copilot-instructions.md`](.github/copilot-instructions.md) (GitHub Copilot).

## License

MIT
