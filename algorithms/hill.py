"""
Hill Cipher Implementation (2x2 Matrix)
Polygraphic substitution cipher using linear algebra modulo 26.
"""

import math
import re

def _mod_inverse_26(a: int) -> int:
    """Computes the modular multiplicative inverse of a modulo 26."""
    a = a % 26
    for x in range(1, 26):
        if (a * x) % 26 == 1:
            return x
    raise ValueError("Determinant has no inverse mod 26. Matrix is not invertible.")

def parse_hill_key(key_input: str) -> list[list[int]]:
    """
    Parses a 4-letter string (e.g. 'HILL') or 4 space-separated integers (e.g. '3 3 2 5')
    into a 2x2 integer matrix and validates invertibility modulo 26.
    """
    key_input = key_input.strip()
    # Check for numeric format
    num_matches = re.findall(r'-?\d+', key_input)
    if len(num_matches) == 4:
        nums = [int(n) % 26 for n in num_matches]
        matrix = [[nums[0], nums[1]], [nums[2], nums[3]]]
    else:
        letters = [c.upper() for c in key_input if c.isalpha()]
        if len(letters) != 4:
            raise ValueError("Hill key must be exactly 4 letters or 4 numbers (e.g., 'HILL' or '3 3 2 5').")
        nums = [ord(c) - ord('A') for c in letters]
        matrix = [[nums[0], nums[1]], [nums[2], nums[3]]]

    det = (matrix[0][0] * matrix[1][1] - matrix[0][1] * matrix[1][0]) % 26
    if math.gcd(det, 26) != 1:
        raise ValueError("Determinant has no inverse mod 26. Matrix is not invertible.")

    return matrix

def _get_inverse_matrix(matrix: list[list[int]]) -> list[list[int]]:
    """Computes the inverse of a 2x2 matrix modulo 26."""
    det = (matrix[0][0] * matrix[1][1] - matrix[0][1] * matrix[1][0]) % 26
    det_inv = _mod_inverse_26(det)

    # Adjugate matrix mod 26
    inv00 = (matrix[1][1] * det_inv) % 26
    inv01 = (-matrix[0][1] * det_inv) % 26
    inv10 = (-matrix[1][0] * det_inv) % 26
    inv11 = (matrix[0][0] * det_inv) % 26

    return [[inv00, inv01], [inv10, inv11]]

def hill_encrypt(plaintext: str, key_input: str) -> str:
    """
    Encrypts plaintext using Hill Cipher (2x2 matrix) with the given key.
    Preserves case and non-alphabetic characters.
    """
    matrix = parse_hill_key(key_input)
    
    # Extract letters and record positions
    letters = []
    positions = []
    cases = []
    for idx, ch in enumerate(plaintext):
        if ch.isalpha():
            letters.append(ord(ch.upper()) - ord('A'))
            positions.append(idx)
            cases.append(ch.isupper())

    # Pad with 'X' (23) if odd
    if len(letters) % 2 != 0:
        letters.append(ord('X') - ord('A'))
        positions.append(len(plaintext))
        cases.append(True)

    # Encrypt pairs
    cipher_vals = []
    for i in range(0, len(letters), 2):
        p1, p2 = letters[i], letters[i + 1]
        c1 = (matrix[0][0] * p1 + matrix[0][1] * p2) % 26
        c2 = (matrix[1][0] * p1 + matrix[1][1] * p2) % 26
        cipher_vals.extend([c1, c2])

    # Reconstruct text
    result = list(plaintext)
    if len(positions) > len(result):
        result.append('X')

    for pos, val, is_upper in zip(positions, cipher_vals, cases):
        ch = chr(val + (ord('A') if is_upper else ord('a')))
        if pos < len(result):
            result[pos] = ch
        else:
            result.append(ch)

    return "".join(result)

def hill_decrypt(ciphertext: str, key_input: str) -> str:
    """
    Decrypts ciphertext using Hill Cipher (2x2 matrix) with the given key.
    """
    matrix = parse_hill_key(key_input)
    inv_matrix = _get_inverse_matrix(matrix)

    letters = []
    positions = []
    cases = []
    for idx, ch in enumerate(ciphertext):
        if ch.isalpha():
            letters.append(ord(ch.upper()) - ord('A'))
            positions.append(idx)
            cases.append(ch.isupper())

    if len(letters) % 2 != 0:
        letters.append(ord('X') - ord('A'))
        positions.append(len(ciphertext))
        cases.append(True)

    plain_vals = []
    for i in range(0, len(letters), 2):
        c1, c2 = letters[i], letters[i + 1]
        p1 = (inv_matrix[0][0] * c1 + inv_matrix[0][1] * c2) % 26
        p2 = (inv_matrix[1][0] * c1 + inv_matrix[1][1] * c2) % 26
        plain_vals.extend([p1, p2])

    result = list(ciphertext)
    for pos, val, is_upper in zip(positions, plain_vals, cases):
        ch = chr(val + (ord('A') if is_upper else ord('a')))
        if pos < len(result):
            result[pos] = ch
        else:
            result.append(ch)

    return "".join(result)
