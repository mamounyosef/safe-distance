"""Label the visible-danger windows in a browser (this PC serves; same kind of page as the BDD100K tool).

Shows batch 1 of set.json (40 crash windows + 15 decoys, random order, anonymous names) one at a time: the 2 s the
model saw, looped. No risk number and nothing that says crash or normal. The question:
    "Should a warning system alert the driver now: is a collision with OUR car developing?"
Keys (the same order as the BDD100K tool): 1 normal (no alert), 2 risk (alert), 3 unsure,
right/left arrow (or d/a) next/previous, space replay. Every label is saved at once (atomic write).

Labels: <data_dir>/human_labels.json  {name: {"label": "no" | "yes" | "unsure", "key": "1" | "2" | "3", "by", "at"}}
(NOT in git: together with set.json it says which windows are crashes).

The page needs ?key=<KEY> (printed at start). Share with:  ngrok http 8766  (then the https link + ?key=...)

RUN IT (from the repo root; make_set.py first):
    .venv\\Scripts\\python.exe src\\risk\\runs\\stage1_lora\\late_validation\\visible_labels\\label_web.py
"""

from __future__ import annotations

import json
import re
import secrets
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

import yaml

HERE = Path(__file__).resolve().parent
CFG = yaml.safe_load((HERE / "config.yaml").read_text(encoding="utf-8"))

# ---- CONFIG ----
DATA = Path(CFG["set"]["data_dir"])
LABELS = DATA / "human_labels.json"
KEY_FILE = DATA / ".label_web_key"                 # the page's access key, kept between restarts
PORT = CFG["web"]["port"]
KEYS = {"1": "no", "2": "yes", "3": "unsure"}      # 1 normal, 2 risk (alert), 3 unsure
# ----------------

import sys
BATCH = int(sys.argv[1]) if len(sys.argv) > 1 else 1                     # which batch to label (default 1)
ROWS = [it for it in json.loads((DATA / "set.json").read_text()) if it["batch"] == BATCH]   # in its order
LOCK = threading.Lock()
KEY = KEY_FILE.read_text().strip() if KEY_FILE.exists() else secrets.token_urlsafe(12)
KEY_FILE.write_text(KEY)


def load() -> dict:
    return json.loads(LABELS.read_text()) if LABELS.exists() else {}


def save(labels: dict) -> None:
    tmp = LABELS.with_suffix(".tmp")
    tmp.write_text(json.dumps(labels, indent=1))
    tmp.replace(LABELS)                            # atomic: never a half-written file


def info(i: int) -> dict:
    """What the page needs for window number i (0-based). Only the anonymous name: nothing about crash or normal."""
    labels = load()
    name = ROWS[i]["name"]
    lab = labels.get(name, {})
    return {"i": i, "n": len(ROWS), "name": name, "video": f"/clips/{name}.mp4",
            "label": lab.get("label"), "by": lab.get("by"), "labelled": sum(r["name"] in labels for r in ROWS)}


def next_unlabelled(after: int) -> int:
    labels = load()
    for k in list(range(after + 1, len(ROWS))) + list(range(0, after + 1)):
        if ROWS[k]["name"] not in labels:
            return k
    return max(0, min(after + 1, len(ROWS) - 1))


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def _ok(self, body: bytes, ctype: str, code: int = 200, extra: dict | None = None) -> None:
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        for k, v in (extra or {}).items():
            self.send_header(k, v)
        self.end_headers()
        self.wfile.write(body)

    def _json(self, obj) -> None:
        self._ok(json.dumps(obj).encode(), "application/json")

    def _authorised(self, q: dict) -> bool:
        if q.get("key", [""])[0] == KEY:
            return True
        self._ok(b"missing or wrong key", "text/plain", 403)
        return False

    def do_GET(self):
        u = urlparse(self.path)
        q = parse_qs(u.query)
        if not self._authorised(q):
            return
        if u.path == "/":
            self._ok(PAGE.encode(), "text/html; charset=utf-8")
        elif u.path == "/api/clip":
            self._json(info(max(0, min(int(q.get("i", ["0"])[0]), len(ROWS) - 1))))
        elif u.path == "/api/next":
            self._json({"i": next_unlabelled(int(q.get("after", ["-1"])[0]))})
        elif re.fullmatch(r"/clips/w\d{3}\.mp4", u.path):
            self._video(DATA / "clips8" / u.path.split("/")[-1])   # the 16 frames at 8 fps (what the model sees)
        else:
            self._ok(b"not found", "text/plain", 404)

    def _video(self, path: Path) -> None:
        """Serve an mp4 with byte ranges (browsers need them to loop and seek)."""
        if not path.exists():
            self._ok(b"clip not prepared", "text/plain", 404)
            return
        data = path.read_bytes()
        m = re.match(r"bytes=(\d*)-(\d*)", self.headers.get("Range") or "")
        if m:
            a = int(m.group(1) or 0)
            b = min(int(m.group(2) or len(data) - 1), len(data) - 1)
            self._ok(data[a:b + 1], "video/mp4", 206,
                     {"Content-Range": f"bytes {a}-{b}/{len(data)}", "Accept-Ranges": "bytes"})
        else:
            self._ok(data, "video/mp4", 200, {"Accept-Ranges": "bytes"})

    def do_POST(self):
        u = urlparse(self.path)
        q = parse_qs(u.query)
        if not self._authorised(q) or u.path != "/api/label":
            return
        body = json.loads(self.rfile.read(int(self.headers.get("Content-Length", 0))) or b"{}")
        i, k, user = int(body["i"]), str(body["key"]), str(body.get("user", "?"))[:40]
        if k not in KEYS or not 0 <= i < len(ROWS):
            self._ok(b"bad label", "text/plain", 400)
            return
        with LOCK:
            labels = load()
            labels[ROWS[i]["name"]] = {"label": KEYS[k], "key": k, "by": user,
                                       "at": time.strftime("%Y-%m-%d %H:%M:%S")}
            save(labels)
        self._json({"saved": True, "next": next_unlabelled(i)})


PAGE = r"""<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Visible danger labelling</title>
<style>
 body{margin:0;background:#111;color:#eee;font:15px system-ui,sans-serif}
 .wrap{max-width:1000px;margin:0 auto;padding:12px 16px}
 .bar{display:flex;flex-wrap:wrap;gap:8px 18px;align-items:center;margin:8px 0}
 video{width:100%;background:#000;border-radius:4px}
 .q{font:600 18px system-ui;margin:10px 0}
 .btn{font:600 16px system-ui;padding:10px 16px;border:0;border-radius:6px;cursor:pointer}
 .n{background:#2e7d32;color:#fff}.c{background:#c62828;color:#fff}.u{background:#f9a825;color:#000}.g{background:#444;color:#fff}
 .lab{font-weight:700}.muted{color:#aaa}
</style></head><body><div class="wrap">
<div class="bar"><span id="pos"></span><span id="done" class="muted"></span><span id="me" class="muted"></span></div>
<video id="v" autoplay muted loop playsinline></video>
<div class="q">Should a warning system alert the driver now: is a collision with OUR car developing?</div>
<div class="bar"><span>Label: <span id="lab" class="lab"></span></span></div>
<div class="bar">
 <button class="btn n" onclick="label('1')">1 normal (no alert)</button>
 <button class="btn c" onclick="label('2')">2 risk (alert)</button>
 <button class="btn u" onclick="label('3')">3 unsure</button>
 <button class="btn g" onclick="go(cur.i-1)">&larr; previous</button>
 <button class="btn g" onclick="go(cur.i+1)">next &rarr;</button>
 <button class="btn g" onclick="nextFree()">next unlabelled</button>
</div>
<p class="muted">Keys: 1 normal (no alert), 2 risk (alert), 3 unsure, arrows previous/next, space replay. Judge only what is visible up to the last frame. Labels save immediately.</p>
</div><script>
const key=new URLSearchParams(location.search).get('key');
let user=null; try{user=localStorage.getItem('labeller')}catch(e){}
while(!user){user=(window.prompt('Your name (saved with each label):')||'').trim()}
try{localStorage.setItem('labeller',user)}catch(e){}
document.getElementById('me').textContent='you: '+user;
let cur=null; const v=document.getElementById('v');
const colours={no:'#66bb6a',yes:'#ef5350',unsure:'#ffca28'};
const names={no:'1 normal',yes:'2 risk',unsure:'3 unsure'};
async function api(p){const r=await fetch(p+(p.includes('?')?'&':'?')+'key='+key);return r.json()}
async function go(i){ if(cur&&(i<0||i>=cur.n))return; cur=await api('/api/clip?i='+i); show() }
async function nextFree(){ const r=await api('/api/next?after='+(cur?cur.i:-1)); go(r.i) }
function show(){
 v.src=cur.video+'?key='+key; v.play().catch(()=>{});
 document.getElementById('pos').textContent=`${cur.i+1}/${cur.n}   ${cur.name}`;
 document.getElementById('done').textContent=`labelled ${cur.labelled}/${cur.n}`;
 const l=document.getElementById('lab'); l.textContent=cur.label?(names[cur.label]+(cur.by?' (by '+cur.by+')':'')):'-';
 l.style.color=colours[cur.label]||'#ccc';
}
v.addEventListener('ended',()=>{v.currentTime=0;v.play().catch(()=>{})});
let lastT=-1,stuck=0;
setInterval(()=>{ if(!cur||v.paused)return; if(v.currentTime===lastT){stuck+=500}else{stuck=0;lastT=v.currentTime}
 if(stuck>=1500){stuck=0;const s=v.src;v.src='';v.src=s;v.play().catch(()=>{})} },500);
async function label(k){ const r=await fetch('/api/label?key='+key,{method:'POST',headers:{'Content-Type':'application/json'},
 body:JSON.stringify({i:cur.i,key:k,user})}); if(!r.ok){alert('not saved: '+r.status);return}
 const j=await r.json(); go(j.next) }
document.addEventListener('keydown',e=>{ if(!cur)return;
 if(['1','2','3'].includes(e.key))label(e.key);
 else if(e.key==='ArrowRight'||e.key==='d')go(cur.i+1);
 else if(e.key==='ArrowLeft'||e.key==='a')go(cur.i-1);
 else if(e.key===' '){e.preventDefault();v.currentTime=0;v.play()} });
nextFree();
</script></body></html>"""


if __name__ == "__main__":
    print(f"{len(ROWS)} windows, {sum(r['name'] in load() for r in ROWS)} already labelled")
    print(f"open on this PC:  http://localhost:{PORT}/?key={KEY}")
    print(f"for a phone:      ngrok http {PORT}   then open  https://<ngrok-address>/?key={KEY}")
    ThreadingHTTPServer(("127.0.0.1", PORT), Handler).serve_forever()
