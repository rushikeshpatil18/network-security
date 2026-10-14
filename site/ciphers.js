/* Classical Cryptography Toolkit — pure cipher logic (no DOM).
 * Faithful JS port of algorithms/*.py. All ciphers throw Error on bad keys.
 */
"use strict";

const mod26 = (x) => ((x % 26) + 26) % 26;
const isAlpha = (c) => /[A-Za-z]/.test(c);
const gcd = (a, b) => (b === 0 ? Math.abs(a) : gcd(b, a % b));

/* ---------------- Caesar ---------------- */
function caesarEncrypt(text, shift) {
  shift = mod26(Number(shift));
  let out = "";
  for (const ch of text) {
    if (ch >= "A" && ch <= "Z") out += String.fromCharCode(mod26(ch.charCodeAt(0) - 65 + shift) + 65);
    else if (ch >= "a" && ch <= "z") out += String.fromCharCode(mod26(ch.charCodeAt(0) - 97 + shift) + 97);
    else out += ch;
  }
  return out;
}
const caesarDecrypt = (text, shift) => caesarEncrypt(text, -Number(shift));

/* ---------------- Monoalphabetic ---------------- */
const ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZ";
function generateMonoKey() {
  const arr = ALPHABET.split("");
  const rnd = new Uint32Array(arr.length);
  crypto.getRandomValues(rnd);
  for (let i = arr.length - 1; i > 0; i--) {
    const j = rnd[i] % (i + 1);
    [arr[i], arr[j]] = [arr[j], arr[i]];
  }
  return arr.join("");
}
function monoEncrypt(text, key) {
  key = key.toUpperCase();
  const m = {};
  for (let i = 0; i < 26; i++) {
    m[ALPHABET[i]] = key[i];
    m[ALPHABET[i].toLowerCase()] = key[i].toLowerCase();
  }
  return [...text].map((c) => m[c] ?? c).join("");
}
function monoDecrypt(text, key) {
  key = key.toUpperCase();
  const m = {};
  for (let i = 0; i < 26; i++) {
    m[key[i]] = ALPHABET[i];
    m[key[i].toLowerCase()] = ALPHABET[i].toLowerCase();
  }
  return [...text].map((c) => m[c] ?? c).join("");
}

/* ---------------- Playfair ---------------- */
function playfairMatrix(keyword) {
  const seen = new Set();
  const clean = [];
  for (const raw of keyword.toUpperCase()) {
    if (/[A-Z]/.test(raw)) {
      const c = raw === "J" ? "I" : raw;
      if (!seen.has(c)) { seen.add(c); clean.push(c); }
    }
  }
  for (const c of "ABCDEFGHIKLMNOPQRSTUVWXYZ") {
    if (!seen.has(c)) { seen.add(c); clean.push(c); }
  }
  return [clean.slice(0, 5), clean.slice(5, 10), clean.slice(10, 15), clean.slice(15, 20), clean.slice(20, 25)];
}
function playfairPos(matrix, ch) {
  const c = ch === "J" ? "I" : ch;
  for (let r = 0; r < 5; r++)
    for (let col = 0; col < 5; col++)
      if (matrix[r][col] === c) return [r, col];
  return [0, 0];
}
function playfairPrepare(text) {
  const letters = [...text.toUpperCase()].filter((c) => /[A-Z]/.test(c)).map((c) => (c === "J" ? "I" : c));
  const digrams = [];
  let i = 0;
  while (i < letters.length) {
    const first = letters[i];
    if (i + 1 < letters.length) {
      const second = letters[i + 1];
      if (first === second) {
        digrams.push([first, first === "X" ? "Q" : "X"]);
        i += 1;
      } else {
        digrams.push([first, second]);
        i += 2;
      }
    } else {
      digrams.push([first, first === "X" ? "Z" : "X"]);
      i += 1;
    }
  }
  return digrams;
}
function playfairEncrypt(text, keyword) {
  const m = playfairMatrix(keyword);
  let out = "";
  for (const [c1, c2] of playfairPrepare(text)) {
    const [r1, k1] = playfairPos(m, c1);
    const [r2, k2] = playfairPos(m, c2);
    if (r1 === r2) out += m[r1][(k1 + 1) % 5] + m[r2][(k2 + 1) % 5];
    else if (k1 === k2) out += m[(r1 + 1) % 5][k1] + m[(r2 + 1) % 5][k2];
    else out += m[r1][k2] + m[r2][k1];
  }
  return out;
}
function playfairDecrypt(text, keyword) {
  const m = playfairMatrix(keyword);
  const letters = [...text.toUpperCase()].filter((c) => /[A-Z]/.test(c)).map((c) => (c === "J" ? "I" : c));
  let out = "";
  for (let i = 0; i < letters.length; i += 2) {
    if (i + 1 < letters.length) {
      const [r1, k1] = playfairPos(m, letters[i]);
      const [r2, k2] = playfairPos(m, letters[i + 1]);
      if (r1 === r2) out += m[r1][(k1 + 4) % 5] + m[r2][(k2 + 4) % 5];
      else if (k1 === k2) out += m[(r1 + 4) % 5][k1] + m[(r2 + 4) % 5][k2];
      else out += m[r1][k2] + m[r2][k1];
    } else out += letters[i];
  }
  return out;
}

/* ---------------- Hill (2x2) ---------------- */
function modInv26(a) {
  a = mod26(a);
  for (let x = 1; x < 26; x++) if ((a * x) % 26 === 1) return x;
  throw new Error("Determinant has no inverse mod 26. Matrix is not invertible.");
}
function parseHillKey(input) {
  const s = String(input).trim();
  const nums = s.match(/-?\d+/g) || [];
  let m;
  if (nums.length === 4) {
    const v = nums.map((n) => mod26(parseInt(n, 10)));
    m = [[v[0], v[1]], [v[2], v[3]]];
  } else {
    const letters = [...s].filter((c) => /[A-Za-z]/.test(c)).map((c) => c.toUpperCase());
    if (letters.length !== 4) throw new Error("Hill key must be exactly 4 letters or 4 numbers (e.g., 'HILL' or '3 3 2 5').");
    const v = letters.map((c) => c.charCodeAt(0) - 65);
    m = [[v[0], v[1]], [v[2], v[3]]];
  }
  const det = mod26(m[0][0] * m[1][1] - m[0][1] * m[1][0]);
  if (gcd(det, 26) !== 1) throw new Error("Determinant has no inverse mod 26. Matrix is not invertible.");
  return m;
}
function hillInverse(m) {
  const detInv = modInv26(mod26(m[0][0] * m[1][1] - m[0][1] * m[1][0]));
  return [
    [mod26(m[1][1] * detInv), mod26(-m[0][1] * detInv)],
    [mod26(-m[1][0] * detInv), mod26(m[0][0] * detInv)],
  ];
}
function hillCrypt(text, keyInput, encrypt) {
  const m = encrypt ? parseHillKey(keyInput) : hillInverse(parseHillKey(keyInput));
  const letters = [], positions = [], cases = [];
  [...text].forEach((ch, idx) => {
    if (isAlpha(ch)) { letters.push(ch.toUpperCase().charCodeAt(0) - 65); positions.push(idx); cases.push(ch === ch.toUpperCase()); }
  });
  if (letters.length % 2 !== 0) { letters.push(23); positions.push(text.length); cases.push(true); }
  const vals = [];
  for (let i = 0; i < letters.length; i += 2) {
    vals.push(mod26(m[0][0] * letters[i] + m[0][1] * letters[i + 1]));
    vals.push(mod26(m[1][0] * letters[i] + m[1][1] * letters[i + 1]));
  }
  const res = [...text];
  if (positions.length > res.length) res.push("X");
  positions.forEach((pos, i) => {
    const ch = String.fromCharCode(vals[i] + (cases[i] ? 65 : 97));
    if (pos < res.length) res[pos] = ch; else res.push(ch);
  });
  return res.join("");
}
const hillEncrypt = (t, k) => hillCrypt(t, k, true);
const hillDecrypt = (t, k) => hillCrypt(t, k, false);

/* ---------------- Vigenere ---------------- */
function vigenereKey(keyword) {
  const k = [...keyword].filter((c) => /[A-Za-z]/.test(c)).map((c) => c.toUpperCase());
  if (!k.length) throw new Error("Keyword must contain alphabetic characters.");
  return k;
}
function vigenereEncrypt(text, keyword) {
  const k = vigenereKey(keyword);
  let j = 0, out = "";
  for (const ch of text) {
    if (ch >= "A" && ch <= "Z") { out += String.fromCharCode(mod26(ch.charCodeAt(0) - 65 + (k[j++ % k.length].charCodeAt(0) - 65)) + 65); }
    else if (ch >= "a" && ch <= "z") { out += String.fromCharCode(mod26(ch.charCodeAt(0) - 97 + (k[j++ % k.length].charCodeAt(0) - 65)) + 97); }
    else out += ch;
  }
  return out;
}
function vigenereDecrypt(text, keyword) {
  const k = vigenereKey(keyword);
  let j = 0, out = "";
  for (const ch of text) {
    if (ch >= "A" && ch <= "Z") { out += String.fromCharCode(mod26(ch.charCodeAt(0) - 65 - (k[j++ % k.length].charCodeAt(0) - 65)) + 65); }
    else if (ch >= "a" && ch <= "z") { out += String.fromCharCode(mod26(ch.charCodeAt(0) - 97 - (k[j++ % k.length].charCodeAt(0) - 65)) + 97); }
    else out += ch;
  }
  return out;
}

/* ---------------- OTP ---------------- */
function generateOtpKey(length) {
  length = Math.max(1, length);
  const rnd = new Uint32Array(length);
  crypto.getRandomValues(rnd);
  return [...rnd].map((n) => String.fromCharCode(65 + (n % 26))).join("");
}
function otpCrypt(text, key, encrypt) {
  const kl = [...key].filter((c) => /[A-Za-z]/.test(c)).map((c) => c.toUpperCase());
  const count = [...text].filter(isAlpha).length;
  if (kl.length < count) throw new Error(encrypt ? "Key length shorter than plaintext." : "Key length shorter than ciphertext.");
  let j = 0, out = "";
  for (const ch of text) {
    const s = kl[j];
    if (ch >= "A" && ch <= "Z") { out += String.fromCharCode(mod26(ch.charCodeAt(0) - 65 + (encrypt ? 1 : -1) * (s.charCodeAt(0) - 65)) + 65); j++; }
    else if (ch >= "a" && ch <= "z") { out += String.fromCharCode(mod26(ch.charCodeAt(0) - 97 + (encrypt ? 1 : -1) * (s.charCodeAt(0) - 65)) + 97); j++; }
    else out += ch;
  }
  return out;
}
const otpEncrypt = (t, k) => otpCrypt(t, k, true);
const otpDecrypt = (t, k) => otpCrypt(t, k, false);

/* ---------------- Rail Fence ---------------- */
function railEncrypt(text, rails) {
  rails = Number(rails);
  if (!Number.isInteger(rails) || rails < 2) throw new Error("Number of rails must be an integer >= 2.");
  if (text.length <= rails) return text;
  const fence = Array.from({ length: rails }, () => []);
  let r = 0, step = 1;
  for (const ch of text) {
    fence[r].push(ch);
    r += step;
    if (r === 0 || r === rails - 1) step = -step;
  }
  return fence.map((row) => row.join("")).join("");
}
function railDecrypt(text, rails) {
  rails = Number(rails);
  if (!Number.isInteger(rails) || rails < 2) throw new Error("Number of rails must be an integer >= 2.");
  if (text.length <= rails) return text;
  const idx = [];
  let r = 0, step = 1;
  for (let i = 0; i < text.length; i++) {
    idx.push(r);
    r += step;
    if (r === 0 || r === rails - 1) step = -step;
  }
  const counts = Array.from({ length: rails }, (_, k) => idx.filter((v) => v === k).length);
  const slices = [];
  let p = 0;
  for (const c of counts) { slices.push([...text.slice(p, p + c)]); p += c; }
  const ptrs = new Array(rails).fill(0);
  return idx.map((k) => slices[k][ptrs[k]++]).join("");
}

/* ---------------- Columnar ---------------- */
function columnarClean(keyword) {
  const k = [...keyword].filter((c) => /[A-Za-z]/.test(c)).map((c) => c.toUpperCase());
  if (!k.length) throw new Error("Keyword must contain alphabetic characters.");
  return k;
}
function columnarOrder(k) {
  return [...k.keys()].sort((a, b) => (k[a] < k[b] ? -1 : k[a] > k[b] ? 1 : a - b));
}
function getColumnOrder(keyword) {
  const k = columnarClean(keyword);
  const order = [...k.keys()].sort((a, b) => (k[a] < k[b] ? -1 : k[a] > k[b] ? 1 : a - b));
  const ranks = new Array(k.length);
  order.forEach((idx, rank) => { ranks[idx] = rank + 1; });
  return ranks;
}
function columnarEncrypt(text, keyword) {
  const k = columnarClean(keyword);
  const w = k.length, n = text.length;
  if (!n) return text;
  const h = Math.ceil(n / w);
  const order = columnarOrder(k);
  let out = "";
  for (const col of order)
    for (let row = 0; row < h; row++) {
      const i = row * w + col;
      if (i < n) out += text[i];
    }
  return out;
}
function columnarDecrypt(text, keyword) {
  const k = columnarClean(keyword);
  const w = k.length, n = text.length;
  if (!n) return text;
  const h = Math.ceil(n / w);
  let last = n % w;
  if (last === 0) last = w;
  const lens = Array.from({ length: w }, (_, c) => (c < last ? h : h - 1));
  const order = columnarOrder(k);
  const grid = {};
  let p = 0;
  for (const col of order) { grid[col] = [...text.slice(p, p + lens[col])]; p += lens[col]; }
  let out = "";
  for (let row = 0; row < h; row++)
    for (let col = 0; col < w; col++)
      if (row < grid[col].length) out += grid[col][row];
  return out;
}

/* ---------------- validation + dispatch (mirrors utils/validator.py) ---------------- */
function validateInput(cipher, text, key) {
  if (text == null || String(text).length === 0) throw new Error("Input text cannot be empty.");
  const k = String(key ?? "").trim();
  switch (cipher) {
    case "Caesar Cipher":
      if (!/^-?\d+$/.test(k)) throw new Error(`Shift key must be an integer (e.g. 5). Got '${key || ""}'.`);
      break;
    case "Monoalphabetic Cipher": {
      const clean = [...k].filter((c) => /[A-Za-z]/.test(c)).map((c) => c.toUpperCase());
      if (k.length !== 26 || clean.length !== 26 || new Set(clean).size !== 26)
        throw new Error("Key must contain 26 unique alphabetic characters (A-Z permutation).");
      break;
    }
    case "Playfair Cipher":
    case "Vigenère Cipher":
    case "Columnar Transposition Cipher":
      if (![...k].some((c) => /[A-Za-z]/.test(c))) throw new Error("Keyword must contain alphabetic characters.");
      break;
    case "Hill Cipher":
      parseHillKey(k);
      break;
    case "One-Time Pad": {
      const kl = [...k].filter((c) => /[A-Za-z]/.test(c)).length;
      const pl = [...String(text)].filter(isAlpha).length;
      if (kl < pl) throw new Error("Key length shorter than plaintext.");
      break;
    }
    case "Rail Fence Cipher":
      if (!/^-?\d+$/.test(k) || parseInt(k, 10) < 2) throw new Error(`Number of rails must be an integer >= 2 (e.g. 3). Got '${key}'.`);
      break;
  }
}

function runCipher(cipher, text, key, mode) {
  const enc = mode === "encrypt";
  validateInput(cipher, text, key);
  const k = String(key).trim();
  switch (cipher) {
    case "Caesar Cipher": return { result: enc ? caesarEncrypt(text, parseInt(k, 10)) : caesarDecrypt(text, parseInt(k, 10)), info: "" };
    case "Monoalphabetic Cipher": return { result: enc ? monoEncrypt(text, k) : monoDecrypt(text, k), info: "" };
    case "Playfair Cipher": {
      const m = playfairMatrix(k);
      return { result: enc ? playfairEncrypt(text, k) : playfairDecrypt(text, k), info: enc ? "Playfair 5x5 · " + m.map((r) => r.join(" ")).join(" / ") : "" };
    }
    case "Hill Cipher": {
      const m = parseHillKey(k);
      return { result: enc ? hillEncrypt(text, k) : hillDecrypt(text, k), info: enc ? `Hill 2x2 · [ ${m[0][0]} ${m[0][1]} ] [ ${m[1][0]} ${m[1][1]} ]` : "" };
    }
    case "Vigenère Cipher": return { result: enc ? vigenereEncrypt(text, k) : vigenereDecrypt(text, k), info: "" };
    case "One-Time Pad": return { result: enc ? otpEncrypt(text, k) : otpDecrypt(text, k), info: "" };
    case "Rail Fence Cipher": return { result: enc ? railEncrypt(text, parseInt(k, 10)) : railDecrypt(text, parseInt(k, 10)), info: "" };
    case "Columnar Transposition Cipher":
      return { result: enc ? columnarEncrypt(text, k) : columnarDecrypt(text, k), info: enc ? "Column order: " + JSON.stringify(getColumnOrder(k)) : "" };
    default: throw new Error("Unknown cipher");
  }
}

function benchmarkAll(text) {
  const alpha = [...text].filter(isAlpha).length;
  const otpKey = generateOtpKey(Math.max(10, alpha));
  const jobs = [
    ["Caesar Cipher", "Substitution", (t) => caesarEncrypt(t, 5), (c) => caesarDecrypt(c, 5)],
    ["Monoalphabetic Cipher", "Substitution", (t) => monoEncrypt(t, "QWERTYUIOPASDFGHJKLZXCVBNM"), (c) => monoDecrypt(c, "QWERTYUIOPASDFGHJKLZXCVBNM")],
    ["Playfair Cipher", "Substitution", (t) => playfairEncrypt(t, "MONARCHY"), (c) => playfairDecrypt(c, "MONARCHY")],
    ["Hill Cipher", "Substitution", (t) => hillEncrypt(t, "3 3 2 5"), (c) => hillDecrypt(c, "3 3 2 5")],
    ["Vigenère Cipher", "Substitution", (t) => vigenereEncrypt(t, "KEYWORD"), (c) => vigenereDecrypt(c, "KEYWORD")],
    ["One-Time Pad", "Substitution", (t) => otpEncrypt(t, otpKey), (c) => otpDecrypt(c, otpKey)],
    ["Rail Fence Cipher", "Transposition", (t) => railEncrypt(t, 3), (c) => railDecrypt(c, 3)],
    ["Columnar Transposition Cipher", "Transposition", (t) => columnarEncrypt(t, "GERMAN"), (c) => columnarDecrypt(c, "GERMAN")],
  ];
  return jobs.map(([name, type, ef, df]) => {
    try {
      const t0 = performance.now();
      const ct = ef(text);
      const enc = performance.now() - t0;
      const t1 = performance.now();
      df(ct);
      const dec = performance.now() - t1;
      return { name, type, enc, dec, status: "PASS", sample: ct };
    } catch (e) {
      return { name, type, enc: 0, dec: 0, status: "ERROR", sample: "" };
    }
  });
}

// node test hook (browser ignores)
if (typeof module !== "undefined") {
  module.exports = { caesarEncrypt, caesarDecrypt, monoEncrypt, monoDecrypt, generateMonoKey, playfairMatrix, playfairEncrypt, playfairDecrypt, parseHillKey, hillEncrypt, hillDecrypt, vigenereEncrypt, vigenereDecrypt, generateOtpKey, otpEncrypt, otpDecrypt, railEncrypt, railDecrypt, getColumnOrder, columnarEncrypt, columnarDecrypt, validateInput, runCipher, benchmarkAll };
}
