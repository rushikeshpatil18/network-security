"""
One-Time Pad (OTP) Cipher Implementation
Information-theoretically secure modular additive cipher with random key.
"""

import secrets
import string

def generate_otp_key(length: int) -> str:
    """
    Generates a cryptographically secure random key of given alphabetic length.
    """
    length = max(1, length)
    return "".join(secrets.choice(string.ascii_uppercase) for _ in range(length))

def otp_encrypt(plaintext: str, key: str) -> str:
    """
    Encrypts plaintext using One-Time Pad with the given key.
    Requires alphabetic key length >= alphabetic plaintext length.
    Preserves case and non-alphabetic characters.
    """
    key_letters = [c.upper() for c in key if c.isalpha()]
    plain_letters_count = sum(1 for c in plaintext if c.isalpha())
    if len(key_letters) < plain_letters_count:
        raise ValueError("Key length shorter than plaintext.")

    result = []
    key_idx = 0

    for char in plaintext:
        if 'A' <= char <= 'Z':
            shift = ord(key_letters[key_idx]) - ord('A')
            result.append(chr((ord(char) - ord('A') + shift) % 26 + ord('A')))
            key_idx += 1
        elif 'a' <= char <= 'z':
            shift = ord(key_letters[key_idx]) - ord('A')
            result.append(chr((ord(char) - ord('a') + shift) % 26 + ord('a')))
            key_idx += 1
        else:
            result.append(char)

    return "".join(result)

def otp_decrypt(ciphertext: str, key: str) -> str:
    """
    Decrypts ciphertext using One-Time Pad with the given key.
    """
    key_letters = [c.upper() for c in key if c.isalpha()]
    cipher_letters_count = sum(1 for c in ciphertext if c.isalpha())
    if len(key_letters) < cipher_letters_count:
        raise ValueError("Key length shorter than ciphertext.")

    result = []
    key_idx = 0

    for char in ciphertext:
        if 'A' <= char <= 'Z':
            shift = ord(key_letters[key_idx]) - ord('A')
            result.append(chr((ord(char) - ord('A') - shift) % 26 + ord('A')))
            key_idx += 1
        elif 'a' <= char <= 'z':
            shift = ord(key_letters[key_idx]) - ord('A')
            result.append(chr((ord(char) - ord('a') - shift) % 26 + ord('a')))
            key_idx += 1
        else:
            result.append(char)

    return "".join(result)
