"""Taxpayer registration update handler."""

import json
import re
from datetime import datetime
from typing import Any, Dict

from forms.base import FormHandler


class RegistroHandler(FormHandler):
    """Handler for taxpayer registration (registro_de_contribuyentes) updates."""

    METHOD_VERIFICATION = 'actualizacion/verificar'
    METHOD_RECOVER = 'actualizacion/recuperar'
    METHOD_CHECK_STEP = 'actualizacion/verificarPaso'
    METHOD_SAVE = 'actualizacion/guardar?'
    METHOD_ACCEPT_DOCUMENT = 'ru/documento/archivos/aceptarDocumento'

    def process(self, link: str) -> bool:
        """
        Process taxpayer registration update.

        Args:
            link: The URL link to the update form

        Returns:
            True if successful, False otherwise
        """
        print('Retrieving taxpayer data...')
        self.http.random_sleep()
        taxpayer_page = self.http.get(f'{self.url_host}{link}')

        if not self.contains_text(taxpayer_page, 'Actualización de Contribuyente'):
            self.send_message('Error', 'No profile available')
            return False

        # Recover existing data
        recover_data = {'ruc': self.cedula, 'categoria': 'EDICION'}
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
        domicil = recover.get('domicilio', {})

        # Current date
        now = datetime.now()
        current_date = now.strftime('%d/%m/%Y')
        year = now.strftime('%Y')

        # Build sub_data dictionary
        sub_data = {
            'formaJuridica': 'FISICO',
            'ruc': self.cedula,
            'categoria': 'EDICION',
            'generalesFormaJuridica': 'FISICO',
            'generalesFechaSolicitud': current_date,
            'generalesTipoInscripcion': 'SOLICITADA',
            'categoriaContribuyente': 'PEQUENO',
            'generalesTipoDocumento': general.get('generalesTipoDocumento', ''),
            'operacionesMesCierreVigente': general.get('operacionesMesCierreHistorico'),
            'nombreCompleto': general.get('nombreCompleto', ''),
            'generalesPaisDocumento': 'PY',
            'operacionesMesCierre': general.get('operacionesMesCierreHistorico'),
            'ley285': general.get('ley285', ''),
            'generalesPaisDocumento_': 'Paraguay',
            'generalesDv': self.dv,
            'generalesNumeroDocumento': self.cedula,
            'declaraInternet': general.get('declaraInternet', ''),
            'operacionesImportador': general.get('operacionesImportador', ''),
            'generalesNombres': general.get('generalesNombres', ''),
            'generalesCorreo01': general.get('generalesCorreo01', ''),
            'operacionesFechaInicio': general.get('operacionesFechaInicio', ''),
            'operacionesExportador': general.get('operacionesExportador', ''),
            'tipoInscripcion': 'SOLICITADA',
            'generalesApellido01': general.get('generalesApellido01', ''),
            'operacionesFuncionarios': general.get('operacionesFuncionarios'),
            'generalesEstado': general.get('generalesEstado', ''),
            'generalesRuc': self.cedula,
            'generalesRegionalTexto': general.get('generalesRegionalTexto', ''),
            'fechaInicioActividad': general.get('operacionesFechaInicio', ''),
            'generalesRegional': general.get('generalesRegional'),
            'generalesTipoDocumento_': general.get('generalesTipoDocumento', ''),
            'operacionesMesCierre_': 'DICIEMBRE',
            'generalesCiudadanoActualizado': general.get('generalesCiudadanoActualizado', ''),
            'operacionesMesCierreHistorico': general.get('operacionesMesCierreHistorico'),
            'generalesNombreCompleto': general.get('generalesNombreCompleto', ''),
            'generalesFechaNacimiento': general.get('generalesFechaNacimiento', ''),
            # Domicilio fields
            'domicilioTipoVia': domicil.get('domicilioTipoVia', ''),
            'domicilioCelular01Sufijo': domicil.get('domicilioCelular01Sufijo', ''),
            'domicilioReferencias': domicil.get('domicilioReferencias', ''),
            'domicilioCelular01Prefijo': domicil.get('domicilioCelular01Prefijo', ''),
            'domicilioCelular01': f"({domicil.get('domicilioCelular01Prefijo', '')}){domicil.get('domicilioCelular01Sufijo', '')}",
            'domicilioDistrito_': domicil.get('domicilioDistrito_', ''),
            'domicilioLatitud': domicil.get('domicilioLatitud', ''),
            'domicilioDepartamento_': domicil.get('domicilioDepartamento_', ''),
            'domicilioBarrio_': domicil.get('domicilioBarrio_', ''),
            'domicilioTipoVia_': domicil.get('domicilioTipoVia', ''),
            'domicilioNombreVia': domicil.get('domicilioNombreVia', ''),
            'domicilioTipoInmueble': domicil.get('domicilioTipoInmueble', ''),
            'domicilioNumeroPuerta': domicil.get('domicilioNumeroPuerta', ''),
            'domicilioTipoInmueble_': domicil.get('domicilioTipoInmueble', ''),
            'domicilioLongitud': domicil.get('domicilioLongitud', ''),
            'domicilioLocalidad': domicil.get('domicilioLocalidad'),
            'domicilioLocalidad_': domicil.get('domicilioDistrito_', ''),
            'domicilioDepartamento': 1,
            'domicilioBarrio': domicil.get('domicilioBarrio'),
            'domicilioDistrito': domicil.get('domicilioLocalidad'),
        }

        # Check step
        check_data = {
            'ruc': self.cedula,
            'categoria': 'EDICION',
            'paso': 'generales',
            'captura': sub_data
        }

        print('Checking step...')
        self.http.random_sleep()
        check_response = self.http.post_json(f'{self.url_base}/{self.METHOD_CHECK_STEP}', check_data)

        if check_response.strip() != '[]':
            self.send_message('Error', check_response)
            return False

        # Add additional fields for verification
        sub_data.update({
            'domicilioTelefono02Prefijo': '',
            'domicilioCelular02Prefijo': '',
            'domicilioCelular02': '',
            'domicilioTelefono02': '',
            'domicilioCelular02Sufijo': '',
            'domicilioTelefono02Sufijo': '',
            'domicilioFechaModificacion': current_date,
            'edicionDomicilio': 'S',
            'domicilioLat': domicil.get('domicilioLatitud'),
            'domicilioLng': domicil.get('domicilioLongitud'),
        })

        verify_data = {
            'ruc': self.cedula,
            'categoria': 'EDICION',
            'captura': sub_data
        }

        print('Verifying data...')
        self.http.random_sleep()
        verify_response = self.http.post_json(f'{self.url_base}/{self.METHOD_VERIFICATION}', verify_data)

        if verify_response.strip() != '[]':
            self.send_message('Error', verify_response)
            return False

        # Save data
        print('Saving tax payer data...')
        self.http.random_sleep()
        save_response = self.http.post_json(f'{self.url_base}/{self.METHOD_SAVE}', verify_data)

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
        except json.JSONDecodeError:
            pass  # Continue anyway

        # Follow final redirect
        final_url = accept_result.get('url', '') if 'accept_result' in dir() else ''
        if final_url:
            self.http.get(f'{self.url_base}/{final_url}')

        self.send_message('Success!', 'Tax payer info updated successfully!')
        return True
