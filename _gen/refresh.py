#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Content Refresh: en eski yazıyı EN GÜNCEL motorla aynı slug'da yeniden üretir.
- 45+ gün önce yenilenen (veya hiç yenilenmeyen) yazılar sıraya girer
- Aynı URL korunur, içerik v-güncel motor kalitesine yükselir, dateModified tazelenir
- Görseller korunur (fetch_hero mevcunu atlar), sonrasında index_ping çalışır
Env: GEMINI_API_KEY/ANTHROPIC_API_KEY, REFRESH_SLUG (ops: belirli yazıyı zorla), REFRESH_DAYS (vars 45)
"""
import os, sys, json, datetime
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
import generate as G

GEN = Path(__file__).parent
RSTATE_F = GEN / "refresh_state.json"
DAYS = int(os.environ.get("REFRESH_DAYS", "45"))

def main():
    posts = json.loads((GEN / "posts.json").read_text(encoding="utf-8"))
    rstate = json.loads(RSTATE_F.read_text(encoding="utf-8")) if RSTATE_F.exists() else {}
    force = os.environ.get("REFRESH_SLUG", "").strip()

    def last_touch(p):
        return rstate.get(p["slug"]) or p.get("date", "2026-06-01")

    if force:
        cand = [p for p in posts if p["slug"] == force]
        if not cand: sys.exit(f"slug bulunamadı: {force}")
    else:
        cutoff = (datetime.date.today() - datetime.timedelta(days=DAYS)).isoformat()
        cand = sorted([p for p in posts if last_touch(p) <= cutoff], key=last_touch)[:1]
        if not cand:
            print(f"↻ Yenilenecek yazı yok ({DAYS} günden eski yok)."); return

    target = cand[0]
    slug = target["slug"]
    city = target["title"].split()[0].rstrip(":,")
    kw = f"{city} gezilecek yerler"
    print(f"↻ REFRESH: /blog/{slug}/  (anahtar: {kw})")

    prompt = G.PROMPT.format(kw=kw,
        angle=f"{city} için 2026 güncel, kapsamlı gezi rehberi (mevcut yazının tazelenmiş hali — daha derin ve güncel)",
        one=G.APPS["routevia"]["one"], name=G.APPS["routevia"]["name"])
    d = None
    for tryi in range(2):
        txt = G.call_llm(prompt if tryi == 0 else prompt + "\n\nYour previous attempt failed validation. Ensure 1000+ WORDS and the required sections.")
        try: c = G.parse_json(txt)
        except Exception as e: print(f"  JSON hatası: {e}"); continue
        errs, wc, hh = G.validate(c, kw)
        if not errs: d = c; print(f"  ✓ {wc} kelime"); break
        print(f"  ✗ {', '.join(errs)}")
    if not d: sys.exit("  ⚠️ kalite tutmadı, yenileme iptal (eski yazı korunur)")

    d["slug"] = slug  # URL SABİT
    iqs = d.get("img_queries") or []
    G.fetch_hero((iqs[0] if iqs else f"{city} Turkey travel"), slug)  # mevcut görsel varsa atlar
    if len(iqs) > 1:
        d["body"] = G.insert_inpost_images(d["body"], slug, iqs[1:3], d["title"])
    G.write_post(d, "routevia", posts)

    # posts.json: başlık/özet tazele, sıra ve tarih korunur
    for p in posts:
        if p["slug"] == slug:
            p["title"], p["desc"] = d["title"], d["meta_description"]
    (GEN / "posts.json").write_text(json.dumps(posts, ensure_ascii=False, indent=1), encoding="utf-8")
    rstate[slug] = datetime.date.today().isoformat()
    RSTATE_F.write_text(json.dumps(rstate, ensure_ascii=False, indent=1), encoding="utf-8")
    G.rebuild_index(posts)
    (GEN / "new_urls.txt").write_text(f"{G.SITE}/blog/{slug}/", encoding="utf-8")  # index_ping için
    print(f"✓ yenilendi: /blog/{slug}/")

if __name__ == "__main__":
    main()
