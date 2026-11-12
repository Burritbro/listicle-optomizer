"""Restyle the LanderLab Campanelli presell to the ConsumerGrabs house style (L1 listicle look).
usage: python3 -I campanelli_cg_build.py <landerlab_export.html> <out.html>

- Brand system copied from consumergrabs.com/l1: blue header bar + logo, Arial/Helvetica ink #23201A,
  azure #1F6FD6 CTAs, amber number pills, soft yellow highlight, cream legal footer.
- Removes everything that isn't page content or your FunnelFlux tag (lazy-load + state-button scripts,
  the leftover landerlab.io placeholder button, empty widgets).
- Inline images re-encoded to metadata-free WebP (drops Adobe Firefly C2PA 'Generated Image' credentials).
"""
import re, sys, io, base64
from PIL import Image

SRC, OUT = sys.argv[1], sys.argv[2]
LINK = 'https://path.consumergrabs.com/action/35'
LOGO = 'https://imagedelivery.net/c_gViAg48Noh05UnSpa2Mw/db54eaa4-d42f-498b-7d8e-f9b153484b00/format=webp,w=900,h=300'
s = open(SRC, encoding='utf-8').read()


def sub(pat, rep, n=1, flags=re.S):
    global s
    s, k = re.subn(pat, rep, s, flags=flags)
    assert k == n, (pat[:80], k, n)


# ---------- head: brand CSS + FunnelFlux only ----------
CSS = r'''
      :root {
        --cg-blue: #3358d4; --blue: #1F6FD6; --blue-dark: #1858AE;
        --hl: #FFE9AE; --num: #F2A33C;
        --ink: #23201A; --ink-soft: #46413A; --muted: #6B6458;
        --line: #EFE7D8; --cream: #F8F2E7; --green: #157A3B; --green-bg: #E2F6E6;
      }
      *, ::before, ::after { box-sizing: border-box }
      html { -webkit-text-size-adjust: 100%; -webkit-tap-highlight-color: transparent }
      body { margin: 0; background: #fff; color: var(--ink); font-family: Helvetica, Arial, "Segoe UI", sans-serif;
             font-size: 17.5px; line-height: 1.65; -webkit-font-smoothing: antialiased; overflow-x: hidden }
      @media (min-width: 768px) { body { font-size: 19px } }
      img, video { display: block; max-width: 100%; height: auto }
      p { margin: 0 0 18px }
      strong { font-weight: 700 }
      a { color: var(--blue); font-weight: 600; text-decoration: none }
      a:hover { text-decoration: underline }

      /* header — same bar as L1 */
      .header { background: var(--cg-blue); border-top: 6px solid #3a3a3a; padding: 6px 20px; text-align: center }
      .header-logo a { display: inline-block; line-height: 0 }
      .header-logo img { width: auto; height: 80px; margin: 0 auto }
      @media (min-width: 768px) { .header-logo img { height: 92px } }
      .notice { display: block; text-align: center; font-size: 11px; letter-spacing: .12em; text-transform: uppercase;
                color: #8a8378; padding: 10px 0 0 }

      /* article column */
      .content { padding: 4px 0 8px }
      .container, .container-sm { max-width: 840px; margin: 0 auto; padding: 0 20px }
      .container { padding: 0 20px }
      .content-heading { text-align: center }
      .teaser { font-style: italic; font-size: 18px; color: var(--ink-soft); margin: 8px 0 6px }
      h1 { font-family: Arial, Helvetica, sans-serif; font-size: clamp(30px, 6.4vw, 46px); font-weight: 800; line-height: 1.12;
           letter-spacing: -.5px; color: var(--ink); margin: 6px auto 14px; max-width: 760px }
      .byline { display: flex; flex-wrap: wrap; justify-content: center; align-items: center; gap: 4px 8px;
                font-size: 15px; color: var(--muted); margin: 0 0 22px }
      .byline b { color: var(--ink-soft) }
      .byline .dot { opacity: .6 }
      .byline a { color: var(--muted); font-weight: 400; text-decoration: underline }

      .media { margin: 0 0 22px }
      .media video, .media img { width: 100%; border-radius: 12px; background: #f2efe9 }

      .highlight { background: var(--hl); padding: 1px 3px; box-decoration-break: clone; -webkit-box-decoration-break: clone }
      .content-tag { display: block; background: #FFF6E5; border-left: 4px solid var(--num); border-radius: 6px;
                     padding: 12px 14px; font-size: 16px; color: var(--ink-soft) }

      /* numbered reasons — L1 item title with amber pill */
      .item-title { font-family: Arial, Helvetica, sans-serif; font-size: clamp(22px, 4.6vw, 30px); font-weight: 800;
                    line-height: 1.22; letter-spacing: -.2px; color: var(--ink); margin: 34px 0 14px }
      .num { display: inline-flex; align-items: center; justify-content: center; background: var(--num); color: var(--ink);
             border-radius: 50%; width: 1.45em; height: 1.45em; font-size: .82em; margin-right: 10px; vertical-align: 3px;
             box-shadow: 0 2px 0 rgba(35, 32, 26, .18) }

      /* feature card */
      .highlight-box { border: 1px solid var(--line); border-radius: 14px; background: #FFFCF6; padding: 18px; margin: 26px 0 }
      .highlight-box video { width: 100%; border-radius: 10px; margin: 0 0 16px }
      .highlight-box h2 { font-family: Arial, Helvetica, sans-serif; font-size: 24px; font-weight: 800; line-height: 1.2;
                          color: var(--ink); margin: 0 0 12px }
      .highlight-box ul { list-style: none; padding: 0; margin: 0 0 16px }
      .highlight-box li { position: relative; padding-left: 30px; margin: 0 0 8px; font-weight: 600 }
      .highlight-box li::before { content: "\2713"; position: absolute; left: 0; top: 1px; width: 20px; height: 20px;
                                  border-radius: 50%; background: var(--green-bg); color: var(--green); font-size: 13px;
                                  line-height: 20px; text-align: center; font-weight: 800 }

      /* CTAs — L1 button */
      /* !important: LanderLab's published styles.css restyles .ll-btn-temp */
      .cta_b, .ll-btn-temp { display: block !important; width: 100% !important; margin: 20px 0 !important; padding: 16px 20px !important;
             background: var(--blue) !important; color: #fff !important; border: 0 !important; border-radius: 8px !important;
             box-shadow: none !important; font: 700 18px/1.25 Helvetica, Arial, sans-serif !important;
             text-align: center !important; text-decoration: none !important; cursor: pointer }
      .cta_b::after, .ll-btn-temp::after { content: " \2192" }
      .cta_b:hover, .ll-btn-temp:hover { background: var(--blue-dark) !important }
      .deal-badge { display: table; margin: 26px auto 0; padding: 7px 16px; border: 1px solid #1FA94F; border-radius: 999px;
                    background: var(--green-bg); color: var(--green) !important; font-size: 15px; font-weight: 700 }
      .promo { border-top: 1px solid var(--line); margin-top: 30px; padding-top: 24px }

      /* legal footer — L1 cream */
      .footer { background: var(--cream); border-top: 1px solid var(--line); margin-top: 34px; padding: 28px 0 44px;
                font-size: 12.5px; line-height: 1.55; color: #666; text-align: center }
      .footer .links { margin: 0 0 14px; font-size: 14px }
      .footer .links a { color: var(--ink-soft); font-weight: 600 }
      .footer .links span { margin: 0 8px; color: #bbb }
      .footer .disc { text-align: left; margin: 0 0 12px }
      .footer .disc b { display: block; color: var(--ink); font-size: 13px; margin-bottom: 4px }
      .footer .copyright { border-top: 1px solid var(--line); margin: 20px 0 0; padding-top: 16px }
    '''
FF = '''<!-- FF Pro Page Defaults (must come BEFORE the universal tag). FunnelFlux resolves this page by its URL. -->
    <script>var fluxDefaults = { f: "3vkva49LIKjr" }</script>
    <!-- FF Pro Universal Tag -->
    <script>!function(f,l,u,x,j,s,a,b){window.flux||(j="undefined"!=typeof fluxOptions?fluxOptions:{},s="undefined"!=typeof fluxDefaults?fluxDefaults:{},(a=l.createElement("script")).src="https://"+u+"/integration/lumetricv2.min.js?v="+x,a.type="text/javascript",a.async="true",queue=[],window.flux={track:function(){queue.push(arguments)}},a.onload=a.onreadystatechange=function(){var rs=this.readyState;if(!rs||"complete"==rs||"loaded"==rs)try{for(window.flux=new Lumetric(u,x,j,s);0!=queue.length;){var args=queue.pop();window.flux.track.apply(null,args)}}catch(e){}},(b=document.getElementsByTagName("script")[0]).parentNode.insertBefore(a,b))}(window,document,"path.consumergrabs.com","3.3.0");</script>
    <!-- FF Pro View Event -->
    <script>flux.track("view")</script>'''
head = f'''<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <meta name="format-detection" content="telephone=no">
    <title>Campanelli Pro Series Stain Remover on QVC!</title>
    <style>{CSS}</style>
    {FF}
  </head>'''
sub(r'<head>.*?</head>', lambda m: head)   # drops old CSS, lazy-load script, state-button script, duplicate meta

# ---------- header ----------
sub(r'<div id="iisi" class="header">.*?</div>\s*</div>\s*</div>',
    f'''<header id="iisi" class="header">
      <div id="iesw" class="header-logo">
        <a id="ic5e" href="{LINK}"><img id="if0t" src="{LOGO}" width="225" height="75" alt="ConsumerGrabs"></a>
      </div>
    </header>
    <span id="itrt9" class="notice">Advertisement</span>''')

# ---------- headline block: L1 teaser + byline ----------
sub(r'<p id="i7t74" class="content-prehead"> </p>',
    '<p id="i7t74" class="teaser">The XL stain remover QVC shoppers keep reordering</p>')
sub(r'<div id="ie0kc">.*?</div>',
    '''<div id="ie0kc" class="byline">by <b>Mike James</b><span class="dot">&middot;</span><span class="pub-date">November 9, 2026</span><span class="dot">&middot;</span><a href="#disclosure">Advertiser Disclosure</a></div>''')

# ---------- media ----------
sub(r'<p id="ipimr">\s*<video id="iyvx5"[^>]*>\s*<source[^>]*src="([^"]+)">\s*</video>\s*</p>',
    r'<div id="ipimr" class="media"><video id="iyvx5" autoplay muted loop playsinline controls preload="auto" src="\1"></video></div>')
sub(r'<video id="iqvk7"[^>]*src="([^"]+)"[^>]*>\s*<source[^>]*>\s*</video>',
    r'<video id="iqvk7" autoplay muted loop playsinline preload="metadata" src="\1"></video>')


def webp(b64, width=1200):
    im = Image.open(io.BytesIO(base64.b64decode(b64))).convert('RGB')
    if im.width > width:
        im = im.resize((width, round(im.height * width / im.width)), Image.LANCZOS)
    out = io.BytesIO(); im.save(out, 'WEBP', quality=80, method=6)   # PIL writes no EXIF/XMP/C2PA unless asked
    return im.size, base64.b64encode(out.getvalue()).decode()


def inline_img(m):
    (w, h), data = webp(m.group(3))
    return f'<img id="{m.group(1)}" alt="{m.group(2)}" width="{w}" height="{h}" src="data:image/webp;base64,{data}">'
s, k = re.subn(r'<img id="(\w+)" alt="([^"]*)" src="data:image/\w+;base64,([^"]+)">', inline_img, s)
assert k == 2, k
for cid in ['io8qte', 'iarqwq', 'i7q7d1']:          # image wrappers -> rounded media blocks
    sub(r'<div id="%s" class="container">' % cid, f'<div id="{cid}" class="container media">')
s = re.sub(r'\s*<p id="(iggv2q|iy1rge|i103dk)"></p>', '', s)
sub(r'(<img id="iyql42"[^>]*?) class="ll-image">', r'\1 loading="lazy" width="1570" height="1011">')

# ---------- numbered reasons -> L1 item titles with amber pills ----------
s, k = re.subn(r'<p id="(\w+)">\s*<strong id="\w+">(\d)\. (.*?)</strong>\s*</p>',
               r'<h3 id="\1" class="item-title"><span class="num">\2</span>\3</h3>', s)
assert k == 9, k

# ---------- CTAs / offer block ----------
sub(r'<div id="iqcna" class="cta_contain">\s*(<a id="cta_b".*?</a>)\s*</div>', r'\1')
s = s.replace(' name="ck" value="Check Availability"', '').replace(' name="ck" value="Check Inventory &amp; Apply Discount!"', '')
sub(r'<p id="itpeh2">\s*<strong id="\w+">November 2026: (.*?)</strong>\s*</p>',
    r'<p id="itpeh2" class="promo"><strong><span class="cur-month">November</span> <span class="cyear">2026</span>: \1</strong></p>')
# leftover LanderLab placeholder button (href="https://landerlab.io") + empty widgets -> one real CTA with deal pill
sub(r'<div id="il680i" class="clear"></div>.*?<p id="iakxej">&nbsp;</p>',
    f'''<a class="deal-badge" href="{LINK}" data-lum="action">&#127991;&#65039; Special Deal: Up To 40% OFF</a>
        <a id="ivvagm" href="{LINK}" data-lum="action" class="ll-btn-temp">Shop Campanelli Now</a>''')
s = re.sub(r'\s*<div id="imdml" class="clear"></div>', '', s)
s = re.sub(r'\s+data-gjs-type="[^"]*"', '', s)
s = s.replace(' class="mb-0 fw-bold"', '').replace(' class="fw-bold"', '')

# ---------- footer ----------
sub(r'<div id="ipzwjp" class="footer">.*?</div>\s*</div>',
    f'''<footer id="disclosure" class="footer">
      <div class="container">
        <p class="links"><a href="https://consumergrabs.com/privacy" target="_blank">Privacy Policy</a><span>|</span><a href="https://consumergrabs.com/terms" target="_blank">Terms of Service</a><span>|</span><a href="https://consumergrabs.com/contact" target="_blank">Contact Us</a></p>
        <p class="disc"><b>Advertisement</b>THIS IS AN ADVERTISEMENT AND NOT AN ACTUAL NEWS ARTICLE, BLOG, OR CONSUMER PROTECTION UPDATE. The story depicted on this site is based on the results some people who have used these products have achieved; individual results may vary.</p>
        <p class="disc"><b>Affiliate Disclosure</b>This site contains paid advertising. We may receive compensation for clicks on or purchases of products featured on this page.</p>
        <p class="copyright">&copy; <span class="cyear">2026</span> Consumergrabs.com &mdash; All Rights Reserved.</p>
      </div>
    </footer>''')

# ---------- dates ----------
sub(r'<script id="i1kmjk">.*?</script>', '''<script>
      (function () {
        var now = new Date(), d = new Date(now); d.setDate(d.getDate() - 3);
        var pub = d.toLocaleDateString('en-US', { month: 'long', day: 'numeric', year: 'numeric' });
        document.querySelectorAll('.pub-date').forEach(function (e) { e.textContent = pub; });
        document.querySelectorAll('.cyear').forEach(function (e) { e.textContent = now.getFullYear(); });
        document.querySelectorAll('.cur-month').forEach(function (e) { e.textContent = now.toLocaleDateString('en-US', { month: 'long' }); });
      })();
    </script>''')

# ---------- audit: nothing but page content + FunnelFlux ----------
text = re.sub(r'data:image/webp;base64,[A-Za-z0-9+/=]+', 'data:', s)   # audit markup, not image bytes
for bad in ['landerlab.io', 'unforgettablegadgets.com/action', 'heatmap', 'gtag(', 'googletagmanager', 'fbq(', 'fbevents', 'facebook.com/tr',
            'taboola', 'clarity', 'bat.bing', 'tiktok', 'everflow', '<iframe', 'lazy-video', 'class="lazy', 'boxed_province', 'Firefly', 'c2pa']:
    assert bad not in text, bad
scripts = re.findall(r'<script[^>]*>', s)
assert len(scripts) == 4, scripts        # fluxDefaults, FF tag, flux.track view, date script
assert s.count(f'href="{LINK}"') == 13, s.count(f'href="{LINK}"')
open(OUT, 'w', encoding='utf-8').write(s)
print('ok', len(s), 'bytes | links ->', s.count(f'href="{LINK}"'), '| scripts', len(scripts))
