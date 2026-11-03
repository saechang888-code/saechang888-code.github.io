#!/usr/bin/env python3
"""Assemble the generated library content into one editorial homepage."""
from html import escape
from pathlib import Path
import re

PATH = Path("index.html")
source = PATH.read_text(encoding="utf-8")

def tag_attrs(text):
    return {m.group(1).lower(): m.group(3) for m in re.finditer(r"([\w:-]+)\s*=\s*([\"'])(.*?)\2", text, re.S)}

def extract_element(markup, tag, attr=None, value=None, required=True):
    opener = re.compile(r"<" + re.escape(tag) + r"\b[^>]*>", re.I | re.S)
    token_re = re.compile(r"</?" + re.escape(tag) + r"\b[^>]*>", re.I | re.S)
    for match in opener.finditer(markup):
        attrs = tag_attrs(match.group(0))
        actual = attrs.get(attr.lower()) if attr else None
        if attr == "class":
            matches = value in (actual or "").split()
        else:
            matches = actual == value if attr else True
        if not matches:
            continue
        depth = 0
        for token in token_re.finditer(markup, match.start()):
            text = token.group(0)
            if text.startswith("</"):
                depth -= 1
            elif not text.rstrip().endswith("/>"):
                depth += 1
            if depth == 0:
                return markup[match.start():token.end()]
    if required:
        raise ValueError(f"Required <{tag}> element not found: {attr}={value}")
    return ""

def extract_section(markup, section_id):
    return extract_element(markup, "section", "id", section_id)

head = extract_element(source, "head")
topbar = extract_element(source, "header", "class", "topbar")
hero_main = extract_element(source, "div", "class", "hero-main")
today = extract_element(source, "a", "class", "today")
stats = extract_element(source, "ul", "class", "stats")
event = extract_element(source, "aside", "class", "evbanner", required=False)
church_banner = extract_element(source, "a", "class", "church-banner", required=False)
footer = extract_element(source, "footer")
sections = {name: extract_section(source, name) for name in ("fresh", "stories", "sermon", "youtube", "poems", "pensees", "reading", "works", "church")}

# Replace the previous visual layer with the new complete page treatment.
head = re.sub(r"<link\b(?=[^>]*\brel=[\"']stylesheet[\"'])(?=[^>]*\bhref=[\"']assets/home-premium\.css[^\"']*[\"'])[^>]*>\s*", "", head, flags=re.I)
head = re.sub(r"<link\b(?=[^>]*\bhref=[\"']assets/library-luxe\.css[^\"']*[\"'])[^>]*>\s*", "", head, flags=re.I)
head = head.replace("</head>", '<link rel="stylesheet" href="assets/library-luxe.css?v=search-round-09">\n</head>', 1)
html_tag = re.search(r"<html\b[^>]*>", source, re.I)
if not html_tag:
    raise ValueError("The generated page has no html root.")
doctype = re.search(r"<!doctype[^>]*>", source, re.I)
lang = tag_attrs(html_tag.group(0)).get("lang", "ko")

# Keep scripts added by data builders, but don't duplicate the search script
# already preserved inside the new hero copy.
head_start = source.find(head.split("\n", 1)[0]) if head else -1
hero_start = source.find(hero_main)
hero_end = hero_start + len(hero_main) if hero_start >= 0 else -1
extra_scripts = []
for match in re.finditer(r"<script\b[^>]*>[\s\S]*?</script>", source, re.I):
    if hero_start >= 0 and hero_start <= match.start() < hero_end:
        continue
    if "application/ld+json" in match.group(0).lower():
        continue
    if match.start() >= source.find("</head>"):
        extra_scripts.append(match.group(0))

quicknav = '''<nav class="collection-nav" aria-label="서재 바로가기">
  <a href="#fresh"><span>01</span><b>새로 쓴 이야기</b></a>
  <a href="#stories"><span>02</span><b>주제별 예화</b></a>
  <a href="#sermon"><span>03</span><b>설교와 성경연구</b></a>
  <a href="#poems"><span>04</span><b>시와 생각</b></a>
  <a href="#reading"><span>05</span><b>읽은 책</b></a>
</nav>'''

body = f'''<body class="reading-room">
<a class="skip-link" href="#main">본문 바로가기</a>
{event}
{topbar}
<header class="library-hero" id="about">
  <div class="hero-copy"><div class="hero-copy-inner">{hero_main}</div></div>
  <aside class="hero-art" aria-label="오늘의 이야기">
    <div class="hero-art-top"><span>THE READING ROOM</span><span>이재선 목사의 서재</span></div>
    <div class="hero-art-story"><span class="hero-art-label">오늘의 이야기</span>{today}</div>
    <div class="hero-art-bottom"><span>말씀 · 이야기 · 기록</span><span class="art-rule"></span></div>
  </aside>
  <div class="hero-metrics"><div class="container">{stats}</div></div>
</header>
<main class="container library-main" id="main">
  <div class="library-intro">
    <div><span class="section-kicker">THE COLLECTION</span><h2>오래 읽고, 깊이 남기는<br>한 사람의 서재</h2></div>
    <p>강단에서 전한 말씀과 삶에서 건져 올린 이야기, 읽고 쓴 기록을 한곳에 모았습니다.<br>필요한 주제에서 시작해 천천히 둘러보세요.</p>
  </div>
  {quicknav}
  {sections["fresh"]}
  {sections["stories"]}
  {sections["sermon"]}
  {sections["youtube"]}
  <div class="reader-spread" aria-label="시와 생각의 노트">
    {sections["poems"]}
    {sections["pensees"]}
  </div>
  {sections["reading"]}
  {sections["works"]}
  {sections["church"]}
  {church_banner}
</main>
{footer}
{''.join(extra_scripts)}
</body>'''
new_page = (doctype.group(0) + "\n" if doctype else "<!doctype html>\n") + f'<html lang="{escape(lang, quote=True)}">\n{head}\n{body}\n</html>\n'
PATH.write_text(new_page, encoding="utf-8")
print("Composed editorial homepage:", len(new_page), "characters; sections:", ", ".join(sections))
