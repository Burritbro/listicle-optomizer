import re, sys
SRC, OUT = sys.argv[1], sys.argv[2]
B = 'https://static.ll-assets.com/variants/unpublished/24f6f7a488efc0455e1cb95aea962bed'
IMG = B + '/en/assets/image/2bc8e588-69d0-4f7e-b753-a728b316efda/6a66db17e6ff5f11647c24ee/'
LINK = 'https://path.consumergrabs.com/action/3vkva49LIKjr/43h7DYsxFykX/56'
IDX = B + '/index.html'
s = open(SRC).read()

def sub(pat, rep, n=1, flags=re.S):
    global s
    s, k = re.subn(pat, rep, s, flags=flags)
    assert k == n, (pat[:80], k, n)

def cut_div(div_id, replacement=''):
    """Remove the <div id=...> element (balanced) and put replacement in its place."""
    global s
    m = re.search(r'<div id="%s"[^>]*>' % div_id, s); assert m, div_id
    depth = 0
    for t in re.finditer(r'<(/?)div\b[^>]*>', s[m.start():]):
        depth += -1 if t.group(1) else 1
        if depth == 0:
            end = m.start() + t.end()
            s = s[:m.start()] + replacement + s[end:]
            return
    raise ValueError(div_id)

# ---------- head: keep page styles, drop every tracker / CTRWow runtime ----------
styles = re.findall(r'<style>.*?</style>', s[:s.find('</head>')], re.S)
assert len(styles) == 3
dmca = re.sub(r'\.ctr_marked_branding_item_child\s*\{.*?\}\s*\.__ctr_marked_branding_item_img\s*\{.*?\}', '', styles[1], flags=re.S)
FF = '''<!-- FF Pro Page Defaults (must come BEFORE the universal tag). FunnelFlux resolves this page by its URL. -->
    <script>var fluxDefaults = { f: "3vkva49LIKjr" }</script>
    <!-- FF Pro Universal Tag -->
    <script>!function(f,l,u,x,j,s,a,b){window.flux||(j="undefined"!=typeof fluxOptions?fluxOptions:{},s="undefined"!=typeof fluxDefaults?fluxDefaults:{},(a=l.createElement("script")).src="https://"+u+"/integration/lumetricv2.min.js?v="+x,a.type="text/javascript",a.async="true",queue=[],window.flux={track:function(){queue.push(arguments)}},a.onload=a.onreadystatechange=function(){var rs=this.readyState;if(!rs||"complete"==rs||"loaded"==rs)try{for(window.flux=new Lumetric(u,x,j,s);0!=queue.length;){var args=queue.pop();window.flux.track.apply(null,args)}}catch(e){}},(b=document.getElementsByTagName("script")[0]).parentNode.insertBefore(a,b))}(window,document,"path.consumergrabs.com","3.3.0");</script>
    <!-- FF Pro View Event -->
    <script>flux.track("view")</script>'''
head = f'''<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <title>10 Reasons People Are Skipping The Oven and Grill For This Genius Microwave Hack</title>
    <meta name="title" content="10 Reasons People Are Skipping The Oven and Grill For This Genius Microwave Hack">
    {styles[0]}
    <link rel="stylesheet" href="{B}/en/assets/css/pre-1.css">
    {dmca}
    {styles[2]}
    {FF}
  </head>'''
sub(r'<html[^>]*>', '<html lang="en">')
sub(r'<head>.*?</head>', lambda m: head)

# ---------- body: tracking, loaders, hidden iframes, builder branding ----------
cut_div('ivmf'); cut_div('i09q'); cut_div('i3p66l'); cut_div('irswu2')
cut_div('i9wfhl')                      # hidden div with CTRWow tracking iframe (loadimage)
cut_div('ii9prv')                      # "Built with CTRWow" badge
cut_div('batBeacon487446349635')       # Bing beacon
sub(r'\s*<noscript id="i\w+">\s*<iframe[^>]*googletagmanager[^>]*></iframe>\s*</noscript>', '', n=3)
body_scripts = s[s.find('<script id="i6c7m8">'):s.find('</body>')]
assert body_scripts.count('<script') == 11, body_scripts.count('<script')
s = s.replace(body_scripts, '')

# ---------- links ----------
n_cta = s.count('href="%s"' % IDX)
sub(r'(<a id="iy1zk6" ctr-type-link="external" href=")' + re.escape(IDX), r'\1https://consumergrabs.com/privacy')
sub(r'(<a id="i3gh5j" ctr-type-link="external" href=")' + re.escape(IDX), r'\1https://consumergrabs.com/terms')
s = s.replace('href="%s"' % IDX, 'href="%s"' % LINK)
sub(r'href="\./\[www\.dmca\.com/Protection/Status\.aspx\]\(https://www\.dmca\.com/Protection/Status\.aspx\)"', 'href="https://www.dmca.com/Protection/Status.aspx"')
# sticky bar: drop the broken url=/order-now attributes the copy left behind
sub(r' url="[^"]*" order-now"=""', '')

# ---------- videos: plain autoplay video instead of CTRWow player (thumb sat on top of the video without its JS) ----------
def video(src, poster):
    return (f'<video playsinline muted autoplay loop preload="metadata" poster="{poster}" src="{src}" '
            f'style="width:100%;height:auto;display:block"></video>')
for gid, vid_rel, thumb_rel in [
    ('i7fu81', '1fa01656-8523-4f03-81b5-80d5817d0099/banner-1.mp4', '5c9f6e4e-ea17-4fd2-b415-2c95a427ccc9/banner.jpg'),
    ('iiw8nu', 'a4457cf8-0d47-4c1b-8311-5120fce1618a/img-1.1.mp4', '9244e2c0-24fc-425b-a982-7f54730b89f1/img-1.jpg'),
    ('ijhvwu', '23041914-351d-452a-82fd-00be1a6f20cd/img-2.1.mp4', 'bf15ed3c-61b6-47ed-a328-197c8d8b04ec/img-2.jpg'),
    ('ibo089', None, '7672bb48-50ec-42ae-be06-100e0f128dae/img-5.jpg')]:
    # LanderLab's imported MP4s are truncated (~30KB, no moov atom) or missing, so every video loads from the merchant's original
    MERCH = 'https://www.turborocketchef.com/en/assets/image/2bc8e588-69d0-4f7e-b753-a728b316efda/6a66db17e6ff5f11647c24ee/'
    src = MERCH + (vid_rel or '5959afe4-ae22-495b-ab34-4be440440e40/img-5.1.mp4')
    cut_div(gid, video(src, IMG + thumb_rel))
cut_div('i9gcx9')   # Wistia player (4.4-min, 21MB+ TV spot); the section's still image stays

# ---------- rolling dates + sticky bar ----------
sub(r'<span id="ieqb4">Published 06/15/2026 at 3:56 PM</span>', '<span id="ieqb4">Published <span class="pub-date">11/10/2026</span></span>')
for sid, off in [('i9wsjg', 1), ('i326lg', 3), ('ipqnth', 5)]:
    sub(r'<span id="%s" class="datetime">[^<]*</span>' % sid, f'<span id="{sid}" class="datetime" data-days-ago="{off}"></span>')
JS = '''<script>
      (function () {
        var now = new Date();
        function ago(n) { var d = new Date(now); d.setDate(d.getDate() - n); return d; }
        var p = ago(1), pad = function (x) { return (x < 10 ? '0' : '') + x; };
        document.querySelectorAll('.pub-date').forEach(function (e) { e.textContent = pad(p.getMonth() + 1) + '/' + pad(p.getDate()) + '/' + p.getFullYear(); });
        document.querySelectorAll('[data-days-ago]').forEach(function (e) {
          e.textContent = ago(+e.getAttribute('data-days-ago')).toLocaleDateString('en-US', { month: 'short', day: '2-digit', year: 'numeric' });
        });
        // sticky buy bar: show once the reader is past the intro, hide while the final offer box is on screen
        var bar = document.getElementById('idebk7'), start = document.getElementById('i8myb8'), end = document.getElementById('iq0sx');
        function update() {
          if (!bar || !start) return;
          var past = start.getBoundingClientRect().top < 0;
          var r = end && end.getBoundingClientRect(), atEnd = r && r.top < window.innerHeight && r.bottom > 0;
          bar.classList.toggle('hidden', !past || atEnd);
        }
        window.addEventListener('scroll', update, { passive: true });
        window.addEventListener('resize', update);
        update();
      })();
    </script>
  </body>'''
sub(r'\s*</body>', '\n    ' + JS)

body = s[s.find('<body'):]
for bad in ['index.html', 'everflow', 'EF.', 'axon', 'bat.bing', 'clarity', 'googletagmanager', 'gtag(', 'wowsuite.ai/leads', 'ctr_tframe', '__googleAPIKey', 'geolocation']:
    assert bad not in s, bad
assert s.count(LINK) == n_cta - 2, (s.count(LINK), n_cta)
open(OUT, 'w').write(s)
print('ok', len(s), 'CTAs ->', s.count(LINK))
