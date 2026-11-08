import re, sys
LINK = sys.argv[1] if len(sys.argv) > 1 else '{{FUNNELFLUX_LINK}}'
PAGE_ID = sys.argv[2] if len(sys.argv) > 2 else '{{FF_PAGE_ID}}'
OUT = sys.argv[3] if len(sys.argv) > 3 else '/home/user/listicle-optomizer/pages/powerblower_presell_fixed.html'
B = 'https://static.ll-assets.com/variants/unpublished/cbe2f20bde4a6c63cd884e94fb854069'
IMG = B + '/powerblower/app/desktop/images/'
s = open(sys.argv[4] if len(sys.argv) > 4 else 'powerblower_source.html').read()

def cut(pat, n=1, flags=re.S):
    global s
    s, k = re.subn(pat, '', s, flags=flags)
    assert k == n, (pat[:60], k)

# ---------- HEAD ----------
head_new = f'''<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <title>Wood Ranger Power Blower</title>
    <link rel="stylesheet" href="{B}/powerblower/assets/css/app.css">
    <link href="{B}/cdn.jsdelivr.net/npm/bootstrap@5.3.1/dist/css/bootstrap.min.css" rel="stylesheet" crossorigin="anonymous">
    <link href="{B}/powerblower/app/desktop/css/normalise.css" rel="stylesheet" type="text/css">
    <link href="{B}/powerblower/app/desktop/css/components.css" rel="stylesheet" type="text/css">
    <link href="{B}/powerblower/app/desktop/css/next-starter.css" rel="stylesheet" type="text/css">
    <link href="{B}/powerblower/app/desktop/css/presell-beta.css" rel="stylesheet" type="text/css">
    <link rel="stylesheet" href="{B}/cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <!-- FF Pro Page Defaults (must come BEFORE the universal tag) -->
    <script>var fluxDefaults = {{ p: "{PAGE_ID}", f: "3vkva49LIKjr" }}</script>
    <!-- FF Pro Universal Tag -->
    <script>!function(f,l,u,x,j,s,a,b){{window.flux||(j="undefined"!=typeof fluxOptions?fluxOptions:{{}},s="undefined"!=typeof fluxDefaults?fluxDefaults:{{}},(a=l.createElement("script")).src="https://"+u+"/integration/lumetricv2.min.js?v="+x,a.type="text/javascript",a.async="true",queue=[],window.flux={{track:function(){{queue.push(arguments)}}}},a.onload=a.onreadystatechange=function(){{var rs=this.readyState;if(!rs||"complete"==rs||"loaded"==rs)try{{for(window.flux=new Lumetric(u,x,j,s);0!=queue.length;){{var args=queue.pop();window.flux.track.apply(null,args)}}}}catch(e){{}}}},(b=document.getElementsByTagName("script")[0]).parentNode.insertBefore(a,b))}}(window,document,"path.consumergrabs.com","3.3.0");</script>
    <!-- FF Pro View Event -->
    <script>flux.track("view")</script>
  </head>'''
s, k = re.subn(r'<head>.*?</head>', lambda m: head_new, s, count=1, flags=re.S); assert k == 1

# ---------- BODY: merchant tracking ----------
cut(r'\s*<script src="[^"]*kkdi6trk\.com/scripts/main\.js"[^>]*></script>')
cut(r'\s*<script type="text/javascript" id="ixyv">.*?</script>')          # EF.conversion on every load
cut(r'\s*<!-- Google Tag Manager \(noscript\) -->\s*<noscript id="iniu">.*?</noscript><!-- End Google Tag Manager \(noscript\) -->')
# merchant checkout-funnel scripts (config, jQuery form/validation libs, ajax traffic check, address autocomplete)
for sid in ['il8rkh', 'imvoz2', 'iatwba', 'iw7ylo', 'ip0m5k', 'i284kg', 'i28yaw', 'id5q9v']:
    cut(r'\s*<script[^>]*id="%s"[^>]*>.*?</script>' % sid)
for sid in ['i930gf', 'i4zrov', 'iuhfwh', 'imrjhf', 'iog1n8', 'iw4xf1', 'i5l0x4', 'ipxo7k', 'i18207', 'i6ul4l', 'iil3wf', 'iwi4dz', 'imkqh3', 'i6kwak', 'imglop', 'i3ujed']:
    cut(r'\s*<script[^>]*id="%s"[^>]*>\s*</script>' % sid)
cut(r'\s*<iframe id="i7xf1u"[^>]*></iframe>')
# year/query-string script: keep only the copyright year (rest needed jQuery and targeted elements that don't exist)
cut(r'<script id="itrrht">.*?</script>')
s = s.replace('</body>', '''<script>
      document.querySelectorAll(".cyear").forEach(function (el) { el.textContent = new Date().getFullYear(); });
    </script>
  </body>''', 1)

# ---------- links ----------
idx = B + '/index.html'
for cid in ['it2yrg', 'iij3oa', 'ifdyzq']:
    s, k = re.subn(r'(<a id="%s" href=")%s' % (cid, re.escape(idx)), r'\g<1>' + LINK, s); assert k == 1, cid
s, k = re.subn(r'(<a id="iwvlxj" href=")[^"]+', r'\g<1>https://consumergrabs.com/terms', s); assert k == 1
s, k = re.subn(r'(<a id="imn4c4" href=")[^"]+', r'\g<1>https://consumergrabs.com/privacy', s); assert k == 1

# ---------- broken assets ----------
s = s.replace('src="./powerblower/app/desktop/images/trending_usa_mob.svg"', 'src="https://get.woodrangertools.com/powerblower/app/desktop/images/trending_usa_mob.svg"')
s, k = re.subn(r'(<img id="ij0hh" loading="lazy" src=")%s' % re.escape(idx), r'\g<1>' + IMG + 'Img%20-%20Taylor%20Robinson_margin.png', s); assert k == 1
s, k = re.subn(r'(<img id="ih84xi" loading="lazy" src=")%s(" alt=")' % re.escape(idx), r'\g<1>' + IMG + r'image%2025.png\g<2>DMCA Protected', s); assert k == 1
s, k = re.subn(r'poster="/powerblower/app/desktop/images/', 'poster="' + IMG, s); assert k == 5, k

s, k = re.subn(re.escape(B) + r'/video\.woodrangertools\.com/', 'https://video.woodrangertools.com/', s); assert k == 4, k   # LanderLab copies are truncated (no moov atom)
assert 'index.html' not in re.sub(r'<!--.*?-->', '', s, flags=re.S), 'index.html left'
assert 'EF.' not in s and 'googletagmanager' not in re.sub(r'<!--.*?-->', '', s, flags=re.S)
open(OUT, 'w').write(s)
print('ok', OUT, len(s))
