"""Bygger utmaningar-betyg.json (steg 2, 3, 5) av passager, öppen kodning, kategorier, koppling och namnträffar i propositionens skäl."""
import json,re,sys,difflib,collections,unicodedata
S=sys.argv[1]; OUT=sys.argv[2]
sys.path.insert(0,S+'/bin')
from kategorier import KATEGORIER,kategori_for
K=json.load(open(f'{S}/korpus.json')); P={p['id']:p for p in json.load(open(f'{S}/passager.json'))}
R=json.load(open(f'{S}/kodning/alla.json'))
KT={x['uid']:x for i in (1,2) for x in json.load(open(f'{S}/kodning/koppling{i}.json'))}
BEM=json.load(open(f'{S}/bemotande_traffar.json'))
pilot=json.load(open('research/remissanalys/pilot-betyg.json'))
FPROP={f['id']:[r['ref'] for r in (f['proposition'] or {}).get('avsnitt',[])] for f in pilot['forslag']}
GRUPP={'kommuner':'huvudman','enskilda_huvudman':'huvudman','skr':'huvudmannaorganisation','almega':'huvudmannaorganisation','ideburna':'huvudmannaorganisation'}
def n(t): return re.sub(r'[\s\-­]','',unicodedata.normalize('NFC',t))
# citatkontroll mot källtext (pdftotext-sida eller OCR-text)
SID={(d['id'],i+1):n(t) for d in K['korpus'] for i,t in enumerate(d['text_per_sida'])}
# OCR-citat på sidorna 1–2 i Norrköpings remissvar granskade manuellt mot sidbilden (2026-11-10)
MANUELL_OCR={'U287','U288','U289','U290','U291','U292','U293','U294','U295','U296'}
ut=[]
for x in R:
    p=P[x['id']]
    kp=p['koppling']
    if kp['typ']=='förankrad':
        koppling={'typ':'förankrad','forslag':kp['forslag'],'grund':kp['grund'],'kalla_for_grund':kp.get('kalla_for_grund'),'tolkning':False}
    else:
        k=KT[x['uid']]
        koppling={'typ':'tolkad' if k['forslag'] else None,'forslag':k['forslag'] or [],'motivering':k['motivering'],'metod':'modellkodning mot förslagsrutorna F01–F80 (konservativ; null när ingen enskild rimlig koppling)','tolkning':bool(k['forslag'])}
    auto=n(x['citat']) in SID[(p['dok'],p['sida'])]
    # bemötande: namnförekomster i skäl
    avs=sorted({a for f in koppling['forslag'] for a in FPROP.get(f,[])})
    alla=[b for b in BEM if b['avsandare']==p['avsandare']]
    i_avs=[b for b in alla if b['avsnitt'] in avs]
    if avs:
        bem={'bemott_namngiven':bool(i_avs),'sokt_i':[f'skäl i prop.-avsnitt {a}' for a in avs],'traffar':[{k_:b[k_] for k_ in ('namn_i_texten','citat','sida','kalla','avsnitt')} for b in i_avs]}
    else:
        bem={'bemott_namngiven':None,'forklaring':'Utmaningen saknar koppling till ett förslag som propositionen behandlar i ett avsnitt; ingen avsnittsvis sökning möjlig.','sokt_i':[]}
    bem['namngiven_i_ovriga_skal']=[{k_:b[k_] for k_ in ('namn_i_texten','citat','sida','kalla','avsnitt')} for b in alla if b not in i_avs]
    ut.append({'id':x['uid'],'passage':x['id'],'avsandare':p['avsandare'],'fokusgrupp':p['kategori_avsandare'],'grupp':GRUPP[p['kategori_avsandare']],
        'citat':x['citat'],'sida':p['sida'],'url':p['url'],'ocr':p['ocr'],
        'kalla':{'text':f"Remissvar från {p['avsandare']} (U2025/00401), s. {p['sida']}"+(' (OCR)' if p['ocr'] else ''),'url':p['url']},
        'citatkontroll':{'metod':('automatisk mot OCR-text + manuell mot sidbild' if x['uid'] in MANUELL_OCR else ('automatisk mot OCR-text' if p['ocr'] else 'automatisk mot pdftotext-sidtext')) if auto else 'manuell','ok':True if auto else None},
        'oppen_kod':x['oppen_kod'],'kodarens_beskrivning':x['beskrivning'],
        'kategori':kategori_for(x['oppen_kod']),'tolkning':True,
        'koppling':koppling,'bemotande':bem})
# dubbletter inom samma avsändare (t.ex. Stockholms tjänsteutlåtanden som upprepar varandra)
for i,a in enumerate(ut):
    for b in ut[:i]:
        if a['avsandare']==b['avsandare'] and difflib.SequenceMatcher(None,a['citat'],b['citat']).ratio()>=0.9:
            a['dublett_av']=b['id']; break
    a.setdefault('dublett_av',None)
saknade=[{'avsandare':s['namn'],'fokusgrupp':s['kategori'],'grupp':GRUPP[s['kategori']],'svarat_som':'spontant yttrande','skal':'Spontana yttranden publiceras inte på regeringen.se ("Övriga yttranden finns tillgängliga i departementet"); inte inhämtade enligt spikens avgränsning.','kalla':{'text':'Prop. 2025/26:197 bilaga 3 (förteckning över remissinstanserna)','url':'https://www.regeringen.se/contentassets/a37af6932a5f4cf794499eb68a798d63/ett-likvardigt-betygssystem-prop.-202526197.pdf'}} for s in K['saknade']]
meta={'reform_id':'betyg','skapad':'2026-11-10','status':'research — inte publik data',
 'kedja':{'sou':'SOU 2025:18','dnr':'U2025/00401','proposition':['Prop. 2025/26:197','Prop. 2025/26:194 (del)'],'bet':'2025/26:UbU26','rskr':'2025/26:335','beslut':'2026-06-09'},
 'korpus':{'publicerade_remissvar':len(K['korpus']),'ocr':[d['avsandare'] for d in K['korpus'] if d['ocr']],'passager':len(P),'saknade_remissvar':len(saknade)},
 'tolkning':'Endast två steg innehåller tolkning och är märkta: (a) att en passage beskriver en utmaning och dess kategori (tolkning: true på varje utmaning; öppen kodning gjord av modell, kategorier = ordnade nyckelordsregler över öppna koder, se kategorier[].regel) och (b) koppling.typ="tolkad". Allt annat är mekaniskt härlett.',
 'ingen_bedomning':'Inget fält anger om en utmaning är löst, kvarstår eller tillräckligt bemött. bemott_namngiven anger bara om avsändarens namn förekommer i propositionens skäl i det kopplade avsnittet.',
 'dubbletter':'dublett_av sätts när samma avsändare har ett citat med ≥ 90 % likhet med ett tidigare citat; dubbletter räknas inte i rapportens antal.'}
kat=[{'id':k,'namn':nm,'definition':d,'regel':rx} for k,nm,d,rx in KATEGORIER]
json.dump({'_meta':meta,'kategorier':kat,'utmaningar':ut,'saknade_remissvar':saknade},open(OUT,'w'),ensure_ascii=False,indent=1)
c=collections.Counter
uu=[u for u in ut if not u['dublett_av']]
print('utmaningar',len(ut),'ej dubblett',len(uu))
print('kategori',c(u['kategori'] for u in uu)); print('grupp',c(u['fokusgrupp'] for u in uu))
print('koppling',c(u['koppling']['typ'] for u in uu)); print('citat auto',c(u['citatkontroll']['metod'] for u in ut))
print('bemött',c(u['bemotande']['bemott_namngiven'] for u in uu))
