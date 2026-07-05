#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Yeni blog yazısı yayınlanınca Routevia kullanıcılarına FCM push atar.
generate.py'nin yazdığı _gen/new_urls.txt'ten okur; günde en fazla 1 bildirim
(kullanıcıyı sıkmamak için — birden çok yazı varsa yalnızca ilki gönderilir).
Env: FIREBASE_SA (routevia-prod service account JSON; yoksa atlar)."""
import os, re, json, html, urllib.request
from pathlib import Path

GEN = Path(__file__).resolve().parent
ROOT = GEN.parent
NEW = GEN / "new_urls.txt"
TOPIC = "blog"
esc = html.unescape


def meta(h, *pats):
    for p in pats:
        m = re.search(p, h, re.I | re.S)
        if m:
            return esc(re.sub(r"\s+", " ", m.group(1)).strip())
    return ""


def main():
    sa_json = os.environ.get("FIREBASE_SA")
    urls = [u.strip() for u in NEW.read_text(encoding="utf-8").splitlines() if u.strip()] if NEW.exists() else []
    urls = [u for u in urls if "/blog/" in u]
    if not urls:
        print("Push: yeni blog yazısı yok"); return
    if not sa_json:
        print("⚠️ FIREBASE_SA yok → push atlandı"); return

    url = urls[0]
    slug = url.rstrip("/").split("/blog/")[-1]
    p = ROOT / "blog" / slug / "index.html"
    h = p.read_text(encoding="utf-8", errors="ignore") if p.exists() else ""
    title = meta(h, r"<title>(.*?)</title>") or "Yeni gezi yazısı yayında"
    title = re.sub(r"\s*[|·]\s*[^|·]*$", "", title).strip()[:60]
    desc = meta(h, r'<meta\s+name="description"\s+content="(.*?)"')[:120] or "Yeni rotalar ve gezilecek yerler seni bekliyor."

    from google.oauth2 import service_account
    import google.auth.transport.requests
    creds = service_account.Credentials.from_service_account_info(
        json.loads(sa_json), scopes=["https://www.googleapis.com/auth/firebase.messaging"])
    creds.refresh(google.auth.transport.requests.Request())
    project = json.loads(sa_json)["project_id"]

    body = {"message": {
        "topic": TOPIC,
        "notification": {"title": f"🗺️ {title}", "body": desc},
        "data": {"url": url, "type": "blog"},
        "apns": {"payload": {"aps": {"sound": "default"}}},
    }}
    req = urllib.request.Request(
        f"https://fcm.googleapis.com/v1/projects/{project}/messages:send",
        data=json.dumps(body).encode(),
        headers={"Authorization": f"Bearer {creds.token}", "Content-Type": "application/json"},
        method="POST")
    resp = json.loads(urllib.request.urlopen(req, timeout=30).read())
    print(f"✓ Push gönderildi ({TOPIC}): {title} → {resp.get('name', resp)}")


if __name__ == "__main__":
    main()
