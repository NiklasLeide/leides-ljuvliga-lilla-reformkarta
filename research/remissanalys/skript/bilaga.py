import re,json,sys
SPEC={ # reform: (propfile, prop nr, first pdf page, bilaga)
 'laroplaner':('194','Prop. 2025/26:194',269),
 'betyg':('197','Prop. 2025/26:197',226),
 'stod':('195','Prop. 2025/26:195',177),
 'spraklig':('194','Prop. 2025/26:194',314),
 'studiero':('193','Prop. 2025/26:193',184),
 'tid':('196','Prop. 2025/26:196',142),
 'tioarig':('143','Prop. 2024/25:143',223),
}
def clean(s):
    s=re.sub(r'Prop\. 20\d\d/\d\d:\d+\s*','',s)
    s=re.sub(r'Bilaga \d+\s*','',s)
    s=re.sub(r'\n\s*\d{1,3}\s*\n','\n',s)
    s=re.sub(r'\s+',' ',s)
    s=re.sub(r'(\w)-(?!och\b|eller\b|samt\b)(?=[a-zåäö])',r'\1',s)  # avstavning utan mellanslag
    s=re.sub(r'(\w)-(och|eller) ',r'\1- \2 ',s)
    s=re.sub(r'(\w)- (?!och |eller |samt )(?=[a-zåäö])',r'\1',s)  # avstavning över radbrytning
    return s.strip()
def split(s):
    s=s.strip().rstrip('.')
    parts=[p.strip() for p in re.split(r',\s*(?![^()]*\))',s)]
    out=[]
    for i,p in enumerate(parts):
        p=re.sub(r'^(samt|och)\s+','',p)
        # sista listposten: "X och Y" / "X samt Y" -> två namn (inte "Barn- och Ungdoms...")
        m=re.match(r'(.+?[^-])\s+(samt|och)\s+([A-ZÅÄÖ].*)$',p)
        if m and (i==len(parts)-1 or m.group(2)=='samt'):
            out+=[m.group(1),m.group(3)]
        else: out.append(p)
    return [o for o in out if o]
res={}
for k,(f,prop,pg) in SPEC.items():
    pages=open(sys.argv[1]+f'/prop{f}r.txt').read().split('\f')
    txt=''; pmap=[]
    for i in range(pg-1,pg+3):
        p=pages[i]
        if i>pg-1 and ('Förteckning över remissinstanserna' in p or 'Lagrådsremissens' in p or 'Lagrådets yttrande' in p or 'Sammanfattning' in p[:300]):
            # cut at that heading
            cut=min([p.find(h) for h in ['Förteckning över remissinstanserna','Lagrådsremissens','Lagrådets','Sammanfattning'] if p.find(h)>=0])
            txt+=p[:cut]; pmap.append(i+1); break
        txt+=p+'\n'; pmap.append(i+1)
    a=txt.find('Efter remiss har yttranden')
    body=clean(txt[a:])
    for pn in pmap: body=re.sub(r'\s%d\s'%pn,' ',body)
    # dela i grupper vid fasta inledningsfraser (inte vid punkt: "Kungl.", "m.fl." finns i namn)
    MARK=[('svarat',r'Efter remiss har yttranden kommit in från'),
          ('spontant',r'(?:Därutöver|Dessutom) har (?:spontana )?yttranden (?:inkommit|lämnats|kommit in) från|Spontana yttranden har därutöver inkommit från'),
          ('privatpersoner',r'[A-ZÅÄÖ][a-zåäö]+ spontana yttranden har inkommit från privatpersoner'),
          ('ej_svarat',r'Följande remissinstanser har [^:]*:')]
    hits=[]
    for name,rx in MARK:
        for m in re.finditer(rx,body): hits.append((m.start(),m.end(),name))
    hits.sort()
    groups={'svarat':None,'spontant':None,'ej_svarat':None,'privatpersoner':None}
    for i,(st,en,name) in enumerate(hits):
        seg_end=hits[i+1][0] if i+1<len(hits) else len(body)
        seg=body[en:seg_end].strip()
        groups[name+'_text']=body[st:seg_end].strip()
        if name=='privatpersoner': groups[name]=body[st:seg_end].strip(); continue
        groups[name]=split(seg)
    rest=body
    res[k]={'prop':prop,'pdfsidor':pmap,**groups}
    print('==',k,prop,pmap,'svarat',len(groups['svarat'] or []),'spontant',len(groups['spontant'] or []),'ej',len(groups['ej_svarat'] or []),'|',groups['privatpersoner'])
# kända tryckfel: komma saknas i propositionens lista (verifierat i PDF-texten)
for k in res:
    for g in ('svarat','ej_svarat','spontant'):
        L=res[k][g] or []
        out=[]
        for n in L:
            if n=='Dals-Eds kommun Elevernas riksförbund': out+=['Dals-Eds kommun','Elevernas riksförbund']; res[k].setdefault('_anm',[]).append('Komma saknas i propositionen mellan "Dals-Eds kommun" och "Elevernas riksförbund"; delat.')
            else: out.append(n)
        res[k][g]=out or res[k][g]
json.dump(res,open(sys.argv[2],'w'),ensure_ascii=False,indent=1)
