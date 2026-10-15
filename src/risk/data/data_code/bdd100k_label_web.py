"""Label BDD100K train clips together in a browser (this PC serves; friends join through a link).

Same job as bdd100k_label.py (ranks 201-638, labels in src/risk/data/bdd100k_ids/manual_labels.json, same file
and format, plus "by" = who labelled), but as a small web server so several people can label at once:
  - each person types a name once; every label records it
  - "next" hands out the first clip nobody has labelled and nobody else is looking at (claimed for 3 min),
    so two people never do the same clip by accident
  - arrows move freely through all clips (shows the existing label and who gave it)
  - every label is saved at once (atomic write, a lock for simultaneous clicks)
Keys: 1 normal, 2 crash (real danger), 3 unsure, right/left arrow (or d/a) next/previous, space replay.

The page needs ?key=<KEY> (printed at start) so only people with the link can open it.
Share it with:  ngrok http 8765   (then send the https link + ?key=...)

RUN IT (from the repo root; clips first made by bdd100k_label.py --prepare):

    .venv\\Scripts\\python.exe src\\risk\\data\\data_code\\bdd100k_label_web.py
"""

from __future__ import annotations

import json
import re
import secrets
import sys
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

sys.path.insert(0, str(Path(__file__).resolve().parent))
from bdd100k_label import BEFORE_S, CLIPS, LABELS, load_labels, save_labels, todo  # noqa: E402
from bdd100k_review import SERIES  # noqa: E402

# ---- CONFIG ----
PORT = 8765
KEY_FILE = LABELS.with_name(".label_web_key")     # the access key, kept between restarts (not in git)
CLAIM_S = 180                                     # a clip shown to one person is skipped by "next" for others
LABEL_NAMES = {"1": "normal", "2": "real", "3": "unsure"}
# ----------------

ROWS = todo()                                     # clips in rank order
SERIES_ALL = json.loads(SERIES.read_text())
LOCK = threading.Lock()
LABELS_NOW = load_labels()
CLAIMS: dict[str, tuple[str, float]] = {}         # clip -> (person, time claimed)
KEY = KEY_FILE.read_text().strip() if KEY_FILE.exists() else secrets.token_urlsafe(12)
KEY_FILE.write_text(KEY)


def clip_info(i: int) -> dict:
    """Everything the page needs for clip number i (0-based, rank order)."""
    r = ROWS[i]
    start = max(0.0, r["peak_s"] - BEFORE_S)
    lab = LABELS_NOW.get(r["clip"], {})
    return {"i": i, "n": len(ROWS), "rank": r["rank"], "clip": r["clip"], "max_risk": r["max_risk"],
            "peak_s": r["peak_s"], "start_s": start, "video": f"/clips/{r['rank']:04d}_{r['clip']}.mp4",
            "series": [(t, p) for t, p in SERIES_ALL[r["clip"]] if start - 2 <= t <= start + 6],
            "label": lab.get("label"), "by": lab.get("by"),
            "labelled": len([x for x in ROWS if x["clip"] in LABELS_NOW])}


def next_free(user: str, after: int) -> int:
    """First clip after `after` with no label and not claimed by someone else (wraps around)."""
    now = time.time()
    for k in list(range(after + 1, len(ROWS))) + list(range(0, after + 1)):
        c = ROWS[k]["clip"]
        who, t = CLAIMS.get(c, (None, 0))
        if c not in LABELS_NOW and (who in (None, user) or now - t > CLAIM_S):
            return k
    return max(0, min(after + 1, len(ROWS) - 1))   # everything is labelled: just move on


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *a):                   # quiet console
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
        elif u.path == "/api/clip":              # one clip by index, and claim it for this person
            i = max(0, min(int(q.get("i", ["0"])[0]), len(ROWS) - 1))
            with LOCK:
                if ROWS[i]["clip"] not in LABELS_NOW:
                    CLAIMS[ROWS[i]["clip"]] = (q.get("user", ["?"])[0], time.time())
                self._json(clip_info(i))
        elif u.path == "/api/next":              # next clip nobody has done
            with LOCK:
                i = next_free(q.get("user", ["?"])[0], int(q.get("after", ["-1"])[0]))
            self._json({"i": i})
        elif u.path.startswith("/clips/") and re.fullmatch(r"/clips/\d{4}_[\w-]+\.mp4", u.path):
            self._video(CLIPS / u.path.split("/")[-1])
        else:
            self._ok(b"not found", "text/plain", 404)

    def _video(self, path: Path) -> None:
        """Serve an mp4, with byte ranges (browsers need them to replay and seek)."""
        if not path.exists():
            self._ok(b"clip not prepared", "text/plain", 404)
            return
        data = path.read_bytes()
        rng = self.headers.get("Range")
        m = re.match(r"bytes=(\d*)-(\d*)", rng or "")
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
        i, key, user = int(body["i"]), str(body["key"]), str(body.get("user", "?"))[:40]
        if key not in LABEL_NAMES or not 0 <= i < len(ROWS):
            self._ok(b"bad label", "text/plain", 400)
            return
        r = ROWS[i]
        with LOCK:                               # simultaneous clicks from two people: one at a time
            LABELS_NOW[r["clip"]] = {"rank": r["rank"], "label": LABEL_NAMES[key], "max_risk": r["max_risk"],
                                     "peak_s": r["peak_s"], "by": user, "at": time.strftime("%Y-%m-%d %H:%M:%S")}
            save_labels(LABELS_NOW)
            CLAIMS.pop(r["clip"], None)
            nxt = next_free(user, i)
        self._json({"saved": True, "next": nxt})


PAGE = r"""<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>BDD100K labelling</title>
<style>
 body{margin:0;background:#111;color:#eee;font:15px system-ui,sans-serif}
 .wrap{max-width:980px;margin:0 auto;padding:12px 16px}
 .bar{display:flex;flex-wrap:wrap;gap:8px 18px;align-items:center;margin:8px 0}
 video{width:100%;background:#000;border-radius:4px}
 .risk{font:600 22px ui-monospace,Consolas,monospace}
 .btn{font:600 16px system-ui;padding:10px 16px;border:0;border-radius:6px;cursor:pointer}
 .n{background:#2e7d32;color:#fff}.c{background:#c62828;color:#fff}.u{background:#f9a825;color:#000}.g{background:#444;color:#fff}
 .lab{font-weight:700}.muted{color:#aaa}
</style></head><body><div class="wrap">
<div class="bar"><span id="pos"></span><span id="done" class="muted"></span><span id="me" class="muted"></span></div>
<video id="v" autoplay muted loop playsinline></video>
<div class="bar"><span class="risk" id="risk"></span><span id="peak" class="muted"></span></div>
<div class="bar"><span>Label: <span id="lab" class="lab"></span></span></div>
<div class="bar">
 <button class="btn n" onclick="label('1')">1 normal</button>
 <button class="btn c" onclick="label('2')">2 crash</button>
 <button class="btn u" onclick="label('3')">3 unsure</button>
 <button class="btn g" onclick="go(cur.i-1)">&larr; previous</button>
 <button class="btn g" onclick="go(cur.i+1)">next &rarr;</button>
 <button class="btn g" onclick="nextFree()">next unlabelled</button>
</div>
<p class="muted">Keys: 1 normal, 2 crash, 3 unsure, arrows previous/next, space replay. Labels save immediately.</p>
</div><script>
const key=new URLSearchParams(location.search).get('key');
let user=null; try{user=localStorage.getItem('labeller')}catch(e){}
while(!user){user=(window.prompt('Your name (saved with each label):')||'').trim()}
try{localStorage.setItem('labeller',user)}catch(e){}
document.getElementById('me').textContent='you: '+user;
let cur=null; const v=document.getElementById('v');
const colours={normal:'#66bb6a',real:'#ef5350',unsure:'#ffca28'};
async function api(p){const r=await fetch(p+(p.includes('?')?'&':'?')+'key='+key+'&user='+encodeURIComponent(user));return r.json()}
async function go(i){ if(cur&&(i<0||i>=cur.n))return; cur=await api('/api/clip?i='+i); show() }
async function nextFree(){ const r=await api('/api/next?after='+(cur?cur.i:-1)); go(r.i) }
function show(){
 v.src=cur.video+'?key='+key; v.play().catch(()=>{});
 document.getElementById('pos').textContent=`${cur.i+1}/${cur.n}   rank ${cur.rank}`;
 document.getElementById('done').textContent=`labelled ${cur.labelled}/${cur.n}`;
 document.getElementById('peak').textContent=`peak ${cur.max_risk.toFixed(3)}`;
 const l=document.getElementById('lab'); l.textContent=cur.label?(cur.label+(cur.by?' (by '+cur.by+')':'')):'-';
 l.style.color=colours[cur.label]||'#ccc';
}
v.addEventListener('timeupdate',()=>{ if(!cur)return; const t=cur.start_s+v.currentTime; let p=null;
 for(const [tt,pp] of cur.series){ if(tt<=t)p=pp }
 document.getElementById('risk').textContent='BADAS risk '+(p===null?'-':p.toFixed(3))+`   ${(t-cur.peak_s).toFixed(1)} s from peak`;
 document.getElementById('risk').style.color=(p!==null&&p>=0.99)?'#ef5350':'#eee' });
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
    print(f"{len(ROWS)} clips, {len([r for r in ROWS if r['clip'] in LABELS_NOW])} already labelled")
    print(f"open on this PC:  http://localhost:{PORT}/?key={KEY}")
    print(f"for a friend:     ngrok http {PORT}   then send  https://<ngrok-address>/?key={KEY}")
    ThreadingHTTPServer(("127.0.0.1", PORT), Handler).serve_forever()
