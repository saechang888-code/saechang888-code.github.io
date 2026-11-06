# 이재선 시집 자연시 1·2권 (poems.json 자연시) → 시집   python book_poems.py [1|2]
#   1권 『기도원 오솔길에서』 2011–2012년 21편 · 2권 『솔숲에 부는 바람』 2013–2014년 18편
#   anshik/nature{권}/index.html (홈페이지에서 읽는 쪽) + nature{권}.epub + 책만들기\자연시{권}_*.pdf (인쇄용 A5)
#   그림은 책만들기\그림 (캔바에서 만든 수채화), 표지는 책만들기\표지\poem1.png (cover.py)
# 같은 시가 블로그에 두 번 올라간 것은 나중 것 하나만 쓰고, 영어로 옮긴 시는 넣지 않는다. 시 본문은 고치지 않는다.
import os, re, sys, json, html, zipfile, datetime, difflib, subprocess
from PIL import Image
D = os.path.dirname(os.path.abspath(__file__))
BK = os.path.join(os.path.dirname(D), '책만들기')
VOL = int(sys.argv[1]) if len(sys.argv) > 1 else 1
KEY = f'nature{VOL}'
OUT = os.path.join(D, 'anshik', KEY)
os.makedirs(OUT, exist_ok=True)
esc = lambda s: html.escape(s, quote=False)
TITLE = {1: '기도원 오솔길에서', 2: '솔숲에 부는 바람'}[VOL]
SUB, AUTHOR = f'이재선 시집 · 자연시 {VOL}', '이재선'

# ---------- 시 고르기 ----------
P = sorted([p for p in json.load(open(os.path.join(D, 'poems.json'), encoding='utf-8-sig')) if p['cat'] == '자연시'], key=lambda p: p['date'])
def core(b): return re.sub(r'\s', '', ''.join(l for l in b.strip().split('\n')[1:]))
groups = []
for p in P:
    if not re.search('[가-힣]', p['body'][:40]): continue          # 영어로 옮긴 시
    for g in groups:
        if difflib.SequenceMatcher(None, core(p['body']), core(g[0]['body'])).ratio() > 0.6: g.append(p); break
    else: groups.append([p])

def parse(p):
    L = [l.rstrip() for l in p['body'].strip().split('\n')]
    title, notes, body = L[0].strip(), [], []
    for l in L[1:]:
        t = l.strip()
        if t == AUTHOR: continue
        if t.startswith('*') or re.match(r'^\d{4}년\s*\d{1,2}월', t): notes.append(t.lstrip('*').strip()); continue
        body.append(t)
    while body and not body[0]: body.pop(0)
    while body and not body[-1]: body.pop()
    st, cur = [], []
    for t in body:
        if t: cur.append(t)
        elif cur: st.append(cur); cur = []
    if cur: st.append(cur)
    m = re.search(r'(\d{4})년\s*(\d{1,2})월\s*(\d{1,2})일', p['body'])
    d = f'{m.group(1)}-{int(m.group(2)):02d}-{int(m.group(3)):02d}' if m else '2011-06-30'   # 날짜 없는 「끊어진 낚시 줄」은 2011년 여름 시들 곁에
    return dict(title=title, stanzas=st, notes=notes, d=d)

poems = sorted((parse(g[-1]) for g in groups), key=lambda x: x['d'])
poems = [x for x in poems if (x['d'] < '2013') == (VOL == 1)]      # 1권: 2011–2012년 / 2권: 2013–2014년
if VOL == 1:   # 계절로 나눔 (달 기준)
    SEASONS = [('봄', 'spring', (3, 4, 5)), ('여름', 'summer', (6, 7, 8)), ('가을', 'autumn', (9, 10, 11)), ('겨울', 'winter', (12, 1, 2))]
    parts = [(name, key, [x for x in poems if int(x['d'][5:7]) in months]) for name, key, months in SEASONS]
    ART = {k: os.path.join(BK, '그림', k + '.jpg') for _, k, _ in SEASONS}
else:          # 쓴 때를 따라 넷으로 나눔 (2013 늦겨울 · 여름과 가을 · 초겨울 · 2014 솔숲)
    SEASONS = [('늦겨울', 's1', ('2013-01', '2013-03')), ('여름과 가을', 's2', ('2013-03', '2013-11')), ('초겨울', 's3', ('2013-11', '2014-01')), ('솔숲에서', 's4', ('2014-01', '2015'))]
    parts = [(name, key, [x for x in poems if a <= x['d'] < b]) for name, key, (a, b) in SEASONS]
    ART = {k: os.path.join(BK, '그림', 'poem2', k + '.jpg') for _, k, _ in SEASONS}

# ---------- 그림 ----------
def jpg(src, dst, w):
    im = Image.open(src).convert('RGB'); im.thumbnail((w, w * 2)); im.save(dst, quality=84, optimize=True, progressive=True)
jpg(os.path.join(BK, '표지', f'poem{VOL}.png'), os.path.join(OUT, 'cover.jpg'), 1600)
jpg(os.path.join(BK, '표지', f'poem{VOL}.png'), os.path.join(OUT, 'cover_s.jpg'), 600)
for _, key, _ in SEASONS: jpg(ART[key], os.path.join(OUT, key + '.jpg'), 1400)
for i, x in enumerate(poems, 1):                                     # 시마다 그림 한 장 (캔바 AI 애니메이션풍, 주인님 11-06)
    x['art'] = f'p{i:02d}.jpg'; jpg(os.path.join(BK, '그림', 'poems', f'{VOL}-{i:02d}.jpg'), os.path.join(OUT, x['art']), 1200)

INTRO = {1: [f'이 시집에는 이재선 목사가 2011년과 2012년에 쓴 자연시 {len(poems)}편을 담았습니다.',
              '동산교회 수지수양관과 광은기도원에서 기도하고 산책하며 만난 나무와 바람, 매미와 낙엽을 적은 시들입니다.',
              '시마다 끝에 언제 어디서 썼는지를 적은 지은이의 메모를 그대로 두었고, 계절을 따라 봄·여름·가을·겨울로 나누었습니다.'],
         2: [f'이 시집에는 이재선 목사가 2013년과 2014년에 쓴 자연시 {len(poems)}편을 담았습니다.',
              '광은기도원과 명성수양관, 남해 바닷가에서 만난 눈 덮인 소나무와 시냇물, 갈대와 갈매기를 적은 시들입니다.',
              '시마다 끝에 언제 어디서 썼는지를 적은 지은이의 메모를 그대로 두었고, 쓴 때를 따라 넷으로 나누었습니다.']}[VOL]

def poem_html(x, x_ml=False, base=''):
    br = '<br/>' if x_ml else '<br>'
    art = f'<div class="art"><img src="{base}{x["art"]}" alt="「{esc(x["title"])}」 그림"{"/" if x_ml else ""}></div>'
    st = ''.join(f'<p class="st">{br.join(esc(l) for l in s)}</p>' for s in x['stanzas'])
    nt = ''.join(f'<p class="note">{esc(n)}</p>' for n in x['notes'])
    return f'{art}<h3>{esc(x["title"])}</h3>{st}{nt}'

CSS = '''body{font-family:"Nanum Myeongjo","Noto Serif KR",serif;line-height:1.95;color:#2e2a22}
h2{font-size:1.6em;text-align:center;margin:.4em 0 .2em;letter-spacing:.3em}h3{font-size:1.25em;margin:0 0 1.1em;letter-spacing:.04em}
.st{margin:0 0 1.2em;word-break:keep-all}.note{font-size:.84em;color:#857a63;margin:1.6em 0 0;line-height:1.7;word-break:keep-all}
.season img{width:100%;height:auto;border-radius:6px}.art{margin:0 0 1.2em}.art img{width:100%;height:auto;border-radius:6px}'''

# ---------- 홈페이지에서 읽는 쪽 ----------
n = 0; toc = []; secs = []
for name, key, ps in parts:
    if not ps: continue
    toc.append(f'<li class="s"><a href="#{key}">{name}</a></li>' + ''.join(f'<li><a href="#p{n + i + 1}">{esc(x["title"])}</a></li>' for i, x in enumerate(ps)))
    secs.append(f'<section id="{key}" class="season"><img src="{key}.jpg" alt="{name} 수채화" loading="lazy" width="1400" height="933"><h2>{name}</h2></section>')
    for x in ps:
        n += 1; secs.append(f'<article id="p{n}" class="poem">{poem_html(x)}</article>')
page = f'''<!doctype html><html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{TITLE} — {SUB}</title>
<meta name="description" content="이재선 목사(새암교회)의 자연시집 『{TITLE}』 — 기도원과 수양관에서 쓴 자연시 {len(poems)}편을 봄·여름·가을·겨울로 엮었습니다.">
<link rel="canonical" href="https://saechang888-code.github.io/anshik/{KEY}/">
<link href="https://fonts.googleapis.com/css2?family=Nanum+Myeongjo:wght@400;700&family=Noto+Sans+KR:wght@400;700&display=swap" rel="stylesheet">
<style>:root{{--bg:#fbf8f1;--ink:#2e2a22;--muted:#857a63;--accent:#7a5a2e;--rule:#e8dfcd}}
@media (prefers-color-scheme:dark){{:root{{--bg:#1d1b17;--ink:#ece6d8;--muted:#b3a68a;--accent:#d8b27a;--rule:#3a352c}}}}
body{{margin:0;background:var(--bg);color:var(--ink)}}{CSS.replace("#2e2a22", "var(--ink)").replace("#857a63", "var(--muted)")}
.wrap{{max-width:640px;margin:0 auto;padding:0 18px 80px}}.bar{{font-family:"Noto Sans KR",sans-serif;font-size:14px;padding:14px 0;display:flex;gap:12px;flex-wrap:wrap}}
.bar a,#toc a{{color:var(--accent)}}.cover{{text-align:center;margin:12px 0 30px}}.cover img{{width:320px;max-width:76vw;height:auto;border-radius:6px;box-shadow:0 14px 34px rgba(0,0,0,.35)}}
.dl{{display:inline-block;margin:18px 6px 0;padding:9px 18px;border-radius:999px;border:1px solid var(--accent);color:var(--accent);font-family:"Noto Sans KR",sans-serif;font-weight:700;font-size:14px;text-decoration:none}}
.intro{{font-size:15px;color:var(--muted)}}#toc{{font-family:"Noto Sans KR",sans-serif;border:1px solid var(--rule);border-radius:14px;padding:16px 22px;font-size:15px}}
#toc ul{{margin:.4em 0 0;padding:0;list-style:none;columns:2;line-height:1.9}}#toc li.s{{font-weight:700;margin-top:.4em}}
.season{{margin:56px 0 10px}}.poem{{padding:34px 0;border-bottom:1px solid var(--rule)}}</style></head><body><div class="wrap">
<div class="bar"><a href="../../index.html">← 독서주특기 홈</a><a href="../index.html">안식월 시집</a></div>
<div class="cover"><img src="cover_s.jpg" srcset="cover_s.jpg 600w, cover.jpg 1600w" sizes="320px" alt="『{TITLE}』 표지 수채화" width="600" height="900"><br>
<a class="dl" href="{KEY}.epub" download>전자책(EPUB)</a><a class="dl" href="{KEY}.pdf" download>인쇄용 PDF</a></div>
{''.join(f'<p class="intro">{esc(t)}</p>' for t in INTRO)}
<nav id="toc" aria-label="차례"><b>차례</b><ul>{''.join(toc)}</ul></nav>
{''.join(secs)}
<p style="font-family:Noto Sans KR,sans-serif;font-size:13px;color:var(--muted);margin-top:40px">© {AUTHOR} · 새암교회(경기도 용인시 수지구 고기로 165). 그림: 캔바 AI로 그린 그림. 무단 전재를 삼가 주세요.</p>
</div></body></html>'''
open(os.path.join(OUT, 'index.html'), 'w', encoding='utf-8').write(page)
json.dump(dict(title=TITLE, sub=SUB, n=len(poems), intro=INTRO, parts=[[name, [x['title'] for x in ps]] for name, _, ps in parts if ps],
               sample=[dict(title=x['title'], stanzas=x['stanzas'], notes=x['notes'], art=x['art']) for x in poems[:2]]),
          open(os.path.join(OUT, 'toc.json'), 'w', encoding='utf-8'), ensure_ascii=False)   # 블로그 소개 글(blogger.py)이 읽는 차례

# ---------- EPUB 3 ----------
def xhtml(title, body):
    return (f'<?xml version="1.0" encoding="utf-8"?>\n<!DOCTYPE html>\n<html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops" lang="ko" xml:lang="ko">'
            f'<head><meta charset="utf-8"/><title>{esc(title)}</title><link rel="stylesheet" type="text/css" href="style.css"/></head><body>{body}</body></html>')
files = {'cover.xhtml': xhtml(TITLE, f'<div style="text-align:center"><img src="cover.jpg" alt="{TITLE} 표지" style="max-width:100%;max-height:100%"/></div>'),
         'intro.xhtml': xhtml('이 시집에 대하여', '<h3>이 시집에 대하여</h3>' + ''.join(f'<p>{esc(t)}</p>' for t in INTRO))}
navl = ['<li><a href="intro.xhtml">이 시집에 대하여</a></li>']; n = 0
for name, key, ps in parts:
    if not ps: continue
    files[f's_{key}.xhtml'] = xhtml(name, f'<div class="season"><img src="{key}.jpg" alt="{name}"/></div><h2>{name}</h2>')
    sub = []
    for x in ps:
        n += 1; files[f'p{n:02d}.xhtml'] = xhtml(x['title'], poem_html(x, True)); sub.append(f'<li><a href="p{n:02d}.xhtml">{esc(x["title"])}</a></li>')
    navl.append(f'<li><a href="s_{key}.xhtml">{name}</a><ol>{"".join(sub)}</ol></li>')
nav = xhtml('차례', f'<nav epub:type="toc" id="toc"><h2>차례</h2><ol>{"".join(navl)}</ol></nav>')
now = datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
imgs = ['cover.jpg'] + [k + '.jpg' for _, k, ps in parts if ps] + [x['art'] for x in poems]
opf = f'''<?xml version="1.0" encoding="utf-8"?>
<package xmlns="http://www.idpf.org/2007/opf" version="3.0" unique-identifier="bid" xml:lang="ko">
<metadata xmlns:dc="http://purl.org/dc/elements/1.1/"><dc:identifier id="bid">urn:uuid:5a1d0e6c-2011-4e00-9e1a-0000000000a{VOL}</dc:identifier><dc:title>{TITLE} — {SUB}</dc:title>
<dc:creator>{AUTHOR}</dc:creator><dc:language>ko</dc:language><dc:publisher>새암교회</dc:publisher><meta property="dcterms:modified">{now}</meta></metadata>
<manifest><item id="css" href="style.css" media-type="text/css"/><item id="nav" href="nav.xhtml" media-type="application/xhtml+xml" properties="nav"/>
{''.join(f'<item id="i{i}" href="{f}" media-type="image/jpeg"{" properties=" + chr(34) + "cover-image" + chr(34) if i == 0 else ""}/>' for i, f in enumerate(imgs))}
{''.join(f'<item id="{f[:-6]}" href="{f}" media-type="application/xhtml+xml"/>' for f in files)}</manifest>
<spine><itemref idref="cover"/><itemref idref="nav"/>{''.join(f'<itemref idref="{f[:-6]}"/>' for f in files if f != 'cover.xhtml')}</spine></package>'''
ep = os.path.join(OUT, KEY + '.epub')
with zipfile.ZipFile(ep, 'w') as z:
    z.writestr(zipfile.ZipInfo('mimetype'), 'application/epub+zip', compress_type=zipfile.ZIP_STORED)
    z.writestr('META-INF/container.xml', '<?xml version="1.0"?><container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container"><rootfiles><rootfile full-path="OEBPS/content.opf" media-type="application/oebps-package+xml"/></rootfiles></container>', zipfile.ZIP_DEFLATED)
    for name, s in [('content.opf', opf), ('style.css', CSS), ('nav.xhtml', nav)] + list(files.items()): z.writestr('OEBPS/' + name, s, zipfile.ZIP_DEFLATED)
    for f in imgs: z.write(os.path.join(OUT, f), 'OEBPS/' + f)

# ---------- 인쇄용 PDF (A5, 시 한 편에 한 쪽) ----------
pp = [f'<div class="pg cv"><img src="{OUT}/cover.jpg"></div>',
      f'<div class="pg tp"><h1>{TITLE}</h1><p class="s2">{SUB}</p><p class="au">{AUTHOR} 지음</p></div>',
      '<div class="pg"><h3>이 시집에 대하여</h3>' + ''.join(f'<p>{esc(t)}</p>' for t in INTRO) + '</div>']
n = 0; tocp = []
for name, key, ps in parts:
    if not ps: continue
    tocp.append(f'<p class="ts">{name}</p>' + ''.join(f'<p class="ti">{esc(x["title"])}</p>' for x in ps))
    pp.append(f'<div class="pg sn"><img src="{OUT}/{key}.jpg"><h2>{name}</h2></div>')
    for x in ps: pp.append(f'<div class="pg">{poem_html(x, base=OUT + "/")}</div>')
pp.insert(3, f'<div class="pg toc"><h3>차례</h3>{"".join(tocp)}</div>')
pdf_html = f'''<!doctype html><html lang="ko"><head><meta charset="utf-8">
<link href="https://fonts.googleapis.com/css2?family=Nanum+Myeongjo:wght@400;700;800&display=swap" rel="stylesheet">
<style>@page{{size:148mm 210mm;margin:24mm 20mm 18mm}}@page full{{margin:0}}html,body{{margin:0}}{CSS}
.pg{{break-after:page;font-size:10.5pt}}.pg .st{{break-inside:avoid}}
.cv{{page:full}}.cv img{{width:148mm;height:210mm;object-fit:cover;display:block}}
.tp{{text-align:center;padding-top:46mm}}.tp h1{{font-size:26pt;font-weight:800;margin:0}}.tp .s2{{color:#857a63;margin:6mm 0}}.tp .au{{margin-top:40mm;font-weight:700}}
.sn{{padding:16mm 0 0;text-align:center}}.sn img{{width:100%;border-radius:3mm}}.sn h2{{margin-top:12mm}}
.toc{{font-size:10pt;columns:2}}.toc h3{{column-span:all}}.toc .ts{{font-weight:700;margin:3mm 0 1mm;break-after:avoid}}.toc .ti{{margin:0;line-height:1.7}}</style></head>
<body>{"".join(pp)}</body></html>'''
hp = os.path.join(BK, f'_자연시{VOL}.html'); open(hp, 'w', encoding='utf-8').write(pdf_html)
pdf = os.path.join(BK, f'자연시{VOL}_{TITLE.replace(" ", "")}.pdf')
subprocess.run([r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe', '--headless=new', '--disable-gpu', '--virtual-time-budget=8000',
                '--no-pdf-header-footer', f'--print-to-pdf={pdf}', 'file:///' + hp.replace('\\', '/')], capture_output=True)
if os.path.exists(pdf): __import__('shutil').copy(pdf, os.path.join(OUT, KEY + '.pdf'))   # 홈페이지에서 내려받기
print('시', len(poems), '편 ·', [(a, len(c)) for a, _, c in parts], '· EPUB', os.path.getsize(ep), '· PDF', os.path.getsize(pdf) if os.path.exists(pdf) else '없음')
