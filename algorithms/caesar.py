"""
Caesar Cipher Implementation
Monoalphabetic shift cipher shifting alphabet characters mod 26.
"""

def caesar_encrypt(plaintext: str, shift: int) -> str:
    """
    Encrypts plaintext using Caesar Cipher with specified integer shift.
    Preserves case and non-alphabetic characters.
    """
    shift = shift % 26
    result = []
    for char in plaintext:
        if 'A' <= char <= 'Z':
            result.append(chr((ord(char) - ord('A') + shift) % 26 + ord('A')))
        elif 'a' <= char <= 'z':
            result.append(chr((ord(char) - ord('a') + shift) % 26 + ord('a')))
        else:
            result.append(char)
    return "".join(result)

def caesar_decrypt(ciphertext: str, shift: int) -> str:
    """
    Decrypts ciphertext using Caesar Cipher with specified integer shift.
    """
    return caesar_encrypt(ciphertext, -shift)
