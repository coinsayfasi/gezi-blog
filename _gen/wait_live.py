#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""new_urls.txt içindeki URL'ler production'da 200 dönene kadar bekler."""
import time
import urllib.error
import urllib.request
from pathlib import Path

NEW = Path(__file__).resolve().parent / "new_urls.txt"
ATTEMPTS = 18
WAIT_SECONDS = 10


def read_urls():
    if not NEW.exists():
        return []
    return [u.strip() for u in NEW.read_text(encoding="utf-8").splitlines() if u.strip()]


def is_live(url):
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "gezi-blog-deploy-check/1.0", "Cache-Control": "no-cache"},
    )
    try:
        with urllib.request.urlopen(req, timeout=20) as response:
            return response.status == 200
    except (urllib.error.URLError, TimeoutError):
        return False


def main():
    pending = read_urls()
    if not pending:
        print("Canlılık kontrolü: yeni URL yok")
        return

    for attempt in range(1, ATTEMPTS + 1):
        pending = [url for url in pending if not is_live(url)]
        if not pending:
            print("✓ Tüm yeni URL'ler production'da canlı")
            return
        print(f"Canlılık kontrolü {attempt}/{ATTEMPTS}: {len(pending)} URL bekleniyor")
        if attempt < ATTEMPTS:
            time.sleep(WAIT_SECONDS)

    raise SystemExit("Production bekleme süresi doldu: " + ", ".join(pending))


if __name__ == "__main__":
    main()
