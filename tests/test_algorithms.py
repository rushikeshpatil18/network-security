"""
Automated Unit Test Suite for Classical Cryptography Toolkit
Verifies all 8 classical ciphers, key validation, invertibility, and file operations.
"""

import unittest
import tempfile
import os

from algorithms.caesar import caesar_encrypt, caesar_decrypt
from algorithms.monoalphabetic import (
    monoalphabetic_encrypt,
    monoalphabetic_decrypt,
    generate_monoalphabetic_key,
)
from algorithms.playfair import playfair_encrypt, playfair_decrypt, generate_playfair_matrix
from algorithms.hill import hill_encrypt, hill_decrypt, parse_hill_key
from algorithms.vigenere import vigenere_encrypt, vigenere_decrypt
from algorithms.otp import otp_encrypt, otp_decrypt, generate_otp_key
from algorithms.rail_fence import rail_fence_encrypt, rail_fence_decrypt
from algorithms.columnar import columnar_encrypt, columnar_decrypt, get_column_order

from utils.validator import validate_cipher_input
from utils.file_handler import read_text_file, write_text_file
from utils.benchmark import benchmark_algorithms

class TestClassicalCryptoToolkit(unittest.TestCase):

    # 1. Caesar Cipher
    def test_01_caesar_encryption(self):
        pt = "NETWORK SECURITY"
        shift = 5
        self.assertEqual(caesar_encrypt(pt, shift), "SJYBTWP XJHZWNYD")

    def test_02_caesar_decryption(self):
        ct = "SJYBTWP XJHZWNYD"
        shift = 5
        self.assertEqual(caesar_decrypt(ct, shift), "NETWORK SECURITY")

    def test_03_caesar_invalid_shift(self):
        with self.assertRaises(ValueError):
            validate_cipher_input("Caesar Cipher", "TEST", "abc")

    # 2. Monoalphabetic Cipher
    def test_04_monoalphabetic_encrypt_decrypt(self):
        pt = "ATTACK AT DAWN"
        key = "QWERTYUIOPASDFGHJKLZXCVBNM"
        enc = monoalphabetic_encrypt(pt, key)
        self.assertEqual(enc, "QZZQEA QZ RQVF")
        dec = monoalphabetic_decrypt(enc, key)
        self.assertEqual(dec, pt)

    def test_05_monoalphabetic_invalid_key(self):
        with self.assertRaises(ValueError):
            validate_cipher_input("Monoalphabetic Cipher", "TEST", "SHORTKEY")

    def test_06_monoalphabetic_random_key(self):
        key = generate_monoalphabetic_key()
        self.assertEqual(len(key), 26)
        self.assertEqual(len(set(key)), 26)

    # 3. Playfair Cipher
    def test_07_playfair_matrix_generation(self):
        matrix = generate_playfair_matrix("MONARCHY")
        self.assertEqual(len(matrix), 5)
        for row in matrix:
            self.assertEqual(len(row), 5)
        # First row should be M, O, N, A, R
        self.assertEqual(matrix[0], ['M', 'O', 'N', 'A', 'R'])

    def test_08_playfair_encrypt_decrypt(self):
        pt = "INSTRUMENT"
        key = "MONARCHY"
        enc = playfair_encrypt(pt, key)
        dec = playfair_decrypt(enc, key)
        # Decrypted text should recover INSTRUMENT
        self.assertEqual(dec, pt)

    # 4. Hill Cipher
    def test_09_hill_valid_encryption_decryption(self):
        pt = "HELP"
        key = "3 3 2 5"
        enc = hill_encrypt(pt, key)
        self.assertEqual(enc, "HIAT")
        dec = hill_decrypt(enc, key)
        self.assertEqual(dec, pt)

    def test_10_hill_invalid_determinant(self):
        with self.assertRaises(ValueError):
            validate_cipher_input("Hill Cipher", "TEST", "2 4 2 4")

    # 5. Vigenère Cipher
    def test_11_vigenere_encrypt_decrypt(self):
        pt = "Network Security"
        key = "KEY"
        enc = vigenere_encrypt(pt, key)
        dec = vigenere_decrypt(enc, key)
        self.assertEqual(dec, pt)

    # 6. One-Time Pad
    def test_12_otp_valid_encrypt_decrypt(self):
        pt = "CONFIDENTIAL MESSAGE"
        key = generate_otp_key(sum(1 for c in pt if c.isalpha()))
        enc = otp_encrypt(pt, key)
        dec = otp_decrypt(enc, key)
        self.assertEqual(dec, pt)

    def test_13_otp_short_key_error(self):
        with self.assertRaises(ValueError):
            validate_cipher_input("One-Time Pad", "PLAINTEXT", "SHORT")

    # 7. Rail Fence Cipher
    def test_14_rail_fence_encrypt_decrypt(self):
        pt = "DEFEND THE EAST WALL"
        rails = 3
        enc = rail_fence_encrypt(pt, rails)
        dec = rail_fence_decrypt(enc, rails)
        self.assertEqual(dec, pt)

    def test_15_rail_fence_invalid_rails(self):
        with self.assertRaises(ValueError):
            validate_cipher_input("Rail Fence Cipher", "TEST", "1")

    # 8. Columnar Transposition Cipher
    def test_16_columnar_encrypt_decrypt(self):
        pt = "SECRET MESSAGE"
        key = "GERMAN"
        enc = columnar_encrypt(pt, key)
        dec = columnar_decrypt(enc, key)
        self.assertEqual(dec, pt)
        order = get_column_order(key)
        self.assertEqual(len(order), 6)

    # 9. Utilities & Benchmarking
    def test_17_benchmark_and_file_io(self):
        results = benchmark_algorithms("TEST PLAINTEXT")
        self.assertEqual(len(results), 8)
        for r in results:
            self.assertEqual(r.status, "PASS")

        # Test File I/O
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".txt") as tmp:
            tmp_path = tmp.name

        try:
            write_text_file(tmp_path, "TEST CONTENT")
            content = read_text_file(tmp_path)
            self.assertEqual(content, "TEST CONTENT")
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)

if __name__ == "__main__":
    unittest.main()
