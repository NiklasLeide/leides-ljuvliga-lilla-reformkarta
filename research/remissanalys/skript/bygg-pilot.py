#!/usr/bin/env python3
"""Bygger pilot/utmaningar/data/utmaningar-betyg.json (Utmaningskartan, pilot betyg; Sprint 16 T3).

Läser ENDAST incheckade filer (sökvägar relativt repo-roten):
  research/remissanalys/v2/utmaningar-betyg-v2.json       utmaningar, typ (v2), koppling, skolform
  research/remissanalys/v2/andringslogg-utmaningstyp.json  steg 1: regelprövning Otydlighet/Likvärdighet
  research/remissanalys/v2/avvikelser-betyg.json          propositionens stycken om utredningens förslag
  research/remissanalys/pilot-betyg.json                  80 utredningsförslag + koppling till propositionsavsnitt
  research/remissanalys/sfs-diff-betyg.json               SOU → proposition → beslutad lydelse per paragraf
  research/remissanalys/kedjor.json                       kedjan SOU → rskr med källor
  research/remissanalys/utmaningar-betyg.json             (v1) saknade, opublicerade remissvar
  research/remissanalys/arbetsfiler/propositionsavsnitt-text.json  propositionsavsnittens text per sida
  research/remissanalys/arbetsfiler/sou-innehall.json     SOU 2025:18:s innehållsförteckning (kapitel, avsnitt)

Körs från repo-roten:  python3 research/remissanalys/skript/bygg-pilot.py
Utdata är deterministisk (inga tidsstämplar från körningen)."""
import json, re, os, collections

ROT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
def L(p): return json.load(open(os.path.join(ROT, p), encoding='utf-8'))
UT = 'pilot/utmaningar/data/utmaningar-betyg.json'
HAMTAT = '2026-11-10'

v2 = L('research/remissanalys/v2/utmaningar-betyg-v2.json')
logg = L('research/remissanalys/v2/andringslogg-utmaningstyp.json')
avv = L('research/remissanalys/v2/avvikelser-betyg.json')
pilot = L('research/remissanalys/pilot-betyg.json')
sfsd = L('research/remissanalys/sfs-diff-betyg.json')
kedjor = L('research/remissanalys/kedjor.json')
v1 = L('research/remissanalys/utmaningar-betyg.json')
ptext = L('research/remissanalys/arbetsfiler/propositionsavsnitt-text.json')['avsnitt']
souinn = L('research/remissanalys/arbetsfiler/sou-innehall.json')

SOU_URL = 'https://www.regeringen.se/contentassets/56408e57ea8e4954bf38491c8bc33d4c/ett-likvardigt-betygssystem-sou-202518-volym-1.pdf'
TYPER = [
    ('Kostnader och finansiering', 'utgifter, ersättning, finansieringsprincipen, resursbehov i pengar'),
    ('Tidplan och reformtakt', 'ikraftträdande, förberedelsetid, samtidiga reformer'),
    ('Personal, kompetens och arbetsbelastning', 'bemanning, kompetensutveckling, lärares och rektorers arbetsbörda'),
    ('System och teknik', 'digitala system, provplattform, infrastruktur, utrustning'),
    ('Organisation och planering', 'schemaläggning, lokaler, genomförande i verksamheten, samordning mellan enheter'),
    ('Otydlighet i förslaget', 'oklara begrepp, oklart ansvar, oklar tillämpning'),
    ('Likvärdighet och konsekvenser för elever', 'effekter för elevgrupper, rättssäkerhet, likvärdig bedömning'),
    ('Övrigt', 'inget av ovanstående'),
]
AVGORANDE_REGEL = ('Citat vars huvudpoäng är att modellen, regleringen eller begreppen är svåra att förstå eller förklara kodas som '
                   'Otydlighet i förslaget, även när elever eller vårdnadshavare nämns som de som ska förstå. Likvärdighet och konsekvenser '
                   'för elever kräver att citatet beskriver en effekt för elever eller skilda utfall mellan elevgrupper, skolor eller huvudmän.')
FOKUS = ['kommuner', 'enskilda_huvudman', 'skr', 'almega', 'ideburna']
FOKUSNAMN = {'kommuner': 'Kommuner', 'enskilda_huvudman': 'Enskilda huvudmän', 'skr': 'Sveriges Kommuner och Regioner (SKR)',
             'almega': 'Almega', 'ideburna': 'Idéburna skolors riksförbund'}

# ---------- utredningsförslag och propositionsavsnitt ----------
F = {f['id']: f for f in pilot['forslag']}
F_AVS = {fid: [r['ref'] for r in (f['proposition'] or {}).get('avsnitt', [])] for fid, f in F.items()}
def sou_sida(f):
    m = re.search(r's\. (\d+)', f['kalla']['text']); return int(m.group(1)) if m else None

# ---------- steg 1: typ efter regelprövning ----------
LOGG = {x['id']: x for x in logg['andringar']}
PROVADE = set(logg['provade_id'])
MOTIVERING_OMFORMULERAD = {'U338': ('lokal hantering kvarstår', 'lokal hantering finns kvar')}

# ---------- steg 3: namnsökning i propositionsavsnittets text ----------
ALIAS = {'SKR': 'Sveriges Kommuner och Regioner'}
def delar_for_sokning(ref):
    """Delar av avsnittet som gäller SOU 2025:18. I prop. 194 hoppas Läroplansutredningens förslag och
    remissinstanserna till det förslaget över (de gäller SOU 2025:19)."""
    a = ptext[ref]; out = []; hoppa = False
    for d in a['delar']:
        if ref.startswith('194:'):
            if d['del'].startswith('Läroplansutredningens'): hoppa = True; continue
            if d['del'].startswith('Utredningen om likvärdiga') or d['del'].startswith('Regeringens') or d['del'].startswith('Skälen'): hoppa = False
            if hoppa: continue
        out.append(d)
    return out
FORK = ('bl.a.', 'm.fl.', 't.ex.', 'dvs.', 's.k.', 'prop.', 'bet.', 'rskr.', 'jfr.', 'kap.', 'resp.', 'ca.', 'm.m.', 'o.d.', 'p.g.a.', 'fr.o.m.', 't.o.m.')
def mening_kring(t, p):
    """Hela meningen runt position p. Meningsslut = punkt + blanksteg + versal, utom efter vanliga förkortningar."""
    slut = [m.end() for m in re.finditer(r'\.(?=\s+[A-ZÅÄÖ0-9])', t) if not any(t[:m.end()].endswith(' ' + f) or t[:m.end()].endswith(f) and len(f) == m.end() for f in FORK)]
    a0 = max([e for e in slut if e <= p], default=0)
    b0 = min([e for e in slut if e > p], default=len(t))
    return t[a0:b0].strip()
def namnformer(avsandare):
    former = [avsandare] + [k for k, v in ALIAS.items() if v == avsandare]
    return former
def sok(avsandare, ref):
    """Ordagranna meningar i avsnittet där avsändaren nämns (fullt namn, kortform eller samordnad kommunuppräkning)."""
    traffar = []
    m_kom = re.match(r'^(.+?) kommun$', avsandare)
    for d in delar_for_sokning(ref):
        # delens text löper över sidgränser; spara startposition per sida så att meningar inte klipps vid sidbrytning
        t = ''; starts = []
        for s in d['sidor']:
            if re.search(r'\w-$', t) and re.match(r'[a-zåäö]', s['text']) and not re.match(r'(och|eller|samt)\b', s['text']):
                t = t[:-1]                      # avstavning över sidbrytning ("Olof-" + "ströms")
            elif t:
                t += ' '
            starts.append((len(t), s['sida'])); t += s['text']
        def sida_for(pos): return max((st for st in starts if st[0] <= pos), key=lambda x: x[0])[1]
        if True:
            pos = []
            for form in namnformer(avsandare):
                fl = re.I if form != 'SKR' else 0   # versalisering varierar i propositionen ("Almega utbildning")
                for m in re.finditer(r'(?<![\wåäö])' + re.escape(form) + r'(?![\wåäö])', t, fl): pos.append((m.start(), m.group(0)))
            if m_kom:  # "Falu, Motala och Söderhamns kommuner"
                bas = m_kom.group(1)
                for m in re.finditer(r'((?:[A-ZÅÄÖ][\wåäöé-]+(?:, | och | samt ))+[A-ZÅÄÖ][\wåäöé-]+) kommuner', t):
                    if bas in re.split(r', | och | samt ', m.group(1)): pos.append((m.start(), m.group(0)))
            for p, form in sorted(set(pos)):
                mening = mening_kring(t, p)
                s = {'sida': sida_for(p)}
                hit = {'namn_i_texten': form, 'citat': mening, 'sida': s['sida'], 'del': d['del'], 'propositionsavsnitt': ref,
                       'kalla': {'text': f"{ptext[ref]['proposition']} s. {s['sida']}, avsnitt {ptext[ref]['avsnitt']} ”{d['del']}”", 'url': ptext[ref]['url']}}
                if hit not in traffar: traffar.append(hit)
    return traffar

# ---------- SFS ----------
SFS = {}
for i, sf in enumerate(sfsd['forslag']): SFS[sf['forslag']] = (i, sf)
lagparagrafer = {}
def sfs_for(fid):
    if fid not in SFS:
        return {'status': None, 'forklaring': 'Inte undersökt: förslaget hade ingen kopplad utmaning i förstudie 2 (sfs-diff-betyg.json).'}
    i, sf = SFS[fid]
    if sf['status'] == 'ej lagtext' or sf['status'].startswith('ej i SFS'):
        return {'status': sf['status'], 'kalla': sf['status_kalla']}
    pars = []
    for j, p in enumerate(sf['paragrafer']):
        b = p.get('beslutad')
        key = p['paragraf']
        if key not in lagparagrafer:
            lagparagrafer[key] = {'paragraf': key, 'sou': p['sou'], 'proposition': p.get('proposition'),
                                  'beslutad': b, 'textlikhet_procent': round(100 * b['likhet_mot_sou'], 1) if b else None,
                                  'diff_sou_mot_beslutad': p.get('diff_sou_mot_beslutad', []), 'manuell_granskning': p['manuell_granskning'],
                                  'belagg': f'research/remissanalys/sfs-diff-betyg.json#/forslag/{i}/paragrafer/{j}'}
        pars.append({'paragraf': key, 'textlikhet_procent': lagparagrafer[key]['textlikhet_procent']})
    if all(lagparagrafer[p['paragraf']]['beslutad'] for p in pars):
        return {'status': 'i beslutad lag', 'paragrafer': pars,
                'kalla': {'text': f'Skollag (2010:800) konsoliderad, riksdagens öppna data, hämtad {HAMTAT} (lydelser enligt SFS 2026:1242, 2026:1243, 2026:1245)', 'url': 'https://data.riksdagen.se/dokument/sfs-2010-800.text'}}
    return {'status': None, 'paragrafer': pars, 'forklaring': 'Minst en paragraf saknar beslutad lydelse; se diff.'}

# ---------- utmaningar ----------
KAP = souinn['kapitel']; AVS = souinn['avsnitt']
def kapitelrubrik(k): return {'kapitel': k, 'rubrik': KAP[k], 'kalla': {'text': f'SOU 2025:18, innehållsförteckning, kapitel {k}', 'url': SOU_URL}}
utmaningar = []
for u in v2['utmaningar']:
    t = dict(u['utmaningstyp'])
    if u['id'] in LOGG:
        assert LOGG[u['id']]['gammal'] == t['primar']
        t['primar'] = LOGG[u['id']]['ny']; t['motivering'] = LOGG[u['id']]['motivering']
        if t.get('sekundar') == t['primar']: t['sekundar'] = None
    # Kodarnas motiveringar (inte citat) får inte använda ord som kan läsas som bedömning av om en utmaning är löst/kvarstår.
    # Uttrycklig, loggad omformulering (Sprint 16 T3): U338 "lokal hantering kvarstår" -> "lokal hantering finns kvar".
    if 'kvarstår' in t['motivering']:
        assert u['id'] in MOTIVERING_OMFORMULERAD, u['id']
        t['motivering'] = t['motivering'].replace(*MOTIVERING_OMFORMULERAD[u['id']])
    typ = {'primar': t['primar'], 'sekundar': t.get('sekundar'), 'motivering': t['motivering'], 'tolkning': True,
           'regelprovad': u['id'] in PROVADE, 'andrad_vid_regelprovning': u['id'] in LOGG}
    k = u['koppling']; niva = k['niva']; fids = k['forslag']
    if niva == 'förslag' and len(fids) > 1: niva = 'avsnitt'
    if fids:
        sou_avs = sorted({F[f]['sou_avsnitt'] for f in fids}, key=lambda a: [int(x) for x in a.split('.')])
    elif niva == 'kapitel':
        sou_avs = sorted({a for g in k.get('grund', []) for a in re.findall(r'\b(\d{1,2}(?:\.\d{1,2}){1,3})\b', g) if a in AVS},
                         key=lambda a: [int(x) for x in a.split('.')]) or None
    else:
        sou_avs = None
    koppling = {'niva': niva, 'forslag': fids, 'sou_avsnitt': sou_avs, 'kapitel': k.get('kapitel', []), 'tolkning': niva == 'tolkad'}
    if niva in ('förslag', 'avsnitt', 'kapitel'):
        koppling['grund'] = k.get('grund'); koppling['kalla_for_grund'] = k.get('kalla_for_grund')
    if niva == 'tolkad': koppling['motivering'] = k.get('motivering')
    # namngivning i propositionen
    refs = sorted({r for f in fids for r in F_AVS.get(f, [])}) if niva in ('förslag', 'avsnitt', 'tolkad') else []
    if refs:
        tr = [h for r in refs for h in sok(u['avsandare'], r)]
        namn = {'namngiven': bool(tr), 'propositionsavsnitt': refs, 'traffar': tr,
                'sokt_i': [{'text': f"{ptext[r]['proposition']} avsnitt {ptext[r]['avsnitt']} (hela avsnittets text"
                            + (", utom delar om SOU 2025:19" if r.startswith('194:') else '') + ')', 'url': ptext[r]['url']} for r in refs],
                'anm': 'Anger bara om avsändarens namn förekommer i avsnittets text; ingen bedömning av innehållet.'}
    else:
        namn = None
    utmaningar.append({
        'id': u['id'], 'avsandare': u['avsandare'], 'fokusgrupp': u['fokusgrupp'], 'grupp': u['grupp'],
        'citat': u['citat'], 'sida': u['sida'], 'url': u['url'], 'ocr': u['ocr'], 'kalla': u['kalla'], 'citatkontroll': u['citatkontroll'],
        'utmaningstyp': typ, 'koppling': koppling,
        'sakomrade': [kapitelrubrik(c) for c in koppling['kapitel']] or None,
        'skolform': u['skolform'], 'namngivning_i_propositionen': namn})

# ---------- utredningsförslag ----------
redaktionell_grund = {'förslagsruta': 'Utredningsförslaget motsvaras av propositionens förslags-/bedömningsruta (ämnesmatchning, förstudie 1).',
                      'avsnittsnivå': 'Matchning på avsnittsnivå enligt propositionens egen avgränsning av vilka SOU-avsnitt den behandlar.',
                      'osäker ämnesmatchning': 'Osäker ämnesmatchning.',
                      'övergripande avsnitt, detalj ej behandlad': 'Propositionen tar ställning övergripande i avsnittet; detaljförslaget nämns inte i rutan.',
                      'ingen': 'Förslaget motsvaras inte av något propositionsavsnitt.'}
forslag = []
for fid, f in F.items():
    forslag.append({'id': fid, 'text': f['forslag_ordagrant'], 'sou_avsnitt': f['sou_avsnitt'], 'sou_avsnittsrubrik': f['sou_avsnittsrubrik'],
                    'sou_sida': sou_sida(f), 'kalla': f['kalla'],
                    'propositionsavsnitt': {'refs': F_AVS[fid], 'matchning': f['matchning']['typ'],
                                            'grund': redaktionell_grund.get(f['matchning']['typ']), 'redaktionell': True},
                    'sfs': sfs_for(fid)})

# ---------- propositionsavsnitt ----------
REF_AV = {}
for fid, refs in F_AVS.items():
    for r in refs: REF_AV.setdefault(r, []).append(fid)
propositionsavsnitt = []
for a in avv['avsnitt']:
    ref = f"{a['proposition'].split(':')[-1]}:{a['avsnitt']}"
    propositionsavsnitt.append({'ref': ref, 'proposition': a['proposition'], 'avsnitt': a['avsnitt'],
                                'rubrik': ptext[ref]['rubrik'] if ref in ptext else a['rubrik'],
                                'overensstammelse': a['overensstammelse'], 'avvikelse_beskriven': a['avvikelse_beskriven'],
                                'avvikelsetext': a['text'], 'sida': a['sida'], 'url': a['kalla']['url'], 'kalla': a['kalla'],
                                'kopplade_utredningsforslag': {'forslag': sorted(REF_AV.get(ref, []), key=lambda x: int(x[1:])), 'redaktionell': True}})

# ---------- avsändare ----------
avs = {}
for u in utmaningar:
    a = avs.setdefault(u['avsandare'], {'namn': u['avsandare'], 'fokusgrupp': u['fokusgrupp'], 'grupp': u['grupp'],
                                        'remissvar': {'text': f"Remissvar från {u['avsandare']} på SOU 2025:18 (U2025/00401)", 'url': u['url']}, 'antal_utmaningar': 0})
    a['antal_utmaningar'] += 1
avsandare = sorted(avs.values(), key=lambda a: a['namn'])

# ---------- avsändarräkning ----------
def rakna(sel):
    return {'antal_avsandare': len({u['avsandare'] for u in sel}), 'antal_utmaningar': len(sel),
            'per_fokusgrupp': {g: {'antal_avsandare': len({u['avsandare'] for u in sel if u['fokusgrupp'] == g}),
                                   'avsandare': sorted({u['avsandare'] for u in sel if u['fokusgrupp'] == g})} for g in FOKUS}}
SAKNAMN = [KAP[k] for k in sorted(KAP, key=int) if 9 <= int(k) <= 20]
def har_sak(u, s): return any(x['rubrik'] == s for x in (u['sakomrade'] or []))
raknning = {
    'princip': 'Unika avsändare per cell, efter primär utmaningstyp. En utmaning kopplad till flera kapitel räknas i varje kapitel.',
    'totalt': rakna(utmaningar),
    'per_utmaningstyp': {n: rakna([u for u in utmaningar if u['utmaningstyp']['primar'] == n]) for n, _ in TYPER},
    'per_sakomrade': {s: rakna([u for u in utmaningar if har_sak(u, s)]) for s in SAKNAMN},
    'utan_sakomrade': rakna([u for u in utmaningar if not u['sakomrade']]),
    'per_kombination': [dict(utmaningstyp=n, sakomrade=s, **rakna(sel)) for n, _ in TYPER for s in SAKNAMN
                        if (sel := [u for u in utmaningar if u['utmaningstyp']['primar'] == n and har_sak(u, s)])],
}

# ---------- meta ----------
bet = [r for r in kedjor['reformer'] if r['id'] == 'betyg'][0]
saknade = [{'avsandare': s['avsandare'], 'fokusgrupp': s['fokusgrupp'], 'grupp': s['grupp'], 'skal': s['skal'], 'kalla': s['kalla']} for s in v1['saknade_remissvar']]
meta = {
    'reform': {'id': 'betyg', 'namn': 'Ett likvärdigt betygssystem'},
    'kedja': {'utredningsbetankande': bet['utredningsbetankande'], 'remiss': {k: bet['remiss'][k] for k in ('url', 'diarienummer', 'publicerad', 'svar_senast', 'kalla')},
              'proposition': [bet['proposition'], {'nr': 'Prop. 2025/26:194', 'anm': 'Behandlar SOU 2025:18 avsnitt 9.3 och 9.4 (avsnitt 6.7–6.8 i propositionen).',
                                                    'kalla': {'text': 'Prop. 2025/26:194 (regeringen.se)', 'url': 'https://www.regeringen.se/rattsliga-dokument/proposition/2026/03/prop.-202526194'}}],
              'utskottsbetankande': bet['utskottsbetankande'], 'rskr': bet['rskr']},
    'hamtningsdatum': HAMTAT,
    'korpus': {'publicerade_remissvar': 29, 'avsandare_med_utmaningar': len(avsandare), 'utmaningar': len(utmaningar),
               'beskrivning': 'Publicerade remissvar på regeringen.se från fokusgrupperna (kommuner, SKR, Almega Utbildning, Idéburna skolors riksförbund). '
                              '29 remissvar är publicerade; 28 av avsändarna har minst en kodad utmaning (Kils kommun har ingen).',
               'opublicerade_remissvar_som_saknas': {'antal': len(saknade), 'per_grupp': dict(collections.Counter(s['fokusgrupp'] for s in saknade)), 'avsandare': saknade}},
    'tolkning': 'Fält med tolkning: true är tolkning (utmaningstyp; koppling med nivå "tolkad"). Kopplingen mellan utredningsförslag och propositionsavsnitt är redaktionell: true. Övrigt är mekaniskt härlett ur källtext.',
    'ingen_bedomning': 'Inget fält anger om en utmaning har lösts eller om propositionen har bemött den i sak.',
    'kopplingsnivaer': {'förslag': 'remissvarets hänvisning pekar ut exakt ett utredningsförslag',
                        'avsnitt': 'remissvarets hänvisning pekar ut ett SOU-avsnitt med flera förslag',
                        'kapitel': 'remissvaret anger bara kapitel (eller avsnitt utan förslagsruta); ingen koppling till enskilda förslag',
                        'tolkad': 'ingen egen hänvisning; koppling genom tolkning (tolkning: true)', 'null': 'ingen koppling'},
    'byggd_av': 'research/remissanalys/skript/bygg-pilot.py',
}
data = {'meta': meta,
        'utmaningstyper': [{'namn': n, 'definition': d} for n, d in TYPER],
        'avgorande_regel': AVGORANDE_REGEL,
        'sakomraden': [{'kapitel': k, 'rubrik': KAP[k], 'kalla': {'text': f'SOU 2025:18, innehållsförteckning, kapitel {k}', 'url': SOU_URL}} for k in sorted(KAP, key=int) if 9 <= int(k) <= 20],
        'fokusgrupper': [{'id': g, 'namn': FOKUSNAMN[g], 'grupp': 'huvudman' if g in ('kommuner', 'enskilda_huvudman') else 'huvudmannaorganisation'} for g in FOKUS],
        'avsandare': avsandare,
        'utmaningar': utmaningar,
        'propositionsavsnitt': propositionsavsnitt,
        'utredningsforslag': forslag,
        'lagparagrafer': lagparagrafer,
        'avsandarrakning': raknning}
os.makedirs(os.path.join(ROT, os.path.dirname(UT)), exist_ok=True)
with open(os.path.join(ROT, UT), 'w', encoding='utf-8') as fh:
    json.dump(data, fh, ensure_ascii=False, indent=1); fh.write('\n')
c = collections.Counter
print('skrev', UT, '| utmaningar', len(utmaningar), '| avsändare', len(avsandare))
print('nivå', dict(c(u['koppling']['niva'] for u in utmaningar)))
print('namngiven', dict(c(None if u['namngivning_i_propositionen'] is None else u['namngivning_i_propositionen']['namngiven'] for u in utmaningar)))
print('primär', dict(c(u['utmaningstyp']['primar'] for u in utmaningar)))
