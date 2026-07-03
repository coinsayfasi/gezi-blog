#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Mevcut yazılara 'Hızlı Bilgiler' kutusu ekler (ilk <h2>'den hemen önce).
İdempotent. Yeni yazılarda kutu PROMPT'tan otomatik gelir."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BLOG = ROOT / "blog"

FACTS = {
 "mardin-gezilecek-yerler-gezi-rehberi": ("2-3 gün", "Nisan-Haziran ve Eylül-Ekim", "Kişi başı orta bütçe", "Eski şehir yürünür; Midyat/Dara için araç veya dolmuş", "Uygun (taş sokaklar yokuşlu, bebek arabası zorlanır)", "Mardin Havalimanı (MQM), merkeze ~25 dk"),
 "alacati-gezilecek-yerler-gezi-rehberi": ("2 gün (hafta sonu ideal)", "Mayıs-Eylül (sörf için yaz ayları)", "Kişi başı orta-yüksek bütçe", "Önerilir — İzmir'den ~1 saat; merkez yürünür", "Uygun (taş sokaklar akşam kalabalık olur)", "İzmir Adnan Menderes (ADB), ~1 saat"),
 "cesme-gezilecek-yerler-gezi-rehberi": ("2-3 gün", "Haziran-Eylül", "Kişi başı orta-yüksek bütçe", "Önerilir — plajlar merkeze dağınık", "Çok uygun (Ilıca gibi sığ plajlar var)", "İzmir Adnan Menderes (ADB), ~1 saat"),
 "konya-gezilecek-yerler-gezi-rehberi": ("1-2 gün", "Nisan-Haziran ve Eylül-Ekim (Şeb-i Arus: Aralık)", "Kişi başı ekonomik bütçe", "Gerekmez — merkez yürünür, tramvay ağı iyi", "Uygun (müzeler ve geniş meydanlar)", "Konya Havalimanı (KYA), merkeze ~30 dk"),
 "bursa-gezilecek-yerler-gezi-rehberi": ("2 gün (kışın Uludağ için +1)", "Dört mevsim (kayak: Aralık-Mart)", "Kişi başı orta bütçe", "Şart değil — teleferik ve metro yeterli", "Çok uygun (teleferik ve Uludağ çocukların favorisi)", "Bursa Yenişehir (YEI); İstanbul'dan feribot alternatifi"),
 "trabzon-gezilecek-yerler-gezi-rehberi": ("2-3 gün (Uzungöl + Sümela dahil)", "Mayıs-Eylül (yaylalar için yaz)", "Kişi başı orta bütçe", "Önerilir — yayla ve Uzungöl için; günlük turlar alternatif", "Uygun (Uzungöl çevresi yürüyüşe elverişli)", "Trabzon Havalimanı (TZX), merkeze ~15 dk"),
 "izmir-gezilecek-yerler-gezi-rehberi": ("2-3 gün (Efes/Şirince için +1)", "Nisan-Haziran ve Eylül-Ekim", "Kişi başı orta bütçe", "Şehir içinde gerekmez (İZBAN/metro); Efes-Çeşme için önerilir", "Uygun (Kordon ve sahil bandı bebek arabası dostu)", "İzmir Adnan Menderes (ADB)"),
 "antalya-gezilecek-yerler-gezi-rehberi": ("3-4 gün", "Nisan-Haziran ve Eylül-Kasım (yaz öğlenleri çok sıcak)", "Kişi başı orta bütçe", "Kaleiçi için gerekmez; Aspendos/Side/Düden için önerilir", "Çok uygun (plajlar ve akvaryum)", "Antalya Havalimanı (AYT), merkeze ~25 dk"),
 "kapadokya-gezi-rehberi-en-iyi-gezilecek-yerler-ve-ipuclari": ("2-3 gün", "Nisan-Haziran ve Eylül-Kasım", "Kişi başı orta-yüksek bütçe (balon ayrı tutulmalı)", "Önerilir — vadiler dağınık; günlük turlar alternatif", "Uygun (balon turlarında genelde 6 yaş sınırı var)", "Nevşehir (NAV) ~40 dk; Kayseri (ASR) ~1 saat"),
}

def box(f):
    gun, donem, butce, arac, cocuk, hava = f
    return ('<div class="quickfacts"><h2>Hızlı Bilgiler</h2><ul>'
            f'<li><strong>Kaç gün yeterli:</strong> {gun}</li>'
            f'<li><strong>En iyi dönem:</strong> {donem}</li>'
            f'<li><strong>Ortalama bütçe:</strong> {butce}</li>'
            f'<li><strong>Araç gerekli mi:</strong> {arac}</li>'
            f'<li><strong>Çocukla uygun mu:</strong> {cocuk}</li>'
            f'<li><strong>En yakın havalimanı:</strong> {hava}</li>'
            '</ul></div>')

changed = 0
for slug, f in FACTS.items():
    p = BLOG / slug / "index.html"
    if not p.exists():
        print(f"  ⚠️ yok: {slug}"); continue
    html = p.read_text(encoding="utf-8")
    if "quickfacts" in html:
        print(f"  = zaten var: {slug}"); continue
    a0 = html.find("<article")
    h2 = html.find("<h2", a0)
    if h2 == -1:
        print(f"  ⚠️ h2 yok: {slug}"); continue
    html = html[:h2] + box(f) + "\n" + html[h2:]
    p.write_text(html, encoding="utf-8")
    changed += 1
    print(f"  ✓ {slug}")
print(f"\n✓ {changed}/{len(FACTS)} yazıya Hızlı Bilgiler eklendi")
