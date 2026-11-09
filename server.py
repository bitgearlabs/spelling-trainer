"""Local web server for the Spelling Trainer (stdlib only)."""
import json
import os
import random
import tempfile
import threading
import uuid
import webbrowser
from collections import deque
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from checker import check
from generators import CATEGORIES, Opts, generate, speak_chars
from tts_engines import ENGINES

ROOT = os.path.dirname(os.path.abspath(__file__))
PORT = 8765
ITEMS = {}
AUDIO = {}
TTS_LOCK = threading.Lock()
RECENT = deque(maxlen=200)  # recent answers, to avoid repeats


def is_us(engine, voice):
    v = (voice or "").upper()
    return (engine == "edge" and v.startswith("EN-US")) or (engine == "gtts" and voice == "com")         or (engine == "pyttsx3" and "EN-US" in v)


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def _send(self, code, body, ctype="application/json"):
        if isinstance(body, (dict, list)):
            body = json.dumps(body).encode()
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def _json(self):
        n = int(self.headers.get("Content-Length") or 0)
        return json.loads(self.rfile.read(n) or b"{}")

    def do_GET(self):
        path, _, qs = self.path.partition("?")
        if path in ("/", "/index.html"):
            with open(os.path.join(ROOT, "web", "index.html"), "rb") as f:
                return self._send(200, f.read(), "text/html; charset=utf-8")
        if path == "/api/engines":
            return self._send(200, [{"key": k, "label": e.label, "available": e.available()}
                                    for k, e in ENGINES.items()])
        if path == "/api/voices":
            key = dict(p.split("=") for p in qs.split("&") if "=" in p).get("engine", "edge")
            try:
                with TTS_LOCK:
                    v = ENGINES[key].voices()
                return self._send(200, [{"name": n, "id": i} for n, i in v])
            except Exception as e:  # noqa: BLE001
                return self._send(500, {"error": str(e)})
        if path == "/api/categories":
            return self._send(200, CATEGORIES)
        self._send(404, {"error": "not found"})

    def do_POST(self):
        d = self._json()
        if self.path == "/api/question":
            cats = [c for c in d.get("cats", []) if c in CATEGORIES] or list(CATEGORIES)
            us = is_us(d.get("engine"), d.get("voice"))
            dbl = d.get("double", "auto")
            opts = Opts(double=(not us) if dbl == "auto" else dbl == "always",
                        zero=d.get("zero", "random"), hard=bool(d.get("hard")), us=us)
            for _ in range(30):
                item = generate(random.choice(cats), opts)
                if item.answer not in RECENT:
                    break
            RECENT.append(item.answer)
            qid = uuid.uuid4().hex
            if len(ITEMS) > 500:
                ITEMS.clear()
            ITEMS[qid] = item
            return self._send(200, {"id": qid, "category": item.category,
                                    "label": CATEGORIES[item.category], "hint": item.hint})
        if self.path == "/api/check":
            item = ITEMS.get(d.get("id"))
            if not item:
                return self._send(404, {"error": "unknown question"})
            return self._send(200, {"correct": check(item, d.get("answer", "")), "answer": item.answer})
        if self.path == "/api/tts":
            eng = ENGINES.get(d.get("engine"))
            if not eng:
                return self._send(400, {"error": "unknown engine"})
            item = ITEMS.get(d.get("id"))
            text = item.spoken if item else d.get("text", "")
            if d.get("spell"):
                text = speak_chars(d["spell"], use_double=False, zee=is_us(d.get("engine"), d.get("voice")))
            voice, speed = d.get("voice", ""), float(d.get("speed", 1))
            key = (text, eng.key, voice, speed)
            if key not in AUDIO:
                path = os.path.join(tempfile.gettempdir(), uuid.uuid4().hex + eng.ext)
                try:
                    with TTS_LOCK:
                        eng.synth(text, voice, speed, path)
                    with open(path, "rb") as f:
                        if len(AUDIO) > 200:
                            AUDIO.clear()
                        AUDIO[key] = f.read()
                except Exception as e:  # noqa: BLE001
                    return self._send(500, {"error": str(e)})
                finally:
                    if os.path.exists(path):
                        os.remove(path)
            return self._send(200, AUDIO[key], "audio/mpeg" if eng.ext == ".mp3" else "audio/wav")
        self._send(404, {"error": "not found"})


def main():
    srv = ThreadingHTTPServer(("127.0.0.1", PORT), Handler)
    url = f"http://spelling.localhost:{PORT}"
    print(f"Spelling Trainer running at {url}  (Ctrl+C to stop)")
    threading.Timer(0.8, lambda: webbrowser.open(url)).start()
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
