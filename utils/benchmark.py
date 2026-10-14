"""
Benchmark Module
Measures and compares execution speed of all 8 classical ciphers.
"""

import time
from dataclasses import dataclass
from typing import List

from algorithms.caesar import caesar_encrypt, caesar_decrypt
from algorithms.monoalphabetic import monoalphabetic_encrypt, monoalphabetic_decrypt
from algorithms.playfair import playfair_encrypt, playfair_decrypt
from algorithms.hill import hill_encrypt, hill_decrypt
from algorithms.vigenere import vigenere_encrypt, vigenere_decrypt
from algorithms.otp import otp_encrypt, otp_decrypt, generate_otp_key
from algorithms.rail_fence import rail_fence_encrypt, rail_fence_decrypt
from algorithms.columnar import columnar_encrypt, columnar_decrypt

BENCHMARK_EDUCATIONAL_NOTE = (
    "\n[EDUCATIONAL NOTE]\n"
    "Benchmarking compares execution speed on your CPU, NOT mathematical cryptographic strength.\n"
    "Fast algorithms (like Caesar) offer virtually ZERO modern security against frequency analysis,\n"
    "whereas One-Time Pad offers perfect theoretical secrecy despite simple linear runtime.\n"
    "Modern secure applications require standardized cryptosystems like AES, RSA, or ECC."
)

@dataclass
class BenchmarkResult:
    name: str
    cipher_type: str
    encrypt_time_ms: float
    decrypt_time_ms: float
    status: str
    ciphertext: str

def benchmark_algorithms(text: str) -> List[BenchmarkResult]:
    """
    Executes encryption and decryption across all 8 classical ciphers
    using the provided plaintext, measuring execution times in milliseconds.
    """
    results = []

    # Prepare keys
    alpha_count = sum(1 for c in text if c.isalpha())
    otp_key = generate_otp_key(max(10, alpha_count))

    benchmarks = [
        ("Caesar Cipher", "Substitution", lambda t: caesar_encrypt(t, 5), lambda c: caesar_decrypt(c, 5)),
        ("Monoalphabetic Cipher", "Substitution", lambda t: monoalphabetic_encrypt(t, "QWERTYUIOPASDFGHJKLZXCVBNM"), lambda c: monoalphabetic_decrypt(c, "QWERTYUIOPASDFGHJKLZXCVBNM")),
        ("Playfair Cipher", "Substitution", lambda t: playfair_encrypt(t, "MONARCHY"), lambda c: playfair_decrypt(c, "MONARCHY")),
        ("Hill Cipher", "Substitution", lambda t: hill_encrypt(t, "3 3 2 5"), lambda c: hill_decrypt(c, "3 3 2 5")),
        ("Vigenère Cipher", "Substitution", lambda t: vigenere_encrypt(t, "KEYWORD"), lambda c: vigenere_decrypt(c, "KEYWORD")),
        ("One-Time Pad", "Substitution", lambda t: otp_encrypt(t, otp_key), lambda c: otp_decrypt(c, otp_key)),
        ("Rail Fence Cipher", "Transposition", lambda t: rail_fence_encrypt(t, 3), lambda c: rail_fence_decrypt(c, 3)),
        ("Columnar Transposition Cipher", "Transposition", lambda t: columnar_encrypt(t, "GERMAN"), lambda c: columnar_decrypt(c, "GERMAN")),
    ]

    for name, c_type, enc_fn, dec_fn in benchmarks:
        try:
            # Measure encryption
            t0 = time.perf_counter()
            ciphertext = enc_fn(text)
            t1 = time.perf_counter()
            enc_ms = (t1 - t0) * 1000.0

            # Measure decryption
            t2 = time.perf_counter()
            dec_text = dec_fn(ciphertext)
            t3 = time.perf_counter()
            dec_ms = (t3 - t2) * 1000.0

            status = "PASS"
        except Exception as e:
            enc_ms = 0.0
            dec_ms = 0.0
            status = f"ERROR: {str(e)[:15]}"
            ciphertext = ""

        results.append(BenchmarkResult(
            name=name,
            cipher_type=c_type,
            encrypt_time_ms=enc_ms,
            decrypt_time_ms=dec_ms,
            status=status,
            ciphertext=ciphertext
        ))

    return results
