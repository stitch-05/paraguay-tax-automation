"""Captcha solving using Capsolver API."""

import json
import time
import urllib.error
import urllib.parse
import urllib.request
from typing import Optional, Dict, Any


class CapsolverClient:
    """Client for Capsolver API to solve captchas."""

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
            print(f'Solving reCAPTCHA v2 for {website_url}...')

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


def get_capsolver_client(api_key: Optional[str], verbose: bool = False) -> Optional[CapsolverClient]:
    """
    Get a Capsolver client if API key is provided.

    Args:
        api_key: Capsolver API key
        verbose: Enable verbose output

    Returns:
        CapsolverClient instance or None if no API key
    """
    if not api_key:
        return None
    return CapsolverClient(api_key, verbose=verbose)
