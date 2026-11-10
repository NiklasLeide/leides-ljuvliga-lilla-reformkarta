#!/usr/bin/env python3
"""Validerar pilot/utmaningar/data/utmaningar-<id>.json (Sprint 16 T3; parametrisk sedan Sprint 17 T2).
Användning (från repo-roten): python3 research/remissanalys/skript/validera-pilot.py [<reform-id>]   (standard: betyg)

Kontroller:
 1. giltig JSON
 2. antal utmaningar och avsändare = antal i mellanfilen research/remissanalys/reformer/<id>/utmaningar.json (dubbletter
    borträknade), både i avsandare[] och som unika avsändare bland utmaningarna; varje citat har citatkontroll.ok = true
    och OCR-citat har ocr = true och "(OCR)" i källtexten
 3. varje utmaning har icke-tomt citat, sida och url
 4. varje icke-null värde har källa: varje källobjekt ({text,url}) har icke-tom text och url, och dessa poster
    måste ha källa: utmaning, sakområde, namnträff i propositionen, sökt propositionsavsnitt, propositionsavsnitt,
    utredningsförslag, SFS-status som inte är null, lagparagrafens SOU-/propositions-/beslutade lydelse,
    avsändarens remissvar, kedjans led, opublicerat remissvar
 5. inga nycklar eller strängvärden innehåller orden "löst", "kvarstår" eller "bemött tillräckligt"
 6. varje propositionsavsnitts rubrik återfinns, fullständig, i respektive propositions innehållsförteckning
    (research/remissanalys/reformer/<id>/propositioner-innehall.json, extraherad oberoende av avsnittstexten)
Avslutar med kod 0 om allt går igenom, annars 1 och en lista över fel."""
import json, os, re, sys

ROT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
RID = sys.argv[1] if len(sys.argv) > 1 else 'betyg'
FIL = os.path.join(ROT, f'pilot/utmaningar/data/utmaningar-{RID}.json')
MELLAN = os.path.join(ROT, f'research/remissanalys/reformer/{RID}')
_uu = [u for u in json.load(open(os.path.join(MELLAN, 'utmaningar.json'), encoding='utf-8'))['utmaningar'] if not u['dublett_av']]
N_UTM = len(_uu); N_AVS = len({u['avsandare'] for u in _uu})
fel = []
def F(m): fel.append(m)

try:
    d = json.load(open(FIL, encoding='utf-8'))
except Exception as e:
    print('FEL: ogiltig JSON:', e); sys.exit(1)

def kalla_ok(k, var):
    if not isinstance(k, dict) or not str(k.get('text') or '').strip() or not str(k.get('url') or '').strip():
        F(f'källa saknas eller är ofullständig: {var}')

U = d.get('utmaningar', []); A = d.get('avsandare', [])
if len(U) != N_UTM: F(f'antal utmaningar {len(U)} ≠ {N_UTM} (mellanfilen)')
if len(A) != N_AVS: F(f'antal avsändare i avsandare[] {len(A)} ≠ {N_AVS}')
if len({u.get("avsandare") for u in U}) != N_AVS: F(f'antal unika avsändare bland utmaningarna ≠ {N_AVS}')
for u in U:
    if (u.get('citatkontroll') or {}).get('ok') is not True: F(f"{u.get('id')}: citatet är inte kontrollerat ordagrant mot källtexten")
    if u.get('ocr') and '(OCR)' not in (u.get('kalla') or {}).get('text', ''): F(f"{u.get('id')}: OCR-citat saknar märkning i källan")
if len({u.get('id') for u in U}) != len(U): F('dubblerade utmaningsid')

for u in U:
    i = u.get('id')
    for f in ('citat', 'sida', 'url'):
        if u.get(f) in (None, '') : F(f'{i}: saknar {f}')
    kalla_ok(u.get('kalla'), f'{i}.kalla')
    if not u.get('utmaningstyp', {}).get('primar'): F(f'{i}: saknar primär utmaningstyp')
    if u.get('utmaningstyp', {}).get('tolkning') is not True: F(f'{i}: utmaningstyp saknar tolkning: true')
    k = u.get('koppling', {})
    if k.get('niva') not in ('förslag', 'avsnitt', 'kapitel', 'tolkad', None): F(f'{i}: okänd kopplingsnivå {k.get("niva")}')
    if k.get('niva') == 'kapitel' and k.get('forslag'): F(f'{i}: kapitelnivå med enskilda förslag')
    if k.get('niva') == 'förslag' and len(k.get('forslag', [])) != 1: F(f'{i}: nivå förslag kräver exakt ett förslag')
    if k.get('niva') == 'avsnitt' and len(k.get('forslag', [])) < 2: F(f'{i}: nivå avsnitt kräver flera förslag')
    if k.get('niva') == 'tolkad' and k.get('tolkning') is not True: F(f'{i}: tolkad koppling saknar tolkning: true')
    for j, s in enumerate(u.get('sakomrade') or []): kalla_ok(s.get('kalla'), f'{i}.sakomrade[{j}]')
    n = u.get('namngivning_i_propositionen')
    if n is not None:
        if n.get('namngiven') is not bool(n.get('traffar')): F(f'{i}: namngiven stämmer inte med träffar')
        for j, h in enumerate(n.get('traffar', [])):
            kalla_ok(h.get('kalla'), f'{i}.namngivning.traffar[{j}]')
            if not h.get('citat') or not h.get('sida'): F(f'{i}: namnträff saknar citat eller sida')
        for j, s in enumerate(n.get('sokt_i', [])): kalla_ok(s, f'{i}.namngivning.sokt_i[{j}]')
for a in A: kalla_ok(a.get('remissvar'), f'avsandare {a.get("namn")}.remissvar')
for p in d.get('propositionsavsnitt', []):
    kalla_ok(p.get('kalla'), f'propositionsavsnitt {p.get("ref")}')
    if p.get('kopplade_utredningsforslag', {}).get('redaktionell') is not True: F(f'propositionsavsnitt {p.get("ref")}: koppling ej märkt redaktionell')
for f in d.get('utredningsforslag', []):
    kalla_ok(f.get('kalla'), f'utredningsförslag {f.get("id")}')
    if f.get('propositionsavsnitt', {}).get('redaktionell') is not True: F(f'utredningsförslag {f.get("id")}: koppling ej märkt redaktionell')
    s = f.get('sfs') or {}
    if s.get('status') is not None: kalla_ok(s.get('kalla'), f'utredningsförslag {f.get("id")}.sfs')
    elif not s.get('forklaring'): F(f'utredningsförslag {f.get("id")}: SFS-status null utan förklaring')
    if s.get('status') in ('ändrad', 'oförändrad'): F(f'utredningsförslag {f.get("id")}: otillåten SFS-etikett')
for key, p in d.get('lagparagrafer', {}).items():
    kalla_ok(p.get('sou', {}).get('kalla'), f'lagparagraf {key}.sou')
    if p.get('proposition'): kalla_ok(p['proposition'].get('kalla'), f'lagparagraf {key}.proposition')
    if p.get('beslutad'): kalla_ok(p['beslutad'].get('kalla'), f'lagparagraf {key}.beslutad')
for s in d.get('sakomraden', []): kalla_ok(s.get('kalla'), f'sakområde {s.get("kapitel")}')
ked = d.get('meta', {}).get('kedja', {})
for led, v in ked.items():
    for j, x in enumerate(v if isinstance(v, list) else [v]): kalla_ok(x.get('kalla'), f'kedja.{led}[{j}]')
for s in d.get('meta', {}).get('korpus', {}).get('opublicerade_remissvar_som_saknas', {}).get('avsandare', []):
    kalla_ok(s.get('kalla'), f'opublicerat remissvar {s.get("avsandare")}')

# 6. rubriker mot propositionernas innehållsförteckning
INNEH = json.load(open(os.path.join(MELLAN, 'propositioner-innehall.json'), encoding='utf-8'))['propositioner']
norm = lambda s: re.sub(r'\s+', ' ', s or '').strip()
for p in d.get('propositionsavsnitt', []):
    pr = p.get('proposition', '').split(':')[-1]
    toc = INNEH.get(pr, {}).get('innehallsforteckning', {})
    t = toc.get(p.get('avsnitt'), {}).get('titel')
    if t is None: F(f'propositionsavsnitt {p.get("ref")}: avsnittet saknas i innehållsförteckningen')
    elif norm(t) != norm(p.get('rubrik')): F(f'propositionsavsnitt {p.get("ref")}: rubriken "{p.get("rubrik")}" ≠ innehållsförteckningens "{t}"')

# generellt: varje källobjekt någonstans i filen ska ha text och url
def walk(o, path):
    if isinstance(o, dict):
        if set(o.keys()) >= {'text', 'url'} and path.split('/')[-1] in ('kalla', 'remissvar', 'status_kalla') :
            kalla_ok(o, path)
        for k, v in o.items():
            if RX.search(k): F(f'förbjudet ord i nyckel {path}/{k}')
            walk(v, f'{path}/{k}')
    elif isinstance(o, list):
        for i, v in enumerate(o): walk(v, f'{path}[{i}]')
    elif isinstance(o, str) and RX.search(o):
        F(f'förbjudet ord i värde {path}: "{RX.search(o).group(0)}"')
RX = re.compile(r'\b(löst|kvarstår)\b|bemött tillräckligt', re.I)
walk(d, '')

if fel:
    print(f'VALIDERING MISSLYCKADES: {len(fel)} fel'); [print(' -', x) for x in fel[:100]]; sys.exit(1)
print(f'VALIDERING OK: {len(U)} utmaningar, {len(A)} avsändare, {len(d.get("propositionsavsnitt", []))} propositionsavsnitt, '
      f'{len(d.get("utredningsforslag", []))} utredningsförslag, {len(d.get("lagparagrafer", {}))} lagparagrafer')
