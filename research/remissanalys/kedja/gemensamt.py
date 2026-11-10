"""Gemensamma hjälpfunktioner för Utmaningskartans kedja (Sprint 17 T1).

Varje steg körs från repo-roten med reformens id:   python3 research/remissanalys/kedja/<steg>.py <reform-id>
Alla filer läses och skrivs inom repot:
  research/remissanalys/reformer/<id>.json      konfiguration (kedja, källor, betygsspecifika parametrar)
  research/remissanalys/reformer/<id>/          mellanfiler (incheckade)
  research/remissanalys/reformer/<id>/kallor/   nedladdade källor och sidtext (cache, checkas inte in, se .gitignore)
  research/remissanalys/kedja/gemensamt.json    låst metod: utmaningstyper, avgörande regel, fokusgrupper, klassningslistor
"""
import json, os, re, sys, unicodedata

ROT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
KEDJA = os.path.join(ROT, 'research/remissanalys/kedja')
REFORMER = os.path.join(ROT, 'research/remissanalys/reformer')


def reform_id():
    if len(sys.argv) < 2:
        sys.exit(f'Användning: python3 {os.path.relpath(sys.argv[0], ROT)} <reform-id>')
    return sys.argv[1]


def config(rid):
    p = os.path.join(REFORMER, f'{rid}.json')
    if not os.path.exists(p): sys.exit(f'Ingen konfiguration: {os.path.relpath(p, ROT)}')
    c = json.load(open(p, encoding='utf-8'))
    if str(c.get('status', '')).startswith('mall'):
        print(f'OBS: {rid}.json är en mall; saknade värden (null) måste fyllas i innan stegen kan köras.', file=sys.stderr)
    return c


def gemensamt():
    return json.load(open(os.path.join(KEDJA, 'gemensamt.json'), encoding='utf-8'))


def mapp(rid, *delar):
    p = os.path.join(REFORMER, rid, *delar)
    os.makedirs(os.path.dirname(p) if os.path.splitext(p)[1] else p, exist_ok=True)
    return p


def las(rid, namn):
    return json.load(open(os.path.join(REFORMER, rid, namn), encoding='utf-8'))


def skriv(rid, namn, data):
    p = mapp(rid, namn)
    with open(p, 'w', encoding='utf-8') as fh:
        json.dump(data, fh, ensure_ascii=False, indent=1); fh.write('\n')
    return p


def N(s):
    return unicodedata.normalize('NFC', s).strip()


def kravs(c, *nycklar):
    """Stoppa med tydligt fel om ett konfigurationsvärde saknas (mallar har null)."""
    v = c
    for k in nycklar:
        v = v.get(k) if isinstance(v, dict) else None
        if v is None: sys.exit(f'Konfigurationsvärdet {".".join(nycklar)} saknas (null) för {c.get("id")}.')
    return v


def kategori(namn, g):
    """Fokusgrupps-/kategoriklassning av en avsändare (samma regler som förstudie 1, listor i gemensamt.json)."""
    n = N(namn); kl = g['klassning']
    if n == 'Sveriges Kommuner och Regioner': return 'skr'
    if re.match(r'Almega\b', n, re.I): return 'almega'
    if n.lower() == 'idéburna skolors riksförbund': return 'ideburna'
    if re.search(r'\bkommun$', n): return 'kommuner'
    if n in kl['enskilda_huvudman']: return 'enskilda_huvudman'
    if re.match(r'Region ', n) or n == 'Västra Götalandsregionen': return 'regioner'
    if n in kl['myndigheter_exakt'] or re.match(r'(Statens |Myndigheten |Förvaltningsrätten|Kammarrätten|Länsstyrelsen)', n) \
       or re.search(r'(universitet|Högskolan [A-ZÅÄÖ]|Högskolan i |universitet\)|vid [A-ZÅÄÖ][a-zåäö]+ universitet)', n) and 'Waldorf' not in n and n != 'Folkuniversitetet':
        return 'myndigheter'
    if re.search(r'privatperson', n): return 'ovriga'
    return 'ovriga_organisationer'


GRUPP = {'kommuner': 'huvudman', 'enskilda_huvudman': 'huvudman', 'skr': 'huvudmannaorganisation',
         'almega': 'huvudmannaorganisation', 'ideburna': 'huvudmannaorganisation'}


def slug(namn):
    return re.sub(r'[^a-z0-9]+', '-', unicodedata.normalize('NFKD', namn.lower()).encode('ascii', 'ignore').decode()).strip('-')
