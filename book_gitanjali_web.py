# 이재선 찬양시집 『아침 파도』(기탄잘리) → 홈페이지   python book_gitanjali_web.py
#   책만들기\기탄잘리\plan.json·src.json (book_gen.py 와 같은 자료) · 그림 책만들기\그림\gitanjali (르누아르, 퍼블릭 도메인) · 표지 책만들기\표지\gitanjali1.png
#   anshik/gitanjali/index.html + gitanjali.epub + gitanjali.pdf   시 본문은 고치지 않는다.
import os, re, sys, json, html, zipfile, datetime, shutil
from PIL import Image
D = os.path.dirname(os.path.abspath(__file__))
BK = os.path.join(os.path.dirname(D), '책만들기')
H = os.path.join(BK, '기탄잘리')
KEY = 'gitanjali'
OUT = os.path.join(D, 'anshik', KEY)
os.makedirs(OUT, exist_ok=True)
esc = lambda s: html.escape(s, quote=False)
B = json.load(open(os.path.join(H, 'plan.json'), encoding='utf-8'))['books'][0]
SRC = {str(x['key']): x for x in json.load(open(os.path.join(H, 'src.json'), encoding='utf-8'))}
TITLE, AUTHOR, SUB = B['title'], '이재선', '이재선 찬양시집 · 기탄잘리'
INTRO, CAPS = B['intro'], B['captions']
CREDIT = B['colophon'][0]

def parse(body):
    L = [l.rstrip() for l in body.strip().split('\n')]
    title, notes, lines = L[0].strip(), [], []
    for l in L[1:]:
        t = l.strip()
        if t == AUTHOR: continue
        if t.startswith('*') or re.match(r'^\d{4}년\s*\d{1,2}월', t): notes.append(t.lstrip('*').strip()); continue
        lines.append(t)
    while lines and not lines[0]: lines.pop(0)
    while lines and not lines[-1]: lines.pop()
    st, cur = [], []
    for t in lines:
        if t: cur.append(t)
        elif cur: st.append(cur); cur = []
    if cur: st.append(cur)
    return dict(title=title, stanzas=st, notes=notes)

def jpg(src, dst, w):
    im = Image.open(src).convert('RGB'); im.thumbnail((w, w * 2)); im.save(dst, quality=84, optimize=True, progressive=True)
cv = Image.open(os.path.join(BK, '표지', 'gitanjali1.png')).convert('RGB')
cw = cv.height * 2 // 3; cv = cv.crop(((cv.width - cw) // 2, 0, (cv.width - cw) // 2 + cw, cv.height))
cv.resize((1400, 2100), Image.LANCZOS).save(os.path.join(OUT, 'cover.jpg'), quality=84, optimize=True, progressive=True)
cv.resize((600, 900), Image.LANCZOS).save(os.path.join(OUT, 'cover_s.jpg'), quality=84, optimize=True, progressive=True)

poems = []
for n, k in enumerate(B['poems'], 1):
    x = parse(SRC[str(k)]['body']); x['art'] = f'p{n:02d}.jpg'; x['cap'] = CAPS[n - 1]
    jpg(os.path.join(B['art_dir'], f'{n:02d}.jpg'), os.path.join(OUT, x['art']), 900); poems.append(x)

def poem_html(x, ml=False):
    br = '<br/>' if ml else '<br>'
    art = f'<figure class="art"><img src="{x["art"]}" alt="{esc(x["cap"])}"{"/" if ml else ""}><figcaption>{esc(x["cap"])}</figcaption></figure>'
    st = ''.join(f'<p class="st">{br.join(esc(l) for l in s)}</p>' for s in x['stanzas'])
    nt = ''.join(f'<p class="note">{esc(n)}</p>' for n in x['notes'])
    return f'{art}<h3>{esc(x["title"])}</h3>{st}{nt}'

CSS = '''body{font-family:"Nanum Myeongjo","Noto Serif KR",serif;line-height:1.95;color:#2e2a22}
h2{font-size:1.5em;text-align:center;margin:.4em 0 .2em;letter-spacing:.1em}h3{font-size:1.25em;margin:0 0 1.1em;letter-spacing:.04em}
.st{margin:0 0 1.2em;word-break:keep-all}.note{font-size:.84em;color:#857a63;margin:1.6em 0 0;line-height:1.7;word-break:keep-all}
.art{margin:0 auto 1.4em;max-width:480px;text-align:center}.art img{width:100%;height:auto;border-radius:4px}.art figcaption{font-size:.78em;color:#857a63;margin-top:.5em}'''

toc = ''.join(f'<li><a href="#p{i}">{esc(x["title"])}</a></li>' for i, x in enumerate(poems, 1))
secs = ''.join(f'<article id="p{i}" class="poem">{poem_html(x)}</article>' for i, x in enumerate(poems, 1))
page = f'''<!doctype html><html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{TITLE} — {SUB}</title>
<meta name="description" content="이재선 목사(새암교회)의 찬양시집 『{TITLE}』 — {esc(B['sub'])}. 찬양시 {len(poems)}편과 르누아르의 그림.">
<link rel="canonical" href="https://saechang888-code.github.io/anshik/{KEY}/">
<link href="https://fonts.googleapis.com/css2?family=Nanum+Myeongjo:wght@400;700&family=Noto+Sans+KR:wght@400;700&display=swap" rel="stylesheet">
<style>:root{{--bg:#fbf8f1;--ink:#2e2a22;--muted:#857a63;--accent:#7a5a2e;--rule:#e8dfcd}}
@media (prefers-color-scheme:dark){{:root{{--bg:#1d1b17;--ink:#ece6d8;--muted:#b3a68a;--accent:#d8b27a;--rule:#3a352c}}}}
body{{margin:0;background:var(--bg);color:var(--ink)}}{CSS.replace("#2e2a22", "var(--ink)").replace("#857a63", "var(--muted)")}
.wrap{{max-width:640px;margin:0 auto;padding:0 18px 80px}}.bar{{font-family:"Noto Sans KR",sans-serif;font-size:14px;padding:14px 0;display:flex;gap:12px;flex-wrap:wrap}}
.bar a,#toc a{{color:var(--accent)}}.cover{{text-align:center;margin:12px 0 30px}}.cover img{{width:320px;max-width:76vw;height:auto;border-radius:6px;box-shadow:0 14px 34px rgba(0,0,0,.35)}}
.dl{{display:inline-block;margin:18px 6px 0;padding:9px 18px;border-radius:999px;border:1px solid var(--accent);color:var(--accent);font-family:"Noto Sans KR",sans-serif;font-weight:700;font-size:14px;text-decoration:none}}
.intro{{font-size:15px;color:var(--muted)}}#toc{{font-family:"Noto Sans KR",sans-serif;border:1px solid var(--rule);border-radius:14px;padding:16px 22px;font-size:15px}}
#toc ul{{margin:.4em 0 0;padding:0;list-style:none;columns:2;line-height:1.9}}
.poem{{padding:34px 0;border-bottom:1px solid var(--rule)}}</style></head><body><div class="wrap">
<div class="bar"><a href="../../index.html">← 독서주특기 홈</a><a href="../index.html">안식월 시집</a></div>
<div class="cover"><img src="cover_s.jpg" srcset="cover_s.jpg 600w, cover.jpg 1400w" sizes="320px" alt="『{TITLE}』 표지" width="600" height="900"><br>
<a class="dl" href="{KEY}.epub" download>전자책(EPUB)</a><a class="dl" href="{KEY}.pdf" download>인쇄용 PDF</a></div>
{''.join(f'<p class="intro">{esc(t)}</p>' for t in INTRO)}
<nav id="toc" aria-label="차례"><b>차례</b><ul>{toc}</ul></nav>
{secs}
<p style="font-family:Noto Sans KR,sans-serif;font-size:13px;color:var(--muted);margin-top:40px">© {AUTHOR} · 새암교회(경기도 용인시 수지구 고기로 165). {esc(CREDIT)} 무단 전재를 삼가 주세요.</p>
</div></body></html>'''
open(os.path.join(OUT, 'index.html'), 'w', encoding='utf-8').write(page)
json.dump(dict(title=TITLE, sub=SUB, n=len(poems), intro=INTRO, parts=[['찬양시 16편', [x['title'] for x in poems]]],
               sample=[dict(title=x['title'], stanzas=x['stanzas'], notes=x['notes'], art=x['art']) for x in poems[:2]]),
          open(os.path.join(OUT, 'toc.json'), 'w', encoding='utf-8'), ensure_ascii=False)   # 블로그 소개 글(blogger.py)이 읽는 차례

def xhtml(title, body):
    return (f'<?xml version="1.0" encoding="utf-8"?>\n<!DOCTYPE html>\n<html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops" lang="ko" xml:lang="ko">'
            f'<head><meta charset="utf-8"/><title>{esc(title)}</title><link rel="stylesheet" type="text/css" href="style.css"/></head><body>{body}</body></html>')
files = {'cover.xhtml': xhtml(TITLE, f'<div style="text-align:center"><img src="cover.jpg" alt="{TITLE} 표지" style="max-width:100%;max-height:100%"/></div>'),
         'intro.xhtml': xhtml('이 시집에 대하여', '<h3>이 시집에 대하여</h3>' + ''.join(f'<p>{esc(t)}</p>' for t in INTRO))}
sub = []
for n, x in enumerate(poems, 1):
    files[f'p{n:02d}.xhtml'] = xhtml(x['title'], poem_html(x, True)); sub.append(f'<li><a href="p{n:02d}.xhtml">{esc(x["title"])}</a></li>')
files['colophon.xhtml'] = xhtml('판권', f'<p><b>{TITLE}</b> — {SUB}</p><p>지은이 {AUTHOR} (새암교회 목사)</p><p>새암교회 · 경기도 용인시 수지구 고기로 165</p>' + ''.join(f'<p>{esc(t)}</p>' for t in B['colophon']) + '<p>© 이재선. 무단 전재를 삼가 주세요.</p>')
nav = xhtml('차례', f'<nav epub:type="toc" id="toc"><h2>차례</h2><ol><li><a href="intro.xhtml">이 시집에 대하여</a></li>{"".join(sub)}</ol></nav>')
now = datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
imgs = ['cover.jpg'] + [x['art'] for x in poems]
opf = f'''<?xml version="1.0" encoding="utf-8"?>
<package xmlns="http://www.idpf.org/2007/opf" version="3.0" unique-identifier="bid" xml:lang="ko">
<metadata xmlns:dc="http://purl.org/dc/elements/1.1/"><dc:identifier id="bid">urn:uuid:5a1d0e6c-2023-4e00-9e1a-0000000000c1</dc:identifier><dc:title>{TITLE} — {SUB}</dc:title>
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

pdf = os.path.join(BK, B['pdfname'])
if os.path.exists(pdf): shutil.copy(pdf, os.path.join(OUT, KEY + '.pdf'))
print('시', len(poems), '편 · EPUB', os.path.getsize(ep), '· PDF', os.path.getsize(pdf) if os.path.exists(pdf) else '없음')
