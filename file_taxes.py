#!/usr/bin/env python3
"""
Automatically file taxes in Paraguay.

This script interacts with Paraguay's official tax portal (marangatu.set.gov.py)
to file VAT forms (Form 211), receipt summary forms (Form 955), and update
profile information.
"""

import base64
import json
import sys
from datetime import datetime
from typing import Any, Dict, List, Optional

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
    METHOD_AUTH = 'authenticate'
    METHOD_PROFILE = 'perfil/publico'
    METHOD_PENDING = 'perfil/vencimientos'
    METHOD_MENU = 'perfil/menu'
    METHOD_CHECK_PROFILE = 'perfil/informacionControlesPerfil'

    # Check session
    print('Checking session...')
    home_page = http.get(URL_BASE)

    if '/eset/logout' in home_page:
        print('Logged in')
    else:
        print('Logging in...')
        http.random_sleep()

        login_data = {
            'usuario': config.username,
            'clave': config.password,
        }
        login_response = http.post_login(f'{URL_BASE}/{METHOD_AUTH}', login_data)

        if 'Usuario o Contraseña incorrectos' in login_response:
            send_message('Error', 'Incorrect login credentials')
            return 1
        elif 'Código de Seguridad no es correcto' in login_response:
            send_message(
                'Error',
                f'Login on the website and fill out a captcha first '
                f'https://marangatu.set.gov.py/eset/login?login_error=2&usuario={config.username}'
            )
            return 1
        else:
            print('Logged in')

    # Get profile
    token = encrypt('{}')
    import urllib.parse
    token_encoded = urllib.parse.quote(token)

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
