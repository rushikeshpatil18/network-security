"""
Playfair Cipher Implementation
Polygraphic substitution cipher using a 5x5 key matrix with 'I' and 'J' merged.
"""

def generate_playfair_matrix(keyword: str) -> list[list[str]]:
    """
    Constructs a 5x5 Playfair matrix from the provided keyword.
    Combines 'I' and 'J'.
    """
    cleaned = []
    seen = set()
    for char in keyword.upper():
        if char.isalpha():
            c = 'I' if char == 'J' else char
            if c not in seen:
                seen.add(c)
                cleaned.append(c)

    alphabet = "ABCDEFGHIKLMNOPQRSTUVWXYZ"
    for char in alphabet:
        if char not in seen:
            seen.add(char)
            cleaned.append(char)

    matrix = []
    for i in range(0, 25, 5):
        matrix.append(cleaned[i:i + 5])
    return matrix

def _prepare_plaintext(text: str) -> list[tuple[str, str]]:
    """
    Formats plaintext into digrams for Playfair encryption.
    Replaces 'J' with 'I', inserts filler 'X' between identical letters in a pair,
    and appends 'X' (or 'Z') if the length is odd.
    """
    letters = []
    for char in text.upper():
        if char.isalpha():
            letters.append('I' if char == 'J' else char)

    digrams = []
    i = 0
    while i < len(letters):
        first = letters[i]
        if i + 1 < len(letters):
            second = letters[i + 1]
            if first == second:
                filler = 'Q' if first == 'X' else 'X'
                digrams.append((first, filler))
                i += 1
            else:
                digrams.append((first, second))
                i += 2
        else:
            filler = 'Z' if first == 'X' else 'X'
            digrams.append((first, filler))
            i += 1

    return digrams

def _find_position(matrix: list[list[str]], char: str) -> tuple[int, int]:
    """Finds row and column of a character in the 5x5 Playfair matrix."""
    c = 'I' if char == 'J' else char
    for r in range(5):
        for col in range(5):
            if matrix[r][col] == c:
                return r, col
    return 0, 0

def playfair_encrypt(plaintext: str, keyword: str) -> str:
    """
    Encrypts plaintext using Playfair Cipher with the given keyword.
    """
    matrix = generate_playfair_matrix(keyword)
    digrams = _prepare_plaintext(plaintext)
    cipher_chars = []

    for c1, c2 in digrams:
        r1, col1 = _find_position(matrix, c1)
        r2, col2 = _find_position(matrix, c2)

        if r1 == r2:
            cipher_chars.append(matrix[r1][(col1 + 1) % 5])
            cipher_chars.append(matrix[r2][(col2 + 1) % 5])
        elif col1 == col2:
            cipher_chars.append(matrix[(r1 + 1) % 5][col1])
            cipher_chars.append(matrix[(r2 + 1) % 5][col2])
        else:
            cipher_chars.append(matrix[r1][col2])
            cipher_chars.append(matrix[r2][col1])

    return "".join(cipher_chars)

def playfair_decrypt(ciphertext: str, keyword: str) -> str:
    """
    Decrypts ciphertext using Playfair Cipher with the given keyword.
    """
    matrix = generate_playfair_matrix(keyword)
    letters = [('I' if c == 'J' else c) for c in ciphertext.upper() if c.isalpha()]
    
    plain_chars = []
    for i in range(0, len(letters), 2):
        if i + 1 < len(letters):
            c1, c2 = letters[i], letters[i + 1]
            r1, col1 = _find_position(matrix, c1)
            r2, col2 = _find_position(matrix, c2)

            if r1 == r2:
                plain_chars.append(matrix[r1][(col1 - 1) % 5])
                plain_chars.append(matrix[r2][(col2 - 1) % 5])
            elif col1 == col2:
                plain_chars.append(matrix[(r1 - 1) % 5][col1])
                plain_chars.append(matrix[(r2 - 1) % 5][col2])
            else:
                plain_chars.append(matrix[r1][col2])
                plain_chars.append(matrix[r2][col1])
        else:
            plain_chars.append(letters[i])

    return "".join(plain_chars)
