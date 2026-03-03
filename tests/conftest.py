"""Pytest configuration and shared fixtures."""

import json
from pathlib import Path
from typing import Any, Dict, List
from unittest.mock import MagicMock

import pytest

from config import Config
from http_client import HTTPClient


@pytest.fixture
def test_config() -> Config:
    """Create a config object in mockup mode for testing."""
    config = Config()
    config.username = 'test_user'
    config.password = 'test_pass'
    config.mockup_mode = True
    config.verbose = False  # Disable verbose to prevent AnimatedWaitContext issues
    config.debug = False    # Disable debug to prevent AnimatedWaitContext issues
    config.verify_ssl = False
    config.notification_service = None
    return config


@pytest.fixture
def test_http_client(test_config: Config) -> HTTPClient:
    """Create an HTTPClient in mockup mode for testing."""
    client = HTTPClient(
        cookies_file=test_config.cookies_file,
        user_agents_file=test_config.user_agents_file,
        verify_ssl=test_config.verify_ssl,
        verbose=test_config.verbose,
        debug=test_config.debug,
        mockup_mode=True,
        mockup_dir=test_config.mockup_dir
    )
    return client


@pytest.fixture
def test_profile() -> Dict[str, Any]:
    """Create a mock profile for testing."""
    return {
        'rucActivo': '8765432',
        'dvActivo': '1',  # Example DV
        'nombre': 'Test Taxpayer',
        'estado': 'INCOMPLETO',
        'vencimientos': []
    }


@pytest.fixture
def test_menu() -> List[Dict[str, Any]]:
    """Create a mock menu for testing with form URLs."""
    return [
        {
            'aplicacion': 'SG00005',  # VAT form affidavit
            'url': '/eset/gestionComprobantesVirtuales.do',
            'nombre': 'Gestión de Impuestos'
        },
        {
            'aplicacion': 'DI03100',  # Receipt management affidavit
            'url': '/eset/gdi/index.do',
            'nombre': 'Gestión de Comprobantes'
        },
        {
            'aplicacion': 'RU00001',  # Taxpayer registration affidavit
            'url': '/eset/actualizacion/editar_contribuyente.do',
            'nombre': 'Actualizar Contribuyente'
        }
    ]


@pytest.fixture
def test_notifier_mock() -> MagicMock:
    """Create a mock notifier for testing."""
    notifier = MagicMock()
    notifier.send = MagicMock(return_value=None)
    return notifier


@pytest.fixture
def mock_notifier_function():
    """Create a mock notifier function that tracks calls."""
    class Notifier:
        def __init__(self):
            self.calls = []

        def __call__(self, service, title, message, prefix=''):
            self.calls.append({
                'service': service,
                'title': title,
                'message': message,
                'prefix': prefix
            })

    return Notifier()


@pytest.fixture
def mockup_permit_response() -> Dict[str, Any]:
    """Create a mock permission response for Form211."""
    return {
        'permite': True,
        'url': '/eset/crear?_cyp=test_token_123'
    }


@pytest.fixture
def mockup_form_page_html() -> str:
    """Create mock HTML for a form page with input elements."""
    return """
    <html>
    <head><title>Form</title></head>
    <body>
        <input type="hidden" name="_cyp" value="test_token_123" />
        <input type="text" name="primeroApellido" value="" />
        <input type="text" name="segundoApellido" value="" />
        <input type="text" name="nombre" value="" />
        <input type="hidden" name="exportador" value="0" />
        <input type="hidden" name="fechaDiferida" value="" />
        <input type="text" name="C1" value="100" />
        <input type="hidden" name="C2" value="" />
        <input type="hidden" name="C3" value="" />
        <div data-ng-controller="FormController" data-ng-init="init()">
            Controller Data
        </div>
    </body>
    </html>
    """


@pytest.fixture
def mockup_form_submission_response() -> Dict[str, Any]:
    """Create a mock form submission response."""
    return {
        'exito': True,
        'operacion': {
            'errores': []
        },
        'documento': '202401001'
    }


@pytest.fixture
def mockup_operations_response() -> List[Dict[str, Any]]:
    """Create a mock operations list response for Form955."""
    return [
        {
            'id': '6',
            'nombre': 'Recibos',
            'url': '/eset/gdi/di/talonresumen/'
        },
        {
            'id': '7',
            'nombre': 'Facturas',
            'url': '/eset/gdi/di/factura/'
        }
    ]


@pytest.fixture
def mockup_talon_response() -> Dict[str, Any]:
    """Create a mock receipt/talon submission response."""
    return {
        'exito': True,
        'mensaje': 'Comprobante procesado exitosamente',
        'documento': 1234567890
    }


@pytest.fixture
def mockup_recovery_response() -> Dict[str, Any]:
    """Create a mock profile recovery response."""
    return {
        'generales': {
            'ruc': '8765432',
            'dv': '1',
            'razonSocial': 'Test Business',
            'primeroApellido': 'Test',
            'segundoApellido': 'User'
        },
        'domicilio': {
            'calle': 'Test Street 123',
            'ciudad': 'Asunción',
            'pais': 'Paraguay'
        }
    }


@pytest.fixture
def mockup_menu_page_html() -> str:
    """Create mock HTML for a menu page."""
    return """
    <html>
    <head><title>Menu</title></head>
    <body>
        <h1>Presentar Declaración</h1>
        <h2>Gestión de Comprobantes</h2>
        <div class="menu-item">Available form</div>
    </body>
    </html>
    """
