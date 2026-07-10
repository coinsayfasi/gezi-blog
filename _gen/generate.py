#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Tabserve blog — AI ile ÖZGÜN, tam-SEO yazı üretici (Claude API, stdlib).
Kurallar: hedef anahtar kelime=title=H1; H2→H3→H4(→H5); 600+ KELİME; özgün (spin değil);
app CTA + internal link; Article schema. Doğrulama geçmezse YAYINLAMAZ.
Kullanım:
  ANTHROPIC_API_KEY=... python _gen/generate.py            # 1 yeni yazı üret+yayınla
  python _gen/generate.py --rebuild                         # API'siz: listeleme+sitemap yeniden kur
Env: ANTHROPIC_API_KEY, BLOG_MODEL (ops, varsayılan claude-sonnet-4-6), BLOG_COUNT (ops)."""
import os, re, sys, json, html, time, datetime, urllib.request, urllib.error, urllib.parse
from pathlib import Path

SOCIAL = [("YouTube","https://youtube.com/@tabserve"),("Instagram","https://instagram.com/tabservee"),
          ("TikTok","https://tiktok.com/@tabserve"),("Bluesky","https://bsky.app/profile/tabserve.bsky.social"),("Pinterest","https://pinterest.com/nedir_nasil")]

def _svg(d): return f'<svg viewBox="0 0 24 24" width="19" height="19" fill="currentColor" aria-hidden="true"><path d="{d}"/></svg>'
ICON = {
 "X":_svg("M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z"),
 "f":_svg("M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z"),
 "P":_svg("M12.017 0C5.396 0 .029 5.367.029 11.987c0 5.079 3.158 9.417 7.618 11.162-.105-.949-.199-2.403.041-3.439.219-.937 1.406-5.957 1.406-5.957s-.359-.72-.359-1.781c0-1.663.967-2.911 2.168-2.911 1.024 0 1.518.769 1.518 1.688 0 1.029-.653 2.567-.992 3.992-.285 1.193.6 2.165 1.775 2.165 2.128 0 3.768-2.245 3.768-5.487 0-2.861-2.063-4.869-5.008-4.869-3.41 0-5.409 2.562-5.409 5.199 0 1.033.394 2.143.889 2.741.099.12.112.225.085.345-.09.375-.293 1.199-.334 1.363-.053.225-.172.271-.402.165-1.495-.69-2.433-2.878-2.433-4.646 0-3.776 2.748-7.252 7.92-7.252 4.158 0 7.392 2.967 7.392 6.923 0 4.135-2.607 7.462-6.233 7.462-1.214 0-2.354-.629-2.758-1.379l-.749 2.848c-.269 1.045-1.004 2.352-1.498 3.146 1.123.345 2.306.535 3.55.535 6.607 0 11.985-5.365 11.985-11.987C23.97 5.39 18.592.026 11.985.026L12.017 0z"),
 "W":_svg("M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51l-.57-.01c-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.71.306 1.263.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884"),
 "in":_svg("M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.848 3.37-1.848 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433a2.062 2.062 0 01-2.063-2.065 2.064 2.064 0 112.063 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z"),
 "YouTube":_svg("M23.498 6.186a3.016 3.016 0 0 0-2.122-2.136C19.505 3.545 12 3.545 12 3.545s-7.505 0-9.377.505A3.017 3.017 0 0 0 .502 6.186C0 8.07 0 12 0 12s0 3.93.502 5.814a3.016 3.016 0 0 0 2.122 2.136c1.871.505 9.376.505 9.376.505s7.505 0 9.377-.505a3.015 3.015 0 0 0 2.122-2.136C24 15.93 24 12 24 12s0-3.93-.502-5.814zM9.545 15.568V8.432L15.818 12l-6.273 3.568z"),
 "Instagram":_svg("M12 2.163c3.204 0 3.584.012 4.85.07 3.252.148 4.771 1.691 4.919 4.919.058 1.265.069 1.645.069 4.849 0 3.205-.012 3.584-.069 4.849-.149 3.225-1.664 4.771-4.919 4.919-1.266.058-1.644.07-4.85.07-3.204 0-3.584-.012-4.849-.07-3.26-.149-4.771-1.699-4.919-4.92-.058-1.265-.07-1.644-.07-4.849 0-3.204.013-3.583.07-4.849.149-3.227 1.664-4.771 4.919-4.919 1.266-.057 1.645-.069 4.849-.069M12 0C8.741 0 8.333.014 7.053.072 2.695.272.273 2.69.073 7.052.014 8.333 0 8.741 0 12s.014 3.668.072 4.948c.2 4.358 2.618 6.78 6.98 6.98C8.333 23.986 8.741 24 12 24s3.668-.014 4.948-.072c4.354-.2 6.782-2.618 6.979-6.98.059-1.28.073-1.689.073-4.948s-.014-3.667-.072-4.947c-.196-4.354-2.617-6.78-6.979-6.98C15.668.014 15.259 0 12 0m0 5.838a6.162 6.162 0 100 12.324 6.162 6.162 0 000-12.324M12 16a4 4 0 110-8 4 4 0 010 8m6.406-11.845a1.44 1.44 0 100 2.881 1.44 1.44 0 000-2.881"),
 "TikTok":_svg("M12.525.02c1.31-.02 2.61-.01 3.91-.02.08 1.53.63 3.09 1.75 4.17 1.12 1.11 2.7 1.62 4.24 1.79v4.03c-1.44-.05-2.89-.35-4.2-.97-.57-.26-1.1-.59-1.62-.93-.01 2.92.01 5.84-.02 8.75-.08 1.4-.54 2.79-1.35 3.94-1.31 1.92-3.58 3.17-5.91 3.21-1.43.08-2.86-.31-4.08-1.03-2.02-1.19-3.44-3.37-3.65-5.71-.02-.5-.03-1-.01-1.49.18-1.9 1.12-3.72 2.58-4.96 1.66-1.44 3.98-2.13 6.15-1.72.02 1.48-.04 2.96-.04 4.44-.99-.32-2.15-.23-3.02.37-.63.41-1.11 1.04-1.36 1.75-.21.51-.15 1.07-.14 1.61.24 1.64 1.82 3.02 3.5 2.87 1.12-.01 2.19-.66 2.77-1.61.19-.33.4-.67.41-1.06.1-1.79.06-3.57.07-5.36.01-4.03-.01-8.05.02-12.07z"),
 "Bluesky":_svg("M12 10.8c-1.087-2.114-4.046-6.053-6.798-7.995C2.566.944 1.561 1.266.902 1.565.139 1.908 0 3.08 0 3.768c0 .69.378 5.65.624 6.479.815 2.736 3.713 3.66 6.383 3.364-3.912.58-7.387 2.005-2.83 7.078 5.013 5.19 6.87-1.113 7.823-4.308.953 3.195 2.05 9.271 7.733 4.308 4.267-4.308 1.172-6.498-2.74-7.078 2.67.297 5.568-.628 6.383-3.364.246-.828.624-5.79.624-6.478 0-.69-.139-1.861-.902-2.206-.659-.298-1.664-.62-4.3 1.24C16.046 4.748 13.087 8.687 12 10.8Z"),
}
ICON["Pinterest"] = ICON["P"]

def post_extras(url, title):
    """Alt paylaş çubuğu + yazar kutusu + sol kayan çubuk (SVG ikonlu)."""
    u = urllib.parse.quote(url, safe=''); t = urllib.parse.quote(title, safe='')
    S = [("X",f"https://twitter.com/intent/tweet?url={u}&amp;text={t}"),("f",f"https://www.facebook.com/sharer/sharer.php?u={u}"),
         ("P",f"https://pinterest.com/pin/create/button/?url={u}&amp;description={t}"),("W",f"https://wa.me/?text={t}%20{u}"),
         ("in",f"https://www.linkedin.com/sharing/share-offsite/?url={u}")]
    lbl = {"X":"X","f":"Facebook","P":"Pinterest","W":"WhatsApp","in":"LinkedIn"}
    share = '<div class="share"><span>Bu yazıyı paylaş:</span>' + ''.join(
        f'<a class="ico" href="{h}" target="_blank" rel="noopener" aria-label="{lbl[n]}">{ICON[n]}</a>' for n,h in S) + '</div>'
    follow = ''.join(f'<a class="ico" href="{lu}" target="_blank" rel="noopener" aria-label="{ln}">{ICON.get(ln,ln)}</a>' for ln,lu in SOCIAL)
    author = ('<div class="author-box"><img class="ab-logo" src="/assets/logo.svg" alt="Tabserve" width="56" height="56">'
              '<div class="ab-body"><b>Türkiye Gezi Rehberi</b><p>Türkiye\'nin il il, ilçe ilçe gezilecek yerlerini paylaşıyoruz. '
              f'Rotanı saniyede planlamak için Routevia uygulamasını ücretsiz indir.</p><div class="follow"><span>Bizi takip et:</span>{follow}</div></div></div>')
    rail = '<div class="share-rail" aria-label="Paylaş">' + ''.join(
        f'<a href="{h}" target="_blank" rel="noopener" aria-label="{lbl[n]}">{ICON[n]}</a>' for n,h in S) + '</div>'
    return share + author, rail

ROOT = Path(__file__).resolve().parents[1]
GEN = ROOT / "_gen"
BLOG = ROOT / "blog"
TOPICS = json.loads((GEN / "topics.json").read_text(encoding="utf-8"))
POSTS_F = GEN / "posts.json"
STATE_F = GEN / "state.json"
SITE = "https://gezi.tabserve.com.tr"
# Sağlayıcı: GEMINI (ücretsiz) öncelikli; yoksa Claude.
# Fallback zinciri — bir model deprecate olursa sıradakini dener (routevia prod gemini-flash-latest kullanıyor).
GEMINI_CANDIDATES = [m for m in [
    os.environ.get("GEMINI_MODEL"), "gemini-flash-latest", "gemini-3.5-flash",
    "gemini-flash-lite-latest", "gemini-3.1-flash-lite", "gemini-2.5-flash", "gemini-pro-latest",
] if m]
CLAUDE_MODEL = os.environ.get("BLOG_MODEL", "claude-sonnet-4-6")
_gemini_ok = None  # çalıştığı doğrulanan model (cache)

APPS = {
 "routevia":{"tag":"Türkiye · Gezi",
   "cta":'<div class="appcta"><b>🚗 Rotanı saniyede planla — Routevia</b><p>Routevia, Türkiye\'nin il il, ilçe ilçe gezilecek yerlerini keşfetmeni ve yapay zekâ ile rotanı saniyede planlamanı sağlar. Ücretsiz, iOS &amp; Android.</p><div class="appbadges"><a href="https://apps.apple.com/app/id6761003117" rel="noopener" aria-label="Routevia — App Store">&#63743; App Store</a><a href="https://play.google.com/store/apps/details?id=com.yunusgunes.routevia" rel="noopener" aria-label="Routevia — Google Play">&#9654; Google Play</a><a class="ghost" href="https://coinsayfasi.github.io/routevia-app/">Daha fazla bilgi →</a></div></div>',
   "name":"Routevia","one":"Türkiye gezi uygulaması Routevia (il il gezilecek yerler + yapay zekâ rota planı)"},
}

def load(p, d): return json.loads(p.read_text(encoding="utf-8")) if p.exists() else d
def slugify(s):
    tr = str.maketrans("çğıíöşúüÇĞİÍÖŞÚÜ", "cgiiosuucgiiosuu")
    return re.sub(r"[^a-z0-9]+", "-", s.translate(tr).lower()).strip("-")[:70]
def words(htmlstr): return len(re.sub(r"\s+"," ",re.sub(r"<[^>]+>"," ",htmlstr)).split())

PROMPT = """Sen uzman bir SEO içerik yazarısın. gezi.tabserve.com.tr (Türkiye gezi blogu) için ÖZGÜN bir TÜRKÇE gezi rehberi yazıyorsun.

HEDEF ANAHTAR KELİME: "{kw}"
AÇI: {angle}
Yazı tek başına gerçekten faydalı olmalı; sonuna otomatik küçük bir uygulama tanıtım kutusu (Routevia) eklenecek — sen sadece makale gövdesini yaz. ({one})

KESİN KURALLAR — hepsine uy:
1. Hedef anahtar kelime "{kw}" BAŞLIKTA geçmeli ve net konu olmalı. Başlık aynı zamanda H1'dir — <h1> YAZMA.
2. Uzunluk: 2500-3000 KELİME gerçek gövde metni (kelime say, karakter değil). Dolgu YAPMA — her bölüm gerçek, somut, özgün bilgi içersin (fiyat aralıkları, süreler, mesafeler, pratik ipuçları, örnek rotalar). Uzunluğu 8-11 zengin H2 bölümüyle doğal doldur.
3. ZORUNLU BÖLÜM YAPISI — büyük gezi siteleri gibi, her biri ayrı <h2> (anahtar kelime varyasyonlu) olacak:
   - EN BAŞA: <div class="tldr"><b>⚡ 30 saniyede ...</b><p>3-4 cümlelik öz: neden gidilir, kaç gün, en iyi dönem, tek cümlelik bütçe hissi.</p></div>
   - Kısa giriş paragrafı (H2'siz)
   - <h2> En iyi gezilecek yerler (4-7 gerçek yer, her biri <h3> + açıklama: giriş nereden, ne kadar sürer, çocukla uygun mu)
   - <h2> Aylara göre hava durumu ve en iyi dönem (mevsim mevsim iklim karakteri + hangi ay ne için ideal)
   - <h2> Örnek rotalar (<h3> ile üç rota: "İlk kez gelenler için 1 günlük rota", "2 günlük rota", "Çocuklu aile rotası" — saat aralıklı somut akış)
   - <h2> Kaç gün yeterli? (önerilen süre)
   - <h2> Nasıl gidilir / ulaşım (uçak/otobüs/araç; şehir içi ulaşım ipuçları)
   - <h2> Nerede kalınır (semt/bölge önerisi; kime hangi bölge uyar)
   - <h2> Ne yenir? (yöresel lezzetler + nerede aranır)
   - <h2> En iyi fotoğraf ve gün batımı noktaları (3-5 nokta; hangi saatte, hangi açıdan)
   - <h2> Öne çıkan yerler karşılaştırması: <table> ile (sütunlar: Yer | Ayrılacak süre | Giriş | Kimlere ideal — Giriş'te "ücretsiz/ücretli/MüzeKart" gibi kategorik yaz, rakam uydurma)
   - <h2> Bütçe rehberi (ekonomik/orta/konfor için GENEL günlük aralık mantığı — kesin fiyat uydurmadan oran ve tasarruf ipuçlarıyla; <ul>)
   - <h2> Turist tuzakları ve güvenlik (bölgeye özgü dolandırıcılık/tuzak uyarıları, pazarlık, taksi, "hediye" tuzağı vb. — SOMUT)
   - <h2> En sık yapılan hatalar (gezginlerin bu destinasyonda yaptığı 4-6 gerçek hata + doğrusu; <ul>)
   - <h2> Bu şehir sana göre mi? (gezgin profiline göre dürüst uygunluk: aileler, çiftler, solo gezginler, doğa tutkunları, tarih meraklıları, gastronomi avcıları — kime ÇOK uyar, kime uymayabilir; <ul> ile)
   - <h2> Pratik gezi ipuçları (madde madde <ul>; MUTLAKA şunları da kapsa: otopark durumu, toplu taşıma, engelli/bebek arabası erişilebilirliği, acil durumda bilinmesi gerekenler)
   H2 altında uygun yerlerde <h3>/<h4> kullan. Mantıklı yuvalama.
4. EN SONDA <h2>Sık Sorulan Sorular</h2> bölümü: 8-10 UZUN KUYRUK soru (ör. 'X kaç günde gezilir?', 'MüzeKart geçerli mi?', 'Çocukla gidilir mi?', 'Yazın gidilir mi?', 'Araç kiralamak şart mı?') — her soru <h3>, cevabı <p> (2-3 cümle, net). Sonra kısa kapanış paragrafı.
5. ÖZGÜN ve SOMUT — gerçek yer adları, gerçek bilgi. İstatistik/kesin fiyat/alıntı UYDURMA (genel bütçe ipucu olur). Tekrar yok, "spin"/genel dolgu yok.
5b. KLİŞE YASAK: "unutulmaz deneyim", "büyüleyici", "mutlaka görülmeli", "eşsiz güzellik", "adeta", "cennet köşesi" gibi kalıpları KULLANMA. Bunun yerine SOMUT fayda yaz: hangi kapıdan girilir, sabah mı öğleden sonra mı gidilir, ne kadar sürer, yürüme mesafesi, çocukla/yaşlıyla uygun mu, otopark/toplu taşıma durumu.
5c. GİRİŞTEN HEMEN SONRA "Hızlı Bilgiler" kutusu ekle — tam şu HTML yapısıyla:
<div class="quickfacts"><h2>Hızlı Bilgiler</h2><ul>
<li><strong>Kaç gün yeterli:</strong> ...</li>
<li><strong>En iyi dönem:</strong> ...</li>
<li><strong>Ortalama bütçe:</strong> ... (genel aralık, "kişi başı orta bütçe" gibi)</li>
<li><strong>Araç gerekli mi:</strong> ...</li>
<li><strong>Çocukla uygun mu:</strong> ...</li>
<li><strong>En yakın havalimanı:</strong> ...</li>
</ul></div>
6. SADECE şu etiketler: h2, h3, h4, h5, p, ul, li, strong, a, table, thead, tbody, tr, th, td ve yalnızca baştaki özet için <div class="tldr">. Markdown yok, <h1> yok, <html>/<head>/<style> yok.
7. 1-2 dış OTORİTE linki ekle (resmi turizm/kültür sitesi, .gov.tr ya da ilgili Wikipedia maddesi). Sadece var olduğundan EMİN olduğun stabil URL'ler — https://tr.wikipedia.org/wiki/<Konu> tercih et. Deep URL UYDURMA. Cümle içinde doğal yerleştir, başlıkta değil.

SADECE geçerli minified JSON çıktısı ver (kod bloğu/yorum yok), tam şu anahtarlar:
{{"title":"...","meta_description":"max 155 karakter, anahtar kelimeyi içersin","keywords":"4-6 virgülle ayrılmış anahtar kelime","slug":"baslıktan-kebab-case-ascii","lat":"şehir merkezi enlem (ondalık)","lon":"boylam","img_queries":["3 ayrı stok foto araması, her biri 2-4 İNGİLİZCE kelime, yazının FARKLI bölümlerini birebir karşılayan somut sahneler: 1) kapak manzarası 2) yemek/çarşı/kültür 3) doğa/detay (örn: [\"Sanliurfa Gobeklitepe\",\"Urfa kebab food\",\"Balikligol pool Urfa\"])"],"body":"makale HTML'i"}}"""

def _post(url, body, headers):
    req = urllib.request.Request(url, data=json.dumps(body).encode(), headers=headers, method="POST")
    for attempt in range(4):
        try:
            return json.loads(urllib.request.urlopen(req, timeout=90).read())
        except urllib.error.HTTPError as e:
            if e.code in (429,529,500,503) and attempt < 3:
                time.sleep(8*(attempt+1)); continue
            raise
    raise RuntimeError("API başarısız")

def call_gemini(prompt, key):
    global _gemini_ok
    cands = ([_gemini_ok] if _gemini_ok else []) + [m for m in GEMINI_CANDIDATES if m != _gemini_ok]
    last = None
    for m in cands:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{m}:generateContent?key={key}"
        try:
            r = _post(url, {"contents":[{"parts":[{"text":prompt}]}],
                            "generationConfig":{"maxOutputTokens":8192,"temperature":0.75,"thinkingConfig":{"thinkingBudget":0}}},
                      {"content-type":"application/json"})
            cands_out = r.get("candidates")
            if not cands_out or not cands_out[0].get("content",{}).get("parts"):
                last = RuntimeError(f"{m}: boş yanıt ({r.get('promptFeedback','')})"); continue
            _gemini_ok = m
            print(f"  (model: {m})")
            return cands_out[0]["content"]["parts"][0]["text"]
        except urllib.error.HTTPError as e:
            if e.code == 404:  # model deprecate/erişilemez → sıradakini dene
                last = e; continue
            raise
    raise last or RuntimeError("hiçbir Gemini modeli çalışmadı")

def call_claude(prompt, key):
    r = _post("https://api.anthropic.com/v1/messages",
        {"model":CLAUDE_MODEL,"max_tokens":2600,"messages":[{"role":"user","content":prompt}]},
        {"x-api-key":key,"anthropic-version":"2023-06-01","content-type":"application/json"})
    return r["content"][0]["text"]

def call_llm(prompt):
    gk = os.environ.get("GEMINI_API_KEY")
    if gk: return call_gemini(prompt, gk)
    ck = os.environ.get("ANTHROPIC_API_KEY")
    if ck: return call_claude(prompt, ck)
    sys.exit("⚠️ GEMINI_API_KEY (ücretsiz) veya ANTHROPIC_API_KEY gerekli")

def parse_json(txt):
    txt = txt.strip()
    if txt.startswith("```"): txt = re.sub(r"^```\w*\s*|\s*```$","",txt)
    i,j = txt.find("{"), txt.rfind("}")
    return json.loads(txt[i:j+1])

def validate(d, kw):
    b = d.get("body","")
    wc = words(b.replace("{{APP_CTA}}",""))
    h2,h3,h4 = len(re.findall(r"<h2",b)),len(re.findall(r"<h3",b)),len(re.findall(r"<h4",b))
    errs=[]
    if wc < 2000: errs.append(f"kelime {wc}<2000")
    if h2 < 3: errs.append(f"H2 {h2}<3")
    if h3 < 2: errs.append(f"H3 {h3}<2")
    if kw.split()[0].lower() not in d.get("title","").lower(): errs.append("anahtar kelime title'da yok")
    return errs, wc, (h2,h3,h4)

PAGE = """<!DOCTYPE html>
<html lang="tr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>__TITLETAG__</title>
<meta name="description" content="__DESC__">
<meta name="keywords" content="__KW__">
<link rel="canonical" href="__URL__">
<meta name="apple-itunes-app" content="app-id=6761003117">
<meta name="robots" content="index,follow,max-image-preview:large">
<meta property="og:type" content="article">
<meta property="og:title" content="__TITLE__">
<meta property="og:description" content="__DESC__">
<meta property="og:url" content="__URL__">
<meta property="og:image" content="__OGIMG__">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:image" content="__OGIMG__">
<link rel="alternate" type="application/rss+xml" title="Türkiye Gezi Rehberi RSS" href="/feed.xml">
<link rel="apple-touch-icon" href="/apple-touch-icon.png">
<link rel="icon" href="/favicon.ico" sizes="32x32">
<link rel="icon" type="image/png" sizes="32x32" href="/favicon-32x32.png">
<link rel="icon" type="image/svg+xml" href="/assets/logo.svg">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="preload" as="style" href="https://fonts.googleapis.com/css2?family=Sora:wght@600;700;800&family=Inter:wght@400;600&display=swap" onload="this.onload=null;this.rel='stylesheet'"><noscript><link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Sora:wght@600;700;800&family=Inter:wght@400;600&display=swap"></noscript>
<style>:root{--bg:#fbfaf7;--card:#fff;--ink:#1f2733;--muted:#69727f;--accent:#2f6bff;--accent2:#8b5cf6;--accent3:#2563eb;--line:#ece8e1;--shadow:0 6px 24px rgba(31,39,51,.07)}*{box-sizing:border-box;margin:0;padding:0}body{font-family:'Inter',-apple-system,BlinkMacSystemFont,sans-serif;background:var(--bg);color:var(--ink);line-height:1.75;-webkit-font-smoothing:antialiased;overflow-x:hidden}.wrap{max-width:1080px;margin:0 auto;padding:0 22px}nav{position:sticky;top:0;z-index:40;background:rgba(251,250,247,.82);border-bottom:1px solid var(--line)}nav .nwrap{max-width:1080px;margin:0 auto;padding:0 22px;display:flex;align-items:center;justify-content:space-between;height:64px}.logo{display:flex;align-items:center;gap:10px;font-weight:700;font-size:19px;color:var(--ink);text-decoration:none}.logo img{width:30px;height:30px;border-radius:9px}.nav-links a{color:var(--muted);text-decoration:none;font-size:14.5px;font-weight:600;margin-left:24px}h1,h2{font-family:'Sora',sans-serif}.page{padding:46px 0 30px}.aurora{position:fixed;inset:0;z-index:-2;background:var(--bg)}a{color:var(--accent);text-decoration:none}.site-footer{margin-top:64px;border-top:1px solid var(--line);background:#fff}.foot-grid{display:grid;grid-template-columns:1.6fr 1fr 1fr 1fr;gap:32px;padding:46px 22px 32px;max-width:1080px;margin:0 auto}@media(max-width:640px){.foot-grid{grid-template-columns:1fr 1fr}}.foot-col a{display:block;color:var(--muted);font-size:14px;margin-bottom:11px}.foot-brand p{color:var(--muted);font-size:14px;margin-top:12px;max-width:280px}.fh{font-size:12.5px;text-transform:uppercase;letter-spacing:.1em;color:var(--ink);font-weight:700;margin-bottom:14px}.foot-bottom{border-top:1px solid var(--line)}.foot-bottom .wrap{display:flex;justify-content:space-between;padding:18px 22px;font-size:13px;color:var(--muted)}.chipwrap{text-align:center}.chiplbl{display:block;font-size:12px;letter-spacing:.22em;text-transform:uppercase;font-weight:700;color:var(--muted);margin-bottom:12px}.chips{display:flex;gap:9px;flex-wrap:wrap;justify-content:center;margin-bottom:24px}.chips a{font-size:13.5px;font-weight:600;padding:8px 15px;border-radius:999px;border:1px solid var(--line);background:#fff;color:var(--ink)}.posts{display:grid;grid-template-columns:repeat(auto-fit,minmax(290px,1fr));gap:22px}.pcard{display:block;background:#fff;border:1px solid var(--line);border-radius:18px;padding:26px;color:var(--ink)}.pcard p{color:var(--muted);font-size:14.5px}.appbadges{display:flex;gap:10px;flex-wrap:wrap;align-items:center;margin-top:14px}.appbadges a{font-size:13.5px;font-weight:700;padding:10px 16px;border-radius:11px;background:#111827;color:#fff}.related{border:1px solid var(--line);border-radius:16px;padding:22px 24px;background:#fff;margin:36px 0 10px}.related ul{list-style:none;margin:0;padding:0}.related a{display:block;padding:12px 2px;color:var(--ink);font-weight:600}.share{display:flex;align-items:center;gap:10px;flex-wrap:wrap;margin:26px 0 6px;padding-top:18px;border-top:1px solid var(--line);color:var(--muted);font-size:14px}.share .ico{display:inline-flex;align-items:center;justify-content:center;width:38px;height:38px;border-radius:50%;border:1px solid var(--line);color:var(--muted)}</style>
<link rel="preload" href="/assets/blog.css?v=12" as="style" onload="this.onload=null;this.rel='stylesheet'"><noscript><link rel="stylesheet" href="/assets/blog.css?v=12"></noscript>
<script type="application/ld+json">__SCHEMA__</script>
<script src="/assets/analytics.js?v=3" defer></script><script src="/assets/enhance.js?v=7" defer></script>
</head>
<body>
<div class="aurora"></div>
<nav><div class="nwrap">
  <a class="logo" href="/"><img src="/assets/logo.svg" alt="Türkiye Gezi Rehberi" width="30" height="30">Gezi Rehberi</a>
  <div class="nav-links"><a href="/">Anasayfa</a><a href="/blog/">Rehberler</a><a href="https://coinsayfasi.github.io/routevia-app/">Routevia</a></div>
</div></nav>
<main class="wrap page">
__RAIL__
  <div class="crumb"><a href="/">Anasayfa</a> › <a href="/blog/">Rehberler</a> › __CRUMB__</div>
  <article class="post">
    <h1 class="title">__TITLE__</h1>
    <p class="meta">__TAG__ · __READ__ dk okuma · __NICE__</p>
__BODY__
  </article>
</main>
<footer class="site-footer">
  <div class="wrap foot-grid">
    <div class="foot-brand">
      <a class="logo" href="/"><img src="/assets/logo.svg" alt="Türkiye Gezi Rehberi" width="30" height="30">Gezi Rehberi</a>
      <p>Simple, useful mobile apps for travel, trips and rentals — free to start on iOS &amp; Android.</p>
    </div>
    <div class="foot-col">
      <p class="fh">Apps</p>
      <a href="https://coinsayfasi.github.io/onebag/">OneBag</a>
      <a href="https://coinsayfasi.github.io/routevia-app/">Routevia</a>
      <a href="https://coinsayfasi.github.io/rentflow/">RentFlow</a>
    </div>
    <div class="foot-col">
      <p class="fh">Company</p>
      <a href="/blog/">Blog</a>
      <a href="/#about">About</a>
      <a href="/gizlilik.html">Gizlilik</a>
      <a href="mailto:teknopattv@gmail.com">Contact</a>
    </div>
  </div>
  <div class="foot-bottom"><div class="wrap">
    <span>© 2026 Tabserve · Built by Yunus Güneş</span>
    <span>Made with ♥ in Türkiye · <a rel="me" href="https://mastodon.social/@tabserve">Mastodon</a> · <a href="https://www.youtube.com/@tabserve" rel="noopener">YouTube</a> · <a rel="me" href="https://bsky.app/profile/tabserve.bsky.social">Bluesky</a></span>
  </div></div>
</footer>
<script src="/assets/cookie.js?v=2" defer></script>
</body>
</html>
"""

def faq_schema(body):
    """Gövdedeki 'Sık Sorulan Sorular' bölümünden FAQPage JSON-LD üretir.
    Google'da 'People also ask' / zengin sonuç alanı kazandırır."""
    m = re.search(r'<h2[^>]*>[^<]*S[ıi]k Sorulan Sorular[^<]*</h2>([\s\S]*)', body, re.I)
    if not m: return None
    strip = lambda s: re.sub(r'<[^>]+>', '', s).strip()
    qas = re.findall(r'<h3[^>]*>([\s\S]*?)</h3>\s*<p[^>]*>([\s\S]*?)</p>', m.group(1))
    items = [{"@type":"Question","name":strip(q),
              "acceptedAnswer":{"@type":"Answer","text":strip(a)}}
             for q, a in qas if strip(q) and strip(a)]
    if not items: return None
    return {"@context":"https://schema.org","@type":"FAQPage","mainEntity":items}

def add_internal_links(body, posts, current_slug, max_links=4):
    """Diğer yazıların şehir adı gövdede ilk geçtiği paragrafta iç link olur.
    Yeni domain'de otorite dağılımı için kritik. Sadece <p> içinde, link/başlık
    içermeyen serbest metinde, yazı başına şehir başına 1 kez."""
    added = 0
    for p in posts:
        if added >= max_links or p["slug"] == current_slug: continue
        city = p["title"].split()[0]
        if len(city) < 4: continue
        href = f'/blog/{p["slug"]}/'
        if href in body: continue
        pat = re.compile(r'<p>((?:(?!</p>|<a\s|<h\d)[\s\S])*?)\b(' + re.escape(city) + r')\b')
        mm = pat.search(body)
        if not mm: continue
        s, e = mm.start(2), mm.end(2)
        body = body[:s] + f'<a href="{href}">{mm.group(2)}</a>' + body[e:]
        added += 1
    return body

def related_block(posts, current_slug, n=4):
    """Yazı sonuna 'İlgili Gezi Rehberleri' bloğu — iç linkleme + kardeş site."""
    others = [p for p in posts if p["slug"] != current_slug][:n]
    if not others: return ""
    lis = "".join(f'<li><a href="/blog/{p["slug"]}/">{html.escape(p["title"].split(":")[0].strip())}</a></li>'
                  for p in others)
    # Kardeş İngilizce site: birebir konu varsa yazıya, yoksa blog köküne
    x = CROSS.get(current_slug)
    if x:
        lis += (f'<li><a href="{SISTER_URL}/blog/{x}/" hreflang="en">'
                f'Read this guide in English (Tabserve Blog)</a></li>')
    else:
        lis += (f'<li><a href="{SISTER_URL}/blog/" hreflang="en">'
                f'İngilizce gezi &amp; seyahat rehberleri — Tabserve Blog</a></li>')
    return ('<section class="related"><h2>İlgili Gezi Rehberleri</h2><ul>'
            + lis + '</ul></section>')

def insert_cta(body, cta):
    if "{{APP_CTA}}" in body:
        return body.replace("{{APP_CTA}}", cta, 1)
    pos = [m.start() for m in re.finditer(r"<h2", body)]
    if len(pos) >= 2:
        i = pos[len(pos)//2]; return body[:i] + cta + body[i:]
    return body + cta


SOURCES_BOX = ('<div class="contrib sources"><b>📚 Faydalı Resmî Kaynaklar</b>'
 '<p><a href="https://www.ktb.gov.tr" rel="noopener">Kültür ve Turizm Bakanlığı</a> · '
 '<a href="https://muze.gov.tr" rel="noopener">Müzeler (MüzeKart)</a> · '
 '<a href="https://www.mgm.gov.tr" rel="noopener">Meteoroloji (MGM)</a> · '
 '<a href="https://goturkiye.com" rel="noopener">GoTürkiye</a></p></div>')

CONTRIB_BOX = ('<div class="contrib"><b>🗣️ Sen de katkıda bulun</b>'
 '<p>Bu rehbere eklenecek bir ipucun, güncel bir bilgin ya da düzeltmen mi var? '
 '<a href="mailto:teknopattv@gmail.com?subject=Rehber%20katk%C4%B1s%C4%B1">Bize yaz</a> — '
 'seçilen katkıları adınla yayınlıyoruz. Yer fotoğraflarını ve deneyimlerini '
 '<a href="https://coinsayfasi.github.io/routevia-app/" rel="noopener">Routevia topluluğunda</a> da paylaşabilirsin.</p></div>')

ONEBAG_CTA = ('<div class="appcta onebagcta"><b>🧳 Bu gezi için bavulunu OneBag\'le hazırla</b>'
 '<p><b>YENİ — AI Çek &amp; İşaretle:</b> çantanın fotoğrafını çek, OneBag\'in yapay zekâsı '
 'eşyaları otomatik işaretlesin ve eksik kritiği (pasaport, cüzdan) uyarsın. '
 'Ayrıca destinasyona göre valiz listesi + 89 havayolu ağırlık takibi.'
 '</p>'
 '<div class="appbadges"><a href="https://apps.apple.com/app/id6761047805" rel="noopener" aria-label="OneBag — App Store">&#63743; App Store</a>'
 '<a href="https://play.google.com/store/apps/details?id=com.onebag.travel" rel="noopener" aria-label="OneBag — Google Play">&#9654; Google Play</a>'
 '<a class="ghost" href="/gezi-butcesi-hesaplayici/">🧮 Bütçe hesapla</a></div></div>')

def insert_map(body, city):
    """Hızlı Bilgiler kutusundan sonra keysiz Google Maps embed (lazy)."""
    q = urllib.parse.quote(city + " Türkiye")
    fig = (f'<figure class="mapembed"><iframe src="https://www.google.com/maps?q={q}&output=embed" '
           f'width="100%" height="340" style="border:0;border-radius:16px" loading="lazy" '
           f'referrerpolicy="no-referrer-when-downgrade" title="{html.escape(city)} haritası"></iframe>'
           f'<figcaption>📍 {html.escape(city)} konumu — yakınlaştırıp keşfedebilirsin</figcaption></figure>')
    i = body.find("</ul></div>")  # quickfacts kapanışı
    if i != -1 and 'quickfacts' in body[:i]:
        i += len("</ul></div>")
        return body[:i] + fig + body[i:]
    return fig + body

def fetch_hero(query, slug):
    """Pexels'ten konuya birebir uygun YATAY görsel indir →
    assets/blog/<slug>.webp (1600w, masaüstü) + <slug>-800.webp (mobil, srcset).
    Key yoksa veya sonuç zayıfsa sessizce görselsiz devam (kötü görsel > görselsiz değildir)."""
    key = os.environ.get("PEXELS_API_KEY", "").strip()
    if not key: return False
    out = ROOT / "assets" / "blog"
    if any((out / f"{slug}{s}.{e}").exists() for s in ("",) for e in ("webp","jpg","jpeg","png")):
        return True  # manuel/mevcut görsel korunur
    try:
        u = "https://api.pexels.com/v1/search?" + urllib.parse.urlencode(
            {"query": query, "orientation": "landscape", "size": "large", "per_page": 5})
        r = json.loads(urllib.request.urlopen(
            urllib.request.Request(u, headers={"Authorization": key, "User-Agent": "tabserve-blog/1.0"}), timeout=25).read())
        photos = r.get("photos") or []
        if not photos: return False
        src = photos[0]["src"].get("large2x") or photos[0]["src"].get("large")
        raw = urllib.request.urlopen(urllib.request.Request(
            src, headers={"User-Agent": "tabserve-blog/1.0"}), timeout=40).read()
        out.mkdir(parents=True, exist_ok=True)
        try:
            import io
            from PIL import Image
            im = Image.open(io.BytesIO(raw)).convert("RGB")
            for w_, suf in ((1600, ""), (800, "-800")):
                img = im if im.width <= w_ else im.resize(
                    (w_, round(im.height * w_ / im.width)), Image.LANCZOS)
                img.save(out / f"{slug}{suf}.webp", "WEBP", quality=82)
        except ImportError:
            (out / f"{slug}.jpg").write_bytes(raw)  # Pillow yoksa JPEG fallback
        print(f"  🖼  Pexels: {slug} ← \"{query}\" (foto: {photos[0].get('photographer','?')})")
        return True
    except Exception as e:
        print(f"  (görsel atlandı: {type(e).__name__})")
        return False

def fetch_inpost(query, slug, idx):
    """İçerik içi görsel: 1000w tek boyut, lazy — assets/blog/<slug>-in<idx>.webp"""
    key = os.environ.get("PEXELS_API_KEY", "").strip()
    if not key: return None
    out = ROOT / "assets" / "blog"
    f = out / f"{slug}-in{idx}.webp"
    if f.exists(): return f"/assets/blog/{f.name}"
    try:
        u = "https://api.pexels.com/v1/search?" + urllib.parse.urlencode(
            {"query": query, "orientation": "landscape", "size": "large", "per_page": 3})
        r = json.loads(urllib.request.urlopen(urllib.request.Request(
            u, headers={"Authorization": key, "User-Agent": "tabserve-blog/1.0"}), timeout=25).read())
        photos = r.get("photos") or []
        if not photos: return None
        src = photos[0]["src"].get("large") or photos[0]["src"].get("large2x")
        raw = urllib.request.urlopen(urllib.request.Request(
            src, headers={"User-Agent": "tabserve-blog/1.0"}), timeout=40).read()
        import io
        from PIL import Image
        im = Image.open(io.BytesIO(raw)).convert("RGB")
        if im.width > 1000:
            im = im.resize((1000, round(im.height * 1000 / im.width)), Image.LANCZOS)
        out.mkdir(parents=True, exist_ok=True)
        im.save(f, "WEBP", quality=80)
        print(f"  🖼  Pexels iç görsel {idx}: {slug} ← \"{query}\"")
        return f"/assets/blog/{f.name}"
    except Exception as e:
        print(f"  (iç görsel atlandı: {type(e).__name__})"); return None

def insert_inpost_images(body, slug, queries, alt_base):
    """2. ve 4. H2 öncesine içerik görseli yerleştirir (varsa)."""
    pos = [m.start() for m in re.finditer(r"<h2", body)]
    spots = [i for i in (1, 3) if i < len(pos)][:len(queries)]
    for k in reversed(range(len(spots))):
        rel = fetch_inpost(queries[k], slug, k + 1)
        if not rel: continue
        fig = (f'<figure class="inpost"><img src="{rel}" alt="{html.escape(alt_base)}" '
               f'loading="lazy" decoding="async" width="1000" height="560"></figure>')
        i = pos[spots[k]]
        body = body[:i] + fig + body[i:]
    return body

def _openverse(q, n):
    out = []
    try:
        u = "https://api.openverse.org/v1/images/?q=" + q.replace(" ", "+") + "&license_type=commercial&size=medium&page_size=18"
        r = json.loads(urllib.request.urlopen(urllib.request.Request(u, headers={"User-Agent":"tabserve-blog/1.0"}), timeout=20).read())
        seen = set()
        for it in r.get("results", []):
            img = it.get("url") or it.get("thumbnail") or ""
            if img and img not in seen:
                seen.add(img)
                out.append({"url": img, "creator": it.get("creator") or "Unknown", "license": (it.get("license") or "CC").upper()})
            if len(out) >= n: break
    except Exception as e:
        print(f"  (görsel hata: {type(e).__name__})")
    return out

def get_images(query, n=3, fallback="travel"):
    """Anahtarsız Openverse görselleri — uzun sorgu sonuç vermezse kısaltıp/fallback dener."""
    ws = query.split()
    for q in [" ".join(ws[:3]), " ".join(ws[:2]), fallback]:
        if not q.strip(): continue
        out = _openverse(q, n)
        if out: return out
    return []

def _figure(img, alt, caption_text, hero=False):
    cap = (html.escape(caption_text) + " — " if caption_text else "") + f"Photo: {html.escape(img['creator'])} (Openverse, {html.escape(img['license'])})"
    w, h = (1200, 630) if hero else (1000, 560)
    perf = ' fetchpriority="high"' if hero else ' decoding="async"'  # LCP boost / async decode
    return (f'<figure class="{"hero" if hero else "inpost"}"><img src="{html.escape(img["url"])}" '
            f'alt="{html.escape(alt)}" loading="{"eager" if hero else "lazy"}"{perf} width="{w}" height="{h}">'
            f'<figcaption>{cap}</figcaption></figure>')

def _h2_text(body, p):
    m = re.match(r'<h2[^>]*>(.*?)</h2>', body[p:], re.S)
    return re.sub(r'<[^>]+>', '', m.group(1)).strip() if m else ''

def write_post(d, app, posts=()):
    slug = d["slug"]; url = f"{SITE}/blog/{slug}/"
    body = insert_cta(d["body"], APPS[app]["cta"])
    try:
        la, lo = float(d.get("lat", 0)), float(d.get("lon", 0))
        if 35 < la < 43 and 25 < lo < 45:  # Türkiye sınırı makul kontrol
            body = f'<span id="geo" data-lat="{la}" data-lon="{lo}" hidden></span>' + body
    except (TypeError, ValueError):
        pass
    body = insert_map(body, d["title"].split()[0])
    body = add_internal_links(body, posts, slug)
    ogimg = f"{SITE}/assets/tabserve-og.png"
    # Görsel: assets/blog/<slug>.(webp|jpg|png) varsa hero olur (Pexels otomasyonu
    # veya manuel). -800 varyantı varsa srcset ile tam mobil/masaüstü uyum.
    for ext in ("webp","jpg","jpeg","png"):
        ip = ROOT / "assets" / "blog" / f"{slug}.{ext}"
        if ip.exists():
            rel = f"/assets/blog/{slug}.{ext}"
            small = ROOT / "assets" / "blog" / f"{slug}-800.{ext}"
            srcset = (f' srcset="/assets/blog/{slug}-800.{ext} 800w, {rel} 1600w"'
                      f' sizes="(max-width:820px) 100vw, 780px"') if small.exists() else ""
            body = (f'<figure class="hero"><img src="{rel}"{srcset} alt="{html.escape(d["title"])}" loading="eager" fetchpriority="high" '
                    f'width="1200" height="630"><figcaption>{html.escape(d["meta_description"])}</figcaption></figure>') + body
            ogimg = SITE + rel
            break
    today = datetime.date.today()
    schemas = [{"@context":"https://schema.org","@type":"Article","headline":d["title"],
        "description":d["meta_description"],"image":ogimg,"author":{"@type":"Organization","name":"Tabserve"},
        "publisher":{"@type":"Organization","name":"Tabserve","logo":{"@type":"ImageObject","url":f"{SITE}/assets/tabserve-og.png"}},
        "datePublished":today.isoformat(),"dateModified":today.isoformat(),"mainEntityOfPage":url}]
    faq = faq_schema(body)
    if faq: schemas.append(faq)
    schemas.append({"@context":"https://schema.org","@type":"BreadcrumbList","itemListElement":[
        {"@type":"ListItem","position":1,"name":"Anasayfa","item":f"{SITE}/"},
        {"@type":"ListItem","position":2,"name":"Blog","item":f"{SITE}/blog/"},
        {"@type":"ListItem","position":3,"name":d["title"]}]})
    schema = json.dumps(schemas, ensure_ascii=False)
    read = max(4, round(words(body)/180))
    extras, rail = post_extras(url, d["title"])
    body = body + SOURCES_BOX + ONEBAG_CTA + CONTRIB_BOX + related_block(posts, slug) + extras  # ilgili rehberler + paylaş + yazar
    _ttl=d["title"]; _sfx=" | Türkiye Gezi Rehberi"; _ttag=(_ttl+_sfx) if len(_ttl+_sfx)<=70 else (_ttl if len(_ttl)<=70 else _ttl[:70].rsplit(" ",1)[0]); page = (PAGE.replace("__TITLETAG__", html.escape(_ttag)).replace("__TITLE__", html.escape(d["title"])).replace("__DESC__", html.escape(d["meta_description"]))
        .replace("__KW__", html.escape(d["keywords"])).replace("__URL__", url).replace("__OGIMG__", html.escape(ogimg))
        .replace("__SCHEMA__", schema).replace("__CRUMB__", html.escape(d["title"] if len(d["title"]) <= 42 else d["title"][:42].rsplit(" ", 1)[0] + "…"))
        .replace("__TAG__", APPS[app]["tag"]).replace("__READ__", str(read)).replace("__RAIL__", rail)
        .replace("__NICE__", "Yayın: " + today.strftime("%d.%m.%Y") + " · Güncelleme: " + today.strftime("%d.%m.%Y")).replace("__BODY__", body))
    (BLOG / slug).mkdir(parents=True, exist_ok=True)
    (BLOG / slug / "index.html").write_text(page, encoding="utf-8")

PER_PAGE = 9  # listeleme sayfası başına yazı

# Kardeş site çapraz linkleri (aynı yayıncı — TR↔EN doğal iç ağ)
SISTER_URL = "https://apps.tabserve.com.tr"
CROSS = {  # gezi slug -> apps.tabserve slug (birebir konu eşleşmesi)
  "kapadokya-gezi-rehberi-en-iyi-gezilecek-yerler-ve-ipuclari": "cappadocia-travel-guide",
  "antalya-gezilecek-yerler-gezi-rehberi": "antalya-travel-guide-beaches-old-town-day-trips",
}

# Site GENELİ arama: /assets/search.json'dan tüm yazılarda arar (sayfalamadan bağımsız)
SEARCH = """
<div class="psearch" style="max-width:540px;margin:0 auto 26px;position:relative">
  <input id="q" type="search" placeholder="Rehber ara: şehir, ilçe, yer…" aria-label="Rehber ara" autocomplete="off"
    style="width:100%;box-sizing:border-box;padding:13px 20px 13px 46px;border-radius:999px;border:1px solid rgba(120,120,140,.28);background:rgba(255,255,255,.75);font:inherit;font-size:15px;outline:none">
  <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" style="position:absolute;left:17px;top:50%;transform:translateY(-50%);opacity:.5" aria-hidden="true"><circle cx="11" cy="11" r="7"/><path d="M21 21l-4.3-4.3"/></svg>
  <p id="qn" style="display:none;text-align:center;color:var(--muted);margin:14px 0 0">Sonuç bulunamadı — farklı bir kelime deneyin.</p>
</div>
<div id="qres" class="posts" style="display:none"></div>
<script>document.addEventListener('DOMContentLoaded',function(){var q=document.getElementById('q');if(!q)return;
var grid=document.querySelector('.posts:not(#qres)'),nav=document.querySelector('.pagenav'),res=document.getElementById('qres'),qn=document.getElementById('qn'),idx=null;
function norm(s){return s.toLocaleLowerCase('tr')}
function esc(s){var d=document.createElement('div');d.textContent=s;return d.innerHTML}
q.addEventListener('input',function(){var v=norm(q.value.trim());
 if(!v){res.style.display='none';res.innerHTML='';if(grid)grid.style.display='';if(nav)nav.style.display='';qn.style.display='none';return}
 function run(){var hits=idx.filter(function(p){return norm(p.t+' '+p.d).indexOf(v)>-1}).slice(0,30);
  if(grid)grid.style.display='none';if(nav)nav.style.display='none';
  if(!hits.length){res.style.display='none';res.innerHTML='';qn.style.display='block';return}
  qn.style.display='none';
  res.innerHTML=hits.map(function(p){return '<a class="pcard in" href="'+p.u+'"><h3>'+esc(p.t)+'</h3><p>'+esc(p.d)+'</p></a>'}).join('');
  res.style.display='';}
 if(idx){run()}else{fetch('/assets/search.json').then(function(r){return r.json()}).then(function(j){idx=j;run()}).catch(function(){})}
});
var qp=new URLSearchParams(location.search).get("q");
if(qp){q.value=qp;q.dispatchEvent(new Event("input"));}});</script>
"""


# ── Bölge mimarisi: il/ilçe → bölge (hub sayfaları /<bolge>-gezilecek-yerler/) ──
REGION_NAMES = {"ege":"Ege","akdeniz":"Akdeniz","karadeniz":"Karadeniz","marmara":"Marmara",
                "ic-anadolu":"İç Anadolu","dogu-anadolu":"Doğu Anadolu","guneydogu-anadolu":"Güneydoğu Anadolu"}
# Bölge sayfaları için özgün meta description (duplike açıklamayı önler)
REGION_DESC = {
 "ege":"Ege Bölgesi gezilecek yerler: İzmir, Çeşme, Alaçatı, Bodrum, Fethiye ve Pamukkale. Mavi bayraklı koylar, antik kentler ve şehir şehir Ege gezi rehberleri.",
 "akdeniz":"Akdeniz Bölgesi gezilecek yerler: Antalya, Kaş, Kalkan, Alanya, Side ve Kekova. Turkuaz koylar, antik kentler ve şehir şehir Akdeniz gezi rehberleri.",
 "karadeniz":"Karadeniz Bölgesi gezilecek yerler: Trabzon, Uzungöl, Ayder, Amasra ve Safranbolu. Yeşil yaylalar, tarihi konaklar ve şehir şehir Karadeniz gezi rehberleri.",
 "marmara":"Marmara Bölgesi gezilecek yerler: İstanbul, Bursa, Edirne, Sapanca ve Çanakkale. Tarih, kültür, hafta sonu kaçamakları ve şehir şehir Marmara gezi rehberleri.",
 "ic-anadolu":"İç Anadolu gezilecek yerler: Kapadokya, Konya, Ankara, Safranbolu ve Eskişehir. Peribacaları, tarihi ve manevi duraklar, şehir şehir İç Anadolu gezi rehberleri.",
 "dogu-anadolu":"Doğu Anadolu gezilecek yerler: Van, Erzurum, Kars, Ağrı ve Nemrut Dağı. Göller, kayak merkezleri, tarih ve şehir şehir Doğu Anadolu gezi rehberleri.",
 "guneydogu-anadolu":"Güneydoğu Anadolu gezilecek yerler: Mardin, Şanlıurfa, Gaziantep, Diyarbakır ve Göbeklitepe. Tarih, gastronomi ve şehir şehir Güneydoğu gezi rehberleri."}
_R = {
 "ege":"izmir aydin mugla manisa denizli usak kutahya afyon afyonkarahisar cesme alacati bodrum marmaris fethiye kusadasi sirince ayvalik cunda didim datca akyaka pamukkale",
 "akdeniz":"antalya mersin adana hatay isparta burdur kahramanmaras osmaniye alanya side kas kalkan kemer belek olimpos cirali kekova anamur",
 "karadeniz":"trabzon rize artvin giresun ordu samsun sinop kastamonu bartin zonguldak duzce bolu amasya tokat corum gumushane bayburt uzungol ayder amasra safranbolu karabuk abant",
 "marmara":"istanbul bursa canakkale balikesir edirne kirklareli tekirdag kocaeli sakarya yalova bilecik iznik bozcaada gokceada sapanca",
 "ic-anadolu":"ankara konya kayseri eskisehir sivas yozgat kirsehir nevsehir nigde aksaray karaman kirikkale cankiri kapadokya goreme urgup avanos",
 "dogu-anadolu":"erzurum kars van agri ardahan igdir mus bitlis bingol tunceli elazig malatya erzincan hakkari dogubayazit",
 "guneydogu-anadolu":"gaziantep sanliurfa urfa mardin diyarbakir batman siirt sirnak adiyaman kilis midyat hasankeyf halfeti nemrut",
}
CITY2REGION = {c: r for r, cities in _R.items() for c in cities.split()}

def region_of(slug):
    return CITY2REGION.get(slug.split("-")[0])

def rebuild_index(posts):
    def card(p):
        return (f'    <a class="pcard" href="/blog/{p["slug"]}/"><span class="tag">{html.escape(p["tag"])}</span>'
                f'<h3>{html.escape(p["title"])}</h3><p>{html.escape(p["desc"])}</p></a>')
    # site geneli arama index'i
    (ROOT / "assets" / "search.json").write_text(json.dumps(
        [{"t": p["title"], "d": p["desc"], "u": f"/blog/{p['slug']}/"} for p in posts],
        ensure_ascii=False), encoding="utf-8")
    head = f"""<!DOCTYPE html>
<html lang="tr"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="blogarama-site-verification" content="blogarama-f925cf24-3b60-4d6a-bc6c-f8253efd471d">
<link rel="preconnect" href="https://pagead2.googlesyndication.com" crossorigin>
<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-7579691213276550" crossorigin="anonymous"></script>
<title>__T__ | Türkiye Gezi Rehberi</title>
<meta name="description" content="__DESC__">
<link rel="canonical" href="__CANON__">__PREVNEXT__
<meta name="apple-itunes-app" content="app-id=6761003117">
<meta name="robots" content="index,follow,max-image-preview:large">
<meta property="og:type" content="website">
<meta property="og:title" content="__T__">
<meta property="og:description" content="__DESC__">
<meta property="og:url" content="__CANON__">
<meta property="og:image" content="https://gezi.tabserve.com.tr/assets/og-home.jpg">
<meta property="og:site_name" content="Türkiye Gezi Rehberi">
<meta property="og:locale" content="tr_TR">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="__T__">
<meta name="twitter:description" content="__DESC__">
<meta name="twitter:image" content="https://gezi.tabserve.com.tr/assets/og-home.jpg">
<script type="application/ld+json">{{"@context":"https://schema.org","@type":"WebSite","name":"Türkiye Gezi Rehberi","url":"https://gezi.tabserve.com.tr/","inLanguage":"tr-TR","publisher":{{"@type":"Organization","name":"Tabserve","url":"https://gezi.tabserve.com.tr/","logo":{{"@type":"ImageObject","url":"https://gezi.tabserve.com.tr/assets/logo.svg"}}}},"potentialAction":{{"@type":"SearchAction","target":"https://gezi.tabserve.com.tr/blog/?q={{search_term_string}}","query-input":"required name=search_term_string"}}}}</script>__XSCHEMA__
<link rel="alternate" type="application/rss+xml" title="Türkiye Gezi Rehberi RSS" href="/feed.xml">
<link rel="apple-touch-icon" href="/apple-touch-icon.png">
<link rel="icon" href="/favicon.ico" sizes="32x32">
<link rel="icon" type="image/png" sizes="32x32" href="/favicon-32x32.png">
<link rel="icon" type="image/svg+xml" href="/assets/logo.svg">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="preload" as="style" href="https://fonts.googleapis.com/css2?family=Sora:wght@600;700;800&family=Inter:wght@400;600&display=swap" onload="this.onload=null;this.rel='stylesheet'"><noscript><link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Sora:wght@600;700;800&family=Inter:wght@400;600&display=swap"></noscript>
<style>:root{{--bg:#fbfaf7;--card:#fff;--ink:#1f2733;--muted:#69727f;--accent:#2f6bff;--accent2:#8b5cf6;--accent3:#2563eb;--line:#ece8e1;--shadow:0 6px 24px rgba(31,39,51,.07)}}*{{box-sizing:border-box;margin:0;padding:0}}body{{font-family:'Inter',-apple-system,BlinkMacSystemFont,sans-serif;background:var(--bg);color:var(--ink);line-height:1.75;-webkit-font-smoothing:antialiased;overflow-x:hidden}}.wrap{{max-width:1080px;margin:0 auto;padding:0 22px}}nav{{position:sticky;top:0;z-index:40;background:rgba(251,250,247,.82);border-bottom:1px solid var(--line)}}nav .nwrap{{max-width:1080px;margin:0 auto;padding:0 22px;display:flex;align-items:center;justify-content:space-between;height:64px}}.logo{{display:flex;align-items:center;gap:10px;font-weight:700;font-size:19px;color:var(--ink);text-decoration:none}}.logo img{{width:30px;height:30px;border-radius:9px}}.nav-links a{{color:var(--muted);text-decoration:none;font-size:14.5px;font-weight:600;margin-left:24px}}h1,h2{{font-family:'Sora',sans-serif}}.page{{padding:46px 0 30px}}.aurora{{position:fixed;inset:0;z-index:-2;background:var(--bg)}}a{{color:var(--accent);text-decoration:none}}.site-footer{{margin-top:64px;border-top:1px solid var(--line);background:#fff}}.foot-grid{{display:grid;grid-template-columns:1.6fr 1fr 1fr 1fr;gap:32px;padding:46px 22px 32px;max-width:1080px;margin:0 auto}}@media(max-width:640px){{.foot-grid{{grid-template-columns:1fr 1fr}}}}.foot-col a{{display:block;color:var(--muted);font-size:14px;margin-bottom:11px}}.foot-brand p{{color:var(--muted);font-size:14px;margin-top:12px;max-width:280px}}.fh{{font-size:12.5px;text-transform:uppercase;letter-spacing:.1em;color:var(--ink);font-weight:700;margin-bottom:14px}}.foot-bottom{{border-top:1px solid var(--line)}}.foot-bottom .wrap{{display:flex;justify-content:space-between;padding:18px 22px;font-size:13px;color:var(--muted)}}.chipwrap{{text-align:center}}.chiplbl{{display:block;font-size:12px;letter-spacing:.22em;text-transform:uppercase;font-weight:700;color:var(--muted);margin-bottom:12px}}.chips{{display:flex;gap:9px;flex-wrap:wrap;justify-content:center;margin-bottom:24px}}.chips a{{font-size:13.5px;font-weight:600;padding:8px 15px;border-radius:999px;border:1px solid var(--line);background:#fff;color:var(--ink)}}.posts{{display:grid;grid-template-columns:repeat(auto-fit,minmax(290px,1fr));gap:22px}}.pcard{{display:block;background:#fff;border:1px solid var(--line);border-radius:18px;padding:26px;color:var(--ink)}}.pcard p{{color:var(--muted);font-size:14.5px}}.appbadges{{display:flex;gap:10px;flex-wrap:wrap;align-items:center;margin-top:14px}}.appbadges a{{font-size:13.5px;font-weight:700;padding:10px 16px;border-radius:11px;background:#111827;color:#fff}}.related{{border:1px solid var(--line);border-radius:16px;padding:22px 24px;background:#fff;margin:36px 0 10px}}.related ul{{list-style:none;margin:0;padding:0}}.related a{{display:block;padding:12px 2px;color:var(--ink);font-weight:600}}.share{{display:flex;align-items:center;gap:10px;flex-wrap:wrap;margin:26px 0 6px;padding-top:18px;border-top:1px solid var(--line);color:var(--muted);font-size:14px}}.share .ico{{display:inline-flex;align-items:center;justify-content:center;width:38px;height:38px;border-radius:50%;border:1px solid var(--line);color:var(--muted)}}</style>
<link rel="preload" href="/assets/blog.css?v=12" as="style" onload="this.onload=null;this.rel='stylesheet'"><noscript><link rel="stylesheet" href="/assets/blog.css?v=12"></noscript><script src="/assets/analytics.js?v=3" defer></script><script src="/assets/enhance.js?v=7" defer></script>
</head>
<body>
<div class="aurora"></div>
<nav><div class="nwrap"><a class="logo" href="/"><img src="/assets/logo.svg" alt="Türkiye Gezi Rehberi" width="30" height="30">Gezi Rehberi</a>
<div class="nav-links"><a href="/">Anasayfa</a><a href="/hakkinda.html">Hakkında</a><a href="https://coinsayfasi.github.io/routevia-app/">Routevia</a></div></div></nav>"""
    foot = """<footer class="site-footer">
  <div class="wrap foot-grid">
    <div class="foot-brand">
      <a class="logo" href="/"><img src="/assets/logo.svg" alt="Türkiye Gezi Rehberi" width="30" height="30">Gezi Rehberi</a>
      <p>Türkiye'nin il il, ilçe ilçe gezilecek yerleri. Rotanı <a href="https://coinsayfasi.github.io/routevia-app/" style="color:var(--accent3)">Routevia</a> ile planla — ücretsiz.</p>
    </div>
    <div class="foot-col"><p class="fh">Keşfet</p>
      <a href="/blog/">Tüm Rehberler</a>
      <a href="/gezi-butcesi-hesaplayici/">Bütçe Hesaplayıcı</a>
      <a href="https://coinsayfasi.github.io/routevia-app/">Routevia Uygulaması</a>
      <a href="https://apps.tabserve.com.tr/blog/">Tabserve Blog (English)</a>
    </div>
    <div class="foot-col"><p class="fh">Kurumsal</p>
      <a href="/hakkinda.html">Hakkında</a>
      <a href="/gizlilik.html">Gizlilik Politikası</a>
      <a href="/cerez.html">Çerez Politikası</a><a href="/kullanim-kosullari.html">Kullanım Koşulları</a>
      <a href="mailto:teknopattv@gmail.com">İletişim</a>
    </div>
  </div>
  <div class="foot-bottom"><div class="wrap">
    <span>© 2026 Türkiye Gezi Rehberi · Tabserve</span>
    <span>Made with ♥ in Türkiye · <a rel="me" href="https://mastodon.social/@tabserve">Mastodon</a> · <a href="https://www.youtube.com/@tabserve" rel="noopener">YouTube</a> · <a rel="me" href="https://bsky.app/profile/tabserve.bsky.social">Bluesky</a></span>
  </div></div>
</footer>
<script>const io=new IntersectionObserver(e=>e.forEach(x=>{if(x.isIntersecting){x.target.classList.add('in');io.unobserve(x.target)}}),{threshold:.12});document.querySelectorAll('.pcard,.reveal').forEach((el,i)=>{el.style.transitionDelay=(i%4*70)+'ms';io.observe(el)});</script>
<noscript><style>.pcard,.reveal{opacity:1;transform:none}</style></noscript>
<script src="/assets/cookie.js?v=2" defer></script>
</body></html>
"""
    home_cards = "\n".join(card(p) for p in posts[:PER_PAGE])
    # Popüler Rotalar bloğu (yayında olan yazılardan)
    POPD = [("sanliurfa","2 Günlük Şanlıurfa Rotası"),("kapadokya","3 Günlük Kapadokya Rotası"),
            ("safranbolu","1 Günlük Safranbolu Rotası"),("gaziantep","Hafta Sonu Gaziantep Rotası"),
            ("gobeklitepe","Göbeklitepe Günübirlik Rota"),("mardin","2 Günlük Mardin Rotası")]
    _slugmap = {pp["slug"].split("-")[0]: pp["slug"] for pp in posts}
    _pr = [(f"/blog/{_slugmap[k]}/", lbl) for k, lbl in POPD if k in _slugmap][:4]
    poproutes = ("" if not _pr else
        '<div class="chipwrap" style="margin-top:26px"><span class="chiplbl">🧭 Popüler Rotalar</span><nav class="chips">'
        + "".join(f'<a href="{u}">{lbl}</a>' for u, lbl in _pr) + "</nav></div>")
    home_faq = [
      ("Türkiye'de en güzel gezilecek yerler nereleri?","Kapadokya, İstanbul, Efes, Pamukkale, Antalya, Ege ve Akdeniz kıyıları, Karadeniz yaylaları ve Güneydoğu'nun tarihi şehirleri Türkiye'nin en çok gezilen yerleridir. Sitemizde 81 il ve popüler ilçeler için detaylı gezi rehberleri bulabilirsiniz."),
      ("Kapadokya kaç günde gezilir?","Kapadokya'yı rahat bir tempoda gezmek için 2-3 gün idealdir. Balon turu, yeraltı şehirleri, Göreme Açık Hava Müzesi ve vadileri bu sürede görebilirsiniz."),
      ("Türkiye'de yaz tatili için nereye gidilir?","Yaz tatili için Bodrum, Fethiye, Marmaris, Çeşme, Alanya, Kaş ve Antalya kıyıları en popüler seçeneklerdir. Berrak koylar, plajlar ve deniz aktiviteleri için idealdir."),
      ("Türkiye gezi rotası nasıl planlanır?","Gün sayınızı, ulaşım şeklinizi ve gezi hızınızı belirleyip bölgeleri gruplayarak planlama yapabilirsiniz. Routevia uygulaması, gitmek istediğiniz yerlere göre otomatik günlük rota oluşturur."),
      ("Türkiye'de kışın nereye gidilir?","Kışın Uludağ, Kartalkaya, Palandöken kayak merkezleri; Abant, Bolu ve Kapadokya karlı manzaralarıyla; Şanlıurfa, Mardin ve Gaziantep ise tarihi-kültürel gezi için idealdir."),
      ("Ege ve Akdeniz'de görülmesi gereken yerler neresi?","Ege'de Efes, Şirince, Alaçatı, Bodrum ve Pamukkale; Akdeniz'de Antalya, Kaş, Kekova, Olimpos ve Side mutlaka görülmesi gereken yerlerdir."),
    ]
    faq_html = ('<section class="reveal" style="max-width:780px;margin:44px auto 6px"><h2 style="font-family:\'Sora\',sans-serif;font-size:25px;color:var(--ink);margin-bottom:16px">Sık Sorulan Sorular</h2>'
        + "".join(f'<details style="border:1px solid var(--line);border-radius:12px;background:#fff;padding:2px 18px;margin-bottom:10px"><summary style="cursor:pointer;font-weight:600;padding:14px 0;color:var(--ink)">{html.escape(q)}</summary><p style="color:var(--muted);padding:0 0 14px">{html.escape(a)}</p></details>' for q,a in home_faq) + '</section>')
    faq_schema = '<script type="application/ld+json">' + json.dumps({"@context":"https://schema.org","@type":"FAQPage","mainEntity":[{"@type":"Question","name":q,"acceptedAnswer":{"@type":"Answer","text":a}} for q,a in home_faq]}, ensure_ascii=False) + '</script>'
    org_schema = '<script type="application/ld+json">' + json.dumps({"@context":"https://schema.org","@type":"Organization","name":"Tabserve","alternateName":"Türkiye Gezi Rehberi","url":SITE+"/","logo":SITE+"/assets/logo.svg","email":"teknopattv@gmail.com","foundingDate":"2025","founder":{"@type":"Person","name":"Yunus Güneş"},"sameAs":["https://mastodon.social/@tabserve","https://bsky.app/profile/tabserve.bsky.social","https://www.youtube.com/@tabserve","https://t.me/gezirehberitr","https://github.com/coinsayfasi","https://indiepa.ge/tabserve"]}, ensure_ascii=False) + '</script>'
    # ── HUB: Bölgeler kartları ────────────────────────────────────────────────
    _regions = [
      ("ege-gezilecek-yerler","Ege","🏖️","Çeşme, Bodrum, İzmir, Alaçatı — mavi bayraklı koylar ve antik kentler"),
      ("akdeniz-gezilecek-yerler","Akdeniz","☀️","Antalya, Kaş, Alanya, Side — turkuaz deniz ve bol güneş"),
      ("marmara-gezilecek-yerler","Marmara","🌉","İstanbul, Bursa, Sapanca — tarih, kültür ve şehir kaçamakları"),
      ("karadeniz-gezilecek-yerler","Karadeniz","🌲","Uzungöl, Ayder, Trabzon, Amasra — yeşil yaylalar ve sis"),
      ("ic-anadolu-gezilecek-yerler","İç Anadolu","🎈","Kapadokya, Konya, Safranbolu — peribacaları ve derin tarih"),
      ("guneydogu-anadolu-gezilecek-yerler","Güneydoğu Anadolu","🏛️","Mardin, Şanlıurfa, Gaziantep, Göbeklitepe — medeniyetin beşiği"),
    ]
    regions_html = ('<section class="reveal" style="max-width:1080px;margin:8px auto 0">'
      '<h2 style="font-family:\'Sora\',sans-serif;font-size:27px;text-align:center;margin:10px 0 4px;color:var(--ink)">Bölgelere Göre Keşfet</h2>'
      '<p style="text-align:center;color:var(--muted);margin-bottom:22px">Türkiye\'nin her bölgesi ayrı bir dünya — ilham almak için başla</p>'
      '<div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(248px,1fr));gap:16px">'
      + "".join(f'<a href="/{s}/" style="display:block;background:#fff;border:1px solid var(--line);border-radius:16px;padding:22px;color:var(--ink);box-shadow:var(--shadow)"><div style="font-size:30px;line-height:1">{e}</div><h3 style="font-family:\'Sora\',sans-serif;font-size:19px;margin:10px 0 6px">{n}</h3><p style="color:var(--muted);font-size:14px;line-height:1.6;margin:0">{d}</p></a>' for s,n,e,d in _regions)
      + '</div></section>')
    # ── HUB: Popüler Şehirler ─────────────────────────────────────────────────
    _pcities = [("kapadokya-gezi-rehberi-en-iyi-gezilecek-yerler-ve-ipuclari","Kapadokya"),("antalya-gezilecek-yerler-gezi-rehberi","Antalya"),
      ("izmir-gezilecek-yerler-gezi-rehberi","İzmir"),("bursa-gezilecek-yerler-gezi-rehberi","Bursa"),
      ("trabzon-gezilecek-yerler-gezi-rehberi","Trabzon"),("marmaris-gezilecek-yerler-gezi-rehberi","Marmaris"),
      ("cesme-gezilecek-yerler-gezi-rehberi","Çeşme"),("alacati-gezilecek-yerler-gezi-rehberi","Alaçatı"),
      ("mardin-gezilecek-yerler-gezi-rehberi","Mardin"),("gaziantep-gezilecek-yerler-gezi-rehberi","Gaziantep"),
      ("safranbolu-gezilecek-yerler-gezi-rehberi","Safranbolu"),("konya-gezilecek-yerler-gezi-rehberi","Konya")]
    _have = {p["slug"] for p in posts}
    cities_html = ('<section class="reveal" style="max-width:1080px;margin:46px auto 0">'
      '<h2 style="font-family:\'Sora\',sans-serif;font-size:27px;text-align:center;margin:10px 0 4px;color:var(--ink)">Popüler Şehirler</h2>'
      '<p style="text-align:center;color:var(--muted);margin-bottom:20px">En çok gezilen destinasyonların detaylı rehberleri</p>'
      '<div style="display:flex;flex-wrap:wrap;gap:10px;justify-content:center">'
      + "".join(f'<a href="/blog/{s}/" style="padding:11px 19px;border-radius:999px;border:1px solid var(--line);background:#fff;color:var(--ink);font-weight:600;font-size:14.5px;box-shadow:var(--shadow)">{n}</a>' for s,n in _pcities if s in _have)
      + '</div></section>')
    # ── HUB: kapsamlı rehber metni ────────────────────────────────────────────
    hub_html = '''<section class="reveal" style="max-width:820px;margin:52px auto 6px;color:var(--muted);font-size:16.5px;line-height:1.85">
  <h2 style="font-family:'Sora',sans-serif;font-size:27px;color:var(--ink);margin-bottom:14px">Türkiye Gezi Rehberi: Nereye, Ne Zaman, Nasıl?</h2>
  <p>Türkiye; antik kentleri, turkuaz koyları, karlı dağları ve binlerce yıllık kültürüyle tek bir tatile sığmayacak kadar zengin bir ülke. Bu <strong>Türkiye gezi rehberi</strong>, 81 ili ve popüler ilçeleri il il, ilçe ilçe ele alarak <strong>gezilecek yerler</strong>, ulaşım, konaklama, bütçe ve rota planlamasını tek yerde topluyor. İster ilk kez geliyor ol, ister yeni bir rota arıyor ol — nereden başlayacağını burada bulacaksın.</p>

  <h3 style="font-family:'Sora',sans-serif;font-size:21px;color:var(--ink);margin:26px 0 10px">Bölge Bölge Türkiye</h3>
  <p><a href="/ege-gezilecek-yerler/">Ege</a>; Çeşme, Alaçatı ve Bodrum\'un mavi bayraklı koylarıyla, Efes ve Bergama gibi antik kentleriyle deniz ve tarihi bir arada sunar. <a href="/akdeniz-gezilecek-yerler/">Akdeniz</a>, Antalya\'dan Kaş\'a uzanan turkuaz kıyısı ve uzun yaz sezonuyla plaj tatilinin merkezidir. <a href="/marmara-gezilecek-yerler/">Marmara</a>, İstanbul ve Bursa\'nın tarih-kültür ağırlığını taşırken hafta sonu kaçamaklarına da elverişlidir. <a href="/karadeniz-gezilecek-yerler/">Karadeniz</a>; Uzungöl, Ayder ve yaylalarıyla yemyeşil bir doğa vaat eder. <a href="/ic-anadolu-gezilecek-yerler/">İç Anadolu</a>, Kapadokya\'nın peribacaları ve Konya\'nın manevi mirasıyla; <a href="/guneydogu-anadolu-gezilecek-yerler/">Güneydoğu Anadolu</a> ise Mardin, Şanlıurfa ve Göbeklitepe ile medeniyetin başladığı toprakları keşfettirir.</p>

  <h3 style="font-family:'Sora',sans-serif;font-size:21px;color:var(--ink);margin:26px 0 10px">Ne Zaman Gidilir?</h3>
  <p>Doğru mevsim, gezinin keyfini ikiye katlar. Kabaca bir yol haritası:</p>
  <div style="overflow-x:auto;margin:8px 0 4px"><table style="width:100%;border-collapse:collapse;font-size:15px;background:#fff;border:1px solid var(--line);border-radius:12px;overflow:hidden">
   <thead><tr style="background:#f6f4ef;text-align:left"><th style="padding:11px 14px">Bölge</th><th style="padding:11px 14px">En İyi Dönem</th><th style="padding:11px 14px">Öne Çıkan</th></tr></thead>
   <tbody>
   <tr style="border-top:1px solid var(--line)"><td style="padding:11px 14px"><strong>Ege &amp; Akdeniz</strong></td><td style="padding:11px 14px">Mayıs–Haziran, Eylül–Ekim</td><td style="padding:11px 14px">Deniz, kalabalıksız koylar</td></tr>
   <tr style="border-top:1px solid var(--line)"><td style="padding:11px 14px"><strong>Kapadokya</strong></td><td style="padding:11px 14px">Nisan–Haziran, Eylül–Kasım</td><td style="padding:11px 14px">Balon turu, ılıman hava</td></tr>
   <tr style="border-top:1px solid var(--line)"><td style="padding:11px 14px"><strong>Karadeniz</strong></td><td style="padding:11px 14px">Haziran–Eylül</td><td style="padding:11px 14px">Yaylalar, yeşil doğa</td></tr>
   <tr style="border-top:1px solid var(--line)"><td style="padding:11px 14px"><strong>Güneydoğu</strong></td><td style="padding:11px 14px">Mart–Mayıs, Ekim–Kasım</td><td style="padding:11px 14px">Serin hava, tarih turu</td></tr>
   </tbody></table></div>

  <h3 style="font-family:'Sora',sans-serif;font-size:21px;color:var(--ink);margin:26px 0 10px">Rota Nasıl Planlanır?</h3>
  <p>İyi bir rota, gününü ve enerjini boşa harcamaz. Gün sayını, ulaşım şeklini ve gezi hızını belirleyip yakın destinasyonları grupla: örneğin bir Ege turunda İzmir–Çeşme–Alaçatı\'yı; bir Kapadokya kaçamağında Göreme–Uçhisar–Avanos\'u aynı güzergâhta birleştir. Gitmek istediğin yerleri seç, gerisini <a href="https://coinsayfasi.github.io/routevia-app/"><strong>Routevia</strong></a> uygulamasına bırak — yapay zekâ, süreye göre günlük gezi rotanı saniyeler içinde oluşturur. Hazır <a href="/blog/">şehir rehberlerimizden</a> ilham alıp kendi rotanı da kurabilirsin.</p>

  <h3 style="font-family:'Sora',sans-serif;font-size:21px;color:var(--ink);margin:26px 0 10px">Ulaşım, Konaklama ve Bütçe</h3>
  <p>Büyük şehirler arası uçak en hızlısıdır; bölge içi keşiflerde ise kiralık araç özgürlük sağlar. Konaklamada yaz aylarında kıyı bölgelerini önceden ayırtmak hem yer hem fiyat avantajı verir. Tahmini masrafını önceden görmek istersen <a href="/gezi-butcesi-hesaplayici/">gezi bütçesi hesaplayıcımızı</a> kullanabilir; her şehir rehberimizde ise güncel ulaşım, konaklama ve yeme-içme ipuçlarını bulabilirsin.</p>
  <p>Yeni il ve ilçe rehberleri düzenli olarak ekleniyor. Keşfetmeye <a href="/blog/">tüm gezi rehberlerinden</a> ya da yukarıdaki bölgelerden başlayabilirsin — iyi yolculuklar!</p>
</section>'''
    home = (head.replace("__T__", "81 İl ve En Güzel Gezilecek Yerler").replace("__DESC__", "Türkiye'nin 81 ili ve popüler ilçeleri için gezilecek yerler, rota önerileri, konaklama, ulaşım ve yeme içme rehberleri. Seyahatini Routevia ile planla.").replace("__CANON__", f"{SITE}/").replace("__PREVNEXT__", "").replace("__XSCHEMA__",
        org_schema + '<script type="application/ld+json">{"@context":"https://schema.org","@type":"CollectionPage","name":"Türkiye Gezi Rehberi","url":"https://gezi.tabserve.com.tr/","inLanguage":"tr-TR","description":"Türkiye\'nin 81 ili ve popüler ilçeleri için gezi rehberleri."}</script>' + faq_schema)
        + f"""
<header style="text-align:center;padding:70px 22px 30px">
  <span class="brand" style="display:inline-block;font-size:13px;letter-spacing:.28em;text-transform:uppercase;font-weight:700;color:var(--accent3)">Türkiye Gezi Rehberi</span>
  <h1 style="font-family:'Sora',sans-serif;font-size:clamp(24px,5vw,48px);font-weight:800;letter-spacing:-.02em;margin:16px 0 12px">Türkiye Gezi Rehberi:<br>81 İl, İlçe İlçe Gezilecek Yerler</h1>
  <p style="color:var(--muted);font-size:18px;max-width:640px;margin:0 auto">81 il ve popüler ilçeler için gezilecek yerler, ulaşım, konaklama, yeme-içme ve rota önerileri. Seyahat planını <strong>Routevia</strong> ile saniyeler içinde oluştur.</p>
</header>
<main class="wrap page" style="padding-top:10px">
{SEARCH}
{regions_html}
{cities_html}
  <h2 style="font-family:'Sora',sans-serif;font-size:27px;text-align:center;margin:48px 0 4px;color:var(--ink)">Son Gezi Rehberleri</h2>
  <p style="text-align:center;color:var(--muted);margin-bottom:22px">En yeni eklenen il ve ilçe rehberleri</p>
  <div class="posts">
{home_cards}
  </div>
  <div style="text-align:center;margin:28px 0 4px"><a class="allbtn" href="/blog/">Tüm Gezi Rehberleri →</a></div>
{poproutes}

  <!-- Routevia uygulama vitrini -->
  <section class="appshow reveal">
    <img class="aico" src="/assets/routevia.webp" alt="Routevia uygulama simgesi" width="96" height="96" loading="lazy">
    <div class="abody">
      <h2>Routevia — cebindeki gezi rehberi</h2>
      <div class="stars">★★★★★ 4.9 <span>· App Store puanı (25 değerlendirme)</span></div>
      <p>Bu sitedeki tüm rehberlerin uygulaması: 81 ilin gezilecek yerleri cebinde, yapay zekâ rotanı saniyede planlasın.</p>
      <ul><li>İl il keşif</li><li>AI rota planı</li><li>Favoriler &amp; check-in</li><li>Ücretsiz</li></ul>
      <div class="appbadges"><a href="https://apps.apple.com/app/id6761003117" rel="noopener" aria-label="Routevia — App Store">&#63743; App Store</a><a href="https://play.google.com/store/apps/details?id=com.yunusgunes.routevia" rel="noopener" aria-label="Routevia — Google Play">&#9654; Google Play</a></div>
    </div>
  </section>
{hub_html}
{faq_html}
</main>
""" + foot)
    (ROOT / "index.html").write_text(home, encoding="utf-8")

    # ── Sayfalamalı listeleme: /blog/ (s.1), /blog/page/2/ ... ────────────────
    chunks = [posts[i:i+PER_PAGE] for i in range(0, len(posts), PER_PAGE)] or [[]]
    total = len(chunks)
    page_url  = lambda n: f"{SITE}/blog/" if n == 1 else f"{SITE}/blog/page/{n}/"
    page_href = lambda n: "/blog/" if n == 1 else f"/blog/page/{n}/"

    for n, chunk in enumerate(chunks, 1):
        cards = "\n".join(card(p) for p in chunk)
        prevnext = ""
        if n > 1:     prevnext += f'\n<link rel="prev" href="{page_url(n-1)}">'
        if n < total: prevnext += f'\n<link rel="next" href="{page_url(n+1)}">'
        pagenav = ""
        if total > 1:
            items = [f'<a href="{page_href(n-1)}" aria-label="Önceki">‹</a>' if n > 1 else '<span class="dis">‹</span>']
            items += [('<span class="cur">%d</span>' % i) if i == n else f'<a href="{page_href(i)}">{i}</a>' for i in range(1, total+1)]
            items.append(f'<a href="{page_href(n+1)}" aria-label="Sonraki">›</a>' if n < total else '<span class="dis">›</span>')
            pagenav = '<nav class="pagenav" aria-label="Sayfalar">' + "".join(items) + '</nav>'
        # <title>: her sayfa benzersiz olsun (SEO — sayfa no kalır)
        title = "Tüm Gezi Rehberleri" if n == 1 else f"Gezi Rehberleri — Sayfa {n}"
        # Görünür H1: sayfa no YOK (altta pagenav + breadcrumb zaten gösteriyor)
        h1 = "Tüm Gezi Rehberleri"
        list_desc = (f"Türkiye'nin tüm gezi rehberleri — il il, ilçe ilçe gezilecek yerler, ulaşım, konaklama ve rota önerileri. {len(posts)} güncel rehber." if n == 1 else f"Türkiye gezi rehberleri, sayfa {n}. İl il, ilçe ilçe gezilecek yerler, ulaşım, konaklama ve rota önerileri.")
        listing = (head.replace("__T__", title).replace("__DESC__", list_desc).replace("__CANON__", page_url(n)).replace("__PREVNEXT__", prevnext).replace("__XSCHEMA__",
            '<script type="application/ld+json">' + json.dumps({"@context":"https://schema.org","@type":"BreadcrumbList","itemListElement":[{"@type":"ListItem","position":1,"name":"Anasayfa","item":SITE+"/"},{"@type":"ListItem","position":2,"name":"Rehberler" if n==1 else f"Rehberler — Sayfa {n}","item":page_url(n)}]}, ensure_ascii=False) + '</script>')
            + f"""
<main class="wrap page">
  <div class="crumb"><a href="/">Anasayfa</a> › Rehberler{'' if n == 1 else f' › Sayfa {n}'}</div>
  <h1 class="title">{h1}</h1>
  <p class="meta">Türkiye'nin il il, ilçe ilçe gezilecek yerleri.{f' ({len(posts)} rehber)' if n == 1 else ''}</p>
{SEARCH}
  <div class="posts">
{cards}
  </div>
  {pagenav}
</main>
""" + foot)
        outdir = BLOG if n == 1 else BLOG / "page" / str(n)
        outdir.mkdir(parents=True, exist_ok=True)
        (outdir / "index.html").write_text(listing, encoding="utf-8")

    # yazı azalırsa bayat sayfa dizinlerini temizle
    pd = BLOG / "page"
    if pd.exists():
        for d in pd.iterdir():
            if d.is_dir() and d.name.isdigit() and int(d.name) > total:
                for f in d.iterdir(): f.unlink()
                d.rmdir()

    # ── Bölge hub sayfaları ───────────────────────────────────────────────────
    by_region = {}
    for po in posts:
        r = region_of(po["slug"])
        if r: by_region.setdefault(r, []).append(po)
    region_slugs = []
    for r, rposts in by_region.items():
        rname = REGION_NAMES[r]
        rslug = f"{r}-gezilecek-yerler"
        region_slugs.append((rslug, rname, len(rposts)))
        rcards = "\n".join(card(pp) for pp in rposts)
        rpage = (head.replace("__T__", f"{rname} Bölgesi Gezilecek Yerler").replace("__DESC__", REGION_DESC.get(r, f"{rname} Bölgesi gezilecek yerler, şehir şehir gezi rehberleri, ulaşım, konaklama ve rota önerileri. {rname} bölgesini Routevia ile keşfet.")).replace("__CANON__", f"{SITE}/{rslug}/").replace("__PREVNEXT__", "").replace("__XSCHEMA__",
            '<script type="application/ld+json">' + json.dumps({"@context":"https://schema.org","@type":"BreadcrumbList","itemListElement":[{"@type":"ListItem","position":1,"name":"Anasayfa","item":SITE+"/"},{"@type":"ListItem","position":2,"name":"Rehberler","item":SITE+"/blog/"},{"@type":"ListItem","position":3,"name":rname}]}, ensure_ascii=False) + '</script>')
            + f"""
<main class="wrap page">
  <div class="crumb"><a href="/">Anasayfa</a> › <a href="/blog/">Rehberler</a> › {rname}</div>
  <h1 class="title">{rname} Bölgesi Gezilecek Yerler</h1>
  <p class="meta">{rname} Bölgesi'nin il il, ilçe ilçe gezi rehberleri — gezilecek yerler, ulaşım, konaklama ve rota önerileri. ({len(rposts)} rehber)</p>
  <div class="posts">
{rcards}
  </div>
  <p style="margin-top:26px"><a class="allbtn" href="/blog/">Tüm Gezi Rehberleri →</a></p>
</main>
""" + foot)
        outd = ROOT / rslug
        outd.mkdir(parents=True, exist_ok=True)
        (outd / "index.html").write_text(rpage, encoding="utf-8")

    # Bölge çipleri (anasayfa + listeleme sayfalarına enjekte)
    if region_slugs:
        region_slugs.sort(key=lambda x: -x[2])
        EMO = {"ege":"🌊","akdeniz":"🏖️","karadeniz":"🌲","marmara":"🌉",
               "ic-anadolu":"🎈","dogu-anadolu":"⛰️","guneydogu-anadolu":"🕌"}
        chips = ('<div class="chipwrap"><span class="chiplbl">Bölgelere göre keşfet</span>'
                 '<nav class="chips" aria-label="Bölgeler">' + "".join(
            f'<a href="/{rs}/">{EMO.get(rs.replace("-gezilecek-yerler",""),"📍")} {rn}<b>{n}</b></a>'
            for rs, rn, n in region_slugs) + "</nav></div>")
        for fpath in [ROOT / "index.html", BLOG / "index.html"] + sorted((BLOG / "page").glob("*/index.html")) if (BLOG/"page").exists() else [ROOT / "index.html", BLOG / "index.html"]:
            try:
                c = fpath.read_text(encoding="utf-8")
                c = c.replace('<div class="posts">', chips + '\n  <div class="posts">', 1)
                fpath.write_text(c, encoding="utf-8")
            except FileNotFoundError:
                pass

    # ── RSS feed ─────────────────────────────────────────────────────────────
    items = "".join(
        f"<item><title>{html.escape(pp['title'])}</title><link>{SITE}/blog/{pp['slug']}/</link>"
        f"<guid>{SITE}/blog/{pp['slug']}/</guid><description>{html.escape(pp['desc'])}</description>"
        f"<pubDate>{datetime.datetime.strptime(pp.get('date','2026-06-30'), '%Y-%m-%d').strftime('%a, %d %b %Y')} 09:00:00 GMT</pubDate></item>"
        for pp in posts[:20])
    (ROOT / "feed.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?><rss version="2.0"><channel>'
        f'<title>Türkiye Gezi Rehberi</title><link>{SITE}/</link>'
        '<description>İl il, ilçe ilçe gezilecek yerler ve gezi rehberleri</description>'
        f'<language>tr</language>{items}</channel></rss>', encoding="utf-8")

    # sitemap
    static = [("/","1.0","daily"),("/blog/","0.8","weekly"),("/gezi-butcesi-hesaplayici/","0.6","monthly"),("/hakkinda.html","0.3","yearly"),("/gizlilik.html","0.3","yearly"),("/cerez.html","0.3","yearly"),("/kullanim-kosullari.html","0.3","yearly")]
    urls = "".join(f'  <url><loc>{SITE}{u}</loc><changefreq>{c}</changefreq><priority>{p}</priority></url>\n' for u,p,c in static)
    urls += "".join(f'  <url><loc>{SITE}/{rs}/</loc><changefreq>weekly</changefreq><priority>0.6</priority></url>\n' for rs, _, _ in region_slugs)
    urls += "".join(f'  <url><loc>{SITE}/blog/page/{n}/</loc><changefreq>weekly</changefreq><priority>0.5</priority></url>\n' for n in range(2, total+1))
    urls += "".join(f'  <url><loc>{SITE}/blog/{po["slug"]}/</loc><changefreq>monthly</changefreq><priority>0.7</priority></url>\n' for po in posts)
    (ROOT / "sitemap.xml").write_text(f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{urls}</urlset>\n', encoding="utf-8")

def main():
    posts = load(POSTS_F, [])
    if "--rebuild" in sys.argv:
        rebuild_index(posts); print(f"✓ listeleme+sitemap yeniden kuruldu ({len(posts)} yazı)"); return
    if not (os.environ.get("GEMINI_API_KEY") or os.environ.get("ANTHROPIC_API_KEY")):
        sys.exit("⚠️ GEMINI_API_KEY (ücretsiz) veya ANTHROPIC_API_KEY gerekli")
    state = load(STATE_F, {"used":[]}); used = set(state["used"])
    n = int(os.environ.get("BLOG_COUNT","1")); made = 0; new_urls = []
    for topic in TOPICS:
        if made >= n: break
        if topic["keyword"] in used: continue
        kw, app = topic["keyword"], topic["app"]
        print(f"\n📝 [{app}] {kw}")
        prompt = PROMPT.format(kw=kw, angle=topic["angle"], one=APPS[app]["one"], name=APPS[app]["name"])
        d = None
        for tryi in range(2):
            txt = call_llm(prompt if tryi==0 else prompt+"\n\nYour previous attempt failed validation. Ensure 1000+ WORDS and H2/H3/H4 hierarchy and the {{APP_CTA}} token.")
            try: cand = parse_json(txt)
            except Exception as e: print(f"  JSON parse hatası: {e}"); continue
            errs, wc, hh = validate(cand, kw)
            if not errs: d = cand; print(f"  ✓ {wc} kelime · H2/H3/H4={hh}"); break
            print(f"  ✗ doğrulama: {', '.join(errs)} → tekrar")
        if not d:
            print("  ⚠️ bu konu atlandı (kalite tutmadı)"); used.add(kw); continue
        d["slug"] = slugify(d.get("slug") or d["title"])
        iqs = d.get("img_queries") or ([d["img_query"]] if d.get("img_query") else [])
        fetch_hero((iqs[0] if iqs else f"{kw.split()[0]} Turkey travel"), d["slug"])
        if len(iqs) > 1:
            d["body"] = insert_inpost_images(d["body"], d["slug"], iqs[1:3], d["title"])
        write_post(d, app, posts)
        posts.insert(0, {"slug":d["slug"],"title":d["title"],"desc":d["meta_description"],
                         "tag":APPS[app]["tag"],"date":datetime.date.today().isoformat()})
        used.add(kw); made += 1
        new_urls.append(f"{SITE}/blog/{d['slug']}/")
        print(f"  ✓ yayınlandı: /blog/{d['slug']}/")
    # dedup posts by slug (en yeni kalsın)
    seen=set(); uniq=[]
    for p in posts:
        if p["slug"] in seen: continue
        seen.add(p["slug"]); uniq.append(p)
    POSTS_F.write_text(json.dumps(uniq, ensure_ascii=False, indent=1), encoding="utf-8")
    STATE_F.write_text(json.dumps({"used":list(used)}, ensure_ascii=False, indent=1), encoding="utf-8")
    rebuild_index(uniq)
    (GEN / "new_urls.txt").write_text("\n".join(new_urls), encoding="utf-8")  # index_ping.py için
    print(f"\n✓ {made} yeni yazı · toplam {len(uniq)} · {len(used)}/{len(TOPICS)} konu kullanıldı")

if __name__ == "__main__":
    main()
