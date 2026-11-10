"""Steg 6 (v2): propositionens stycke om utredningens förslag per avsnitt, ordagrant, med kontroll mot PDF-texten."""
import json,re,sys,unicodedata
S,OUT=sys.argv[1],sys.argv[2]
U={'197':'https://www.regeringen.se/contentassets/a37af6932a5f4cf794499eb68a798d63/ett-likvardigt-betygssystem-prop.-202526197.pdf',
   '194':'https://www.regeringen.se/contentassets/42c1e2e4596b4f8682e3d8283b91a138/nya-laroplaner--for-en-stark-kunskapsskola-prop.-202526194.pdf'}
def n(t): return re.sub(r'[\s\-­–]','',unicodedata.normalize('NFC',t))
RAW={k:n(re.sub(r'Prop\. 2025/26:19\d|\n\d{1,3}\n','',open(f'{S}/pdf/prop{k}r.txt').read())) for k in U}
pilot=json.load(open('research/remissanalys/pilot-betyg.json'))
F_PER_AVS={}
for f in pilot['forslag']:
    for r in (f['proposition'] or {}).get('avsnitt',[]): F_PER_AVS.setdefault(r['ref'],[]).append(f['id'])
out=[]
for pr,fil,labels in (('197','prop197_sec.json',['Utredningens förslag','Utredningens bedömning']),('194','prop194_sec.json',['Utredningen om likvärdiga betyg och meritvärdens förslag'])):
    for s in json.load(open(f'{S}/{fil}')):
        if pr=='194' and not any(l in s['delar'] for l in labels): continue
        lab=next((l for l in labels if l in s['delar']),None)
        post={'proposition':f'Prop. 2025/26:{pr}','avsnitt':s['avsnitt'],'rubrik':s['rubrik'],'forslag_i_avsnittet':F_PER_AVS.get(f'{pr}:{s["avsnitt"]}',[])}
        if not lab:
            post.update(text=None,overensstammelse=None,avvikelse_beskriven=None,kalla=None,anm='Stycket saknas i avsnittet.'); out.append(post); continue
        d=s['delar'][lab]; t=d['text']
        m=re.search(r'stämmer (?:också )?(?:i huvudsak |delvis )?överens',t)
        first=re.match(r'(.+?\.)(\s|$)',t)
        rest=t[first.end():].strip() if first else ''
        # ordagrann kontroll: hela stycket (normaliserat) ska finnas i PDF-texten; annars kontroll i delar om 60 tecken
        nt=n(t); ok=nt in RAW[pr]
        chunks=[nt[i:i+60] for i in range(0,len(nt),60)]; miss=[c for c in chunks if c not in RAW[pr]]
        post.update(rubrik_i_propositionen=lab,text=t,overensstammelse=m.group(0) if m else None,avvikelse_beskriven=bool(rest),
            kalla={'text':f"Prop. 2025/26:{pr} s. {', '.join(map(str,d['sidor']))}, avsnitt {s['avsnitt']} ”{lab}”",'url':U[pr]},sida=d['sidor'],
            kontroll={'metod':'automatisk mot pdftotext (blanksteg/bindestreck normaliserade)','hela_stycket':ok,'delar_utan_traff':len(miss),'delar':len(chunks)})
        out.append(post)
json.dump({'_meta':{'beskrivning':'Propositionens stycke "Utredningens förslag" (prop. 194: "Utredningen om likvärdiga betyg och meritvärdens förslag") per avsnitt med regeringens förslags-/bedömningsruta, ordagrant fram till nästa underrubrik.',
  'overensstammelse':'propositionens exakta fras','avvikelse_beskriven':'true om stycket innehåller fler meningar än den inledande om överensstämmelse (mekaniskt)'},'avsnitt':out},open(OUT,'w'),ensure_ascii=False,indent=1)
from collections import Counter
print(len(out),'saknas',sum(1 for o in out if not o['text']),Counter(o['overensstammelse'] for o in out),Counter(o['avvikelse_beskriven'] for o in out))
print('kontroll',[(o['avsnitt'],o['kontroll']) for o in out if o.get('kontroll') and not o['kontroll']['hela_stycket']])
