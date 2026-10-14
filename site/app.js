/* CRYPT0_KIT UI wiring — static site, no backend. */
"use strict";
(function () {
  const $ = (id) => document.getElementById(id);
  const CIPHERS = [
    ["Caesar Cipher", "SHIFT", "5", "Integer shift (e.g. 5)"],
    ["Monoalphabetic Cipher", "SUBSTITUTION", "QWERTYUIOPASDFGHJKLZXCVBNM", "26 unique letters A-Z"],
    ["Playfair Cipher", "DIGRAM 5x5", "MONARCHY", "Keyword (e.g. MONARCHY)"],
    ["Hill Cipher", "MATRIX 2x2", "HILL", "4 letters (HILL) or 4 numbers (3 3 2 5)"],
    ["Vigenère Cipher", "POLYALPHA", "SECRETKEY", "Keyword (e.g. SECRETKEY)"],
    ["One-Time Pad", "UNBREAKABLE", "SECRETKEYWORDOK", "Key length >= plaintext letters"],
    ["Rail Fence Cipher", "ZIGZAG", "3", "Rails integer >= 2"],
    ["Columnar Transposition Cipher", "COLUMNAR", "GERMAN", "Keyword (e.g. GERMAN)"],
  ];
  const HELP = {
    "Caesar Cipher": "Substitution shift.\nKey: integer (e.g. 5).\nC = (P + k) mod 26",
    "Monoalphabetic Cipher": "26-letter permutation key.\nUse gen_key for a random key.",
    "Playfair Cipher": "5x5 digram matrix, J->I.\nKey: keyword (e.g. MONARCHY).",
    "Hill Cipher": "2x2 matrix mod 26.\nKey: 4 letters (HILL) or 4 numbers.",
    "Vigenère Cipher": "Repeating keyword shift.\nC_i = (P_i + K_i) mod 26",
    "One-Time Pad": "Unbreakable if random, same length, single use.",
    "Rail Fence Cipher": "Zigzag transposition.\nKey: rails >= 2.",
    "Columnar Transposition Cipher": "Keyword column-shuffle.\nKey: e.g. GERMAN.",
  };
  const META = Object.fromEntries(CIPHERS.map(([n, b, d, h]) => [n, { badge: b, def: d, hint: h }]));

  const cipherSel = $("cipher"), sideSel = $("sideCipher");
  CIPHERS.forEach(([n]) => {
    const o = document.createElement("option"); o.value = n; o.textContent = n; cipherSel.appendChild(o);
    const s = document.createElement("option"); s.value = n; s.textContent = n; sideSel.appendChild(s);
  });

  function show(p) {
    document.querySelectorAll("section").forEach((s) => s.classList.remove("active"));
    $(p).classList.add("active");
    document.querySelectorAll(".navbtn").forEach((b) => b.classList.toggle("active", b.dataset.p === p));
    $("pageTitle").textContent = { dashboard: "root@crypter:~$ cipher.exe", compare: "root@crypter:~$ benchmark.exe", help: "root@crypter:~$ manual.txt" }[p];
  }
  document.querySelectorAll(".navbtn").forEach((b) => { b.onclick = () => show(b.dataset.p); });

  function setCipher(n) {
    cipherSel.value = n; sideSel.value = n;
    $("badge").textContent = META[n].badge;
    $("keyHint").textContent = "KEY — " + META[n].hint;
    $("key").value = META[n].def;
    $("genBtn").disabled = !(n === "Monoalphabetic Cipher" || n === "One-Time Pad");
    $("matrix").textContent = "Key visual will appear here for Playfair / Hill";
    show("dashboard");
  }
  cipherSel.onchange = () => setCipher(cipherSel.value);
  sideSel.onchange = () => setCipher(sideSel.value);

  const status = (m) => { $("status").textContent = m; };
  const showErr = (m) => { $("err").textContent = m; $("err").style.display = "block"; };

  let lastPlain = "", lastCipher = "";
  function call(op) {
    const cipher = cipherSel.value;
    let src = $("inp").value;
    const rawKey = $("key").value;
    let key = rawKey.trim();
    if (cipher === "Caesar Cipher" && key === "") { key = "5"; $("key").value = "5"; }
    if ((cipher === "Caesar Cipher" || cipher === "Rail Fence Cipher") && !/^-?\d+$/.test(key)) {
      showErr(cipher === "Caesar Cipher"
        ? "Shift key must be an integer (e.g. 5). You entered: " + (rawKey === "" ? "(empty)" : '"' + rawKey + '"')
        : "Rails must be an integer >= 2 (e.g. 3). You entered: " + (rawKey === "" ? "(empty)" : '"' + rawKey + '"'));
      return;
    }
    if (cipher === "Rail Fence Cipher" && parseInt(key, 10) < 2) { showErr('Rails must be >= 2. You entered: "' + rawKey + '"'); return; }
    if (op === "decrypt" && $("out").value.trim() !== "" && src === lastPlain && $("out").value === lastCipher) src = $("out").value;
    $("err").style.display = "none";
    try {
      const { result, info } = runCipher(cipher, src, key, op);
      $("out").value = result;
      if (info) $("matrix").textContent = info;
      if (op === "encrypt") { lastPlain = src; lastCipher = result; }
      status((op === "encrypt" ? "[+] encrypted with " : "[+] decrypted with ") + cipher);
    } catch (e) { showErr(e.message); }
  }
  $("encBtn").onclick = () => call("encrypt");
  $("decBtn").onclick = () => call("decrypt");
  $("swapBtn").onclick = () => { if ($("out").value.trim() !== "") { $("inp").value = $("out").value; status("[+] output moved to input — now decrypt to reverse."); } };
  $("clrBtn").onclick = () => { $("inp").value = ""; $("out").value = ""; };
  $("copyBtn").onclick = () => { navigator.clipboard.writeText($("out").value); status("[+] copied to clipboard."); };
  $("genBtn").onclick = () => {
    if (cipherSel.value === "Monoalphabetic Cipher") { $("key").value = generateMonoKey(); status("[+] random key generated."); }
    else if (cipherSel.value === "One-Time Pad") {
      const n = [...$("inp").value].filter((c) => /[A-Za-z]/.test(c)).length || 10;
      $("key").value = generateOtpKey(n); status("[+] secure OTP key generated (" + Math.max(1, n) + " chars).");
    }
  };
  $("benchBtn").onclick = () => {
    const text = $("benchIn").value;
    if (!text.trim()) { showErr("Enter benchmark plaintext first."); return; }
    const rows = benchmarkAll(text);
    $("benchBody").innerHTML = rows.map((x) =>
      `<tr><td>${x.name}</td><td>${x.type}</td><td>${x.enc.toFixed(4)}</td><td>${x.dec.toFixed(4)}</td><td>${x.status}</td><td>${(x.sample || "").slice(0, 28)}</td></tr>`).join("");
    status("[+] benchmarked " + rows.length + " ciphers.");
  };

  const hl = $("helpList");
  Object.keys(HELP).forEach((k, i) => {
    const b = document.createElement("button");
    b.className = "helpbtn" + (i === 0 ? " active" : "");
    b.textContent = k;
    b.onclick = () => {
      document.querySelectorAll(".helpbtn").forEach((x) => x.classList.remove("active"));
      b.classList.add("active");
      $("helpTitle").textContent = k;
      $("helpBody").textContent = HELP[k];
    };
    hl.appendChild(b);
  });
  $("helpTitle").textContent = Object.keys(HELP)[0];
  $("helpBody").textContent = HELP[Object.keys(HELP)[0]];

  // theme
  function applyTheme(t) {
    document.documentElement.dataset.theme = t;
    $("themeBtn").textContent = t === "light" ? "dark mode" : "light mode";
    try { localStorage.setItem("cryptokit-theme", t); } catch (e) {}
  }
  $("themeBtn").onclick = () => applyTheme(document.documentElement.dataset.theme === "light" ? "dark" : "light");
  try { applyTheme(localStorage.getItem("cryptokit-theme") || "dark"); } catch (e) { applyTheme("dark"); }

  setCipher("Caesar Cipher");
})();
