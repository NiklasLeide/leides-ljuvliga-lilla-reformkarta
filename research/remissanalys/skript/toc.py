import re,json
P=open('pdf/sou202518-volym-1.txt').read().split('\f')
toc=[]; buf=''
for p in P[:25]:
    for l in p.split('\n'):
        s=l.strip()
        if not s: continue
        m=re.match(r'^(\d{1,2}(?:\.\d{1,2}){0,4})\s+(.*)$',s)
        if m: buf=s
        elif buf: buf+=' '+s
        else: continue
        mm=re.match(r'^(\d{1,2}(?:\.\d{1,2}){0,4})\s+(.*?)\s*\.{3,}\s*(\d{1,4})$',buf)
        if mm: toc.append({'avsnitt':mm.group(1),'rubrik':re.sub(r'\s+',' ',mm.group(2)),'sida':int(mm.group(3))}); buf=''
json.dump(toc,open('sou_toc.json','w'),ensure_ascii=False,indent=1)
print(len(toc)); print([ (t['avsnitt'],t['sida']) for t in toc if t['avsnitt'].startswith(('9.','10.','20.'))][:60])
