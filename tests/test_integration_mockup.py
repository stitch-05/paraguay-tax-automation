"""
Integration tests using mockup mode.
Tests the full workflow from config to HTTP client to form handlers.
"""

import json

import pytest

from config import create_argument_parser, load_config
from http_client import HTTPClient
from forms.form_211 import Form211Handler
from forms.form_955 import Form955Handler


class TestMockupIntegration:
    """Integration tests using mockup files."""

    def test_config_to_http_client_flow(self):
        """Test Config -> HTTPClient -> Request workflow."""
        # Simulate command line with --mockup flag
        parser = create_argument_parser()
        args = parser.parse_args(['--mockup', '--verbose'])

        # Load configuration
        config = load_config(args)
        assert config.mockup_mode == True
        assert config.verbose == True

        # Create HTTPClient with config
        http = HTTPClient(
            cookies_file=config.cookies_file,
            user_agents_file=config.user_agents_file,
            verify_ssl=config.verify_ssl,
            verbose=config.is_verbose,
            debug=config.is_debug,
            mockup_mode=config.mockup_mode,
            mockup_dir=config.mockup_dir,
        )
        assert http.mockup_mode == True

        # Make a request
        url = 'https://marangatu.set.gov.py/eset/perfil/vencimientos?t3=test'
        response = http.get(url)
        assert len(response) > 0

        # Verify it's valid JSON
        data = json.loads(response)
        assert isinstance(data, list)
        assert len(data) > 0

    def test_authenticate_request_mockup(self):
        """Test authentication POST request in mockup mode."""
        parser = create_argument_parser()
        args = parser.parse_args(['--mockup'])
        config = load_config(args)

        http = HTTPClient(
            cookies_file=config.cookies_file,
            user_agents_file=config.user_agents_file,
            verify_ssl=config.verify_ssl,
            verbose=False,
            debug=False,
            mockup_mode=True,
            mockup_dir=config.mockup_dir,
        )

        login_url = 'https://marangatu.set.gov.py/eset/authenticate'
        login_data = {
            'ruc': '80000000',
            'dv': '1',
            'password': 'test',
        }
        login_response = http.post_login(login_url, login_data)
        assert len(login_response) > 0
        assert '<html' in login_response.lower()

    @pytest.mark.parametrize("handler_class,period_or_link,expected_msg", [
        (Form211Handler, '202601', 'VAT filed successfully!'),
        (Form955Handler, '202601', 'Receipts for period 202601 filed successfully!'),
    ])
    def test_form_handler_end_to_end(self, test_config, test_http_client, test_profile, test_notifier_mock, handler_class, period_or_link, expected_msg):
        """Test full end-to-end workflow for each form handler."""
        # Get menu
        menu_response = test_http_client.get(
            'https://marangatu.set.gov.py/eset/perfil/menu?t3=integration_test_token'
        )
        menu = json.loads(menu_response)

        # Create handler
        handler = handler_class(
            http_client=test_http_client,
            config=test_config,
            notifier=test_notifier_mock,
            profile=test_profile,
            menu=menu,
        )

        # Process form
        result = handler.process(period_or_link)

        # Verify success
        assert result is True
        test_notifier_mock.send.assert_called_once()
        call_args = test_notifier_mock.send.call_args
        assert call_args[0][0] == 'Success!'
        assert expected_msg in call_args[0][1]
