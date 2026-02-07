"""HTTP client with cookie persistence, user-agent rotation, and random delays."""

import http.cookiejar
import json
import random
import ssl
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Optional, Union


class HTTPClient:
    """HTTP client for interacting with the Marangatu tax portal."""

    URL_HOST = 'https://marangatu.set.gov.py'
    URL_BASE = f'{URL_HOST}/eset'

    def __init__(
        self,
        cookies_file: Path,
        user_agents_file: Path,
        verify_ssl: bool = False,
        verbose: bool = False,
        debug: bool = False,
        mockup_mode: bool = False,
        mockup_dir: Optional[Path] = None
    ):
        self.cookies_file = cookies_file
        self.user_agents_file = user_agents_file
        self.verify_ssl = verify_ssl
        self.verbose = verbose
        self.debug = debug
        self.mockup_mode = mockup_mode
        self.mockup_dir = mockup_dir

        # Load cookies
        self.cookie_jar = http.cookiejar.MozillaCookieJar(str(cookies_file))
        if cookies_file.exists():
            try:
                self.cookie_jar.load(ignore_discard=True, ignore_expires=True)
            except Exception as e:
                if self.verbose:
                    print(f'Warning: Could not load cookies: {e}')

        # Select random user agent
        self.user_agent = self._load_random_user_agent()

        # Create SSL context
        self.ssl_context = self._create_ssl_context()

        # Build opener with cookie handler
        cookie_handler = urllib.request.HTTPCookieProcessor(self.cookie_jar)
        https_handler = urllib.request.HTTPSHandler(context=self.ssl_context)
        self.opener = urllib.request.build_opener(cookie_handler, https_handler)

    def _create_ssl_context(self) -> ssl.SSLContext:
        """Create SSL context with appropriate settings."""
        context = ssl.create_default_context()
        if not self.verify_ssl:
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE
        return context

    def _load_random_user_agent(self) -> str:
        """Load a random user agent from the user-agents file."""
        default_ua = (
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
            'AppleWebKit/537.36 (KHTML, like Gecko) '
            'Chrome/120.0.0.0 Safari/537.36'
        )

        if not self.user_agents_file.exists():
            return default_ua

        try:
            with open(self.user_agents_file, 'r', encoding='utf-8') as f:
                agents = [line.strip() for line in f if line.strip()]
            if agents:
                return random.choice(agents)
        except Exception as e:
            if self.verbose:
                print(f'Warning: Could not load user agents: {e}')

        return default_ua

    def _load_mockup_file(self, url: str) -> str:
        """Load mockup data from local file based on URL."""
        if not self.mockup_dir or not self.mockup_dir.exists():
            raise FileNotFoundError(f"Mockup directory not found: {self.mockup_dir}")

        # Parse URL to get path and query params
        parsed = urllib.parse.urlparse(url)
        path = parsed.path

        # Remove leading slash and extract path components
        if path.startswith('/'):
            path = path[1:]

        # Map URL path to file path
        # e.g., /eset/perfil/vencimientos -> __mockup__/eset/perfil/vencimientos.json
        # e.g., /eset -> __mockup__/eset/index.json
        # First try with .json extension
        json_file = self.mockup_dir / f"{path}.json"
        html_file = self.mockup_dir / f"{path}.html"
        index_json = self.mockup_dir / path / "index.json"
        index_html = self.mockup_dir / path / "index.html"

        target_file = None
        if json_file.exists():
            target_file = json_file
        elif html_file.exists():
            target_file = html_file
        elif index_json.exists():
            target_file = index_json
        elif index_html.exists():
            target_file = index_html
        else:
            # Try without extension
            plain_file = self.mockup_dir / path
            if plain_file.exists() and plain_file.is_file():
                target_file = plain_file

        if not target_file:
            raise FileNotFoundError(
                f"Mockup file not found for URL: {url}\n"
                f"Tried: {json_file}, {html_file}, {index_json}, {index_html}"
            )

        if self.verbose or self.debug:
            print(f"MOCKUP FILE: {target_file}")

        with open(target_file, 'r', encoding='utf-8') as f:
            return f.read()

    def save_cookies(self) -> None:
        """Save cookies to file."""
        try:
            self.cookie_jar.save(ignore_discard=True, ignore_expires=True)
        except Exception as e:
            if self.verbose:
                print(f'Warning: Could not save cookies: {e}')


    def _make_request(
        self,
        url: str,
        data: Optional[Union[str, bytes, dict]] = None,
        headers: Optional[dict] = None,
        method: Optional[str] = None
    ) -> str:
        """Make an HTTP request and return the response body."""
        # Check if mockup mode is enabled
        if self.mockup_mode:
            if self.debug:
                print(f'\r\033[K', end='')  # Clear current line
                print(f'DEBUG: {method or ("POST" if data else "GET")} {urllib.parse.unquote(url)}')
            return self._load_mockup_file(url)

        request_headers = {
            'User-Agent': self.user_agent,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
        }

        if headers:
            request_headers.update(headers)

        # Prepare data
        encoded_data = None
        if data is not None:
            if isinstance(data, dict):
                if headers and 'application/json' in headers.get('Content-Type', ''):
                    encoded_data = json.dumps(data).encode('utf-8')
                else:
                    encoded_data = urllib.parse.urlencode(data).encode('utf-8')
            elif isinstance(data, str):
                encoded_data = data.encode('utf-8')
            else:
                encoded_data = data

        # Create request
        req = urllib.request.Request(
            url,
            data=encoded_data,
            headers=request_headers,
            method=method
        )

        if self.debug:
            # Clear any animation line and print debug on new line
            print(f'\r\033[K', end='')  # Clear current line
            print(f'DEBUG: {req.get_method()} {urllib.parse.unquote(url)}')
            if encoded_data:
                print(f'DEBUG: Data: {encoded_data[:200]}...' if len(encoded_data) > 200 else f'DEBUG: Data: {encoded_data}')

        try:
            with self.opener.open(req) as response:
                content = response.read().decode('utf-8', errors='replace')
                self.save_cookies()
                return content
        except urllib.error.HTTPError as e:
            if self.verbose:
                print(f'HTTP Error {e.code}: {e.reason}')
            try:
                content = e.read().decode('utf-8', errors='replace')
                return content
            except Exception:
                raise
        except urllib.error.URLError as e:
            if self.verbose:
                print(f'URL Error: {e.reason}')
            raise

    def get(self, url: str, headers: Optional[dict] = None) -> str:
        """Make a GET request."""
        return self._make_request(url, headers=headers)

    def post(
        self,
        url: str,
        data: Union[str, bytes, dict],
        headers: Optional[dict] = None
    ) -> str:
        """Make a POST request with form data."""
        return self._make_request(url, data=data, headers=headers)

    def post_json(
        self,
        url: str,
        data: Union[str, dict],
        headers: Optional[dict] = None
    ) -> str:
        """Make a POST request with JSON data."""
        json_headers = {'Content-Type': 'application/json'}
        if headers:
            json_headers.update(headers)

        if isinstance(data, dict):
            json_data = json.dumps(data)
        else:
            json_data = data

        return self._make_request(url, data=json_data.encode('utf-8'), headers=json_headers)

    def post_login(self, url: str, data: dict) -> str:
        """Make a login POST request."""
        return self.post(url, data)
