import re, sys
SRC = sys.argv[1]; OUT = sys.argv[2]
B = 'https://static.ll-assets.com/variants/unpublished/6f3d85ddf005749eeeb3ccb0161b8d98'
s = open(SRC).read()

def sub(pat, rep, n=1, flags=re.S):
    global s
    s, k = re.subn(pat, rep, s, flags=flags)
    assert k == n, (pat[:70], k)

FF = '''<!-- FF Pro Page Defaults (must come BEFORE the universal tag) -->
    <script>var fluxDefaults = { p: "43dJv8NuMnAk", f: "3vkva49LIKjr" }</script>
    <!-- FF Pro Universal Tag -->
    <script>!function(f,l,u,x,j,s,a,b){window.flux||(j="undefined"!=typeof fluxOptions?fluxOptions:{},s="undefined"!=typeof fluxDefaults?fluxDefaults:{},(a=l.createElement("script")).src="https://"+u+"/integration/lumetricv2.min.js?v="+x,a.type="text/javascript",a.async="true",queue=[],window.flux={track:function(){queue.push(arguments)}},a.onload=a.onreadystatechange=function(){var rs=this.readyState;if(!rs||"complete"==rs||"loaded"==rs)try{for(window.flux=new Lumetric(u,x,j,s);0!=queue.length;){var args=queue.pop();window.flux.track.apply(null,args)}}catch(e){}},(b=document.getElementsByTagName("script")[0]).parentNode.insertBefore(a,b))}(window,document,"path.consumergrabs.com","3.3.0");</script>
    <!-- FF Pro View Event -->
    <script>flux.track("view")</script>'''

head = f'''<head>
    <meta charset="utf-8">
    <meta content="width=device-width, initial-scale=1, viewport-fit=cover" name="viewport">
    <title>Why Families Are Rethinking Central Heating This Winter</title>
    <link href="{B}/review/powerheat/assets/css/style.css" rel="stylesheet">
    {FF}
  </head>'''
sub(r'<head>.*?</head>', lambda m: head)        # drops merchant Taboola 1596027, GTM-M3VQK66, 4 junk index.html scripts, index.html stylesheet, bad preconnects

# merchant Taboola page_view events at the end of body
sub(r'\s*<script type="text/javascript" id="ius5og">.*?</script>', '')
sub(r'\s*<script type="text/javascript" id="i3p7bk">.*?</script>', '')

# footer: merchant's relative (broken) legal links -> your pages; publisher copyright
sub(r'href="\./getpowerheatpro\.com/3/terms\.php"', 'href="https://consumergrabs.com/terms"')
sub(r'href="\./getpowerheatpro\.com/3/privacy\.php"', 'href="https://consumergrabs.com/privacy"')
sub(r'href="\./getpowerheatpro\.com/3/contact\.php"', 'href="https://consumergrabs.com/contact"')
sub(r'© 2026 Onninest\. All Rights Reserved\.', '© <span data-local-year>2026</span> ConsumerGrabs. All Rights Reserved.')

# rolling dates via the page's own main.js ([data-local-date] + data-offset)
sub(r'<time id="ia1as">November 4, 2026</time>', '<time id="ia1as" data-local-date="" data-offset="3">Nov 8, 2026</time>')
sub(r'<time id="i67irv">November 11, 2026</time>', '<time id="i67irv" data-local-date="" data-offset="0">Nov 11, 2026</time>')

# typo
sub(r'Cozy Covevides an intelligent solution', 'Cozy Cove provides an intelligent solution')

assert 'tfa.js' not in s and 'GTM-' not in s and 'index.html' not in s and './getpowerheatpro' not in s
assert s.count('/action/3vkva49LIKjr/43dKomq9XRvo/102') == 9, s.count('/action/3vkva49LIKjr/43dKomq9XRvo/102')
open(OUT, 'w').write(s)
print('ok', len(s))
