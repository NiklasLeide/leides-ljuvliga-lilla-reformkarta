import re,json,sys
def pages(f): return open(f).read().split('\f')
def printed(p,idx):
    lines=[l.strip() for l in p.strip().split('\n') if l.strip()]
    for l in lines[-1:]+lines[:1]:
        if re.fullmatch(r'\d{1,4}',l): return int(l)
    return None
out=[]
for vol in ('volym-1','volym-2'):
    P=pages(f'pdf/sou202518-{vol}.txt')
    sec=None; sectitle=None
    for i,p in enumerate(P):
        lines=p.split('\n')
        for j,l in enumerate(lines):
            m=re.match(r'^\s{0,25}(\d{1,2}(?:\.\d{1,2}){1,4})\s{1,6}([A-ZÅÄÖ].{3,90})$',l)
            if m and not re.search(r'\.{4,}|\s\d+$',l): sec=m.group(1); sectitle=m.group(2).strip()
            mb=re.match(r'^\s*(Förslag|Bedömning):\s*(.*)$',l)
            if mb:
                ind=len(l)-len(l.lstrip())
                txt=[mb.group(2).strip()]; k=j+1; blank=0
                pp=i; LL=lines
                while True:
                    if k>=len(LL):
                        pp+=1
                        if pp>=len(P): break
                        LL=P[pp].split('\n'); k=0; continue
                    s=LL[k]
                    if not s.strip():
                        blank+=1
                        if blank>=1 and len(txt)>1: break
                        k+=1; continue
                    if re.match(r'^\s*(Förslag|Bedömning):',s): break
                    if re.match(r'^\s*SOU 2025:18\s*$',s.strip()) or re.match(r'^\s*\d{1,4}\s*$',s): k+=1; continue
                    blank=0; txt.append(re.sub(r'\s{3,}.*$','',s.strip()) if ind<5 else s.strip()); k+=1
                t=' '.join(txt); t=re.sub(r'(\w)- (?=[a-zåäö])',r'\1',t)
                out.append({'vol':vol,'pdfsida':i+1,'sida':printed(p,i),'avsnitt':sec,'avsnittsrubrik':sectitle,'typ':mb.group(1),'text':t})
json.dump(out,open('sou_boxes.json','w'),ensure_ascii=False,indent=1)
print(len(out), sum(1 for x in out if x['typ']=='Förslag'))
for x in out:
    if x['typ']=='Förslag': print(x['vol'][-1],x['sida'],x['avsnitt'],'|',x['text'][:110])
