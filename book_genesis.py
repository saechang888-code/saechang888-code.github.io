# 이재선 목사 창세기 강해집 2권 (posts.json 창세기 설교) → 책만들기\창세기\ (읽는 쪽 html · EPUB · 인쇄용 A5 PDF)
#   1권 『태초에 복이 있었다』 1–24장 · 2권 『돌베개가 변하여』 25–50장 — 주인님 지시(11-06): 장별로, 1장부터
#   설교가 아닌 글(주례사·축복문·피피티 본문·성경구절 모음)과 같은 설교가 두 번 올라간 것은 뺀다. 설교 본문 글은 고치지 않고,
#   옛 한글 파일에서 줄이 중간에 끊긴 것만 이어 붙인다. 그림: 표지는 cover.py, 부 그림은 귀스타브 도레 성경 판화(퍼블릭 도메인)
import os, re, json, html, zipfile, datetime, subprocess, collections, shutil
from PIL import Image
D = os.path.dirname(os.path.abspath(__file__))
BK = os.path.join(os.path.dirname(D), '책만들기')
OUT = os.path.join(BK, '창세기'); os.makedirs(OUT, exist_ok=True)
esc = lambda s: html.escape(s, quote=False)
AUTHOR = '이재선 목사'

DROP = {'(창2장)결혼주례사(채정호,신유선)', '(창1장)2004년5월23일 설교파워포인트본문', '(창6장)항상감사 성경구절', '결혼 축복문',
        '(창37장)동상이몽', '(창37장)자녀를 비전으로 키우라', '(창32장)씨름의 기도', '기도는 레슬링이다',
        '(창49장)레위는 어떻게 성전봉사자가 되었는가?', '(창31장)에덴-가나안-천국'}   # 뒤 넷은 같은 설교의 다른 판 — 긴 판을 남김
RENAME = {'(창9장)찬송가:410,404,411': '무지개 사랑', '(창31장)천국에서 아는 척 하지요': '에덴-가나안-천국', '(창3장)4.6.7': '4·6·7'}
VOLS = [dict(no=1, key='genesis1', title='태초에 복이 있었다', sub='창세기 강해 1 · 1–24장', cover='gen1.png', rng=(1, 24),
             parts=[('제1부', '태초에 — 창조와 타락과 홍수', (1, 11), 'creation'), ('제2부', '믿음의 조상 아브라함', (12, 24), 'abraham')]),
        dict(no=2, key='genesis2', title='돌베개가 변하여', sub='창세기 강해 2 · 25–50장', cover='gen2.png', rng=(25, 50),
             parts=[('제3부', '이삭과 야곱 — 씨름하여 이긴 사람', (25, 36), 'jacob'), ('제4부', '요셉과 열두 지파', (37, 50), 'joseph')])]
PLATE = {'creation': '「빛의 창조」', 'abraham': '「가나안 땅으로 가는 아브라함」', 'jacob': '「천사와 씨름하는 야곱」', 'joseph': '「형들에게 자기를 밝히는 요셉」', 'dove': '「방주에서 날려 보낸 비둘기」'}

ALL = json.load(open(os.path.join(D, 'posts.json'), encoding='utf-8'))
S = [p for p in ALL if p['kind'] == '설교' and '창세기' in p['category'] and p['title'] not in DROP]
WORDS = collections.Counter(w for p in ALL if p['kind'] == '설교' for w in re.findall(r'[가-힣]+', p['body']))

REF = re.compile(r'창\s?(\d+):\s?(\d+)(?:\s?[-~]\s?(\d+))?')
DATE = re.compile(r'(\d{4})\s*년\s*(\d{1,2})\s*월\s*(\d{1,2})\s*일')
VERSE = re.compile(r'^\(?[가-힣]{1,3}\s?\d+:\d+')
def is_head(t, title):
    return ('본문' in t or '예배' in t or '기도회' in t or t.startswith(('찬송', '찬양')) or (re.match(r'^창\s?\d+:\d', t) and len(t) < 40)
            or re.match(r'^(날자|날짜|장소)\s*:', t) or (re.match(r'^\d{4}\s*년', t) and len(t) < 40)
            or re.sub(r'\W', '', t).startswith(re.sub(r'\W', '', title)[:6]) or re.match(r'^\d{4}년 \d+월 \d+일 · ', t))

TAIL = set('라는 이라는 이라고 라고 니다 습니다 입니다 합니다 했습니다 었습니다 았습니다 였습니다 됩니다 습니까 니까 는데 지만 면서 도록 에서 에게 으로 부터 까지 처럼'.split())   # 줄 첫머리에 오면 앞 낱말에 붙는 꼬리
def join_wrapped(lines):
    """옛 한글 파일에서 한 문장이 여러 줄로 끊긴 것을 잇는다 (띄어쓰기는 설교 전체 낱말 빈도로 판단)"""
    out = []
    for l in lines:
        t = l.strip()
        prev = out[-1] if out else ''
        if (t and prev and len(prev) >= 25 and not re.search(r'[.?!。．"”’\'…:)\]」』]$', prev) and not VERSE.match(prev)
                and not re.match(r'^(\d+[.)]|[①-⑳]|[-*/]|\(?[가-힣]{1,3}\s?\d+:\d+)', t)):
            a = re.findall(r'[가-힣]+$', prev); b = re.findall(r'^[가-힣]+', t)
            glue = ' '
            if a and b and (b[0] in TAIL or (len(b[0]) == 1 and b[0] in '은는을를이가에의도다로와과' and WORDS.get(a[0] + b[0], 0) >= 1) or(WORDS.get(a[0] + b[0], 0) >= 1 and WORDS.get(a[0] + b[0], 0) >= WORDS.get(b[0], 0) * 0.2)): glue = ''
            out[-1] = prev + glue + t
        else:
            out.append(t)
    return out

def sermon(p):
    title = RENAME.get(p['title']) or re.sub(r'\s*본문\s*:.*$', '', re.sub(r'^\(창\d+장\)', '', p['title'])).strip()
    title = re.sub(r'\(창\d+장\)$', '', title).strip().strip('“”"\' ')
    L = [l for l in p['body'].replace('\t', '   ').split('\n')]
    head, i = [], 0
    while i < len(L) and len(head) < 4:
        t = L[i].strip()
        if not t: i += 1; continue
        if is_head(t, title) and len(t) < 160: head.append(t); i += 1
        else: break
    h = ' '.join(head)
    m = REF.search(h) or REF.search(p['body'][:400])
    ref = f'창세기 {m.group(1)}:{m.group(2)}' + (f'-{m.group(3)}' if m.group(3) else '') if m else ''
    dm = [x for x in DATE.finditer(h) if not re.search(r'\d{4}년 \d+월 \d+일 · ', h[x.start():x.end() + 3])]
    date = f'{dm[-1].group(1)}년 {int(dm[-1].group(2))}월 {int(dm[-1].group(3))}일' if dm else ''
    if not dm and (m2 := re.search(r'(19|20)(\d\d)\.\s*(\d{1,2})\.\s*(\d{1,2})', h)): date = f'{m2.group(1)}{m2.group(2)}년 {int(m2.group(3))}월 {int(m2.group(4))}일'
    sv = ([x for x in re.finditer(r'([가-힣]*교회)?\s*([가-힣0-9]*(?:예배|기도회))(\([^)]*\))?', h[len(title):] if h.startswith(title) else h)] or [None])[-1]
    service = (re.sub(r'\s+', '', (sv.group(1) or '') + (sv.group(2) or '')) + (sv.group(3) or '')) if sv else ''
    body = join_wrapped(L[i:])
    items = []
    for t in body:
        t = re.sub(r'[ 　]{2,}', ' ', t)
        if not t: continue
        if VERSE.match(t): items.append(('verse', t))
        elif re.match(r'^\d+\.\s*\S', t) and len(t) < 70: items.append(('h4', t))
        elif re.match(r'^(\d+\)|[①-⑳])\s*\S', t) and len(t) < 70: items.append(('h5', t))
        else: items.append(('p', t))
    ch = int(m.group(1)) if m else int(re.match(r'\(창(\d+)장\)', p['title']).group(1))
    v = int(m.group(2)) if m else 0
    v2 = int(m.group(3)) if m and m.group(3) else v
    return dict(title=title, ref=ref, date=date, service=service, items=items, ch=ch, v=v, v2=v2, n=sum(len(t) for _, t in items))

SER = sorted((sermon(p) for p in S), key=lambda s: (s['ch'], s['v'], s['date']))

KRV = json.load(open(os.path.join(os.path.dirname(D), 'berith-app', 'data', 'bible', 'krv', 'gen.json'), encoding='utf-8'))['chapters']
def passage(s):
    """제목 밑에 넣는 본문 말씀 — 개역한글(저작권 끝남, 주인님 11-06)"""
    if not s['ref'] or not s['v']: return ''
    vs = KRV[s['ch'] - 1][s['v'] - 1:s['v2']]
    return '<div class="pass">' + ''.join(f'<p><sup>{s["v"] + i}</sup>{esc(t)}</p>' for i, t in enumerate(vs)) + '</div>'

def body_html(s, x=False):
    meta = s['ref']   # 본문만 (설교한 날·예배 이름은 뺌 — 주인님 11-06)
    r = [f'<h3>{esc(s["title"])}</h3>', f'<p class="meta">본문 · {esc(meta)}</p>' if meta else '', passage(s)]
    for tag, t in s['items']:
        r.append(f'<p class="verse">{esc(t)}</p>' if tag == 'verse' else f'<{tag}>{esc(t)}</{tag}>' if tag in ('h4', 'h5') else f'<p>{esc(t)}</p>')
    return '\n'.join(r)

CSS = '''body{font-family:"Nanum Myeongjo","Noto Serif KR",serif;line-height:1.85;color:#26231e}
h1{font-size:1.9em;text-align:center}h2{font-size:1.45em;text-align:center;margin:0 0 .2em;color:#1f2b3a}h2 small{display:block;font-size:.55em;color:#8a7650;letter-spacing:.12em}
h3{font-size:1.25em;margin:0 0 .2em;color:#1f2b3a}.meta{font-family:"Noto Sans KR",sans-serif;font-size:.8em;color:#8a7650;margin:0 0 1.4em}
h4{font-size:1.05em;margin:1.6em 0 .5em;color:#2f4a3a}h5{font-size:1em;margin:1.2em 0 .4em}
p{margin:0 0 .9em;word-break:keep-all;overflow-wrap:anywhere;text-align:justify}.verse{color:#2f4a3a;padding-left:.9em;border-left:3px solid #c9d3c2;text-align:left}
.pass{background:#f4f1e8;border-radius:6px;padding:.8em 1em .3em;margin:0 0 1.6em;font-size:.92em;line-height:1.75}.pass p{margin:0 0 .5em;text-align:left}.pass sup{color:#8a7650;font-size:.7em;margin-right:.3em}
.plate{text-align:center}.plate img{max-width:100%;height:auto}.cap{font-size:.78em;color:#8a7650;text-align:center}'''

def jpg(src, dst, w):
    im = Image.open(src).convert('RGB'); im.thumbnail((w, w * 2)); im.save(dst, quality=84, optimize=True, progressive=True)

for V in VOLS:
    od = os.path.join(OUT, V['key']); os.makedirs(od, exist_ok=True)
    jpg(os.path.join(BK, '표지', V['cover']), os.path.join(od, 'cover.jpg'), 1600)
    for _, _, _, k in V['parts']: jpg(os.path.join(BK, '그림', 'dore', k + '.jpg'), os.path.join(od, k + '.jpg'), 1200)
    for c in range(V['rng'][0], V['rng'][1] + 1):                    # 장 그림 (캔바 AI 수채화, 11-06)
        f = os.path.join(BK, '그림', 'gen', f'{c}.jpg')
        if os.path.exists(f): jpg(f, os.path.join(od, f'ch{c}.jpg'), 1400)
    ss = [s for s in SER if V['rng'][0] <= s['ch'] <= V['rng'][1]]
    years = sorted(int(s['date'][:4]) for s in ss if s['date'])
    intro = [f'이 책은 이재선 목사가 {years[0]}년부터 {years[-1]}년까지 동산교회·새창교회·새암교회 강단에서 창세기 {V["rng"][0]}–{V["rng"][1]}장을 본문으로 전한 설교 {len(ss)}편을 성경의 장 차례대로 엮은 것입니다.',
             '설교마다 제목 밑에 본문 말씀을 개역한글판으로 실었습니다. 설교 원고는 고치지 않고 그대로 실었습니다.',
             '각 부의 그림은 귀스타브 도레(Gustave Doré, 1832–1883)의 성경 판화이고, 장마다 넣은 수채화는 캔바 AI로 그렸습니다.']
    # 부 → 장 → 설교
    tree = []
    for pno, pname, (a, b), pk in V['parts']:
        chs = [(c, [s for s in ss if s['ch'] == c]) for c in range(a, b + 1)]
        tree.append((pno, pname, pk, [(c, l) for c, l in chs if l]))
    # ---------- EPUB ----------
    def xhtml(t, body):
        return (f'<?xml version="1.0" encoding="utf-8"?>\n<!DOCTYPE html>\n<html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops" lang="ko" xml:lang="ko">'
                f'<head><meta charset="utf-8"/><title>{esc(t)}</title><link rel="stylesheet" type="text/css" href="style.css"/></head><body>{body}</body></html>')
    files = {'cover.xhtml': xhtml(V['title'], f'<div style="text-align:center"><img src="cover.jpg" alt="{V["title"]} 표지" style="max-width:100%;max-height:100%"/></div>'),
             'intro.xhtml': xhtml('이 책에 대하여', '<h3>이 책에 대하여</h3>' + ''.join(f'<p>{esc(t)}</p>' for t in intro))}
    navl = ['<li><a href="intro.xhtml">이 책에 대하여</a></li>']; k = 0
    for pno, pname, pk, chs in tree:
        files[f'part_{pk}.xhtml'] = xhtml(pname, f'<div class="plate"><img src="{pk}.jpg" alt="{PLATE[pk]}"/></div><p class="cap">귀스타브 도레, {PLATE[pk]}</p><h2><small>{pno}</small>{esc(pname)}</h2>')
        cl = []
        for c, l in chs:
            sl = []
            for s in l:
                k += 1; f = f's{k:03d}.xhtml'
                pre = f'<h2><small>창세기</small>{c}장</h2>' if s is l[0] else ''
                if s is l[0] and os.path.exists(os.path.join(od, f'ch{c}.jpg')): pre = f'<div class="plate"><img src="ch{c}.jpg" alt="창세기 {c}장 그림"/></div>' + pre
                files[f] = xhtml(s['title'], pre + body_html(s, True)); sl.append(f'<li><a href="{f}">{esc(s["title"])}</a></li>')
            cl.append(f'<li><a href="{sl[0].split(chr(34))[1]}">창세기 {c}장</a><ol>{"".join(sl)}</ol></li>')
        navl.append(f'<li><a href="part_{pk}.xhtml">{pno} {esc(pname)}</a><ol>{"".join(cl)}</ol></li>')
    nav = xhtml('차례', f'<nav epub:type="toc" id="toc"><h2>차례</h2><ol>{"".join(navl)}</ol></nav>')
    imgs = ['cover.jpg'] + [pk for _, _, pk, _ in tree] + [f'ch{c}' for _, _, _, chs in tree for c, _ in chs if os.path.exists(os.path.join(od, f'ch{c}.jpg'))]
    imgs = ['cover.jpg'] + [x + '.jpg' for x in imgs[1:]]
    now = datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
    opf = f'''<?xml version="1.0" encoding="utf-8"?>
<package xmlns="http://www.idpf.org/2007/opf" version="3.0" unique-identifier="bid" xml:lang="ko">
<metadata xmlns:dc="http://purl.org/dc/elements/1.1/"><dc:identifier id="bid">urn:uuid:5a1d0e6c-0001-4e00-9e1a-00000000006{V["no"]}</dc:identifier><dc:title>{V["title"]} — {V["sub"]}</dc:title>
<dc:creator>{AUTHOR}</dc:creator><dc:language>ko</dc:language><dc:publisher>새암교회</dc:publisher><meta property="dcterms:modified">{now}</meta></metadata>
<manifest><item id="css" href="style.css" media-type="text/css"/><item id="nav" href="nav.xhtml" media-type="application/xhtml+xml" properties="nav"/>
{''.join(f'<item id="i{i}" href="{f}" media-type="image/jpeg"' + (' properties="cover-image"' if i == 0 else '') + '/>' for i, f in enumerate(imgs))}
{''.join(f'<item id="x_{f[:-6]}" href="{f}" media-type="application/xhtml+xml"/>' for f in files)}</manifest>
<spine><itemref idref="x_cover"/><itemref idref="nav"/>{''.join(f'<itemref idref="x_{f[:-6]}"/>' for f in files if f != 'cover.xhtml')}</spine></package>'''
    ep = os.path.join(od, V['key'] + '.epub')
    with zipfile.ZipFile(ep, 'w') as z:
        z.writestr(zipfile.ZipInfo('mimetype'), 'application/epub+zip', compress_type=zipfile.ZIP_STORED)
        z.writestr('META-INF/container.xml', '<?xml version="1.0"?><container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container"><rootfiles><rootfile full-path="OEBPS/content.opf" media-type="application/oebps-package+xml"/></rootfiles></container>', zipfile.ZIP_DEFLATED)
        for name, s in [('content.opf', opf), ('style.css', CSS), ('nav.xhtml', nav)] + list(files.items()): z.writestr('OEBPS/' + name, s, zipfile.ZIP_DEFLATED)
        for f in imgs: z.write(os.path.join(od, f), 'OEBPS/' + f)
    # ---------- 인쇄용 PDF (A5) ----------
    pg = [f'<div class="pg cv"><img src="{od}/cover.jpg"></div>',
          f'<div class="pg tp"><h1>{V["title"]}</h1><p class="s2">{V["sub"]}</p><p class="au">{AUTHOR} 지음</p><p class="pub">새암교회</p></div>',
          '<div class="pg"><h3>이 책에 대하여</h3>' + ''.join(f'<p>{esc(t)}</p>' for t in intro) + '</div>']
    toc = []
    for pno, pname, pk, chs in tree:
        toc.append(f'<p class="tp1">{pno} {esc(pname)}</p>' + ''.join(f'<p class="tc">창세기 {c}장</p>' + ''.join(f'<p class="ts">{esc(s["title"])}</p>' for s in l) for c, l in chs))
        pg.append(f'<div class="pg pt"><img src="{od}/{pk}.jpg"><p class="cap">귀스타브 도레, {PLATE[pk]}</p><h2><small>{pno}</small>{esc(pname)}</h2></div>')
        for c, l in chs:
            art = f'<img class="ci" src="{od}/ch{c}.jpg">' if os.path.exists(os.path.join(od, f'ch{c}.jpg')) else ''
            pg.append(f'<div class="pg chp">{art}<h2><small>창세기</small>{c}장</h2>' + ''.join(f'<p class="ts">{esc(s["title"])}</p>' for s in l) + '</div>')
            for s in l: pg.append(f'<div class="pg">{body_html(s)}</div>')
    pg.insert(3, f'<div class="pg toc"><h3>차례</h3>{"".join(toc)}</div>')
    doc = f'''<!doctype html><html lang="ko"><head><meta charset="utf-8">
<link href="https://fonts.googleapis.com/css2?family=Nanum+Myeongjo:wght@400;700;800&family=Noto+Sans+KR:wght@400;700&display=swap" rel="stylesheet">
<style>@page{{size:148mm 210mm;margin:20mm 17mm 18mm;@bottom-center{{content:counter(page);font-size:8pt;color:#8a7650}}}}@page full{{margin:0;@bottom-center{{content:none}}}}html,body{{margin:0}}{CSS}
body{{font-size:9.8pt}}.pg{{break-after:page}}.cv{{page:full}}.cv img{{width:148mm;height:210mm;object-fit:cover;display:block}}
.tp{{text-align:center;padding-top:40mm}}.tp h1{{font-size:24pt;font-weight:800;margin:0}}.tp .s2{{color:#8a7650;text-align:center}}.tp .au{{margin-top:50mm;font-weight:700;text-align:center}}.tp .pub{{text-align:center}}
.pt{{text-align:center;padding-top:6mm}}.pt img{{max-width:100%;max-height:135mm}}.chp{{padding-top:4mm;text-align:center}}.chp .ci{{width:100%;border-radius:2mm;margin-bottom:8mm}}.chp .ts{{text-align:center;margin:.2em 0}}
.toc{{font-size:8.6pt;columns:2;column-gap:8mm}}.toc h3{{column-span:all}}.toc p{{margin:0;line-height:1.6;text-align:left}}.tp1{{font-weight:800;margin-top:3mm!important;break-after:avoid}}.tc{{font-weight:700;margin-top:1.5mm!important;break-after:avoid}}.toc .ts{{padding-left:3mm}}
h4,h5{{break-after:avoid}}</style></head><body>{"".join(pg)}</body></html>'''
    hp = os.path.join(od, '_print.html'); open(hp, 'w', encoding='utf-8').write(doc)
    pdf = os.path.join(OUT, f'창세기강해{V["no"]}_{V["title"].replace(" ", "")}.pdf')
    subprocess.run([r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe', '--headless=new', '--disable-gpu', '--virtual-time-budget=15000',
                    '--no-pdf-header-footer', f'--print-to-pdf={pdf}', 'file:///' + hp.replace('\\', '/')], capture_output=True, timeout=600)
    print(V['no'], '권', len(ss), '편', sum(s['n'] for s in ss), '자 ·', len([c for t in tree for c in t[3]]), '개 장 · EPUB', os.path.getsize(ep),
          '· PDF', os.path.getsize(pdf) if os.path.exists(pdf) else '없음')
    # ---------- 홈페이지에서 읽는 쪽: books/genesis{권}/ (주인님 11-06: 홈페이지와 블로그에 올려줘) ----------
    web = os.path.join(D, 'books', V['key']); os.makedirs(web, exist_ok=True)
    for f in imgs: shutil.copy(os.path.join(od, f), os.path.join(web, f))
    jpg(os.path.join(od, 'cover.jpg'), os.path.join(web, 'cover_s.jpg'), 600)
    shutil.copy(ep, os.path.join(web, V['key'] + '.epub'))
    if os.path.exists(pdf): shutil.copy(pdf, os.path.join(web, V['key'] + '.pdf'))
    toc, secs, k = [], [], 0
    for pno, pname, pk, chs in tree:
        toc.append(f'<li class="p"><a href="#part-{pk}">{pno} {esc(pname)}</a></li>')
        secs.append(f'<section id="part-{pk}" class="part"><img src="{pk}.jpg" alt="{PLATE[pk]}" loading="lazy"><p class="cap">귀스타브 도레, {PLATE[pk]}</p><h2><small>{pno}</small>{esc(pname)}</h2></section>')
        for c, l in chs:
            toc.append(f'<li class="c"><a href="#ch{c}">창세기 {c}장</a></li>')
            art = f'<img src="ch{c}.jpg" alt="창세기 {c}장 그림" loading="lazy">' if os.path.exists(os.path.join(web, f'ch{c}.jpg')) else ''
            secs.append(f'<section id="ch{c}" class="chap">{art}<h2><small>창세기</small>{c}장</h2></section>')
            for s in l:
                k += 1; toc.append(f'<li><a href="#s{k}">{esc(s["title"])}</a></li>')
                secs.append(f'<article id="s{k}" class="serm">{body_html(s)}<p class="top"><a href="#toc">↑ 차례로</a></p></article>')
    page = f'''<!doctype html><html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{V["title"]} — {V["sub"]} · {AUTHOR}</title>
<meta name="description" content="이재선 목사(새암교회)의 창세기 강해 설교집 『{V["title"]}』 — 창세기 {V["rng"][0]}–{V["rng"][1]}장 설교 {len(ss)}편을 장 차례대로 엮었습니다. 홈페이지에서 읽거나 EPUB·PDF로 내려받을 수 있습니다.">
<link rel="canonical" href="https://saechang888-code.github.io/books/{V["key"]}/">
<link href="https://fonts.googleapis.com/css2?family=Nanum+Myeongjo:wght@400;700&family=Noto+Sans+KR:wght@400;700&display=swap" rel="stylesheet">
<style>:root{{--bg:#fbf8f2;--ink:#26231e;--muted:#8a7650;--accent:#1f4a3a;--rule:#e6dccb;--pass:#f4f1e8}}
@media (prefers-color-scheme:dark){{:root{{--bg:#1b1a17;--ink:#ece6da;--muted:#b9a98a;--accent:#9cc7ae;--rule:#3a352d;--pass:#26241f}}}}
body{{margin:0;background:var(--bg);color:var(--ink)}}{CSS.replace("#26231e", "var(--ink)").replace("#8a7650", "var(--muted)").replace("#f4f1e8", "var(--pass)").replace("#1f2b3a", "var(--accent)").replace("#2f4a3a", "var(--accent)")}
.wrap{{max-width:720px;margin:0 auto;padding:0 18px 80px}}.bar{{font-family:"Noto Sans KR",sans-serif;font-size:14px;padding:14px 0;display:flex;gap:12px;flex-wrap:wrap}}
.bar a,#toc a,.top a{{color:var(--accent)}}.cover{{text-align:center;margin:12px 0 26px}}.cover img{{width:320px;max-width:76vw;height:auto;border-radius:6px;box-shadow:0 14px 34px rgba(0,0,0,.35)}}
.dl{{display:inline-block;margin:18px 6px 0;padding:9px 18px;border-radius:999px;border:1px solid var(--accent);color:var(--accent);font-family:"Noto Sans KR",sans-serif;font-weight:700;font-size:14px;text-decoration:none}}
.intro{{font-size:15px;color:var(--muted);text-align:left}}#toc{{font-family:"Noto Sans KR",sans-serif;border:1px solid var(--rule);border-radius:14px;padding:16px 22px;font-size:15px}}
#toc ul{{margin:.4em 0 0;padding:0;list-style:none;line-height:1.9}}#toc li.p{{font-weight:700;margin-top:.8em}}#toc li.c{{font-weight:700;margin-top:.4em;color:var(--muted)}}#toc li:not(.p):not(.c){{padding-left:1em}}
.part,.chap{{text-align:center;margin:56px 0 10px}}.part img,.chap img{{width:100%;height:auto;border-radius:6px}}.serm{{padding:34px 0;border-bottom:1px solid var(--rule)}}
.top{{font-family:"Noto Sans KR",sans-serif;font-size:14px;text-align:right}}</style></head><body><div class="wrap">
<div class="bar"><a href="../../index.html">← 독서주특기 홈</a><a href="../../writings/index.html?k=설교">설교 모음</a></div>
<div class="cover"><img src="cover_s.jpg" srcset="cover_s.jpg 600w, cover.jpg 1600w" sizes="320px" alt="『{V["title"]}』 표지" width="600" height="900"><br>
<a class="dl" href="{V["key"]}.epub" download>전자책(EPUB)</a><a class="dl" href="{V["key"]}.pdf" download>인쇄용 PDF</a></div>
{"".join(f'<p class="intro">{esc(t)}</p>' for t in intro)}
<nav id="toc" aria-label="차례"><b>차례</b><ul>{"".join(toc)}</ul></nav>
{"".join(secs)}
<p style="font-family:Noto Sans KR,sans-serif;font-size:13px;color:var(--muted);margin-top:40px">© {AUTHOR} · 새암교회(경기도 용인시 수지구 고기로 165). 본문 말씀: 개역한글판. 장 그림: 캔바 AI. 부 그림: 귀스타브 도레(퍼블릭 도메인). 무단 전재를 삼가 주세요.</p>
</div></body></html>'''
    open(os.path.join(web, 'index.html'), 'w', encoding='utf-8').write(page)
    json.dump(dict(title=V['title'], sub=V['sub'], n=len(ss), intro=intro, parts=[[f'{pno} {pname}', [[c, [s['title'] for s in l]] for c, l in chs]] for pno, pname, pk, chs in tree]),
              open(os.path.join(web, 'toc.json'), 'w', encoding='utf-8'), ensure_ascii=False)   # 블로그 소개 글(blogger.py)이 읽는 차례
    print('  홈페이지', web, sum(os.path.getsize(os.path.join(web, f)) for f in os.listdir(web)) // 1024, 'KB')
