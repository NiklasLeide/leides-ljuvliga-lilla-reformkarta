"""Steg 2a: segmentera remissvar i passager och hitta remissvarets egna hänvisningar (förankrad koppling)."""
import json,re,sys
S=sys.argv[1]
K=json.load(open(f'{S}/korpus.json'))
toc=json.load(open(f'{S}/sou_toc.json'))
boxes=[b for b in json.load(open(f'{S}/sou_boxes.json')) if b['typ']=='Förslag']
TOC={t['avsnitt']:t['rubrik'] for t in toc if 9<=int(t['avsnitt'].split('.')[0])<=20}
def norm(s): return re.sub(r'\s+',' ',s.replace('­','')).strip()
def low(s): return re.sub(r'[^a-zåäöé0-9 ]','',norm(s).lower())
RUBRIK={low(v):k for k,v in TOC.items() if len(v)>=12}
def f_for(sec):
    if '.' not in sec: return [b['id'] for b in boxes if b['avsnitt'].split('.')[0]==sec]
    ids=[b['id'] for b in boxes if b['avsnitt']==sec or b['avsnitt'].startswith(sec+'.')]
    if not ids and '.' in sec:  # förälder
        par=sec.rsplit('.',1)[0]; ids=[b['id'] for b in boxes if b['avsnitt']==par]
    return ids
SECRX=re.compile(r'(?<![\d.,§:/])(?:avsnitt(?:en)?|kapitel|kap\.?)?\s*(\d{1,2}(?:\.\d{1,2}){1,3})(?![\d,]|\s*§|\s*kap)',re.I)
CHAPRX=re.compile(r'\b(?:kapitel|kap\.)\s+((?:9|1\d|20)(?:(?:,\s*|\s+och\s+)(?:9|1\d|20))*)\b(?!\s*(?:§|kap|\.\d))',re.I)
def hanvisningar(t):
    h=[]
    for m in SECRX.finditer(t):
        sec=m.group(1)
        if sec in TOC: h.append({'typ':'avsnitt','varde':sec,'text':norm(m.group(0))})
    for m in CHAPRX.finditer(t):
        for c in re.findall(r'\d+',m.group(1)): h.append({'typ':'kapitel','varde':c,'text':norm(m.group(0))})
    lt=low(t)
    for r,sec in RUBRIK.items():
        if r and r in lt and len(lt)<len(r)+40:  # rubrikrad = SOU-rubrik
            h.append({'typ':'rubrik','varde':sec,'text':norm(t)[:120]})
    return h
def is_heading(t):
    t=norm(t); return 0<len(t)<130 and not re.search(r'[.:;]\s*$',t) and not re.search(r'\b(och|att|som|för|med|är)$',t)
passager=[]
import collections
HEADSPLIT=re.compile(r'(?<=[.!?”"\)])\s+(?=(?:Kapitel\s+\d{1,2}\b|\d{1,2}(?:\.\d{1,2}){1,3}\s+[A-ZÅÄÖ]))')
def split_heading(t):
    """'13.3 Meritvärdering i komvux på gymnasial nivå Utifrån …' -> (rubrik, brödtext) när rubriken känns igen i SOU:ns innehållsförteckning."""
    m=re.match(r'(?:\d+\(\d+\)\s*)?(?:Kapitel\s+\d{1,2}[:.]?\s*[^.]*?\s+)?(\d{1,2}(?:\.\d{1,2}){1,3})\s+(.*)$',t)
    if m and m.group(1) in TOC:
        title=TOC[m.group(1)]; rest=m.group(2)
        if low(rest).startswith(low(title)[:max(10,len(low(title))-3)]):
            # hitta slutet på titeln i originaltexten (ord för ord)
            n=len(title.split()); words=rest.split()
            return t[:len(t)-len(' '.join(words[n:]))].strip() if words[n:] else t, ' '.join(words[n:])
        return None,None
    m=re.match(r'Kapitel\s+(\d{1,2})\b',t)
    return None,None
for d in K['korpus']:
    # block som upprepas på flera sidor i samma dokument = sidhuvud/sidfot
    allblocks=[norm(re.sub(r'(\w)-\n(\w)',r'\1\2',bl).replace('\n',' ')) for pg in d['text_per_sida'] for bl in re.split(r'\n\s*\n',pg)]
    rep={b for b,c in collections.Counter(re.sub(r'\d+','#',x) for x in allblocks).items() if c>=3 and len(b)<200}
    rub=None; rub_h=[]; n=0
    for si,page in enumerate(d['text_per_sida'],start=1):
        for bl in re.split(r'\n\s*\n',page.replace('\r','')):
            t0=norm(re.sub(r'(\w)-\n(\w)',r'\1\2',bl).replace('\n',' '))
            if len(t0)<3 or re.fullmatch(r'[\d\s()/]+',t0) or re.sub(r'\d+','#',t0) in rep: continue
            for t in HEADSPLIT.split(t0):
                h_t,body=split_heading(t)
                if h_t:
                    rub=h_t; rub_h=hanvisningar(h_t)
                    if not body or len(body)<25: continue
                    t=body
                h=hanvisningar(t)
                if is_heading(t):
                    rub=t; rub_h=h
                    if len(t)<25: continue
                n+=1
                egna=h; arvda=[] if h else rub_h
                secs=[x['varde'] for x in egna+arvda if x['typ'] in ('avsnitt','rubrik','kapitel')]
                fids=sorted({f for s_ in secs for f in f_for(s_)}, key=lambda x:int(x[1:]))
                passager.append({'id':f"{d['id']}#{n}",'dok':d['id'],'avsandare':d['avsandare'],'kategori_avsandare':d['kategori'],'url':d['url'],'sida':si,'ocr':d['ocr'],
                    'text':t,'rubrik':rub,'hanvisningar_egna':egna,'hanvisningar_rubrik':arvda,'forankrade_forslag':fids})
json.dump(passager,open(f'{S}/passager.json','w'),ensure_ascii=False,indent=1)
print('passager',len(passager),'tecken',sum(len(p['text']) for p in passager))
print('med egen/rubrik-hänvisning',sum(1 for p in passager if p['hanvisningar_egna'] or p['hanvisningar_rubrik']),'med F',sum(1 for p in passager if p['forankrade_forslag']))
c=collections.Counter(p['dok'] for p in passager); print(c.most_common(6))
