import re,json,sys
sys.path.insert(0,'bin')
from klass import kategori,N
ALIAS={'Skolverket':'Statens skolverk','Skolinspektionen':'Statens skolinspektion','SKR':'Sveriges Kommuner och Regioner',
 'SPSM':'Specialpedagogiska skolmyndigheten','IFAU':'Institutet för arbetsmarknads- och utbildningspolitisk utvärdering',
 'UHR':'Universitets- och högskolerådet','JO':'Riksdagens ombudsmän (JO)','LO':'Landsorganisationen i Sverige (LO)','Saco':'Sveriges akademikers centralorganisation (Saco)',
 'CSN':'Centrala studiestödsnämnden','UKÄ':'Universitetskanslersämbetet','DO':'Diskrimineringsombudsmannen','GIH':'Gymnastik- och idrottshögskolan',
 'MYH':'Myndigheten för yrkeshögskolan','IMY':'Integritetsskyddsmyndigheten','SiS':'Statens institutionsstyrelse'}
GENERISK=re.compile(r'\b((?:Så gott som alla|En majoritet av|Majoriteten av|De flesta|Flera|Några|Många|Ett fåtal|Ett par|Enstaka|Ett antal|Ett flertal|Övriga|Ett stort antal|Andra)[^.,;:]{0,30}?(?:remissinstanser(?:na)?|kommuner(?:na)?|huvudmän(?:nen)?|myndigheter(?:na)?|organisationer(?:na)?|universitet|lärosäten))',re.I)
def namngivna(text, kanda):
    """kanda: lista av namn i remissförteckningen. Returnerar ordagranna träffar i ordning."""
    t=text
    hits=[]  # (pos, verbatim, resolved)
    # 1) samordnade kommunnamn: "Falu, Motala och Söderhamns kommuner"
    for m in re.finditer(r'((?:[A-ZÅÄÖ][\wåäöé-]+(?:, | och | samt ))+[A-ZÅÄÖ][\wåäöé-]+) kommuner',t):
        names=re.split(r', | och | samt ',m.group(1))
        res=[]
        for n in names:
            cand=n+' kommun'
            res.append(next((k for k in kanda if N(k).lower()==cand.lower() or N(k).lower()==(n+'s kommun').lower()),cand))
        hits.append((m.start(),m.group(0),res))
    taken=[(h[0],h[0]+len(h[1])) for h in hits]
    def free(a,b): return all(b<=x or a>=y for x,y in taken)
    # 2) kända namn ur förteckningen (längst först)
    for k in sorted(set(kanda),key=len,reverse=True):
        kk=re.escape(N(k)).replace(r'\ ',r'\s+')
        for m in re.finditer(r'(?<![\wåäö])'+kk+r'(?![\wåäö])',t):
            if free(m.start(),m.end()):
                hits.append((m.start(),m.group(0),[N(k)])); taken.append((m.start(),m.end()))
    # 3) enstaka "X kommun" som inte fångats
    for m in re.finditer(r'[A-ZÅÄÖ][\wåäöé-]+ kommun(?!er)',t):
        if free(m.start(),m.end()):
            hits.append((m.start(),m.group(0),[m.group(0)])); taken.append((m.start(),m.end()))
    # 4) förkortningar/kortformer
    for a,full in ALIAS.items():
        for m in re.finditer(r'(?<![\wåäö(])'+re.escape(a)+r'(?![\wåäö)])',t):
            if free(m.start(),m.end()):
                hits.append((m.start(),m.group(0),[full])); taken.append((m.start(),m.end()))
    hits.sort()
    out=[]; seen=set()
    for pos,verb,res in hits:
        for r in res:
            if r in seen: continue
            seen.add(r)
            out.append({'namn_i_texten':re.sub(r'\s+',' ',verb),'namn_i_forteckningen':r if any(N(r)==N(k) for k in kanda) else None,'kategori':kategori(r)})
    gen=[re.sub(r'\s+',' ',m.group(1)) for m in GENERISK.finditer(t)]
    return out,gen
