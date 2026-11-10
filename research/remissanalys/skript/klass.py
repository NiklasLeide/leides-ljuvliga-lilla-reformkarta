import re,unicodedata
N=lambda s: unicodedata.normalize('NFC',s).strip()
# Enskilda huvudmän: namn som enligt extern kunskap är huvudmän för fristående skolor.
# Grund: INTE källtexten — måste verifieras mot Skolverkets register (Skolenhetsregistret) före v1.
ENSKILDA={'Academedia AB','Frida Utbildning AB','Fridaskolorna AB','Internationella Engelska Skolan','Internationella Engelska Skolan AB',
 'Internationella Engelska Skolan i Sverige AB','Internationella Engelska skolan i Sverige AB','Kunskapsskolan i Sverige AB',
 'Lärandegruppen i Sverige AB','Stiftelsen Viktor Rydberg skolor','OneSchool Global'}
OSAKER={'OneSchool Global':'Antas vara huvudman för fristående skolor (extern kunskap, ej verifierad).',
 'Folkuniversitetet':'Studieförbund; kan vara huvudman för fristående skolor — klassad som övrig organisation, verifiera.',
 'Göteborgsregionen':'Kommunalförbund — varken kommun eller region i kategorilistan; klassad som övrig organisation.',
 'Lapplands Kommunalförbund':'Kommunalförbund — klassad som övrig organisation.',
 'Expertrådet för läsning':'Oklar organisationsform — klassad som övrig organisation, verifiera.',
 'Nationellt centrum för kvinnofrid':'Del av Uppsala universitet enligt extern kunskap — klassad som myndighet, verifiera.',
 'Waldorflärarhögskolan':'Enskild högskola — klassad som övrig organisation.',
 'Waldorflärarhögskolan (WLH)':'Enskild högskola — klassad som övrig organisation.',
 'Friskolornas riksförbund':'Ej någon av de tre fokusorganisationerna enligt namnet; inga samband antas (briefens regel).',
 'Almega utbildningsföretagen':'Annat namn än remisslistans "Almega Utbildning" — räknas till Almega enligt briefen (namnet innehåller Almega), flaggas.'}
MYND_EXAKT={'Arbetsmiljöverket','Barnombudsmannen','Brottsförebyggande rådet','Centrala studiestödsnämnden','Diskrimineringsombudsmannen',
 'Folkhälsomyndigheten','Integritetsskyddsmyndigheten','Jämställdhetsmyndigheten','Justitiekanslern','Karolinska institutet','Konstfack',
 'Kriminalvården','Kungliga Musikhögskolan i Stockholm','Kungliga biblioteket','Linnéuniversitetet','Mittuniversitetet','Polismyndigheten',
 'Regelrådet','Riksdagens ombudsmän','Riksdagens ombudsmän (JO)','Sameskolstyrelsen','Sametinget','Skolforskningsinstitutet',
 'Skolväsendets överklagandenämnd','Socialstyrelsen','Specialpedagogiska skolmyndigheten','Statistiska centralbyrån','Statskontoret',
 'Tillväxtverket','Universitets- och högskolerådet','Universitetskanslersämbetet','Gymnastik- och idrottshögskolan',
 'Institutet för arbetsmarknads- och utbildningspolitisk utvärdering','Institutet för arbetsmarknadsoch utbildningspolitisk utvärdering',
 'Institutet för mänskliga rättigheter','Institutet för språk och folkminnen','Nationellt centrum för kvinnofrid'}
def kategori(n):
    n=N(n)
    if n=='Sveriges Kommuner och Regioner': return 'skr'
    if re.match(r'Almega\b',n,re.I): return 'almega'
    if n.lower()=='idéburna skolors riksförbund': return 'ideburna'
    if re.search(r'\bkommun$',n): return 'kommuner'
    if n in ENSKILDA: return 'enskilda_huvudman'
    if re.match(r'Region ',n) or n=='Västra Götalandsregionen': return 'regioner'
    if n in MYND_EXAKT or re.match(r'(Statens |Myndigheten |Förvaltningsrätten|Kammarrätten|Länsstyrelsen)',n) \
       or re.search(r'(universitet|Högskolan [A-ZÅÄÖ]|Högskolan i |universitet\)|vid [A-ZÅÄÖ][a-zåäö]+ universitet)',n) and 'Waldorf' not in n and n!='Folkuniversitetet':
        return 'myndigheter'
    if re.search(r'privatperson',n): return 'ovriga'
    return 'ovriga_organisationer'
GRUPP={'kommuner':'huvudman','enskilda_huvudman':'huvudman','skr':'huvudmannaorganisation','almega':'huvudmannaorganisation','ideburna':'huvudmannaorganisation'}
