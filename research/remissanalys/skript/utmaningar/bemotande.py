"""Steg 5: förekomster av fokusgruppernas namn i propositionernas skäl (prop. 197 alla avsnitt; prop. 194 avsnitt 6.7–6.8).
Ren namnsökning, ingen bedömning av innehållet."""
import json,re,sys
sys.path.insert(0,sys.argv[1]+'/bin')
from namn import namngivna
from pagefind import find_page
S=sys.argv[1]
senders=sorted({p['avsandare'] for p in json.load(open(f'{S}/passager.json'))})
U={'197':'https://www.regeringen.se/contentassets/a37af6932a5f4cf794499eb68a798d63/ett-likvardigt-betygssystem-prop.-202526197.pdf',
   '194':'https://www.regeringen.se/contentassets/42c1e2e4596b4f8682e3d8283b91a138/nya-laroplaner--for-en-stark-kunskapsskola-prop.-202526194.pdf'}
traffar=[]
for pr,fil in (('197','prop197_sec.json'),('194','prop194_sec.json')):
    for s in json.load(open(f'{S}/{fil}')):
        if pr=='194' and s['avsnitt'] not in ('6.7','6.8'): continue
        for lab,d in s['delar'].items():
            if not lab.startswith('Skälen'): continue
            t=d['text']
            hits,_=namngivna(t,senders)
            for h in hits:
                if h['namn_i_forteckningen'] not in senders: continue
                # meningen som innehåller namnet (ordagrant ur extraherad text)
                i=t.find(h['namn_i_texten'])
                a=max(t.rfind('. ',0,i)+2,0) if t.rfind('. ',0,i)>=0 else 0
                b=t.find('. ',i); b=len(t) if b<0 else b+1
                mening=t[a:b].strip()
                sida=find_page(f'{S}/pdf/prop{pr}.txt',mening[:70]) or find_page(f'{S}/pdf/prop{pr}.txt',h['namn_i_texten'])
                traffar.append({'avsandare':h['namn_i_forteckningen'],'namn_i_texten':h['namn_i_texten'],'proposition':'Prop. 2025/26:'+pr,'avsnitt':f"{pr}:{s['avsnitt']}",
                    'citat':mening,'kalla':{'text':f"Prop. 2025/26:{pr} s. {sida}, avsnitt {s['avsnitt']} ”{lab}”",'url':U[pr]},'sida':sida})
json.dump(traffar,open(f'{S}/bemotande_traffar.json','w'),ensure_ascii=False,indent=1)
from collections import Counter
print(len(traffar),Counter(t['avsandare'] for t in traffar).most_common())
