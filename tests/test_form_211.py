"""Tests for Form211Handler - VAT (IVA) form filing."""

import json
from unittest.mock import patch, MagicMock

import pytest

from forms.form_211 import Form211Handler


class TestForm211Handler:
    """Test suite for Form211Handler."""

    def test_form211_process_success(
        self,
        test_config,
        test_http_client,
        test_profile,
        test_menu,
        test_notifier_mock,
        mockup_menu_page_html,
        mockup_permit_response,
        mockup_form_page_html,
        mockup_form_submission_response
    ):
        """Test successful VAT form 211 filing with mockup responses."""
        # Setup HTTP client mock to return expected responses in order
        http_responses = {
            'get_menu': mockup_menu_page_html,
            'get_permit': json.dumps(mockup_permit_response),
            'get_form': mockup_form_page_html,
            'post_submit': json.dumps(mockup_form_submission_response)
        }

        call_count = {'get': 0, 'post': 0}
        original_get = test_http_client.get
        original_post_json = test_http_client.post_json

        def mock_get(url):
            if 'gestionComprobantesVirtuales' in url or 'gdi/index.do' in url:
                return http_responses['get_menu']
            elif 'declaracion/permite' in url:
                return http_responses['get_permit']
            elif 'crear' in url:
                return http_responses['get_form']
            return original_get(url)

        def mock_post_json(url, data):
            if 'presentar' in url:
                return http_responses['post_submit']
            return original_post_json(url, data)

        test_http_client.get = mock_get
        test_http_client.post_json = mock_post_json

        # Create handler
        handler = Form211Handler(
            http_client=test_http_client,
            config=test_config,
            notifier=test_notifier_mock,
            profile=test_profile,
            menu=test_menu
        )

        # Process VAT form for January 2024
        result = handler.process('202401')

        # Assertions
        assert result is True, 'Form211 handler should return True on success'

    def test_form211_menu_url_not_found(
        self,
        test_config,
        test_http_client,
        test_profile,
        test_notifier_mock
    ):
        """Test Form211 handling when menu URL is not found."""
        # Empty menu - no matching application code
        empty_menu = []

        handler = Form211Handler(
            http_client=test_http_client,
            config=test_config,
            notifier=test_notifier_mock,
            profile=test_profile,
            menu=empty_menu
        )

        result = handler.process('202401')

        assert result is False, 'Should return False when menu URL not found'

    def test_form211_menu_page_validation_fails(
        self,
        test_config,
        test_http_client,
        test_profile,
        test_menu,
        test_notifier_mock
    ):
        """Test Form211 when menu page doesn't contain expected text."""
        # Mock HTTP client to return page without expected text
        def mock_get(url):
            return '<html><body>Wrong page</body></html>'

        test_http_client.get = mock_get

        handler = Form211Handler(
            http_client=test_http_client,
            config=test_config,
            notifier=test_notifier_mock,
            profile=test_profile,
            menu=test_menu
        )

        result = handler.process('202401')

        assert result is False, 'Should return False when menu page validation fails'

    def test_form211_permit_response_invalid_json(
        self,
        test_config,
        test_http_client,
        test_profile,
        test_menu,
        test_notifier_mock,
        mockup_menu_page_html
    ):
        """Test Form211 handling of invalid JSON in permit response."""
        call_count = {'count': 0}

        def mock_get(url):
            call_count['count'] += 1
            if call_count['count'] == 1:  # First call - menu page
                return mockup_menu_page_html
            else:  # Second call - permit response with invalid JSON
                return 'invalid json response'

        test_http_client.get = mock_get

        handler = Form211Handler(
            http_client=test_http_client,
            config=test_config,
            notifier=test_notifier_mock,
            profile=test_profile,
            menu=test_menu
        )

        result = handler.process('202401')

        assert result is False, 'Should return False on invalid permit JSON'

    def test_form211_permit_denied(
        self,
        test_config,
        test_http_client,
        test_profile,
        test_menu,
        test_notifier_mock,
        mockup_menu_page_html
    ):
        """Test Form211 when permission to file is denied."""
        denied_permit = {'permite': False, 'razon': 'Form already filed'}

        call_count = {'count': 0}

        def mock_get(url):
            call_count['count'] += 1
            if call_count['count'] == 1:  # Menu page
                return mockup_menu_page_html
            else:  # Permit response
                return json.dumps(denied_permit)

        test_http_client.get = mock_get

        handler = Form211Handler(
            http_client=test_http_client,
            config=test_config,
            notifier=test_notifier_mock,
            profile=test_profile,
            menu=test_menu
        )

        result = handler.process('202401')

        assert result is False, 'Should return False when permission denied'

    def test_form211_submission_failure(
        self,
        test_config,
        test_http_client,
        test_profile,
        test_menu,
        test_notifier_mock,
        mockup_menu_page_html,
        mockup_permit_response,
        mockup_form_page_html
    ):
        """Test Form211 submission failure with error response."""
        # Response with exito=False
        error_response = {
            'exito': False,
            'operacion': {
                'errores': [
                    {'descripcion': 'VAT period already filed'}
                ]
            }
        }

        call_count = {'count': 0}

        def mock_get(url):
            call_count['count'] += 1
            if call_count['count'] == 1:  # Menu
                return mockup_menu_page_html
            elif call_count['count'] == 2:  # Permit
                return json.dumps(mockup_permit_response)
            else:  # Form page
                return mockup_form_page_html

        def mock_post_json(url, data):
            return json.dumps(error_response)

        test_http_client.get = mock_get
        test_http_client.post_json = mock_post_json

        handler = Form211Handler(
            http_client=test_http_client,
            config=test_config,
            notifier=test_notifier_mock,
            profile=test_profile,
            menu=test_menu
        )

        result = handler.process('202401')

        assert result is False, 'Should return False when submission fails'

    def test_form211_extraction_of_cyp_token(
        self,
        test_config,
        test_http_client,
        test_profile,
        test_menu,
        test_notifier_mock,
        mockup_menu_page_html,
        mockup_form_submission_response
    ):
        """Test Form211 correctly extracts _cyp token from permit URL."""
        permit_response = {
            'permite': True,
            'url': '/eset/crear?_cyp=extracted_token_xyz&other=param'
        }

        # Mock form page with different token than in URL
        form_page_html = """
        <html>
        <head><title>Form</title></head>
        <body>
            <input type="hidden" name="_cyp" value="ignored_value" />
            <input type="text" name="primeroApellido" value="" />
        </body>
        </html>
        """

        submitted_data = None

        def mock_post_json(url, data):
            nonlocal submitted_data
            submitted_data = json.loads(data)
            return json.dumps(mockup_form_submission_response)

        call_count = {'count': 0}

        def mock_get(url):
            call_count['count'] += 1
            if call_count['count'] == 1:
                return mockup_menu_page_html
            elif call_count['count'] == 2:
                return json.dumps(permit_response)
            else:
                return form_page_html

        test_http_client.get = mock_get
        test_http_client.post_json = mock_post_json

        handler = Form211Handler(
            http_client=test_http_client,
            config=test_config,
            notifier=test_notifier_mock,
            profile=test_profile,
            menu=test_menu
        )

        result = handler.process('202401')

        assert result is True
        assert submitted_data is not None
        # Token should be extracted from the URL, not from the form
        assert submitted_data['_cyp'] == 'extracted_token_xyz', \
            'Token should be extracted from permit URL, not from form inputs'
