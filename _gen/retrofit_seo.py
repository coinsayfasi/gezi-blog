#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Mevcut yazılara retroaktif SEO: FAQPage JSON-LD + iç linkler + İlgili Rehberler.
Tek seferlik; idempotent (ikinci çalıştırma değişiklik yapmaz).
Kullanım: python _gen/retrofit_seo.py
"""
import json, re, html
from pathlib import Path

from generate import faq_schema, add_internal_links, related_block

ROOT = Path(__file__).resolve().parents[1]
BLOG = ROOT / "blog"
POSTS = json.loads((ROOT / "_gen" / "posts.json").read_text(encoding="utf-8"))

changed = 0
for post in POSTS:
    slug = post["slug"]
    f = BLOG / slug / "index.html"
    if not f.exists():
        print(f"  ⚠️ yok: {slug}")
        continue
    page = f.read_text(encoding="utf-8")
    orig = page

    # Makale gövdesini izole et (nav/footer'a dokunma)
    a0 = page.find("<article")
    a1 = page.find("</article>")
    if a0 == -1 or a1 == -1:
        print(f"  ⚠️ article bulunamadı: {slug}")
        continue
    art = page[a0:a1]

    # 1) FAQPage JSON-LD (share çubuğundan öncesi = gerçek gövde)
    if "FAQPage" not in page:
        body_end = art.find('<div class="share">')
        faq = faq_schema(art[:body_end] if body_end != -1 else art)
        if faq:
            tag = '<script type="application/ld+json">' + json.dumps(faq, ensure_ascii=False) + "</script>\n"
            page = page.replace("</head>", tag + "</head>", 1)
            art = page[page.find("<article"):page.find("</article>")]

    # 2) İç linkler (yalnızca article içinde)
    linked = add_internal_links(art, POSTS, slug)
    if linked != art:
        page = page.replace(art, linked, 1)
        art = linked

    # 3) İlgili Rehberler bloğu (share çubuğunun hemen önüne)
    if "İlgili Gezi Rehberleri" not in page:
        rel = related_block(POSTS, slug)
        if rel and '<div class="share">' in page:
            page = page.replace('<div class="share">', rel + '<div class="share">', 1)

    if page != orig:
        f.write_text(page, encoding="utf-8")
        changed += 1
        print(f"  ✓ {slug}")
    else:
        print(f"  = değişiklik yok: {slug}")

print(f"\n✓ {changed}/{len(POSTS)} yazı güncellendi")
