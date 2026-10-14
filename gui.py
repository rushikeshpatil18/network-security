"""
Graphical User Interface (GUI) Module — Modern Indigo SaaS redesign.

Layout: dark left sidebar navigation + light main workspace with cards.
Toolkit logic (ciphers, files, benchmark) is unchanged — only UI/UX restyled.
Standard library only: tkinter / ttk.
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import time
from typing import Dict, Any

# Import algorithm functions and utilities
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
from algorithms.columnar import columnar_encrypt, columnar_decrypt

from utils.file_handler import read_text_file, write_text_file
from utils.benchmark import benchmark_algorithms, BENCHMARK_EDUCATIONAL_NOTE
from utils.validator import validate_cipher_input

# Help explanations dictionary (unchanged content)
ALGORITHM_HELP = {
    "Caesar Cipher": (
        "CIPHER TYPE: Substitution (Monoalphabetic Shift)\n\n"
        "DESCRIPTION:\n"
        "One of the earliest and simplest ciphers. Each letter in the plaintext is shifted by a fixed number of positions down the alphabet.\n\n"
        "KEY REQUIREMENTS:\n"
        "An integer shift value (e.g., 3 or 5).\n\n"
        "ENCRYPTION FORMULA: C = (P + k) mod 26\n"
        "DECRYPTION FORMULA: P = (C - k) mod 26"
    ),
    "Monoalphabetic Cipher": (
        "CIPHER TYPE: Substitution (Monoalphabetic Permutation)\n\n"
        "DESCRIPTION:\n"
        "Replaces each letter of the alphabet with a unique corresponding letter according to a fixed 26-letter substitution alphabet key.\n\n"
        "KEY REQUIREMENTS:\n"
        "A string of exactly 26 unique alphabetic characters (e.g., QWERTYUIOPASDFGHJKLZXCVBNM).\n\n"
        "FEATURES:\n"
        "Supports 'Generate Random Key' for quick key creation."
    ),
    "Playfair Cipher": (
        "CIPHER TYPE: Substitution (Polygraphic 5x5 Matrix)\n\n"
        "DESCRIPTION:\n"
        "Encrypts pairs of letters (digrams) using a 5x5 matrix constructed from a keyword. 'J' is merged with 'I'.\n\n"
        "KEY REQUIREMENTS:\n"
        "An alphabetic keyword (e.g., MONARCHY).\n\n"
        "RULES:\n"
        "- Same Row: Shift right (encrypt) / left (decrypt).\n"
        "- Same Column: Shift down (encrypt) / up (decrypt).\n"
        "- Rectangle: Swap column indices."
    ),
    "Hill Cipher": (
        "CIPHER TYPE: Substitution (Polygraphic 2x2 Matrix)\n\n"
        "DESCRIPTION:\n"
        "Uses linear algebra mod 26 with a 2x2 key matrix to transform letter pairs.\n\n"
        "KEY REQUIREMENTS:\n"
        "A 4-letter word (e.g., HILL) or 4 integers (e.g., '3 3 2 5'). Matrix determinant must be coprime to 26.\n\n"
        "FORMULA: [C1, C2]^T = [K] * [P1, P2]^T mod 26"
    ),
    "Vigenère Cipher": (
        "CIPHER TYPE: Polyalphabetic Substitution\n\n"
        "DESCRIPTION:\n"
        "Uses a repeating keyword where each letter of the key determines the Caesar shift for the corresponding plaintext letter.\n\n"
        "KEY REQUIREMENTS:\n"
        "An alphabetic keyword (e.g., SECRETKEY).\n\n"
        "FORMULA: C_i = (P_i + K_i) mod 26"
    ),
    "One-Time Pad": (
        "CIPHER TYPE: Polyalphabetic Substitution (Mod 26 Additive / Unbreakable)\n\n"
        "DESCRIPTION:\n"
        "Mathematically unbreakable if key is truly random, equal in length to plaintext, and used only once.\n\n"
        "KEY REQUIREMENTS:\n"
        "Random key with length >= alphabetic length of plaintext."
    ),
    "Rail Fence Cipher": (
        "CIPHER TYPE: Transposition (Zigzag Pattern)\n\n"
        "DESCRIPTION:\n"
        "Writes plaintext in a downward/upward zigzag path across a specified number of parallel rails and reads off row by row.\n\n"
        "KEY REQUIREMENTS:\n"
        "An integer number of rails (key >= 2)."
    ),
    "Columnar Transposition Cipher": (
        "CIPHER TYPE: Transposition (Matrix Column Shuffling)\n\n"
        "DESCRIPTION:\n"
        "Writes plaintext in rows under a keyword, then reads out characters column by column in alphabetical order of the key.\n\n"
        "KEY REQUIREMENTS:\n"
        "An alphabetic keyword (e.g., GERMAN)."
    ),
}

CIPHER_KEY_HINTS = {
    "Caesar Cipher": "Enter integer shift (e.g., 5):",
    "Monoalphabetic Cipher": "Enter 26 unique letters (A-Z permutation):",
    "Playfair Cipher": "Enter keyword (e.g., MONARCHY):",
    "Hill Cipher": "Enter 4 letters (e.g. HILL) or 4 numbers (e.g. '3 3 2 5'):",
    "Vigenère Cipher": "Enter keyword (e.g., SECRETKEY):",
    "One-Time Pad": "Enter key (length >= plaintext letters):",
    "Rail Fence Cipher": "Enter number of rails (integer >= 2):",
    "Columnar Transposition Cipher": "Enter keyword (e.g., GERMAN):",
}

CIPHER_BADGE = {
    "Caesar Cipher": ("SHIFT", "#4F46E5"),
    "Monoalphabetic Cipher": ("SUBSTITUTION", "#7C3AED"),
    "Playfair Cipher": ("DIGRAM 5x5", "#0D9488"),
    "Hill Cipher": ("MATRIX 2x2", "#B45309"),
    "Vigenère Cipher": ("POLYALPHA", "#4F46E5"),
    "One-Time Pad": ("UNBREAKABLE", "#059669"),
    "Rail Fence Cipher": ("ZIGZAG", "#64748B"),
    "Columnar Transposition Cipher": ("COLUMNAR", "#64748B"),
}

FONT_FAMILY = "Segoe UI"


class CryptoToolkitGUI:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("CryptoKit — Classical Cryptography Toolkit")
        self.root.geometry("1140x760")
        self.root.minsize(1024, 680)

        # Palette — modern indigo SaaS
        self.c = {
            "sidebar_bg": "#1E1B4B",     # indigo-950
            "sidebar_hover": "#312E81",  # indigo-900
            "sidebar_active": "#4F46E5", # indigo-600
            "sidebar_text": "#E0E7FF",
            "sidebar_muted": "#A5B4FC",
            "main_bg": "#EEF2FF",        # indigo-50 tinted
            "card_bg": "#FFFFFF",
            "card_border": "#E0E7FF",
            "ink": "#1E1B4B",
            "muted": "#64748B",
            "accent": "#4F46E5",
            "accent_dark": "#3730A3",
            "success": "#059669",
            "dark_panel": "#0F172A",
            "input_bg": "#F8FAFC",
        }
        self.root.configure(bg=self.c["main_bg"])

        self.style = ttk.Style()
        try:
            self.style.theme_use("clam")
        except Exception:
            pass
        self._configure_styles()

        # ---- shell: sidebar + main ----
        self.sidebar = tk.Frame(self.root, bg=self.c["sidebar_bg"], width=248)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        self.main = tk.Frame(self.root, bg=self.c["main_bg"])
        self.main.pack(side="right", fill="both", expand=True)

        self._build_sidebar()
        self._build_topbar()
        self._build_pages()

        # round-trip tracking: encrypt stores (plain -> cipher) so an
        # immediate Decrypt reverses the output, not the input again.
        self._last_plain = ""
        self._last_cipher = ""

        self._show_page("dashboard")

    # ------------------------------------------------------------------
    # styles
    # ------------------------------------------------------------------
    def _configure_styles(self):
        s = self.style
        s.configure("Card.TFrame", background="white")
        s.configure("TLabel", background="white", foreground="#1E1B4B",
                    font=(FONT_FAMILY, 10))
        s.configure("CardTitle.TLabel", background="white",
                    foreground="#1E1B4B", font=(FONT_FAMILY, 11, "bold"))
        s.configure("CardSub.TLabel", background="white",
                    foreground="#64748B", font=(FONT_FAMILY, 9))
        s.configure("TCombobox", fieldbackground="white")
        s.configure("SaaS.Treeview", background="white", fieldbackground="white",
                    foreground="#1E1B4B", rowheight=26, font=(FONT_FAMILY, 9))
        s.configure("SaaS.Treeview.Heading", background="#EEF2FF",
                    foreground="#3730A3", font=(FONT_FAMILY, 9, "bold"))
        s.map("SaaS.Treeview", background=[("selected", "#4F46E5")],
              foreground=[("selected", "white")])

    # ------------------------------------------------------------------
    # sidebar
    # ------------------------------------------------------------------
    def _sidebar_btn(self, parent, text, cmd):
        b = tk.Button(parent, text=text, command=cmd,
                      bg=self.c["sidebar_bg"], fg=self.c["sidebar_text"],
                      activebackground=self.c["sidebar_hover"],
                      activeforeground="white",
                      font=(FONT_FAMILY, 11), anchor="w",
                      relief="flat", bd=0, padx=18, pady=11, cursor="hand2")
        b.pack(fill="x", pady=1)
        b.bind("<Enter>", lambda e, btn=b: self._hover(btn, True))
        b.bind("<Leave>", lambda e, btn=b: self._hover(btn, False))
        return b

    def _hover(self, btn, entering):
        if btn in self._nav_buttons.values() and self._active_page:
            for key, b in self._nav_buttons.items():
                if b is btn and key == self._active_page:
                    return
        btn.configure(bg=self.c["sidebar_hover"] if entering else self.c["sidebar_bg"])

    def _build_sidebar(self):
        # brand
        brand = tk.Frame(self.sidebar, bg=self.c["sidebar_bg"])
        brand.pack(fill="x", padx=18, pady=(22, 6))
        tk.Label(brand, text="◆  CRYPTO / KIT", bg=self.c["sidebar_bg"],
                 fg="white", font=(FONT_FAMILY, 15, "bold"), anchor="w").pack(anchor="w")
        tk.Label(brand, text="Classical ciphers · NS mini-project",
                 bg=self.c["sidebar_bg"], fg=self.c["sidebar_muted"],
                 font=(FONT_FAMILY, 9), anchor="w").pack(anchor="w", pady=(2, 0))

        # divider
        tk.Frame(self.sidebar, bg="#312E81", height=1).pack(fill="x", padx=18, pady=12)

        tk.Label(self.sidebar, text="WORKSPACE", bg=self.c["sidebar_bg"],
                 fg=self.c["sidebar_muted"], font=(FONT_FAMILY, 8, "bold"),
                 anchor="w").pack(anchor="w", padx=18, pady=(0, 6))

        self._nav_buttons: Dict[str, tk.Button] = {}
        self._active_page = ""
        nav = [
            ("dashboard", "◉   Cipher Dashboard"),
            ("files", "▤   File Operations"),
            ("benchmark", "▲   Compare Algorithms"),
            ("help", "?    Help & Docs"),
        ]
        for key, label in nav:
            self._nav_buttons[key] = self._sidebar_btn(
                self.sidebar, label, lambda k=key: self._show_page(k))

        # cipher quick-pick
        tk.Frame(self.sidebar, bg="#312E81", height=1).pack(fill="x", padx=18, pady=12)
        tk.Label(self.sidebar, text="CIPHER SHORTCUT", bg=self.c["sidebar_bg"],
                 fg=self.c["sidebar_muted"], font=(FONT_FAMILY, 8, "bold"),
                 anchor="w").pack(anchor="w", padx=18, pady=(0, 6))
        self.side_cipher = ttk.Combobox(self.sidebar, values=list(CIPHER_KEY_HINTS.keys()),
                                        state="readonly", font=(FONT_FAMILY, 9))
        self.side_cipher.set("Caesar Cipher")
        self.side_cipher.pack(fill="x", padx=18)
        self.side_cipher.bind("<<ComboboxSelected>>", self._on_sidebar_cipher)

        # footer
        foot = tk.Frame(self.sidebar, bg=self.c["sidebar_bg"])
        foot.pack(side="bottom", fill="x", padx=18, pady=18)
        tk.Label(foot, text="8 ciphers · session-only · no data retained",
                 bg=self.c["sidebar_bg"], fg=self.c["sidebar_muted"],
                 font=(FONT_FAMILY, 8), wraplength=200, justify="left").pack(anchor="w")
        tk.Button(foot, text="Exit Application", command=self.root.quit,
                  bg="#312E81", fg="white", activebackground="#4338CA",
                  activeforeground="white", font=(FONT_FAMILY, 10, "bold"),
                  relief="flat", bd=0, padx=12, pady=8, cursor="hand2").pack(fill="x", pady=(10, 0))

    def _on_sidebar_cipher(self, event=None):
        val = self.side_cipher.get()
        if hasattr(self, "combo_cipher"):
            self.combo_cipher.set(val)
            self._on_cipher_change()
        self._show_page("dashboard")

    # ------------------------------------------------------------------
    # topbar + pages
    # ------------------------------------------------------------------
    def _build_topbar(self):
        bar = tk.Frame(self.main, bg="white", height=68,
                       highlightbackground=self.c["card_border"],
                       highlightthickness=1)
        bar.pack(fill="x")
        bar.pack_propagate(False)
        left = tk.Frame(bar, bg="white")
        left.pack(side="left", fill="y", padx=20, pady=10)
        self.lbl_page_title = tk.Label(left, text="Cipher Dashboard", bg="white",
                                       fg=self.c["ink"], font=(FONT_FAMILY, 14, "bold"))
        self.lbl_page_title.pack(anchor="w")
        self.lbl_page_sub = tk.Label(left, text="Encrypt and decrypt with live key visuals",
                                     bg="white", fg=self.c["muted"],
                                     font=(FONT_FAMILY, 9))
        self.lbl_page_sub.pack(anchor="w")

        right = tk.Frame(bar, bg="white")
        right.pack(side="right", padx=20)
        self.badge = tk.Label(right, text="SHIFT", bg="#4F46E5", fg="white",
                              font=(FONT_FAMILY, 9, "bold"), padx=12, pady=5)
        self.badge.pack(side="right", padx=(8, 0))
        tk.Label(right, text="NS · 2026–27", bg="#EEF2FF", fg="#3730A3",
                 font=(FONT_FAMILY, 9, "bold"), padx=12, pady=5).pack(side="right")

        # status strip
        strip = tk.Frame(self.main, bg=self.c["main_bg"])
        strip.pack(fill="x", padx=20, pady=(10, 0))
        self.lbl_status = tk.Label(strip, text="Ready — pick a cipher on the left.",
                                   bg=self.c["main_bg"], fg=self.c["muted"],
                                   font=(FONT_FAMILY, 9), anchor="w")
        self.lbl_status.pack(fill="x")

    def _card(self, parent, padx=20, pady=14):
        outer = tk.Frame(parent, bg=self.c["main_bg"])
        outer.pack(fill="x", padx=20, pady=(10, 0))
        inner = tk.Frame(outer, bg=self.c["card_bg"],
                         highlightbackground=self.c["card_border"],
                         highlightthickness=1, padx=padx, pady=pady)
        inner.pack(fill="x")
        return inner

    def _build_pages(self):
        self.page_wrap = tk.Frame(self.main, bg=self.c["main_bg"])
        self.page_wrap.pack(fill="both", expand=True, pady=(0, 16))

        self.page_dashboard = tk.Frame(self.page_wrap, bg=self.c["main_bg"])
        self.page_files = tk.Frame(self.page_wrap, bg=self.c["main_bg"])
        self.page_benchmark = tk.Frame(self.page_wrap, bg=self.c["main_bg"])
        self.page_help = tk.Frame(self.page_wrap, bg=self.c["main_bg"])
        for p in (self.page_dashboard, self.page_files,
                  self.page_benchmark, self.page_help):
            p.place(relx=0, rely=0, relwidth=1, relheight=1)

        self._build_dashboard_tab()
        self._build_file_tab()
        self._build_benchmark_tab()
        self._build_help_tab()

    def _show_page(self, key):
        mapping = {
            "dashboard": (self.page_dashboard, "Cipher Dashboard",
                          "Encrypt and decrypt with live key visuals"),
            "files": (self.page_files, "File Operations",
                      "Encrypt or decrypt UTF-8 text files up to 1 MB"),
            "benchmark": (self.page_benchmark, "Compare Algorithms",
                          "Median repeated-run timings, not security strength"),
            "help": (self.page_help, "Help & Documentation",
                     "Key rules, formulas, and usage guide"),
        }
        page, title, sub = mapping[key]
        page.tkraise()
        self._active_page = key
        self.lbl_page_title.config(text=title)
        self.lbl_page_sub.config(text=sub)
        for k, b in self._nav_buttons.items():
            if k == key:
                b.configure(bg=self.c["sidebar_active"], fg="white")
            else:
                b.configure(bg=self.c["sidebar_bg"], fg=self.c["sidebar_text"])

    def _set_status(self, msg):
        ts = time.strftime("%H:%M:%S")
        self.lbl_status.config(text=f"[{ts}] {msg}")

    # ------------------------------------------------------------------
    # TAB 1: DASHBOARD
    # ------------------------------------------------------------------
    def _build_dashboard_tab(self):
        # config card
        cfg = self._card(self.page_dashboard)
        tk.Label(cfg, text="Cipher configuration", bg="white",
                 fg=self.c["ink"], font=(FONT_FAMILY, 11, "bold")).grid(
                     row=0, column=0, columnspan=3, sticky="w", pady=(0, 8))

        tk.Label(cfg, text="Select cipher", bg="white", fg=self.c["muted"],
                 font=(FONT_FAMILY, 9, "bold")).grid(row=1, column=0, sticky="w")
        self.combo_cipher = ttk.Combobox(cfg, values=list(CIPHER_KEY_HINTS.keys()),
                                         state="readonly", width=32,
                                         font=(FONT_FAMILY, 10))
        self.combo_cipher.set("Caesar Cipher")
        self.combo_cipher.grid(row=2, column=0, sticky="ew", padx=(0, 12), pady=4)
        self.combo_cipher.bind("<<ComboboxSelected>>", self._on_cipher_change)

        self.lbl_key = tk.Label(cfg, text=CIPHER_KEY_HINTS["Caesar Cipher"],
                                bg="white", fg=self.c["muted"],
                                font=(FONT_FAMILY, 9, "bold"))
        self.lbl_key.grid(row=1, column=1, columnspan=2, sticky="w")
        keyrow = tk.Frame(cfg, bg="white")
        keyrow.grid(row=2, column=1, columnspan=2, sticky="ew", pady=4)
        cfg.grid_columnconfigure(0, weight=1)
        cfg.grid_columnconfigure(1, weight=2)

        self.entry_key = tk.Entry(keyrow, font=("Consolas", 11), bg=self.c["input_bg"],
                                  fg=self.c["ink"], relief="flat",
                                  highlightbackground=self.c["card_border"],
                                  highlightthickness=1)
        self.entry_key.insert(0, "5")
        self.entry_key.pack(side="left", fill="x", expand=True, ipady=6, padx=(0, 8))
        self.btn_gen_key = tk.Button(keyrow, text="Generate key", command=self._generate_key,
                                     bg="#EEF2FF", fg="#3730A3",
                                     activebackground="#E0E7FF", activeforeground="#3730A3",
                                     font=(FONT_FAMILY, 10, "bold"), relief="flat",
                                     bd=0, padx=14, pady=6, cursor="hand2",
                                     state="disabled")
        self.btn_gen_key.pack(side="left")

        # io cards
        io_outer = tk.Frame(self.page_dashboard, bg=self.c["main_bg"])
        io_outer.pack(fill="both", expand=True, padx=20, pady=(10, 0))
        left_card = tk.Frame(io_outer, bg="white",
                             highlightbackground=self.c["card_border"],
                             highlightthickness=1)
        left_card.pack(side="left", fill="both", expand=True, padx=(0, 6))
        right_card = tk.Frame(io_outer, bg="white",
                              highlightbackground=self.c["card_border"],
                              highlightthickness=1)
        right_card.pack(side="right", fill="both", expand=True, padx=(6, 0))

        tk.Label(left_card, text="●  INPUT  —  plaintext", bg="white",
                 fg=self.c["muted"], font=(FONT_FAMILY, 9, "bold")).pack(anchor="w", padx=14, pady=(12, 4))
        self.txt_input = tk.Text(left_card, wrap="word", font=("Consolas", 11),
                                 bg=self.c["input_bg"], fg=self.c["ink"],
                                 relief="flat", height=9,
                                 highlightbackground=self.c["card_border"],
                                 highlightthickness=1)
        self.txt_input.pack(fill="both", expand=True, padx=14, pady=(0, 12))
        self.txt_input.insert("1.0", "NETWORK SECURITY")

        tk.Label(right_card, text="●  OUTPUT  —  result", bg="white",
                 fg=self.c["muted"], font=(FONT_FAMILY, 9, "bold")).pack(anchor="w", padx=14, pady=(12, 4))
        self.txt_output = tk.Text(right_card, wrap="word", font=("Consolas", 11),
                                  bg=self.c["dark_panel"], fg="#A7F3D0",
                                  relief="flat", height=9, insertbackground="white")
        self.txt_output.pack(fill="both", expand=True, padx=14, pady=(0, 12))

        # matrix pill
        pill_wrap = tk.Frame(self.page_dashboard, bg=self.c["main_bg"])
        pill_wrap.pack(fill="x", padx=20, pady=(10, 0))
        self.lbl_matrix_info = tk.Label(pill_wrap, text="Key visual will appear here for Playfair / Hill",
                                        bg="#EEF2FF", fg="#3730A3",
                                        font=("Consolas", 9), anchor="w",
                                        padx=12, pady=7)
        self.lbl_matrix_info.pack(fill="x")

        # actions
        act = tk.Frame(self.page_dashboard, bg=self.c["main_bg"])
        act.pack(fill="x", padx=20, pady=10)
        self._action_btn(act, "Encrypt →", self.c["accent"], "white",
                         self._do_encrypt).pack(side="left", padx=(0, 8))
        self._action_btn(act, "← Decrypt", self.c["dark_panel"], "white",
                         self._do_decrypt).pack(side="left", padx=8)
        self._action_btn(act, "⇄ Output → Input", "white", self.c["ink"],
                         self._use_output_as_input, border=True).pack(side="left", padx=8)
        self._action_btn(act, "Clear", "white", self.c["ink"],
                         self._clear_dashboard, border=True).pack(side="left", padx=8)
        self._action_btn(act, "Copy output", "white", self.c["ink"],
                         self._copy_output, border=True).pack(side="left", padx=8)

    def _action_btn(self, parent, text, bg, fg, cmd, border=False):
        b = tk.Button(parent, text=text, command=cmd, bg=bg, fg=fg,
                      activebackground=self.c["sidebar_hover"] if bg != "white" else "#F1F5F9",
                      activeforeground=fg if bg != "white" else self.c["ink"],
                      font=(FONT_FAMILY, 10, "bold"), relief="flat", bd=0,
                      padx=18, pady=9, cursor="hand2")
        if border:
            b.configure(highlightbackground=self.c["card_border"],
                        highlightthickness=1)
        return b

    def _on_cipher_change(self, event=None):
        cipher = self.combo_cipher.get()
        self.lbl_key.config(text=CIPHER_KEY_HINTS.get(cipher, "Enter Key:"))
        label, color = CIPHER_BADGE.get(cipher, ("CIPHER", "#4F46E5"))
        self.badge.config(text=label, bg=color)
        if hasattr(self, "side_cipher") and self.side_cipher.get() != cipher:
            self.side_cipher.set(cipher)

        if cipher in ["Monoalphabetic Cipher", "One-Time Pad"]:
            self.btn_gen_key.config(state="normal")
        else:
            self.btn_gen_key.config(state="disabled")

        defaults = {
            "Caesar Cipher": "5",
            "Monoalphabetic Cipher": "QWERTYUIOPASDFGHJKLZXCVBNM",
            "Playfair Cipher": "KEYWORD",
            "Hill Cipher": "HILL",
            "Vigenère Cipher": "SECRETKEY",
            "One-Time Pad": "SECRETKEYWORDOK",
            "Rail Fence Cipher": "3",
            "Columnar Transposition Cipher": "GERMAN"
        }
        if cipher in defaults:
            self.entry_key.delete(0, tk.END)
            self.entry_key.insert(0, defaults[cipher])

        self.lbl_matrix_info.config(
            text="Key visual will appear here for Playfair / Hill")

    def _generate_key(self):
        cipher = self.combo_cipher.get()
        if cipher == "Monoalphabetic Cipher":
            new_key = generate_monoalphabetic_key()
            self.entry_key.delete(0, tk.END)
            self.entry_key.insert(0, new_key)
            self._set_status("Random monoalphabetic key generated.")
        elif cipher == "One-Time Pad":
            text = self.txt_input.get("1.0", tk.END).strip()
            alpha_len = sum(1 for c in text if c.isalpha())
            if alpha_len == 0:
                alpha_len = 10
            new_key = generate_otp_key(alpha_len)
            self.entry_key.delete(0, tk.END)
            self.entry_key.insert(0, new_key)
            self._set_status(f"Secure OTP key generated ({alpha_len} chars).")

    def _do_encrypt(self):
        cipher = self.combo_cipher.get()
        text = self.txt_input.get("1.0", tk.END).rstrip("\n")
        key = self.entry_key.get().strip()
        if cipher == "Caesar Cipher" and key == "":
            key = "5"
            self.entry_key.delete(0, tk.END)
            self.entry_key.insert(0, key)

        try:
            validate_cipher_input(cipher, text, key)
            res = ""

            if cipher == "Caesar Cipher":
                res = caesar_encrypt(text, int(key))
            elif cipher == "Monoalphabetic Cipher":
                res = monoalphabetic_encrypt(text, key)
            elif cipher == "Playfair Cipher":
                res = playfair_encrypt(text, key)
                matrix = generate_playfair_matrix(key)
                matrix_str = "Playfair 5x5  ·  " + "  /  ".join(" ".join(row) for row in matrix)
                self.lbl_matrix_info.config(text=matrix_str)
            elif cipher == "Hill Cipher":
                res = hill_encrypt(text, key)
                matrix = parse_hill_key(key)
                self.lbl_matrix_info.config(
                    text=f"Hill 2x2  ·  [ {matrix[0][0]:2d} {matrix[0][1]:2d} ]  [ {matrix[1][0]:2d} {matrix[1][1]:2d} ]")
            elif cipher == "Vigenère Cipher":
                res = vigenere_encrypt(text, key)
            elif cipher == "One-Time Pad":
                res = otp_encrypt(text, key)
            elif cipher == "Rail Fence Cipher":
                res = rail_fence_encrypt(text, int(key))
            elif cipher == "Columnar Transposition Cipher":
                res = columnar_encrypt(text, key)

            self.txt_output.delete("1.0", tk.END)
            self.txt_output.insert("1.0", res)
            self._last_plain = text
            self._last_cipher = res
            self._set_status(f"Encrypted with {cipher} — {len(res)} chars.")
        except Exception as e:
            messagebox.showerror("Cipher Error", str(e))
            self._set_status(f"Encrypt failed: {e}")

    def _use_output_as_input(self):
        out_text = self.txt_output.get("1.0", tk.END).rstrip("\n")
        if not out_text:
            return
        self.txt_input.delete("1.0", tk.END)
        self.txt_input.insert("1.0", out_text)
        self._set_status("Output moved to input — now Decrypt to reverse.")

    def _do_decrypt(self):
        cipher = self.combo_cipher.get()
        text = self.txt_input.get("1.0", tk.END).rstrip("\n")
        out_text = self.txt_output.get("1.0", tk.END).rstrip("\n")
        # If user just encrypted (input unchanged, output holds ciphertext),
        # decrypt the output so NETWORK → SJYBTWP → NETWORK round-trips.
        if out_text and text == self._last_plain and out_text == self._last_cipher:
            text = out_text
        key = self.entry_key.get().strip()
        if cipher == "Caesar Cipher" and key == "":
            key = "5"
            self.entry_key.delete(0, tk.END)
            self.entry_key.insert(0, key)

        try:
            validate_cipher_input(cipher, text, key)
            res = ""

            if cipher == "Caesar Cipher":
                res = caesar_decrypt(text, int(key))
            elif cipher == "Monoalphabetic Cipher":
                res = monoalphabetic_decrypt(text, key)
            elif cipher == "Playfair Cipher":
                res = playfair_decrypt(text, key)
            elif cipher == "Hill Cipher":
                res = hill_decrypt(text, key)
            elif cipher == "Vigenère Cipher":
                res = vigenere_decrypt(text, key)
            elif cipher == "One-Time Pad":
                res = otp_decrypt(text, key)
            elif cipher == "Rail Fence Cipher":
                res = rail_fence_decrypt(text, int(key))
            elif cipher == "Columnar Transposition Cipher":
                res = columnar_decrypt(text, key)

            self.txt_output.delete("1.0", tk.END)
            self.txt_output.insert("1.0", res)
            self._set_status(f"Decrypted with {cipher} — {len(res)} chars.")
        except Exception as e:
            messagebox.showerror("Cipher Error", str(e))
            self._set_status(f"Decrypt failed: {e}")

    def _clear_dashboard(self):
        self.txt_input.delete("1.0", tk.END)
        self.txt_output.delete("1.0", tk.END)
        self.lbl_matrix_info.config(
            text="Key visual will appear here for Playfair / Hill")
        self._set_status("Workspace cleared.")

    def _copy_output(self):
        out_text = self.txt_output.get("1.0", tk.END).rstrip("\n")
        if out_text:
            self.root.clipboard_clear()
            self.root.clipboard_append(out_text)
            messagebox.showinfo("Copied", "Output copied to clipboard.")
            self._set_status("Output copied to clipboard.")

    # ------------------------------------------------------------------
    # TAB 2: FILE OPERATIONS
    # ------------------------------------------------------------------
    def _build_file_tab(self):
        box = self._card(self.page_files)
        tk.Label(box, text="Encrypt / decrypt text files", bg="white",
                 fg=self.c["ink"], font=(FONT_FAMILY, 11, "bold")).grid(
                     row=0, column=0, columnspan=3, sticky="w", pady=(0, 2))
        tk.Label(box, text="UTF-8 .txt only · 1 MB limit · output via save dialog",
                 bg="white", fg=self.c["muted"], font=(FONT_FAMILY, 9)).grid(
                     row=1, column=0, columnspan=3, sticky="w", pady=(0, 10))

        tk.Label(box, text="TEXT FILE", bg="white", fg=self.c["muted"],
                 font=(FONT_FAMILY, 9, "bold")).grid(row=2, column=0, sticky="w")
        self.entry_file_path = tk.Entry(box, font=("Consolas", 10),
                                        bg=self.c["input_bg"], fg=self.c["ink"],
                                        relief="flat",
                                        highlightbackground=self.c["card_border"],
                                        highlightthickness=1)
        self.entry_file_path.grid(row=3, column=0, columnspan=2, sticky="ew",
                                  pady=4, ipady=6)
        tk.Button(box, text="Browse…", command=self._browse_file,
                  bg="#EEF2FF", fg="#3730A3", font=(FONT_FAMILY, 10, "bold"),
                  relief="flat", bd=0, padx=16, pady=6, cursor="hand2").grid(
                      row=3, column=2, padx=(8, 0))

        tk.Label(box, text="CIPHER", bg="white", fg=self.c["muted"],
                 font=(FONT_FAMILY, 9, "bold")).grid(row=4, column=0, sticky="w", pady=(8, 0))
        tk.Label(box, text="KEY", bg="white", fg=self.c["muted"],
                 font=(FONT_FAMILY, 9, "bold")).grid(row=4, column=1, columnspan=2, sticky="w", pady=(8, 0))
        self.combo_file_cipher = ttk.Combobox(box, values=list(CIPHER_KEY_HINTS.keys()),
                                              state="readonly", font=(FONT_FAMILY, 10))
        self.combo_file_cipher.set("Caesar Cipher")
        self.combo_file_cipher.grid(row=5, column=0, sticky="ew", padx=(0, 8), pady=4)
        self.entry_file_key = tk.Entry(box, font=("Consolas", 10),
                                       bg=self.c["input_bg"], fg=self.c["ink"],
                                       relief="flat",
                                       highlightbackground=self.c["card_border"],
                                       highlightthickness=1)
        self.entry_file_key.insert(0, "5")
        self.entry_file_key.grid(row=5, column=1, columnspan=2, sticky="ew", pady=4, ipady=6)
        box.grid_columnconfigure(0, weight=1)
        box.grid_columnconfigure(1, weight=1)

        btnrow = tk.Frame(box, bg="white")
        btnrow.grid(row=6, column=0, columnspan=3, sticky="w", pady=12)
        self._action_btn(btnrow, "Encrypt & save file", self.c["accent"], "white",
                         self._encrypt_file_action).pack(side="left", padx=(0, 8))
        self._action_btn(btnrow, "Decrypt & save file", self.c["dark_panel"], "white",
                         self._decrypt_file_action).pack(side="left", padx=8)

        log_outer = tk.Frame(self.page_files, bg=self.c["main_bg"])
        log_outer.pack(fill="both", expand=True, padx=20, pady=(10, 0))
        log_card = tk.Frame(log_outer, bg=self.c["dark_panel"], padx=14, pady=12)
        log_card.pack(fill="both", expand=True)
        tk.Label(log_card, text="●  OPERATION LOG", bg=self.c["dark_panel"],
                 fg="#A5B4FC", font=(FONT_FAMILY, 9, "bold")).pack(anchor="w", pady=(0, 6))
        self.txt_file_log = tk.Text(log_card, height=9, font=("Consolas", 9),
                                    bg=self.c["dark_panel"], fg="#E0E7FF",
                                    relief="flat", wrap="word", insertbackground="white")
        self.txt_file_log.pack(fill="both", expand=True)
        self.txt_file_log.insert("1.0", "File Operations Log:\nSelect a file and algorithm to begin.")

    def _browse_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")])
        if file_path:
            self.entry_file_path.delete(0, tk.END)
            self.entry_file_path.insert(0, file_path)
            self._set_status(f"Selected file: {file_path}")

    def _encrypt_file_action(self):
        in_path = self.entry_file_path.get().strip()
        cipher = self.combo_file_cipher.get()
        key = self.entry_file_key.get().strip()

        try:
            content = read_text_file(in_path)
            validate_cipher_input(cipher, content, key)

            out_path = filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[("Text Files", "*.txt")],
                title="Save Encrypted File As"
            )
            if not out_path:
                return

            if cipher == "Caesar Cipher":
                res = caesar_encrypt(content, int(key))
            elif cipher == "Monoalphabetic Cipher":
                res = monoalphabetic_encrypt(content, key)
            elif cipher == "Playfair Cipher":
                res = playfair_encrypt(content, key)
            elif cipher == "Hill Cipher":
                res = hill_encrypt(content, key)
            elif cipher == "Vigenère Cipher":
                res = vigenere_encrypt(content, key)
            elif cipher == "One-Time Pad":
                res = otp_encrypt(content, key)
            elif cipher == "Rail Fence Cipher":
                res = rail_fence_encrypt(content, int(key))
            elif cipher == "Columnar Transposition Cipher":
                res = columnar_encrypt(content, key)

            saved_path = write_text_file(out_path, res)

            log_msg = f"[SUCCESS] Encrypted '{in_path}'\nUsing: {cipher}\nOutput File: {saved_path}\n"
            self.txt_file_log.insert(tk.END, f"\n{log_msg}")
            self._set_status(f"File encrypted → {saved_path}")
            messagebox.showinfo("Success", f"File encrypted successfully!\nSaved to: {saved_path}")
        except Exception as e:
            messagebox.showerror("File Error", str(e))
            self._set_status(f"File encrypt failed: {e}")

    def _decrypt_file_action(self):
        in_path = self.entry_file_path.get().strip()
        cipher = self.combo_file_cipher.get()
        key = self.entry_file_key.get().strip()

        try:
            content = read_text_file(in_path)
            validate_cipher_input(cipher, content, key)

            out_path = filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[("Text Files", "*.txt")],
                title="Save Decrypted File As"
            )
            if not out_path:
                return

            if cipher == "Caesar Cipher":
                res = caesar_decrypt(content, int(key))
            elif cipher == "Monoalphabetic Cipher":
                res = monoalphabetic_decrypt(content, key)
            elif cipher == "Playfair Cipher":
                res = playfair_decrypt(content, key)
            elif cipher == "Hill Cipher":
                res = hill_decrypt(content, key)
            elif cipher == "Vigenère Cipher":
                res = vigenere_decrypt(content, key)
            elif cipher == "One-Time Pad":
                res = otp_decrypt(content, key)
            elif cipher == "Rail Fence Cipher":
                res = rail_fence_decrypt(content, int(key))
            elif cipher == "Columnar Transposition Cipher":
                res = columnar_decrypt(content, key)

            saved_path = write_text_file(out_path, res)

            log_msg = f"[SUCCESS] Decrypted '{in_path}'\nUsing: {cipher}\nOutput File: {saved_path}\n"
            self.txt_file_log.insert(tk.END, f"\n{log_msg}")
            self._set_status(f"File decrypted → {saved_path}")
            messagebox.showinfo("Success", f"File decrypted successfully!\nSaved to: {saved_path}")
        except Exception as e:
            messagebox.showerror("File Error", str(e))
            self._set_status(f"File decrypt failed: {e}")

    # ------------------------------------------------------------------
    # TAB 3: BENCHMARK / COMPARISON
    # ------------------------------------------------------------------
    def _build_benchmark_tab(self):
        top = self._card(self.page_benchmark)
        tk.Label(top, text="Plaintext for comparison", bg="white",
                 fg=self.c["ink"], font=(FONT_FAMILY, 11, "bold")).pack(anchor="w")
        self.txt_bench_input = tk.Text(top, height=3, font=("Consolas", 10),
                                       bg=self.c["input_bg"], fg=self.c["ink"],
                                       relief="flat",
                                       highlightbackground=self.c["card_border"],
                                       highlightthickness=1)
        self.txt_bench_input.pack(fill="x", pady=8)
        self.txt_bench_input.insert("1.0", "THE QUICK BROWN FOX JUMPS OVER THE LAZY DOG 12345")
        self._action_btn(top, "▶  Run comparison across all ciphers",
                         self.c["accent"], "white",
                         self._run_benchmark).pack(anchor="w")

        table_outer = tk.Frame(self.page_benchmark, bg=self.c["main_bg"])
        table_outer.pack(fill="both", expand=True, padx=20, pady=(10, 0))
        table_card = tk.Frame(table_outer, bg="white",
                              highlightbackground=self.c["card_border"],
                              highlightthickness=1, padx=12, pady=12)
        table_card.pack(fill="both", expand=True)

        columns = ("name", "type", "enc_time", "dec_time", "status", "sample_cipher")
        self.tree_bench = ttk.Treeview(table_card, columns=columns, show="headings",
                                       height=8, style="SaaS.Treeview")

        self.tree_bench.heading("name", text="Algorithm")
        self.tree_bench.heading("type", text="Type")
        self.tree_bench.heading("enc_time", text="Enc (ms)")
        self.tree_bench.heading("dec_time", text="Dec (ms)")
        self.tree_bench.heading("status", text="Status")
        self.tree_bench.heading("sample_cipher", text="Sample ciphertext")

        self.tree_bench.column("name", width=190)
        self.tree_bench.column("type", width=110)
        self.tree_bench.column("enc_time", width=90, anchor="e")
        self.tree_bench.column("dec_time", width=90, anchor="e")
        self.tree_bench.column("status", width=80, anchor="center")
        self.tree_bench.column("sample_cipher", width=250)

        scroll = ttk.Scrollbar(table_card, orient="vertical", command=self.tree_bench.yview)
        self.tree_bench.configure(yscrollcommand=scroll.set)

        self.tree_bench.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")

        note_card = tk.Frame(self.page_benchmark, bg="#1E1B4B", padx=14, pady=10)
        note_card.pack(fill="x", padx=20, pady=10)
        tk.Label(note_card, text="Speed ≠ security — fast Caesar is trivially breakable; OTP is theoretically unbreakable.",
                 bg="#1E1B4B", fg="#C7D2FE", font=(FONT_FAMILY, 9),
                 wraplength=900, justify="left").pack(anchor="w")
        self.txt_bench_note = tk.Text(note_card, height=3, font=("Consolas", 8),
                                      bg="#1E1B4B", fg="#A5B4FC", relief="flat",
                                      wrap="word")
        self.txt_bench_note.pack(fill="x", pady=(6, 0))
        self.txt_bench_note.insert("1.0", BENCHMARK_EDUCATIONAL_NOTE.strip())

    def _run_benchmark(self):
        text = self.txt_bench_input.get("1.0", tk.END).strip()
        if not text:
            messagebox.showwarning("Warning", "Please enter plaintext for benchmarking.")
            return

        for item in self.tree_bench.get_children():
            self.tree_bench.delete(item)

        results = benchmark_algorithms(text)
        for r in results:
            self.tree_bench.insert(
                "",
                "end",
                values=(
                    r.name,
                    r.cipher_type,
                    f"{r.encrypt_time_ms:.4f}",
                    f"{r.decrypt_time_ms:.4f}",
                    r.status,
                    r.ciphertext[:30] + ("..." if len(r.ciphertext) > 30 else "")
                )
            )
        self._set_status(f"Benchmarked {len(results)} ciphers on {len(text)} chars.")

    # ------------------------------------------------------------------
    # TAB 4: HELP & DOCUMENTATION
    # ------------------------------------------------------------------
    def _build_help_tab(self):
        wrap = tk.Frame(self.page_help, bg=self.c["main_bg"])
        wrap.pack(fill="both", expand=True, padx=20, pady=(10, 0))

        left_card = tk.Frame(wrap, bg="white", width=240,
                             highlightbackground=self.c["card_border"],
                             highlightthickness=1, padx=12, pady=12)
        left_card.pack(side="left", fill="y", padx=(0, 6))
        left_card.pack_propagate(False)
        tk.Label(left_card, text="Topics", bg="white", fg=self.c["ink"],
                 font=(FONT_FAMILY, 11, "bold")).pack(anchor="w", pady=(0, 8))

        self.list_help_topics = tk.Listbox(left_card, font=(FONT_FAMILY, 10),
                                           bg=self.c["input_bg"], fg=self.c["ink"],
                                           relief="flat", highlightthickness=1,
                                           highlightbackground=self.c["card_border"],
                                           selectbackground=self.c["accent"],
                                           selectforeground="white", activestyle="none")
        self.list_help_topics.pack(fill="both", expand=True)

        for name in ALGORITHM_HELP.keys():
            self.list_help_topics.insert(tk.END, name)

        self.list_help_topics.bind("<<ListboxSelect>>", self._on_help_select)

        right_card = tk.Frame(wrap, bg="white",
                              highlightbackground=self.c["card_border"],
                              highlightthickness=1, padx=16, pady=14)
        right_card.pack(side="right", fill="both", expand=True, padx=(6, 0))
        tk.Label(right_card, text="Algorithm guide", bg="white", fg=self.c["ink"],
                 font=(FONT_FAMILY, 11, "bold")).pack(anchor="w", pady=(0, 8))

        self.txt_help_detail = tk.Text(right_card, wrap="word", font=(FONT_FAMILY, 10),
                                       bg=self.c["input_bg"], fg=self.c["ink"],
                                       relief="flat",
                                       highlightbackground=self.c["card_border"],
                                       highlightthickness=1, padx=10, pady=10)
        self.txt_help_detail.pack(fill="both", expand=True)

        self.list_help_topics.select_set(0)
        self._on_help_select()

    def _on_help_select(self, event=None):
        sel = self.list_help_topics.curselection()
        if not sel:
            return
        topic = self.list_help_topics.get(sel[0])
        content = ALGORITHM_HELP.get(topic, "No documentation available.")

        self.txt_help_detail.delete("1.0", tk.END)
        self.txt_help_detail.insert("1.0", f"{topic.upper()}\n\n{content}")


def launch_gui():
    """Launches the Tkinter GUI dashboard."""
    root = tk.Tk()
    app = CryptoToolkitGUI(root)
    root.mainloop()


if __name__ == "__main__":
    launch_gui()
