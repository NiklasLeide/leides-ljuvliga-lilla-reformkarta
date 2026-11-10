# Sprint 14 T4 — datapatch enligt docs/revision/2026-11-andringslista.md + Niklas beslut 2026-11-10.
# reforms/uppdrag/tidslinje/andringar: JSON-objekt (round-trip verifierad formatbevarande).
# guide/utredningar: riktade strängbyten; varje old måste finnas exakt n gånger, annars avbrott
# utan skrivning. Radetiketter = rad-ID i ändringslistan (B# = beslut i chatten).
import json, sys, os
ROOT = sys.argv[1]
P = lambda f: os.path.join(ROOT, f)
log = []
def L(tag, msg): log.append(f'{tag:6} {msg}')

NOT_1243 = ('Riksdagens betänkande anger att ändringarna i huvudsak träder i kraft den 1 juli 2028. '
            'Samordningslagen SFS 2026:1243 träder i kraft den 2 juli 2028.')
SFS800 = 'https://data.riksdagen.se/dokument/sfs-2010-800.html'
LAGEN = 'https://lagen.nu/2010:800'
AUG = 'https://www.regeringen.se/regeringsuppdrag/2026/08/andring-av-uppdraget-till-statens-skolverk-att-forbereda-inforandet-av-en-tioarig-grundskola-och-ta-fram-forslag-pa-nya-laroplaner/'

def setx(obj, key, old, new, tag):
    if obj.get(key) != old:
        raise SystemExit(f'[{tag}] {key}: väntat {old!r}, fick {obj.get(key)!r}')
    obj[key] = new; L(tag, f'{key}')

# ======================= reforms.json =======================
reforms = json.load(open(P('data/reforms.json'), encoding='utf-8'))
RF = {r['id']: r for r in reforms}
setx(RF['vinst'], 'transition',
     'Riksdagen beslutade 2026-08-13 (bet. 2025/26:UbU30; rskr ej publicerad 2026-08-25). Prop. 2025/26:292, överlämnad 2026-06-25. Ikraftträdande 1 juli 2027.',
     'Riksdagen beslutade 2026-08-13 (bet. 2025/26:UbU30, rskr. 2025/26:438). Prop. 2025/26:292, överlämnad 2026-06-25. Ikraftträdande 1 juli 2027 (SFS 2026:1634).', 'R1R2')
setx(RF['profession'], 'transition', 'I kraft 1 sep 2025.',
     'Riksdagen beslutade 2023-05-31 (bet. 2022/23:UbU13, rskr. 2022/23:206). I kraft 1 sep 2025.', 'R3')
setx(RF['timplan'], 'transition', 'Beslutad. Tillämpas stegvis.',
     'Riksdagen beslutade 2023-12-20 (bet. 2023/24:UbU5, rskr. 2023/24:106). Tillämpas stegvis.', 'R4')
setx(RF['tioarig'], 'transition', 'Riksdagen har beslutat. Tillämpas fr.o.m. HT 2028.',
     'Riksdagen beslutade 2025-06-18 (bet. 2024/25:UbU17, rskr. 2024/25:289). Tillämpas fr.o.m. HT 2028.', 'R5')
# Beslut 1 — datum per lag enligt lagen.nu:s förarbetesregister:
#   2026:1242 (1 juli 2028): prop 194, 195, 198 · 2026:1243 (2 juli 2028): prop 194, 196, 197, 198
#   2026:1244 (1 juli 2030): prop 197 · 2026:1245 (1 jan 2031): prop 194, 197, 198
setx(RF['tid'], 'ikraft', '1 aug 2026 / 1 juli 2027 / 1 juli 2028', '1 aug 2026 / 1 juli 2027 / 2 juli 2028', 'R7')
setx(RF['tid'], 'transition',
     'Riksdagen beslutade 2026-06-09 (bet. 2025/26:UbU25, rskr. 2025/26:332). Ikraftträdande stegvis: kränkande behandling 1 augusti 2026 (SFS 2026:1096), undervisningsuppdraget 1 juli 2027 (SFS 2026:1097), övriga ändringar 1 juli 2028 (SFS 2026:1243).',
     'Riksdagen beslutade 2026-06-09 (bet. 2025/26:UbU25, rskr. 2025/26:332). Ikraftträdande stegvis: kränkande behandling 1 augusti 2026 (SFS 2026:1096), undervisningsuppdraget 1 juli 2027 (SFS 2026:1097), övriga ändringar 2 juli 2028 (SFS 2026:1243). ' + NOT_1243, 'R7')
setx(RF['betyg'], 'ikraft', '1 juli 2028', '2 juli 2028', 'R8/B1')
setx(RF['betyg'], 'transition',
     'Riksdagen beslutade 2026-06-09 (bet. 2025/26:UbU26, rskr. 2025/26:335). Skollagen: 1 juli 2028. Ny betygsskala stegvis fr.o.m. HT 2027 (gymnasiet) resp. HT 2028 (grundskolan). Slutprov fr.o.m. VT 2029 (gymnasiet), VT 2031 (grundskolan). Komvux: 1 jan 2031. Synkroniserat med tioårig grundskola.',
     'Riksdagen beslutade 2026-06-09 (bet. 2025/26:UbU26, rskr. 2025/26:335). Skollagen: 2 juli 2028 (SFS 2026:1243). Ny betygsskala stegvis fr.o.m. HT 2027 (gymnasiet) resp. HT 2028 (grundskolan). Slutprov fr.o.m. VT 2029 (gymnasiet), VT 2031 (grundskolan). Komvux: 1 jan 2031 (SFS 2026:1245). Synkroniserat med tioårig grundskola. ' + NOT_1243, 'R8/B1')
setx(RF['laroplaner'], 'ikraft', '1 juli 2028', '1 juli 2028 / 2 juli 2028', 'B1')
setx(RF['laroplaner'], 'transition',
     'Riksdagen beslutade 2026-06-03 (bet. 2025/26:UbU23, rskr. 2025/26:327). Merparten 1 juli 2028. Komvux-ändringar 1 jan 2031.',
     'Riksdagen beslutade 2026-06-03 (bet. 2025/26:UbU23, rskr. 2025/26:327). Ikraftträdande 1 juli 2028 (SFS 2026:1242) och 2 juli 2028 (SFS 2026:1243). Komvux-ändringar 1 jan 2031 (SFS 2026:1245). ' + NOT_1243, 'B1')
setx(RF['yrkes'], 'ikraft', '1 juli 2026 / 2 juli 2028', '1 juli 2026 / 1 juli 2028 / 2 juli 2028', 'B1')
setx(RF['yrkes'], 'transition',
     'Riksdagen beslutade 2026-05-27 (bet. 2025/26:UbU27, rskr. 2025/26:307). Entreprenad och rätt att fullfölja: 1 juli 2026. Övriga ändringar: 2 juli 2028.',
     'Riksdagen beslutade 2026-05-27 (bet. 2025/26:UbU27, rskr. 2025/26:307). Entreprenad och rätt att fullfölja: 1 juli 2026 (SFS 2026:960). Övriga ändringar: 1 juli 2028 (SFS 2026:1242) och 2 juli 2028 (SFS 2026:1243). Komvux: 1 jan 2031 (SFS 2026:1245). ' + NOT_1243, 'B1')
setx(RF['stod'], 'transition',
     'Riksdagen beslutade 2026-06-03 (bet. 2025/26:UbU24, rskr. 2025/26:328). Ikraftträdande 1 juli 2028.',
     'Riksdagen beslutade 2026-06-03 (bet. 2025/26:UbU24, rskr. 2025/26:328). Ikraftträdande 1 juli 2028 (SFS 2026:1242).', 'B1')
# Beslut 2 — studiero
setx(RF['studiero'], 'transition',
     'Riksdagen beslutade 2026-06-03 (bet. 2025/26:UbU22, rskr. 2025/26:308). Merparten träder i kraft 1 augusti 2026. Vissa bestämmelser om stödundervisning träder i kraft 1 juli 2028.',
     'Riksdagen beslutade 2026-06-03 (bet. 2025/26:UbU22, rskr. 2025/26:308). Lagändringarna börjar gälla 1 augusti 2026 (SFS 2026:1198).', 'R11/B2')
setx(RF['skolpeng'], 'transition',
     'Föreslaget ikraftträdande 1 jan 2027, tillämpas 2028. Slutbetänkande (gymnasiet) väntas nov 2026.',
     'Föreslaget ikraftträdande 1 jan 2027, tillämpas 2028. Slutbetänkande (gymnasiet) SOU 2026:65 lämnat 29 oktober 2026.', 'R9')
setx(RF['sprak'], 'transition', 'Utredning pågår. Redovisning senast 11 juni 2026.',
     'Slutbetänkande SOU 2026:37 överlämnat 17 juni 2026. Ny utredning om obligatorisk förskola med språkutvecklande insatser tillsatt 3 september 2026 (U2026/01573), redovisas senast 1 september 2027.', 'R10')
OLD_SV = 'https://www.skolverket.se/styrning-och-ansvar/forandringar-inom-skolomradet/tioarig-grundskola-och-nya-laroplaner'
for rid in ('laroplaner', 'tioarig'):
    hit = [l for l in RF[rid]['links'] if l['u'] == OLD_SV]
    assert len(hit) == 1, rid
    hit[0]['u'] = 'https://www.skolverket.se/styrning-och-ansvar/en-skola-i-forandring/nya-laroplaner-och-kursplaner'; L('R12', rid)
hit = [l for l in RF['betyg']['links'] if l['u'] == 'https://www.regeringen.se/rattsliga-dokument/statens-offentliga-utredningar/2025/03/sou-202518/']
assert len(hit) == 1
hit[0]['u'] = 'https://www.regeringen.se/rattsliga-dokument/statens-offentliga-utredningar/2025/02/sou-202518/'; L('R13', 'betyg')

# ======================= uppdrag.json =======================
up = json.load(open(P('data/uppdrag.json'), encoding='utf-8'))
def rel(node, titel_start):
    h = [r for r in up[node].get('relaterade', []) if r.get('titel', '').startswith(titel_start)]
    assert len(h) == 1, (node, titel_start, len(h)); return h[0]
setx(up['laroplaner'], 'kort',
     'Uppdrag att ta fram förslag till nya kursplaner (U2025/02427). 40 Mkr 2026. Förslag till regeringen mars 2027.',
     'Uppdrag att ta fram förslag på nya läroplaner (U2025/02427). 40 Mkr 2026. Förslag till regeringen senast 14 maj 2027.', 'U1U3')
ft = up['laroplaner']['fulltext']
assert ft.count('31 mars 2027') == 1, ft.count('31 mars 2027')
up['laroplaner']['fulltext'] = ft.replace('31 mars 2027', '14 maj 2027 (ursprungligen 31 mars 2027; senarelagt genom U2026/01483, 20 augusti 2026)'); L('U2', 'laroplaner.fulltext')
for node in ('laroplaner', 'tioarig'):
    r = rel(node, 'Ändring av uppdraget om tioårig grundskola')
    setx(r, 'kort', 'Redovisningen av förslagen till nya och reviderade läroplaner senareläggs till 14 maj 2027 (U2026/00888, 24 aug 2026).',
         'Redovisningen av förslagen till nya och reviderade läroplaner senareläggs till 14 maj 2027 (U2026/01483, 20 aug 2026).', 'U4')
    assert r['fulltext'].startswith('Ändring av uppdraget till Statens skolverk att förbereda införandet av en tioårig grundskola och ta fram förslag på nya läroplaner (U2025/02427, U2026/00888; 24 augusti 2026).')
    r['fulltext'] = r['fulltext'].replace('(U2025/02427, U2026/00888; 24 augusti 2026).',
        '(U2026/01483; 20 augusti 2026). Beslutet ändrar uppdraget U2025/02427 och U2026/00888.'); L('U5', node)
    setx(r['kallor'][0], 'text', 'Regeringsuppdrag (U2026/00888)', 'Regeringsuppdrag (U2026/01483)', 'U6')
    # U7 — apriländringen (ny relaterad post, före augustiändringen)
    i = up[node]['relaterade'].index(r)
    up[node]['relaterade'].insert(i, {
        'titel': 'Ändring av uppdraget om tioårig grundskola och nya läroplaner (april 2026)',
        'kort': 'Förslagen till nya läroplaner ska utgå från prop. 2025/26:194; experter från Läroplansutredningen ges en central roll (U2026/00888, 23 april 2026).',
        'fulltext': 'Ändring av uppdraget till Statens skolverk att förbereda införandet av en tioårig grundskola och ta fram förslag på nya läroplaner (U2026/00888; 23 april 2026). Förslagen till nya läroplaner ska utgå från propositionen Nya läroplaner – för en stark kunskapsskola (prop. 2025/26:194). Experter från Läroplansutredningen (U 2023:09) ges en aktiv och central roll. Skolverket ska senast den 15 juni 2026 ge en samlad redovisning till Regeringskansliet (Utbildningsdepartementet).',
        'kallor': [{'text': 'Regeringsuppdrag (U2026/00888)', 'url': 'https://www.regeringen.se/regeringsuppdrag/2026/04/andring-av-uppdraget-till-statens-skolverk-att-forbereda-inforandet-av-en-tioarig-grundskola-och-ta-fram-forslag-pa-nya-laroplaner/'}],
        'typ': 'uppdrag'}); L('U7', node)
# U8 — införandestödets beslutsdatum (fem noder)
n8 = 0
for node, v in up.items():
    for r in v.get('relaterade', []):
        if '(U2026/01265, 23 juni 2026)' in (r.get('fulltext') or ''):
            r['fulltext'] = r['fulltext'].replace('(U2026/01265, 23 juni 2026)', '(U2026/01265, 18 juni 2026)'); n8 += 1
assert n8 == 5, n8; L('U8', '5 noder')
r = rel('betyg', 'Uppdrag om digitala prov')
DP = 'https://www.regeringen.se/globalassets/regeringen/dokument/utbildningsdepartementet/u2026_01377-uppdrag-till-statens-skolverk-om-digitala-prov_webb.pdf'
setx(r, 'kort', 'Regeringsuppdrag till Skolverket om digitala prov (24 juli 2026). Uppdragets innehåll framgår av regeringsbeslutet — se källan.',
     'Digitala nationella slutprov i grundskolan, specialskolan och på gymnasial nivå (U2026/01377, 23 juli 2026). Ersätter tidigare uppdrag om digitaliserade nationella prov. Delredovisning om central rättning senast 1 december 2026; årlig redovisning 15 februari.', 'U9U10')
setx(r, 'fulltext', 'Regeringsuppdrag till Statens skolverk om digitala prov, daterat den 24 juli 2026. Uppdragets fullständiga innehåll och villkor framgår av regeringsbeslutet (se källan).',
     'Uppdrag till Statens skolverk om digitala prov (U2026/01377, 23 juli 2026). Skolverket ska utveckla och tillhandahålla digitala nationella slutprov i grundskolan, specialskolan och på gymnasial nivå. Uppdraget ersätter tidigare givna uppdrag om digitaliserade nationella prov, bl.a. U2026/00283. Den del som rör central rättning delredovisas senast den 1 december 2026; uppdraget redovisas årligen senast den 15 februari.', 'U9U10')
setx(r['kallor'][0], 'text', 'Regeringsuppdrag 2026-07-24', 'Regeringsuppdrag (U2026/01377)', 'U9')
r['kallor'].append({'text': 'Regeringsbeslut U2026/01377 (PDF)', 'url': DP}); L('U9', 'kalla PDF')
r = rel('betyg', 'Ändring av uppdraget att digitalisera')
setx(r, 'kort', 'Genomförandeplan för digitaliserade och centralt rättade nationella slutprov (U2026/00283). Digitala prov senarelagda, pappersprov tills vidare. Central rättning fortgår — gymnasiet HT 2026, grundskolan VT 2028. Redovisas 8 maj 2026.',
     'Genomförandeplan för digitaliserade och centralt rättade nationella slutprov (U2026/00283). Digitala prov senarelagda, pappersprov tills vidare. Redovisad 8 maj 2026 (U2026/00976). Ersatt av uppdraget om digitala prov (U2026/01377, 23 juli 2026).', 'U11-13')
ft = r['fulltext']; cut = ' Central rättning HT 2026: uppsatsdelarna i svenska/sva kurs 3 samt engelska kurs 6 i gymnasieskolan. Central rättning VT 2028: uppsatsdelarna i svenska/sva och engelska i årskurs 9.'
assert ft.count(cut) == 1
r['fulltext'] = ft.replace(cut, ' Skolverket redovisade uppdraget den 8 maj 2026 (U2026/00976). Uppdraget har ersatts av uppdraget om digitala prov (U2026/01377, 23 juli 2026).'); L('U11-13', 'fulltext')
r['kallor'].append({'text': 'Skolverkets redovisning 8 maj 2026', 'url': 'https://www.skolverket.se/sok-publikationer/publikationsserier/regeringsuppdrag/2026/redovisning-av-andring-av-uppdraget-att-digitalisera-de-nationella-proven'})
up['betyg']['relaterade'].append({
    'titel': 'Uppdrag om ett likvärdigt betygssystem',
    'kort': 'System för nationella slutprov, kalibrering och bedömningsstöd (U2026/01561, 3 sep 2026). Bedömningsstöd redovisas senast 15 jan 2027; slutprov och beräkning/rapportering slutredovisas 15 feb 2028; kalibrering 15 feb 2030.',
    'fulltext': 'Uppdrag till Statens skolverk om ett likvärdigt betygssystem (U2026/01561, 3 september 2026). Den del av uppdraget som rör bedömningsstöd redovisas senast den 15 januari 2027. Den del som avser nationella slutprov och den del som avser hur processerna för beräkning och rapportering ska utformas slutredovisas den 15 februari 2028. Den del som avser kalibrering slutredovisas den 15 februari 2030.',
    'kallor': [{'text': 'Regeringsbeslut U2026/01561 (PDF, via Skolverket)', 'url': 'https://www.skolverket.se/download/18.359c24d31a0a86b47d62daf/1789566333305/U2026_01561_Uppdrag-om-ett-likvardigt-betygssystem.pdf'}],
    'typ': 'uppdrag'}); L('U14', 'betyg')
ft = up['betyg']['fulltext']
assert ft.count('1 juli 2028: Ändringar i skollagen träder i kraft.') == 1
up['betyg']['fulltext'] = ft.replace('1 juli 2028: Ändringar i skollagen träder i kraft.', '2 juli 2028: Ändringar i skollagen träder i kraft (SFS 2026:1243).'); L('U15/B1', 'betyg.fulltext')
k = up['betyg']['kallor'][0]
setx(k, 'url', 'https://www.skolverket.se/styrning-och-ansvar/forandringar-inom-skolomradet/forberedelser-for-inforande-av-nytt-betygssystem',
     'https://www.skolverket.se/styrning-och-ansvar/en-skola-i-forandring/nytt-betygssystem', 'U16')
setx(k, 'text', 'Skolverket: förberedelser betygssystem', 'Skolverket: Nytt betygssystem', 'U16')
up['stod'].setdefault('relaterade', []).insert(0, {
    'titel': 'Uppdrag om framtagning av standardiserade tester',
    'kort': 'Framtagning av standardiserade tester (U2026/01274, 18 juni 2026). Ersätter uppdraget att förbereda framtagande av standardiserade tester (U2025/02022). Delredovisas senast 1 juni 2027, slutredovisas senast 1 juni 2028.',
    'fulltext': 'Uppdrag till Statens skolverk om framtagning av standardiserade tester (U2026/01274, 18 juni 2026). Uppdraget ersätter tidigare givet uppdrag att förbereda framtagande av standardiserade tester (U2025/02022). Uppdraget delredovisas senast den 1 juni 2027 och slutredovisas senast den 1 juni 2028.',
    'kallor': [{'text': 'Regeringsbeslut U2026/01274 (PDF, via Skolverket)', 'url': 'https://www.skolverket.se/download/18.667f30a619ed441dc0c6bf20/1783341393618/U2026_01274_Framtagning-av-standardiserade-tester.pdf'}],
    'typ': 'uppdrag'}); L('U17', 'stod')
up['stod']['kort'] = up['stod']['kort'] + ' Ersatt av uppdraget om framtagning av standardiserade tester (U2026/01274, 18 juni 2026).'; L('U17', 'stod.kort')
r = rel('studiero', 'Stödmaterial för att förebygga sexualbrott')
setx(r, 'kort', 'Stödmaterial för att förebygga sexualbrott och andra grova brott (RB 2025). Redovisas 18 feb 2026.',
     'Stödmaterial för att förebygga sexualbrott och andra grova brott (RB 2025). Redovisad 12 feb 2026.', 'U18')
r['kallor'].append({'text': 'Skolverkets redovisning', 'url': 'https://www.skolverket.se/sok-publikationer/publikationsserier/regeringsuppdrag/2026/stodmaterial-for-att-forebygga-sexualbrott-och-andra-grova-brott'})
SB_OLD = 'Nationell kartläggning och internationell lägesbild ska redovisas senast 29 maj 2026.'
SB_NEW = "Nationell kartläggning och internationell lägesbild redovisades 29 maj 2026 ('Att förebygga på plats – situationell brottsprevention i skolan')."
n19 = 0
r = rel('studiero', 'Situationell brottsprevention')
if SB_OLD in r['fulltext']: r['fulltext'] = r['fulltext'].replace(SB_OLD, SB_NEW); n19 += 1
r['kallor'].append({'text': 'Rapport: Att förebygga på plats', 'url': 'https://www.skolverket.se/sok-publikationer/publikationsserier/ovrigt-material/2026/att-forebygga-pa-plats---situationell-brottsprevention-i-skolan'})
if SB_OLD in up['studiero']['fulltext']: up['studiero']['fulltext'] = up['studiero']['fulltext'].replace(SB_OLD, SB_NEW); n19 += 1
assert n19 >= 1, 'U19'; L('U19', f'{n19} fält')
ft = up['sprak']['fulltext']
o20 = 'Stöd för uppföljning av barns språkutveckling i förskolan (RB 2025, punkt 12). Redovisas senast 5 juni 2026.'
assert ft.count(o20) == 1, ft[:300]
up['sprak']['fulltext'] = ft.replace(o20, 'Stöd för uppföljning av barns språkutveckling i förskolan (RB 2025, punkt 12). Redovisad 20 maj 2026.'); L('U20', 'sprak')
up['tioarig'].setdefault('relaterade', []).append({
    'titel': 'Förbereda fortbildning för förskollärare och lärare',
    'kort': 'Skolverket har redovisat förslag på fortbildning som kan ge legitimerade förskollärare och lärare behörighet att undervisa i årskurs 1–4 när den tioåriga grundskolan införs hösten 2028.',
    'fulltext': 'Skolverket föreslår fortbildning som kan ge legitimerade förskollärare och lärare behörighet att undervisa i årskurs 1–4 när den tioåriga grundskolan införs hösten 2028. Diarienummer och redovisningsdatum återges inte här (ej verifierade i revisionen 2026-11-10) — se källan.',
    'kallor': [{'text': 'Skolverket: Förbereda fortbildning för förskollärare och lärare', 'url': 'https://www.skolverket.se/sok-publikationer/publikationsserier/regeringsuppdrag/2026/forbereda-fortbildning-for-forskollarare-och-larare'}],
    'typ': 'uppdrag'}); L('U21', 'tioarig')
IU = {'titel': 'Stöd i tillämpningen av nya regler om informationsutbyte',
      'kort': 'Juridisk vägledning och stöd om nya regler om informationsutbyte (U2026/00991, 13 maj 2026). Vägledning redovisas senast 25 juni 2027; slutredovisning senast 15 december 2028.',
      'fulltext': 'Uppdrag till Statens skolverk om stöd i tillämpningen av nya regler om informationsutbyte (U2026/00991, 13 maj 2026). Uppdraget avser bl.a. uppgiftsskyldighet vid övergång mellan skolformer och vid byte av skolenhet (prop. 2025/26:192) och den sekretessbrytande bestämmelsen i 10 kap. 15 a § OSL som även kommer att kunna tillämpas av och i förhållande till enskilda huvudmän (prop. 2025/26:191). Juridisk vägledning redovisas senast den 25 juni 2027; uppdraget slutredovisas senast den 15 december 2028.',
      'kallor': [{'text': 'Regeringsuppdrag (U2026/00991)', 'url': 'https://www.regeringen.se/regeringsuppdrag/2026/05/uppdrag-till-statens-skolverk-om-stod-i-tillampningen-av-nya-regler-om-informationsutbyte/'}],
      'typ': 'uppdrag'}
for node in ('brott', 'offentlighet'):
    up[node].setdefault('relaterade', []).append(json.loads(json.dumps(IU))); L('U22', node)
setx(up['gy25']['kallor'][0], 'url', 'https://www.skolverket.se/styrning-och-ansvar/forandringar-inom-skolomradet/gy25----amnesbetyg-pa-gymnasial-niva',
     'https://www.skolverket.se/styrning-och-ansvar/en-skola-i-forandring/tidigare-forandringar/gy25----amnesbetyg-pa-gymnasial-niva', 'U23')
setx(up['skolpeng'], 'kort', 'Utredning pågår. Inget uppdrag till Skolverket.',
     'Slutbetänkande lämnat (SOU 2026:65, 29 okt 2026). Inget uppdrag till Skolverket.', 'U24')

# ======================= tidslinje.json =======================
tl = json.load(open(P('data/tidslinje.json'), encoding='utf-8'))
H = tl['handelser']
def ev(i):
    h = [x for x in H if x['id'] == i]; assert len(h) == 1, i; return h[0]
for i, tag in (('laroplaner-remiss', 'T1'), ('riksdag-q2-2026', 'T2'), ('studiero-delar-ikraft', 'T7/B2'),
               ('central-rattning-gy', 'T10/B3'), ('central-rattning-grundskola', 'T10/B3')):
    H.remove(ev(i)); L(tag, f'strök {i}')
setx(ev('laroplaner-forslag'), 'kalla', 'U2025/02427, senarelagt U2026/00888', 'U2025/02427, senarelagt U2026/01483', 'T3')
setx(ev('laroplaner-forslag'), 'titel', 'Förslag till nya kursplaner lämnas till regeringen', 'Omarbetade förslag till nya läro- och kursplaner lämnas till regeringen', 'T4')
setx(ev('betyg-ikraft'), 'datum', '2028-07-01', '2028-07-02', 'B1')
setx(ev('betyg-ikraft'), 'kalla', 'Prop. 2025/26:197', 'Prop. 2025/26:197, SFS 2026:1243', 'B1')
setx(ev('laroplaner-ikraft'), 'kalla', 'Prop. 2025/26:194', 'Prop. 2025/26:194, SFS 2026:1242', 'B1')
setx(ev('stod-ikraft'), 'kalla', 'Prop. 2025/26:195', 'Prop. 2025/26:195, SFS 2026:1242', 'B1')
setx(ev('undervisningstid-ikraft'), 'kalla', 'Prop. 2025/26:196', 'Prop. 2025/26:196, SFS 2026:1097', 'B1')
NYA_H = [
    {'id': 'tid-krankande-ikraft', 'typ': 'ikraftträdande', 'datum': '2026-08-01', 'titel': 'Ändringarna om kränkande behandling träder i kraft', 'reform': 'tid', 'kategori': 'larare', 'kalla': 'Prop. 2025/26:196, SFS 2026:1096'},
    {'id': 'vinst-ikraft', 'typ': 'ikraftträdande', 'datum': '2027-07-01', 'titel': 'Skärpta villkor för friskolesektorn träder i kraft', 'reform': 'vinst', 'kategori': 'styrning', 'kalla': 'Prop. 2025/26:292, SFS 2026:1634'},
    {'id': 'tid-samordning-ikraft', 'typ': 'ikraftträdande', 'datum': '2028-07-02', 'titel': 'Tid för undervisningsuppdraget — övriga ändringar träder i kraft', 'reform': 'tid', 'kategori': 'larare', 'kalla': 'Prop. 2025/26:196, SFS 2026:1243'},
]
# håll kronologisk ordning som filen har (kvartal 'YYYY-Qn' sorteras som kvartalets start)
def sk(h):
    d = h['datum']
    if '-Q' in d: y, q = d.split('-Q'); return f'{y}-{(int(q)-1)*3+1:02d}-01'
    return d
for nh in NYA_H:
    pos = next((n for n, x in enumerate(H) if sk(x) > sk(nh)), len(H))
    H.insert(pos, nh)
L('T8T9', '3 nya händelser insatta på datumposition (övrig ordning orörd)')

# ======================= andringar.json =======================
an = json.load(open(P('data/andringar.json'), encoding='utf-8'))
def post(datum, rid):
    h = [a for a in an if a['datum'] == datum and rid in a['reform_ids']]; assert len(h) == 1, (datum, rid); return h[0]
p = post('2026-08-24', 'laroplaner')
setx(p, 'datum', '2026-08-24', '2026-08-20', 'A1')
setx(p['kalla'], 'text', 'Regeringsuppdrag (U2026/00888)', 'Regeringsuppdrag (U2026/01483)', 'A1')
setx(post('2026-08-13', 'vinst')['kalla'], 'text', 'Riksdagsbeslut — bet. 2025/26:UbU30', 'Riksdagsbeslut — bet. 2025/26:UbU30, rskr. 2025/26:438', 'A2')
setx(post('2026-06-09', 'tid'), 'text',
     'Riksdagen beslutade om propositionen Tid för undervisningsuppdraget (prop. 2025/26:196). Ikraftträdande stegvis: 1 augusti 2026, 1 juli 2027 och 1 juli 2028 (SFS 2026:1096/1097/1243).',
     'Riksdagen beslutade om propositionen Tid för undervisningsuppdraget (prop. 2025/26:196). Ikraftträdande stegvis: 1 augusti 2026, 1 juli 2027 och 2 juli 2028 (SFS 2026:1096/1097/1243).', 'A3')
setx(post('2026-06-09', 'betyg'), 'text',
     'Riksdagen beslutade om ett nytt betygssystem med skalan 1–10 (prop. 2025/26:197). Skollagsändringarna träder i kraft 1 juli 2028; ny betygsskala införs stegvis från höstterminen 2027.',
     'Riksdagen beslutade om ett nytt betygssystem med skalan 1–10 (prop. 2025/26:197). Skollagsändringarna träder i kraft 2 juli 2028 (SFS 2026:1243); ny betygsskala införs stegvis från höstterminen 2027.', 'A4/B1')
setx(post('2026-06-03', 'laroplaner'), 'text',
     'Riksdagen beslutade om nya läroplaner och en tydligare kunskapsinriktning (prop. 2025/26:194). Merparten träder i kraft 1 juli 2028.',
     'Riksdagen beslutade om nya läroplaner och en tydligare kunskapsinriktning (prop. 2025/26:194). Ikraftträdande 1 juli 2028 (SFS 2026:1242) och 2 juli 2028 (SFS 2026:1243).', 'B1')
setx(post('2026-06-03', 'stod'), 'text',
     'Riksdagen beslutade om förbättrat stöd och stärkt elevhälsa (prop. 2025/26:195). Ikraftträdande 1 juli 2028.',
     'Riksdagen beslutade om förbättrat stöd och stärkt elevhälsa (prop. 2025/26:195). Ikraftträdande 1 juli 2028 (SFS 2026:1242).', 'B1')
setx(post('2026-05-27', 'yrkes'), 'text',
     'Riksdagen beslutade om en reformerad yrkesutbildning (prop. 2025/26:198). Entreprenad och rätt att fullfölja träder i kraft 1 juli 2026; övriga ändringar 2 juli 2028.',
     'Riksdagen beslutade om en reformerad yrkesutbildning (prop. 2025/26:198). Entreprenad och rätt att fullfölja träder i kraft 1 juli 2026; övriga ändringar 1 juli 2028 (SFS 2026:1242) och 2 juli 2028 (SFS 2026:1243).', 'B1')
setx(post('2026-06-03', 'studiero'), 'text',
     'Riksdagen beslutade om stärkt trygghet och studiero i skolan (prop. 2025/26:193). Merparten träder i kraft 1 augusti 2026.',
     'Riksdagen beslutade om stärkt trygghet och studiero i skolan (prop. 2025/26:193). Lagändringarna börjar gälla 1 augusti 2026.', 'B2')
an.sort(key=lambda a: a['datum'], reverse=True)  # stabil sort: bara A1 (08-24→08-20) kan flytta

# ======================= utredningar.json (strängbyten) =======================
U = open(P('data/utredningar.json'), encoding='utf-8').read()
def S(old, new, tag, n=1):
    global U
    c = U.count(old)
    if c != n: raise SystemExit(f'[{tag}] utredningar.json: väntade {n}, fick {c}: {old[:100]!r}')
    U = U.replace(old, new); L(tag, 'utredningar.json')
for nr, old, new, tag in [
    ('2023:120', '2023-08-14', '2023-08-10', 'D1'), ('2021:89', '2021-10-21', '2021-10-20', 'D2'),
    ('2023:34', '2023-03-09', '2023-03-02', 'D3'), ('2023:31', '2023-03-09', '2023-02-23', 'D4'),
    ('2023:114', '2023-07-06', '2023-07-13', 'D5'), ('2024:85', '2024-09-26', '2024-09-19', 'D6'),
    ('2023:153', '2023-10-19', '2023-11-02', 'D7'), ('2025:102', '2025-12-05', '2025-11-27', 'D8'),
    ('2025:98', '2025-11-17', '2025-11-13', 'D9'), ('2026:39', '2026-05-29', '2026-05-28', 'D10'),
    ('2025:111', '2025-12-29', '2025-12-18', 'D11'), ('2026:98', '2026-08-28', '2026-08-27', 'D12'),
    ('2025:39', '2025-04-28', '2025-04-16', 'D13'), ('2025:64', '2025-06-18', '2025-06-19', 'D14')]:
    S(f'"nr": "Dir. {nr}", "datum": "{old}"', f'"nr": "Dir. {nr}", "datum": "{new}"', tag)
S('"tillsatt": "2023-10-19",\n    "redovisning": "2026-11-01"', '"tillsatt": "2023-11-02",\n    "redovisning": "2026-11-01"', 'D15')
S('"tillsatt": "2021-10-21"', '"tillsatt": "2021-10-20"', 'D16')
for nr, titel, tag in [
    ('2025:18', 'Tilläggsdirektiv till Utredningen om en förbättrad elevhälsa', 'D17'),
    ('2025:62', 'Tilläggsdirektiv till Utredningen om en förbättrad elevhälsa', 'D18'),
    ('2024:79', 'Tilläggsdirektiv till utredningen Stärkt trygghet och studiero i skolan', 'D19'),
    ('2023:22', 'Tilläggsdirektiv till utredningen om att säkerheten i skolan ska förbättras', 'D20'),
    ('2022:10', 'Tilläggsdirektiv till Skolinformationsutredningen', 'D21'),
    ('2023:23', 'Tilläggsdirektiv till Skolinformationsutredningen', 'D21'),
    ('2023:34', 'Tilläggsdirektiv till Skolinformationsutredningen', 'D21'),
    ('2023:31', 'Tilläggsdirektiv till Utredningen om fler vägar till arbetslivet', 'D22'),
    ('2023:114', 'Tilläggsdirektiv till Utredningen om fler vägar till arbetslivet', 'D22'),
    ('2023:110', 'Tilläggsdirektiv till Yrkesvuxutredningen', 'D23'),
    ('2022:102', 'En skola utan vinstintresse', 'D24'),
    ('2024:85', 'Tilläggsdirektiv till Utredningen om vinst i skolan', 'D25'),
    ('2025:39', 'Tilläggsdirektiv till Utredningen om en reform av den statliga barn- och ungdomsvården för en trygg och kvalitativ vård', 'D26'),
    ('2024:48', 'Bättre förutsättningar för rektorerna inom skolväsendet', 'D27'),
    ('2025:50', 'Tilläggsdirektiv till Utredningen om bättre förutsättningar för rektorerna inom skolväsendet', 'D28')]:
    i = U.index(f'"nr": "Dir. {nr}"'); j = U.index('}', i)
    seg = U[i:j]
    if seg.count('"titel": null') != 1: raise SystemExit(f'[{tag}] Dir. {nr}: titel ej null: {seg!r}')
    U = U[:i] + seg.replace('"titel": null', f'"titel": "{titel}"') + U[j:]; L(tag, f'Dir. {nr}.titel')
S('{ "nr": "Dir. 2025:111", "datum": "2025-12-18", "typ": "tilläggs", "titel": "Tilläggsdirektiv till Utredningen om tydligare regler vid undantag från skolplikten" }\n',
  '{ "nr": "Dir. 2025:111", "datum": "2025-12-18", "typ": "tilläggs", "titel": "Tilläggsdirektiv till Utredningen om tydligare regler vid undantag från skolplikten" },\n      { "nr": "Dir. 2026:117", "datum": "2026-09-03", "typ": "tilläggs", "titel": "Tilläggsdirektiv till Utredningen om tydligare regler vid undantag från skolplikten" }\n', 'D29')
S('"redovisning": "2026-11-18"', '"redovisning": "2027-03-31"', 'D30')
S('"noteringar": "Dir. 2025:77 beslutades i juli 2025 (exakt datum ej verifierat). cat satt redaktionellt."',
  '"noteringar": "Dir. 2025:77 beslutades i juli 2025 (exakt datum ej verifierat). cat satt redaktionellt. Dir. 2026:117 (beslut 2026-09-03) förlängde utredningstiden till 2027-03-31 (data.riksdagen.se/dokument/HEB1117)."', 'D30')
S('{ "nr": "Dir. 2025:91", "datum": "2025-10-09", "typ": "huvud", "titel": "En åldersgräns på sociala medier" }\n',
  '{ "nr": "Dir. 2025:91", "datum": "2025-10-09", "typ": "huvud", "titel": "En åldersgräns på sociala medier" },\n      { "nr": "Dir. 2026:123", "datum": "2026-10-22", "typ": "tilläggs", "titel": "Tilläggsdirektiv till Utredningen om en åldersgräns på sociala medier" }\n', 'D31')
S('"redovisning": "2026-11-14"', '"redovisning": "2026-12-31"', 'D32')
S('{ "nr": "SOU 2026:35", "titel": "En åldersgräns för barns tillgång till sociala medier", "typ": "del", "datum": null }',
  '{ "nr": "SOU 2026:35", "titel": "En åldersgräns för barns tillgång till sociala medier", "typ": "del", "datum": "2026-06-02" }', 'S4')
S('"noteringar": "Indirekt påverkan. Delredovisning 2026-06-12, slutredovisning 2026-11-14. SOU 2026:35 lämnad (datum ej verifierat). cat satt redaktionellt."',
  '"noteringar": "Indirekt påverkan. Delredovisning 2026-06-12. SOU 2026:35 publicerad 2026-06-02 (regeringen.se; saknas i riksdagens öppna data). Dir. 2026:123 (beslut 2026-10-22) förlängde slutredovisningen från 2026-11-14 till 2026-12-31. cat satt redaktionellt."', 'D32')
S('{ "nr": "Dir. 2025:39", "datum": "2025-04-16", "typ": "tilläggs", "titel": "Tilläggsdirektiv till Utredningen om en reform av den statliga barn- och ungdomsvården för en trygg och kvalitativ vård" }\n',
  '{ "nr": "Dir. 2025:39", "datum": "2025-04-16", "typ": "tilläggs", "titel": "Tilläggsdirektiv till Utredningen om en reform av den statliga barn- och ungdomsvården för en trygg och kvalitativ vård" },\n      { "nr": "Dir. 2025:95", "datum": "2025-10-30", "typ": "tilläggs", "titel": "Tilläggsdirektiv till utredningen En reform av den statliga barn- och ungdomsvården för en trygg och kvalitativ vård" }\n', 'D33')
S('"redovisning": "2026-03-02"', '"redovisning": "2026-08-11"', 'D34')
S('{ "nr": "Dir. 2023:175", "datum": "2023-12-14", "typ": "huvud", "titel": "Införande av grundläggande svenska och översyn av modersmålsundervisningen" }\n',
  '{ "nr": "Dir. 2023:175", "datum": "2023-12-14", "typ": "huvud", "titel": "Införande av grundläggande svenska och översyn av modersmålsundervisningen" },\n      { "nr": "Dir. 2024:72", "datum": "2024-08-22", "typ": "tilläggs", "titel": "Tilläggsdirektiv till Utredningen om införande av grundläggande svenska och översyn av modersmålsundervisningen" }\n', 'D35')
S('{ "nr": null, "titel": null, "typ": "del", "datum": "2025-03-28" }',
  '{ "nr": "SOU 2025:37", "titel": "Skärpta villkor för friskolesektorn", "typ": "del", "datum": "2025-03-28" }', 'S1')
S('Huvuddirektivets titel och delbetänkandets SOU-nummer/titel (2025-03-28) ej verifierade.',
  'Huvuddirektivets titel och delbetänkandets SOU-nummer/titel verifierade 2026-11-10 mot riksdagens öppna data (HAB1102, HDB337); riksdagen anger SOU 2025:37:s publiceringsdatum 2025-04-08, datumet 2025-03-28 är överlämningsdatum enligt tidigare research.', 'S1')
S('"kallor": [ { "text": "Dir. 2022:102", "url": "https://www.regeringen.se/rattsliga-dokument/kommittedirektiv/2022/06/dir.-2022102" } ]',
  '"kallor": [ { "text": "Dir. 2022:102", "url": "https://data.riksdagen.se/dokument/HAB1102.html" } ]', 'R14')
S('{ "nr": "SOU 2025:72", "titel": "Verktyg för en mer likvärdig resursfördelning till skolan", "typ": "del", "datum": "2025-06-12" }\n',
  '{ "nr": "SOU 2025:72", "titel": "Verktyg för en mer likvärdig resursfördelning till skolan", "typ": "del", "datum": "2025-06-12" },\n      { "nr": "SOU 2026:65", "titel": "Verktyg för en mer likvärdig resursfördelning", "typ": "slut", "datum": "2026-10-29" }\n', 'S2')
S('"status": "pagaende",\n    "cat": "styrning",\n    "utredare": "Lena Holmdahl"', '"status": "avslutad",\n    "cat": "styrning",\n    "utredare": "Lena Holmdahl"', 'S3')
S('Delbetänkandet SOU 2025:72 utgör skolpeng-reformens nuvarande status. Slutbetänkande (gymnasiet) väntas nov 2026."',
  'Delbetänkandet SOU 2025:72 utgör skolpeng-reformens nuvarande status. Slutbetänkandet SOU 2026:65 (gymnasieskolan och anpassade gymnasieskolan) lämnat 2026-10-29."', 'S2')
S('{ "nr": "SOU 2025:19", "titel": "Kunskap för alla', '{ "nr": "SOU 2025:19", "titel": "Kunskap för alla', 'S5chk')
i = U.index('"nr": "SOU 2025:19"'); j = U.index('}', i); seg = U[i:j]
assert seg.count('"datum": "2024-12-20"') == 1, seg
U = U[:i] + seg.replace('"datum": "2024-12-20"', '"datum": "2025-02-26"') + U[j:]; L('S5', 'SOU 2025:19.datum')
S('"redovisning": "2026-10-16"', '"redovisning": "2027-11-30"', 'L1')
i = U.index('"id": "utr-barnungdomsvard-styrning"'); j = U.index('"noteringar": "', i); k = U.index('"\n', j + 15)
U = U[:j] + '"noteringar": "Indirekt påverkan via samverkan socialtjänst–skola. Utredare ej verifierad (sammanställningens uppgift föreföll felaktig). cat satt redaktionellt. Dir. 2026:98 (beslut vid regeringssammanträde 2026-08-27) utvidgar uppdraget: utredaren ska kartlägga förekomsten av hot och våld mot personal och förtroendevalda vid handläggningen av ärenden som gäller barn och unga enligt socialtjänstlagen och LVU, analysera och ta ställning till deras behov av skydd och stöd, lämna förslag på åtgärder för att minska utsattheten och lämna nödvändiga författningsförslag. Utredningstiden förlängs från 2026-10-16 till 2027-11-30. Riksdagens metadata anger kommittébeteckning S 2025:06 för Dir. 2026:98, men direktivets titel anger S 2025:08 och texten utvidgar dir. 2025:74 — källfel i metadata, kopplingen hit är korrekt."' + U[k + 1:]; L('L2', 'noteringar')

# Nya spårade utredningar (beslut B1/B4/B5 + godkända B2/B3). cat ärvs från kopplad_reform.
def ny(id_, bet, titel, dep, utredare, tillsatt, red, direktiv, kopplad, kallor, not_):
    cat = RF[kopplad]['cat']
    d = ',\n'.join('      ' + json.dumps(x, ensure_ascii=False).replace('{"', '{ "').replace('"}', '" }').replace('", "', '", "').replace('null}', 'null }') for x in direktiv)
    dlist = '[\n' + d + '\n    ]' if direktiv else '[]'
    k = ', '.join(json.dumps(x, ensure_ascii=False).replace('{"', '{ "').replace('"}', '" }') for x in kallor)
    return (',\n  {\n'
            f'    "id": "{id_}",\n    "beteckning": {json.dumps(bet, ensure_ascii=False)},\n    "titel": "{titel}",\n'
            f'    "dep": "{dep}",\n    "status": "pagaende",\n    "cat": "{cat}",\n    "utredare": {json.dumps(utredare, ensure_ascii=False)},\n'
            f'    "tillsatt": "{tillsatt}",\n    "redovisning": "{red}",\n    "direktiv": {dlist},\n    "betankanden": [],\n'
            f'    "prop": null,\n    "kopplad_reform": "{kopplad}",\n    "kallor": [ {k} ],\n    "noteringar": {json.dumps(not_, ensure_ascii=False)}\n  }}')
nya = [
  ny('utr-svenskamnen', None, 'Utredningen om en översyn av svenskämnenas indelning', 'Utbildningsdepartementet', None, '2026-09-03', '2027-12-06',
     [{'nr': 'Dir. 2026:107', 'datum': '2026-09-03', 'typ': 'huvud', 'titel': 'En översyn av svenskämnenas indelning'}], 'laroplaner',
     [{'text': 'Dir. 2026:107', 'url': 'https://data.riksdagen.se/dokument/HEB1107.html'}],
     'Uppdraget enligt direktivet: en särskild utredare ska se över konstruktionen av ämnena svenska och svenska som andraspråk och lämna förslag som innebär att ämnena antingen delas in på ett annat sätt än i dag eller slås samman till ett ämne med två kursplaner, varav den ena ska avse grundläggande svenska. Kommittébeteckning ännu ej angiven i riksdagens data (2026-11-10). Utredare ej verifierad. Spåras enligt beslut 2026-11-10 (Sprint 14), kopplad till laroplaner; cat ärvd via kopplad_reform.'),
  ny('utr-forskola-sprak-obligatorisk', None, 'Uppdrag att föreslå obligatorisk förskola med språkutvecklande insatser', 'Utbildningsdepartementet', 'Camilla Mårtensen', '2026-09-03', '2027-09-01',
     [], 'sprak',
     [{'text': 'Uppdrag U2026/01573', 'url': 'https://www.regeringen.se/rattsliga-dokument/kommittedirektiv/2026/09/u202601573/'}, {'text': 'Pressmeddelande 2026-09-04', 'url': 'https://www.regeringen.se/pressmeddelanden/2026/09/ny-utredning-om-obligatorisk-forskola-med-sprakutvecklande-insatser-for-barn-som-inte-moter-det-svenska-spraket-hemma/'}],
     'Departementsuppdrag (regeringskanslibeslut U2026/01573, 2026-09-03), inget kommittédirektivnummer — syns därför inte i riksdagens öppna data. En utredare ges i uppdrag att lämna författningsförslag som innebär att förskola med språkutvecklande insatser ska vara obligatorisk om barnet bedöms behöva sådant stöd för att det inte exponeras i tillräcklig utsträckning för det svenska språket i hemmiljön. Kompletterar förslagen i SOU 2026:37. Utredare enligt pressmeddelandet. Detta är förskoledirektivet som aviserades 2026-08-31; cat ärvd via kopplad_reform.'),
  ny('utr-skarpta-villkor-huvudman', None, 'Uppdrag att utreda vissa skärpta villkor för enskilda huvudmän inom skolväsendet', 'Utbildningsdepartementet', None, '2026-09-01', '2027-09-30',
     [], 'vinst',
     [{'text': 'Uppdrag U2026/01547', 'url': 'https://www.regeringen.se/rattsliga-dokument/kommittedirektiv/2026/09/u202601547/'}],
     'Departementsuppdrag (U2026/01547, 2026-09-01): en utredare ska biträda Regeringskansliet (Utbildningsdepartementet). Utredaren ska bl.a. lämna förslag till ett generellt förbud för fysiska och juridiska personer med hemvist eller säte utanför EU eller EES att genom direkt eller indirekt ägande ha ett väsentligt inflytande över en enskild huvudman inom skolväsendet, och lämna nödvändiga författningsförslag. Utredare ej verifierad. cat ärvd via kopplad_reform.'),
  ny('utr-valdsdad-skolmiljo', None, 'Utredningen om åtgärder för att förebygga och förhindra allvarliga våldsdåd i skolmiljöer', 'Justitiedepartementet', None, '2026-09-03', '2028-05-31',
     [{'nr': 'Dir. 2026:105', 'datum': '2026-09-03', 'typ': 'huvud', 'titel': 'Åtgärder för att förebygga och förhindra allvarliga våldsdåd i skolmiljöer'}], 'brott',
     [{'text': 'Dir. 2026:105', 'url': 'https://data.riksdagen.se/dokument/HEB1105.html'}],
     'Uppdraget enligt direktivet: en särskild utredare ska kartlägga de allvarliga våldsdåd i skolmiljöer som skett i Sverige de senaste 15 åren, analysera berörda aktörers insatser före, under och efter dåden och ta ställning till om fler åtgärder behöver vidtas. Departementsöverskridande (Ju-dep) — spåras enligt relevansregeln DEC-020, kopplad till brott enligt beslut 2026-11-10. Utredare ej verifierad. cat ärvd via kopplad_reform.'),
  ny('utr-nationell-yrkesutbildning', None, 'Uppdrag att utreda nationell yrkesutbildning', 'Utbildningsdepartementet', None, '2026-09-03', '2027-03-31',
     [], 'yrkes',
     [{'text': 'Uppdrag U2026/01569', 'url': 'https://www.regeringen.se/rattsliga-dokument/kommittedirektiv/2026/09/u202601569/'}, {'text': 'Pressmeddelande 2026-09-08', 'url': 'https://www.regeringen.se/pressmeddelanden/2026/09/utredning-tillsatts-for-ett-eventuellt-permanentande-av-nationell-yrkesutbildning/'}],
     'Departementsuppdrag (U2026/01569, 2026-09-03). Uppdraget: omhänderta erfarenheter från pilotverksamheten med nationell yrkesutbildning och föreslå författningsreglering som möjliggör ett eventuellt permanent införande av utbildningsformen, samt analysera hur den kan vara ett komplement till andra yrkesutbildningar på gymnasial nivå. Utredare ej verifierad. Spåras enligt beslut 2026-11-10, kopplad till yrkes; cat ärvd via kopplad_reform.'),
]
assert U.rstrip().endswith('}\n]') or U.rstrip().endswith('}\n]'.strip())
idx = U.rstrip().rfind(']')
body = U[:idx].rstrip()
assert body.endswith('}')
U = body + ''.join(nya) + '\n]\n'
L('B1-5', '5 nya utredningar')

# ======================= guide.json (strängbyten) =======================
G = open(P('data/guide.json'), encoding='utf-8').read()
def GS(old, new, tag, n=1):
    global G
    c = G.count(old)
    if c != n: raise SystemExit(f'[{tag}] guide.json: väntade {n}, fick {c}: {old[:100]!r}')
    G = G.replace(old, new); L(tag, 'guide.json')
def gblock(rid):
    i = G.index(f'"reform_id": "{rid}"'); j = G.find('"reform_id": "', i + 10)
    return i, (j if j > 0 else len(G))
def GB(rid, old, new, tag, n=1):
    global G
    i, j = gblock(rid); seg = G[i:j]; c = seg.count(old)
    if c != n: raise SystemExit(f'[{tag}] guide {rid}: väntade {n}, fick {c}: {old[:100]!r}')
    G = G[:i] + seg.replace(old, new) + G[j:]; L(tag, f'guide.{rid}')
# tid — G1 G2 G3 G10
GB('tid', '{ "datum": "2028-07-01", "typ": "ikraft", "omfattning": "Övriga ändringar börjar gälla den 1 juli 2028 (SFS 2026:1243)" }',
   '{ "datum": "2028-07-02", "typ": "ikraft", "omfattning": "Övriga ändringar börjar gälla den 2 juli 2028 (SFS 2026:1243)" }', 'G1G2')
GB('tid', '"text": "Denna lag träder i kraft den 1 juli 2028.",\n        "kalla": { "text": "Prop. 2025/26:196, lagförslag 2.3", "url": "https://data.riksdagen.se/dokument/HD03196.html" }',
   '"text": "1. Denna lag träder i kraft den 2 juli 2028.",\n        "kalla": { "text": "SFS 2026:1243 (samordningslag, bet. 2025/26:UbU26), ikraftträdande- och övergångsbestämmelser", "url": "' + SFS800 + '" }', 'G3')
GB('tid', 'sfs: kammarbeslut 2026-06-09, författning ej kungjord vid inmatning.',
   'sfs: tre lagar — SFS 2026:1096 (1 augusti 2026), 2026:1097 (1 juli 2027) och 2026:1243 (2 juli 2028); fältet är enkelvärt och lämnas null, SFS-numren står i omfattning (verifierat mot lagen.nu:s förarbetesregister 2026-11-10). ' + NOT_1243 + ' Prop. 2025/26:196 saknade övergångsbestämmelser för det tredje lagförslaget; utskottet samordnade det i SFS 2026:1243 (bet. 2025/26:UbU26).', 'G10/B1')
# betyg — G4 G5 G11
GB('betyg', '{ "datum": "2028-07-01", "typ": "ikraft", "omfattning": "Ändringarna i skollagen börjar i huvudsak gälla den 1 juli 2028" }',
   '{ "datum": "2028-07-02", "typ": "ikraft", "omfattning": "Ändringarna i skollagen börjar gälla den 2 juli 2028 (SFS 2026:1243)" }', 'G4/B1')
GB('betyg', '"omfattning": "För kommunal vuxenutbildning börjar ändringarna gälla den 1 januari 2031" }',
   '"omfattning": "För kommunal vuxenutbildning börjar ändringarna gälla den 1 januari 2031 (SFS 2026:1245)" }', 'B1')
i, j = gblock('betyg'); seg = G[i:j]
o = '{ "datum": "2031-01-01", "typ": "ikraft"'
assert seg.count(o) == 1
seg = seg.replace(o, '{ "datum": "2030-07-01", "typ": "ikraft", "omfattning": "Lagändringarna i SFS 2026:1244 börjar gälla den 1 juli 2030 och tillämpas första gången på utbildning som påbörjas efter den 30 juni 2031" },\n      ' + o)
G = G[:i] + seg + G[j:]; L('G5', 'guide.betyg')
GB('betyg', '"text": "1. Denna lag träder i kraft den 1 juli 2028. 2. Lagen tillämpas första gången i fråga om',
   '"text": "1. Denna lag träder i kraft den 2 juli 2028. 2. Lagen tillämpas första gången i fråga om', 'G4/B1')
i, j = gblock('betyg'); seg = G[i:j]
k = seg.index('"text": "1. Denna lag träder i kraft den 2 juli 2028.')
kk = seg.index('"kalla": {', k); ke = seg.index('}', kk) + 1
assert 'Prop. 2025/26:197' in seg[kk:ke], seg[kk:ke]
seg = seg[:kk] + '"kalla": { "text": "SFS 2026:1243 (samordningslag, bet. 2025/26:UbU26), ikraftträdande- och övergångsbestämmelser", "url": "' + SFS800 + '" }' + seg[ke:]
G = G[:i] + seg + G[j:]; L('G4/B1', 'betyg punkt 1–2 källa → SFS 2026:1243 (punkt 3–4 behåller prop-källan)')
GB('betyg', '"sfs": null', '"sfs": "2026:1243"', 'G11')
GB('betyg', 'sfs: kammarbeslut 2026-06-09, författning ej kungjord vid inmatning.',
   'sfs: 2026:1243 (2 juli 2028); reformen ingår även i SFS 2026:1244 (1 juli 2030) och 2026:1245 (1 januari 2031) enligt lagen.nu:s förarbetesregister (verifierat 2026-11-10). ' + NOT_1243, 'G11/B1')
# laroplaner — G12 + nytt steg 2028-07-02
GB('laroplaner', '"omfattning": "Merparten av lagändringarna börjar gälla den 1 juli 2028. Nya läroplaner',
   '"omfattning": "Lagändringarna i SFS 2026:1242 börjar gälla den 1 juli 2028. Nya läroplaner', 'B1')
i, j = gblock('laroplaner'); seg = G[i:j]
o = '{ "datum": "2031-01-01", "typ": "ikraft", "omfattning": "Lagförslaget om ändring i skollagen avseende kommunal vuxenutbildning träder i kraft den 1 januari 2031" }'
assert seg.count(o) == 1
seg = seg.replace(o, '{ "datum": "2028-07-02", "typ": "ikraft", "omfattning": "Ändringarna i samordningslagen SFS 2026:1243 börjar gälla den 2 juli 2028" },\n      ' + o.replace('1 januari 2031" }', '1 januari 2031 (SFS 2026:1245)" }'))
G = G[:i] + seg + G[j:]; L('B1', 'guide.laroplaner steg')
GB('laroplaner', '"sfs": null', '"sfs": "2026:1242"', 'G12')
GB('laroplaner', 'sfs: kammarbeslut 2026-06-03, författning ej kungjord vid inmatning.',
   'sfs: 2026:1242 (1 juli 2028); reformen ingår även i SFS 2026:1243 (2 juli 2028) och 2026:1245 (1 januari 2031) enligt lagen.nu:s förarbetesregister (verifierat 2026-11-10). ' + NOT_1243, 'G12/B1')
# stod G6, studiero G7, register G8, timplan G9, brott G13 G14, offentlighet G15
GB('stod', '"omfattning": "Ändringarna i skollagen börjar gälla den 1 juli 2028" }', '"omfattning": "Ändringarna i skollagen börjar gälla den 1 juli 2028 (SFS 2026:1242)" }', 'B1')
GB('stod', '"sfs": null', '"sfs": "2026:1242"', 'G6')
GB('stod', 'sfs: kammarbeslut 2026-06-03, författning ej kungjord vid inmatning.', 'sfs: 2026:1242 (lagen.nu:s förarbetesregister, verifierat 2026-11-10).', 'G6')
GB('studiero', '"sfs": null', '"sfs": "2026:1198"', 'G7')
GB('studiero', 'sfs: kammarbeslut 2026-06-03, författning ej kungjord vid inmatning.', 'sfs: 2026:1198 (ikraft 2026-08-01; lagen.nu:s förarbetesregister och SFS-texten, verifierat 2026-11-10).', 'G7')
GB('register', '"sfs": null', '"sfs": "2026:760"', 'G8')
GB('register', 'sfs: kammarbeslut 2026-05-27, författning ej kungjord vid inmatning.', 'sfs: 2026:760 (skollagen; lagen.nu:s förarbetesregister, verifierat 2026-11-10).', 'G8')
GB('timplan', '"sfs": null', '"sfs": "2023:943"', 'G9')
GB('brott', '"sfs": null', '"sfs": "2026:734"', 'G13')
GB('brott', 'sfs: kammarbeslut 2026-05-27, författning ej kungjord vid inmatning.',
   'sfs: 2026:734 (guidens övergångstext är ordagrant dess); prop. 2025/26:192 gav även SFS 2026:735, 2026:736 och 2026:737 (lagen.nu, verifierat 2026-11-10).', 'G13')
GB('brott', '"omfattning": "Bestämmelserna tillämpas första gången på utbildning och annan verksamhet som bedrivs efter den 31 december 2026" }',
   '"omfattning": "Bestämmelserna tillämpas första gången på utbildning och annan verksamhet som bedrivs efter den 31 december 2026" },\n      { "datum": "2028-01-01", "typ": "tillampning", "omfattning": "Ändringen i 3 kap. 12 k § skollagen (SFS 2026:737, i kraft 1 juli 2026) tillämpas första gången på utbildning och annan verksamhet som bedrivs efter den 31 december 2027" }', 'G14/B10')
GB('offentlighet', '"sfs": null', '"sfs": "2026:714"', 'G15')
GB('offentlighet', 'sfs: kammarbeslut 2026-05-26, författning ej kungjord vid inmatning.',
   'sfs: 2026:714 (offentlighets- och sekretesslagen; guidens övergångstext är ordagrant dess). Skollagsdelen är SFS 2026:716 (lagen.nu, verifierat 2026-11-10).', 'G15')
# yrkes G16 + steg (beslut 10: förarbetena till 1242 och 1245 anger prop. 198)
GB('yrkes', '{ "datum": "2028-07-02", "typ": "ikraft", "omfattning": "Övriga lagändringar 2 juli 2028" }',
   '{ "datum": "2028-07-01", "typ": "ikraft", "omfattning": "Lagändringarna i SFS 2026:1242 börjar gälla 1 juli 2028" },\n      { "datum": "2028-07-02", "typ": "ikraft", "omfattning": "Övriga lagändringar 2 juli 2028 (SFS 2026:1243)" },\n      { "datum": "2031-01-01", "typ": "ikraft", "omfattning": "Lagändringarna i SFS 2026:1245 börjar gälla 1 januari 2031" }', 'G16/B10')
GB('yrkes', "steg 2-lagens (2028-07-02) SFS-nummer ej verifierat.",
   "steg 2 = SFS 2026:1243 (2 juli 2028); prop. 2025/26:198 ingår även i SFS 2026:1242 (1 juli 2028) och 2026:1245 (1 januari 2031) enligt lagen.nu:s förarbetesregister (verifierat 2026-11-10). " + NOT_1243, 'G16/B1')
GB('profession', "senareläggningslagens eget SFS-nummer ej verifierat (propen anger '2024:000').",
   "senareläggningslagen är SFS 2024:1074 (prop. 2023/24:166, bet. 2024/25:UbU4, rskr. 2024/25:40; lagen.nu:s förarbetesregister, verifierat 2026-11-10).", 'G17')
GB('tioarig', "en senare ändring av denna ändringslag; ej verifierad mot SFS-kungörelsen.",
   "en senare ändring av denna ändringslag; belagd 2026-11-10 (prop. 2025/26:10, bet. 2025/26:UbU4, rskr. 2025/26:49; lagen.nu). Övergångspunkt 3 får ny lydelse 2027-01-01 genom SFS 2026:716.", 'G18')
GB('timplan', "SFS-nummer för lagändringen ej verifierat i tillgängliga källor (finns inte på Skolverkets Aktuella regeländringar) — null tills belagt.",
   "SFS-nummer för lagändringen: 2023:943 (bet. 2023/24:UbU5, prop. 2023/24:20, rskr. 2023/24:106; lagen.nu:s förarbetesregister och SFS-texten, verifierat 2026-11-10).", 'G9')
# senast_andrad för ändrade poster
for rid in ('betyg', 'laroplaner', 'tid', 'stod', 'studiero', 'brott', 'offentlighet', 'register', 'yrkes', 'profession', 'timplan', 'tioarig'):
    GB(rid, '"senast_andrad": "2026-06-12"', '"senast_andrad": "2026-11-10"', 'sen')

# ======================= skriv =======================
json.loads(G); json.loads(U)   # validera före skrivning
open(P('data/reforms.json'), 'w', encoding='utf-8').write(json.dumps(reforms, ensure_ascii=False, indent=2))
open(P('data/uppdrag.json'), 'w', encoding='utf-8').write(json.dumps(up, ensure_ascii=False, indent=2))
open(P('data/tidslinje.json'), 'w', encoding='utf-8').write(json.dumps(tl, ensure_ascii=False, indent=2) + '\n')
open(P('data/andringar.json'), 'w', encoding='utf-8').write(json.dumps(an, ensure_ascii=False, indent=2) + '\n')
open(P('data/utredningar.json'), 'w', encoding='utf-8').write(U)
open(P('data/guide.json'), 'w', encoding='utf-8').write(G)
print('\n'.join(log)); print(f'{len(log)} operationer OK')
