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

## Configuration

Edit `.env` and add your Marangatu credentials:

```bash
export USERNAME="your_ruc_number"
export PASSWORD="your_password"
```

### Automatic Captcha Solving

The script uses [NopeCHA](https://nopecha.com/) free tier by default for automatic captcha solving:

- **Free tier**: 5 reCAPTCHA v2 solves per day (no API key needed)
- **With API key**: Higher daily limits

When a captcha is required during login, the script will automatically:

- Detect the captcha type (reCAPTCHA v2)
- Submit the captcha to NopeCHA for solving
- Retry login with the solved captcha response

If NopeCHA fails, you'll be prompted to solve the captcha manually in a browser.

#### Optional: Custom API keys

```bash
# NopeCHA (recommended, free tier available)
export NOPECHA_API_KEY="your_nopecha_api_key"

# Or Capsolver (paid alternative)
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

Add to your crontab (edit with `crontab -e`):

```cron
0 6 1 * * /path/to/paraguay-tax-automation/venv/bin/python /path/to/paraguay-tax-automation/file_taxes.py >/dev/null 2>&1
```

This will run the script on the 1st of every month at 6 AM.

## Requirements

- Python 3.8+
- pycryptodome

## Known Limitations

- Form 211 only supports 0 VAT filing
- NopeCHA free tier allows 5 reCAPTCHA solves/day (enough for monthly tax filing)

## License

MIT
