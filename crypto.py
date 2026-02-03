"""AES-128-CBC encryption for API token generation."""

import base64
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad

# Same key and IV as the Bash version
KEY = bytes.fromhex('707265696d707265736f436f72726563')  # 16 bytes for AES-128
IV = bytes.fromhex('50506172736574696d65313773327733')   # 16 bytes


def encrypt(plaintext: str) -> str:
    """
    Encrypt plaintext using AES-128-CBC.

    Args:
        plaintext: The string to encrypt

    Returns:
        Base64-encoded ciphertext
    """
    if not plaintext:
        return ''

    cipher = AES.new(KEY, AES.MODE_CBC, IV)
    padded_data = pad(plaintext.encode('utf-8'), AES.block_size)
    ciphertext = cipher.encrypt(padded_data)
    return base64.b64encode(ciphertext).decode('utf-8')
