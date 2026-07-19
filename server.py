
/
напиши серверок с игрой только py файл как здесь [app]
name  = "hello"
entry = "python3"
args  = ["server.py"]

[net]
port = 8080

[runtime]
autosave = "off"
health   = "/health"
#!/usr/bin/env python3# Minimal app to try runlord with: answers with the version it was given.#   runlord up --root examples/hello#   curl localhost:8080import osfrom http.server import BaseHTTPRequestHandler, ThreadingHTTPServerPORT = int(os.environ.get("PORT", "3000"))VERSION = os.environ.get("RUNLORD_VERSION", "dev")class Handler(BaseHTTPRequestHandler):    def do_GET(self):        if self.path == "/health":            body = b"ok\n"        else:            body = f"hello from {VERSION}\n".encode()        self.send_response(200)        self.send_header("Content-Type", "text/plain")        self.send_header("Content-Length", str(len(body)))        self.end_headers()        self.wfile.write(body)    def log_message(self, fmt, *args):        print(fmt % args, flush=True)if __name__ == "__main__":    ThreadingHTTPServer(("127.0.0.1", PORT), Handler).serve_forever()
11:34 PM
Thought
Сделаю один server.py в стиле runlord: /health, порт из PORT, и простая браузерная игра. Сначала проверю, как правильно создать файл.
Пишу один server.py в стиле runlord: /health, порт из PORT и встроенная браузерная игра.
Исправлю опечатку в print и проверю, что сервер стартует.
Исправляю строку запуска и отдаю готовый файл.
Поправлю строку print через Python и отдам готовый файл.
Сервер уже отвечает — поправлю строку лога и отдам server.py.
Исправляю строку лога и отдаю готовый server.py.
Отдаю готовый server.py — сервер уже проверен.
Файл готов — отдаю server.py на скачивание.
Shared file
server
.py
Thought
Готово — один файл server.py (скачай карточку выше).
Это HTTP-сервер под runlord со Snake в браузере.
Эндпоинты
/ — игра
/health → ok
POST /api/score — сохранить результат
GET /api/scores — топ
runlord (runlord.toml рядом с server.py)
[app]
name  = "snake"
entry = "python3"
args  = ["server.py"]

[net]
port = 8080

[runtime]
autosave = "off"
health   = "/health"
​
Запуск
runlord up --root .
# или
PORT=8080 python3 server.py
​
Открой http://localhost:8080 — стрелки/WASD, пробел = пауза, на телефоне свайпы и кнопки.

server.py
#!/usr/bin/env python3
# Snake game server for runlord.
#   runlord up --root .
#   open http://localhost:8080
import json
import os
import random
import secrets
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse
​
PORT = int(os.environ.get("PORT", "8080"))
VERSION = os.environ.get("RUNLORD_VERSION", "dev")
​
# In-memory high scores (per process lifetime)
_lock = threading.Lock()
_scores: list[dict] = []
​
​
def _add_score(name: str, score: int) -> list[dict]:
    name = (name or "anon").strip()[:16] or "anon"
    score = max(0, min(int(score), 999999))
    with _lock:
        _scores.append(
            {
                "name": name,
                "score": score,
                "ts": int(time.time()),
                "id": secrets.token_hex(4),
            }
        )
        _scores.sort(key=lambda s: (-s["score"], s["ts"]))
        del _scores[20:]
        return list(_scores)
​
​
def _top_scores() -> list[dict]:
    with _lock:
        return list(_scores)
​
​
HTML = r"""<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1, user-scalable=no">
<title>Snake · runlord</title>
<style>
  :root {
    --bg: #0b1020;
    --panel: #121a33;
    --grid: #1a2448;
    --snake: #5eead4;
    --snake-head: #99f6e4;
    --food: #f472b6;
    --text: #e2e8f0;
    --muted: #94a3b8;
    --accent: #818cf8;
    --danger: #fb7185;
  }
  * { box-sizing: border-box; }
  html, body {
    margin: 0; height: 100%;
    background: radial-gradient(1200px 600px at 50% -10%, #1e293b 0%, var(--bg) 55%);
    color: var(--text);
    font-family: ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto, sans-serif;
  }
  body {
    display: flex; flex-direction: column; align-items: center;
    justify-content: flex-start; min-height: 100%; padding: 20px 12px 40px;
  }
  h1 {
    margin: 0 0 4px; font-size: 1.5rem; letter-spacing: 0.04em;
    font-weight: 700;
  }
  .sub { color: var(--muted); font-size: 0.85rem; margin-bottom: 16px; }
  .wrap {
    display: grid;
    grid-template-columns: 1fr;
    gap: 16px;
    width: min(100%, 420px);
  }
  @media (min-width: 760px) {
    .wrap { grid-template-columns: 420px 220px; width: auto; align-items: start; }
  }
  .panel {
    background: color-mix(in srgb, var(--panel) 92%, transparent);
    border: 1px solid #243056;
    border-radius: 16px;
    padding: 14px;
    box-shadow: 0 20px 50px rgba(0,0,0,.35);
  }
  .hud {
    display: flex; justify-content: space-between; align-items: center;
    margin-bottom: 10px; gap: 8px; flex-wrap: wrap;
  }
  .stat { font-variant-numeric: tabular-nums; }
  .stat b { color: var(--snake); }
  canvas {
    display: block; width: 100%; height: auto;
    background: var(--grid);
    border-radius: 12px;
    touch-action: none;
    image-rendering: pixelated;
  }
  .btns { display: flex; gap: 8px; margin-top: 12px; flex-wrap: wrap; }
  button, .name-input {
    appearance: none; border: 0; border-radius: 10px;
    padding: 10px 14px; font: inherit; cursor: pointer;
  }
  button {
    background: var(--accent); color: white; font-weight: 600;
  }
  button.secondary { background: #243056; color: var(--text); }
  button:active { transform: translateY(1px); }
  .name-input {
    flex: 1; min-width: 100px;
    background: #0f172a; color: var(--text);
    border: 1px solid #334155;
  }
  .help { color: var(--muted); font-size: 0.8rem; line-height: 1.45; margin-top: 10px; }
  .help kbd {
    background: #1e293b; border: 1px solid #334155; border-bottom-width: 2px;
    border-radius: 6px; padding: 1px 6px; font-size: 0.75rem; color: var(--text);
  }
  h2 { margin: 0 0 10px; font-size: 1rem; }
  ol { margin: 0; padding-left: 1.2rem; }
  li { margin: 4px 0; font-variant-numeric: tabular-nums; }
  .empty { color: var(--muted); font-size: 0.9rem; }
  .overlay {
    position: absolute; inset: 0; display: none;
    align-items: center; justify-content: center;
    background: rgba(11,16,32,.72); border-radius: 12px;
    text-align: center; padding: 20px;
  }
  .overlay.show { display: flex; }
  .stage { position: relative; }
  .overlay h3 { margin: 0 0 6px; font-size: 1.35rem; }
  .overlay p { margin: 0 0 12px; color: var(--muted); }
  .pad {
    display: grid; grid-template-columns: repeat(3, 56px); gap: 8px;
    justify-content: center; margin-top: 12px;
  }
  .pad button { width: 56px; height: 56px; padding: 0; font-size: 1.2rem; background: #243056; }
  .pad .sp { visibility: hidden; }
  footer { margin-top: 18px; color: var(--muted); font-size: 0.75rem; }
</style>
</head>
<body>
  <h1>🐍 Snake</h1>
  <div class="sub">single-file python · runlord ready</div>
​
  <div class="wrap">
    <div class="panel">
      <div class="hud">
        <div class="stat">Очки: <b id="score">0</b></div>
        <div class="stat">Рекорд: <b id="best">0</b></div>
        <div class="stat">Скорость: <b id="spd">1</b></div>
      </div>
      <div class="stage">
        <canvas id="c" width="400" height="400" aria-label="Snake game"></canvas>
        <div class="overlay show" id="overlay">
          <div>
            <h3 id="otitle">Snake</h3>
            <p id="omsg">Стрелки / WASD · пробел — пауза</p>
            <button id="startBtn" type="button">Играть</button>
          </div>
        </div>
      </div>
      <div class="btns">
        <input class="name-input" id="name" maxlength="16" placeholder="Имя для таблицы" value="player">
        <button class="secondary" id="pauseBtn" type="button">Пауза</button>
      </div>
      <div class="pad" aria-hidden="true">
        <span class="sp"></span>
        <button type="button" data-dir="up">↑</button>
        <span class="sp"></span>
        <button type="button" data-dir="left">←</button>
        <button type="button" data-dir="down">↓</button>
        <button type="button" data-dir="right">→</button>
      </div>
      <div class="help">
        Ешь розовые яблоки, не врезайся в стены и в себя.<br>
        <kbd>↑</kbd><kbd>↓</kbd><kbd>←</kbd><kbd>→</kbd> или <kbd>WASD</kbd>, <kbd>Space</kbd> — пауза.
      </div>
    </div>
​
    <div class="panel">
      <h2>🏆 Топ</h2>
      <ol id="board"><li class="empty">Пока пусто</li></ol>
    </div>
  </div>
​
  <footer>version __VERSION__ · /health ok</footer>
​
<script>
(() => {
  const COLS = 20, ROWS = 20;
  const canvas = document.getElementById('c');
  const ctx = canvas.getContext('2d');
  const scoreEl = document.getElementById('score');
  const bestEl = document.getElementById('best');
  const spdEl = document.getElementById('spd');
  const overlay = document.getElementById('overlay');
  const otitle = document.getElementById('otitle');
  const omsg = document.getElementById('omsg');
  const startBtn = document.getElementById('startBtn');
  const pauseBtn = document.getElementById('pauseBtn');
  const nameEl = document.getElementById('name');
  const boardEl = document.getElementById('board');
​
  const BEST_KEY = 'snake_best_v1';
  let best = Number(localStorage.getItem(BEST_KEY) || 0);
  bestEl.textContent = best;
​
  let snake, dir, nextDir, food, score, tickMs, alive, paused, timer, stepAcc;
​
  function cell() {
    return canvas.width / COLS;
  }
​
  function randEmpty() {
    const taken = new Set(snake.map(p => p.x + ',' + p.y));
    let x, y, guard = 0;
    do {
      x = Math.floor(Math.random() * COLS);
      y = Math.floor(Math.random() * ROWS);
      guard++;
    } while (taken.has(x + ',' + y) && guard < 500);
    return { x, y };
  }
​
  function reset() {
    const cx = Math.floor(COLS / 2), cy = Math.floor(ROWS / 2);
    snake = [{x:cx,y:cy},{x:cx-1,y:cy},{x:cx-2,y:cy}];
    dir = {x:1,y:0};
    nextDir = {x:1,y:0};
    food = randEmpty();
    score = 0;
    tickMs = 140;
    alive = true;
    paused = false;
    stepAcc = 0;
    scoreEl.textContent = '0';
    spdEl.textContent = '1';
    hideOverlay();
  }
​
  function showOverlay(title, msg, btn) {
    otitle.textContent = title;
    omsg.textContent = msg;
    startBtn.textContent = btn || 'Ещё раз';
    overlay.classList.add('show');
  }
  function hideOverlay() { overlay.classList.remove('show'); }
​
  function setDir(nx, ny) {
    if (!alive || paused) return;
    // no 180° turn
    if (dir.x + nx === 0 && dir.y + ny === 0) return;
    nextDir = { x: nx, y: ny };
  }
​
  function draw() {
    const s = cell();
    // board
    ctx.fillStyle = '#1a2448';
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    // subtle grid
    ctx.strokeStyle = 'rgba(255,255,255,0.04)';
    ctx.lineWidth = 1;
    for (let i = 0; i <= COLS; i++) {
      ctx.beginPath(); ctx.moveTo(i*s, 0); ctx.lineTo(i*s, canvas.height); ctx.stroke();
    }
    for (let j = 0; j <= ROWS; j++) {
      ctx.beginPath(); ctx.moveTo(0, j*s); ctx.lineTo(canvas.width, j*s); ctx.stroke();
    }
    // food
    const fr = s * 0.36;
    ctx.fillStyle = '#f472b6';
    ctx.beginPath();
    ctx.arc(food.x*s + s/2, food.y*s + s/2, fr, 0, Math.PI*2);
    ctx.fill();
    // snake
    snake.forEach((p, i) => {
      const pad = i === 0 ? 1.5 : 2.5;
      ctx.fillStyle = i === 0 ? '#99f6e4' : '#5eead4';
      roundRect(ctx, p.x*s + pad, p.y*s + pad, s - pad*2, s - pad*2, 4);
      ctx.fill();
    });
  }
​
  function roundRect(c, x, y, w, h, r) {
    c.beginPath();
    c.moveTo(x+r, y);
    c.arcTo(x+w, y, x+w, y+h, r);
    c.arcTo(x+w, y+h, x, y+h, r);
    c.arcTo(x, y+h, x, y, r);
    c.arcTo(x, y, x+w, y, r);
    c.closePath();
  }
​
  function step() {
    if (!alive || paused) return;
    dir = nextDir;
    const head = { x: snake[0].x + dir.x, y: snake[0].y + dir.y };
    if (head.x < 0 || head.y < 0 || head.x >= COLS || head.y >= ROWS) {
      return die();
    }
    if (snake.some(p => p.x === head.x && p.y === head.y)) {
      return die();
    }
    snake.unshift(head);
    if (head.x === food.x && head.y === food.y) {
      score += 10;
      scoreEl.textContent = score;
      if (score > best) {
        best = score;
        bestEl.textContent = best;
        localStorage.setItem(BEST_KEY, String(best));
      }
      // speed up a bit every apple
      tickMs = Math.max(55, 140 - Math.floor(score / 10) * 4);
      spdEl.textContent = String(Math.min(20, 1 + Math.floor(score / 20)));
      food = randEmpty();
    } else {
      snake.pop();
    }
  }
​
  async function die() {
    alive = false;
    showOverlay('Game Over', 'Очки: ' + score, 'Снова');
    try {
      await fetch('/api/score', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name: nameEl.value, score })
      });
      await loadBoard();
    } catch (_) {}
  }
​
  let last = 0;
  function loop(ts) {
    timer = requestAnimationFrame(loop);
    if (!last) last = ts;
    const dt = ts - last;
    last = ts;
    if (alive && !paused) {
      stepAcc += dt;
      while (stepAcc >= tickMs) {
        stepAcc -= tickMs;
        step();
      }
    }
    draw();
  }
​
  function startGame() {
    cancelAnimationFrame(timer);
    reset();
    last = 0; stepAcc = 0;
    timer = requestAnimationFrame(loop);
  }
​
  function togglePause() {
    if (!alive) return;
    paused = !paused;
    pauseBtn.textContent = paused ? 'Продолжить' : 'Пауза';
    if (paused) showOverlay('Пауза', 'Нажми пробел или кнопку', 'Продолжить');
    else hideOverlay();
  }
​
  startBtn.addEventListener('click', () => {
    if (paused && alive) { paused = false; pauseBtn.textContent = 'Пауза'; hideOverlay(); return; }
    startGame();
  });
  pauseBtn.addEventListener('click', togglePause);
​
  const keyMap = {
    ArrowUp:[0,-1], ArrowDown:[0,1], ArrowLeft:[-1,0], ArrowRight:[1,0],
    w:[0,-1], s:[0,1], a:[-1,0], d:[1,0],
    W:[0,-1], S:[0,1], A:[-1,0], D:[1,0],
  };
  window.addEventListener('keydown', (e) => {
    if (e.code === 'Space') { e.preventDefault(); togglePause(); return; }
    const v = keyMap[e.key];
    if (v) { e.preventDefault(); setDir(v[0], v[1]); }
  });
​
  document.querySelectorAll('.pad button').forEach(btn => {
    btn.addEventListener('click', () => {
      const m = { up:[0,-1], down:[0,1], left:[-1,0], right:[1,0] }[btn.dataset.dir];
      if (m) setDir(m[0], m[1]);
    });
  });
​
  // swipe
  let sx=0, sy=0;
  canvas.addEventListener('touchstart', e => {
    const t = e.changedTouches[0]; sx = t.clientX; sy = t.clientY;
  }, {passive:true});
  canvas.addEventListener('touchend', e => {
    const t = e.changedTouches[0];
    const dx = t.clientX - sx, dy = t.clientY - sy;
    if (Math.hypot(dx,dy) < 24) return;
    if (Math.abs(dx) > Math.abs(dy)) setDir(dx>0?1:-1, 0);
    else setDir(0, dy>0?1:-1);
  }, {passive:true});
​
  async function loadBoard() {
    try {
      const r = await fetch('/api/scores');
      const data = await r.json();
      if (!data.length) {
        boardEl.innerHTML = '<li class="empty">Пока пусто</li>';
        return;
      }
      boardEl.innerHTML = data.map(s =>
        `<li><strong>${escapeHtml(s.name)}</strong> — ${s.score}</li>`
      ).join('');
    } catch (_) {}
  }
  function escapeHtml(t) {
    return String(t).replace(/[&<>"']/g, c => ({
      '&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'
    })[c]);
  }
​
  // idle board draw
  snake = [{x:8,y:10},{x:7,y:10},{x:6,y:10}];
  food = {x:14,y:10};
  draw();
  loadBoard();
})();
</script>
</body>
</html>
""".replace("__VERSION__", VERSION)
​
​
class Handler(BaseHTTPRequestHandler):
    server_version = f"snake-runlord/{VERSION}"
​
    def _send(self, code: int, body: bytes, content_type: str) -> None:
        self.send_response(code)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)
​
    def _read_json(self) -> dict:
        length = int(self.headers.get("Content-Length", "0") or 0)
        raw = self.rfile.read(length) if length else b"{}"
        try:
            data = json.loads(raw.decode("utf-8") or "{}")
        except json.JSONDecodeError:
            return {}
        return data if isinstance(data, dict) else {}
​
    def do_GET(self) -> None:
        path = urlparse(self.path).path
        if path == "/health":
            self._send(200, b"ok\n", "text/plain; charset=utf-8")
            return
        if path == "/api/scores":
            body = json.dumps(_top_scores(), ensure_ascii=False).encode("utf-8")
            self._send(200, body, "application/json; charset=utf-8")
            return
        if path in ("/", "/index.html", "/game"):
            self._send(200, HTML.encode("utf-8"), "text/html; charset=utf-8")
            return
        self._send(404, b"not found\n", "text/plain; charset=utf-8")
​
    def do_POST(self) -> None:
        path = urlparse(self.path).path
        if path == "/api/score":
            data = self._read_json()
            name = str(data.get("name", "anon"))
            try:
                score = int(data.get("score", 0))
            except (TypeError, ValueError):
                score = 0
            top = _add_score(name, score)
            body = json.dumps(top, ensure_ascii=False).encode("utf-8")
            self._send(200, body, "application/json; charset=utf-8")
            return
        self._send(404, b"not found\n", "text/plain; charset=utf-8")
​
    def log_message(self, fmt: str, *args) -> None:
        print(fmt % args, flush=True)
​
​
if __name__ == "__main__":
    # 0.0.0.0 so runlord / containers can reach the port
    host = os.environ.get("HOST", "0.0.0.0")
    print(f"snake listening on http://{host}:{PORT} (version={VERSION})", flush=True)
    ThreadingHTTPServer((host, PORT), Handler).serve_forever()
​
Notion AI finished.Copied code to clipboard
