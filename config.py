"""Configuration management for file-taxes-paraguay."""

import argparse
import os
import re
from pathlib import Path
from typing import Optional


class Config:
    """Configuration container with values from .env files and CLI arguments."""

    def __init__(self):
        # Credentials
        self.username: str = ''
        self.password: str = ''

        # Captcha solver (NopeCHA free tier by default, Capsolver as paid alternative)
        self.nopecha_api_key: str = ''
        self.capsolver_api_key: str = ''

        # Notification settings
        self.notification_service: Optional[str] = None
        self.message_prefix: str = '\U0001F1F5\U0001F1FE taxes\n'  # Paraguay flag emoji

        # Pushover
        self.pushover_token: str = ''
        self.pushover_user: str = ''

        # Signal
        self.signal_user: str = ''
        self.signal_recipient: str = ''

        # Email/SMTP
        self.smtp_host: str = ''
        self.smtp_port: int = 587
        self.smtp_addr: str = ''
        self.smtp_pwd: str = ''
        self.smtp_recv: str = ''

        # HTTP client settings
        self.wget_output: str = '-q'  # -q for quiet, '' for verbose, -d for debug
        self.wget_flags: str = ''
        self.verify_ssl: bool = False  # Default to False to match --no-check-certificate

        # Working directory (same as the script)
        self.working_dir: Path = Path(__file__).parent

    @property
    def cookies_file(self) -> Path:
        return self.working_dir / 'cookies.txt'

    @property
    def user_agents_file(self) -> Path:
        return self.working_dir / 'user-agents.txt'

    @property
    def env_file(self) -> Path:
        return self.working_dir / '.env'

    @property
    def env_local_file(self) -> Path:
        return self.working_dir / '.env.local'

    @property
    def is_verbose(self) -> bool:
        return self.wget_output in ('', '-d')

    @property
    def is_debug(self) -> bool:
        return self.wget_output == '-d'


def parse_env_file(filepath: Path) -> dict:
    """
    Parse a shell-style .env file.

    Handles lines like:
        export KEY="value"
        export KEY='value'
        export KEY="value" # comment
        export KEY="value"$'\\n'
        KEY=value
        # comments
    """
    if not filepath.exists():
        return {}

    env_vars = {}
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()

            # Skip empty lines and comments
            if not line or line.startswith('#'):
                continue

            # Remove 'export ' prefix if present
            if line.startswith('export '):
                line = line[7:]

            # Match KEY=value
            match = re.match(r'^([A-Za-z_][A-Za-z0-9_]*)=(.*)$', line)
            if match:
                key = match.group(1)
                rest = match.group(2)

                # Parse the value considering quotes
                value = ''
                if rest.startswith('"'):
                    # Double-quoted value - find closing quote
                    end_quote = rest.find('"', 1)
                    if end_quote != -1:
                        value = rest[1:end_quote]
                        # Check for $'\n' suffix after the closing quote
                        suffix = rest[end_quote + 1:].strip()
                        if suffix.startswith("$'\\n'"):
                            value += '\n'
                    else:
                        value = rest[1:]  # No closing quote found
                elif rest.startswith("'"):
                    # Single-quoted value - find closing quote
                    end_quote = rest.find("'", 1)
                    if end_quote != -1:
                        value = rest[1:end_quote]
                    else:
                        value = rest[1:]  # No closing quote found
                else:
                    # Unquoted value - take until comment or end
                    if '#' in rest:
                        value = rest.split('#')[0].strip()
                    else:
                        value = rest.strip()

                env_vars[key] = value

    return env_vars


def load_config(args: Optional[argparse.Namespace] = None) -> Config:
    """
    Load configuration from .env files and CLI arguments.

    Priority: CLI args > .env.local > .env > defaults
    """
    config = Config()

    # Load .env file
    env_vars = parse_env_file(config.env_file)

    # Override with .env.local
    env_vars.update(parse_env_file(config.env_local_file))

    # Apply environment variables to config
    if 'USERNAME' in env_vars:
        config.username = env_vars['USERNAME']
    if 'PASSWORD' in env_vars:
        config.password = env_vars['PASSWORD']
    if 'NOPECHA_API_KEY' in env_vars:
        config.nopecha_api_key = env_vars['NOPECHA_API_KEY']
    if 'CAPSOLVER_API_KEY' in env_vars:
        config.capsolver_api_key = env_vars['CAPSOLVER_API_KEY']
    if 'NOTIFICATION_SERVICE' in env_vars:
        config.notification_service = env_vars['NOTIFICATION_SERVICE']
    if 'MESSAGE_PREFIX' in env_vars:
        config.message_prefix = env_vars['MESSAGE_PREFIX']
    if 'PUSHOVER_TOKEN' in env_vars:
        config.pushover_token = env_vars['PUSHOVER_TOKEN']
    if 'PUSHOVER_USER' in env_vars:
        config.pushover_user = env_vars['PUSHOVER_USER']
    if 'SIGNAL_USER' in env_vars:
        config.signal_user = env_vars['SIGNAL_USER']
    if 'SIGNAL_RECIPIENT' in env_vars:
        config.signal_recipient = env_vars['SIGNAL_RECIPIENT']
    if 'SMTP_HOST' in env_vars:
        config.smtp_host = env_vars['SMTP_HOST']
    if 'SMTP_PORT' in env_vars:
        try:
            config.smtp_port = int(env_vars['SMTP_PORT'])
        except ValueError:
            pass
    if 'SMTP_ADDR' in env_vars:
        config.smtp_addr = env_vars['SMTP_ADDR']
    if 'SMTP_PWD' in env_vars:
        config.smtp_pwd = env_vars['SMTP_PWD']
    if 'SMTP_RECV' in env_vars:
        config.smtp_recv = env_vars['SMTP_RECV']
    if 'WGET_OUTPUT' in env_vars:
        config.wget_output = env_vars['WGET_OUTPUT']
    if 'WGET_FLAGS' in env_vars:
        config.wget_flags = env_vars['WGET_FLAGS']
        # Parse --no-check-certificate flag
        if '--no-check-certificate' in config.wget_flags:
            config.verify_ssl = False

    # Override with CLI arguments if provided
    if args:
        if args.username:
            config.username = args.username
        if args.password:
            config.password = args.password
        if hasattr(args, 'nopecha_api_key') and args.nopecha_api_key:
            config.nopecha_api_key = args.nopecha_api_key
        if hasattr(args, 'capsolver_api_key') and args.capsolver_api_key:
            config.capsolver_api_key = args.capsolver_api_key
        if args.notification_service:
            config.notification_service = args.notification_service
        if args.pushover_token:
            config.pushover_token = args.pushover_token
        if args.pushover_user:
            config.pushover_user = args.pushover_user
        if args.signal_user:
            config.signal_user = args.signal_user
        if args.signal_recipient:
            config.signal_recipient = args.signal_recipient
        if args.smtp_server:
            parts = args.smtp_server.split(':')
            config.smtp_host = parts[0]
            if len(parts) > 1:
                try:
                    config.smtp_port = int(parts[1])
                except ValueError:
                    pass
        if args.smtp_user:
            config.smtp_addr = args.smtp_user
        if args.smtp_password:
            config.smtp_pwd = args.smtp_password
        if args.smtp_recipient:
            config.smtp_recv = args.smtp_recipient
        if args.message_prefix:
            config.message_prefix = args.message_prefix
        if args.wget_output is not None:
            config.wget_output = args.wget_output
        if args.wget_flags:
            config.wget_flags = args.wget_flags

    return config


def create_argument_parser() -> argparse.ArgumentParser:
    """Create the CLI argument parser."""
    parser = argparse.ArgumentParser(
        description='Automatically file taxes in Paraguay.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  python file_taxes.py -u USERNAME -p PASSWORD
  python file_taxes.py -ns signal -su +10123456789 -sr +19876543210
  python file_taxes.py --verbose
  python file_taxes.py --debug
'''
    )

    # Credentials
    parser.add_argument('-u', '--username', help='Marangatu login username')
    parser.add_argument('-p', '--password', help='Marangatu login password')

    # Captcha solving (NopeCHA free tier used by default)
    parser.add_argument('-nc', '--nopecha-api-key', help='NopeCHA API key (optional, free tier works without key)')
    parser.add_argument('-ca', '--capsolver-api-key', help='Capsolver API key (paid alternative)')

    # Notification service
    parser.add_argument('-ns', '--notification-service',
                        choices=['pushover', 'signal', 'email'],
                        help='Choose notification service')
    parser.add_argument('-mp', '--message-prefix',
                        help='Prefix for notification messages')

    # Pushover
    parser.add_argument('-pt', '--pushover-token',
                        help='Pushover application API token')
    parser.add_argument('-pu', '--pushover-user',
                        help='Pushover user/group key')

    # Signal
    parser.add_argument('-su', '--signal-user',
                        help='Signal sender phone number')
    parser.add_argument('-sr', '--signal-recipient',
                        help='Signal recipient phone number')

    # Email/SMTP
    parser.add_argument('-Ss', '--smtp-server',
                        help='SMTP server and port (HOST:PORT)')
    parser.add_argument('-Su', '--smtp-user',
                        help='SMTP username/email address')
    parser.add_argument('-Sp', '--smtp-password',
                        help='SMTP password')
    parser.add_argument('-Sr', '--smtp-recipient',
                        help='Email recipient(s), separate with semicolon')

    # Debug/verbosity
    parser.add_argument('-wo', '--wget-output',
                        help='Output mode: -q (quiet), empty (verbose), -d (debug)')
    parser.add_argument('-wf', '--wget-flags',
                        help='Additional flags for HTTP requests')
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='Enable verbose output')
    parser.add_argument('-d', '--debug', action='store_true',
                        help='Enable debug output')

    return parser


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = create_argument_parser()
    args = parser.parse_args()

    # Handle shorthand verbose/debug flags
    if args.debug:
        args.wget_output = '-d'
    elif args.verbose:
        args.wget_output = ''

    return args
