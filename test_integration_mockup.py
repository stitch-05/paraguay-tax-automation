#!/usr/bin/env python3
"""
Integration test for mockup mode.
Simulates the flow of creating an HTTPClient from a Config object.
"""

from config import create_argument_parser, load_config
from http_client import HTTPClient

print("Integration Test: Config -> HTTPClient -> Request")
print("=" * 60)

# Simulate command line with --mockup flag
print("\n1. Parsing CLI arguments with --mockup flag...")
parser = create_argument_parser()
args = parser.parse_args(['--mockup', '--verbose'])
print("   PASS")

# Load configuration
print("\n2. Loading configuration...")
config = load_config(args)
print(f"   mockup_mode: {config.mockup_mode}")
print(f"   verbose: {config.verbose}")
print(f"   mockup_dir: {config.mockup_dir}")
assert config.mockup_mode == True
assert config.verbose == True
print("   PASS")

# Create HTTPClient with config
print("\n3. Creating HTTPClient from config...")
http = HTTPClient(
    cookies_file=config.cookies_file,
    user_agents_file=config.user_agents_file,
    verify_ssl=config.verify_ssl,
    verbose=config.is_verbose,
    debug=config.is_debug,
    mockup_mode=config.mockup_mode,
    mockup_dir=config.mockup_dir,
)
print(f"   HTTPClient mockup_mode: {http.mockup_mode}")
print(f"   HTTPClient mockup_dir: {http.mockup_dir}")
assert http.mockup_mode == True
print("   PASS")

# Make a request
print("\n4. Making GET request in mockup mode...")
url = 'https://marangatu.set.gov.py/eset/perfil/vencimientos?t3=test'
response = http.get(url)
print(f"   Response length: {len(response)} bytes")
assert len(response) > 0
print("   PASS")

# Verify it's JSON
print("\n5. Verifying response format...")
import json
try:
    data = json.loads(response)
    print(f"   Parsed JSON with {len(data)} items")
    if len(data) > 0:
        print(f"   First item keys: {list(data[0].keys())}")
    print("   PASS")
except json.JSONDecodeError as e:
    print(f"   FAIL: Not valid JSON - {e}")
    exit(1)

print("\n6. Making authenticate POST request in mockup mode...")
login_url = 'https://marangatu.set.gov.py/eset/authenticate'
login_data = {
    'ruc': '80000000',
    'dv': '1',
    'password': 'test',
}
login_response = http.post_login(login_url, login_data)
print(f"   Response length: {len(login_response)} bytes")
assert len(login_response) > 0
if '<html' not in login_response.lower():
    print("   FAIL: Expected HTML response")
    exit(1)
print("   PASS")

print("\n" + "=" * 60)
print("Integration test completed successfully!")
print("\nSummary:")
print("  - CLI argument parsing: OK")
print("  - Configuration loading: OK")
print("  - HTTPClient creation: OK")
print("  - Mockup request handling: OK")
print("  - Response format: OK")
print("  - Authenticate request: OK")
