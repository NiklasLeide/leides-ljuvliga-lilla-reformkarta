"""Steg 4: SFS-diff per utredningsförslag (lagtext): SOU 2025:18 (författningskommentar 22.1) -> prop. 197/194 lagförslag -> beslutad lydelse
(skollagen i konsoliderad form, riksdagens öppna data; versioner införda genom SFS 2026:1242, 2026:1243, 2026:1245)."""
import json,re,sys,difflib
S=sys.argv[1]; FIDS=set(json.load(open(sys.argv[2]))); OUT=sys.argv[3]
HAMTAT='2026-11-10'
boxes={b['id']:b for b in json.load(open(f'{S}/sou_boxes.json')) if b['typ']=='Förslag'}
sou=json.load(open(f'{S}/sou_paragrafer.json'))
sfsd=json.load(open(f'{S}/sfs_skollag.json')); sfs=sfsd['versioner']
props=[json.load(open(f'{S}/prop197_lag.json')),json.load(open(f'{S}/prop194_lag.json'))]
BETYGSLAGAR=('2026:1242','2026:1243','2026:1245')
# övergångsbestämmelser i konsoliderad skollag (block som börjar med raden 'ÅÅÅÅ:NNNN')
_t=open(f'{S}/sfs/skollag.txt',encoding='utf-8').read(); _t=_t[_t.find('\nÖvergångsbestämmelser'):]
for _m in re.finditer(r'\n(2026:124[235])\n(.*?)(?=\n\d{4}:\d+\n|\Z)',_t,re.S):
    sfs.append({'kap':'ikraft','par':'övergångsbestämmelser','ikraft':None,'upphor':None,'lag':_m.group(1),'text':re.sub(r'\s+',' ',_m.group(2)).strip()})
# propositionens ikraftträdande- och övergångsbestämmelser per lagförslag (rå text efter sista paragrafen)
_pr=open(f'{S}/pdf/prop197r.txt').read()
_lag=_pr[_pr.find('2.1 Förslag till lag om ändring i skollagen'):_pr.find('Ärendet och dess beredning',_pr.find('2.3'))] if False else None
U_SOU='https://www.regeringen.se/contentassets/56408e57ea8e4954bf38491c8bc33d4c/ett-likvardigt-betygssystem-sou-202518-volym-1.pdf'
U_P={'Prop. 2025/26:197':'https://www.regeringen.se/contentassets/a37af6932a5f4cf794499eb68a798d63/ett-likvardigt-betygssystem-prop.-202526197.pdf',
     'Prop. 2025/26:194':'https://www.regeringen.se/contentassets/42c1e2e4596b4f8682e3d8283b91a138/nya-laroplaner--for-en-stark-kunskapsskola-prop.-202526194.pdf'}
U_SFS='https://data.riksdagen.se/dokument/sfs-2010-800.text'
FORORDNINGAR=[('Gymnasieförordning (2010:2039)','https://data.riksdagen.se/dokument/sfs-2010-2039.text'),('Skolförordning (2011:185)','https://data.riksdagen.se/dokument/sfs-2011-185.text'),
 ('Högskoleförordning (1993:100)','https://data.riksdagen.se/dokument/sfs-1993-100.text'),('Förordning (2011:1108) om vuxenutbildning','https://data.riksdagen.se/dokument/sfs-2011-1108.text'),
 ('Förordning (2014:854) om vidareutbildning i form av ett fjärde tekniskt år','https://data.riksdagen.se/dokument/sfs-2014-854.text')]
def n(t): return re.sub(r'[\s\-–­]','',t.lower())
def sim(a,b): return difflib.SequenceMatcher(None,n(a),n(b),autojunk=False).ratio()
def wdiff(a,b):
    A=a.split(); B=b.split(); out=[]
    for op,i1,i2,j1,j2 in difflib.SequenceMatcher(None,A,B,autojunk=False).get_opcodes():
        if op!='equal': out.append({'op':{'replace':'ersatt','delete':'struken','insert':'tillagd'}[op],'fore':' '.join(A[i1:i2]) or None,'efter':' '.join(B[j1:j2]) or None})
    return out
def paragrafer_for(f):
    a=boxes[f]['avsnitt']
    return [p for p in sou if any(x==a or x.startswith(a+'.') or a.startswith(x+'.') for x in p['avsnitt'])]
def match(cands,text):
    """Bästa kandidat: först samma kap+§, annars högst textlikhet inom kapitlet."""
    best=None
    for c in cands:
        r=sim(text,c['text'])
        if best is None or r>best[0]: best=(r,c)
    return best
res=[]
for f in sorted(FIDS,key=lambda x:int(x[1:])):
    b=boxes[f]; pp=paragrafer_for(f)
    post={'forslag':f,'sou_avsnitt':b['avsnitt'],'forslag_kalla':{'text':f"SOU 2025:18 s. {b['sida']}",'url':U_SOU},'paragrafer':[]}
    if not pp:
        if re.search(r'ska ges i uppgift|ges i uppdrag|ska ge Statens skolverk i uppdrag|ska ansvara för|instruktion',b['text']):
            post.update(status='ej lagtext',status_kalla={'text':'Förslaget gäller uppdrag/ansvar för myndighet; ingen paragraf i SOU:ns författningskommentar till skollagen (avsnitt 22.1) hänvisar till avsnitt '+b['avsnitt'],'url':U_SOU})
        else:
            post.update(status=f'ej i SFS per {HAMTAT}',status_kalla={'text':'Ingen paragraf i SOU:ns författningskommentar till skollagen (22.1) hänvisar till avsnitt '+b['avsnitt']+' — förslaget avser förordningsnivå. Konsoliderade förordningar hämtade '+HAMTAT+' innehåller inte den nya betygsskalan (0 träffar på "betyget 4"): '+'; '.join(x[0] for x in FORORDNINGAR),'url':FORORDNINGAR[0][1],'ovriga_urler':[x[1] for x in FORORDNINGAR[1:]]})
        res.append(post); continue
    stats=[]
    for p in pp:
        rad={'paragraf':f"{p['kap']} kap. {p['par']} §",'sou':{'text':p['text'],'kalla':{'text':f"SOU 2025:18 s. {p['sida']} (författningskommentar 22.1)",'url':U_SOU}}}
        # proposition
        pc=[dict(text=q['foreslagen'],kap=q['kap'],par=q['par'],sida=q['sida'],prop=pr['proposition'],lf=lf['lagforslag']) for pr in props for lf in pr['lagforslag'] for q in lf['paragrafer'] if q['kap']==p['kap']]
        same=[c for c in pc if c['par']==p['par'].replace(' ','')]
        m=match(same,p['text']) or match(pc,p['text'])
        if m:
            r,c=m
            rad['proposition']={'text':c['text'],'paragraf':f"{c['kap']} kap. {c['par']} §",'likhet_mot_sou':round(r,3),'kalla':{'text':f"{c['prop']} s. {c['sida']}, lagförslag {c['lf']}",'url':U_P[c['prop']]},
                                'matchning':'nummer' if c['par']==p['par'].replace(' ','') else 'textlikhet','manuell_granskning':r<0.8}
        else: rad['proposition']=None
        # SFS
        sc=[v for v in sfs if v['kap']==p['kap'] and v['lag'] in BETYGSLAGAR]
        same=[v for v in sc if v['par']==p['par'].replace(' ','')]
        ms=match(same,p['text']) or match(sc,p['text'])
        cur=[v for v in sfs if v['kap']==p['kap'] and v['par']==p['par'].replace(' ','') and v['ikraft'] is None]
        if ms:
            r,v=ms
            rad['beslutad']={'text':v['text'],'paragraf':f"{v['kap']} kap. {v['par']} §",'sfs':v['lag'],'ikraft':v['ikraft'],'likhet_mot_sou':round(r,3),
                             'kalla':{'text':f"Skollag (2010:800) {v['kap']} kap. {v['par']} § i lydelse enligt SFS {v['lag']}"+(f", träder i kraft {v['ikraft']}" if v['ikraft'] else '')+f"; konsoliderad text hämtad {HAMTAT} ({sfsd['meta']['andrad_tom']})",'url':U_SFS},
                             'matchning':'nummer' if v['par']==p['par'].replace(' ','') else 'textlikhet','manuell_granskning':r<0.8}
            if r>=0.999: st='oförändrad'
            else: st='ändrad'; rad['diff_sou_mot_beslutad']=wdiff(p['text'],v['text'])
        else:
            rad['beslutad']=None
            if cur: rad['nuvarande_sfs']={'text':cur[0]['text'],'sfs':cur[0]['lag'],'kalla':{'text':f"Skollag (2010:800) {p['kap']} kap. {p['par']} §, gällande lydelse (SFS {cur[0]['lag']}), hämtad {HAMTAT}",'url':U_SFS}}
            st='ej med'
        rad['status']=st; stats.append(st)
        rad['manuell_granskning']=bool((rad.get('proposition') or {}).get('manuell_granskning') or (rad.get('beslutad') or {}).get('manuell_granskning'))
        post['paragrafer'].append(rad)
    us=set(stats)
    post['status']=stats[0] if len(us)==1 else 'blandad'
    post['status_per_paragraf']={s:stats.count(s) for s in us}
    post['status_kalla']={'text':'Härledd per paragraf: SOU:ns föreslagna lydelse jämförd med beslutad lydelse (SFS 2026:1242/1243/1245). Statusvärdet är mekaniskt (textlikhet), inte en bedömning.','url':U_SFS}
    res.append(post)
meta={'hamtningsdatum':HAMTAT,'beslutad_lydelse_kalla':'Skollag (2010:800) konsoliderad, riksdagens öppna data (Källa: Regeringskansliet / Lagrummet), '+sfsd['meta']['andrad_tom']+'. Ändrings-SFS i original (svenskforfattningssamling.se) nåddes inte från miljön.',
      'statusregler':{'oförändrad':'SOU:ns föreslagna paragraf = beslutad lydelse (normaliserad textlikhet ≥ 0,999)','ändrad':'beslutad lydelse finns men skiljer sig; ordagrann ord-diff sparas','ej med':'ingen version införd genom SFS 2026:1242/1243/1245 för paragrafen','ej lagtext':'förslaget är inte författningstext (uppdrag/ansvar)',f'ej i SFS per {HAMTAT}':'förslaget avser förordning som ännu inte finns i SFS'},
      'matchning':'Paragrafer matchas på kapitel + nummer; saknas samma nummer används högst textlikhet inom kapitlet. Likhet < 0,80 ⇒ manuell_granskning: true.',
      'forslag_till_paragraf':'Paragrafer knyts till förslag via SOU:ns författningskommentar ("Bestämmelsen behandlas i avsnitt …"), dvs. på avsnittsnivå — flera förslag i samma avsnitt delar paragrafer.'}
json.dump({'_meta':meta,'forslag':res},open(OUT,'w'),ensure_ascii=False,indent=1)
from collections import Counter
print('förslag',len(res),Counter(r['status'] for r in res))
rows=[x for r in res for x in r['paragrafer']]
print('paragrafrader',len(rows),Counter(x['status'] for x in rows),'manuell',sum(x['manuell_granskning'] for x in rows))
print('auto-matchade (nummer & likhet>=0.8, prop och SFS):',sum(1 for x in rows if x.get('beslutad') and not x['manuell_granskning'] and x['beslutad']['matchning']=='nummer'))
