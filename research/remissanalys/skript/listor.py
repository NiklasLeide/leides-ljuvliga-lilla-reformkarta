import re,json
d=json.load(open('rem.json'))
d['tioarig']['remisslista_pdf']=[{'namn':'Remissinstanser för En tioårig grundskola, SOU 2021:33','url':'https://www.regeringen.se/contentassets/5787ca62fd6242df94ad7b09833113a0/remissinstanser-for-en-tioarig-grundskola-sou-202133/','sektion':'Remissinstanser:'}]
for k,v in d.items():
    t=open(f'dl/lista/{k}.txt').read()
    names=[]; cur=None
    for line in t.split('\n'):
        m=re.match(r'\s*(\d{1,3})\.\s+(.*\S)\s*$',line)
        if m: names.append(m.group(2)); cur=len(names)-1; continue
        # fortsättningsrad för långa namn
        if cur is not None and line.startswith('                       ') and line.strip() and not re.search(r'Telefon|Fax|Webb|Postadress|Besök|E-post',line):
            pass
    # leta efter fritt formulerade stycken (t.ex. "Remissvaren ska ha kommit in ...")
    v['remisslista']=names
    v['remisslista_meta']={'svar_senast':(re.search(r'senast (?:den )?(\d+ \w+ \d{4})',t) or [None,None])[1],'dnr':(re.search(r'U20\d\d/\d+',t) or [None])[0]}
    print(k,len(names),v['remisslista_meta'], names[:3], names[-2:])
json.dump(d,open('rem.json','w'),ensure_ascii=False,indent=1)
# tioårig: onumrerad lista
t=open('dl/lista/tioarig.txt').read()
body=t[t.find('Remissinstanser')+len('Remissinstanser'):]
end=re.search(r'\n\s*(Remissvaren ska|Svaren bör|Remissvar ska|Regeringskansliet|Myndigheter under)',body)
body=body[:end.start()] if end else body
names=[l.strip() for l in body.split('\n') if l.strip() and not re.search(r'Telefon|Fax:|Webb:|Postadress|Besöksadress|E-post|^\d+ \(\d+\)$|^\d+$|^\d+ \(\d+\)$',l)]
d['tioarig']['remisslista']=names
print('tioarig',len(names),names[-5:])
json.dump(d,open('rem.json','w'),ensure_ascii=False,indent=1)
