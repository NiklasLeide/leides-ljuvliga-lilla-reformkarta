"""Bygger research/remissanalys/v2/utmaningar-betyg-v2.json (steg 1–4, 7) och avsandare-betyg.json (steg 5)."""
import json,re,sys,collections,unicodedata
S=sys.argv[1]; V2='research/remissanalys/v2/'
v1=json.load(open('research/remissanalys/utmaningar-betyg.json'))
P={p['id']:p for p in json.load(open(f'{S}/passager.json'))}
boxes=[b for b in json.load(open(f'{S}/sou_boxes.json')) if b['typ']=='Förslag']
BOX={b['id']:b for b in boxes}
toc=json.load(open(f'{S}/sou_toc.json'))
KAPRUBRIK={t['avsnitt']:t['rubrik'] for t in toc if '.' not in t['avsnitt']}
sou_par=json.load(open(f'{S}/sou_paragrafer.json'))
PAR={(p['kap'],p['par'].replace(' ','')):p['avsnitt'] for p in sou_par if p['kap']!='ikraft'}
sfsd=json.load(open('research/remissanalys/sfs-diff-betyg.json'))
SFSF={f['forslag']:(i,f) for i,f in enumerate(sfsd['forslag'])}
KOD={x['id']:x for k in (1,2,3,4) for x in json.load(open(f'{S}/v2/svar{k}.json'))}
TYPER=['Kostnader och finansiering','Tidplan och reformtakt','Personal, kompetens och arbetsbelastning','System och teknik','Organisation och planering','Otydlighet i förslaget','Likvärdighet och konsekvenser för elever','Övrigt']
SOU_URL='https://www.regeringen.se/rattsliga-dokument/statens-offentliga-utredningar/2025/02/sou-202518/'
def f_exact(sec):  # förslag i avsnittet eller dess underavsnitt – ingen kapitelexpansion, ingen föräldrafallback
    return [b['id'] for b in boxes if b['avsnitt']==sec or b['avsnitt'].startswith(sec+'.')]
SKOLFORM=[('anpassad gymnasieskola',r'anpassad(?:e)? gymnasieskol\w*'),('anpassad grundskola',r'anpassad(?:e)? grundskol\w*'),
          ('förskoleklass',r'förskoleklass\w*'),('grundskola',r'grundskol\w*'),('specialskola',r'specialskol\w*'),('sameskola',r'sameskol\w*'),
          ('gymnasieskola',r'gymnasieskol\w*'),('kommunal vuxenutbildning',r'kommunal(?:a)? vuxenutbildning\w*|komvux\w*|vuxenutbildning\w*')]
def skolformer(t):
    t=t.lower(); out=[]
    for namn,rx in SKOLFORM:
        if re.search(r'\b(?:'+rx+r')',t): out.append(namn); t=re.sub(r'\b(?:'+rx+r')',' ',t)
    return out
def kopplingsniva(u):
    p=P[u['passage']]
    egna=list(p['hanvisningar_egna'])
    for m in re.finditer(r'(\d{1,2}) kap\.\s*(\d{1,3}(?:\s?[a-z])?)\s*§',p['text']):
        k=(m.group(1),m.group(2).replace(' ',''))
        if k in PAR: egna.append({'typ':'paragraf','varde':f'{k[0]} kap. {k[1]} §','text':m.group(0),'avsnitt':PAR[k]})
    refs=egna if egna else p['hanvisningar_rubrik']; kalla='remissvarets egen text' if egna else 'rubrik i remissvaret som passagen står under'
    fids=[]; kap=set(); grund=[]
    for h in refs:
        if h['typ'] in ('avsnitt','rubrik'):
            ff=f_exact(h['varde']); grund.append(h['text'])
            if ff: fids+=ff
            else: kap.add(h['varde'].split('.')[0])
        elif h['typ']=='paragraf':
            grund.append(h['text'])
            for a in h['avsnitt']:
                ff=f_exact(a); fids+=ff
                if not ff: kap.add(a.split('.')[0])
        elif h['typ']=='kapitel': kap.add(h['varde']); grund.append(h['text'])
    fids=sorted(set(fids),key=lambda x:int(x[1:]))
    if fids:
        return {'niva':'förslag','forslag':fids,'kapitel':sorted({BOX[f]['avsnitt'].split('.')[0] for f in fids},key=int),'flera_forslag_i_hanvisat_avsnitt':len(fids)>1,'grund':grund,'kalla_for_grund':kalla,'tolkning':False}
    if kap:
        return {'niva':'kapitel','forslag':[],'kapitel':sorted(kap,key=int),'grund':grund,'kalla_for_grund':kalla,'tolkning':False,
                'anm':'Hänvisningen pekar på kapitel (eller avsnitt utan förslagsruta); ingen expansion till enskilda förslag.'}
    k=u['koppling']
    if k['typ']=='tolkad' and k['forslag']:
        return {'niva':'tolkad','forslag':k['forslag'],'kapitel':sorted({BOX[f]['avsnitt'].split('.')[0] for f in k['forslag']},key=int),'motivering':k.get('motivering'),'tolkning':True}
    return {'niva':None,'forslag':[],'kapitel':[],'tolkning':False}
def sfs_for(fids):
    out=[]
    for f in fids:
        if f not in SFSF: out.append({'forslag':f,'status':None,'forklaring':'förslaget saknas i sfs-diff-betyg.json'}); continue
        i,sf=SFSF[f]
        if sf['status'] in ('ej lagtext',) or sf['status'].startswith('ej i SFS'):
            out.append({'forslag':f,'status':sf['status'],'kalla':sf['status_kalla']}); continue
        pars=[{'paragraf':x['paragraf'],'sfs':(x.get('beslutad') or {}).get('sfs'),'textlikhet_procent':round(100*(x.get('beslutad') or {}).get('likhet_mot_sou',0),1) if x.get('beslutad') else None,
               'manuell_granskning':x['manuell_granskning'],'diff':f'research/remissanalys/sfs-diff-betyg.json#/forslag/{i}/paragrafer/{j}'} for j,x in enumerate(sf['paragrafer'])]
        if all(p_['sfs'] for p_ in pars):
            out.append({'forslag':f,'status':'i beslutad lag','paragrafer':pars,'kalla':{'text':'Skollag (2010:800) konsoliderad, riksdagens öppna data, hämtad 2026-11-10 (SFS 2026:1242/1243/1245)','url':'https://data.riksdagen.se/dokument/sfs-2010-800.text'}})
        else:
            out.append({'forslag':f,'status':None,'paragrafer':pars,'forklaring':'minst en paragraf saknar beslutad lydelse; se diff'})
    return out
ut=[]
for u in v1['utmaningar']:
    if u['dublett_av']: continue
    k=KOD[u['id']]; assert k['primar'] in TYPER and (k['sekundar'] in TYPER+[None])
    kn=kopplingsniva(u)
    sak=[{'kapitel':c,'rubrik':KAPRUBRIK.get(c),'kalla':{'text':f'SOU 2025:18, innehållsförteckning, kapitel {c}','url':SOU_URL}} for c in kn['kapitel']] or None
    ut.append({'id':u['id'],'avsandare':u['avsandare'],'fokusgrupp':u['fokusgrupp'],'grupp':u['grupp'],
        'citat':u['citat'],'sida':u['sida'],'url':u['url'],'ocr':u['ocr'],'kalla':u['kalla'],'citatkontroll':u['citatkontroll'],
        'utmaningstyp':{'primar':k['primar'],'sekundar':k['sekundar'] if k['sekundar']!=k['primar'] else None,'motivering':k['motivering'],'tolkning':True},
        'koppling':kn,'sakomrade':sak,'skolform':skolformer(u['citat']),
        'sfs':sfs_for(kn['forslag']) if kn['forslag'] else None})
meta={'reform_id':'betyg','version':2,'skapad':'2026-11-10','status':'research — inte publik data','kalla_v1':'research/remissanalys/utmaningar-betyg.json (citat oförändrade)',
 'tolkning':'Två steg innehåller tolkning och är märkta tolkning: true: utmaningstyp (modellkodning genom läsning, gemensam instruktion i taxonomi.md) och koppling.niva="tolkad". Övrigt är mekaniskt härlett.',
 'ingen_bedomning':'Inget fält anger om en utmaning är löst, kvarstår eller tillräckligt bemött.'}
json.dump({'_meta':meta,'utmaningstyper':TYPER,'utmaningar':ut},open(V2+'utmaningar-betyg-v2.json','w'),ensure_ascii=False,indent=1)
# steg 5: avsändarräkning
FG=['kommuner','enskilda_huvudman','skr','almega','ideburna']
def rakna(sel):
    av=sorted({u['avsandare'] for u in sel})
    return {'antal_avsandare':len(av),'antal_passager':len(sel),'per_fokusgrupp':{g:{'antal':len({u['avsandare'] for u in sel if u['fokusgrupp']==g}),'avsandare':sorted({u['avsandare'] for u in sel if u['fokusgrupp']==g})} for g in FG},'avsandare':av}
SAK=sorted({s['rubrik'] for u in ut for s in (u['sakomrade'] or [])})
res={'_meta':{'raknas':'primär utmaningstyp; sakområde = SOU-kapitlets rubrik (en utmaning kopplad till flera kapitel räknas i vart och ett); avsändare räknas en gång per cell',
  'enskilda_huvudman':'0 — de fem enskilda huvudmännens remissvar är spontana yttranden som inte publiceras på regeringen.se'},
  'totalt':rakna(ut),
  'per_utmaningstyp':{t:rakna([u for u in ut if u['utmaningstyp']['primar']==t]) for t in TYPER},
  'per_sakomrade':{s:rakna([u for u in ut if any(x['rubrik']==s for x in (u['sakomrade'] or []))]) for s in SAK},
  'utan_sakomrade':rakna([u for u in ut if not u['sakomrade']]),
  'per_typ_och_sakomrade':{f'{t} × {s}':rakna(sel) for t in TYPER for s in SAK if (sel:=[u for u in ut if u['utmaningstyp']['primar']==t and any(x['rubrik']==s for x in (u['sakomrade'] or []))])}}
json.dump(res,open(V2+'avsandare-betyg.json','w'),ensure_ascii=False,indent=1)
C=collections.Counter
print('utmaningar',len(ut)); print('primär',C(u['utmaningstyp']['primar'] for u in ut)); print('nivå',C(u['koppling']['niva'] for u in ut))
print('kapitel med forslag?',sum(1 for u in ut if u['koppling']['niva']=='kapitel' and u['koppling']['forslag']))
print('skolform',C(s for u in ut for s in u['skolform'])); print('sfs',C(x['status'] for u in ut for x in (u['sfs'] or [])))
print('avsändare per typ',{t:res['per_utmaningstyp'][t]['antal_avsandare'] for t in TYPER})
