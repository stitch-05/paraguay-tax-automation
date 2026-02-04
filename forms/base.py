"""Base class for form handlers."""

import json
import re
import urllib.parse
from abc import ABC, abstractmethod
from html.parser import HTMLParser
from typing import Any, Callable, Dict, List, Optional, Tuple

from utils import send_message as notify


class InputParser(HTMLParser):
    """HTML parser to extract input elements and their attributes."""

    def __init__(self):
        super().__init__()
        self.inputs: List[Dict[str, str]] = []

    def handle_starttag(self, tag: str, attrs: List[Tuple[str, Optional[str]]]) -> None:
        if tag == 'input':
            attr_dict = {k: v for k, v in attrs if v is not None}
            self.inputs.append(attr_dict)


class DivAttributeParser(HTMLParser):
    """HTML parser to extract data-ng-init attribute from specific divs."""

    def __init__(self, controller_name: str):
        super().__init__()
        self.controller_name = controller_name
        self.ng_init_value: Optional[str] = None

    def handle_starttag(self, tag: str, attrs: List[Tuple[str, Optional[str]]]) -> None:
        if tag == 'div':
            attr_dict = dict(attrs)
            controller = attr_dict.get('data-ng-controller', '')
            if self.controller_name in controller:
                self.ng_init_value = attr_dict.get('data-ng-init')


class FormHandler(ABC):
    """Abstract base class for form handlers."""

    def __init__(
        self,
        http_client: Any,
        config: Any,
        notifier: Any,
        profile: Dict[str, Any],
        menu: List[Dict[str, Any]]
    ):
        self.http = http_client
        self.config = config
        self.notifier = notifier
        self.profile = profile
        self.menu = menu

        # Profile data
        self.cedula = profile.get('rucActivo', '')
        self.dv = profile.get('dvActivo', '')
        self.name = profile.get('nombre', '')

    @property
    def url_base(self) -> str:
        return self.http.URL_BASE

    @property
    def url_host(self) -> str:
        return self.http.URL_HOST

    def encrypt_token(self, data: dict) -> str:
        """Encrypt a dictionary as a token for API requests."""
        from crypto import encrypt
        json_str = json.dumps(data, separators=(',', ':'))
        return urllib.parse.quote(encrypt(json_str))

    def send_message(self, title: str, message: str) -> None:
        """Send a notification message."""
        notify(self.notifier, title, message, self.config.message_prefix)

    def get_menu_url(self, application_code: str) -> Optional[str]:
        """Get URL for a menu application by its code."""
        for item in self.menu:
            if item.get('aplicacion') == application_code:
                return item.get('url')
        return None

    def parse_inputs(self, html: str) -> List[Dict[str, str]]:
        """Parse input elements from HTML."""
        parser = InputParser()
        parser.feed(html)
        return parser.inputs

    def extract_div_ng_init(self, html: str, controller_name: str) -> Optional[str]:
        """Extract data-ng-init attribute from a div with specific controller."""
        parser = DivAttributeParser(controller_name)
        parser.feed(html)
        return parser.ng_init_value

    def contains_text(self, html: str, text: str) -> bool:
        """Check if HTML contains specific text."""
        return text in html

    @abstractmethod
    def process(self, period_or_link: str) -> bool:
        """
        Process the form.

        Args:
            period_or_link: Either a period string (YYYYMM) for tax forms,
                           or a link for profile updates

        Returns:
            True if successful, False otherwise
        """
        pass
