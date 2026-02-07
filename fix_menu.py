#!/usr/bin/env python3
"""Fix corrupted menu.json in mockup data."""

import json

# Read the broken file as text
with open('__mockup__/eset/perfil/menu.json', 'r') as f:
    content = f.read()

# Replace all incomplete token placeholders with a valid fake token
fake_token = 'test1234567890abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_'

# Replace the broken tokens - they appear as _cyp=token at end of line or middle of line
fixed_content = content.replace('_cyp=token\n', f'_cyp={fake_token}",\n')
fixed_content = fixed_content.replace('_cyp=token"', f'_cyp={fake_token}"')

# Verify it's valid JSON now
try:
    menu = json.loads(fixed_content)
    print(f'✓ Fixed! Successfully parsed {len(menu)} menu items')
    
    # Find SG00005
    sg00005 = [item for item in menu if item.get('aplicacion') == 'SG00005']
    if sg00005:
        print(f'✓ Found SG00005: {sg00005[0].get("nombre")}')
    else:
        print('✗ SG00005 not found!')
except json.JSONDecodeError as e:
    print(f'✗ Still has errors: {e}')
    exit(1)

# Write back
with open('__mockup__/eset/perfil/menu.json', 'w') as f:
    f.write(fixed_content)

print('✓ File fixed and saved')
