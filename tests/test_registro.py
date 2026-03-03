"""Tests for RegistroHandler - Taxpayer registration profile updates."""

import json
from unittest.mock import MagicMock

import pytest

from forms.registro import RegistroHandler


class TestRegistroHandler:
    """Test suite for RegistroHandler."""

    def test_registro_process_success(
        self,
        test_config,
        test_http_client,
        test_profile,
        test_notifier_mock,
        mockup_menu_page_html,
        mockup_recovery_response,
        mockup_form_submission_response
    ):
        """Test successful taxpayer registration update."""
        # Make menu page contain expected text for Registro
        registro_page = mockup_menu_page_html.replace(
            'Presentar Declaración',
            'Actualización de Contribuyente'
        )

        call_count = {'count': 0}
        redirect_page = (
            '<html><body>Enviar Solicitud'
            '<div data-ng-controller="DocumentoArchivosController" '
            'data-ng-init="vm.init(\'12345,\', {})"></div>'
            '</body></html>'
        )

        def mock_get(url):
            call_count['count'] += 1
            if 'actualizacion' in url and call_count['count'] == 1:
                return registro_page
            if '/eset/ru/documento/archivos/finalizado' in url:
                return '<html><body>Documento finalizado</body></html>'
            if '/eset/ru/documento/archivos/' in url:
                return redirect_page
            else:
                return json.dumps(mockup_recovery_response)

        def mock_post_json(url, data):
            if 'verificarPaso' in url or 'actualizacion/verificar' in url:
                return '[]'
            if 'aceptarDocumento' in url:
                return json.dumps({'url': '/eset/ru/documento/archivos/finalizado'})
            return json.dumps({
                **mockup_form_submission_response,
                'url': '/eset/ru/documento/archivos/'
            })

        test_http_client.get = mock_get
        test_http_client.post_json = mock_post_json

        handler = RegistroHandler(
            http_client=test_http_client,
            config=test_config,
            notifier=test_notifier_mock,
            profile=test_profile,
            menu=[]
        )

        result = handler.process('/eset/actualizacion/editar_contribuyente.do')

        assert result is True, 'RegistroHandler should return True on success'

    def test_registro_page_validation_fails(
        self,
        test_config,
        test_http_client,
        test_profile,
        test_notifier_mock
    ):
        """Test Registro when page validation fails."""
        def mock_get(url):
            return '<html><body>Wrong page</body></html>'

        test_http_client.get = mock_get

        handler = RegistroHandler(
            http_client=test_http_client,
            config=test_config,
            notifier=test_notifier_mock,
            profile=test_profile,
            menu=[]
        )

        result = handler.process('/eset/actualizacion/editar_contribuyente.do')

        assert result is False, 'Should return False when page validation fails'

    def test_registro_recovery_invalid_json(
        self,
        test_config,
        test_http_client,
        test_profile,
        test_notifier_mock,
        mockup_menu_page_html
    ):
        """Test Registro with invalid JSON in recovery response."""
        registro_page = mockup_menu_page_html.replace(
            'Presentar Declaración',
            'Actualización de Contribuyente'
        )

        call_count = {'count': 0}

        def mock_get(url):
            call_count['count'] += 1
            if call_count['count'] == 1:
                return registro_page
            else:
                return 'invalid json response'

        test_http_client.get = mock_get

        handler = RegistroHandler(
            http_client=test_http_client,
            config=test_config,
            notifier=test_notifier_mock,
            profile=test_profile,
            menu=[]
        )

        result = handler.process('/eset/actualizacion/editar_contribuyente.do')

        assert result is False, 'Should return False on invalid recovery JSON'

    def test_registro_submission_failure(
        self,
        test_config,
        test_http_client,
        test_profile,
        test_notifier_mock,
        mockup_menu_page_html,
        mockup_recovery_response
    ):
        """Test Registro submission failure."""
        error_response = {
            'exito': False,
            'operacion': {
                'errores': [
                    {'descripcion': 'Required fields missing'}
                ]
            }
        }

        registro_page = mockup_menu_page_html.replace(
            'Presentar Declaración',
            'Actualización de Contribuyente'
        )

        call_count = {'count': 0}

        def mock_get(url):
            call_count['count'] += 1
            if call_count['count'] == 1:
                return registro_page
            else:
                return json.dumps(mockup_recovery_response)

        def mock_post_json(url, data):
            if 'verificarPaso' in url or 'actualizacion/verificar' in url:
                return '[]'
            return json.dumps(error_response)

        test_http_client.get = mock_get
        test_http_client.post_json = mock_post_json

        handler = RegistroHandler(
            http_client=test_http_client,
            config=test_config,
            notifier=test_notifier_mock,
            profile=test_profile,
            menu=[]
        )

        result = handler.process('/eset/actualizacion/editar_contribuyente.do')

        assert result is False, 'Should return False on submission failure'

    def test_registro_recovery_data_structure(
        self,
        test_config,
        test_http_client,
        test_profile,
        test_notifier_mock,
        mockup_menu_page_html,
        mockup_form_submission_response
    ):
        """Test Registro correctly extracts and uses recovery data."""
        recovery_data = {
            'generales': {
                'ruc': '8765432',
                'razonSocial': 'Test Business Name',
                'primeroApellido': 'TestApellido1',
                'segundoApellido': 'TestApellido2'
            },
            'domicilio': {
                'pais': 'Paraguay'
            }
        }

        registro_page = mockup_menu_page_html.replace(
            'Presentar Declaración',
            'Actualización de Contribuyente'
        )

        submitted_data = None
        redirect_page = (
            '<html><body>Enviar Solicitud'
            '<div data-ng-controller="DocumentoArchivosController" '
            'data-ng-init="vm.init(\'12345,\', {})"></div>'
            '</body></html>'
        )

        def mock_get(url):
            if 'actualizacion/editar' in url:
                return registro_page
            if 'actualizacion/recuperar' in url:
                return json.dumps(recovery_data)
            if '/eset/ru/documento/archivos/' in url:
                return redirect_page
            return '<html><body>Documento finalizado</body></html>'

        def mock_post_json(url, data):
            nonlocal submitted_data
            if 'actualizacion/guardar' in url:
                submitted_data = data
                return json.dumps({
                    **mockup_form_submission_response,
                    'url': '/eset/ru/documento/archivos/'
                })
            if 'verificarPaso' in url or 'actualizacion/verificar' in url:
                return '[]'
            return json.dumps({'url': '/eset/ru/documento/archivos/finalizado'})

        test_http_client.get = mock_get
        test_http_client.post_json = mock_post_json

        handler = RegistroHandler(
            http_client=test_http_client,
            config=test_config,
            notifier=test_notifier_mock,
            profile=test_profile,
            menu=[]
        )

        result = handler.process('/eset/actualizacion/editar_contribuyente.do')

        assert result is True
        assert submitted_data is not None, 'Form data should be submitted'
