# 이미 홈페이지·블로그에 있는 글(posts.json)과 겹치는지 표시: 시는 dup 표시(시집에는 두되 블로그에는 다시 올리지 않음), 묵상은 겹치면 뺀다
import json,re
n=lambda s: re.sub(r'[\W\d_]','',s)
big=' '.join(n(p['body']) for p in json.load(open('posts.json',encoding='utf-8')))
def dup(x,k):
    ls=[n(l) for l in x['body'].split('\n') if len(n(l))>=12][:k]
    return bool(ls) and sum(1 for l in ls if l[:25] in big)>=max(1,len(ls)-1)
P=json.load(open('anshik_poems.json',encoding='utf-8'))
for p in P: p['dup']=dup(p,3)
json.dump(P,open('anshik_poems.json','w',encoding='utf-8'),ensure_ascii=False,indent=0)
M=[m for m in json.load(open('anshik_pensees.json',encoding='utf-8')) if not dup(m,2)]
for k,m in enumerate(M,1): m['id']=f'm{k:03d}'
json.dump(M,open('anshik_pensees.json','w',encoding='utf-8'),ensure_ascii=False,indent=0)
print('시',len(P),'새 시',sum(1 for p in P if not p['dup']),'묵상',len(M))
