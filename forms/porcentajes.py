"""Income percentages by activity update handler."""

import json
import re
from datetime import datetime
from typing import Any, Dict

from forms.base import FormHandler


class PorcentajesHandler(FormHandler):
    """Handler for income percentages (porcentajes_actividades) updates."""

    METHOD_VERIFICATION = 'actualizacion/verificar'
    METHOD_RECOVER = 'actualizacion/recuperar'
    METHOD_SAVE = 'actualizacion/guardar?'
    METHOD_ACCEPT_DOCUMENT = 'ru/documento/archivos/aceptarDocumento'

    def process(self, link: str) -> bool:
        """
        Process income percentages update.

        Args:
            link: The URL link to the update form

        Returns:
            True if successful, False otherwise
        """
        print('Retrieving taxpayer data...')
        self.http.random_sleep()
        taxpayer_page = self.http.get(f'{self.url_host}{link}')

        if not self.contains_text(taxpayer_page, 'Porcentajes de Ingreso por Actividades Económicas'):
            self.send_message('Error', 'No profile available')
            return False

        # Recover existing data
        recover_data = {'ruc': self.cedula, 'categoria': 'PORCENTAJES_ACTIVIDAD'}
        token_recover = self.encrypt_token(recover_data)

        print('Retrieving form data...')
        self.http.random_sleep()
        recover_response = self.http.get(f'{self.url_base}/{self.METHOD_RECOVER}?t3={token_recover}')

        try:
            recover = json.loads(recover_response)
        except json.JSONDecodeError:
            self.send_message('Error', 'Invalid response when recovering data')
            return False

        # Extract general data
        general = recover.get('generales', {})

        # Current date
        now = datetime.now()
        current_date = now.strftime('%d/%m/%Y')
        year = now.strftime('%Y')

        # Build data dictionary
        captura = {
            'formaJuridica': 'FISICO',
            'ruc': self.cedula,
            'categoria': 'PORCENTAJES_ACTIVIDAD',
            'generalesFechaSolicitud': current_date,
            'generalesTipoInscripcion': 'SOLICITADA',
            'operacionesFechaInicio': general.get('operacionesFechaInicio', ''),
            'operacionesMesCierreHistorico': general.get('operacionesMesCierreHistorico'),
            'nombreCompleto': general.get('nombreCompleto', ''),
            'generalesNombreCompleto': general.get('generalesNombreCompleto', ''),
            'edicionPorcentajes': general.get('edicionPorcentajes', ''),
            'generalesPorcentajesActividadesAnho': year,
            'generalesPorcentajesActividadesAnho_': year,
            # Empty phone fields
            'domicilioTelefono01': '',
            'domicilioTelefono02': '',
            'domicilioCelular01': '',
            'domicilioCelular02': '',
            # Default activity percentage - this should ideally come from the recovered data
            # but the Bash version has it hardcoded
            'porcentajeActividadNombre.1': '96099 - OTRAS ACTIVIDADES DE SERVICIOS PERSONALES N.C.P.',
            'porcentajeActividad.1': 'C4_96099',
            'porcentajeActividadValor.1': 100,
        }

        save_data = {
            'ruc': self.cedula,
            'categoria': 'PORCENTAJES_ACTIVIDAD',
            'captura': captura
        }

        # Note: The Bash version has a commented-out verification step
        # Uncomment and implement if needed:
        # print('Verifying data...')
        # self.http.random_sleep()
        # verify_response = self.http.post_json(f'{self.url_base}/{self.METHOD_VERIFICATION}', save_data)
        # if verify_response.strip() != '[]':
        #     self.send_message('Error', verify_response)
        #     return False

        # Save data
        print('Saving percentage data...')
        self.http.random_sleep()
        save_response = self.http.post_json(f'{self.url_base}/{self.METHOD_SAVE}', save_data)

        try:
            save_result = json.loads(save_response)
        except json.JSONDecodeError:
            self.send_message('Error', 'Invalid response when saving data')
            return False

        if save_result.get('exito') is False:
            error = ''
            try:
                errors = save_result.get('operacion', {}).get('errores', [])
                if errors:
                    error = errors[0].get('descripcion', '')
            except (KeyError, IndexError, TypeError):
                pass
            self.send_message('Error', error or 'Unknown error saving data')
            return False

        # Follow redirect to document
        print('Redirecting to document...')
        redirect_url = save_result.get('url', '')
        redirect_page = self.http.get(f'{self.url_base}/{redirect_url}')

        if not self.contains_text(redirect_page, 'Enviar Solicitud'):
            self.send_message('Error', "Can't update percentages")
            return False

        # Extract document ID from ng-init
        ng_init = self.extract_div_ng_init(redirect_page, 'DocumentoArchivosController')
        if not ng_init:
            self.send_message('Error', 'Could not find document controller')
            return False

        # Parse document string - format: vm.init('ID,...', ...)
        match = re.search(r"'([^']+)'", ng_init)
        if not match:
            self.send_message('Error', 'Could not parse document ID')
            return False

        document_string = match.group(1)
        # Remove trailing comma if present
        document_id = document_string.rstrip(',')

        # Accept document
        print('Confirming document...')
        self.http.random_sleep()
        accept_data = {'id': document_id}
        accept_response = self.http.post_json(
            f'{self.url_base}/{self.METHOD_ACCEPT_DOCUMENT}',
            accept_data
        )

        try:
            accept_result = json.loads(accept_response)
            # Follow final redirect
            final_url = accept_result.get('url', '')
            if final_url:
                self.http.get(f'{self.url_base}/{final_url}')
        except json.JSONDecodeError:
            pass  # Continue anyway

        self.send_message('Success!', 'Info on the percentage of income from economic activity updated successfully!')
        return True
