# 이재선 목사 『Exodus 엑서더스 — 새암교회 이야기』(2020 출애굽판 원고 ebook_exodus.txt) → e북
#   saeam/exodus/index.html (홈페이지에서 읽는 쪽) + saeam/exodus/exodus.epub (내려받는 전자책)
# 원고를 바꾸면 이 파일을 다시 돌려 두 결과물을 함께 올린다 (배포 때 자동으로 돌지 않음)
import os, re, html, zipfile, datetime
D = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(D, 'saeam', 'exodus')
L = [l.strip() for l in open(os.path.join(D, 'ebook_exodus.txt'), encoding='utf-8').read().split('\n')]
def line(n): return L[n - 1]
def esc(s): return html.escape(s, quote=False)

TITLE, SUB, AUTHOR = 'Exodus 엑서더스', '새암교회 이야기 — 무기력한 신앙생활을 탈출해 전도하는 교회로', '이재선 목사'
CH = {253: ('', '출정식'), 314: ('제1장', '엑서더스의 비법'), 426: ('제2장', '애굽의 삶'), 744: ('제3장', '광야의 삶'),
      1058: ('제1숙영지', '새 가족들의 증언 — 예수님 만나는 공동체'), 1370: ('제2숙영지', '제자들의 증언 — 영혼 구원하는 공동체'),
      1674: ('제3숙영지', '사명자들의 증언 — 제자 삼는 공동체'), 2110: ('', '가나안에 도착하다')}
SKIP = {424, 742, 1060, 1372, 1676}           # '제 2 장' 같은 표지 줄, 장 제목에 넣은 부제
H3 = {269, 287, 300, 306, 310, 332, 338, 348, 354, 370, 380, 748, 750, 762, 772, 778, 790, 794, 798, 804, 808, 816,
      1062, 1064, 1070, 1076, 1082, 1230, 1312, 1374, 1390, 1394, 1462, 1592, 1640, 1678, 1754, 1772, 2028, 2086, 2208, 2250}
POEM = {390: 422, 1184: 1228, 1550: 1590, 1994: 2026, 2174: 2206}   # 시 제목 줄: 시가 끝나는 줄
H4 = [(1106, 1178), (1464, 1542), (1848, 1896), (1910, 1984)]
VERSE = re.compile(r'^\((?:[가-힣]{1,4}|[가-힣]+ ?\d?서?) ?\d+:\d+')

def block(a, b):
    """원고 a..b 줄 → [(태그, 글)]"""
    out, n = [], a
    while n <= b:
        t = line(n)
        if not t or n in SKIP: n += 1; continue
        if n in POEM:
            out.append(('h3', t)); body = [line(k) for k in range(n + 1, POEM[n] + 1) if line(k)]
            if body and body[0] == t: body = body[1:]
            out.append(('poem', body)); n = POEM[n] + 1; continue
        if n in H3: out.append(('h3', t))
        elif re.match(r'^-.+-$', t): out.append(('attr', t.strip('-').strip()))
        elif t.startswith('-') and any(x <= n <= y for x, y in H4): out.append(('h4', t.lstrip('-').strip()))
        elif VERSE.match(t): out.append(('verse', t))
        else: out.append(('p', t))
        n += 1
    return out

toc_at = next(i for i, t in enumerate(L, 1) if re.sub(r'\s', '', t) == '목차')
front = [('h3', '지은이 약력')] + [('p', line(n)) for n in range(13, 16) if line(n)] + \
        [('h3', '프롤로그 — 이 책을 쓰는 목적')] + [x for x in block(19, toc_at - 1)]
starts = sorted(CH)
chapters = [('', '지은이 약력과 프롤로그', front)] + \
           [(CH[s][0], CH[s][1], block(s + 1, (starts[i + 1] - 1) if i + 1 < len(starts) else len(L))) for i, s in enumerate(starts)]

def render(items, x=False):
    br = '<br/>' if x else '<br>'
    r = []
    for tag, t in items:
        if tag == 'poem': r.append('<div class="poem">' + br.join(esc(l) for l in t) + '</div>')
        elif tag == 'attr': r.append(f'<p class="attr">— {esc(t)}</p>')
        elif tag == 'verse': r.append(f'<p class="verse">{esc(t)}</p>')
        elif tag in ('h3', 'h4'): r.append(f'<{tag}>{esc(t)}</{tag}>')
        else: r.append(f'<p>{esc(t)}</p>')
    return '\n'.join(r)

CSS = '''body{font-family:"Noto Serif KR","Nanum Myeongjo",serif;line-height:1.9;color:#26231e}
h2{font-size:1.5em;line-height:1.4;margin:0 0 .2em}h2 small{display:block;font-size:.55em;color:#7a6a4f;letter-spacing:.08em;margin-bottom:.3em}
h3{font-size:1.15em;margin:2em 0 .6em;color:#3d5a3a}h4{font-size:1.02em;margin:1.6em 0 .4em}
p{margin:0 0 1em;word-break:keep-all;overflow-wrap:anywhere}.verse{color:#3d5a3a;padding-left:1em;border-left:3px solid #c9d8c2}
.attr{text-align:right;color:#7a6a4f;font-size:.92em}.poem{margin:1em 0 1.6em;padding:1em 1.2em;background:#f6f1e7;border-radius:8px;line-height:2}'''

# ---------- 홈페이지에서 읽는 쪽 ----------
os.makedirs(OUT, exist_ok=True)
toc = ''.join(f'<li><a href="#c{i}">{(esc(a) + " · ") if a else ""}{esc(b)}</a></li>' for i, (a, b, _) in enumerate(chapters))
secs = ''.join(f'<section id="c{i}" class="ch"><h2>{f"<small>{esc(a)}</small>" if a else ""}{esc(b)}</h2>{render(it)}<p class="top"><a href="#toc">↑ 차례로</a></p></section>'
               for i, (a, b, it) in enumerate(chapters))
nchar = sum(len(t if isinstance(t, str) else ''.join(t)) for _, _, it in chapters for _, t in it)
page = f'''<!doctype html><html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{TITLE} — 새암교회 이야기 · {AUTHOR}</title>
<meta name="description" content="이재선 목사(새암교회)가 쓴 『{TITLE}』 — 40년 된 교회가 무기력한 신앙생활을 벗고 영혼 구원하는 교회로 다시 태어난 이야기와 성도들의 간증. 홈페이지에서 읽거나 EPUB으로 내려받을 수 있습니다.">
<link rel="canonical" href="https://saechang888-code.github.io/saeam/exodus/">
<link href="https://fonts.googleapis.com/css2?family=Noto+Serif+KR:wght@400;700&family=Noto+Sans+KR:wght@400;700&display=swap" rel="stylesheet">
<style>:root{{--bg:#fbf8f2;--ink:#26231e;--muted:#7a6a4f;--green:#3d5a3a;--rule:#e6dccb}}
@media (prefers-color-scheme:dark){{:root{{--bg:#1c1a17;--ink:#ece6da;--muted:#b8a98c;--green:#9cc293;--rule:#3a352d}}}}
body{{margin:0;background:var(--bg);color:var(--ink)}}{CSS.replace("#26231e", "var(--ink)").replace("#3d5a3a", "var(--green)").replace("#7a6a4f", "var(--muted)")}
@media (prefers-color-scheme:dark){{.poem{{background:#2a2620}}.verse{{border-color:#4a5e45}}}}
.wrap{{max-width:720px;margin:0 auto;padding:0 18px 80px}}.bar{{font-family:"Noto Sans KR",sans-serif;font-size:14px;padding:14px 0;display:flex;gap:12px;flex-wrap:wrap}}
.bar a,.top a,#toc a{{color:var(--green)}}.cover{{margin:18px 0 28px;padding:44px 28px;border-radius:18px;background:linear-gradient(160deg,#3d5a3a,#20311f);color:#f4efe4;text-align:center}}
.cover .tag{{font-family:"Noto Sans KR",sans-serif;font-size:14px;letter-spacing:.12em;opacity:.85}}.cover h1{{font-size:44px;margin:.25em 0 .1em;letter-spacing:.02em}}
.cover .sub{{font-size:17px;opacity:.92}}.cover .au{{margin-top:1.4em;font-weight:700}}.dl{{display:inline-block;margin-top:1.4em;padding:10px 20px;border-radius:999px;background:#f4efe4;color:#20311f;font-family:"Noto Sans KR",sans-serif;font-weight:700;text-decoration:none}}
#toc{{font-family:"Noto Sans KR",sans-serif;border:1px solid var(--rule);border-radius:14px;padding:18px 22px}}#toc ul{{margin:.4em 0 0;padding:0;list-style:none;line-height:2}}
.ch{{padding-top:40px;border-top:1px solid var(--rule);margin-top:40px}}.top{{font-family:"Noto Sans KR",sans-serif;font-size:14px;text-align:right}}
@media (max-width:520px){{.cover h1{{font-size:34px}}}}</style></head><body><div class="wrap">
<div class="bar"><a href="../../index.html">← 독서주특기 홈</a><a href="../">새암교회 안내</a></div>
<div class="cover"><div class="tag">신앙생활에 활력을</div><h1>{TITLE}</h1><div class="sub">{esc(SUB)}</div><div class="au">{AUTHOR} 지음 · 새암교회</div>
<a class="dl" href="exodus.epub" download>전자책(EPUB) 내려받기</a></div>
<nav id="toc" aria-label="차례"><b>차례</b><ul>{toc}</ul></nav>
{secs}
<p style="font-family:Noto Sans KR,sans-serif;font-size:13px;color:var(--muted);margin-top:40px">© {AUTHOR} · 새암교회(경기도 용인시 수지구 고기로 165). 원고 2020년판. 무단 전재를 삼가 주세요.</p>
</div></body></html>'''
open(os.path.join(OUT, 'index.html'), 'w', encoding='utf-8').write(page)

# ---------- EPUB 3 ----------
def xhtml(title, body):
    return (f'<?xml version="1.0" encoding="utf-8"?>\n<!DOCTYPE html>\n<html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops" lang="ko" xml:lang="ko">'
            f'<head><meta charset="utf-8"/><title>{esc(title)}</title><link rel="stylesheet" type="text/css" href="style.css"/></head><body>{body}</body></html>')
uid = 'urn:uuid:5a1d0e6c-2020-4e00-9e1a-000000000001'
files = {'cover.xhtml': xhtml(TITLE, '<div style="text-align:center;margin-top:30%"><p style="text-align:center;color:#7a6a4f">신앙생활에 활력을</p>' +
                              f'<h1 style="font-size:2.2em">{TITLE}</h1><p style="text-align:center">{esc(SUB)}</p><p style="text-align:center;margin-top:3em"><b>{AUTHOR}</b><br/>새암교회</p></div>')}
for i, (a, b, it) in enumerate(chapters):
    files[f'c{i:02d}.xhtml'] = xhtml(b, f'<h2>{f"<small>{esc(a)}</small>" if a else ""}{esc(b)}</h2>' + render(it, True))
nav = xhtml('차례', '<nav epub:type="toc" id="toc"><h2>차례</h2><ol>' + ''.join(
    f'<li><a href="c{i:02d}.xhtml">{(esc(a) + " · ") if a else ""}{esc(b)}</a></li>' for i, (a, b, _) in enumerate(chapters)) + '</ol></nav>')
now = datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
spine = ['cover.xhtml', 'nav.xhtml'] + [f'c{i:02d}.xhtml' for i in range(len(chapters))]
opf = f'''<?xml version="1.0" encoding="utf-8"?>
<package xmlns="http://www.idpf.org/2007/opf" version="3.0" unique-identifier="bid" xml:lang="ko">
<metadata xmlns:dc="http://purl.org/dc/elements/1.1/"><dc:identifier id="bid">{uid}</dc:identifier><dc:title>{TITLE} — 새암교회 이야기</dc:title>
<dc:creator>{AUTHOR}</dc:creator><dc:language>ko</dc:language><dc:publisher>새암교회</dc:publisher><meta property="dcterms:modified">{now}</meta></metadata>
<manifest><item id="css" href="style.css" media-type="text/css"/><item id="nav" href="nav.xhtml" media-type="application/xhtml+xml" properties="nav"/>
{''.join(f'<item id="{f[:-6]}" href="{f}" media-type="application/xhtml+xml"/>' for f in files)}</manifest>
<spine>{''.join(f'<itemref idref="{"nav" if f == "nav.xhtml" else f[:-6]}"/>' for f in spine)}</spine></package>'''
ep = os.path.join(OUT, 'exodus.epub')
with zipfile.ZipFile(ep, 'w') as z:
    z.writestr(zipfile.ZipInfo('mimetype'), 'application/epub+zip', compress_type=zipfile.ZIP_STORED)
    z.writestr('META-INF/container.xml', '<?xml version="1.0"?><container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container"><rootfiles><rootfile full-path="OEBPS/content.opf" media-type="application/oebps-package+xml"/></rootfiles></container>', zipfile.ZIP_DEFLATED)
    z.writestr('OEBPS/content.opf', opf, zipfile.ZIP_DEFLATED)
    z.writestr('OEBPS/style.css', CSS, zipfile.ZIP_DEFLATED)
    z.writestr('OEBPS/nav.xhtml', nav, zipfile.ZIP_DEFLATED)
    for f, s in files.items(): z.writestr('OEBPS/' + f, s, zipfile.ZIP_DEFLATED)
print('e북', len(chapters), '장', nchar, '자 · EPUB', os.path.getsize(ep), '바이트')
