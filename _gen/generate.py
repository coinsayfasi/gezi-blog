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

def post_extras(url, title):
    """Alt paylaş çubuğu + yazar kutusu (body sonu) ve sol kayan çubuk (rail) HTML'i."""
    u = urllib.parse.quote(url, safe=''); t = urllib.parse.quote(title, safe='')
    S = [("X",f"https://twitter.com/intent/tweet?url={u}&amp;text={t}"),("f",f"https://www.facebook.com/sharer/sharer.php?u={u}"),
         ("P",f"https://pinterest.com/pin/create/button/?url={u}&amp;description={t}"),("W",f"https://wa.me/?text={t}%20{u}"),
         ("in",f"https://www.linkedin.com/sharing/share-offsite/?url={u}")]
    lbl = {"X":"X","f":"Facebook","P":"Pinterest","W":"WhatsApp","in":"LinkedIn"}
    share = '<div class="share"><span>Bu yazıyı paylaş:</span>' + ''.join(
        f'<a href="{h}" target="_blank" rel="noopener" aria-label="Share">{lbl[n]}</a>' for n,h in S) + '</div>'
    follow = ' '.join(f'<a href="{lu}" target="_blank" rel="noopener">{ln}</a>' for ln,lu in SOCIAL)
    author = ('<div class="author-box"><img class="ab-logo" src="/assets/logo.svg" alt="Tabserve" width="56" height="56">'
              '<div class="ab-body"><b>Türkiye Gezi Rehberi</b><p>Türkiye\'nin il il, ilçe ilçe gezilecek yerlerini paylaşıyoruz. '
              f'Rotanı saniyede planlamak için Routevia uygulamasını ücretsiz indir.</p><div class="follow"><span>Bizi takip et:</span>{follow}</div></div></div>')
    rail = '<div class="share-rail" aria-label="Share this post">' + ''.join(
        f'<a href="{h}" target="_blank" rel="noopener" aria-label="Share">{n}</a>' for n,h in S) + '</div>'
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
   "cta":'<div class="appcta"><b>🚗 Rotanı saniyede planla — Routevia</b><p>Routevia, Türkiye\'nin il il, ilçe ilçe gezilecek yerlerini keşfetmeni ve yapay zekâ ile rotanı saniyede planlamanı sağlar. Ücretsiz, iOS &amp; Android.</p><a href="https://coinsayfasi.github.io/routevia-app/">Routevia\'yı keşfet → ücretsiz indir</a></div>',
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
2. Uzunluk: 600-800 KELİME gerçek gövde metni (kelime say, karakter değil). Dolgu yapma.
3. Başlık hiyerarşisi: 4-6 <h2> (anahtar kelime varyasyonlu), H2 altında <h3>, en az bir <h4> (gerekirse <h5>). Mantıklı yuvalama H2 > H3 > H4.
4. Kısa bir sonuç paragrafıyla bitir.
5. ÖZGÜN ve somut — gerçek faydalı bilgi (gezilecek yerler, ne zaman gidilir, ulaşım, ipuçları, nerede kalınır). İstatistik/fiyat/alıntı UYDURMA. Tekrar yok, "spin"/genel dolgu yok.
6. SADECE şu etiketler: h2, h3, h4, h5, p, ul, li, strong, a. Markdown yok, <h1> yok, <html>/<head>/<style> yok.
7. 1-2 dış OTORİTE linki ekle (resmi turizm/kültür sitesi, .gov.tr ya da ilgili Wikipedia maddesi). Sadece var olduğundan EMİN olduğun stabil URL'ler — https://tr.wikipedia.org/wiki/<Konu> tercih et. Deep URL UYDURMA. Cümle içinde doğal yerleştir, başlıkta değil.

SADECE geçerli minified JSON çıktısı ver (kod bloğu/yorum yok), tam şu anahtarlar:
{{"title":"...","meta_description":"max 155 karakter, anahtar kelimeyi içersin","keywords":"4-6 virgülle ayrılmış anahtar kelime","slug":"baslıktan-kebab-case-ascii","body":"makale HTML'i"}}"""

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
    if wc < 600: errs.append(f"kelime {wc}<600")
    if h2 < 3: errs.append(f"H2 {h2}<3")
    if h3 < 2: errs.append(f"H3 {h3}<2")
    if h4 < 1: errs.append(f"H4 {h4}<1")
    if kw.split()[0].lower() not in d.get("title","").lower(): errs.append("anahtar kelime title'da yok")
    return errs, wc, (h2,h3,h4)

PAGE = """<!DOCTYPE html>
<html lang="tr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>__TITLE__ | Türkiye Gezi Rehberi</title>
<meta name="description" content="__DESC__">
<meta name="keywords" content="__KW__">
<link rel="canonical" href="__URL__">
<meta property="og:type" content="article">
<meta property="og:title" content="__TITLE__">
<meta property="og:description" content="__DESC__">
<meta property="og:url" content="__URL__">
<meta property="og:image" content="__OGIMG__">
<link rel="icon" type="image/svg+xml" href="/assets/logo.svg">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="preload" as="style" href="https://fonts.googleapis.com/css2?family=Sora:wght@600;700;800&family=Inter:wght@400;600&display=swap" onload="this.onload=null;this.rel='stylesheet'"><noscript><link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Sora:wght@600;700;800&family=Inter:wght@400;600&display=swap"></noscript>
<link rel="stylesheet" href="/assets/blog.css">
<script type="application/ld+json">__SCHEMA__</script>
</head>
<body>
<div class="aurora"></div>
<nav><div class="nwrap">
  <a class="logo" href="/"><img src="/assets/logo.svg" alt="">Gezi Rehberi</a>
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
      <a class="logo" href="/"><img src="/assets/logo.svg" alt="" width="30" height="30">Gezi Rehberi</a>
      <p>Simple, useful mobile apps for travel, trips and rentals — free to start on iOS &amp; Android.</p>
    </div>
    <div class="foot-col">
      <h4>Apps</h4>
      <a href="https://coinsayfasi.github.io/onebag/">OneBag</a>
      <a href="https://coinsayfasi.github.io/routevia-app/">Routevia</a>
      <a href="https://coinsayfasi.github.io/rentflow/">RentFlow</a>
    </div>
    <div class="foot-col">
      <h4>Company</h4>
      <a href="/blog/">Blog</a>
      <a href="/#about">About</a>
      <a href="/privacy.html">Privacy</a>
      <a href="mailto:teknopattv@gmail.com">Contact</a>
    </div>
  </div>
  <div class="foot-bottom"><div class="wrap">
    <span>© 2026 Tabserve · Built by Yunus Güneş</span>
    <span>Made with ♥ in Türkiye</span>
  </div></div>
</footer>
</body>
</html>
"""

def insert_cta(body, cta):
    if "{{APP_CTA}}" in body:
        return body.replace("{{APP_CTA}}", cta, 1)
    pos = [m.start() for m in re.finditer(r"<h2", body)]
    if len(pos) >= 2:
        i = pos[len(pos)//2]; return body[:i] + cta + body[i:]
    return body + cta

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
    return (f'<figure class="{"hero" if hero else "inpost"}"><img src="{html.escape(img["url"])}" '
            f'alt="{html.escape(alt)}" loading="{"eager" if hero else "lazy"}" width="{w}" height="{h}">'
            f'<figcaption>{cap}</figcaption></figure>')

def _h2_text(body, p):
    m = re.match(r'<h2[^>]*>(.*?)</h2>', body[p:], re.S)
    return re.sub(r'<[^>]+>', '', m.group(1)).strip() if m else ''

def write_post(d, app):
    slug = d["slug"]; url = f"{SITE}/blog/{slug}/"
    body = insert_cta(d["body"], APPS[app]["cta"])
    ogimg = f"{SITE}/assets/tabserve-og.png"
    # Görsel: kullanıcı assets/blog/<slug>.(jpg|png|webp) yüklerse hero olarak kullanılır; yoksa görselsiz (temiz).
    for ext in ("jpg","jpeg","png","webp"):
        ip = ROOT / "assets" / "blog" / f"{slug}.{ext}"
        if ip.exists():
            rel = f"/assets/blog/{slug}.{ext}"
            body = (f'<figure class="hero"><img src="{rel}" alt="{html.escape(d["title"])}" loading="eager" '
                    f'width="1200" height="630"><figcaption>{html.escape(d["meta_description"])}</figcaption></figure>') + body
            ogimg = SITE + rel
            print(f"  🖼  manuel görsel: {rel}")
            break
    today = datetime.date.today()
    schema = json.dumps({"@context":"https://schema.org","@type":"Article","headline":d["title"],
        "description":d["meta_description"],"image":ogimg,"author":{"@type":"Organization","name":"Tabserve"},
        "publisher":{"@type":"Organization","name":"Tabserve","logo":{"@type":"ImageObject","url":f"{SITE}/assets/tabserve-og.png"}},
        "datePublished":today.isoformat(),"dateModified":today.isoformat(),"mainEntityOfPage":url}, ensure_ascii=False)
    read = max(4, round(words(body)/180))
    extras, rail = post_extras(url, d["title"])
    body = body + extras  # alt paylaş çubuğu + yazar kutusu (Follow Us)
    page = (PAGE.replace("__TITLE__", html.escape(d["title"])).replace("__DESC__", html.escape(d["meta_description"]))
        .replace("__KW__", html.escape(d["keywords"])).replace("__URL__", url).replace("__OGIMG__", html.escape(ogimg))
        .replace("__SCHEMA__", schema).replace("__CRUMB__", html.escape(d["title"][:40]))
        .replace("__TAG__", APPS[app]["tag"]).replace("__READ__", str(read)).replace("__RAIL__", rail)
        .replace("__NICE__", today.strftime("%B %Y")).replace("__BODY__", body))
    (BLOG / slug).mkdir(parents=True, exist_ok=True)
    (BLOG / slug / "index.html").write_text(page, encoding="utf-8")

def rebuild_index(posts):
    cards = "\n".join(
      f'    <a class="pcard" href="/blog/{p["slug"]}/"><span class="tag">{html.escape(p["tag"])}</span>'
      f'<h2>{html.escape(p["title"])}</h2><p>{html.escape(p["desc"])}</p></a>' for p in posts)
    head = f"""<!DOCTYPE html>
<html lang="tr"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>__T__ | Türkiye Gezi Rehberi</title>
<meta name="description" content="Türkiye'nin il il, ilçe ilçe gezilecek yerleri, gezi rehberleri ve rotaları. Routevia ile rotanı saniyede planla.">
<link rel="canonical" href="__CANON__">
<link rel="icon" type="image/svg+xml" href="/assets/logo.svg">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="preload" as="style" href="https://fonts.googleapis.com/css2?family=Sora:wght@600;700;800&family=Inter:wght@400;600&display=swap" onload="this.onload=null;this.rel='stylesheet'"><noscript><link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Sora:wght@600;700;800&family=Inter:wght@400;600&display=swap"></noscript>
<link rel="stylesheet" href="/assets/blog.css"></head>
<body>
<div class="aurora"></div>
<nav><div class="nwrap"><a class="logo" href="/"><img src="/assets/logo.svg" alt="">Gezi Rehberi</a>
<div class="nav-links"><a href="/">Anasayfa</a><a href="/hakkinda.html">Hakkında</a><a href="https://coinsayfasi.github.io/routevia-app/">Routevia</a></div></div></nav>"""
    foot = """<footer class="site-footer">
  <div class="wrap foot-grid">
    <div class="foot-brand">
      <a class="logo" href="/"><img src="/assets/logo.svg" alt="" width="30" height="30">Gezi Rehberi</a>
      <p>Türkiye'nin il il, ilçe ilçe gezilecek yerleri. Rotanı <a href="https://coinsayfasi.github.io/routevia-app/" style="color:var(--accent3)">Routevia</a> ile planla — ücretsiz.</p>
    </div>
    <div class="foot-col"><h4>Keşfet</h4>
      <a href="/">Tüm Rehberler</a>
      <a href="https://coinsayfasi.github.io/routevia-app/">Routevia Uygulaması</a>
    </div>
    <div class="foot-col"><h4>Kurumsal</h4>
      <a href="/hakkinda.html">Hakkında</a>
      <a href="/gizlilik.html">Gizlilik Politikası</a>
      <a href="/cerez.html">Çerez Politikası</a>
      <a href="mailto:teknopattv@gmail.com">İletişim</a>
    </div>
  </div>
  <div class="foot-bottom"><div class="wrap">
    <span>© 2026 Türkiye Gezi Rehberi · Tabserve</span>
    <span>Made with ♥ in Türkiye</span>
  </div></div>
</footer>
<script>const io=new IntersectionObserver(e=>e.forEach(x=>{if(x.isIntersecting){x.target.classList.add('in');io.unobserve(x.target)}}),{threshold:.12});document.querySelectorAll('.pcard,.reveal').forEach((el,i)=>{el.style.transitionDelay=(i%4*70)+'ms';io.observe(el)});</script>
<noscript><style>.pcard,.reveal{opacity:1;transform:none}</style></noscript>
</body></html>
"""
    home = (head.replace("__T__", "Türkiye Gezi Rehberi — İl İl Gezilecek Yerler").replace("__CANON__", f"{SITE}/")
        + f"""
<header style="text-align:center;padding:70px 22px 30px">
  <span class="brand" style="display:inline-block;font-size:13px;letter-spacing:.28em;text-transform:uppercase;font-weight:700;color:var(--accent3)">Türkiye Gezi Rehberi</span>
  <h1 style="font-family:'Sora',sans-serif;font-size:clamp(30px,5.5vw,52px);font-weight:800;letter-spacing:-.02em;margin:16px 0 12px">İl il, ilçe ilçe<br>Türkiye'yi keşfet</h1>
  <p style="color:var(--muted);font-size:18px;max-width:600px;margin:0 auto">Gezilecek yerler, gezi rehberleri ve rotalar. Rotanı <strong>Routevia</strong> ile saniyede planla.</p>
</header>
<main class="wrap page" style="padding-top:10px">
  <div class="posts">
{cards}
  </div>
</main>
""" + foot)
    (ROOT / "index.html").write_text(home, encoding="utf-8")
    listing = (head.replace("__T__", "Tüm Gezi Rehberleri").replace("__CANON__", f"{SITE}/blog/")
        + f"""
<main class="wrap page">
  <div class="crumb"><a href="/">Anasayfa</a> › Rehberler</div>
  <h1 class="title">Tüm Gezi Rehberleri</h1>
  <p class="meta">Türkiye'nin il il, ilçe ilçe gezilecek yerleri.</p>
  <div class="posts">
{cards}
  </div>
</main>
""" + foot)
    (BLOG / "index.html").write_text(listing, encoding="utf-8")
    # sitemap
    static = [("/","1.0","daily"),("/blog/","0.8","weekly"),("/hakkinda.html","0.3","yearly"),("/gizlilik.html","0.3","yearly"),("/cerez.html","0.3","yearly")]
    urls = "".join(f'  <url><loc>{SITE}{u}</loc><changefreq>{c}</changefreq><priority>{p}</priority></url>\n' for u,p,c in static)
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
            txt = call_llm(prompt if tryi==0 else prompt+"\n\nYour previous attempt failed validation. Ensure 600+ WORDS and H2/H3/H4 hierarchy and the {{APP_CTA}} token.")
            try: cand = parse_json(txt)
            except Exception as e: print(f"  JSON parse hatası: {e}"); continue
            errs, wc, hh = validate(cand, kw)
            if not errs: d = cand; print(f"  ✓ {wc} kelime · H2/H3/H4={hh}"); break
            print(f"  ✗ doğrulama: {', '.join(errs)} → tekrar")
        if not d:
            print("  ⚠️ bu konu atlandı (kalite tutmadı)"); used.add(kw); continue
        d["slug"] = slugify(d.get("slug") or d["title"])
        write_post(d, app)
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
