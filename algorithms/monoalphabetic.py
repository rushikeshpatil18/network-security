"""
Monoalphabetic Cipher Implementation
Single-alphabet substitution mapping each letter of the alphabet to a 26-character permutation key.
"""

import string
import random

ALPHABET = string.ascii_uppercase

def generate_monoalphabetic_key() -> str:
    """Generates a random 26-character substitution key permutation."""
    chars = list(ALPHABET)
    random.shuffle(chars)
    return "".join(chars)

def monoalphabetic_encrypt(plaintext: str, key: str) -> str:
    """
    Encrypts plaintext using the provided 26-letter substitution key.
    Preserves case and non-alphabetic characters.
    """
    key = key.upper()
    sub_map = {}
    for orig, sub in zip(ALPHABET, key):
        sub_map[orig] = sub
        sub_map[orig.lower()] = sub.lower()

    return "".join(sub_map.get(c, c) for c in plaintext)

def monoalphabetic_decrypt(ciphertext: str, key: str) -> str:
    """
    Decrypts ciphertext using the provided 26-letter substitution key.
    """
    key = key.upper()
    rev_map = {}
    for orig, sub in zip(ALPHABET, key):
        rev_map[sub] = orig
        rev_map[sub.lower()] = orig.lower()

    return "".join(rev_map.get(c, c) for c in ciphertext)
