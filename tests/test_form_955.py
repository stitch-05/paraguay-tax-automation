"""Tests for Form955Handler - Receipt management form filing."""

import json

from forms.form_955 import Form955Handler


class TestForm955Handler:
    """Test suite for Form955Handler."""

    @staticmethod
    def _build_handler(test_http_client, test_config, test_notifier_mock, test_profile, menu):
        return Form955Handler(
            http_client=test_http_client,
            config=test_config,
            notifier=test_notifier_mock,
            profile=test_profile,
            menu=menu,
        )

    def test_form955_process_success_uses_expected_endpoints(
        self,
        test_config,
        test_http_client,
        test_profile,
        test_notifier_mock,
        mockup_menu_page_html,
        mockup_talon_response,
    ):
        """Test successful receipt management form 955 filing and URL flow."""
        operations_response = [
            {
                'id': '6',
                'nombre': 'Confirmar Presentación',
                'url': 'gdi/presentacionTalonResumen.do?_cyp=test_token_123',
            }
        ]
        requested_urls = []

        def mock_get(url):
            requested_urls.append(url)
            if url.endswith('/eset/gdi/index.do'):
                return mockup_menu_page_html
            if '/gdi/di/gestion/listarTiposOperaciones?t3=' in url:
                return json.dumps(operations_response)
            if '/eset/gdi/presentacionTalonResumen.do?_cyp=test_token_123' in url:
                return '<html><body>Registro de Comprobantes - Presentación de Talón</body></html>'
            if '/gdi/di/talonresumen/procesarTalon?t3=' in url:
                return json.dumps(mockup_talon_response)
            raise AssertionError(f'Unexpected URL requested: {url}')

        test_http_client.get = mock_get
        menu_with_receipt = [{'aplicacion': 'DI03100', 'url': '/eset/gdi/index.do'}]
        handler = self._build_handler(
            test_http_client, test_config, test_notifier_mock, test_profile, menu_with_receipt
        )

        result = handler.process('202401')

        assert result is True
        assert len(requested_urls) == 4
        assert '/gdi/di/gestion/listarTiposOperaciones?t3=' in requested_urls[1]
        assert '/gdi/di/talonresumen/procesarTalon?t3=' in requested_urls[3]
        test_notifier_mock.send.assert_called_once_with(
            'Success!',
            f'{test_config.message_prefix}Receipts for period 202401 filed successfully!',
        )

    def test_form955_menu_url_not_found(
        self,
        test_config,
        test_http_client,
        test_profile,
        test_notifier_mock,
    ):
        """Test Form955 when menu URL not found."""
        handler = self._build_handler(
            test_http_client,
            test_config,
            test_notifier_mock,
            test_profile,
            menu=[],
        )

        result = handler.process('202401')

        assert result is False
        test_notifier_mock.send.assert_called_once_with(
            'Error',
            f'{test_config.message_prefix}Receipt management menu not found',
        )

    def test_form955_menu_validation_fails(
        self,
        test_config,
        test_http_client,
        test_profile,
        test_notifier_mock,
    ):
        """Test Form955 when menu page validation fails."""
        test_http_client.get = lambda _url: '<html><body>Wrong page content</body></html>'
        menu_with_receipt = [{'aplicacion': 'DI03100', 'url': '/eset/gdi/index.do'}]
        handler = self._build_handler(
            test_http_client, test_config, test_notifier_mock, test_profile, menu_with_receipt
        )

        result = handler.process('202401')

        assert result is False
        test_notifier_mock.send.assert_called_once_with(
            'Error',
            f'{test_config.message_prefix}Not able to manage receipts',
        )

    def test_form955_operations_invalid_json(
        self,
        test_config,
        test_http_client,
        test_profile,
        test_notifier_mock,
        mockup_menu_page_html,
    ):
        """Test Form955 handling invalid JSON in operations response."""

        def mock_get(url):
            if url.endswith('/eset/gdi/index.do'):
                return mockup_menu_page_html
            return 'not valid json'

        test_http_client.get = mock_get
        menu_with_receipt = [{'aplicacion': 'DI03100', 'url': '/eset/gdi/index.do'}]
        handler = self._build_handler(
            test_http_client, test_config, test_notifier_mock, test_profile, menu_with_receipt
        )

        result = handler.process('202401')

        assert result is False
        test_notifier_mock.send.assert_called_once_with(
            'Error',
            f'{test_config.message_prefix}Invalid response when getting operations',
        )

    def test_form955_operations_without_confirm_access(
        self,
        test_config,
        test_http_client,
        test_profile,
        test_notifier_mock,
        mockup_menu_page_html,
    ):
        """Test Form955 when operations do not contain confirm option id 6."""
        operations_without_confirm = [{'id': '4', 'url': 'gdi/editarComprobantes.do'}]

        def mock_get(url):
            if url.endswith('/eset/gdi/index.do'):
                return mockup_menu_page_html
            return json.dumps(operations_without_confirm)

        test_http_client.get = mock_get
        menu_with_receipt = [{'aplicacion': 'DI03100', 'url': '/eset/gdi/index.do'}]
        handler = self._build_handler(
            test_http_client, test_config, test_notifier_mock, test_profile, menu_with_receipt
        )

        result = handler.process('202401')

        assert result is False
        test_notifier_mock.send.assert_called_once_with(
            'Error',
            f'{test_config.message_prefix}No access to receipt forms',
        )

    def test_form955_receipt_forms_validation_fails(
        self,
        test_config,
        test_http_client,
        test_profile,
        test_notifier_mock,
        mockup_menu_page_html,
    ):
        """Test Form955 when receipt forms page does not contain expected title."""
        operations_response = [{'id': '6', 'url': 'gdi/presentacionTalonResumen.do?_cyp=test'}]

        def mock_get(url):
            if url.endswith('/eset/gdi/index.do'):
                return mockup_menu_page_html
            if '/gdi/di/gestion/listarTiposOperaciones?t3=' in url:
                return json.dumps(operations_response)
            return '<html><body>Unexpected content</body></html>'

        test_http_client.get = mock_get
        menu_with_receipt = [{'aplicacion': 'DI03100', 'url': '/eset/gdi/index.do'}]
        handler = self._build_handler(
            test_http_client, test_config, test_notifier_mock, test_profile, menu_with_receipt
        )

        result = handler.process('202401')

        assert result is False
        test_notifier_mock.send.assert_called_once_with(
            'Error',
            f'{test_config.message_prefix}No receipt forms available',
        )

    def test_form955_talon_invalid_json(
        self,
        test_config,
        test_http_client,
        test_profile,
        test_notifier_mock,
        mockup_menu_page_html,
    ):
        """Test Form955 handling invalid JSON in talon response."""
        operations_response = [{'id': '6', 'url': 'gdi/presentacionTalonResumen.do?_cyp=test'}]

        def mock_get(url):
            if url.endswith('/eset/gdi/index.do'):
                return mockup_menu_page_html
            if '/gdi/di/gestion/listarTiposOperaciones?t3=' in url:
                return json.dumps(operations_response)
            if '/eset/gdi/presentacionTalonResumen.do?_cyp=test' in url:
                return '<html><body>Registro de Comprobantes - Presentación de Talón</body></html>'
            return 'not valid json'

        test_http_client.get = mock_get
        menu_with_receipt = [{'aplicacion': 'DI03100', 'url': '/eset/gdi/index.do'}]
        handler = self._build_handler(
            test_http_client, test_config, test_notifier_mock, test_profile, menu_with_receipt
        )

        result = handler.process('202401')

        assert result is False
        test_notifier_mock.send.assert_called_once_with(
            'Error',
            f'{test_config.message_prefix}Filing receipt form 241',
        )

    def test_form955_talon_failure(
        self,
        test_config,
        test_http_client,
        test_profile,
        test_notifier_mock,
        mockup_menu_page_html,
    ):
        """Test Form955 when talon submission fails."""
        operations_response = [{'id': '6', 'url': 'gdi/presentacionTalonResumen.do?_cyp=test'}]
        talon_error = {'exito': False, 'mensaje': 'Receipt management period closed'}

        def mock_get(url):
            if url.endswith('/eset/gdi/index.do'):
                return mockup_menu_page_html
            if '/gdi/di/gestion/listarTiposOperaciones?t3=' in url:
                return json.dumps(operations_response)
            if '/eset/gdi/presentacionTalonResumen.do?_cyp=test' in url:
                return '<html><body>Registro de Comprobantes - Presentación de Talón</body></html>'
            return json.dumps(talon_error)

        test_http_client.get = mock_get
        menu_with_receipt = [{'aplicacion': 'DI03100', 'url': '/eset/gdi/index.do'}]
        handler = self._build_handler(
            test_http_client, test_config, test_notifier_mock, test_profile, menu_with_receipt
        )

        result = handler.process('202401')

        assert result is False
        test_notifier_mock.send.assert_called_once_with(
            'Error',
            f'{test_config.message_prefix}Filing receipt form 241',
        )

    def test_form955_empty_operations_list(
        self,
        test_config,
        test_http_client,
        test_profile,
        test_notifier_mock,
        mockup_menu_page_html,
    ):
        """Test Form955 with empty operations list."""

        def mock_get(url):
            if url.endswith('/eset/gdi/index.do'):
                return mockup_menu_page_html
            return json.dumps([])

        test_http_client.get = mock_get
        menu_with_receipt = [{'aplicacion': 'DI03100', 'url': '/eset/gdi/index.do'}]
        handler = self._build_handler(
            test_http_client, test_config, test_notifier_mock, test_profile, menu_with_receipt
        )

        result = handler.process('202401')

        assert result is False
        test_notifier_mock.send.assert_called_once_with(
            'Error',
            f'{test_config.message_prefix}No access to receipt forms',
        )
