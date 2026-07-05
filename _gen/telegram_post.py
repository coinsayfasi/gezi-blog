#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""gezi.tabserve.com.tr içeriğini Telegram kanalına postlar: (1) YENİ blog
yazıları (new_urls.txt) + (2) evergreen gezilecek-yerler sayfaları (döngüsel
drip, 10 gün tekrar-koruması). Mail/şifre YOK — sadece bot token.
Env: TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID (@kanal veya -100... id). DRIP_PER_RUN
(vars. 2). Token yoksa güvenli atlar."""
import os, json, datetime, urllib.parse, urllib.request
from pathlib import Path
from social_gezi_drip import candidates, local_html, meta  # altyapı reuse

GEN = Path(__file__).resolve().parent
NEW = GEN / "new_urls.txt"
STATE = GEN / "telegram_state.json"
API = "https://api.telegram.org"
TAGS = "#türkiye #gezi #seyahat #gezilecekyerler"
CTA_LINK = "https://coinsayfasi.github.io/go/routevia/"  # Routevia store (takipli)
PER_RUN = int(os.environ.get("DRIP_PER_RUN", "2"))


def tg(method, token, payload):
    data = urllib.parse.urlencode(payload).encode()
    req = urllib.request.Request(f"{API}/bot{token}/{method}", data=data, method="POST")
    return json.loads(urllib.request.urlopen(req, timeout=30).read())


def esc_html(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def send(token, chat, url):
    h = local_html(url)
    if not h:
        return False
    title = meta(h, r'og:title["\']\s+content=["\'](.*?)["\']',
                 r"<title>(.*?)</title>").split(" | ")[0]
    desc = meta(h, r'og:description["\']\s+content=["\'](.*?)["\']',
                r'name=["\']description["\']\s+content=["\'](.*?)["\']')
    if not title:
        return False
    text = (f"🗺️ <b>{esc_html(title)}</b>\n\n{esc_html(desc[:200])}\n\n{url}\n\n"
            f"📲 Routevia ile rota planla: {CTA_LINK}\n\n{TAGS}")
    tg("sendMessage", token, {
        "chat_id": chat, "text": text[:1000], "parse_mode": "HTML",
        "disable_web_page_preview": "false",  # og:image link kartı göster
    })
    print(f"  ✓ Telegram: {url}")
    return True


def load_state():
    if STATE.exists():
        try:
            return json.loads(STATE.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {"posted": {}}


def main():
    token = os.environ.get("TELEGRAM_BOT_TOKEN"); chat = os.environ.get("TELEGRAM_CHAT_ID")
    if not (token and chat):
        print("⚠️ TELEGRAM_BOT_TOKEN/CHAT_ID yok → Telegram atlandı"); return

    st = load_state()
    posted = st.get("posted", {})
    now = datetime.datetime.now(datetime.timezone.utc)

    # (1) YENİ blog yazıları
    new_urls = [u.strip() for u in NEW.read_text(encoding="utf-8").splitlines()
                if u.strip() and "/blog/" in u] if NEW.exists() else []
    for u in new_urls:
        if send(token, chat, u):
            posted[u] = now.isoformat()

    # (2) Evergreen gezilecek-yerler drip (döngüsel)
    cutoff = (now - datetime.timedelta(days=10)).isoformat()
    pending = [u for u in candidates() if posted.get(u, "") < cutoff and u not in new_urls]
    if not pending:
        pending = sorted(candidates(), key=lambda u: posted.get(u, ""))
    for u in pending[:PER_RUN]:
        if send(token, chat, u):
            posted[u] = now.isoformat()

    st["posted"] = posted
    STATE.write_text(json.dumps(st, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
