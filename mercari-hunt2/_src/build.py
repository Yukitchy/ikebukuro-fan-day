#!/usr/bin/env python3
"""The Hunt List: 5 motif designs. Builds ../d1.html .. ../d5.html (self-contained: fonts + photos inlined)."""
import base64, pathlib, re, html as H

SRC = pathlib.Path(__file__).parent
OUT = SRC.parent

# ---------- shared content ----------
TITLE = "The Hunt List"
SUB = "Made for the Ferrucho family · your Ikebukuro day, Sun Dec 20 · guide: Yuuki"
INTRO = ("Tell us what you're hunting for before the tour. We check real prices on Mercari, "
         "Japan's biggest second-hand marketplace, and send you actual listings. "
         "Once you approve, we buy it for you and hand it over in Ikebukuro on Dec 20.")
STEPS = [
    ("You", "Send your list", "The item you want and the most you'd spend."),
    ("Yuuki", "Get real listings", "Links and photos of actual items for sale, with one total: item price plus domestic shipping."),
    ("You", "Approve and pay", "Pay by card through a payment link. Nothing is bought before you say yes."),
    ("Yuuki", "Collect it Dec 20", "We place the order and hand it to you on the tour day."),
]
SOLDOUT = "If something sells out, we tell you straight away. We never buy a substitute without asking."
HONEST = [
    "Mercari is second-hand. Before buying, we always send you photos of the actual item.",
    "No service fee for tour guests. You pay the item price plus domestic shipping only (usually ¥200-700).",
    "Popular items sell fast. The sooner we get your list, the better your chances.",
]
NOTE = "Real listings checked Nov 19, 2026. Prices move daily. The price we send you is always the live one."
CATS = [("cards", "Cards"), ("figures", "Figures"), ("games", "Retro Games")]
ITEMS = [
    ("cards", "m36425879874", "Charizard ex SAR", "Pokémon Card 151, Japanese", "¥35,000-70,000", "PSA 10 graded from ¥93,000", "¥40,200"),
    ("cards", "m14043988340", "Monkey D. Luffy SEC OP05-119", "One Piece Card Game, Japanese", "from ¥1,000", "Secret Parallel ¥9,000-25,000", "¥3,300"),
    ("cards", "m17630640437", "Pokémon Card 151 Sealed Box", "Japanese, still shrink-wrapped", "¥39,000-60,000", "", "¥39,800"),
    ("figures", "m25932299194", "Luffy Gear 5 P.O.P WA-MAXIMUM", "MegaHouse", "¥13,000-28,000", "", "¥13,500"),
    ("figures", "m48700980297", "Zoro “Asura” P.O.P WA-MAXIMUM", "MegaHouse", "¥19,000-30,000", "", "¥19,400"),
    ("figures", "m69113118184", "Nagi Seishiro Nendoroid 2056", "Blue Lock", "around ¥6,600", "Prize figures ¥1,100-3,800", "¥6,666"),
    ("games", "m75254338953", "Pokémon Red", "Game Boy, 1996, boxed", "¥7,000-18,500", "Cartridge only from ¥1,800", "¥9,500"),
    ("games", "m84542502513", "Pokémon Crystal", "Game Boy Color, boxed", "¥9,000-18,000", "Cartridge only from ¥2,900", "¥14,599"),
    ("games", "m35783849029", "Game Boy Color, Clear", "Console, tested working", "¥6,500-13,000", "", "¥8,480"),
]
FORM = [("item", "Item you want", "text", "e.g. Luffy Gear 5 figure"),
        ("series", "Series / Title", "text", "e.g. One Piece"),
        ("budget", "Max budget (¥)", "number", "15000"),
        ("used", "Second-hand OK?", "select", ["Yes, second-hand is fine", "New or unopened only", "Ask me first"]),
        ("notes", "Notes", "textarea", "Condition, size, anything else")]
BTN = "Send the hunt list"

e = H.escape
def url(i): return f"https://jp.mercari.com/item/{i}"
def img(i):
    return "data:image/jpeg;base64," + base64.b64encode((SRC / "img" / f"{i}.jpg").read_bytes()).decode()
IMG = {it[1]: img(it[1]) for it in ITEMS}

def fonts(*keys):
    out = []
    for k in keys:
        css = (SRC / "font" / f"{k}.css").read_text()
        css = re.sub(r"url\((font/[^)]+)\)", lambda m: "url(data:font/woff2;base64," + base64.b64encode((SRC / m.group(1)).read_bytes()).decode() + ")", css)
        out.append(css)
    return "\n".join(out)

BASE_CSS = """
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
[hidden]{display:none!important}
html{-webkit-text-size-adjust:100%;scroll-behavior:smooth;scroll-padding-top:16px}
body{min-height:100vh;padding-bottom:calc(72px + env(safe-area-inset-bottom));-webkit-font-smoothing:antialiased;overflow-x:hidden}
img{display:block;max-width:100%}
a{color:inherit}
h1,h2,h3{text-wrap:balance}
p,li{text-wrap:pretty}
input,select,textarea,button{font:inherit;color:inherit}
input,select,textarea{font-size:16px;width:100%}
textarea{resize:vertical;min-height:88px}
.tabbar{position:fixed;left:0;right:0;bottom:0;z-index:50;display:grid;grid-template-columns:repeat(3,1fr);padding-bottom:env(safe-area-inset-bottom)}
.tabbar button{appearance:none;border:0;background:none;cursor:pointer;min-height:60px;white-space:nowrap}
.sent{display:none}
form.done .sent{display:block}
:focus-visible{outline:2px solid currentColor;outline-offset:3px}
@media(prefers-reduced-motion:reduce){*{animation:none!important;transition:none!important;scroll-behavior:auto!important}}
"""

JS = """
const tabs=[...document.querySelectorAll('[data-tab]')],items=[...document.querySelectorAll('[data-cat]')];
function setCat(c,go){items.forEach(el=>el.hidden=el.dataset.cat!==c);
 tabs.forEach(t=>t.setAttribute('aria-selected',t.dataset.tab===c));
 document.querySelectorAll('[data-catname]').forEach(n=>n.textContent=tabs.find(t=>t.dataset.tab===c).dataset.label);
 if(go)document.getElementById('catalog').scrollIntoView({behavior:'smooth'});}
tabs.forEach(t=>t.addEventListener('click',()=>setCat(t.dataset.tab,true)));setCat('cards');
document.querySelector('form').addEventListener('submit',ev=>{ev.preventDefault();ev.target.classList.add('done')});
"""

def tabbar(extra=lambda k: ""):
    b = "".join(f'<button type="button" role="tab" data-tab="{k}" data-label="{e(l)}">{extra(k)}<span>{e(l)}</span></button>' for k, l in CATS)
    return f'<nav class="tabbar" role="tablist" aria-label="Catalog categories">{b}</nav>'

def form_fields(cls=""):
    out = []
    for name, label, kind, ph in FORM:
        if kind == "select":
            ctl = f'<select name="{name}">' + "".join(f"<option>{e(o)}</option>" for o in ph) + "</select>"
        elif kind == "textarea":
            ctl = f'<textarea name="{name}" placeholder="{e(ph)}"></textarea>'
        else:
            ctl = f'<input name="{name}" type="{kind}" placeholder="{e(ph)}"' + (' inputmode="numeric"' if kind == "number" else "") + ">"
        out.append(f'<label class="{cls}"><span>{e(label)}</span>{ctl}</label>')
    return "".join(out)

SENT = '<p class="sent">Preview only. This form is not connected yet.</p>'

def page(n, title_suffix, theme, font_css, css, body):
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<meta name="theme-color" content="{theme}"><title>The Hunt List | {e(title_suffix)}</title>
<style>{font_css}{BASE_CSS}{css}</style></head><body>{body}<script>{JS}</script></body></html>"""

def alt_line(alt, tag="p", cls="alt"):
    return f'<{tag} class="{cls}">{e(alt)}</{tag}>' if alt else ""

# =====================================================================
# D1  WANTED  : the bounty poster. Price = bounty. Form = your own poster.
# =====================================================================
def d1():
    css = """
:root{--paper:#E7DDC7;--sheet:#F3ECDA;--ink:#2B2019;--sub:#6A5948;--red:#9B2A1E;--rule:#CDBFA3}
body{background:var(--paper);color:var(--ink);font:400 17px/1.6 'Zilla Slab',Georgia,serif}
.w{max-width:1080px;margin:0 auto;padding-inline:20px}
.hero{padding-block:56px 48px;text-align:center}
.hero .kw{font:700 15px/1 'Zilla Slab';letter-spacing:.5em;padding-left:.5em;color:var(--red)}
.hero h1{font:700 clamp(38px,12.4vw,118px)/.95 'Zilla Slab';letter-spacing:-.02em;margin:18px 0 22px;white-space:nowrap}
.hero .sub{font:italic 400 16px/1.5 'Zilla Slab';color:var(--sub);max-width:34ch;margin:0 auto}
.hero .lead{max-width:36em;margin:28px auto 0;font-size:18px}
.hero hr{border:0;border-top:3px double var(--ink);width:72px;margin:32px auto 0}
h2{font:700 clamp(26px,8vw,44px)/1.05 'Zilla Slab';text-align:center;white-space:nowrap}
.k{display:block;text-align:center;font:700 13px/1 'Zilla Slab';letter-spacing:.32em;color:var(--red);margin-bottom:12px}
section{padding-block:56px}
.steps{list-style:none;display:grid;gap:0;margin-top:32px;border-top:1px solid var(--rule)}
.steps li{display:grid;grid-template-columns:56px 1fr;gap:4px 16px;padding:20px 0;border-bottom:1px solid var(--rule)}
.steps b{grid-row:span 2;font:700 44px/1 'Zilla Slab';color:var(--red)}
.steps h3{font:700 20px/1.25 'Zilla Slab'}
.steps p{color:var(--sub);font-size:16px}
.so{text-align:center;margin:24px auto 0;max-width:34em;font-style:italic;color:var(--sub);font-size:16px}
#catalog h2 span{color:var(--red)}
.board{display:grid;gap:28px;margin-top:32px;grid-template-columns:1fr}
@media(min-width:640px){.board{grid-template-columns:repeat(2,1fr)}.steps{grid-template-columns:repeat(2,1fr);column-gap:32px}}
@media(min-width:960px){.board{grid-template-columns:repeat(3,1fr)}}
.poster{background:var(--sheet);padding:26px 24px 24px;text-align:center}
.poster .pw{font:700 clamp(40px,13vw,58px)/.9 'Zilla Slab';letter-spacing:.06em;margin-right:-.06em}
.poster figure{margin:18px 0 18px;border:1px solid var(--ink);padding:6px;background:var(--sheet)}
.poster img{width:100%;aspect-ratio:4/5;object-fit:cover;filter:sepia(.12) contrast(1.02)}
.poster h3{font:700 22px/1.2 'Zilla Slab'}
.poster .ln{font-style:italic;color:var(--sub);font-size:15px;margin-top:4px}
.poster .bl{font:700 13px/1 'Zilla Slab';letter-spacing:.3em;margin:20px 0 4px;color:var(--red)}
.poster .bounty{font:700 46px/1 'Zilla Slab';letter-spacing:-.01em;font-variant-numeric:lining-nums tabular-nums}
.poster .mk{margin-top:14px;padding-top:12px;border-top:1px solid var(--rule);font-size:15px}
.poster .alt{font-size:14px;color:var(--sub)}
.poster a{display:inline-block;margin-top:14px;font:700 15px/1 'Zilla Slab';color:var(--red);text-underline-offset:4px}
.pn{text-align:center;font-style:italic;color:var(--sub);font-size:15px;margin-top:28px}
.honest{max-width:40em;margin:28px auto 0;list-style:none;counter-reset:h}
.honest li{padding:16px 0;border-top:1px solid var(--rule)}
.honest li:last-child{border-bottom:1px solid var(--rule)}
.yours{max-width:560px;margin:32px auto 0;background:var(--sheet);padding:32px 24px}
.yours .pw{font:700 clamp(44px,14vw,64px)/.9 'Zilla Slab';letter-spacing:.06em;text-align:center}
.yours .pc{text-align:center;font-style:italic;color:var(--sub);font-size:15px;margin:8px 0 20px}
.yours label{display:block;margin-top:18px}
.yours label span{display:block;font:700 13px/1 'Zilla Slab';letter-spacing:.2em;text-transform:uppercase;margin-bottom:6px}
.yours input,.yours select,.yours textarea{background:transparent;border:0;border-bottom:1.5px solid var(--ink);padding:8px 0;border-radius:0;outline-offset:2px}
.yours button{margin-top:28px;width:100%;background:var(--red);color:var(--sheet);border:0;padding:18px;font:700 18px/1 'Zilla Slab';letter-spacing:.04em;cursor:pointer;transition:transform .12s}
.yours button:active{transform:scale(.98)}
.sent{margin-top:12px;text-align:center;font-style:italic;color:var(--sub)}
.tabbar{background:var(--ink);color:var(--sheet)}
.tabbar button{font:700 15px/1 'Zilla Slab';letter-spacing:.06em;color:rgba(243,236,218,.62);position:relative}
.tabbar button[aria-selected=true]{color:var(--sheet)}
.tabbar button[aria-selected=true]::after{content:"";position:absolute;left:50%;top:0;width:28px;height:3px;margin-left:-14px;background:#D9573F}
.foot{display:block;text-align:center;padding:24px 0 40px;color:var(--sub);font-size:14px}
"""
    steps = "".join(f"<li><b>{i}</b><h3>{e(t)}</h3><p>{e(d)}</p></li>" for i, (_, t, d) in enumerate(STEPS, 1))
    posters = "".join(f"""<article class="poster" data-cat="{c}"><div class="pw">WANTED</div>
<figure><img src="{IMG[i]}" alt="{e(n)}, real Mercari listing photo" loading="lazy"></figure>
<h3>{e(n)}</h3><p class="ln">{e(ln)}</p><p class="bl">BOUNTY SEEN</p><p class="bounty">{ex}</p>
<p class="mk">Market {e(r)}</p>{alt_line(alt)}<a href="{url(i)}" target="_blank" rel="noopener">See the real listing</a></article>"""
                      for c, i, n, ln, r, alt, ex in ITEMS)
    body = f"""<main>
<header class="hero w"><p class="kw">WANTED</p><h1>{TITLE}</h1><p class="sub">{e(SUB)}</p><p class="lead">{e(INTRO)}</p><hr></header>
<section class="w"><span class="k">THE RULES</span><h2>How a bounty is claimed</h2><ol class="steps">{steps}</ol><p class="so">{e(SOLDOUT)}</p></section>
<section class="w" id="catalog"><span class="k">ON THE BOARD</span><h2><span data-catname>Cards</span></h2><div class="board">{posters}</div><p class="pn">{e(NOTE)}</p></section>
<section class="w"><span class="k">FAIR WARNING</span><h2>The honest part</h2><ul class="honest">{''.join(f'<li>{e(h)}</li>' for h in HONEST)}</ul></section>
<section class="w"><span class="k">YOUR TURN</span><h2>Post your own poster</h2>
<form class="yours"><div class="pw">WANTED</div><p class="pc">Fill it in. We go hunting.</p>{form_fields()}<button type="submit">{BTN}</button>{SENT}</form></section>
<footer class="foot">Guide: Yuuki · Ikebukuro, Sun Dec 20</footer></main>{tabbar()}"""
    return page(1, "Wanted", "#2B2019", fonts("zilla"), css, body)

# =====================================================================
# D2  CHART : a nautical chart. Neatline border, magenta course line, soundings.
# =====================================================================
def d2():
    css = """
:root{--paper:#F4F2EA;--water:#DCE9EC;--ink:#13304A;--sub:#4F6577;--mag:#A3296F;--land:#EADFC0;--rule:#B9C8D0}
body{background:var(--paper);color:var(--ink);font:400 16px/1.65 'IBM Plex Sans',system-ui,sans-serif}
.mono{font-family:'IBM Plex Mono',ui-monospace,monospace}
.w{max-width:980px;margin:0 auto;padding-inline:20px}
.neat{height:12px;border:1.5px solid var(--ink);background:repeating-linear-gradient(90deg,var(--ink) 0 24px,var(--paper) 24px 48px);background-clip:content-box;padding:2px}
.hero{padding-block:40px 0}
.hero .meta{display:flex;justify-content:space-between;font:400 13px/1 'IBM Plex Mono';color:var(--sub);margin:14px 0 40px;letter-spacing:.04em}
.hero h1{font:italic 600 clamp(48px,15.5vw,148px)/.9 'Cormorant Garamond',serif;letter-spacing:-.015em;white-space:nowrap}
.hero .sub{margin-top:18px;font:400 14px/1.6 'IBM Plex Mono';color:var(--sub)}
.hero .lead{margin-top:24px;font-size:18px;max-width:34em}
.hero .neat{margin-top:48px}
section{padding-block:56px}
.lab{font:600 13px/1 'IBM Plex Mono';letter-spacing:.14em;color:var(--mag);text-transform:uppercase}
h2{font:italic 600 clamp(32px,10vw,56px)/1 'Cormorant Garamond',serif;margin-top:10px;white-space:nowrap}
.course{list-style:none;margin-top:32px;position:relative}
.course::before{content:"";position:absolute;left:11px;top:14px;bottom:28px;border-left:2px dashed var(--mag)}
.course li{position:relative;padding:0 0 28px 44px}
.course li::before{content:"";position:absolute;left:4px;top:7px;width:16px;height:16px;border:2px solid var(--mag);border-radius:50%;background:var(--paper)}
.course li:last-child::before{background:var(--mag)}
.course .who{font:400 13px/1 'IBM Plex Mono';color:var(--sub);letter-spacing:.06em}
.course h3{font:italic 600 26px/1.15 'Cormorant Garamond',serif;margin-top:6px}
.course p{color:var(--sub);max-width:34em}
.so{border-left:2px solid var(--mag);padding-left:14px;color:var(--ink);max-width:34em}
.sea{background:var(--water)}
.items{list-style:none;margin-top:28px}
.item{display:grid;grid-template-columns:120px 1fr;gap:18px;padding:20px 0;border-top:1px solid var(--rule)}
.item:last-child{border-bottom:1px solid var(--rule)}
.item img{width:120px;height:120px;object-fit:cover;background:var(--paper)}
.item h3{font:italic 600 24px/1.1 'Cormorant Garamond',serif}
.item .ln{font-size:14px;color:var(--sub);margin-top:2px}
.item .snd{display:flex;align-items:baseline;gap:10px;margin-top:10px;flex-wrap:wrap}
.item .ex{font:600 22px/1 'IBM Plex Mono';font-variant-numeric:tabular-nums}
.item .rg{font:400 13px/1.4 'IBM Plex Mono';color:var(--sub)}
.item .alt{font:400 13px/1.4 'IBM Plex Mono';color:var(--sub)}
.item a{display:inline-block;margin-top:10px;font:600 14px/1 'IBM Plex Sans';color:var(--mag);text-underline-offset:4px}
@media(min-width:720px){.items{display:grid;grid-template-columns:1fr 1fr;column-gap:40px}.item:nth-last-child(2){border-bottom:1px solid var(--rule)}.item{grid-template-columns:150px 1fr}.item img{width:150px;height:150px}}
.pn{margin-top:20px;font:400 13px/1.6 'IBM Plex Mono';color:var(--sub)}
.honest{list-style:none;margin-top:24px;max-width:40em}
.honest li{padding:14px 0 14px 28px;position:relative;border-top:1px solid var(--rule)}
.honest li::before{content:"+";position:absolute;left:4px;top:13px;font:600 16px 'IBM Plex Mono';color:var(--mag)}
form{margin-top:28px;max-width:560px;display:grid;gap:18px}
form label span{display:block;font:600 13px/1 'IBM Plex Mono';letter-spacing:.08em;text-transform:uppercase;margin-bottom:8px;color:var(--sub)}
form input,form select,form textarea{border:1.5px solid var(--ink);background:#FBFAF5;padding:12px 14px;border-radius:2px}
form button{margin-top:8px;background:var(--ink);color:var(--paper);border:0;padding:18px;font:italic 600 24px/1 'Cormorant Garamond',serif;cursor:pointer;transition:transform .12s}
form button:active{transform:scale(.98)}
.sent{font:400 13px 'IBM Plex Mono';color:var(--sub)}
.tabbar{background:var(--paper);border-top:1.5px solid var(--ink)}
.tabbar button{font:600 14px/1 'IBM Plex Mono';letter-spacing:.04em;color:var(--sub)}
.tabbar button[aria-selected=true]{color:var(--mag);text-decoration:underline;text-decoration-thickness:2px;text-underline-offset:8px}
.endneat{padding-block:8px 40px}
"""
    steps = "".join(f'<li><p class="who">{e(w)}</p><h3>{e(t)}</h3><p>{e(d)}</p></li>' for w, t, d in STEPS)
    items = "".join(f"""<li class="item" data-cat="{c}"><img src="{IMG[i]}" alt="{e(n)}, real Mercari listing photo" loading="lazy">
<div><h3>{e(n)}</h3><p class="ln">{e(ln)}</p><div class="snd"><span class="ex">{ex}</span><span class="rg">seen · range {e(r)}</span></div>{alt_line(alt)}
<a href="{url(i)}" target="_blank" rel="noopener">Open the listing</a></div></li>""" for c, i, n, ln, r, alt, ex in ITEMS)
    body = f"""<main>
<header class="hero w"><div class="neat"></div><div class="meta"><span>MERCARI WATERS</span><span>IKEBUKURO 35°43′N</span></div>
<h1>{TITLE}</h1><p class="sub">{e(SUB)}</p><p class="lead">{e(INTRO)}</p><div class="neat"></div></header>
<section class="w"><p class="lab">The course</p><h2>Four legs to Dec 20</h2><ol class="course">{steps}</ol><p class="so">{e(SOLDOUT)}</p></section>
<section class="sea" id="catalog"><div class="w"><p class="lab">Charted finds</p><h2 data-catname>Cards</h2><ul class="items">{items}</ul><p class="pn">{e(NOTE)}</p></div></section>
<section class="w"><p class="lab">Read before sailing</p><h2>The honest part</h2><ul class="honest">{''.join(f'<li>{e(h)}</li>' for h in HONEST)}</ul></section>
<section class="w"><p class="lab">Set your heading</p><h2>Plot your hunt</h2><form>{form_fields()}<button type="submit">{BTN}</button>{SENT}</form></section>
<div class="w endneat"><div class="neat"></div></div></main>{tabbar()}"""
    return page(2, "Charted", "#F4F2EA", fonts("chart", "plexmono", "plexsans"), css, body)

# =====================================================================
# D3  LOGBOOK : ship's log typed on a two-colour ribbon. Catalog = cargo manifest.
# =====================================================================
def d3():
    css = """
:root{--page:#F5F2E9;--ink:#1F1D1A;--sub:#6B665C;--red:#B3261E;--rule:#D6D0C2;--margin:#E3A9A2}
body{background:var(--page);color:var(--ink);font:400 16px/1.65 'Courier Prime','Courier New',monospace}
.w{max-width:860px;margin:0 auto;padding-inline:36px 20px;position:relative}
main{position:relative}
main::before{content:"";position:fixed;top:0;bottom:0;left:max(14px,calc(50% - 430px + 14px));border-left:1.5px solid var(--margin);pointer-events:none}
.hero{padding-block:52px 40px}
.hero .lg{font:700 14px/1 'Courier Prime';letter-spacing:.24em;color:var(--red)}
.hero h1{font:700 clamp(34px,11.4vw,88px)/1 'Courier Prime';letter-spacing:-.03em;margin:16px 0 18px;white-space:nowrap}
.hero .sub{color:var(--sub);font-size:15px}
.hero .lead{margin-top:24px;max-width:36em}
section{padding-block:40px}
h2{font:700 clamp(24px,7.4vw,36px)/1.1 'Courier Prime';white-space:nowrap}
h2 .r{color:var(--red)}
.log{width:100%;border-collapse:collapse;margin-top:20px}
.log th{font:700 13px/1 'Courier Prime';letter-spacing:.14em;text-transform:uppercase;text-align:left;color:var(--sub);padding:0 0 10px;border-bottom:1.5px solid var(--ink)}
.log td{padding:14px 0;border-bottom:1px solid var(--rule);vertical-align:top}
.log td:first-child{width:76px;color:var(--red);font-weight:700}
.log b{display:block}
.log span{color:var(--sub);font-size:15px}
.so{margin-top:18px;max-width:36em}
.so::before{content:"NB  ";font-weight:700;color:var(--red)}
.man{margin-top:20px;border-top:1.5px solid var(--ink)}
.row{display:grid;grid-template-columns:96px 1fr;gap:16px;padding:16px 0;border-bottom:1px solid var(--rule)}
.row img{width:96px;height:96px;object-fit:cover;filter:grayscale(.15)}
.row h3{font:700 18px/1.25 'Courier Prime'}
.row .ln{color:var(--sub);font-size:14px}
.row dl{display:grid;grid-template-columns:auto 1fr;gap:2px 12px;margin-top:8px;font-size:15px}
.row dt{color:var(--sub)}
.row dd.ex{color:var(--red);font-weight:700}
.row a{display:inline-block;margin-top:8px;font-weight:700;font-size:15px;text-underline-offset:3px}
@media(min-width:640px){.row{grid-template-columns:140px 1fr}.row img{width:140px;height:140px}}
.pn{margin-top:16px;color:var(--sub);font-size:14px}
.honest{list-style:none;margin-top:16px}
.honest li{padding:12px 0 12px 32px;border-bottom:1px solid var(--rule);position:relative}
.honest li::before{content:"[x]";position:absolute;left:0;color:var(--red);font-weight:700}
form{margin-top:20px;border-top:1.5px solid var(--ink)}
form label{display:grid;grid-template-columns:1fr;gap:6px;padding:14px 0;border-bottom:1px solid var(--rule)}
form label span{font-weight:700;font-size:14px;letter-spacing:.08em;text-transform:uppercase;color:var(--sub)}
form input,form select,form textarea{background:transparent;border:0;padding:4px 0;border-radius:0;font-family:'Courier Prime',monospace;font-size:17px}
form input::placeholder,form textarea::placeholder{color:#A9A294}
@media(min-width:640px){form label{grid-template-columns:200px 1fr;align-items:baseline}}
form button{margin-top:24px;width:100%;background:var(--ink);color:var(--page);border:0;padding:18px;font:700 17px/1 'Courier Prime';letter-spacing:.06em;cursor:pointer;transition:transform .12s}
form button:active{transform:scale(.98)}
.sent{margin-top:10px;color:var(--sub)}
.sig{padding-block:24px 40px;color:var(--sub);font-size:14px}
.tabbar{background:var(--page);border-top:1.5px solid var(--ink)}
.tabbar button{font:700 15px/1 'Courier Prime';color:var(--sub)}
.tabbar button span{padding:6px 2px;border-bottom:2px solid transparent}
.tabbar button[aria-selected=true]{color:var(--ink)}
.tabbar button[aria-selected=true] span{border-color:var(--red)}
"""
    steps = "".join(f"<tr><td>{e(w)}</td><td><b>{e(t)}</b><span>{e(d)}</span></td></tr>" for w, t, d in STEPS)
    rows = "".join(f"""<article class="row" data-cat="{c}"><img src="{IMG[i]}" alt="{e(n)}, real Mercari listing photo" loading="lazy">
<div><h3>{e(n)}</h3><p class="ln">{e(ln)}</p><dl><dt>Seen</dt><dd class="ex">{ex}</dd><dt>Range</dt><dd>{e(r)}</dd>{f'<dt>Also</dt><dd>{e(alt)}</dd>' if alt else ''}</dl>
<a href="{url(i)}" target="_blank" rel="noopener">Listing &gt;</a></div></article>""" for c, i, n, ln, r, alt, ex in ITEMS)
    body = f"""<main>
<header class="hero w"><p class="lg">SHIP'S LOG</p><h1>{TITLE}</h1><p class="sub">{e(SUB)}</p><p class="lead">{e(INTRO)}</p></header>
<section class="w"><h2>How it runs</h2><table class="log"><thead><tr><th>Who</th><th>Entry</th></tr></thead><tbody>{steps}</tbody></table><p class="so">{e(SOLDOUT)}</p></section>
<section class="w" id="catalog"><h2>Manifest: <span class="r" data-catname>Cards</span></h2><div class="man">{rows}</div><p class="pn">{e(NOTE)}</p></section>
<section class="w"><h2>The honest part</h2><ul class="honest">{''.join(f'<li>{e(h)}</li>' for h in HONEST)}</ul></section>
<section class="w"><h2>New log entry</h2><form>{form_fields()}<button type="submit">{BTN}</button>{SENT}</form></section>
<p class="w sig">Signed, Yuuki. Landfall: Ikebukuro, Sun Dec 20.</p></main>{tabbar()}"""
    return page(3, "Ship's Log", "#F5F2E9", fonts("courier"), css, body)

# =====================================================================
# D4  COLORS : maritime signal flags. The hoist spells H-U-N-T.
# =====================================================================
FLAG_CSS = """
.flag{aspect-ratio:3/2;display:block;width:100%}
.f-H{background:linear-gradient(90deg,#fff 50%,var(--red) 50%);box-shadow:inset 0 0 0 1px var(--line)}
.f-U{background:conic-gradient(var(--red) 0 25%,#fff 0 50%,var(--red) 0 75%,#fff 0);box-shadow:inset 0 0 0 1px var(--line)}
.f-N{background:repeating-conic-gradient(var(--blue) 0 25%,#fff 0 50%) 0 0/50% 50%;box-shadow:inset 0 0 0 1px var(--line)}
.f-T{background:linear-gradient(90deg,var(--red) 33.33%,#fff 0 66.66%,var(--blue) 0);box-shadow:inset 0 0 0 1px var(--line)}
.f-C{background:linear-gradient(var(--blue) 20%,#fff 0 40%,var(--red) 0 60%,#fff 0 80%,var(--blue) 0);box-shadow:inset 0 0 0 1px var(--line)}
.f-F{background:#fff;position:relative;box-shadow:inset 0 0 0 1px var(--line);overflow:hidden}
.f-F::after{content:"";position:absolute;inset:0;background:var(--red);clip-path:polygon(50% 0,100% 50%,50% 100%,0 50%)}
.f-R{background:linear-gradient(90deg,transparent 42%,var(--yellow) 0 58%,transparent 0),linear-gradient(transparent 38%,var(--yellow) 0 62%,transparent 0),var(--red)}
"""
def d4():
    css = FLAG_CSS + """
:root{--bg:#F7F6F1;--ink:#111;--sub:#5B5A55;--red:#D3231B;--blue:#1E4C9A;--yellow:#F3C21C;--line:rgba(17,17,17,.14)}
body{background:var(--bg);color:var(--ink);font:400 16px/1.6 'Archivo',system-ui,sans-serif;font-stretch:100%}
.w{max-width:1100px;margin:0 auto;padding-inline:20px}
.hero{padding-block:28px 48px}
.hoist{display:grid;grid-template-columns:repeat(4,1fr);gap:8px}
.cap{display:grid;grid-template-columns:repeat(4,1fr);gap:8px;margin-top:8px;font:700 13px/1 'Archivo';text-align:center;color:var(--sub)}
.hero h1{font:900 clamp(44px,14.6vw,180px)/.86 'Archivo';font-stretch:62%;text-transform:uppercase;letter-spacing:-.01em;margin-top:32px;white-space:nowrap}
.hero .sub{font:600 14px/1.5 'Archivo';margin-top:18px;max-width:40ch}
.hero .lead{font-size:19px;line-height:1.5;margin-top:24px;max-width:34em}
.hero .key{margin-top:20px;font-size:14px;color:var(--sub)}
section{padding-block:48px;border-top:2px solid var(--ink)}
h2{font:900 clamp(34px,11vw,72px)/.9 'Archivo';font-stretch:62%;text-transform:uppercase;white-space:nowrap}
.steps{list-style:none;display:grid;gap:24px;margin-top:28px}
@media(min-width:760px){.steps{grid-template-columns:repeat(4,1fr)}}
.steps li{border-top:1px solid var(--ink);padding-top:12px}
.steps b{display:block;font:900 56px/1 'Archivo';font-stretch:62%}
.steps h3{font:800 20px/1.2 'Archivo';margin-top:8px}
.steps p{color:var(--sub);margin-top:4px}
.so{margin-top:28px;font-weight:600;max-width:40em}
.ch{display:flex;align-items:center;gap:14px}
.ch .flag{width:60px;flex:none}
.grid{display:grid;grid-template-columns:repeat(2,1fr);gap:28px 14px;margin-top:28px}
@media(min-width:760px){.grid{grid-template-columns:repeat(3,1fr);gap:40px 24px}}
.tile img{width:100%;aspect-ratio:1;object-fit:cover;background:#E9E7E0}
@media(max-width:759px){.tile:nth-child(3n+1){grid-column:span 2}.tile:nth-child(3n+1) img{aspect-ratio:4/3}.tile:nth-child(3n+1) .ex{font-size:40px}}
.tile h3{font:800 16px/1.2 'Archivo';margin-top:12px}
.tile .ln{font-size:13px;color:var(--sub);margin-top:2px}
.tile .ex{font:900 30px/1 'Archivo';font-stretch:75%;margin-top:10px;font-variant-numeric:tabular-nums}
.tile .rg{font-size:14px;font-weight:600;margin-top:6px}
.tile .alt{font-size:13px;color:var(--sub)}
.tile a{display:inline-block;margin-top:8px;font-weight:700;font-size:14px;text-underline-offset:3px}
.pn{margin-top:28px;font-size:14px;color:var(--sub)}
.honest{list-style:none;margin-top:24px;display:grid;gap:20px}
@media(min-width:760px){.honest{grid-template-columns:repeat(3,1fr)}}
.honest li{font-size:18px;line-height:1.45;font-weight:600;border-left:4px solid var(--ink);padding-left:14px}
form{margin-top:28px;display:grid;gap:20px;max-width:620px}
form label span{display:block;font:800 13px/1 'Archivo';text-transform:uppercase;letter-spacing:.08em;margin-bottom:8px}
form input,form select,form textarea{border:2px solid var(--ink);background:#fff;padding:12px;border-radius:0}
form button{background:var(--ink);color:#fff;border:0;padding:20px;font:900 24px/1 'Archivo';font-stretch:62%;text-transform:uppercase;letter-spacing:.02em;cursor:pointer;transition:transform .12s}
form button:active{transform:scale(.98)}
.sent{color:var(--sub);font-size:14px}
.tabbar{background:var(--bg);border-top:2px solid var(--ink)}
.tabbar button{display:flex;align-items:center;justify-content:center;gap:8px;font:800 14px/1 'Archivo';color:var(--sub);position:relative}
.tabbar .flag{width:24px}
.tabbar button[aria-selected=true]{color:var(--ink)}
.tabbar button[aria-selected=true]::before{content:"";position:absolute;top:-2px;left:12%;right:12%;height:5px;background:var(--ink)}
@media(max-width:350px){.tabbar .flag{width:18px}.tabbar button{gap:6px;font-size:13px}}
.end{padding-block:24px 40px;font-size:14px;color:var(--sub)}
"""
    fl = {"cards": "C", "figures": "F", "games": "R"}
    steps = "".join(f"<li><b>{i}</b><h3>{e(t)}</h3><p>{e(d)}</p></li>" for i, (_, t, d) in enumerate(STEPS, 1))
    tiles = "".join(f"""<article class="tile" data-cat="{c}"><img src="{IMG[i]}" alt="{e(n)}, real Mercari listing photo" loading="lazy">
<h3>{e(n)}</h3><p class="ln">{e(ln)}</p><p class="ex">{ex}</p><p class="rg">{e(r)}</p>{alt_line(alt)}<a href="{url(i)}" target="_blank" rel="noopener">Real listing</a></article>""" for c, i, n, ln, r, alt, ex in ITEMS)
    body = f"""<main>
<header class="hero w"><div class="hoist" aria-hidden="true"><i class="flag f-H"></i><i class="flag f-U"></i><i class="flag f-N"></i><i class="flag f-T"></i></div>
<div class="cap" aria-hidden="true"><span>H</span><span>U</span><span>N</span><span>T</span></div>
<h1>{TITLE}</h1><p class="sub">{e(SUB)}</p><p class="lead">{e(INTRO)}</p><p class="key">The flags spell HUNT in the international code of signals.</p></header>
<section class="w"><h2>How it works</h2><ol class="steps">{steps}</ol><p class="so">{e(SOLDOUT)}</p></section>
<section class="w" id="catalog"><div class="ch">{''.join(f'<i class="flag f-{fl[k]}" data-cat="{k}" aria-hidden="true"></i>' for k,_ in CATS)}<h2 data-catname>Cards</h2></div><div class="grid">{tiles}</div><p class="pn">{e(NOTE)}</p></section>
<section class="w"><h2>The honest part</h2><ul class="honest">{''.join(f'<li>{e(h)}</li>' for h in HONEST)}</ul></section>
<section class="w"><h2>Raise your flag</h2><form>{form_fields()}<button type="submit">{BTN}</button>{SENT}</form></section>
<p class="w end">Guide: Yuuki. Ikebukuro, Sun Dec 20.</p></main>{tabbar(lambda k: f'<i class="flag f-{fl[k]}" aria-hidden="true"></i>')}"""
    return page(4, "Colors", "#F7F6F1", fonts("archivo"), css, body)

# =====================================================================
# D5  X MARKS THE SPOT : one dashed route runs down the page and ends at X (Dec 20).
# =====================================================================
def d5():
    css = """
:root{--bg:#FBFAF6;--ink:#1A1918;--sub:#6E6A64;--red:#C2161C;--rule:#E4E0D8}
body{background:var(--bg);color:var(--ink);font:400 16px/1.65 'Work Sans',system-ui,sans-serif}
.w{max-width:760px;margin:0 auto;padding-inline:52px 20px;position:relative}
.route{position:relative}
.route::before{content:"";position:absolute;left:max(25px,calc(50% - 380px + 25px));top:300px;bottom:150px;width:2px;
 background:repeating-linear-gradient(var(--red) 0 10px,transparent 10px 20px);pointer-events:none}
.hero{padding-block:40px 64px;position:relative}
.hero .x{font:400 clamp(160px,50vw,320px)/.8 'Bodoni Moda',serif;font-style:italic;color:var(--red);margin-left:-.06em}
.hero h1{font:600 clamp(42px,13.6vw,92px)/1 'Bodoni Moda',serif;letter-spacing:-.025em;margin-top:8px;white-space:nowrap}
.hero .sub{font:600 13px/1.6 'Work Sans';letter-spacing:.04em;margin-top:18px;color:var(--sub);max-width:38ch}
.hero .lead{margin-top:24px;font-size:18px;line-height:1.6}
.stop{position:relative;padding-block:48px}
.stop::before{content:"";position:absolute;left:-33px;top:58px;width:12px;height:12px;border-radius:50%;background:var(--bg);border:2px solid var(--red)}
.lab{font:600 13px/1 'Work Sans';letter-spacing:.16em;text-transform:uppercase;color:var(--red)}
h2{font:600 clamp(30px,9.4vw,52px)/1.05 'Bodoni Moda',serif;letter-spacing:-.015em;margin-top:12px;white-space:nowrap}
.steps{list-style:none;margin-top:24px}
.steps li{padding:18px 0;border-top:1px solid var(--rule);display:grid;grid-template-columns:40px 1fr;gap:0 12px}
.steps b{font:400 30px/1 'Bodoni Moda',serif;color:var(--red);grid-row:span 2}
.steps h3{font:600 18px/1.3 'Work Sans'}
.steps p{color:var(--sub)}
.so{margin-top:16px;font:italic 400 19px/1.45 'Bodoni Moda',serif}
.find{padding:28px 0;border-top:1px solid var(--rule)}
.find:first-of-type{border-top:0}
.find img{width:100%;aspect-ratio:4/3;object-fit:cover;background:#EFECE6}
.find .hd{display:flex;justify-content:space-between;align-items:baseline;gap:16px;margin-top:16px}
.find h3{font:600 24px/1.15 'Bodoni Moda',serif}
.find .ex{font:600 20px/1 'Work Sans';font-variant-numeric:tabular-nums;white-space:nowrap}
.find .ln{color:var(--sub);font-size:15px;margin-top:4px}
.find .rg{font-size:15px;margin-top:8px}
.find .alt{font-size:14px;color:var(--sub)}
.find a{display:inline-block;margin-top:10px;font-weight:600;font-size:15px;color:var(--red);text-underline-offset:4px}
@media(min-width:620px){.find{display:grid;grid-template-columns:260px 1fr;gap:28px;align-items:start}.find img{aspect-ratio:1}.find .hd{margin-top:0}}
.pn{margin-top:12px;font-size:14px;color:var(--sub)}
.honest{list-style:none;margin-top:20px}
.honest li{padding:14px 0;border-top:1px solid var(--rule)}
.dest{position:relative;padding-block:56px 48px}
.dest .xm{position:absolute;left:-44px;top:36px;font:italic 400 56px/1 'Bodoni Moda',serif;color:var(--red)}
form{margin-top:24px;display:grid;gap:18px}
form label span{display:block;font:600 13px/1 'Work Sans';letter-spacing:.08em;text-transform:uppercase;margin-bottom:8px;color:var(--sub)}
form input,form select,form textarea{border:0;border-bottom:1.5px solid var(--ink);background:transparent;padding:10px 0;border-radius:0}
form button{margin-top:12px;background:var(--red);color:#fff;border:0;padding:18px;font:600 17px/1 'Work Sans';letter-spacing:.02em;cursor:pointer;transition:transform .12s}
form button:active{transform:scale(.98)}
.sent{color:var(--sub);font-size:14px}
.tabbar{background:rgba(251,250,246,.94);backdrop-filter:blur(8px);-webkit-backdrop-filter:blur(8px);border-top:1px solid var(--rule)}
.tabbar button{font:600 15px/1 'Work Sans';color:var(--sub)}
.tabbar button[aria-selected=true]{color:var(--red)}
.tabbar button[aria-selected=true] span::before{content:"\\00d7\\00a0";font-family:'Bodoni Moda',serif;font-style:italic}
"""
    steps = "".join(f"<li><b>{i}</b><h3>{e(t)}</h3><p>{e(d)}</p></li>" for i, (_, t, d) in enumerate(STEPS, 1))
    finds = "".join(f"""<article class="find" data-cat="{c}"><img src="{IMG[i]}" alt="{e(n)}, real Mercari listing photo" loading="lazy">
<div><div class="hd"><h3>{e(n)}</h3><span class="ex">{ex}</span></div><p class="ln">{e(ln)}</p><p class="rg">Market {e(r)}</p>{alt_line(alt)}
<a href="{url(i)}" target="_blank" rel="noopener">See the listing</a></div></article>""" for c, i, n, ln, r, alt, ex in ITEMS)
    body = f"""<main class="route">
<header class="hero w"><div class="x" aria-hidden="true">x</div><h1>{TITLE}</h1><p class="sub">{e(SUB)}</p><p class="lead">{e(INTRO)}</p></header>
<section class="w stop"><p class="lab">The route</p><h2>Four steps to X</h2><ol class="steps">{steps}</ol><p class="so">{e(SOLDOUT)}</p></section>
<section class="w stop" id="catalog"><p class="lab">Found so far</p><h2 data-catname>Cards</h2><div>{finds}</div><p class="pn">{e(NOTE)}</p></section>
<section class="w stop"><p class="lab">Before you go</p><h2>The honest part</h2><ul class="honest">{''.join(f'<li>{e(h)}</li>' for h in HONEST)}</ul></section>
<section class="w dest"><span class="xm" aria-hidden="true">x</span><p class="lab">Ikebukuro, Sun Dec 20</p><h2>Mark your X</h2><form>{form_fields()}<button type="submit">{BTN}</button>{SENT}</form></section>
</main>{tabbar()}"""
    return page(5, "X Marks the Spot", "#FBFAF6", fonts("bodoni", "work"), css, body)

if __name__ == "__main__":
    for n, f in enumerate([d1, d2, d3, d4, d5], 1):
        s = f()
        assert "—" not in s and "–" not in s, f"dash in d{n}"
        (OUT / f"d{n}.html").write_text(s)
        print(f"d{n}.html {len(s)//1024}KB")
