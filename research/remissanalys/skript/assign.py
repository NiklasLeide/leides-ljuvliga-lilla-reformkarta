import json,re
toc=json.load(open('sou_toc.json')); boxes=json.load(open('sou_boxes.json'))
P={v:open(f'pdf/sou202518-{v}.txt').read().split('\f') for v in ('volym-1','volym-2')}
def norm(s): return re.sub(r'\s+',' ',s)
for b in boxes:
    pg=b['sida']; page=norm(P[b['vol']][b['pdfsida']-1])
    pos=page.find(b['text'][:40])
    cands=[t for t in toc if t['sida']<=pg]
    chosen=None
    for t in reversed(cands):
        if t['sida']<pg: chosen=t; break
        hp=page.find(t['rubrik'][:25])
        if hp!=-1 and (pos==-1 or hp<pos): chosen=t; break
    b['avsnitt']=chosen['avsnitt'] if chosen else None; b['avsnittsrubrik']=chosen['rubrik'] if chosen else None
json.dump(boxes,open('sou_boxes.json','w'),ensure_ascii=False,indent=1)
n=0
for b in boxes:
    if b['typ']!='Förslag': continue
    n+=1; b['id']=f"F{n:02d}"
    print(f"{b['id']} s.{b['sida']} {b['avsnitt']} [{(b['avsnittsrubrik'] or '')[:50]}] :: {b['text'][:600]}")
json.dump(boxes,open('sou_boxes.json','w'),ensure_ascii=False,indent=1)
