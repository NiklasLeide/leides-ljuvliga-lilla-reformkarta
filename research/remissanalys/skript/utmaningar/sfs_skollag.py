"""Skollagen (2010:800) i konsoliderad lydelse från riksdagens öppna data (Regeringskansliets SFS-databas):
paragrafversioner inkl. framtida lydelser ('/Träder i kraft I:ÅÅÅÅ-MM-DD/')."""
import re,json,sys
S=sys.argv[1]
L=open(f'{S}/sfs/skollag.txt',encoding='utf-8').read().split('\n')
end=next((i for i,l in enumerate(L) if l.strip()=='Övergångsbestämmelser'),len(L))
L=L[:end]
meta={'andrad_tom':next((l.split(':',1)[1].strip() for l in L[:12] if l.startswith('Ändrad:')),None)}
vers=[]; kap=None; cur=None; prev_blank=True
for l in L:
    s=l.rstrip()
    if not s.strip(): prev_blank=True
    else:
        mk=re.match(r'^(\d+ (?:[a-z] )?kap\.)\s+(\S.*)$',s)
        mp=re.match(r'^(\d+(?: [a-z])?) §(?:\s+/(Träder i kraft I|Upphör att gälla U):(\d{4}-\d{2}-\d{2})/)?\s*(.*)$',s)
        if prev_blank and mk and not s.endswith(('.',',')) and not re.search(r'§',mk.group(2)):
            kap=mk.group(1).replace(' kap.','').replace(' ',''); cur=None
        elif prev_blank and mp and kap:
            cur={'kap':kap,'par':mp.group(1).replace(' ',''),'ikraft':mp.group(3) if mp.group(2) and mp.group(2).startswith('Träder') else None,
                 'upphor':mp.group(3) if mp.group(2) and mp.group(2).startswith('Upphör') else None,'rader':[mp.group(4)] if mp.group(4) else []}
            vers.append(cur)
        elif cur is not None: cur['rader'].append(s.strip())
        prev_blank=False
for v in vers:
    t=re.sub(r'\s+',' ',' '.join(v.pop('rader'))).strip()
    m=list(re.finditer(r'(Lag|Förordning) \((\d{4}:\d+)\)\.',t))
    if m: v['lag']=m[-1].group(2); t=t[:m[-1].start()].strip()
    else: v['lag']=None
    v['text']=t
json.dump({'meta':meta,'versioner':vers},open(f'{S}/sfs_skollag.json','w'),ensure_ascii=False,indent=1)
from collections import Counter
print(meta,len(vers),Counter(v['lag'] for v in vers if v['lag'] and v['lag'].startswith('2026:124')))
for v in vers:
    if v['kap']=='11' and v['par'] in ('20','20a'): print(v)
