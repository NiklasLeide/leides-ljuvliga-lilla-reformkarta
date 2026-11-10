import re,json,sys
f=sys.argv[1]; P=open(f).read().split('\f')
def printed(p):
    L=[l.strip() for l in p.split('\n') if l.strip()]
    for l in L[-3:]+L[:3]:
        m=re.fullmatch(r'(\d{1,3})(\s+Prop\..*)?',l) or re.fullmatch(r'Prop\. \S+\s+(\d{1,3})',l) or re.match(r'^(\d{1,3})\s{5,}',l)
        if m: return int(m.group(1))
    return None
# bygg rad-lista med sidnummer; ta bort marginaltext "Prop. 2025/26:197" i radstart
rows=[]
for i,p in enumerate(P):
    pg=printed(p) or (i+1)
    for l in p.split('\n'):
        l2=re.sub(r'^\s*Prop\. 20\d\d/\d\d:\d+\s{2,}','',l)
        l2=re.sub(r'\s{2,}Prop\. 20\d\d/\d\d:\d+\s*$','',l2)
        rows.append((pg,l2))
HEAD=re.compile(r'^\s{0,25}((?:1?\d)(?:\.\d{1,2}){0,3})\s{2,}([A-ZÅÄÖ].*)$')
LAB=re.compile(r'^\s*(Utredningen om likvärdiga betyg och meritvärdens (?:förslag|bedömning)|Läroplansutredningens (?:förslag|bedömning)|Regeringens förslag|Regeringens bedömning|Utredningens förslag|Utredningens bedömning|Promemorians förslag|Remissinstanserna|Skälen för regeringens.*|Lagrådet)\s*$')
secs=[]; cur=None; lab=None
for pg,l in rows:
    if re.fullmatch(r'\s*\d{1,3}\s*',l): continue
    m=HEAD.match(l)
    if m and not re.search(r'\.{4,}',l):
        cur={'avsnitt':m.group(1),'rubrik':m.group(2).strip(),'sida':pg,'delar':{}}; secs.append(cur); lab=None; continue
    m=LAB.match(l)
    if m and cur is not None:
        lab=m.group(1)
        if lab in cur['delar']:
            n=2
            while f'{lab}#{n}' in cur['delar']: n+=1
            lab=f'{lab}#{n}'
        cur['delar'][lab]={'sida':pg,'rader':[]}; continue
    if cur is not None and lab:
        cur['delar'][lab]['rader'].append(l.strip())
        cur['delar'][lab].setdefault('sidor',set()).add(pg)
for s in secs:
    for k,d in s['delar'].items():
        t=' '.join(x for x in d.pop('rader'))
        t=re.sub(r'\s+',' ',t); t=re.sub(r'(\w)- (?!och |eller |samt )(?=[a-zåäö])',r'\1',t)
        d['text']=t.strip(); d['sidor']=sorted(d.get('sidor',[]))
    s['har_box']=any(k.startswith('Regeringens') for k in s['delar'])
secs=[s for s in secs if s['har_box']]
json.dump(secs,open(sys.argv[2],'w'),ensure_ascii=False,indent=1)
for s in secs:
    u=s['delar'].get('Utredningens förslag') or s['delar'].get('Utredningens bedömning') or {}
    print(s['avsnitt'],s['sida'],s['rubrik'][:60],'| U:',(u.get('text') or '')[:120])
