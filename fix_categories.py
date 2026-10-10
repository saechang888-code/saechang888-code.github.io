# 독후감 카테고리를 신앙서적 · 자녀교육 · 일반서적 · 이지성인문고전 네 가지로 정리 (자동 분류에서 틀린 책은 손으로 고침)
import os, json
D = os.path.dirname(os.path.abspath(__file__))
RENAME = {'신학/신앙서적': '신앙서적', '자녀교육도서': '자녀교육', '일반서적': '일반서적', '이지성 인문고전': '이지성인문고전'}
FIX = {
    '신앙서적': ['20270222-b2', '20270228-b1', '20270306-b2', '20270307-b1', '20270314-b2', '20270313-b1', '20270507-b1',
               '20270614-b2', '20270609-b2', '20270706-b2', '20270628-b2', '20270724-b2', '20270731-b2', '20270802-b1',
               '20270807-b2', '20270716-b2', '20270501-b1', '20270706-b1', '20270516-b1', '20270602-b2', '20270606-b2',
               '20270718-b1'],
    '일반서적': ['20261230-b1', '20270101-b1', '20270119-b1', '20270213-b1', '20270215-b1', '20270524-b1', '20270629-b1',
               '20270721-b1', '20270709-b2', '20270704-b2', '20270303-b1', '20270201-b1', '20270627-b1'],
    '자녀교육': ['20261226-b1', '20270220-b1'],
    '이지성인문고전': ['20270510-b1'],
}
fix = {i: c for c, ids in FIX.items() for i in ids}
path = os.path.join(D, 'posts.json')
posts = json.load(open(path, encoding='utf-8'))
for p in posts:
    if p['kind'] != '독후감': continue
    leaf = p['category'].split('>')[-1].strip()
    p['category'] = '독서 마당 > ' + fix.get(p['id'], RENAME.get(leaf, leaf))
json.dump(posts, open(path, 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
import collections
print(collections.Counter(p['category'] for p in posts if p['kind'] == '독후감'))
