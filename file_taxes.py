#!/usr/bin/env python3
"""
Automatically file taxes in Paraguay.

This script interacts with Paraguay's official tax portal (marangatu.set.gov.py)
to file VAT forms (Form 211), receipt summary forms (Form 955), and update
profile information.
"""

import base64
import json
import re
import sys
from datetime import datetime
from typing import Any, Dict, List, Optional

from captcha_solver import get_captcha_client
from config import Config, load_config, parse_args
from crypto import encrypt
from http_client import HTTPClient
from notifications import get_notifier


def get_current_period() -> str:
    """
    Get the current filing period (previous month in YYYYMM format).

    In January, this returns December of the previous year.
    """
    now = datetime.now()
    year = now.year
    month = now.month

    # Filing is for the previous month
    if month == 1:
        year -= 1
        month = 12
    else:
        month -= 1

    return f'{year}{month:02d}'


def extract_captcha_info(html: str) -> Dict[str, Optional[str]]:
    """
    Extract captcha information from HTML.

    Returns:
        Dict with 'type' (recaptcha_v2, hcaptcha, or None) and 'site_key'
    """
    info = {'type': None, 'site_key': None}

    # Check for reCAPTCHA v2
    recaptcha_match = re.search(r'data-sitekey=["\']([^"\']+)["\']', html)
    if recaptcha_match:
        info['type'] = 'recaptcha_v2'
        info['site_key'] = recaptcha_match.group(1)
        return info

    # Alternative pattern for Google reCAPTCHA
    recaptcha_match2 = re.search(r'google\.com/recaptcha.*?k=([^&"\'\']+)', html, re.DOTALL)
    if recaptcha_match2:
        info['type'] = 'recaptcha_v2'
        info['site_key'] = recaptcha_match2.group(1)
        return info

    return info


def attempt_captcha_solve(config: Config, http: HTTPClient, url_base: str, url_host: str,
                         login_data: Dict[str, str], send_message) -> Optional[str]:
    """
    Attempt to solve a captcha automatically.

    Uses NopeCHA free tier by default (5 reCAPTCHA v2 solves/day).
    Falls back to Capsolver if configured.

    Args:
        config: Configuration object
        http: HTTP client
        url_base: Base URL
        url_host: Host URL
        login_data: Login data dictionary
        send_message: Function to send notification messages

    Returns:
        Login response if successful, None if captcha solving failed
    """
    captcha_client = get_captcha_client(
        nopecha_api_key=config.nopecha_api_key,
        capsolver_api_key=config.capsolver_api_key,
        verbose=config.is_verbose
    )

    print('Captcha required - attempting automatic solving with NopeCHA...')

    # Get login page to extract captcha info
    login_page_url = f'{url_host}/eset/login?login_error=2&usuario={config.username}'
    login_page = http.get(login_page_url)

    captcha_info = extract_captcha_info(login_page)

    if not captcha_info['type'] or not captcha_info['site_key']:
        send_message('Error', 'Captcha detected but could not identify type. Please solve it manually.')
        return None

    print(f"Detected {captcha_info['type']} with site key: {captcha_info['site_key']}")

    # Solve the captcha
    captcha_solution = None
    if captcha_info['type'] == 'recaptcha_v2':
        captcha_solution = captcha_client.solve_recaptcha_v2(
            website_url=login_page_url,
            website_key=captcha_info['site_key']
        )

    if not captcha_solution:
        send_message(
            'Error',
            f'Failed to solve captcha automatically. Please solve it manually at:\n'
            f'https://marangatu.set.gov.py/eset/login?login_error=2&usuario={config.username}'
        )
        return None

    print('Captcha solved! Retrying login...')

    # Retry login with captcha solution
    login_data['g-recaptcha-response'] = captcha_solution
    http.random_sleep()
    return http.post_login(f'{url_base}/authenticate', login_data)


def perform_login(http: HTTPClient, config: Config, url_base: str, url_host: str, send_message) -> bool:
    """
    Perform login and handle any errors or captchas.

    Args:
        http: HTTP client
        config: Configuration object
        url_base: Base URL for authentication
        url_host: Host URL
        send_message: Function to send notification messages

    Returns:
        True if login succeeded, False otherwise
    """
    print('Logging in...')
    http.random_sleep()

    login_data = {
        'usuario': config.username,
        'clave': config.password,
    }
    login_response = http.post_login(f'{url_base}/authenticate', login_data)

    # Check for errors
    if 'Usuario o Contraseña incorrectos' in login_response:
        send_message('Error', 'Incorrect login credentials')
        return False
    elif 'Código de Seguridad no es correcto' in login_response:
        # Captcha required
        captcha_response = attempt_captcha_solve(config, http, url_base, url_host, login_data, send_message)
        if captcha_response is None:
            return False

        # Check captcha response
        if 'Usuario o Contraseña incorrectos' in captcha_response:
            send_message('Error', 'Incorrect login credentials')
            return False
        elif 'Código de Seguridad no es correcto' in captcha_response:
            send_message('Error', 'Captcha solution failed. Please solve it manually.')
            return False
        else:
            print('Logged in successfully with captcha!')
            return True
    else:
        return True


def check_session(http: HTTPClient, config: Config, url_base: str, url_host: str, send_message) -> bool:
    """
    Check if already logged in, or perform login if needed.

    Args:
        http: HTTP client
        config: Configuration object
        url_base: Base URL
        url_host: Host URL
        send_message: Function to send notification messages

    Returns:
        True if logged in (or successfully logged in), False otherwise
    """
    print('Checking session...')
    home_page = http.get(url_base)

    if '/eset/logout' in home_page:
        print('Logged in')
        return True
    else:
        return perform_login(http, config, url_base, url_host, send_message)


def main() -> int:
    """Main entry point."""
    # Parse arguments and load config
    args = parse_args()
    config = load_config(args)

    # Validate credentials
    if not config.username or not config.password:
        print(
            'Please set login credentials in .env, .env.local, or as script arguments.\n'
            'See python file_taxes.py --help'
        )
        return 1

    # Initialize notifier
    notifier = get_notifier(
        service=config.notification_service,
        pushover_token=config.pushover_token,
        pushover_user=config.pushover_user,
        signal_user=config.signal_user,
        signal_recipient=config.signal_recipient,
        smtp_host=config.smtp_host,
        smtp_port=config.smtp_port,
        smtp_addr=config.smtp_addr,
        smtp_pwd=config.smtp_pwd,
        smtp_recv=config.smtp_recv,
    )

    def send_message(title: str, message: str) -> None:
        """Send notification with message prefix."""
        full_message = f'{config.message_prefix}{message}'
        notifier.send(title, full_message)
        print(f'{title} - {message}')

    # Initialize HTTP client
    http = HTTPClient(
        cookies_file=config.cookies_file,
        user_agents_file=config.user_agents_file,
        verify_ssl=config.verify_ssl,
        verbose=config.is_verbose,
        debug=config.is_debug,
    )

    # URLs
    URL_BASE = http.URL_BASE
    URL_HOST = http.URL_HOST
    METHOD_PROFILE = 'perfil/publico'
    METHOD_PENDING = 'perfil/vencimientos'
    METHOD_MENU = 'perfil/menu'
    METHOD_CHECK_PROFILE = 'perfil/informacionControlesPerfil'

    # Check session and login if needed
    if not check_session(http, config, URL_BASE, URL_HOST, send_message):
        return 1

    # Get profile
    token = encrypt('{}')
    import urllib.parse
    token_encoded = urllib.parse.quote(token)

    print('Fetching profile information...')
    http.random_sleep()
    profile_response = http.get(f'{URL_BASE}/{METHOD_PROFILE}?t3={token_encoded}')

    try:
        profile = json.loads(profile_response)
    except json.JSONDecodeError:
        send_message('Error', 'Could not parse profile data')
        return 1

    cedula = profile.get('rucActivo', '')
    dv = profile.get('dvActivo', '')
    name = profile.get('nombre', '')

    if not name:
        send_message('Error', 'Could not get user data')
        return 1

    # Extract first name for greeting
    name_parts = name.split()
    first_name = name_parts[1] if len(name_parts) > 1 else name_parts[0] if name_parts else 'User'
    print(f'Welcome {first_name}!')

    # Check profile info changes
    print('Checking profile info changes...')
    http.random_sleep()
    check_profile_response = http.get(f'{URL_BASE}/{METHOD_CHECK_PROFILE}?t3={token_encoded}')

    try:
        check_profile = json.loads(check_profile_response)
    except json.JSONDecodeError:
        check_profile = {}

    must_update = check_profile.get('debeActualizar', False)

    if must_update:
        # Import form handlers
        from forms import PROFILE_HANDLERS

        vinculos = check_profile.get('vinculos', [])
        for vinculo in vinculos:
            vinculo_name = vinculo.get('texto', '')
            vinculo_link = vinculo.get('url', '')

            # Convert name to handler key (e.g., "Registro de Contribuyentes" -> "registro_de_contribuyentes")
            name_safe = vinculo_name.lower().replace(' ', '_')

            print('================')
            print(f'Profile data {vinculo_name} must be updated')

            if name_safe in PROFILE_HANDLERS:
                handler_class = PROFILE_HANDLERS[name_safe]
                handler = handler_class(
                    http_client=http,
                    config=config,
                    notifier=notifier,
                    profile=profile,
                    menu=[]  # Menu not needed for profile updates
                )
                handler.process(vinculo_link)
            else:
                error = f'Profile data {vinculo_name} requested but not yet implemented. Please update it manually.'
                send_message('Error', error)
    else:
        print('No pending profile actions')

    # Check pending forms
    print('Checking pending forms...')
    http.random_sleep()
    pending_response = http.get(f'{URL_BASE}/{METHOD_PENDING}?t3={token_encoded}')

    try:
        pending_forms = json.loads(pending_response)
    except json.JSONDecodeError:
        pending_forms = []

    if pending_forms:
        # Get menu items
        print('Fetching menu items...')
        http.random_sleep()
        menu_response = http.get(f'{URL_BASE}/{METHOD_MENU}?t3={token_encoded}')

        try:
            menu = json.loads(menu_response)
        except json.JSONDecodeError:
            menu = []

        # Import form handlers
        from forms import FORM_HANDLERS

        current_period = get_current_period()

        for pending in pending_forms:
            tax = pending.get('impuesto', '')
            requested_period = pending.get('periodo', '')

            print('================')
            print(f'Tax form no. {tax} needs to be filed')

            if tax in FORM_HANDLERS:
                if requested_period == current_period:
                    handler_class = FORM_HANDLERS[tax]
                    handler = handler_class(
                        http_client=http,
                        config=config,
                        notifier=notifier,
                        profile=profile,
                        menu=menu
                    )
                    handler.process(requested_period)
                else:
                    print('Please wait for the next fiscal period (e.g. next month) to begin.')
            else:
                error = f'Tax form no. {tax} requested but not yet implemented. Please file it manually.'
                send_message('Error', error)
    else:
        print('No pending actions')

    return 0


if __name__ == '__main__':
    sys.exit(main())
