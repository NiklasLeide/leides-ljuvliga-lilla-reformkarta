"""Steg 2b: koppling passage -> utredningsförslag (F01–F80 i pilot-betyg.json).
förankrad = remissvaret anger själv avsnitt/rubrik (egen rad eller rubriken passagen står under) eller paragraf (via SOU:ns författningskommentar).
tolkad    = annars: TF-IDF-likhet mellan passage och förslagsrutor (TOLKNING, maskinell). null = ingen likhet över tröskeln."""
import json,re,math,sys,collections
S=sys.argv[1]
P=json.load(open(f'{S}/passager.json'))
boxes=[b for b in json.load(open(f'{S}/sou_boxes.json')) if b['typ']=='Förslag']
paras=json.load(open(f'{S}/sou_paragrafer.json'))
STOP=set('och att det som för med av på är en ett till den de inte om ska kan har vara eller även att detta denna dessa från vid när utan samt där vilket vilka också sina sitt sin dess deras utredningen utredningens förslag förslaget föreslår kommun kommunen kommunens'.split())
def tok(t): return [w for w in re.findall(r'[a-zåäöé]{4,}',t.lower()) if w not in STOP]
docs={b['id']:tok(b['text']+' '+(b['avsnittsrubrik'] or '')) for b in boxes}
df=collections.Counter(w for d in docs.values() for w in set(d)); N=len(docs)
def vec(ws):
    c=collections.Counter(ws); v={w:(1+math.log(n))*math.log((N+1)/(df.get(w,0)+1)) for w,n in c.items()}
    nrm=math.sqrt(sum(x*x for x in v.values())) or 1; return {w:x/nrm for w,x in v.items()}
DV={k:vec(v) for k,v in docs.items()}
def cos(a,b): return sum(x*b.get(w,0) for w,x in a.items())
PAR={(p['kap'],p['par'].replace(' ','')):p['avsnitt'] for p in paras}
def f_for_avsnitt(sec): return [b['id'] for b in boxes if b['avsnitt']==sec or b['avsnitt'].startswith(sec+'.')]
TROSKEL=0.15
for p in P:
    egna=list(p['hanvisningar_egna'])
    # paragrafhänvisningar i remissvaret, t.ex. "16 kap. 29 §"
    for m in re.finditer(r'(\d{1,2}) kap\.\s*(\d{1,3}(?:\s?[a-z])?)\s*§',p['text']):
        k=(m.group(1),m.group(2).replace(' ',''))
        if k in PAR: egna.append({'typ':'paragraf','varde':f'{k[0]} kap. {k[1]} §','text':m.group(0),'avsnitt':PAR[k]})
    fids=set(p['forankrade_forslag'])
    for h in egna:
        if h['typ']=='paragraf':
            for a in h['avsnitt']: fids|=set(f_for_avsnitt(a))
    if fids:
        grund=[h['text'] for h in egna] or [f"rubrik: {p['rubrik']}"]
        p['koppling']={'typ':'förankrad','forslag':sorted(fids,key=lambda x:int(x[1:])),'grund':grund,'kalla_for_grund':'remissvarets egen text' if egna else 'rubrik i remissvaret som passagen står under','tolkning':False}
        continue
    v=vec(tok(p['text'])); sc=sorted(((cos(v,DV[k]),k) for k in DV),reverse=True)
    if sc[0][0]>=TROSKEL:
        top=[k for s,k in sc[:3] if s>=max(TROSKEL,0.85*sc[0][0])]
        p['koppling']={'typ':'tolkad','forslag':top,'grund':[f'TF-IDF-likhet {sc[0][0]:.2f} mot {sc[0][1]}'],'metod':f'cosinuslikhet TF-IDF, tröskel {TROSKEL}, högst 3 förslag inom 85 % av bästa','tolkning':True}
    else:
        p['koppling']={'typ':None,'forslag':[],'grund':[f'högsta likhet {sc[0][0]:.2f} < {TROSKEL}'],'tolkning':False}
json.dump(P,open(f'{S}/passager.json','w'),ensure_ascii=False,indent=1)
print(collections.Counter(p['koppling']['typ'] for p in P))
