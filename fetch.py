# 네이버 블로그 카테고리·대표글 수집 -> blog.json
import urllib.request, json, os, time
D = os.path.dirname(os.path.abspath(__file__))
H = {'User-Agent': 'Mozilla/5.0', 'Referer': 'https://m.blog.naver.com/saechang888'}

def get(url):
    return json.loads(urllib.request.urlopen(urllib.request.Request(url, headers=H), timeout=30).read().decode('utf-8'))

cats = get('https://m.blog.naver.com/api/blogs/saechang888/category-list')['result']['mylogCategoryList']
WANT = {101: 9, 179: 1, 36: 6, 91: 3, 92: 3, 93: 3, 94: 3, 45: 3, 46: 3, 47: 3, 90: 3, 161: 5}
posts = {}
for no, n in WANT.items():
    r = get(f'https://m.blog.naver.com/api/blogs/saechang888/post-list?categoryNo={no}&itemCount={n}&page=1')['result']
    posts[no] = [dict(logNo=i['logNo'], title=i['titleWithInspectMessage'], brief=i.get('briefContents') or '',
                      date=time.strftime('%Y.%m.%d', time.localtime(i['addDate'] / 1000)), cat=i.get('categoryName'))
                 for i in r['items']]
    time.sleep(0.3)
# ---- 유튜브 「어음성경」 최근 영상(RSS) + 영상 수 ----
import xml.etree.ElementTree as ET, re
CH = 'UCTktTwZDOXecQWZd57LLtTA'
NS = {'a': 'http://www.w3.org/2005/Atom', 'yt': 'http://www.youtube.com/xml/schemas/2015', 'm': 'http://search.yahoo.com/mrss/'}
yt = {'channel': CH, 'videos': [], 'count': None}
try:
    feed = ET.fromstring(urllib.request.urlopen(urllib.request.Request(
        f'https://www.youtube.com/feeds/videos.xml?channel_id={CH}', headers={'User-Agent': 'Mozilla/5.0'}), timeout=30).read())
    for e in feed.findall('a:entry', NS):
        yt['videos'].append(dict(id=e.findtext('yt:videoId', namespaces=NS), title=e.findtext('a:title', namespaces=NS),
                                 date=e.findtext('a:published', namespaces=NS)[:10].replace('-', '.')))
    page = urllib.request.urlopen(urllib.request.Request('https://www.youtube.com/channel/' + CH,
        headers={'User-Agent': 'Mozilla/5.0', 'Accept-Language': 'ko-KR'}), timeout=30).read().decode('utf-8')
    m = re.search(r'"content":"동영상 (\d+)개"', page)
    if m: yt['count'] = int(m.group(1))
except Exception as ex:
    print('youtube fetch failed:', ex)
    old = os.path.join(D, 'blog.json')
    if os.path.exists(old): yt = json.load(open(old, encoding='utf-8')).get('youtube', yt)

json.dump({'youtube': yt, 'cats': [dict(no=c['categoryNo'], parent=c.get('parentCategoryNo'), cnt=c['postCnt'], name=c['categoryName']) for c in cats],
           'posts': posts}, open(os.path.join(D, 'blog.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print({k: len(v) for k, v in posts.items()})
