"""
Vigenère Cipher Implementation
Polyalphabetic substitution cipher shifting characters using a repeating keyword.
"""

def vigenere_encrypt(plaintext: str, keyword: str) -> str:
    """
    Encrypts plaintext using Vigenère Cipher with the given keyword.
    Preserves character case and non-alphabetic characters.
    """
    key_letters = [c.upper() for c in keyword if c.isalpha()]
    if not key_letters:
        raise ValueError("Keyword must contain alphabetic characters.")

    result = []
    key_idx = 0
    key_len = len(key_letters)

    for char in plaintext:
        if 'A' <= char <= 'Z':
            shift = ord(key_letters[key_idx % key_len]) - ord('A')
            result.append(chr((ord(char) - ord('A') + shift) % 26 + ord('A')))
            key_idx += 1
        elif 'a' <= char <= 'z':
            shift = ord(key_letters[key_idx % key_len]) - ord('A')
            result.append(chr((ord(char) - ord('a') + shift) % 26 + ord('a')))
            key_idx += 1
        else:
            result.append(char)

    return "".join(result)

def vigenere_decrypt(ciphertext: str, keyword: str) -> str:
    """
    Decrypts ciphertext using Vigenère Cipher with the given keyword.
    """
    key_letters = [c.upper() for c in keyword if c.isalpha()]
    if not key_letters:
        raise ValueError("Keyword must contain alphabetic characters.")

    result = []
    key_idx = 0
    key_len = len(key_letters)

    for char in ciphertext:
        if 'A' <= char <= 'Z':
            shift = ord(key_letters[key_idx % key_len]) - ord('A')
            result.append(chr((ord(char) - ord('A') - shift) % 26 + ord('A')))
            key_idx += 1
        elif 'a' <= char <= 'z':
            shift = ord(key_letters[key_idx % key_len]) - ord('A')
            result.append(chr((ord(char) - ord('a') - shift) % 26 + ord('a')))
            key_idx += 1
        else:
            result.append(char)

    return "".join(result)
