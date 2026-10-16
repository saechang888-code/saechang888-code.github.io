# 검색엔진(구글·네이버·다음)이 홈페이지 글을 잘 찾도록: sitemap.xml · robots.txt · 글마다 설명/공유 카드(og) 태그
import os, re, json, html, glob, datetime

D = os.path.dirname(os.path.abspath(__file__))
SITE = 'https://saechang888-code.github.io/'
IMG = SITE + 'assets/hero.jpg'
TODAY = (datetime.datetime.utcnow() + datetime.timedelta(hours=9)).strftime('%Y-%m-%d')

def esc(s): return html.escape(s, quote=True)
def text_of(h):
    t = re.sub(r'<(script|style)\b.*?</\1>', ' ', h, flags=re.S)
    t = re.sub(r'<[^>]+>', ' ', t)
    return re.sub(r'\s+', ' ', html.unescape(t)).strip()

def tag_page(path, url):
    h = open(path, encoding='utf-8').read()
    if 'property="og:title"' in h: return
    m = re.search(r'<title>(.*?)</title>', h, re.S)
    title = html.unescape(m.group(1)).strip() if m else '독서주특기'
    body = re.search(r'<article\b.*?</article>', h, re.S) or re.search(r'<body\b.*', h, re.S)
    desc = text_of(body.group(0) if body else h)[:150]
    meta = (f'<meta name="description" content="{esc(desc)}">\n'
            f'<link rel="canonical" href="{url}">\n'
            f'<meta property="og:type" content="article">\n<meta property="og:site_name" content="독서주특기 · 이재선 목사">\n'
            f'<meta property="og:title" content="{esc(title)}">\n<meta property="og:description" content="{esc(desc)}">\n'
            f'<meta property="og:url" content="{url}">\n<meta property="og:image" content="{IMG}">\n'
            f'<meta name="twitter:card" content="summary_large_image">\n')
    h = h.replace('</title>', '</title>\n' + meta, 1)
    open(path, 'w', encoding='utf-8').write(h)

urls = [(SITE, '1.0'), (SITE + 'writings/index.html', '0.9'), (SITE + 'yehwa/index.html', '0.9'), (SITE + 'event.html', '0.6')]
for sub, pr in (('writings', '0.6'), ('yehwa', '0.7')):
    for f in sorted(glob.glob(os.path.join(D, sub, '*.html'))):
        name = os.path.basename(f)
        u = SITE + sub + '/' + name
        tag_page(f, u)
        if name != 'index.html': urls.append((u, pr))

# 첫 화면에도 공유 카드
home = os.path.join(D, 'index.html'); h = open(home, encoding='utf-8').read()
if 'property="og:title"' not in h:
    h = h.replace('</title>', '</title>\n' + (
        f'<link rel="canonical" href="{SITE}">\n<meta property="og:type" content="website">\n'
        f'<meta property="og:title" content="독서주특기 · 이재선 목사 (새암교회)">\n'
        f'<meta property="og:description" content="강단에서 전한 설교 1,300여 편, 주제별 예화 3,400여 편, 독후감과 시를 날마다 나눕니다.">\n'
        f'<meta property="og:url" content="{SITE}">\n<meta property="og:image" content="{IMG}">\n<meta name="twitter:card" content="summary_large_image">\n'), 1)
    open(home, 'w', encoding='utf-8').write(h)

# 검색엔진 소유 확인 (구글 Search Console · 네이버 서치어드바이저)
VERIFY = ['<meta name="google-site-verification" content="pZkvLgD2zZY8ZxzdHr93jqpC5_ImVbDoKMZ_WWMtQeo" />',
          '<meta name="naver-site-verification" content="cc75e69313c195c9ae47156d59ec8d97ed48a035" />']
h = open(home, encoding='utf-8').read()
add = [v for v in VERIFY if v not in h]
if add:
    h = h.replace('</title>', '</title>\n' + '\n'.join(add), 1)
    open(home, 'w', encoding='utf-8').write(h)

sm =['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
for u, pr in urls:
    sm.append(f'<url><loc>{esc(u)}</loc><lastmod>{TODAY}</lastmod><priority>{pr}</priority></url>')
sm.append('</urlset>')
open(os.path.join(D, 'sitemap.xml'), 'w', encoding='utf-8').write('\n'.join(sm) + '\n')
open(os.path.join(D, 'robots.txt'), 'w', encoding='utf-8').write(f'User-agent: *\nAllow: /\nSitemap: {SITE}sitemap.xml\n')
print('sitemap urls', len(urls))
