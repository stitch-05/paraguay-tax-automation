"""Tests for PorcentajesHandler - Activity income percentages profile updates."""

import json
from unittest.mock import MagicMock

import pytest

from forms.porcentajes import PorcentajesHandler


class TestPorcentajesHandler:
    """Test suite for PorcentajesHandler."""

    def test_porcentajes_process_success(
        self,
        test_config,
        test_http_client,
        test_profile,
        test_notifier_mock,
        mockup_menu_page_html,
        mockup_recovery_response,
        mockup_form_submission_response
    ):
        """Test successful income percentages update."""
        # Make menu page contain expected text for Porcentajes
        porcentajes_page = mockup_menu_page_html.replace(
            'Presentar Declaración',
            'Porcentajes de Ingreso por Actividades Económicas'
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
                return porcentajes_page
            if '/eset/ru/documento/archivos/finalizado' in url:
                return '<html><body>Documento finalizado</body></html>'
            if '/eset/ru/documento/archivos/' in url:
                return redirect_page
            else:
                return json.dumps(mockup_recovery_response)

        def mock_post_json(url, data):
            if 'aceptarDocumento' in url:
                return json.dumps({'url': '/eset/ru/documento/archivos/finalizado'})
            return json.dumps({
                **mockup_form_submission_response,
                'url': '/eset/ru/documento/archivos/'
            })

        test_http_client.get = mock_get
        test_http_client.post_json = mock_post_json

        handler = PorcentajesHandler(
            http_client=test_http_client,
            config=test_config,
            notifier=test_notifier_mock,
            profile=test_profile,
            menu=[]
        )

        result = handler.process('/eset/actualizacion/porcentajes.do')

        assert result is True, 'PorcentajesHandler should return True on success'

    def test_porcentajes_page_validation_fails(
        self,
        test_config,
        test_http_client,
        test_profile,
        test_notifier_mock
    ):
        """Test Porcentajes when page validation fails."""
        def mock_get(url):
            return '<html><body>Wrong page</body></html>'

        test_http_client.get = mock_get

        handler = PorcentajesHandler(
            http_client=test_http_client,
            config=test_config,
            notifier=test_notifier_mock,
            profile=test_profile,
            menu=[]
        )

        result = handler.process('/eset/actualizacion/porcentajes.do')

        assert result is False, 'Should return False when page validation fails'

    def test_porcentajes_recovery_invalid_json(
        self,
        test_config,
        test_http_client,
        test_profile,
        test_notifier_mock,
        mockup_menu_page_html
    ):
        """Test Porcentajes with invalid JSON in recovery response."""
        porcentajes_page = mockup_menu_page_html.replace(
            'Presentar Declaración',
            'Porcentajes de Ingreso por Actividades Económicas'
        )

        call_count = {'count': 0}

        def mock_get(url):
            call_count['count'] += 1
            if call_count['count'] == 1:
                return porcentajes_page
            else:
                return 'not valid json'

        test_http_client.get = mock_get

        handler = PorcentajesHandler(
            http_client=test_http_client,
            config=test_config,
            notifier=test_notifier_mock,
            profile=test_profile,
            menu=[]
        )

        result = handler.process('/eset/actualizacion/porcentajes.do')

        assert result is False, 'Should return False on invalid recovery JSON'

    def test_porcentajes_submission_failure(
        self,
        test_config,
        test_http_client,
        test_profile,
        test_notifier_mock,
        mockup_menu_page_html,
        mockup_recovery_response
    ):
        """Test Porcentajes submission failure."""
        error_response = {
            'exito': False,
            'operacion': {
                'errores': [
                    {'descripcion': 'Income percentages must total 100%'}
                ]
            }
        }

        porcentajes_page = mockup_menu_page_html.replace(
            'Presentar Declaración',
            'Porcentajes de Ingreso por Actividades Económicas'
        )

        call_count = {'count': 0}

        def mock_get(url):
            call_count['count'] += 1
            if call_count['count'] == 1:
                return porcentajes_page
            else:
                return json.dumps(mockup_recovery_response)

        def mock_post_json(url, data):
            return json.dumps(error_response)

        test_http_client.get = mock_get
        test_http_client.post_json = mock_post_json

        handler = PorcentajesHandler(
            http_client=test_http_client,
            config=test_config,
            notifier=test_notifier_mock,
            profile=test_profile,
            menu=[]
        )

        result = handler.process('/eset/actualizacion/porcentajes.do')

        assert result is False, 'Should return False on submission failure'

    def test_porcentajes_recovery_data_parsing(
        self,
        test_config,
        test_http_client,
        test_profile,
        test_notifier_mock,
        mockup_menu_page_html,
        mockup_form_submission_response
    ):
        """Test Porcentajes correctly parses recovery data with activities."""
        recovery_data = {
            'generales': {
                'ruc': '8765432'
            },
            'porcentajePorActividad': [
                {'actividad': 'Servicio A', 'porcentaje': 50},
                {'actividad': 'Servicio B', 'porcentaje': 50}
            ]
        }

        porcentajes_page = mockup_menu_page_html.replace(
            'Presentar Declaración',
            'Porcentajes de Ingreso por Actividades Económicas'
        )

        submitted_data = None
        redirect_page = (
            '<html><body>Enviar Solicitud'
            '<div data-ng-controller="DocumentoArchivosController" '
            'data-ng-init="vm.init(\'12345,\', {})"></div>'
            '</body></html>'
        )

        def mock_get(url):
            if 'actualizacion/porcentajes' in url:
                return porcentajes_page
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
            return json.dumps({'url': '/eset/ru/documento/archivos/finalizado'})

        test_http_client.get = mock_get
        test_http_client.post_json = mock_post_json

        handler = PorcentajesHandler(
            http_client=test_http_client,
            config=test_config,
            notifier=test_notifier_mock,
            profile=test_profile,
            menu=[]
        )

        result = handler.process('/eset/actualizacion/porcentajes.do')

        assert result is True
        assert submitted_data is not None, 'Form data should be submitted'

    def test_porcentajes_encryption_token_generation(
        self,
        test_config,
        test_http_client,
        test_profile,
        test_notifier_mock,
        mockup_menu_page_html,
        mockup_recovery_response,
        mockup_form_submission_response
    ):
        """Test Porcentajes correctly generates encryption tokens."""
        porcentajes_page = mockup_menu_page_html.replace(
            'Presentar Declaración',
            'Porcentajes de Ingreso por Actividades Económicas'
        )

        # Track what was requested
        requested_urls = []
        redirect_page = (
            '<html><body>Enviar Solicitud'
            '<div data-ng-controller="DocumentoArchivosController" '
            'data-ng-init="vm.init(\'12345,\', {})"></div>'
            '</body></html>'
        )

        def mock_get(url):
            requested_urls.append(url)
            if 'actualizacion/porcentajes' in url:
                return porcentajes_page
            if 'actualizacion/recuperar' in url:
                return json.dumps(mockup_recovery_response)
            if '/eset/ru/documento/archivos/' in url:
                return redirect_page
            else:
                return '<html><body>Documento finalizado</body></html>'

        def mock_post_json(url, data):
            requested_urls.append(url)
            if 'aceptarDocumento' in url:
                return json.dumps({'url': '/eset/ru/documento/archivos/finalizado'})
            return json.dumps({
                **mockup_form_submission_response,
                'url': '/eset/ru/documento/archivos/'
            })

        test_http_client.get = mock_get
        test_http_client.post_json = mock_post_json

        handler = PorcentajesHandler(
            http_client=test_http_client,
            config=test_config,
            notifier=test_notifier_mock,
            profile=test_profile,
            menu=[]
        )

        result = handler.process('/eset/actualizacion/porcentajes.do')

        assert result is True
        # Verify requests were made with encryption tokens
        # Requests to actualizacion/recuperar and actualizacion/guardar should have t3 param
        recovery_requests = [u for u in requested_urls if 'actualizacion/recuperar' in u]
        assert len(recovery_requests) > 0, 'Should make request to recovery endpoint'
        assert any('t3=' in u for u in recovery_requests), \
            'Recovery request should include encrypted token (t3 parameter)'
