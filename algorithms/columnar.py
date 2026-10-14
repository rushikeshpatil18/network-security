"""
Columnar Transposition Cipher Implementation
Transposition cipher writing text in rows and reading columns in keyword alphabetical sequence.
"""

import math

def get_column_order(keyword: str) -> list[int]:
    """
    Returns the 1-based numerical sequence / rank order for each character of the keyword.
    """
    upper = [c.upper() for c in keyword if c.isalpha()]
    if not upper:
        raise ValueError("Keyword must contain alphabetic characters.")

    sorted_indices = sorted(range(len(upper)), key=lambda i: (upper[i], i))
    ranks = [0] * len(upper)
    for rank, idx in enumerate(sorted_indices, 1):
        ranks[idx] = rank
    return ranks

def columnar_encrypt(plaintext: str, keyword: str) -> str:
    """
    Encrypts plaintext using Columnar Transposition with the given keyword.
    """
    clean_key = [c.upper() for c in keyword if c.isalpha()]
    if not clean_key:
        raise ValueError("Keyword must contain alphabetic characters.")

    w = len(clean_key)
    n = len(plaintext)
    if n == 0 or w == 0:
        return plaintext

    h = math.ceil(n / w)
    col_order = sorted(range(w), key=lambda c: (clean_key[c], c))

    result = []
    for col in col_order:
        for row in range(h):
            idx = row * w + col
            if idx < n:
                result.append(plaintext[idx])

    return "".join(result)

def columnar_decrypt(ciphertext: str, keyword: str) -> str:
    """
    Decrypts ciphertext using Columnar Transposition with the given keyword.
    """
    clean_key = [c.upper() for c in keyword if c.isalpha()]
    if not clean_key:
        raise ValueError("Keyword must contain alphabetic characters.")

    w = len(clean_key)
    n = len(ciphertext)
    if n == 0 or w == 0:
        return ciphertext

    h = math.ceil(n / w)
    num_last = n % w
    if num_last == 0:
        num_last = w

    col_lengths = [h if c < num_last else h - 1 for c in range(w)]
    col_order = sorted(range(w), key=lambda c: (clean_key[c], c))

    grid = {}
    idx = 0
    for col in col_order:
        length = col_lengths[col]
        grid[col] = list(ciphertext[idx:idx + length])
        idx += length

    result = []
    for row in range(h):
        for col in range(w):
            if row < len(grid[col]):
                result.append(grid[col][row])

    return "".join(result)
