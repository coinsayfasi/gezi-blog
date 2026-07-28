#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""One-time sitewide retrofit for gezi-blog (Türkiye Gezi Rehberi):
1. Founder identity: Yunus Güneş -> Aycan Merve Güneş.
2. Cross-domain link fix: apps.tabserve.com.tr -> www.tabserve.com.tr (main Tabserve site).
3. Article schema author: Organization -> Person.
4. Author-box: brand-only text -> personal author line + link to central author profile.
Idempotent (safe to re-run).
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

SIMPLE_REPLACEMENTS = [
    ("Yunus Güneş", "Aycan Merve Güneş"),
    ("apps.tabserve.com.tr", "www.tabserve.com.tr"),
    (
        '"author": {"@type": "Organization", "name": "Tabserve"}',
        '"author": {"@type": "Person", "name": "Aycan Merve Güneş", "jobTitle": "Independent Full Stack Developer", "url": "https://www.tabserve.com.tr/author.html"}',
    ),
]

OLD_AUTHOR_BOX_HEAD = '<div class="author-box"><img class="ab-logo" src="/assets/logo.svg" alt="Tabserve" width="56" height="56"><div class="ab-body"><b>Türkiye Gezi Rehberi</b><p>Türkiye\'nin il il, ilçe ilçe gezilecek yerlerini paylaşıyoruz. Rotanı saniyede planlamak için Routevia uygulamasını ücretsiz indir.</p>'
NEW_AUTHOR_BOX_HEAD = '<div class="author-box"><img class="ab-logo" src="/assets/logo.svg" alt="Aycan Merve Güneş — Tabserve" width="56" height="56"><div class="ab-body"><b>Yazar: <a href="https://www.tabserve.com.tr/author.html">Aycan Merve Güneş</a></b><p style="color:var(--muted);font-size:13px;margin:2px 0 8px">Bağımsız Full Stack Developer · Tabserve Kurucusu</p><p>Türkiye\'nin il il, ilçe ilçe gezilecek yerlerini paylaşıyorum. Rotanı saniyede planlamak için Routevia uygulamasını ücretsiz indir.</p>'

EXTS = {".html", ".xml", ".json", ".txt"}
SKIP_DIRS = {"_gen", "__pycache__", ".git", "node_modules"}

changed_files = 0
total = 0
for path in ROOT.rglob("*"):
    if path.is_dir() or path.suffix not in EXTS:
        continue
    if any(part in SKIP_DIRS for part in path.parts):
        continue
    text = path.read_text(encoding="utf-8", errors="ignore")
    original = text
    for old, new in SIMPLE_REPLACEMENTS:
        text = text.replace(old, new)
    text = text.replace(OLD_AUTHOR_BOX_HEAD, NEW_AUTHOR_BOX_HEAD)
    if text != original:
        path.write_text(text, encoding="utf-8")
        changed_files += 1
        print(f"  {path.relative_to(ROOT)}")

print(f"\n{changed_files} dosya güncellendi.")
