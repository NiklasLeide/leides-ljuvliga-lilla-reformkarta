"""SOU 2025:18 avsnitt 22.1 (författningskommentar till skollagen): återgiven föreslagen lydelse per paragraf + 'behandlas i avsnitt'."""
import re,json,sys
S=sys.argv[1]
P=open(f'{S}/pdf/sou1r.txt').read().split('\f')
START,END=875,927   # tryckta sidor enligt innehållsförteckningen (22.1 s. 875, 22.2 s. 927)
rows=[]
for pg in range(START,END+1):
    for l in P[pg-1].split('\n'):
        s=l.strip()
        if s in ('SOU 2025:18','Författningskommentar') or re.fullmatch(r'\d{3}',s): continue
        rows.append((pg,s))
out=[]; kap=None; cur=None; mode=None
HEAD=re.compile(r'^(\d+(?: [a-z])?) ?§$')
for pg,s in rows:
    if re.fullmatch(r'\d+(?: [a-z])? kap\.',s): kap=s.replace(' kap.',''); continue
    if s.startswith('Ikraftträdande och övergångsbestämmelser'):
        cur={'kap':'ikraft','par':'övergångsbestämmelser','sida':pg,'text':[],'kommentar':[]}; out.append(cur); mode='text'; continue
    if s=='22.2': break
    m=HEAD.match(s)
    if m and kap:
        cur={'kap':kap,'par':m.group(1),'sida':pg,'text':[],'kommentar':[]}; out.append(cur); mode='text'; continue
    if cur is None: continue
    if mode=='text' and re.match(r'^(Paragrafen|Bestämmelsen|Paragrafens|I paragrafen|Ändringen|Första stycket|Andra stycket|Övervägandena)\b',s):
        mode='komm'
    (cur['text'] if mode=='text' else cur['kommentar']).append(s)
for c in out:
    t=' '.join(c['text']); t=re.sub(r'(\w)-\s(?=[a-zåäö])',r'\1',t); t=re.sub(r'\s+',' ',t).strip()
    k=re.sub(r'\s+',' ',' '.join(c['kommentar']))
    c['text']=t
    c['avsnitt']=sorted(set(re.findall(r'(\d{1,2}(?:\.\d{1,2}){1,3})',' '.join(re.findall(r'(?:behandlas i avsnitt|Övervägandena finns i avsnitt|övervägandena finns i avsnitt|behandlas i avsnitten)[^.]*(?:\.\d[^.]*)*',k)))))
    c['upphavs']=bool(re.search(r'upphävs|ska upphöra att gälla',k)) and not t
    c['kommentar']=k[:400]
json.dump(out,open(f'{S}/sou_paragrafer.json','w'),ensure_ascii=False,indent=1)
print(len(out),'paragrafer;',sum(1 for c in out if c['avsnitt']),'med avsnitt;',sum(1 for c in out if not c['text']),'utan text')
for c in out[:8]: print(c['kap'],c['par'],c['sida'],c['avsnitt'],c['text'][:70])
