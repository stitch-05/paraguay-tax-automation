"""Form 211 - VAT (IVA) form handler."""

import json
import re
from typing import Any, Dict, List

from forms.base import FormHandler
from utils import AnimatedWaitContext


class Form211Handler(FormHandler):
    """Handler for VAT form (Form 211) filing."""

    METHOD_PERMITE = 'declaracion/permite'
    METHOD_PRESENTAR = 'presentar'
    FORM_AFFIDAVIT = 'SG00005'
    TAX = '211'
    FORM = '120'

    def process(self, period_or_link: str) -> bool:
        """
        Process VAT form 211.

        Args:
            period_or_link: The fiscal period in YYYYMM format

        Returns:
            True if successful, False otherwise
        """
        period = period_or_link
        with AnimatedWaitContext('Preparing tax form', self.config.is_verbose):
            # Get taxpayer menu URL
            taxpayer_url = self.get_menu_url(self.FORM_AFFIDAVIT)
            if not taxpayer_url:
                self.send_message('Error', 'Tax payer menu not found')
                return False

            taxpayer_page = self.http.get(f'{self.url_base}/{taxpayer_url}')

        if not self.contains_text(taxpayer_page, 'Presentar Declaración'):
            self.send_message('Error', 'Tax payer not found')
            return False

        # Get permission to create form
        with AnimatedWaitContext('Retrieving tax form', self.config.is_verbose):
            permit_data = {
                'ruc': self.cedula,
                'dv': self.dv,
                'periodo': period,
                'impuesto': self.TAX,
                'formulario': self.FORM,
                'fechaDiferida': None
            }
            token_permit = self.encrypt_token(permit_data)
            permit_response = self.http.get(f'{self.url_base}/{self.METHOD_PERMITE}?t3={token_permit}')

            try:
                permit = json.loads(permit_response)
            except json.JSONDecodeError:
                self.send_message('Error', 'Invalid response when checking form permission')
                return False

            if not permit.get('permite'):
                self.send_message('Error', 'Tax form could not be retrieved')
                return False

            # Load declaration form
            permit_url = permit.get('url', '')
            declaration_form = self.http.get(f'{self.url_host}{permit_url}')

        # Parse input fields from HTML
        inputs = self.parse_inputs(declaration_form)

        # Extract form token (_cyp) from URL
        cyp_match = re.search(r'[?&]_cyp=([^&]+)', permit_url)
        cyp = cyp_match.group(1) if cyp_match else ''

        # Build form data from inputs
        form_data: Dict[str, Any] = {'_cyp': cyp}

        with AnimatedWaitContext('Please wait! Processing tax form data', self.config.is_verbose):
            for inp in inputs:
                name = inp.get('name', '')
                value = inp.get('value', '')

                # Extract name from dynamicProps() wrapper if present
                match = re.match(r'dynamicProps\(([^)]+)\)', name)
                if match:
                    name = match.group(1)

                if not name:
                    continue

                # Skip certain fields
                if name in ('C2', 'C3'):
                    continue

                # Handle special cases
                if name == 'segundoApellido' and not value:
                    value = ''
                elif name == 'fechaDiferida':
                    value = ''
                elif name == 'exportador':
                    value = '0'
                elif not value:
                    value = '0'

                # Only add non-empty values
                if value != 'null' and value:
                    form_data[name] = value

        # Submit the form
        with AnimatedWaitContext('Sending tax form', self.config.is_verbose):
            # Remove spaces from JSON (matching Bash behavior)
            json_data = json.dumps(form_data, separators=(',', ':'))
            final_response = self.http.post_json(f'{self.url_base}/{self.METHOD_PRESENTAR}', json_data)

            try:
                final = json.loads(final_response)
            except json.JSONDecodeError:
                self.send_message('Error', 'Invalid response when filing VAT')
                return False

            status = final.get('exito')

        if not status:
            error = ''
            try:
                errors = final.get('operacion', {}).get('errores', [])
                if errors:
                    error = errors[0].get('descripcion', '')
            except (KeyError, IndexError, TypeError):
                pass

            if not error:
                error = 'No response received when filing VAT. Try again later.'

            self.send_message('Error', error)
            return False

        self.send_message('Success!', 'VAT filed successfully!')
        return True
