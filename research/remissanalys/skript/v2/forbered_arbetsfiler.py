"""Engångsförberedelse (Sprint 16 T3): skriver arbetsfiler som bygg-pilot.py läser.
Källor: pdftotext -layout av Prop. 2025/26:197 och 2025/26:194 (regeringen.se) och SOU 2025:18:s innehållsförteckning.
Resultatet checkas in under research/remissanalys/arbetsfiler/ så att bygget är reproducerbart utan PDF:erna."""
import re,json,sys
S,OUT=sys.argv[1],sys.argv[2]
U={'197':'https://www.regeringen.se/contentassets/a37af6932a5f4cf794499eb68a798d63/ett-likvardigt-betygssystem-prop.-202526197.pdf',
   '194':'https://www.regeringen.se/contentassets/42c1e2e4596b4f8682e3d8283b91a138/nya-laroplaner--for-en-stark-kunskapsskola-prop.-202526194.pdf'}
def printed(p,i):
    L=[l.strip() for l in p.split('\n') if l.strip()]
    for l in L[-3:]+L[:3]:
        m=re.fullmatch(r'(\d{1,3})(\s+Prop\..*)?',l) or re.fullmatch(r'Prop\. \S+\s+(\d{1,3})',l) or re.match(r'^(\d{1,3})\s{5,}',l)
        if m: return int(m.group(1))
    return i+1
HEAD=re.compile(r'^\s{0,25}((?:1?\d)(?:\.\d{1,2}){0,3})\s{2,}([A-ZÅÄÖ].*)$')
LAB=re.compile(r'^\s*(Utredningen om likvärdiga betyg och meritvärdens (?:förslag|bedömning)|Läroplansutredningens (?:förslag|bedömning)|Regeringens förslag|Regeringens bedömning|Utredningens förslag|Utredningens bedömning|Remissinstanserna|Skälen för regeringens.*|Lagrådet)\s*$')
want={'197':None,'194':{'6.7','6.8'}}
out={}
for pr in ('197','194'):
    P=open(f'{S}/pdf/prop{pr}.txt').read().split('\f')
    cur=None; lab=None; secs=[]; prev_blank=False; prev_text=''; in_sub=False; rub_fort=False
    for i,p in enumerate(P):
        pg=printed(p,i)
        rader=p.split('\n')
        for ri,l in enumerate(rader):
            nasta=next((r.strip() for r in rader[ri+1:] if r.strip()),'')
            l2=re.sub(r'^\s*Prop\. 20\d\d/\d\d:\d+\s{2,}','',l); l2=re.sub(r'\s+Prop\. 20\d\d/\d\d:\d+\s*$','',l2); l2=re.sub(r'\s+Prop\.\s*$','',l2); l2=re.sub(r'^\s*20\d\d/\d\d:\d+\s{2,}','',l2)
            mp=re.match(r'^\s*(\d{1,3})\s{3,}(\S.*)$',l2)
            if mp and abs(int(mp.group(1))-pg)<=1: l2=mp.group(2)   # sidnummer i radstart (marginal)
            mt=re.match(r'^(.*\S)\s{3,}(\d{1,3})\s*$',l2)
            if mt and abs(int(mt.group(2))-pg)<=1: l2=mt.group(1)    # sidnummer i radslut (marginal)
            if re.fullmatch(r'\s*\d{1,3}\s*',l2): continue
            # underrubrik inne i en del (kort rad utan avslutande skiljetecken efter tomrad) räknas inte till löptexten
            if in_sub and l2.strip() and not re.search(r'[.,:;-]$',l2.strip()) and re.match(r'[A-ZÅÄÖ]',re.sub(r'^Prop\. 20\d\d/\d\d:\d+\s+','',nasta)) and not LAB.match(l2) and not HEAD.match(l2):
                continue                                   # fortsättningsrad i flerradig underrubrik
            in_sub=False
            if prev_blank and prev_text.endswith(('.',':')) and l2.strip() and len(l2.strip())<70 and not re.search(r'[.,:;]$',l2.strip()) and lab and not LAB.match(l2) and not HEAD.match(l2):
                prev_blank=False; in_sub=True; continue
            prev_blank = not l2.strip()
            if l2.strip(): prev_text=l2.strip()
            m=HEAD.match(l2)
            if m and not re.search(r'\.{4,}',l2):
                cur={'avsnitt':m.group(1),'rubrik':m.group(2).strip(),'delar':[]}; secs.append(cur); lab=None; rub_fort=True; continue
            if rub_fort:
                # rubriken bryts över flera rader i PDF:en; fortsättningsrader fram till första tomrad hör till rubriken
                if l2.strip() and not LAB.match(l2):
                    cur['rubrik']=re.sub(r'(\w)- (?!och |eller |samt )(?=[a-zåäö])',r'\1',cur['rubrik']+' '+l2.strip()); continue
                rub_fort=False
            m=LAB.match(l2)
            if m and cur is not None:
                lab=m.group(1); cur['delar'].append({'del':lab,'sidor':{}}); continue
            if cur is not None and lab and l2.strip():
                d=cur['delar'][-1]; d['sidor'].setdefault(str(pg),[]).append(l2.strip())
    for s in secs:
        if not any(d['del'].startswith('Regeringens') for d in s['delar']): continue
        if want[pr] and s['avsnitt'] not in want[pr]: continue
        delar=[]
        for d in s['delar']:
            sid=[{'sida':int(k),'text':re.sub(r'\s+',' ',re.sub(r'(\w)- (?!och |eller |samt )(?=[a-zåäö])',r'\1',' '.join(v))).strip()} for k,v in d['sidor'].items()]
            delar.append({'del':d['del'],'sidor':sid})
        out[f'{pr}:{s["avsnitt"]}']={'proposition':f'Prop. 2025/26:{pr}','avsnitt':s['avsnitt'],'rubrik':s['rubrik'],'url':U[pr],'delar':delar}
inneh={}
for pr in ('197','194'):
    P=open(f'{S}/pdf/prop{pr}.txt').read().split('\f')
    toc={}; buf=''
    for p in P[:8]:
        for l in p.split('\n'):
            l2=re.sub(r'^\s*Prop\. 20\d\d/\d\d:\d+\s+','',l); l2=re.sub(r'\s+Prop\. 20\d\d/\d\d:\d+\s*$','',l2).strip()
            if not l2: continue
            if re.match(r'^(\d{1,2}(?:\.\d{1,2}){0,3})\s+\S',l2) and not buf: buf=l2
            elif buf: buf+=' '+l2
            else: continue
            mm=re.match(r'^(\d{1,2}(?:\.\d{1,2}){0,3})\s+(.*?)\s*\.{3,}\s*(\d{1,3})$',buf)
            if mm:
                titel=re.sub(r'(\w)- (?!och |eller |samt )(?=[a-zåäö])',r'\1',re.sub(r'\s+',' ',mm.group(2)))
                toc.setdefault(mm.group(1),{'titel':titel,'sida':int(mm.group(3))}); buf=''
            elif len(buf)>400: buf=''
    inneh[pr]={'proposition':f'Prop. 2025/26:{pr}','url':U[pr],'innehallsforteckning':toc}
json.dump({'_meta':{'beskrivning':'Propositionernas innehållsförteckning (avsnittsnummer, rubrik, sida) ur pdftotext -layout; används av validera-pilot.py för att kontrollera att propositionsavsnittens rubriker är fullständiga.'},'propositioner':inneh},open(f'{OUT}/propositioner-innehall.json','w'),ensure_ascii=False,indent=1)
toc=json.load(open(f'{S}/sou_toc.json'))
kap={t['avsnitt']:t['rubrik'] for t in toc if '.' not in t['avsnitt'] and t['avsnitt'].isdigit()}
avs={t['avsnitt']:{'rubrik':t['rubrik'],'sida':t['sida']} for t in toc if t['avsnitt'].split('.')[0].isdigit() and 9<=int(t['avsnitt'].split('.')[0])<=20}
json.dump({'_meta':{'beskrivning':'Propositionsavsnitt (med regeringens förslags-/bedömningsruta) i Prop. 2025/26:197 och avsnitt 6.7–6.8 i Prop. 2025/26:194: all text per underrubrik och tryckt sida, ur pdftotext -layout. Används för namnsökning.','kalla':U},'avsnitt':out},open(f'{OUT}/propositionsavsnitt-text.json','w'),ensure_ascii=False,indent=1)
json.dump({'_meta':{'kalla':{'text':'SOU 2025:18, innehållsförteckning','url':'https://www.regeringen.se/contentassets/56408e57ea8e4954bf38491c8bc33d4c/ett-likvardigt-betygssystem-sou-202518-volym-1.pdf'}},'kapitel':kap,'avsnitt':avs},open(f'{OUT}/sou-innehall.json','w'),ensure_ascii=False,indent=1)
print(len(out),sorted(out))
