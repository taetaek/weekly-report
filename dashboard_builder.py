import base64
import json
import os

from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes

PBKDF2_ITERATIONS = 250_000
AES_KEY_LEN = 32  # 256-bit


CATEGORY_EMOJI = {
    "영어": "🗣",
    "경제": "💰",
    "운동": "🏃",
    "창작&학습": "📚",
    "음악": "🎵",
    "휴식": "🛋",
}

ALL_WEEKDAYS = ["월", "화", "수", "목", "금", "토", "일"]


def _encrypt_payload(payload: dict, password: str) -> dict:
    salt = os.urandom(16)
    nonce = os.urandom(12)
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=AES_KEY_LEN,
        salt=salt,
        iterations=PBKDF2_ITERATIONS,
    )
    key = kdf.derive(password.encode("utf-8"))
    plaintext = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    ciphertext = AESGCM(key).encrypt(nonce, plaintext, None)

    return {
        "salt": base64.b64encode(salt).decode(),
        "nonce": base64.b64encode(nonce).decode(),
        "ciphertext": base64.b64encode(ciphertext).decode(),
        "iterations": PBKDF2_ITERATIONS,
    }


def build_dashboard_html(analysis: dict, week_start, week_end, password: str) -> str:
    if not password:
        raise ValueError("DASHBOARD_PASSWORD가 설정되지 않았습니다.")

    payload = {
        "weekStart": week_start.strftime("%Y.%m.%d"),
        "weekEnd": week_end.strftime("%Y.%m.%d"),
        "categories": [
            {
                "name": cat,
                "emoji": emoji,
                "count": analysis["activity_counts"].get(cat, 0),
                "details": analysis["activity_details"].get(cat, []),
            }
            for cat, emoji in CATEGORY_EMOJI.items()
        ],
        "emptyDays": [d for d in ALL_WEEKDAYS if d not in analysis["active_days"]],
        "graphiteCount": analysis["graphite_count"],
        "graphiteCategories": sorted(analysis.get("graphite_categories", set())),
        "graphiteEvents": analysis.get("graphite_events", []),
    }

    enc = _encrypt_payload(payload, password)

    return _TEMPLATE.format(
        salt=enc["salt"],
        nonce=enc["nonce"],
        ciphertext=enc["ciphertext"],
        iterations=enc["iterations"],
    )


_TEMPLATE = """<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<meta name="robots" content="noindex, nofollow" />
<title>주간 리포트</title>
<style>
  :root {{
    color-scheme: light dark;
    --bg: #f7f7f8;
    --card: #ffffff;
    --text: #1c1c1e;
    --muted: #6b7280;
    --border: #e5e7eb;
    --accent: #4f46e5;
    --alert: #dc2626;
    --alert-bg: #fef2f2;
  }}
  @media (prefers-color-scheme: dark) {{
    :root {{
      --bg: #121214;
      --card: #1c1c1f;
      --text: #f2f2f3;
      --muted: #9a9aa2;
      --border: #2c2c30;
      --accent: #818cf8;
      --alert: #f87171;
      --alert-bg: #2a1414;
    }}
  }}
  * {{ box-sizing: border-box; }}
  body {{
    margin: 0;
    background: var(--bg);
    color: var(--text);
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "Apple SD Gothic Neo", "Malgun Gothic", sans-serif;
    min-height: 100vh;
  }}
  .gate {{
    min-height: 100vh;
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 24px;
  }}
  .gate-box {{
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 16px;
    padding: 32px 28px;
    width: 100%;
    max-width: 340px;
    text-align: center;
  }}
  .gate-box h1 {{ font-size: 18px; margin: 0 0 20px; }}
  .gate-box input {{
    width: 100%;
    padding: 12px 14px;
    border-radius: 10px;
    border: 1px solid var(--border);
    background: var(--bg);
    color: var(--text);
    font-size: 15px;
    text-align: center;
  }}
  .gate-box button {{
    width: 100%;
    margin-top: 12px;
    padding: 12px;
    border-radius: 10px;
    border: none;
    background: var(--accent);
    color: white;
    font-size: 15px;
    font-weight: 600;
    cursor: pointer;
  }}
  .gate-error {{ color: var(--alert); font-size: 13px; margin-top: 10px; min-height: 16px; }}
  main {{ max-width: 640px; margin: 0 auto; padding: 32px 20px 60px; }}
  header h1 {{ font-size: 22px; margin: 0 0 4px; }}
  header p {{ color: var(--muted); margin: 0 0 28px; font-size: 14px; }}
  .card {{
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 14px;
    padding: 18px 20px;
    margin-bottom: 14px;
  }}
  .card h2 {{ font-size: 14px; color: var(--muted); margin: 0 0 12px; font-weight: 600; }}
  .row {{
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 8px 0;
    border-bottom: 1px solid var(--border);
    font-size: 15px;
  }}
  .row:last-child {{ border-bottom: none; }}
  .row .label {{ display: flex; align-items: center; gap: 8px; }}
  .row .count {{ font-weight: 700; }}
  .row.zero {{ color: var(--alert); }}
  .badge {{
    display: inline-block;
    background: var(--alert-bg);
    color: var(--alert);
    border-radius: 999px;
    padding: 2px 10px;
    font-size: 12px;
    font-weight: 600;
  }}
  .empty-days {{ font-size: 15px; }}
  .events {{ margin-top: 10px; font-size: 13px; color: var(--muted); line-height: 1.6; }}
  [hidden] {{ display: none !important; }}
</style>
</head>
<body>
  <div id="gate" class="gate">
    <div class="gate-box">
      <h1>🔒 비밀번호를 입력하세요</h1>
      <input id="pw" type="password" inputmode="text" autocomplete="off" autofocus />
      <button id="unlock">열기</button>
      <div id="err" class="gate-error"></div>
    </div>
  </div>

  <main id="report" hidden></main>

<script>
const ENC = {{
  salt: "{salt}",
  nonce: "{nonce}",
  ciphertext: "{ciphertext}",
  iterations: {iterations}
}};

function b64ToBytes(b64) {{
  const bin = atob(b64);
  const arr = new Uint8Array(bin.length);
  for (let i = 0; i < bin.length; i++) arr[i] = bin.charCodeAt(i);
  return arr;
}}

async function deriveKey(password, salt, iterations) {{
  const enc = new TextEncoder();
  const baseKey = await crypto.subtle.importKey(
    "raw", enc.encode(password), "PBKDF2", false, ["deriveKey"]
  );
  return crypto.subtle.deriveKey(
    {{ name: "PBKDF2", salt, iterations, hash: "SHA-256" }},
    baseKey,
    {{ name: "AES-GCM", length: 256 }},
    false,
    ["decrypt"]
  );
}}

async function tryUnlock(password) {{
  const salt = b64ToBytes(ENC.salt);
  const nonce = b64ToBytes(ENC.nonce);
  const ciphertext = b64ToBytes(ENC.ciphertext);
  const key = await deriveKey(password, salt, ENC.iterations);
  const plaintextBuf = await crypto.subtle.decrypt({{ name: "AES-GCM", iv: nonce }}, key, ciphertext);
  return JSON.parse(new TextDecoder().decode(plaintextBuf));
}}

function render(data) {{
  const main = document.getElementById("report");
  const esc = (s) => String(s).replace(/[&<>]/g, c => ({{"&":"&amp;","<":"&lt;",">":"&gt;"}}[c]));

  let html = `
    <header>
      <h1>📅 주간 일정 리포트</h1>
      <p>${{esc(data.weekStart)}}(월) ~ ${{esc(data.weekEnd)}}(일)</p>
    </header>
    <div class="card">
      <h2>이번주 일정</h2>
  `;
  for (const cat of data.categories) {{
    const zero = cat.count === 0;
    html += `
      <div class="row ${{zero ? "zero" : ""}}">
        <span class="label">${{zero ? "🚨" : ""}}${{cat.emoji}} ${{esc(cat.name)}}</span>
        <span class="count">${{cat.count}}건</span>
      </div>`;
  }}
  html += `</div>`;

  html += `
    <div class="card">
      <h2>일정 없는 요일</h2>
      <div class="empty-days">${{data.emptyDays.length ? esc(data.emptyDays.join(", ")) : "매일 있음 ✅"}}</div>
    </div>
  `;

  const catStr = data.graphiteCategories.length ? ` (${{esc(data.graphiteCategories.join("/"))}})` : "";
  html += `
    <div class="card">
      <h2>저번주 미실행 일정</h2>
      <div class="row ${{data.graphiteCount > 0 ? "zero" : ""}}">
        <span class="label">⬛ 미실행</span>
        <span class="count">${{data.graphiteCount}}건${{catStr}}</span>
      </div>
      ${{data.graphiteEvents.length ? `<div class="events">${{data.graphiteEvents.map(esc).join("<br>")}}</div>` : ""}}
    </div>
  `;

  main.innerHTML = html;
  main.hidden = false;
  document.getElementById("gate").hidden = true;
}}

async function attempt() {{
  const pw = document.getElementById("pw").value;
  const err = document.getElementById("err");
  err.textContent = "";
  if (!pw) return;
  try {{
    const data = await tryUnlock(pw);
    try {{ sessionStorage.setItem("wr_pw", pw); }} catch (e) {{}}
    render(data);
  }} catch (e) {{
    err.textContent = "비밀번호가 올바르지 않습니다.";
  }}
}}

document.getElementById("unlock").addEventListener("click", attempt);
document.getElementById("pw").addEventListener("keydown", (e) => {{
  if (e.key === "Enter") attempt();
}});

(async () => {{
  try {{
    const cached = sessionStorage.getItem("wr_pw");
    if (cached) {{
      const data = await tryUnlock(cached);
      render(data);
    }}
  }} catch (e) {{
    try {{ sessionStorage.removeItem("wr_pw"); }} catch (e2) {{}}
  }}
}})();
</script>
</body>
</html>
"""
