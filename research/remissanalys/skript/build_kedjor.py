import json,sys,re,unicodedata
sys.path.insert(0,'bin')
from klass import kategori,N,OSAKER,GRUPP
from pagefind import find_page
rem=json.load(open('rem.json')); bil=json.load(open('bilagor.json')); pdfc=json.load(open('pdfcheck.json'))
RG='https://www.regeringen.se'
R={
 'laroplaner':dict(brief='Kunskap för alla',reform_id='laroplaner',utr_id='utr-laroplan',
   sou='SOU 2025:19',sou_titel='Kunskap för alla – nya läroplaner med fokus på undervisning och lärande',sou_url=RG+'/rattsliga-dokument/statens-offentliga-utredningar/2025/02/sou-202519/',
   prop='Prop. 2025/26:194',prop_titel='Nya läroplaner – för en stark kunskapsskola',prop_url=RG+'/rattsliga-dokument/proposition/2026/03/prop.-202526194',prop_rd='HD03194',propfil='194',
   bet='2025/26:UbU23',bet_id='HD01UbU23',rskr='2025/26:327',rskr_id='HD0K327',beslut='2026-06-03',
   matchning='Entydig: briefens namn = titeln på SOU 2025:19, kopplad till reforms.json "laroplaner" via utredningar.json utr-laroplan (prop "Prop. 2025/26:194").',
   ovrigt='Delar av SOU 2025:19 behandlas även i prop. 2025/26:195 (avsnitt 4.2) och prop. 2025/26:196 (bilaga 6).'),
 'betyg':dict(brief='Betygsuppdraget',reform_id='betyg',utr_id='utr-betyg',
   sou='SOU 2025:18',sou_titel='Ett likvärdigt betygssystem',sou_url=RG+'/rattsliga-dokument/statens-offentliga-utredningar/2025/02/sou-202518/',
   prop='Prop. 2025/26:197',prop_titel='Ett likvärdigt betygssystem',prop_url=RG+'/rattsliga-dokument/proposition/2026/03/prop.-202526197',prop_rd='HD03197',propfil='197',
   bet='2025/26:UbU26',bet_id='HD01UbU26',rskr='2025/26:335',rskr_id='HD0K335',beslut='2026-06-09',
   matchning='EJ ENTYDIG PÅ NAMN: "Betygsuppdraget" förekommer inte som namn i reforms.json eller utredningar.json. Matchad på sakinnehåll till "betyg" (Betygssystem 1–10, Prop. 2025/26:197, utr-betyg / SOU 2025:18 "Ett likvärdigt betygssystem"). Bekräfta att detta avses.',
   ovrigt='Delar av SOU 2025:18 (avsnitt 9.3 och 9.4) behandlas i prop. 2025/26:194; prop. 2025/26:197 behandlar "alla lagförslag i betänkandet, utom de som lämnas i avsnitt 9.3.7 och 9.4.2 och de lagförslag i avsnitt 9.4.3 som rör annat än lovskola".'),
 'stod':dict(brief='Förbättrat stöd',reform_id='stod',utr_id='utr-elevhalsa',
   sou='SOU 2025:44',sou_titel='Förbättrat stöd i skolan',sou_url=RG+'/rattsliga-dokument/statens-offentliga-utredningar/2025/04/sou-202544/',
   prop='Prop. 2025/26:195',prop_titel='Förbättrat stöd i skolan',prop_url=RG+'/rattsliga-dokument/proposition/2026/03/prop.-202526195',prop_rd='HD03195',propfil='195',
   bet='2025/26:UbU24',bet_id='HD01UbU24',rskr='2025/26:328',rskr_id='HD0K328',beslut='2026-06-03',
   matchning='Entydig: reforms.json "stod" (Förbättrat stöd, Prop. 2025/26:195), utredningar.json utr-elevhalsa (delbetänkande SOU 2025:44).',
   ovrigt='SOU 2025:44 är ett delbetänkande; slutbetänkandet SOU 2025:113 bereds (enligt utredningar.json).'),
 'spraklig':dict(brief='På språklig grund',reform_id=None,utr_id='utr-grundlaggande-svenska',
   sou='SOU 2025:9',sou_titel='På språklig grund',sou_url=RG+'/rattsliga-dokument/statens-offentliga-utredningar/2025/01/sou-20259/',
   prop='Prop. 2025/26:194',prop_titel='Nya läroplaner – för en stark kunskapsskola',prop_url=RG+'/rattsliga-dokument/proposition/2026/03/prop.-202526194',prop_rd='HD03194',propfil='194',
   bet='2025/26:UbU23',bet_id='HD01UbU23',rskr='2025/26:327',rskr_id='HD0K327',beslut='2026-06-03',
   matchning='INGEN EGEN POST I reforms.json. Finns i utredningar.json som utr-grundlaggande-svenska (SOU 2025:9, kopplad_reform null, prop null). Propositionskedjan finns ändå: prop. 2025/26:194 behandlar betänkandets avsnitt 8 (grundläggande svenska som andraspråk). "Förbättrat stöd" (3) och "På språklig grund" (4) är alltså TVÅ olika utredningar (SOU 2025:44 resp. SOU 2025:9) och hamnar i två olika propositioner (195 resp. 194). Obs: utredningar.json saknar prop-kopplingen för SOU 2025:9.',
   ovrigt='Endast delar av SOU 2025:9 (avsnitt 8) behandlas i propositionen; kedjan till rskr gäller bara den delen.'),
 'studiero':dict(brief='Trygghet och studiero',reform_id='studiero',utr_id='utr-studiero',
   sou='SOU 2025:8',sou_titel='Bättre förutsättningar för trygghet och studiero i skolan',sou_url=RG+'/rattsliga-dokument/statens-offentliga-utredningar/2025/01/sou-20258/',
   prop='Prop. 2025/26:193',prop_titel='Bättre förutsättningar för trygghet och studiero i skolan',prop_url=RG+'/rattsliga-dokument/proposition/2026/03/prop.-202526193',prop_rd='HD03193',propfil='193',
   bet='2025/26:UbU22',bet_id='HD01UbU22',rskr='2025/26:308',rskr_id='HD0K308',beslut='2026-06-03',
   matchning='Entydig: reforms.json "studiero" (Prop. 2025/26:193), utr-studiero (SOU 2025:8).',
   ovrigt='Prop. 2025/26:193 behandlar även Ds 2025:9 (mobilförbud, egen remiss U2025/00797). SOU 2025:8 avsnitt 3.2 behandlas i prop. 2025/26:194.'),
 'tid':dict(brief='Tid för undervisningsuppdraget',reform_id='tid',utr_id='utr-tid',
   sou='SOU 2025:26',sou_titel='Tid för undervisningsuppdraget – åtgärder för god undervisning och läraryrkenas attraktivitet',sou_url=RG+'/rattsliga-dokument/statens-offentliga-utredningar/2025/03/sou-202526/',
   prop='Prop. 2025/26:196',prop_titel='Tid för undervisningsuppdraget',prop_url=RG+'/rattsliga-dokument/proposition/2026/03/prop.-202526196',prop_rd='HD03196',propfil='196',
   bet='2025/26:UbU25',bet_id='HD01UbU25',rskr='2025/26:332',rskr_id='HD0K332',beslut='2026-06-09',
   matchning='Entydig: reforms.json "tid" (Reglerad undervisningstid, Prop. 2025/26:196), utr-tid (SOU 2025:26).',ovrigt=None),
 'tioarig':dict(brief='Tioårig grundskola',reform_id='tioarig',utr_id=None,
   sou='SOU 2021:33',sou_titel='En tioårig grundskola – Införandet av en ny årskurs 1 i grundskolan, grundsärskolan, specialskolan och sameskolan',sou_url=RG+'/rattsliga-dokument/statens-offentliga-utredningar/2021/05/sou-202133/',
   prop='Prop. 2024/25:143',prop_titel='En tioårig grundskola',prop_url=RG+'/rattsliga-dokument/proposition/2025/03/prop.-202425143',prop_rd='HC03143',propfil='143',
   bet='2024/25:UbU17',bet_id='HC01UbU17',rskr='2024/25:289',rskr_id='HC0K289',beslut='2025-06-18',
   matchning='Entydig: reforms.json "tioarig" (Prop. 2024/25:143). Ingen post i utredningar.json (SOU 2021:33 äldre än utredningsvyn).',
   ovrigt='Remissen är från 2021; remisslistan använder delvis andra organisationsnamn (t.ex. "Friskolornas riksförbund", "Lärarförbundet", "Sveriges Skolledarförbund").'),
}
ORDER=['laroplaner','betyg','stod','spraklig','studiero','tid','tioarig']
KATS=['kommuner','enskilda_huvudman','skr','almega','ideburna','regioner','myndigheter','ovriga_organisationer','ovriga']
def low(s): return N(s).lower().replace('–','-')
ALIAS={'göteborg kommun':'göteborgs kommun'}
def key(s):
    k=re.sub(r'\s+',' ',low(s)).strip(' .'); k=re.sub(r'\.pdf$','',k); return ALIAS.get(k,k)
FOK={'skr':('Sveriges Kommuner och Regioner',lambda n: key(n)=='sveriges kommuner och regioner'),
     'almega':('Almega',lambda n: key(n).startswith('almega')),
     'ideburna':('Idéburna skolors riksförbund',lambda n: key(n)=='idéburna skolors riksförbund')}
out={'_meta':{
  'beskrivning':'Del A i spiken "Remissvar mot beslut": kedja utredningsbetänkande → remiss → proposition → utskottsbetänkande → riksdagsskrivelse för sju reformer, med remissvar räknade per kategori.',
  'skapad':'2026-11-10','status':'research — inte publik data',
  'kategorier':{'huvudman':['kommuner','enskilda_huvudman'],'huvudmannaorganisation':['skr','almega','ideburna'],'ovrigt':['regioner','myndigheter','ovriga_organisationer','ovriga']},
  'kalla_for_antal':'Propositionens bilaga "Förteckning över remissinstanserna" (vem som yttrat sig efter remiss, spontana yttranden, vem som avstått/inte svarat). Regeringen.se-remissidan publicerar bara svar från inbjudna remissinstanser ("Övriga yttranden finns tillgängliga i departementet") och även avstå-svar, så sidans antal PDF:er är inte antalet yttranden.',
  'klassning':'Kommuner, regioner och SKR/Almega/Idéburna klassas på namnet i källan. Myndigheter och enskilda huvudmän klassas på namnet mot en manuell lista (scripts i research-underlaget) — det är EXTERN KUNSKAP, inte källtext, och ska verifieras (se RAPPORT.md). Kommunalförbund klassas som övriga organisationer.',
  'status_fokusorganisation':{'svarat':'har yttrat sig enligt propositionens förteckning (som remissinstans eller spontant — se pa_remisslistan)','på remisslistan men ej svarat':'på remisslistan och i propositionens lista över dem som avstått eller inte svarat','ej på remisslistan':'finns inte på remisslistan och har inte yttrat sig enligt förteckningen'},
  'riksdagsbeslut':'Beslut = rskr. Kontrollerat i riksdagens dokumentstatus för utskottsbetänkandet: aktivitet BES med status "inträffat" och referens till rskr.'},
 'reformer':[]}
for k in ORDER:
    r=R[k]; rv=rem[k]; b=bil[k]
    pf=f"pdf/prop{r['propfil']}.txt"
    bilaga_sida=b['pdfsidor'][0]
    bil_kalla={'text':f"{r['prop']}, bilaga \"Förteckning över remissinstanserna ({r['sou']})\", s. {bilaga_sida}–{b['pdfsidor'][-1]}",'url':r['prop_url']}
    lista=[N(x) for x in rv['remisslista'] if not re.fullmatch(r'\d+ \(\d+\)',x.strip())]
    LK={key(x) for x in lista}
    avs=[]
    from collections import Counter
    cnt={c:{'remissinstans':0,'spontant':0} for c in KATS}
    for g,typ in (('svarat','remissinstans'),('spontant','spontant')):
        for n in b[g] or []:
            n=N(n)
            parts=[n]
            if n=='Waldorfsfederationen samt en privatperson': parts=['Waldorfsfederationen','en privatperson']
            for p in parts:
                c=kategori(p)
                if p=='privatpersoner':
                    # ospecificerat antal privatpersoner (SOU 2025:19) — räknas inte numeriskt
                    avs.append({'namn':p,'kategori':'ovriga','grupp':'ovrigt','typ':typ,'pa_remisslistan':False,'klassning_anm':'Ospecificerat antal privatpersoner i källan; ingår inte i antalen.'}); continue
                cnt[c][typ]+=1
                avs.append({'namn':p,'kategori':c,'grupp':GRUPP.get(c,'ovrigt'),'typ':typ,'pa_remisslistan':key(p) in LK,
                            'klassning_anm':OSAKER.get(p)})
    priv=None
    if b.get('privatpersoner'):
        m=re.match(r'(\w+) spontana',b['privatpersoner']); tal={'Sju':7,'Sex':6,'Fem':5,'Fyra':4,'Tre':3,'Två':2,'Ett':1,'Åtta':8,'Nio':9,'Tio':10}
        n_priv=tal.get(m.group(1)) if m else None
        cnt['ovriga']['spontant']+=n_priv or 0
        priv={'text':b['privatpersoner'],'antal':n_priv}
    if priv is None and any(a['namn']=='privatpersoner' for a in avs):
        priv={'text':'"privatpersoner" (ordet förekommer i uppräkningen av spontana yttranden, utan antal)','antal':None}
    ej=[N(x) for x in b['ej_svarat'] or []]
    # webbpublicerade PDF:er
    web={key(x['namn']):x['url'] for x in rv['remissvar']}
    for a in avs: a['url']=web.get(key(a['namn']))
    typer=Counter(pdfc[x['url']].get('typ') for x in rv['remissvar'] if x['url'] in pdfc)
    inskannade=[pdfc[x['url']]['namn'] for x in rv['remissvar'] if pdfc.get(x['url'],{}).get('typ')=='inskannad']
    avstar_web=[pdfc[x['url']]['namn'] for x in rv['remissvar'] if pdfc.get(x['url'],{}).get('avstar')]
    # fokusorganisationer
    fok={}
    for fk,(label,match) in FOK.items():
        svar=[a for a in avs if match(a['namn'])]
        pa_lista=[x for x in lista if match(x)]
        ejs=[x for x in ej if match(x)]
        if svar: st='svarat'
        elif pa_lista: st='på remisslistan men ej svarat'
        else: st='ej på remisslistan'
        kall=[{'text':f"Remisslista {r['sou']} ({rv['remisslista_meta']['dnr']})",'url':rv['remisslista_pdf'][0]['url']}, bil_kalla]
        if svar and svar[0].get('url'): kall.append({'text':f"Remissvar från {svar[0]['namn']} på regeringen.se",'url':svar[0]['url']})
        anm=None
        if fk=='almega' and len(svar)>1: anm='Två Almega-namn i samma förteckning: '+' och '.join(f'"{a["namn"]}" ({a["typ"]})' for a in svar)+'. Inga samband antas.'
        if fk=='almega' and k=='tioarig': anm='Almega finns inte på remisslistan 2021. Remisslistan har "Friskolornas riksförbund" (avstod/svarade inte enligt propositionen). Inget samband antas mellan namnen (briefens regel).'
        if fk=='almega' and k=='spraklig': anm='Regeringen.se publicerar ett e-postmeddelande från Almega Utbildning under "Remissvar" som meddelar att organisationen avstår; propositionen listar Almega Utbildning bland dem som avstått eller inte yttrat sig.'
        fok[fk]={'status':st,'namn_i_remisslistan':pa_lista[0] if pa_lista else None,'namn_i_forteckningen':[a['namn'] for a in svar] or (ejs or None),
                 'pa_remisslistan':bool(pa_lista),'typ':svar[0]['typ'] if svar else None,'kallor':kall,'anm':anm}
    remiss_sida=find_page(pf, f"({rv['remisslista_meta']['dnr']})") or find_page(pf,'Remissyttrandena finns tillgängliga')
    rd=lambda i: f'https://data.riksdagen.se/dokument/{i}'
    post={
     'id':r['reform_id'],'namn_i_brief':r['brief'],'matchning':{'reforms_json_id':r['reform_id'],'utredningar_json_id':r['utr_id'],'kommentar':r['matchning']},
     'utredningsbetankande':{'nr':r['sou'],'titel':r['sou_titel'],'kalla':{'text':f"{r['sou']} {r['sou_titel']} (regeringen.se)",'url':r['sou_url']}},
     'remiss':{'url':rv['remiss_url'],'titel':rv['titel'],'diarienummer':rv['remisslista_meta']['dnr'],'publicerad':rv['publicerad'],'svar_senast':(rv['sista_svar'] or '').replace('senast den ','').replace('senast  den ','').strip() or None,
               'remisslista':{'url':rv['remisslista_pdf'][0]['url'],'antal_instanser':len(lista)},
               'kalla':{'text':f"Remiss {rv['remisslista_meta']['dnr']} på regeringen.se",'url':rv['remiss_url']},
               'webbsidans_innehall':'remissvar från inbjudna' if rv['remissvar'] else 'endast remisslista'},
     'proposition':{'nr':r['prop'],'titel':r['prop_titel'],'kalla':{'text':f"{r['prop']} (regeringen.se)",'url':r['prop_url']},'riksdagen':{'text':f"{r['prop']} (riksdagens öppna data)",'url':rd(r['prop_rd'])},'anm':r['ovrigt']},
     'utskottsbetankande':{'bet':r['bet'],'kalla':{'text':f"Bet. {r['bet']} (riksdagens öppna data)",'url':rd(r['bet_id'])},'status':{'text':f"Dokumentstatus bet. {r['bet']}",'url':f"https://data.riksdagen.se/dokumentstatus/{r['bet_id']}"}},
     'rskr':{'nr':r['rskr'],'beslutsdatum':r['beslut'],'status':'inträffat','kalla':{'text':f"Rskr. {r['rskr']}; beslutsaktivitet (BES) {r['beslut']} status inträffat i dokumentstatus för bet. {r['bet']}",'url':f"https://data.riksdagen.se/dokumentstatus/{r['bet_id']}"},'dokument':{'text':f"Rskr. {r['rskr']}",'url':rd(r['rskr_id'])}},
     'remissvar':{
        'kalla':bil_kalla,
        'diarienummer_i_propositionen':{'varde':rv['remisslista_meta']['dnr'] if f"({rv['remisslista_meta']['dnr']})" in open(pf).read().replace('\n',' ') else None,'kalla':{'text':f"{r['prop']} s. {remiss_sida}",'url':r['prop_url']}},
        'antal':{c:{**cnt[c],'totalt':cnt[c]['remissinstans']+cnt[c]['spontant']} for c in KATS},
        'antal_totalt':sum(cnt[c]['remissinstans']+cnt[c]['spontant'] for c in KATS),
        'antal_fokusgrupper':sum(cnt[c]['remissinstans']+cnt[c]['spontant'] for c in ('kommuner','enskilda_huvudman','skr','almega','ideburna')),
        'privatpersoner':priv,
        'avstatt_eller_ej_svarat':{'antal':len(ej),'namn':ej,'kalla':bil_kalla},
        'avsandare':avs,
        'citat':{'efter_remiss':b.get('svarat_text'),'spontana':b.get('spontant_text'),'avstatt':b.get('ej_svarat_text')}},
     'fokusorganisationer':fok,
     'pdf_format':{'publicerade_pdf':len(rv['remissvar']),'text':typer.get('text',0),'inskannad':typer.get('inskannad',0),'inskannade':inskannade,
                   'metod':'pdftotext: >200 tecken/sida = text; 0 tecken och inga inbäddade typsnitt = inskannad',
                   'avsta_svar_bland_publicerade':avstar_web,
                   'anm':None if rv['remissvar'] else 'Remissidan publicerar inga remissvar, bara remisslistan.'},
     'avvikelser':[]}
    # avvikelser lista vs förteckning
    FK={key(x) for x in (b['svarat'] or [])+(b['ej_svarat'] or [])}
    only_list=[x for x in lista if key(x) not in FK]
    only_prop=[x for x in (b['svarat'] or [])+(b['ej_svarat'] or []) if key(x) not in LK]
    if only_list or only_prop: post['avvikelser'].append({'typ':'remisslista_vs_forteckning','endast_i_remisslistan':only_list,'endast_i_propositionens_forteckning':only_prop,
        'anm':'Oftast stavningsvarianter (t.ex. "Karlstad kommun"/"Karlstads kommun"); ej sammanslagna automatiskt.'})
    if b.get('_anm'): post['avvikelser'].append({'typ':'tryckfel_i_kalla','anm':b['_anm']})
    out['reformer'].append(post)
json.dump(out,open(sys.argv[1],'w'),ensure_ascii=False,indent=1)
for p in out['reformer']:
    a=p['remissvar']['antal']
    print(p['namn_i_brief'],'| tot',p['remissvar']['antal_totalt'],'fokus',p['remissvar']['antal_fokusgrupper'],'|',{c:a[c]['totalt'] for c in KATS},'|',{f:v['status'] for f,v in p['fokusorganisationer'].items()},'| dnr i prop:',p['remissvar']['diarienummer_i_propositionen']['varde'],'| pdf',p['pdf_format']['text'],p['pdf_format']['inskannad'])
    for av in p['avvikelser']: print('   AVV',av)
