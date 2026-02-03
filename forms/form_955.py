"""Form 955 - Receipt management form handler."""

import json
from typing import Any, Dict

from forms.base import FormHandler


class Form955Handler(FormHandler):
    """Handler for receipt management form (Form 955) filing."""

    METHOD_TALON = 'gdi/di/talonresumen/procesarTalon'
    METHOD_OPERATIONS = 'gdi/di/gestion/listarTiposOperaciones'
    FORM_AFFIDAVIT = 'DI03100'
    FORM = '241'
    RECEIPT_MANAGEMENT_ID = '6'

    def process(self, period: str) -> bool:
        """
        Process receipt management form 955.

        Args:
            period: The fiscal period in YYYYMM format

        Returns:
            True if successful, False otherwise
        """
        print('Preparing receipt management...')

        # Get receipt management menu URL
        receipt_url = self.get_menu_url(self.FORM_AFFIDAVIT)
        if not receipt_url:
            self.send_message('Error', 'Receipt management menu not found')
            return False

        self.http.random_sleep()
        receipt_page = self.http.get(f'{self.url_base}/{receipt_url}')

        if not self.contains_text(receipt_page, 'Gestión de Comprobantes'):
            self.send_message('Error', 'Not able to manage receipts')
            return False

        # Get operations list
        print('Getting access to receipt forms...')

        operations_data = {'ruc': self.cedula}
        token_operations = self.encrypt_token(operations_data)

        self.http.random_sleep()
        operations_response = self.http.get(
            f'{self.url_base}/{self.METHOD_OPERATIONS}?t3={token_operations}'
        )

        try:
            operations = json.loads(operations_response)
        except json.JSONDecodeError:
            self.send_message('Error', 'Invalid response when getting operations')
            return False

        # Find confirm URL for receipt management
        confirm_url = None
        for op in operations:
            if op.get('id') == self.RECEIPT_MANAGEMENT_ID:
                confirm_url = op.get('url')
                break

        if not confirm_url:
            self.send_message('Error', 'No access to receipt forms')
            return False

        # Load receipt forms page
        print('Retrieving receipt forms...')

        self.http.random_sleep()
        receipt_forms = self.http.get(f'{self.url_base}/{confirm_url}')

        if not self.contains_text(receipt_forms, 'Registro de Comprobantes - Presentación de Talón'):
            self.send_message('Error', 'No receipt forms available')
            return False

        # Submit the talon
        print(f'Sending tax form {self.FORM}...')

        talon_data = {
            'periodo': int(period),
            'formulario': int(self.FORM)
        }
        token_talon = self.encrypt_token(talon_data)

        self.http.random_sleep()
        process_response = self.http.post_json(
            f'{self.url_base}/{self.METHOD_TALON}?t3={token_talon}',
            {}
        )

        try:
            result = json.loads(process_response)
        except json.JSONDecodeError:
            self.send_message('Error', f'Filing receipt form {self.FORM}')
            return False

        status = result.get('exito')

        if status is None:
            self.send_message('Error', f'Filing receipt form {self.FORM}')
            return False

        self.send_message('Success!', f'Receipts for period {period} filed successfully!')
        return True
