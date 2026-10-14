"""
Input Validation Module
Validates plaintext and cryptographic keys across all classical ciphers.
"""

from typing import Any
from algorithms.hill import parse_hill_key

def validate_cipher_input(cipher_name: str, text: str, key: Any) -> None:
    """
    Validates plaintext and key inputs for the chosen cipher.
    Raises ValueError with descriptive guidance upon validation failure.
    """
    if text is None or len(str(text)) == 0:
        raise ValueError("Input text cannot be empty.")

    name = cipher_name.strip()

    if name == "Caesar Cipher":
        try:
            int(str(key).strip())
        except (ValueError, TypeError, AttributeError):
            got = repr(key) if isinstance(key, str) and key.strip() else repr(key)
            raise ValueError(f"Shift key must be an integer (e.g. 5). Got {got}.")

    elif name == "Monoalphabetic Cipher":
        key_str = str(key).strip()
        if len(key_str) != 26:
            raise ValueError("Key must be 26 characters long.")
        clean_key = [c.upper() for c in key_str if c.isalpha()]
        if len(clean_key) != 26 or len(set(clean_key)) != 26:
            raise ValueError("Key must contain 26 unique alphabetic characters (A-Z permutation).")

    elif name == "Playfair Cipher":
        clean_key = [c.upper() for c in str(key) if c.isalpha()]
        if not clean_key:
            raise ValueError("Keyword must contain alphabetic characters.")

    elif name == "Hill Cipher":
        # parse_hill_key handles determinant invertibility checks
        parse_hill_key(str(key))

    elif name == "Vigenère Cipher":
        clean_key = [c.upper() for c in str(key) if c.isalpha()]
        if not clean_key:
            raise ValueError("Keyword must contain alphabetic characters.")

    elif name == "One-Time Pad":
        clean_key = [c.upper() for c in str(key) if c.isalpha()]
        plain_alpha_count = sum(1 for c in str(text) if c.isalpha())
        if len(clean_key) < plain_alpha_count:
            raise ValueError("Key length shorter than plaintext.")

    elif name == "Rail Fence Cipher":
        try:
            rails = int(str(key).strip())
            if rails < 2:
                raise ValueError("Number of rails must be an integer >= 2 (e.g. 3).")
        except (ValueError, TypeError, AttributeError):
            raise ValueError(f"Number of rails must be an integer >= 2 (e.g. 3). Got {repr(key)}.")

    elif name == "Columnar Transposition Cipher":
        clean_key = [c.upper() for c in str(key) if c.isalpha()]
        if not clean_key:
            raise ValueError("Keyword must contain alphabetic characters.")

    else:
        # Unknown cipher name
        pass
