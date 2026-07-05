#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""gezi.tabserve.com.tr içeriğini Mastodon'a postlar: (1) YENİ blog yazıları
(new_urls.txt) + (2) evergreen gezilecek-yerler sayfaları (döngüsel drip, 10 gün
tekrar-koruması). Mail/şifre YOK — sadece access token.
Env: MASTODON_INSTANCE (ör. https://mastodon.social), MASTODON_TOKEN,
DRIP_PER_RUN (vars. 2). Token/instance yoksa güvenli atlar. Mastodon linkten
otomatik og önizleme kartı üretir → gezi görseli+başlığı görünür."""
import os, json, datetime, urllib.parse, urllib.request
from pathlib import Path
from social_gezi_drip import candidates, local_html, meta  # altyapı reuse

GEN = Path(__file__).resolve().parent
NEW = GEN / "new_urls.txt"
STATE = GEN / "mastodon_state.json"
TAGS = "#türkiye #gezi #seyahat #gezilecekyerler"
CTA_LINK = "https://coinsayfasi.github.io/go/routevia/"  # Routevia store (takipli)
PER_RUN = int(os.environ.get("DRIP_PER_RUN", "2"))


def toot(instance, token, status):
    data = urllib.parse.urlencode({"status": status, "visibility": "public",
                                   "language": "tr"}).encode()
    req = urllib.request.Request(
        f"{instance.rstrip('/')}/api/v1/statuses", data=data, method="POST",
        headers={"Authorization": f"Bearer {token}"})
    return json.loads(urllib.request.urlopen(req, timeout=30).read())


def send(instance, token, url):
    h = local_html(url)
    if not h:
        return False
    title = meta(h, r'og:title["\']\s+content=["\'](.*?)["\']',
                 r"<title>(.*?)</title>").split(" | ")[0]
    desc = meta(h, r'og:description["\']\s+content=["\'](.*?)["\']',
                r'name=["\']description["\']\s+content=["\'](.*?)["\']')
    if not title:
        return False
    status = (f"🗺️ {title}\n\n{desc[:180]}\n\n{url}\n\n"
              f"📲 Routevia: {CTA_LINK}\n\n{TAGS}")[:480]
    toot(instance, token, status)
    print(f"  ✓ Mastodon: {url}")
    return True


def load_state():
    if STATE.exists():
        try:
            return json.loads(STATE.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {"posted": {}}


def main():
    instance = os.environ.get("MASTODON_INSTANCE"); token = os.environ.get("MASTODON_TOKEN")
    if not (instance and token):
        print("⚠️ MASTODON_INSTANCE/TOKEN yok → Mastodon atlandı"); return

    st = load_state()
    posted = st.get("posted", {})
    now = datetime.datetime.now(datetime.timezone.utc)

    # (1) YENİ blog yazıları
    new_urls = [u.strip() for u in NEW.read_text(encoding="utf-8").splitlines()
                if u.strip() and "/blog/" in u] if NEW.exists() else []
    for u in new_urls:
        if send(instance, token, u):
            posted[u] = now.isoformat()

    # (2) Evergreen gezilecek-yerler drip (döngüsel)
    cutoff = (now - datetime.timedelta(days=10)).isoformat()
    pending = [u for u in candidates() if posted.get(u, "") < cutoff and u not in new_urls]
    if not pending:
        pending = sorted(candidates(), key=lambda u: posted.get(u, ""))
    for u in pending[:PER_RUN]:
        if send(instance, token, u):
            posted[u] = now.isoformat()

    st["posted"] = posted
    STATE.write_text(json.dumps(st, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
