"""Captcha solving using NopeCHA API (free tier) or Capsolver API (paid)."""

import json
import time
import urllib.error
import urllib.parse
import urllib.request
from typing import Optional, Dict, Any


class NopeCHAClient:
    """
    Client for NopeCHA API to solve captchas.

    Free tier: 100 credits/day (reCAPTCHA v2 = 20 credits = 5 solves/day)
    No API key needed for free tier (uses IP-based tracking).
    """

    API_URL = 'https://api.nopecha.com/token/'

    def __init__(self, api_key: Optional[str] = None, verbose: bool = False):
        """
        Initialize NopeCHA client.

        Args:
            api_key: Optional NopeCHA API key (free tier works without key)
            verbose: Enable verbose output
        """
        self.api_key = api_key
        self.verbose = verbose

    def _make_request(self, method: str, data: Optional[Dict[str, Any]] = None,
                      params: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """Make a request to NopeCHA API."""
        url = self.API_URL

        if params:
            url += '?' + urllib.parse.urlencode(params)

        headers = {
            'Content-Type': 'application/json',
        }

        request_data = None
        if data:
            request_data = json.dumps(data).encode('utf-8')

        req = urllib.request.Request(url, data=request_data, headers=headers, method=method)

        try:
            with urllib.request.urlopen(req, timeout=30) as response:
                response_data = response.read().decode('utf-8')
                return json.loads(response_data)
        except urllib.error.HTTPError as e:
            # NopeCHA returns errors in response body
            try:
                error_body = e.read().decode('utf-8')
                return json.loads(error_body)
            except Exception:
                if self.verbose:
                    print(f'NopeCHA API HTTP error: {e.code}')
                raise
        except urllib.error.URLError as e:
            if self.verbose:
                print(f'NopeCHA API error: {e}')
            raise

    def solve_recaptcha_v2(
        self,
        website_url: str,
        website_key: str,
        timeout: int = 120
    ) -> Optional[str]:
        """
        Solve reCAPTCHA v2.

        Args:
            website_url: URL where the captcha is located
            website_key: reCAPTCHA site key
            timeout: Maximum time to wait for solution (seconds)

        Returns:
            Captcha solution token or None if failed
        """
        if self.verbose:
            print(f'Solving reCAPTCHA v2 for {website_url} using NopeCHA...')

        # Create task
        create_task_payload = {
            'type': 'recaptcha2',
            'sitekey': website_key,
            'url': website_url,
        }

        # Add API key if provided
        if self.api_key:
            create_task_payload['key'] = self.api_key

        try:
            create_response = self._make_request('POST', data=create_task_payload)
        except Exception as e:
            if self.verbose:
                print(f'Failed to create captcha task: {e}')
            return None

        # Check for errors
        if 'error' in create_response:
            error_code = create_response.get('error')
            error_msg = create_response.get('message', 'Unknown error')
            if self.verbose:
                print(f'NopeCHA error {error_code}: {error_msg}')
            return None

        job_id = create_response.get('data')
        if not job_id:
            if self.verbose:
                print('No job ID returned from NopeCHA')
            return None

        if self.verbose:
            print(f'Captcha task created: {job_id[:20]}...')

        # Poll for result
        start_time = time.time()
        poll_interval = 3  # seconds

        while time.time() - start_time < timeout:
            time.sleep(poll_interval)

            params = {'id': job_id}
            if self.api_key:
                params['key'] = self.api_key

            try:
                result_response = self._make_request('GET', params=params)
            except Exception as e:
                if self.verbose:
                    print(f'Failed to get task result: {e}')
                continue

            # Check for errors
            if 'error' in result_response:
                error_code = result_response.get('error')
                error_msg = result_response.get('message', 'Unknown error')

                # Error 14 = still processing
                if error_code == 14:
                    if self.verbose:
                        print(f'Captcha solving in progress... ({int(time.time() - start_time)}s elapsed)')
                    continue
                else:
                    if self.verbose:
                        print(f'NopeCHA error {error_code}: {error_msg}')
                    return None

            # Success - data contains the token
            captcha_response = result_response.get('data')
            if captcha_response and len(captcha_response) > 50:  # Token should be long
                if self.verbose:
                    print('Captcha solved successfully!')
                return captcha_response
            elif self.verbose:
                print(f'Unexpected response: {result_response}')

        if self.verbose:
            print(f'Captcha solving timeout after {timeout}s')
        return None


class CapsolverClient:
    """Client for Capsolver API to solve captchas (paid service)."""

    API_URL = 'https://api.capsolver.com'

    def __init__(self, api_key: str, verbose: bool = False):
        """
        Initialize Capsolver client.

        Args:
            api_key: Capsolver API key
            verbose: Enable verbose output
        """
        self.api_key = api_key
        self.verbose = verbose

    def _make_request(self, endpoint: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Make a request to Capsolver API."""
        url = f'{self.API_URL}/{endpoint}'

        request_data = json.dumps(data).encode('utf-8')
        headers = {
            'Content-Type': 'application/json',
        }

        req = urllib.request.Request(url, data=request_data, headers=headers)

        try:
            with urllib.request.urlopen(req) as response:
                response_data = response.read().decode('utf-8')
                return json.loads(response_data)
        except urllib.error.URLError as e:
            if self.verbose:
                print(f'Capsolver API error: {e}')
            raise

    def solve_recaptcha_v2(
        self,
        website_url: str,
        website_key: str,
        timeout: int = 120
    ) -> Optional[str]:
        """
        Solve reCAPTCHA v2.

        Args:
            website_url: URL where the captcha is located
            website_key: reCAPTCHA site key
            timeout: Maximum time to wait for solution (seconds)

        Returns:
            Captcha solution token or None if failed
        """
        if self.verbose:
            print(f'Solving reCAPTCHA v2 for {website_url} using Capsolver...')

        # Create task
        create_task_payload = {
            'clientKey': self.api_key,
            'task': {
                'type': 'ReCaptchaV2TaskProxyless',
                'websiteURL': website_url,
                'websiteKey': website_key,
            }
        }

        try:
            create_response = self._make_request('createTask', create_task_payload)
        except Exception as e:
            if self.verbose:
                print(f'Failed to create captcha task: {e}')
            return None

        if create_response.get('errorId') != 0:
            error_code = create_response.get('errorCode', 'UNKNOWN')
            error_desc = create_response.get('errorDescription', 'Unknown error')
            if self.verbose:
                print(f'Capsolver error: {error_code} - {error_desc}')
            return None

        task_id = create_response.get('taskId')
        if not task_id:
            if self.verbose:
                print('No task ID returned from Capsolver')
            return None

        if self.verbose:
            print(f'Captcha task created: {task_id}')

        # Poll for result
        start_time = time.time()
        poll_interval = 2  # seconds

        while time.time() - start_time < timeout:
            time.sleep(poll_interval)

            get_result_payload = {
                'clientKey': self.api_key,
                'taskId': task_id,
            }

            try:
                result_response = self._make_request('getTaskResult', get_result_payload)
            except Exception as e:
                if self.verbose:
                    print(f'Failed to get task result: {e}')
                continue

            if result_response.get('errorId') != 0:
                error_code = result_response.get('errorCode', 'UNKNOWN')
                error_desc = result_response.get('errorDescription', 'Unknown error')
                if self.verbose:
                    print(f'Capsolver error: {error_code} - {error_desc}')
                return None

            status = result_response.get('status')

            if status == 'ready':
                solution = result_response.get('solution', {})
                captcha_response = solution.get('gRecaptchaResponse')
                if self.verbose:
                    print('Captcha solved successfully!')
                return captcha_response
            elif status == 'failed':
                if self.verbose:
                    print('Captcha solving failed')
                return None
            elif status == 'processing':
                if self.verbose:
                    print(f'Captcha solving in progress... ({int(time.time() - start_time)}s elapsed)')
                continue
            else:
                if self.verbose:
                    print(f'Unknown status: {status}')

        if self.verbose:
            print(f'Captcha solving timeout after {timeout}s')
        return None


def get_captcha_client(
    nopecha_api_key: Optional[str] = None,
    capsolver_api_key: Optional[str] = None,
    verbose: bool = False
):
    """
    Get a captcha solver client.

    Priority:
    1. NopeCHA with API key (if provided)
    2. NopeCHA free tier (default - 5 reCAPTCHA v2 solves/day)
    3. Capsolver (if API key provided and NopeCHA not available)

    Args:
        nopecha_api_key: Optional NopeCHA API key
        capsolver_api_key: Optional Capsolver API key (paid service)
        verbose: Enable verbose output

    Returns:
        Captcha solver client instance
    """
    # Prefer NopeCHA (free tier available)
    # Even without API key, NopeCHA offers 100 credits/day by IP
    if nopecha_api_key or not capsolver_api_key:
        return NopeCHAClient(api_key=nopecha_api_key, verbose=verbose)

    # Fall back to Capsolver if explicitly configured
    if capsolver_api_key:
        return CapsolverClient(api_key=capsolver_api_key, verbose=verbose)

    # Default to NopeCHA free tier
    return NopeCHAClient(verbose=verbose)


# Backwards compatibility
def get_capsolver_client(api_key: Optional[str], verbose: bool = False) -> Optional[CapsolverClient]:
    """
    Get a Capsolver client if API key is provided.

    DEPRECATED: Use get_captcha_client() instead.

    Args:
        api_key: Capsolver API key
        verbose: Enable verbose output

    Returns:
        CapsolverClient instance or None if no API key
    """
    if not api_key:
        return None
    return CapsolverClient(api_key, verbose=verbose)
