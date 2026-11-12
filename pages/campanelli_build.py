"""Rebuild the network's Campanelli presell as a ConsumerGrabs page.
usage: python3 -I build.py <source.html> <out.html> <lander_action_link>"""
import re, sys
SRC, OUT, LINK = sys.argv[1], sys.argv[2], sys.argv[3]
NET = 'https://www.unforgettablegadgets.com'
LOGO = 'https://imagedelivery.net/c_gViAg48Noh05UnSpa2Mw/db54eaa4-d42f-498b-7d8e-f9b153484b00/format=webp,w=900,h=300'
s = open(SRC, encoding='utf-8', errors='replace').read()

def sub(pat, rep, n=1, flags=re.S):
    global s
    s, k = re.subn(pat, rep, s, flags=flags)
    assert k == n, (pat[:80], k, n)

# ---- assets: page lives at /clean/, so /images, ../images and ../../images all resolve to /images on the network site
s, k = re.subn(r'((?:src|poster|data-src)=")(?:\.\./)*\.?/?images/', r'\1' + NET + '/images/', s)
assert k > 50, k
s, k2 = re.subn(r"url\((['\"]?)(?:\.\./)*\.?/?images/", r"url(\1" + NET + "/images/", s)   # images referenced from the stylesheet
assert k2 == 8, k2
assert not re.search(r'(?:src|poster|data-src)="(?!https?:|data:)', s), re.findall(r'(?:src|poster|data-src)="(?!https?:|data:)[^"]*', s)[:5]

# ---- head: drop the network's canonical + wrong-product og:image, add FunnelFlux
sub(r'\s*<meta property="og:image"[^>]*>', '')
sub(r'\s*<link rel="canonical"[^>]*>', '')
FF = '''
    <!-- FF Pro Page Defaults (must come BEFORE the universal tag). FunnelFlux resolves this page by its URL. -->
    <script>var fluxDefaults = { f: "3vkva49LIKjr" }</script>
    <!-- FF Pro Universal Tag -->
    <script>!function(f,l,u,x,j,s,a,b){window.flux||(j="undefined"!=typeof fluxOptions?fluxOptions:{},s="undefined"!=typeof fluxDefaults?fluxDefaults:{},(a=l.createElement("script")).src="https://"+u+"/integration/lumetricv2.min.js?v="+x,a.type="text/javascript",a.async="true",queue=[],window.flux={track:function(){queue.push(arguments)}},a.onload=a.onreadystatechange=function(){var rs=this.readyState;if(!rs||"complete"==rs||"loaded"==rs)try{for(window.flux=new Lumetric(u,x,j,s);0!=queue.length;){var args=queue.pop();window.flux.track.apply(null,args)}}catch(e){}},(b=document.getElementsByTagName("script")[0]).parentNode.insertBefore(a,b))}(window,document,"path.consumergrabs.com","3.3.0");</script>
    <!-- FF Pro View Event -->
    <script>flux.track("view")</script>
</head>'''
sub(r'\s*</head>', FF)
sub(r'<html>', '<html lang="en">')

# ---- heatmap.com tracker
sub(r'<script>\s*\(function\(\) \{\s*var _heatmap_paq.*?</script>', '')

# ---- buy links: network action link (+ state) -> your FunnelFlux lander link; state kept as a pass-through param
n_links = len(re.findall(r'href="https://go\.unforgettablegadgets\.com/action/13Vdgb9OlNPc/3Y0sp7qK1RkM/1\?[^"]*"', s))
def relink(m):
    st = re.search(r'state=([^"&]*)', m.group(0)).group(1)
    return 'href="%s%s"' % (LINK, ('?state=' + st.replace(' ', '%20')) if st else '')
s = re.sub(r'href="https://go\.unforgettablegadgets\.com/action/13Vdgb9OlNPc/3Y0sp7qK1RkM/1\?[^"]*"', relink, s)

# ---- branding: header logo + contact, footer + disclosure
sub(r'<a href="/"><img src="' + re.escape(NET) + r'/images/logo-blue-unfgadgets-headphonecouple-hires6\.png" width="314" height="75" alt="Unforgettable Gadgets"></a>',
    f'<a href="{LINK}"><img src="{LOGO}" width="225" height="75" alt="ConsumerGrabs" style="height:60px;width:auto"></a>')
sub(r'<div class="header-nav"><a href="/contact-us/">Contact</a>', '<div class="header-nav"><a href="https://consumergrabs.com/contact" target="_blank">Contact</a>')
footer = '''<div class="footer">
  <div class="container">
    <p><span class="container1">&copy;<span class="cyear">2026</span> ConsumerGrabs<br>
      <a href="https://consumergrabs.com/contact" target="_blank">Contact</a> | <a href="https://consumergrabs.com/privacy" target="_blank">Privacy Policy</a> | <a href="https://consumergrabs.com/terms" target="_blank">Terms</a></span></p>
    <p style="font-size:11px;line-height:1.5;opacity:.75;max-width:760px;margin:10px auto 0">THIS IS AN ADVERTISEMENT AND NOT AN ACTUAL NEWS ARTICLE, BLOG, OR CONSUMER PROTECTION UPDATE. The story depicted on this site is based on the results some people who have used these products have achieved; individual results may vary. This page may receive compensation for clicks on or purchases of products featured on this site.</p>
  </div>
</div>
<script>
  (function () {
    var d = new Date(); d.setDate(d.getDate() - 3);
    var pub = d.toLocaleDateString('en-US', { month: 'long', day: 'numeric', year: 'numeric' });
    document.querySelectorAll('.pub-date').forEach(function (e) { e.textContent = pub; });
    document.querySelectorAll('.cyear').forEach(function (e) { e.textContent = new Date().getFullYear(); });
  })();
</script>
</body>'''
sub(r'<div class="footer">.*?</body>', footer)

# ---- rolling byline date
sub(r'<span class="date">July 8, 2026</span>', '<span class="date pub-date">November 9, 2026</span>')

for bad in ['unforgettablegadgets.com/action', 'heatmap', 'href="/', 'canonical', 'roboform']:
    assert bad not in s, bad
assert s.count(LINK) == n_links + 1, (s.count(LINK), n_links)
open(OUT, 'w').write(s)
print('ok', len(s), '| buy links ->', n_links, '+ logo')
