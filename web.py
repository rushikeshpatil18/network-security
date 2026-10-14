"""Web UI for Classical Cryptography Toolkit (stdlib only).
Run: python3 web.py [--port 8080]
Serves a dark cyber-terminal single-page site + JSON API reusing algorithms/.
"""
import json
import sys
import urllib.parse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from algorithms.caesar import caesar_encrypt, caesar_decrypt
from algorithms.monoalphabetic import monoalphabetic_encrypt, monoalphabetic_decrypt, generate_monoalphabetic_key
from algorithms.playfair import playfair_encrypt, playfair_decrypt, generate_playfair_matrix
from algorithms.hill import hill_encrypt, hill_decrypt, parse_hill_key
from algorithms.vigenere import vigenere_encrypt, vigenere_decrypt
from algorithms.otp import otp_encrypt, otp_decrypt, generate_otp_key
from algorithms.rail_fence import rail_fence_encrypt, rail_fence_decrypt
from algorithms.columnar import columnar_encrypt, columnar_decrypt, get_column_order
from utils.validator import validate_cipher_input
from utils.benchmark import benchmark_algorithms

CIPHERS = [
    ("Caesar Cipher", "SHIFT", "5"),
    ("Monoalphabetic Cipher", "SUBSTITUTION", "QWERTYUIOPASDFGHJKLZXCVBNM"),
    ("Playfair Cipher", "DIGRAM 5x5", "MONARCHY"),
    ("Hill Cipher", "MATRIX 2x2", "HILL"),
    ("Vigenère Cipher", "POLYALPHA", "SECRETKEY"),
    ("One-Time Pad", "UNBREAKABLE", "SECRETKEYWORDOK"),
    ("Rail Fence Cipher", "ZIGZAG", "3"),
    ("Columnar Transposition Cipher", "COLUMNAR", "GERMAN"),
]
HINTS = {
    "Caesar Cipher": "Integer shift (e.g. 5)",
    "Monoalphabetic Cipher": "26 unique letters A-Z",
    "Playfair Cipher": "Keyword (e.g. MONARCHY)",
    "Hill Cipher": "4 letters (HILL) or 4 numbers (3 3 2 5)",
    "Vigenère Cipher": "Keyword (e.g. SECRETKEY)",
    "One-Time Pad": "Key length >= plaintext letters",
    "Rail Fence Cipher": "Rails integer >= 2",
    "Columnar Transposition Cipher": "Keyword (e.g. GERMAN)",
}

def do_cipher(cipher, text, key, mode):
    key = str(key).strip() if key is not None else ""
    if cipher == "Caesar Cipher" and key == "":
        key = "5"
    validate_cipher_input(cipher, text, key)
    enc = mode == "encrypt"
    if cipher == "Caesar Cipher":
        return (caesar_encrypt if enc else caesar_decrypt)(text, int(key.strip())), ""
    if cipher == "Monoalphabetic Cipher":
        return (monoalphabetic_encrypt if enc else monoalphabetic_decrypt)(text, key), ""
    if cipher == "Playfair Cipher":
        r = (playfair_encrypt if enc else playfair_decrypt)(text, key)
        m = generate_playfair_matrix(key)
        info = "Playfair 5x5 · " + " / ".join(" ".join(row) for row in m)
        return r, info
    if cipher == "Hill Cipher":
        r = (hill_encrypt if enc else hill_decrypt)(text, key)
        mx = parse_hill_key(key)
        return r, f"Hill 2x2 · [{mx[0][0]:2d} {mx[0][1]:2d}] [{mx[1][0]:2d} {mx[1][1]:2d}]"
    if cipher == "Vigenère Cipher":
        return (vigenere_encrypt if enc else vigenere_decrypt)(text, key), ""
    if cipher == "One-Time Pad":
        return (otp_encrypt if enc else otp_decrypt)(text, key), ""
    if cipher == "Rail Fence Cipher":
        return (rail_fence_encrypt if enc else rail_fence_decrypt)(text, int(key.strip())), ""
    if cipher == "Columnar Transposition Cipher":
        r = (columnar_encrypt if enc else columnar_decrypt)(text, key)
        return r, f"Column order: {get_column_order(key)}"
    raise ValueError("Unknown cipher")

PAGE = """<!DOCTYPE html><html lang="en"><head><meta charset="utf-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>CryptoKit — Classical Cryptography Toolkit</title>
<style>
:root{--bg:#040705;--panel:#080F0A;--panel2:#0C160E;--grn:#00FF41;--dim:#1E6B32;--txt:#C9FFD6;--mut:#5F8F6A;--amb:#FFB000;--red:#FF3131}
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:'Courier New',Consolas,monospace;background:var(--bg);color:var(--txt);display:flex;min-height:100vh;text-shadow:0 0 6px rgba(0,255,65,.35)}
body::after{content:"";position:fixed;inset:0;pointer-events:none;background:repeating-linear-gradient(0deg,rgba(0,0,0,.25) 0 1px,transparent 1px 3px);z-index:99}
aside{width:260px;background:#060C08;border-right:1px solid var(--dim);padding:22px 0;display:flex;flex-direction:column;position:sticky;top:0;height:100vh;z-index:1}
.brand{padding:0 20px 14px}.brand h1{font-size:17px;letter-spacing:1px;color:var(--grn)}.brand h1 .cur{animation:blink 1s steps(1) infinite}.brand p{color:var(--mut);font-size:12px;margin-top:6px}
@keyframes blink{50%{opacity:0}}
.div{height:1px;background:var(--dim);margin:12px 20px;box-shadow:0 0 8px rgba(0,255,65,.4)}
.navlabel{font-size:10px;color:var(--mut);padding:0 20px 8px;letter-spacing:2px;font-weight:700}
.navbtn{display:block;width:100%;text-align:left;background:transparent;border:0;border-left:3px solid transparent;color:var(--txt);font-family:inherit;font-size:14px;padding:11px 20px;cursor:pointer;text-shadow:inherit}
.navbtn:hover{background:var(--panel2)}.navbtn.active{background:var(--panel2);border-left-color:var(--grn);color:var(--grn);font-weight:700}
aside select{margin:0 20px;padding:8px;width:calc(100% - 40px);background:#000;border:1px solid var(--dim);color:var(--grn);font-family:inherit}
.foot{margin-top:auto;padding:14px 20px;color:var(--mut);font-size:11px;line-height:1.6}
main{flex:1;min-width:0;z-index:1}
.top{background:var(--panel);border-bottom:1px solid var(--dim);padding:14px 26px;display:flex;align-items:center;gap:12px}
.top h2{font-size:17px;color:var(--grn)}.top small{color:var(--mut);display:block;font-size:12px;font-weight:400;margin-top:3px}
.badge{margin-left:auto;background:#000;border:1px solid var(--grn);color:var(--grn);font-size:11px;font-weight:700;padding:6px 12px;border-radius:3px;box-shadow:0 0 10px rgba(0,255,65,.35);white-space:nowrap}
.status{padding:10px 26px 0;color:var(--grn);font-size:12px}
section{padding:14px 26px 30px;display:none}section.active{display:block}
.card{background:var(--panel);border:1px solid var(--dim);border-radius:4px;padding:18px;margin-bottom:14px;box-shadow:0 0 18px rgba(0,255,65,.07)}
.card h3{font-size:14px;margin-bottom:4px;color:var(--grn)}.card h3::before{content:"> ";color:var(--dim)}.card .sub{color:var(--mut);font-size:12px;margin-bottom:12px}
.grid2{display:grid;grid-template-columns:1fr 1fr;gap:14px}@media(max-width:900px){.grid2{grid-template-columns:1fr}aside{display:none}}
label.lbl{font-size:11px;font-weight:700;color:var(--mut);display:block;margin:10px 0 6px;letter-spacing:1px}
select,input[type=text]{width:100%;padding:10px 12px;border:1px solid var(--dim);border-radius:3px;background:#000;color:var(--grn);font-size:14px;font-family:inherit;text-shadow:inherit}
select:focus,input[type=text]:focus,textarea:focus{outline:none;border-color:var(--grn);box-shadow:0 0 12px rgba(0,255,65,.35)}
textarea{width:100%;border:1px solid var(--dim);border-radius:3px;background:#000;color:var(--txt);padding:12px;font-family:inherit;font-size:14px;min-height:130px;resize:vertical;text-shadow:inherit}
textarea.dark{background:#000;color:var(--grn);border-color:var(--grn)}
.row{display:flex;gap:10px;flex-wrap:wrap;margin-top:12px}
button.btn{border-radius:3px;padding:11px 18px;font-weight:700;font-size:13px;cursor:pointer;font-family:inherit}
.btn-p{background:var(--grn);color:#000;border:1px solid var(--grn);box-shadow:0 0 14px rgba(0,255,65,.5);text-shadow:none}
.btn-d{background:#000;color:var(--amb);border:1px solid var(--amb)}
.btn-g{background:#000;color:var(--grn);border:1px solid var(--dim)}
.btn-g:hover,.btn-d:hover{border-color:var(--grn)}
.btn-p:hover{background:#4DFF7A}
.pill{background:#000;border:1px dashed var(--dim);color:var(--txt);border-radius:3px;padding:10px 12px;font-size:12px;margin-top:12px;word-break:break-word}
table{width:100%;border-collapse:collapse;font-size:13px;background:#000}
th{background:var(--panel2);color:var(--grn);text-align:left;padding:10px;border-bottom:1px solid var(--grn)}td{padding:9px 10px;border-top:1px solid var(--panel2);color:var(--txt)}
.err{background:#1A0505;border:1px solid var(--red);color:#FF8080;border-radius:3px;padding:10px 12px;font-size:13px;margin-top:12px;display:none;text-shadow:none}
.helpgrid{display:grid;grid-template-columns:240px 1fr;gap:14px}@media(max-width:900px){.helpgrid{grid-template-columns:1fr}}
.helpbtn{display:block;width:100%;text-align:left;background:#000;border:1px solid var(--dim);color:var(--txt);border-radius:3px;padding:9px 10px;margin-bottom:6px;cursor:pointer;font-size:13px;font-family:inherit}
.helpbtn.active{background:var(--panel2);color:var(--grn);border-color:var(--grn)}
pre{white-space:pre-wrap;font-size:13px;line-height:1.55;color:var(--txt)}
/* ---- light theme (toggle) ---- */
body.light{--bg:#F4F7F5;--panel:#FFFFFF;--panel2:#E9F2EC;--grn:#047857;--dim:#C4DCCF;--txt:#14261C;--mut:#64816F;--amb:#92400E;text-shadow:none}
body.light::after{display:none}
body.light aside{background:#FFFFFF;border-right:1px solid #D9E5DD}
body.light .brand h1{color:#047857}
body.light .brand p,body.light .foot,body.light .navlabel{color:#64816F}
body.light .div{background:#D9E5DD;box-shadow:none}
body.light .navbtn{color:#1A2E22;text-shadow:none}
body.light .navbtn:hover{background:#EDF4EF}
body.light .navbtn.active{background:#D7F0E1;color:#047857;border-left-color:#047857}
body.light aside select{background:#F2F7F4;border-color:#CBE0D4;color:#14261C}
body.light .top{background:#FFFFFF;border-bottom:1px solid #D9E5DD}
body.light .top h2{color:#14261C}
body.light .top small{color:#64816F}
body.light .badge{background:#047857;border-color:#047857;color:#fff;box-shadow:none}
body.light .status{color:#047857}
body.light .card{background:#fff;border-color:#D9E5DD;box-shadow:0 1px 4px rgba(20,38,28,.07)}
body.light .card h3{color:#14261C}
body.light .card .sub{color:#64816F}
body.light select,body.light input[type=text]{background:#F7FAF8;border-color:#CBE0D4;color:#14261C;text-shadow:none}
body.light textarea{background:#F7FAF8;border-color:#CBE0D4;color:#14261C;text-shadow:none}
body.light textarea.dark{background:#0B1F14;color:#4DFF9A;border-color:#0B1F14}
body.light .btn-p{background:#047857;border-color:#047857;box-shadow:none}
body.light .btn-d{background:#fff;color:#92400E;border-color:#E8B25C}
body.light .btn-g{background:#fff;color:#14261C;border-color:#CBE0D4}
body.light .pill{background:#F2F7F4;border-color:#CBE0D4;color:#1A2E22}
body.light table{background:#fff}
body.light th{background:#E9F2EC;color:#047857;border-bottom-color:#047857}
body.light td{color:#1A2E22;border-top-color:#E9F2EC}
body.light .helpbtn{background:#F7FAF8;border-color:#CBE0D4;color:#1A2E22}
body.light .helpbtn.active{background:#D7F0E1;color:#047857;border-color:#047857}
body.light pre{color:#1A2E22}
#themeBtn{padding:6px 12px;font-size:12px;white-space:nowrap}
</style></head><body>
<aside><div class="brand"><h1>CRYPT0_KIT<span class="cur">_</span></h1><p>// classical cipher terminal<br/>// NS mini-project v1.0</p></div>
<div class="div"></div><div class="navlabel">[+] MODULES</div>
<button class="navbtn active" data-p="dashboard">[1] cipher.exe</button>
<button class="navbtn" data-p="compare">[2] benchmark.exe</button>
<button class="navbtn" data-p="help">[3] manual.txt</button>
<div class="div"></div><div class="navlabel">[+] PAYLOAD</div>
<select id="sideCipher"></select>
<div class="foot">8 ciphers loaded<br/>session-only // no logs kept<br/>status: <span style="color:#00FF41">ONLINE</span></div></aside>
<main>
<div class="top"><div><h2 id="pageTitle">root@crypter:~$ cipher.exe</h2><small id="pageSub">encrypt // decrypt // live key visuals</small></div><span class="badge" id="badge">SHIFT</span><button class="btn btn-g" id="themeBtn" title="Toggle dark / light theme">light mode</button></div>
<div class="status" id="status">[+] uplink established — select cipher module.</div>
<section id="dashboard" class="active">
<div class="card"><h3>cipher configuration</h3><div class="sub">choose algorithm + key. [generate] works for monoalphabetic + otp.</div>
<div class="grid2"><div><label class="lbl">SELECT CIPHER</label><select id="cipher"></select></div>
<div><label class="lbl" id="keyHint">KEY</label><div style="display:flex;gap:8px"><input type="text" id="key" value="5"/><button class="btn btn-g" id="genBtn" disabled>gen_key</button></div></div></div></div>
<div class="grid2"><div class="card"><h3>stdin — plaintext</h3><textarea id="inp">NETWORK SECURITY</textarea></div>
<div class="card"><h3>stdout — result</h3><textarea id="out" class="dark" readonly placeholder="awaiting output…"></textarea></div></div>
<div class="card"><div class="row"><button class="btn btn-p" id="encBtn">[run] encrypt</button><button class="btn btn-d" id="decBtn">[run] decrypt</button><button class="btn btn-g" id="swapBtn" title="Move output back to input for round-trip">out-&gt;in</button><button class="btn btn-g" id="clrBtn">clear</button><button class="btn btn-g" id="copyBtn">copy</button></div>
<div class="pill" id="matrix">Key visual will appear here for Playfair / Hill</div><div class="err" id="err"></div></div>
</section>
<section id="compare"><div class="card"><h3>benchmark input</h3><textarea id="benchIn">THE QUICK BROWN FOX JUMPS OVER THE LAZY DOG 12345</textarea>
<div class="row"><button class="btn btn-p" id="benchBtn">[run] benchmark all</button></div></div>
<div class="card"><table><thead><tr><th>Algorithm</th><th>Type</th><th>Enc (ms)</th><th>Dec (ms)</th><th>Status</th><th>Sample</th></tr></thead><tbody id="benchBody"><tr><td colspan="6">press run…</td></tr></tbody></table>
<div class="pill">Speed != security — fast Caesar is trivially breakable; OTP is theoretically unbreakable.</div></div></section>
<section id="help"><div class="helpgrid"><div class="card"><h3>topics</h3><div id="helpList"></div></div>
<div class="card"><h3 id="helpTitle">manual</h3><pre id="helpBody"></pre></div></div></section>
</main>
<script>
const CIPHERS=__CIPHERS__, HINTS=__HINTS__, HELP=__HELP__;
const $=id=>document.getElementById(id);
const cipherSel=$('cipher'),sideSel=$('sideCipher');
CIPHERS.forEach(([name,badge,def])=>{const o=document.createElement('option');o.value=name;o.textContent=name;cipherSel.appendChild(o);const s=document.createElement('option');s.value=name;s.textContent=name;sideSel.appendChild(s);});
cipherSel.value='Caesar Cipher';sideSel.value='Caesar Cipher';
const META=Object.fromEntries(CIPHERS.map(([name,badge,def])=>[name,{badge,def}]));
function setCipher(n){cipherSel.value=n;sideSel.value=n;$('badge').textContent=META[n].badge;$('keyHint').textContent='KEY — '+HINTS[n];$('key').value=META[n].def;$('genBtn').disabled=!(n==='Monoalphabetic Cipher'||n==='One-Time Pad');$('matrix').textContent='Key visual will appear here for Playfair / Hill';show('dashboard');}
cipherSel.onchange=()=>setCipher(cipherSel.value);sideSel.onchange=()=>setCipher(sideSel.value);
document.querySelectorAll('.navbtn').forEach(b=>b.onclick=()=>show(b.dataset.p));
function show(p){document.querySelectorAll('section').forEach(s=>s.classList.remove('active'));$(p).classList.add('active');document.querySelectorAll('.navbtn').forEach(b=>b.classList.toggle('active',b.dataset.p===p));$('pageTitle').textContent={dashboard:'root@crypter:~$ cipher.exe',compare:'root@crypter:~$ benchmark.exe',help:'root@crypter:~$ manual.txt'}[p];}
function status(m){$('status').textContent=m;}
function showErr(m){$('err').textContent=m;$('err').style.display='block';}
let lastPlain='',lastCipher='';
async function call(op){const cipher=cipherSel.value;let src=$('inp').value;const rawKey=$('key').value;let key=rawKey.trim();
if(cipher==='Caesar Cipher'&&key===''){key='5';$('key').value='5';}
if((cipher==='Caesar Cipher'||cipher==='Rail Fence Cipher')&&!/^-?\\d+$/.test(key)){showErr(cipher==='Caesar Cipher'?'Shift key must be an integer (e.g. 5). You entered: '+(rawKey===''?"(empty)":'"'+rawKey+'"'):'Rails must be an integer >= 2 (e.g. 3). You entered: '+(rawKey===''?"(empty)":'"'+rawKey+'"'));return;}
if(cipher==='Rail Fence Cipher'&&parseInt(key,10)<2){showErr('Rails must be >= 2. You entered: "'+rawKey+'"');return;}
if(op==='decrypt'&&$('out').value.trim()!==''&&src===lastPlain&&$('out').value===lastCipher){src=$('out').value;}
const body={cipher:cipher,text:src,key:key};$('err').style.display='none';try{const r=await fetch('/api/'+op,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body)});const j=await r.json();if(!j.ok)throw new Error(j.error);$('out').value=j.result;if(j.info)$('matrix').textContent=j.info;if(op==='encrypt'){lastPlain=src;lastCipher=j.result;}status((op==='encrypt'?'Encrypted':'Decrypted')+' with '+body.cipher);}catch(e){$('err').textContent=e.message;$('err').style.display='block';}}
$('encBtn').onclick=()=>call('encrypt');$('decBtn').onclick=()=>call('decrypt');
$('swapBtn').onclick=()=>{if($('out').value.trim()!==''){$('inp').value=$('out').value;status('Output moved to input — now Decrypt to reverse.');}};
$('clrBtn').onclick=()=>{$('inp').value='';$('out').value='';};
$('copyBtn').onclick=()=>{navigator.clipboard.writeText($('out').value);status('Copied to clipboard.');};
$('genBtn').onclick=async()=>{const r=await fetch('/api/generate-key',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({cipher:cipherSel.value,text:$('inp').value})});const j=await r.json();if(j.ok){$('key').value=j.key;status('Key generated.');}};
$('benchBtn').onclick=async()=>{const r=await fetch('/api/benchmark',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({text:$('benchIn').value})});const j=await r.json();$('benchBody').innerHTML=j.results.map(x=>`<tr><td>${x.name}</td><td>${x.type}</td><td>${x.enc.toFixed(4)}</td><td>${x.dec.toFixed(4)}</td><td>${x.status}</td><td>${(x.sample||'').slice(0,28)}</td></tr>`).join('');status('Benchmarked '+j.results.length+' ciphers.');};
const hl=$('helpList');Object.keys(HELP).forEach((k,i)=>{const b=document.createElement('button');b.className='helpbtn'+(i===0?' active':'');b.textContent=k;b.onclick=()=>{document.querySelectorAll('.helpbtn').forEach(x=>x.classList.remove('active'));b.classList.add('active');$('helpTitle').textContent=k;$('helpBody').textContent=HELP[k];};hl.appendChild(b);});
$('helpTitle').textContent=Object.keys(HELP)[0];$('helpBody').textContent=HELP[Object.keys(HELP)[0]];
function applyTheme(t){document.body.classList.toggle('light',t==='light');$('themeBtn').textContent=t==='light'?'dark mode':'light mode';try{localStorage.setItem('cryptokit-theme',t);}catch(e){}}
$('themeBtn').onclick=()=>{applyTheme(document.body.classList.contains('light')?'dark':'light');};
try{applyTheme(localStorage.getItem('cryptokit-theme')||'dark');}catch(e){applyTheme('dark');}
setCipher('Caesar Cipher');
</script></body></html>"""

HELP_JS = {
    "Caesar Cipher": "Substitution shift.\nKey: integer (e.g. 5).\nC = (P + k) mod 26",
    "Monoalphabetic Cipher": "26-letter permutation key.\nUse Generate for a random key.",
    "Playfair Cipher": "5x5 digram matrix, J→I.\nKey: keyword (e.g. MONARCHY).",
    "Hill Cipher": "2x2 matrix mod 26.\nKey: 4 letters (HILL) or 4 numbers.",
    "Vigenère Cipher": "Repeating keyword shift.\nC_i = (P_i + K_i) mod 26",
    "One-Time Pad": "Unbreakable if random, same length, single use.",
    "Rail Fence Cipher": "Zigzag transposition.\nKey: rails >= 2.",
    "Columnar Transposition Cipher": "Keyword column-shuffle.\nKey: e.g. GERMAN.",
}

class Handler(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass
    def _json(self, obj, code=200):
        data = json.dumps(obj).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)
    def _html(self):
        html = PAGE.replace("__CIPHERS__", json.dumps([[n, b, d] for n, b, d in CIPHERS]))
        html = html.replace("__HINTS__", json.dumps(HINTS))
        html = html.replace("__HELP__", json.dumps(HELP_JS))
        data = html.encode()
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)
    def do_GET(self):
        if self.path in ("/", "/index.html"):
            return self._html()
        if self.path == "/api/ciphers":
            return self._json({"ciphers": [{"name": n, "badge": b, "default": d, "hint": HINTS[n]} for n, b, d in CIPHERS]})
        self.send_response(404)
        self.end_headers()
    def _body(self):
        n = int(self.headers.get("Content-Length", 0))
        try:
            return json.loads(self.rfile.read(n) or b"{}")
        except Exception:
            return {}
    def do_POST(self):
        body = self._body()
        try:
            if self.path in ("/api/encrypt", "/api/decrypt"):
                cipher = body.get("cipher") or body.get("algorithm", "Caesar Cipher")
                text = body.get("text", "")
                key = body.get("key", "")
                mode = "encrypt" if self.path.endswith("encrypt") else "decrypt"
                result, info = do_cipher(cipher, text, str(key), mode)
                return self._json({"ok": True, "result": result, "info": info})
            if self.path == "/api/generate-key":
                cipher = body.get("cipher", "")
                text = body.get("text", "")
                if cipher == "Monoalphabetic Cipher":
                    return self._json({"ok": True, "key": generate_monoalphabetic_key()})
                if cipher == "One-Time Pad":
                    alpha = sum(1 for ch in text if ch.isalpha()) or 10
                    return self._json({"ok": True, "key": generate_otp_key(alpha)})
                return self._json({"ok": False, "error": "Generate supported for Monoalphabetic + OTP only"}, 400)
            if self.path == "/api/benchmark":
                text = body.get("text") or "THE QUICK BROWN FOX JUMPS OVER THE LAZY DOG 12345"
                out = [{"name": r.name, "type": r.cipher_type, "enc": r.encrypt_time_ms,
                        "dec": r.decrypt_time_ms, "status": r.status, "sample": r.ciphertext}
                       for r in benchmark_algorithms(text)]
                return self._json({"ok": True, "results": out})
            return self._json({"ok": False, "error": "unknown route"}, 404)
        except Exception as e:
            return self._json({"ok": False, "error": str(e)}, 400)

def main():
    port = 8080
    if len(sys.argv) > 2 and sys.argv[1] == "--port":
        port = int(sys.argv[2])
    srv = ThreadingHTTPServer(("127.0.0.1", port), Handler)
    print(f"Serving CryptoKit web UI on http://127.0.0.1:{port}", flush=True)
    srv.serve_forever()

if __name__ == "__main__":
    main()
