import json,sys,re
sys.path.insert(0,'bin')
from klass import kategori,N,GRUPP
from namn import namngivna
from pagefind import find_page
K=json.load(open('kedjor.json')); bet=[r for r in K['reformer'] if r['id']=='betyg'][0]
b=json.load(open('bilagor.json'))['betyg']; kanda=b['svarat']+b['spontant']+b['ej_svarat']
boxes=[x for x in json.load(open('sou_boxes.json')) if x['typ']=='Förslag']
P197={y['avsnitt']:y for y in json.load(open('prop197_sec.json'))}
P194={y['avsnitt']:y for y in json.load(open('prop194_sec.json'))}
SOU_URL={'volym-1':'https://www.regeringen.se/contentassets/56408e57ea8e4954bf38491c8bc33d4c/ett-likvardigt-betygssystem-sou-202518-volym-1.pdf',
         'volym-2':'https://www.regeringen.se/contentassets/56408e57ea8e4954bf38491c8bc33d4c/ett-likvardigt-betygssystem-sou-202518-volym-2.pdf'}
U197='https://www.regeringen.se/contentassets/a37af6932a5f4cf794499eb68a798d63/ett-likvardigt-betygssystem-prop.-202526197.pdf'
U194='https://www.regeringen.se/contentassets/42c1e2e4596b4f8682e3d8283b91a138/nya-laroplaner--for-en-stark-kunskapsskola-prop.-202526194.pdf'
UBU26='https://data.riksdagen.se/fil/30067395-80F8-46F2-9CFB-20DF8E682DC1'
UBU23S='https://data.riksdagen.se/dokumentstatus/HD01UbU23'
def first_sentence(t):
    m=re.match(r'(.+?\.)(\s|$)',t); return m.group(1) if m else t
# Matchningstabell (manuell; grund anges per rad). typ: 'box' = förslaget motsvaras av propositionens förslags-/bedömningsruta;
# 'detalj' = propositionen tar ställning övergripande i avsnittet men förslagets detaljer finns inte i rutan; None = ingen träff.
D_FORORDNING=('Den mer detaljerade regleringen om hur beräkningen ska gå till bör bestämmas på förordningsnivå.','197','6.1')
M={
 'F01':('197','6.2','box','förslag','Ämne: betygsskala 1–10 (prop. rutan "Regeringens förslag" avsnitt 6.2).'),
 'F02':('197','6.2','box','bedömning','Ämne: betygskriterier på förordningsnivå (prop. rutan "Regeringens bedömning" avsnitt 6.2).'),
 'F03':('194','6.7','box','förslag','Prop. 2025/26:194 avsnitt 6.7, regeringens förslag om den s.k. undantagsbestämmelsen (bortse från enstaka delar).'),
 'F04':('194','6.8','box','förslag','Prop. 2025/26:194 avsnitt 6.8 Sammantagen bedömning; prop. 2025/26:197 anger att avsnitt 9.3.7 inte behandlas där.'),
 'F05':('194','6.7','avsnitt','förslag','Avsnittsnivå: prop. 2025/26:194 anger att den behandlar SOU 2025:18 avsnitt 9.3 och 9.4 om att ändra uttrycket "uppfylla kriterier"; prop. 2025/26:197 behandlar inte avsnitt 9.4.2. Att just detta förslag ingår är inte uttryckligt.'),
 'F06':('194','6.7','avsnitt','förslag','Som F05 (SOU avsnitt 9.4.3, ej lovskola).'),
 'F07':('194','6.7','avsnitt','förslag','Som F05 (SOU avsnitt 9.4.3, ej lovskola).'),
 'F08':('194','6.7','avsnitt','förslag','Som F05 (SOU avsnitt 9.4.3, ej lovskola).'),
 'F09':('197','6.7','box','förslag','Ämne: lovskola (prop. 2025/26:197 behandlar lagförslagen i 9.4.3 som rör lovskola).'),
 'F10':('197','6.13','amne','förslag','OSÄKER ämnesmatchning: följdändringar E→4. Propositionen nämner inte förslaget uttryckligen.'),
 'F11':('197','6.8','box','förslag','Ämne: gymnasiearbetet betyg 1–4. Obs: SOU-förslaget omfattar även komvuxarbetet, som inte nämns i propositionens ruta.'),
 'F12':('197','6.1','box','bedömning','Ämne: ny meritvärdesmodell grundskola (prop. lämnar bedömning, inte lagförslag).'),
 'F21':('197','6.1','box','bedömning','Ämne: ny meritvärdesmodell gymnasieskola/högre utbildning (prop. lämnar bedömning).'),
 'F35':('197','6.5','box','förslag','Ämne: inrapportering av betyg.'),
 'F42':('197','6.5','box','förslag','Ämne: inrapportering av betyg (komvux omfattas av propositionens förslag).'),
 'F49':('197','6.4.2','box','förslag','Ämne: göra om/genomföra nationella slutprov efter avslutad utbildning.'),
 'F50':('197','6.4.2','amne','förslag','OSÄKER ämnesmatchning: tillgodoräkna senare provresultat; propositionens ruta reglerar rätten att göra om prov, inte meritvärdesberäkningen.'),
 'F51':('197','6.4.2','box','förslag','Ämne: avgift för slutprov.'),
 'F52':('197','6.6','box','förslag','Ämne: behörighet meritvärde minst 4.'),
 'F53':('197','6.12.1+6.12.2','box','förslag','Ämne: programinriktat val tas bort (6.12.2) och språkintroduktion (6.12.1).'),
 'F56':('197','6.9','box','förslag','Ämne: gymnasieexamen.'),
 'F57':('197','6.10','box','förslag','Ämne: gymnasieingenjörsexamen.'),
 'F60':('197','6.11','box','förslag','Ämne: meritvärde som urvalsgrund till högskolan.'),
 'F61':('197','6.3','box','förslag','Ämne: bedömningssamråd grundskola/specialskola.'),
 'F62':('197','6.3','box','förslag','Ämne: bedömningssamråd gymnasieskola.'),
 'F63':('197','6.4.3','box','förslag','Ämne: nationella prov ska inte särskilt beaktas.'),
 'F64':('197','6.4.1','box','bedömning','Ämne: nationellt slutprovsystem (prop. lämnar bedömning).'),
 'F69':('197','6.4.1','box','bedömning','Ämne: central bedömning av slutprov (prop. bedömning: "De nationella slutproven bör bedömas centralt").'),
 'F77':('197','8','box','förslag','Ämne: ikraftträdande.'),
 'F78':('197','8','box','förslag','Ämne: övergångsbestämmelser.'),
}
for f in ['F13','F14','F15','F16','F17','F18','F19','F20','F22','F23','F24','F25','F26','F27','F28','F32','F33','F36','F38']:
    M[f]=('197','6.1','detalj','bedömning','Detalj i meritvärdesmodellen; propositionen tar ställning övergripande i avsnitt 6.1 och hänvisar detaljreglering till förordning.')
for f in ['F29','F30','F71','F72']:
    M[f]=('197','6.4.1','detalj','bedömning','Detalj om vilka/hur många slutprov; propositionens bedömning i 6.4.1 är övergripande.')
INGEN={'F31':'Propositionen nämner meritpoäng endast i beskrivningen av nuvarande reglering (avsnitt 5).',
 'F54':'Fritextsökning i propositionen: 0 träffar på "spetsutbildning" och "riksrekryterande".'}
def utfall_prop(text):
    s=first_sentence(text)
    if re.search(r'stämmer (också )?överens med regeringens',s) and not re.search(r'i huvudsak|delvis',s): return 'överensstämmer'
    if re.search(r'\bavviker\b',s): return 'avviker'
    return None
# riksdag
RD_BIFALL={'text':'Bet. 2025/26:UbU26 s. 3, Utskottets förslag till riksdagsbeslut punkt 1: "Därmed bifaller riksdagen propositionerna 2025/26:194 punkterna 1.2 och 2.2, 2025/26:195 delpunkt 2, 2025/26:196 punkt 3.2, 2025/26:197 punkterna 1–4 och 2025/26:198 punkterna 2.2 och 3.2." Kammaren biföll utskottets förslag (acklamation), rskr. 2025/26:335, 2026-06-09.','url':UBU26}
RD_LAGTEKN={'text':'Bet. 2025/26:UbU26 s. 1: "Utskottet ställer sig bakom regeringens förslag till ändringar i skollagen, men med vissa lagtekniska anpassningar och ändringar av ikraftträdande- och övergångsbestämmelserna." s. 29: "De ändringar som utskottet föreslår har enligt utskottets bedömning inte någon betydelse i sak."','url':UBU26}
RD_UBU23={'text':'Bet. 2025/26:UbU23 punkt 1 (dokumentstatus): "Riksdagen a) godtar det som utskottet anför om regeringens förslag till 1. lag om ändring i skollagen (2010:800), 2. lag om ändring i skollagen (2010:800) [...]" Det lagtekniska antagandet av prop. 2025/26:194 punkterna 1.2 och 2.2 sker i bet. 2025/26:UbU26.','url':UBU23S}
fors=[]
for bx in boxes:
    fid=bx['id']
    post={'id':fid,'sou_avsnitt':bx['avsnitt'],'sou_avsnittsrubrik':bx['avsnittsrubrik'],
          'forslag_ordagrant':bx['text'],
          'kalla':{'text':f"SOU 2025:18 {bx['vol'].replace('volym-','volym ')} s. {bx['sida']}, förslagsruta i avsnitt {bx['avsnitt']}",'url':SOU_URL[bx['vol']]},
          'textanm':'Förslagsrutan kan fortsätta med en punktlista/tabell som inte extraherats (rutan slutar med kolon).' if bx['text'].rstrip().endswith(':') else None}
    m=M.get(fid)
    if not m:
        post['proposition']=None
        post['utfall_prop']=None
        post['utfall_prop_kalla']={'text':'Förslaget motsvaras inte av någon förslags- eller bedömningsruta i prop. 2025/26:197 eller prop. 2025/26:194 (manuell genomgång av propositionernas 17 resp. 2 relevanta avsnitt). '+INGEN.get(fid,'Inget uttryckligt ställningstagande hittat; troligen förordnings- eller uppdragsnivå. "ej genomfört" sätts inte utan uttryckligt källstöd.'),'url':U197}
        post['utfall_riksdag']=None
        post['utfall_riksdag_kalla']={'text':'Inget propositionsförslag att besluta om.','url':None}
        post['namngivna_remissinstanser']=[]; post['namngivna_fokusgrupper']=[]; post['generiska_hanvisningar']=[]
        post['matchning']={'typ':'ingen','grund':INGEN.get(fid)}
        fors.append(post); continue
    prop,avs,typ,ruta,grund=m
    secs=[(P197 if prop=='197' else P194)[a] for a in avs.split('+')]
    PURL=U197 if prop=='197' else U194; PNR='Prop. 2025/26:'+prop
    ulab='Utredningens förslag' if prop=='197' else 'Utredningen om likvärdiga betyg och meritvärdens förslag'
    rlab='Remissinstanserna' if prop=='197' else 'Remissinstanserna#2'
    psecs=[]; utf=[]; nam=[]; gen=[]
    for s in secs:
        d=s['delar']; u=d.get(ulab) or d.get('Utredningens bedömning'); r=d.get(rlab)
        reg=d.get('Regeringens förslag') if ruta=='förslag' else d.get('Regeringens bedömning')
        psecs.append({'avsnitt':s['avsnitt'],'rubrik':s['rubrik'],'regeringens_ruta':{'typ':'Regeringens '+ruta,'text':reg['text'] if reg else None,'kalla':{'text':f"{PNR} s. {','.join(map(str,reg['sidor']))}, avsnitt {s['avsnitt']}",'url':PURL} if reg else None},
            'utredningens_forslag_ordagrant':u['text'] if u else None,'utredningens_forslag_kalla':{'text':f"{PNR} s. {','.join(map(str,u['sidor']))}, avsnitt {s['avsnitt']} \"{ulab}\"",'url':PURL} if u else None,
            'remissinstanserna_ordagrant':r['text'] if r else None,'remissinstanserna_kalla':{'text':f"{PNR} s. {','.join(map(str,r['sidor']))}, avsnitt {s['avsnitt']} \"Remissinstanserna\"",'url':PURL} if r else None,
            'anm':None if r else 'Avsnittet saknar rubriken "Remissinstanserna".'})
        if u: utf.append((utfall_prop(u['text']),first_sentence(u['text']),u['sidor'],s['avsnitt']))
        if r:
            o,g=namngivna(r['text'],kanda); nam+= [dict(x,avsnitt=s['avsnitt']) for x in o]; gen+=g
    post['proposition']={'nr':PNR,'avsnitt':psecs}
    post['matchning']={'typ':{'box':'förslagsruta','avsnitt':'avsnittsnivå','amne':'osäker ämnesmatchning','detalj':'övergripande avsnitt, detalj ej behandlad'}[typ],'grund':grund}
    # utfall_prop
    if typ in ('box',) and utf and all(x[0]=='överensstämmer' for x in utf):
        post['utfall_prop']='överensstämmer'
    elif typ=='box' and utf and all(x[0]=='avviker' for x in utf): post['utfall_prop']='avviker'
    else: post['utfall_prop']=None
    post['utfall_prop_citat']=[{'text':x[1],'kalla':{'text':f"{PNR} s. {','.join(map(str,x[2]))}, avsnitt {x[3]}",'url':PURL}} for x in utf]
    if typ=='detalj':
        post['utfall_prop_citat'].append({'text':D_FORORDNING[0],'kalla':{'text':f"Prop. 2025/26:197 s. {find_page('pdf/prop197.txt',D_FORORDNING[0])}, avsnitt 6.1 Skälen för regeringens bedömning",'url':U197}})
    post['utfall_prop_anm']=None if post['utfall_prop'] else ('Utredningens förslag "stämmer i huvudsak/delvis överens" — inte entydigt överensstämmer eller avviker; ingen mappning utan tolkning.' if any(re.search(r'i huvudsak|delvis',x[1]) for x in utf) and typ in ('box','avsnitt','amne') else ('Matchningen är inte uttrycklig; värde sätts inte.' if typ in ('avsnitt','amne') else ('Propositionen tar inte ställning till detaljförslaget.' if typ=='detalj' else None)))
    # riksdag
    if prop=='197' and ruta=='förslag' and typ=='box' and avs!='8':
        post['utfall_riksdag']='bifall'; post['utfall_riksdag_kalla']=RD_BIFALL; post['utfall_riksdag_anm']=RD_LAGTEKN['text']
    elif prop=='194' and typ=='box':
        post['utfall_riksdag']='bifall'; post['utfall_riksdag_kalla']=RD_BIFALL; post['utfall_riksdag_anm']=RD_UBU23['text']+' — '+RD_LAGTEKN['text']
    elif avs=='8':
        post['utfall_riksdag']=None; post['utfall_riksdag_kalla']=RD_LAGTEKN; post['utfall_riksdag_anm']='Riksdagen bifaller punkten men utskottet ändrade ikraftträdande- och övergångsbestämmelserna (enligt utskottet utan betydelse i sak). Varken "bifall" eller "ändrat" kan sättas utan tolkning.'
    elif ruta=='bedömning':
        post['utfall_riksdag']=None; post['utfall_riksdag_kalla']={'text':'Propositionen lämnar en bedömning, inte ett förslag till riksdagsbeslut; riksdagen fattar inget beslut om bedömningen.','url':UBU26}; post['utfall_riksdag_anm']=None
    else:
        post['utfall_riksdag']=None; post['utfall_riksdag_kalla']=RD_BIFALL; post['utfall_riksdag_anm']='Propositionsförslaget bifölls, men kopplingen mellan utredningsförslaget och propositionsförslaget är inte uttrycklig.'
    post['namngivna_remissinstanser']=nam
    post['namngivna_fokusgrupper']=[{'namn_i_texten':x['namn_i_texten'],'namn_i_forteckningen':x['namn_i_forteckningen'],'kategori':x['kategori'],'grupp':GRUPP[x['kategori']]} for x in nam if x['kategori'] in GRUPP]
    post['namngivna_kalla']=[p['remissinstanserna_kalla'] for p in psecs if p['remissinstanserna_kalla']]
    post['generiska_hanvisningar']=gen
    fors.append(post)
# fokus-remissvar
fok=[a for a in bet['remissvar']['avsandare'] if a['kategori'] in GRUPP]
for a in fok:
    a['status']=bet['fokusorganisationer'][a['kategori']]['status'] if a['kategori'] in ('skr','almega','ideburna') else None
    a['svarat_som']='remissinstans (på remisslistan)' if a['typ']=='remissinstans' else 'självmant (spontant yttrande)'
    a['url_anm']=None if a['url'] else ('Spontana yttranden publiceras inte på regeringen.se ("Övriga yttranden finns tillgängliga i departementet").' if a['typ']=='spontant' else 'Ingen PDF hittad på remissidan.')
pilot={'_meta':{'reform_id':'betyg','namn_i_brief':'Betygsuppdraget','skapad':'2026-11-10','status':'research — inte publik data',
  'kedja':{'utredningsbetankande':bet['utredningsbetankande'],'remiss':{k:bet['remiss'][k] for k in ('url','diarienummer','publicerad','svar_senast')},'proposition':[{'nr':'Prop. 2025/26:197','url':U197},{'nr':'Prop. 2025/26:194 (avsnitt 6.7–6.8, del av SOU 2025:18)','url':U194}],
           'utskottsbetankande':[{'bet':'2025/26:UbU26','url':UBU26},{'bet':'2025/26:UbU23 (prop. 194)','url':'https://data.riksdagen.se/dokument/HD01UbU23'}],'rskr':{'nr':'2025/26:335','beslutsdatum':'2026-06-09','kalla':bet['rskr']['kalla']}},
  'val_av_pilot':'Komplett kedja till rskr och flest remissvar från fokusgrupperna av de sju (35: 26 kommuner, 5 enskilda huvudmän, SKR, 2 Almega-namn, Idéburna), enligt propositionens remissförteckning. Tvåa: Tid för undervisningsuppdraget (33).',
  'forslagsenhet':'En post per förslagsruta ("Förslag:") i SOU 2025:18 volym 1 (80 st). Bedömningsrutor ("Bedömning:", 27 st) och författningsförslagens paragrafer är inte egna poster.',
  'vokabular':{'utfall_prop':['överensstämmer','avviker','ej genomfört',None],'utfall_riksdag':['bifall','ändrat',None]},
  'regel_utfall_prop':'Sätts bara när propositionens mening om utredningens förslag uttryckligen säger "stämmer överens med regeringens" (utan "i huvudsak"/"delvis") resp. "avviker", och förslaget matchar en förslags-/bedömningsruta. Annars null med citat.',
  'regel_utfall_riksdag':'"bifall" när förslaget motsvaras av ett propositionsförslag (inte bedömning) som riksdagen enligt UbU26/UbU23 bifallit; ikraftträdande null (ändrade av utskottet utan betydelse i sak). Inga tillkännagivanden (alla motionsyrkanden avslogs, rskr. 2025/26:335).'},
 'riksdagen':{'andrade_forslag':{'varde':'lagtekniska anpassningar och ändrade ikraftträdande- och övergångsbestämmelser, enligt utskottet utan betydelse i sak','kallor':[RD_LAGTEKN,RD_BIFALL]},
   'tillkannagivanden':{'varde':[],'kalla':{'text':'Bet. 2025/26:UbU26 s. 1: "Utskottet anser att riksdagen bör avslå samtliga motionsyrkanden. I betänkandet finns åtta reservationer (S, V, C, MP). I fem av reservationerna (S, V, C, MP) föreslås att riksdagen ska göra tillkännagivanden [...]". Kammaren biföll utskottets förslag på samtliga punkter (dokumentstatus: vinnare utskottet).','url':UBU26}}},
 'remissvar_fokusgrupper':fok,
 'forslag':fors}
json.dump(pilot,open(sys.argv[1],'w'),ensure_ascii=False,indent=1)
from collections import Counter
print('förslag',len(fors),Counter(f['utfall_prop'] for f in fors),Counter(f['utfall_riksdag'] for f in fors),Counter(f['matchning']['typ'] for f in fors))
print('fokus remissvar',len(fok),Counter(a['kategori'] for a in fok), Counter(a['typ'] for a in fok))
# --- normalisera: propositionsavsnitt lagras en gång, förslagen refererar med nyckel "prop:avsnitt"
pilot=json.load(open(sys.argv[1]))
avsn={}
for f in pilot['forslag']:
    if not f['proposition']: continue
    pnr=f['proposition']['nr'].split(':')[-1]
    refs=[]
    for s in f['proposition']['avsnitt']:
        key=f"{pnr}:{s['avsnitt']}"
        rr=s.pop('regeringens_ruta')
        if key not in avsn:
            avsn[key]={'proposition':f['proposition']['nr'],**s,'regeringens_rutor':{}}
        avsn[key]['regeringens_rutor'][rr['typ']]={'text':rr['text'],'kalla':rr['kalla']}
        refs.append({'ref':key,'ruta':rr['typ']})
    f['proposition']={'nr':f['proposition']['nr'],'avsnitt':refs}
    for x in f['namngivna_remissinstanser']: x.pop('avsnitt',None)
pilot['propositionsavsnitt']=avsn
# lägg propositionsavsnitt före förslag i filen
order=['_meta','riksdagen','remissvar_fokusgrupper','propositionsavsnitt','forslag']
json.dump({k:pilot[k] for k in order},open(sys.argv[1],'w'),ensure_ascii=False,indent=1)
print('avsnitt',len(avsn),sorted(avsn))
