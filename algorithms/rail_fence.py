"""
Rail Fence Cipher Implementation
Transposition cipher writing characters in a zigzag pattern across parallel rails.
"""

def rail_fence_encrypt(plaintext: str, rails: int) -> str:
    """
    Encrypts plaintext using Rail Fence Cipher across the given number of rails.
    """
    if rails < 2:
        raise ValueError("Number of rails must be an integer >= 2.")
    if len(plaintext) <= rails:
        return plaintext

    fence = [[] for _ in range(rails)]
    rail = 0
    step = 1

    for char in plaintext:
        fence[rail].append(char)
        rail += step
        if rail == 0 or rail == rails - 1:
            step = -step

    return "".join("".join(row) for row in fence)

def rail_fence_decrypt(ciphertext: str, rails: int) -> str:
    """
    Decrypts ciphertext using Rail Fence Cipher across the given number of rails.
    """
    if rails < 2:
        raise ValueError("Number of rails must be an integer >= 2.")
    if len(ciphertext) <= rails:
        return ciphertext

    rail_indices = []
    rail = 0
    step = 1
    for _ in range(len(ciphertext)):
        rail_indices.append(rail)
        rail += step
        if rail == 0 or rail == rails - 1:
            step = -step

    counts = [rail_indices.count(r) for r in range(rails)]

    rail_slices = []
    idx = 0
    for count in counts:
        rail_slices.append(list(ciphertext[idx:idx + count]))
        idx += count

    result = []
    rail_ptrs = [0] * rails
    for r in rail_indices:
        result.append(rail_slices[r][rail_ptrs[r]])
        rail_ptrs[r] += 1

    return "".join(result)
