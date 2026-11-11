#!/usr/bin/env python3
"""Steg K10 (deterministiskt): bygger pilot/utmaningar/data/utmaningar-<id>.json (Utmaningskartans datafil).

Läser bara incheckade filer: research/remissanalys/reformer/<id>.json (konfiguration), kedja/gemensamt.json (låst metod)
och research/remissanalys/reformer/<id>/:
  utmaningar.json (K7), sfs-diff.json (K8), avvikelser.json (K9), sou-forslag.json och sou-innehall.json (K2),
  propositionsavsnitt-text.json (K3), remissvar.json (K5), forslag-propositionsavsnitt.json (R1), kodning/regelprovning.json (M2)
Steg i byggningen:
  1. utmaningstyp efter regelprövningen (Otydlighet/Likvärdighet); förbjudna ord i motiveringar kräver loggad omformulering i config
  2. kopplingsnivå: 'förslag' med flera förslag blir 'avsnitt'; SOU-avsnitt och sakområde (kapitel) härleds
  3. namngivning i propositionen: ordagranna meningar där avsändarens namn står i de kopplade propositionsavsnitten
  4. utredningsförslag med SFS-status, propositionsavsnitt med avvikelsestycke, avsändare och avsändarräkning
Användning: python3 research/remissanalys/kedja/bygg.py <reform-id>   (utdata deterministisk, inga körningstidsstämplar)"""
import collections, json, os, re, sys
sys.path.insert(0, os.path.dirname(__file__))
from gemensamt import N, ROT, reform_id, config, gemensamt, las, kravs, fokusgrupper

ALIAS = {'SKR': 'Sveriges Kommuner och Regioner'}     # kortformer som propositioner använder om avsändare
FORK = ('bl.a.', 'm.fl.', 't.ex.', 'dvs.', 's.k.', 'prop.', 'bet.', 'rskr.', 'jfr.', 'kap.', 'resp.', 'ca.', 'm.m.', 'o.d.', 'p.g.a.', 'fr.o.m.', 't.o.m.')
REDAKTIONELL_GRUND = {'förslagsruta': 'Utredningsförslaget motsvaras av propositionens förslags-/bedömningsruta (ämnesmatchning, förstudie 1).',
                      'avsnittsnivå': 'Matchning på avsnittsnivå enligt propositionens egen avgränsning av vilka SOU-avsnitt den behandlar.',
                      'osäker ämnesmatchning': 'Osäker ämnesmatchning.',
                      'övergripande avsnitt, detalj ej behandlad': 'Propositionen tar ställning övergripande i avsnittet; detaljförslaget nämns inte i rutan.',
                      'ingen': 'Förslaget motsvaras inte av något propositionsavsnitt.'}
KORPUSNAMN = {'kommuner': 'kommuner', 'enskilda_huvudman': 'enskilda huvudmän'}  # organisationerna namnges med kortform/eget namn
avsort = lambda a: [int(x) for x in a.split('.')]

def mening_kring(t, p):
    """Hela meningen runt position p. Meningsslut = punkt + blanksteg + versal, utom efter vanliga förkortningar."""
    slut = [m.end() for m in re.finditer(r'\.(?=\s+[A-ZÅÄÖ0-9])', t) if not any(t[:m.end()].endswith(' ' + f) or t[:m.end()].endswith(f) and len(f) == m.end() for f in FORK)]
    a0 = max([e for e in slut if e <= p], default=0)
    b0 = min([e for e in slut if e > p], default=len(t))
    return t[a0:b0].strip()

if __name__ == '__main__':
    rid = reform_id(); c = config(rid); g0 = gemensamt()
    HAMTAT = kravs(c, 'hamtningsdatum'); SOUNR = kravs(c, 'sou', 'nr'); DNR = kravs(c, 'remiss', 'diarienummer')
    kmin, kmax = kravs(c, 'sou', 'forslagskapitel'); PROPS = {p['kort']: p for p in kravs(c, 'propositioner')}
    legacy = c.get('legacy_sokvagar') or {}
    SFS_BELAGG = legacy.get('sfs_diff_belagg') or f'research/remissanalys/reformer/{rid}/sfs-diff.json'
    BYGGD_AV = legacy.get('byggd_av') or 'research/remissanalys/kedja/bygg.py'
    UT = f'pilot/utmaningar/data/utmaningar-{rid}.json'
    TYPER = [tuple(t) for t in g0['utmaningstyper']]
    FG = fokusgrupper(c, g0); FOKUS = list(FG)   # gemensamma + config extra_fokusgrupper (oförändrat utan nyckeln)
    # Sprint 17 D: en organisationsgrupp som uttryckligen är null i config fokusorganisationer hör inte till reformens remiss
    # (t.ex. almega för tioarig) och tas bort ur fokusgrupperna och räkningen.
    FOKUS = [g for g in FOKUS if not (g in (c.get('fokusorganisationer') or {}) and c['fokusorganisationer'][g] is None)]
    FORBJUDET = re.compile(r'\b(' + '|'.join(re.escape(o) for o in g0['forbjudna_ord'] if ' ' not in o) + r')\b|' + '|'.join(re.escape(o) for o in g0['forbjudna_ord'] if ' ' in o), re.I)
    OMFORM = {k: tuple(v) for k, v in ((c.get('korrigeringar') or {}).get('motivering_omformulerad') or {}).items()}

    ut0 = [u for u in las(rid, 'utmaningar.json')['utmaningar'] if not u['dublett_av']]
    logg = las(rid, 'kodning/regelprovning.json'); avv = las(rid, 'avvikelser.json'); sfsd = las(rid, 'sfs-diff.json')
    ptext = las(rid, 'propositionsavsnitt-text.json')['avsnitt']; souinn = las(rid, 'sou-innehall.json')
    sf = las(rid, 'sou-forslag.json'); SOU_PDF = sf['_meta']['pdf']; SOU_URL = SOU_PDF['volym-1'] if 'volym-1' in SOU_PDF else next(iter(SOU_PDF.values()))
    BOX = {b['id']: b for b in sf['forslag']}
    FP = {f['id']: f for f in las(rid, 'forslag-propositionsavsnitt.json')['forslag']}
    rv = las(rid, 'remissvar.json')
    F_AVS = {fid: FP[fid]['propositionsavsnitt'] for fid in BOX}

    # ---------- steg 1: typ efter regelprövning ----------
    LOGG = {x['id']: x for x in logg['andringar']}; PROVADE = set(logg['provade_id'])

    # ---------- steg 3: namnsökning ----------
    def delar_for_sokning(ref):
        """Delar av avsnittet som gäller utredningen. I delade propositioner (config hoppa_delar_vid_namnsokning) hoppas andra
        utredningars delar och remissinstanserna till dem över, tills utredningens egen del, regeringens ruta eller skälen börjar."""
        pk = PROPS[ref.split(':')[0]]; hoppa_pre = pk.get('hoppa_delar_vid_namnsokning') or []
        ater = [r for r in pk['utredningens_forslag_rubrik'] + (pk.get('ovriga_delrubriker') or []) if not any(r.startswith(h) for h in hoppa_pre)] + ['Regeringens', 'Skälen']
        out = []; hoppa = False
        for d in ptext[ref]['delar']:
            if hoppa_pre:
                if any(d['del'].startswith(h) for h in hoppa_pre): hoppa = True; continue
                if any(d['del'].startswith(r) for r in ater): hoppa = False
                if hoppa: continue
            out.append(d)
        return out
    def sok(avsandare, ref):
        """Ordagranna meningar i avsnittet där avsändaren nämns (fullt namn, kortform eller samordnad kommunuppräkning)."""
        traffar = []; m_kom = re.match(r'^(.+?) kommun$', avsandare)
        for d in delar_for_sokning(ref):
            # delens text löper över sidgränser; startposition per sida sparas så att meningar inte klipps vid sidbrytning
            t = ''; starts = []
            for s in d['sidor']:
                if re.search(r'\w-$', t) and re.match(r'[a-zåäö]', s['text']) and not re.match(r'(och|eller|samt)\b', s['text']): t = t[:-1]
                elif t: t += ' '
                starts.append((len(t), s['sida'])); t += s['text']
            sida_for = lambda pos: max((st for st in starts if st[0] <= pos), key=lambda x: x[0])[1]
            pos = []
            for form in [avsandare] + [k for k, v in ALIAS.items() if v == avsandare]:
                fl = re.I if form not in ALIAS else 0     # versalisering varierar i propositioner ("Almega utbildning")
                for m in re.finditer(r'(?<![\wåäö])' + re.escape(form) + r'(?![\wåäö])', t, fl): pos.append((m.start(), m.group(0)))
            if m_kom:   # "Falu, Motala och Söderhamns kommuner"
                for m in re.finditer(r'((?:[A-ZÅÄÖ][\wåäöé-]+(?:, | och | samt ))+[A-ZÅÄÖ][\wåäöé-]+) kommuner', t):
                    if m_kom.group(1) in re.split(r', | och | samt ', m.group(1)): pos.append((m.start(), m.group(0)))
            for p, form in sorted(set(pos)):
                sida = sida_for(p)
                hit = {'namn_i_texten': form, 'citat': mening_kring(t, p), 'sida': sida, 'del': d['del'], 'propositionsavsnitt': ref,
                       'kalla': {'text': f"{ptext[ref]['proposition']} s. {sida}, avsnitt {ptext[ref]['avsnitt']} ”{d['del']}”", 'url': ptext[ref]['url']}}
                if hit not in traffar: traffar.append(hit)
        return traffar

    # ---------- SFS ----------
    SFS = {x['forslag']: (i, x) for i, x in enumerate(sfsd['forslag'])}
    andr0 = kravs(c, 'lagar')[0]; lagparagrafer = {}
    def sfs_for(fid):
        if fid not in SFS:
            return {'status': None, 'forklaring': f'Inte undersökt: förslaget hade ingen kopplad utmaning i förstudie 2 ({os.path.basename(SFS_BELAGG)}).'}
        i, x = SFS[fid]
        if x['status'] is None: return {'status': None, 'forklaring': x['status_kalla']['text']}
        if x['status'] == 'ej lagtext' or x['status'].startswith('ej i SFS'): return {'status': x['status'], 'kalla': x['status_kalla']}
        pars = []
        for j, p in enumerate(x['paragrafer']):
            b = p.get('beslutad'); key = p['paragraf']
            if key not in lagparagrafer:
                lagparagrafer[key] = {'paragraf': key, 'sou': p['sou'], 'proposition': p.get('proposition'), 'beslutad': b,
                                      'textlikhet_procent': round(100 * b['likhet_mot_sou'], 1) if b else None,
                                      'diff_sou_mot_beslutad': p.get('diff_sou_mot_beslutad', []), 'manuell_granskning': p['manuell_granskning'],
                                      'belagg': f'{SFS_BELAGG}#/forslag/{i}/paragrafer/{j}'}
            pars.append({'paragraf': key, 'textlikhet_procent': lagparagrafer[key]['textlikhet_procent']})
        if all(lagparagrafer[p['paragraf']]['beslutad'] for p in pars):
            # flera lagar (sfs_diff.py ger då 'lag' per paragrafrad): källan är den lag paragraferna tillhör (första; vid
            # paragrafer ur flera lagar nämns den första lagen, övriga syns i paragrafbeteckningen)
            lag_ = next((p_['lag'] for p_ in x['paragrafer'] if p_.get('lag')), None)
            andr = next((l_ for l_ in kravs(c, 'lagar') if l_['namn'] == lag_), andr0)
            return {'status': 'i beslutad lag', 'paragrafer': pars,
                    'kalla': {'text': f"{andr['namn']} konsoliderad, riksdagens öppna data, hämtad {HAMTAT} (lydelser enligt SFS {', '.join(andr['andringar'])})", 'url': sfsd['_meta'].get('url') or f"https://data.riksdagen.se/dokument/{andr['riksdagen_id']}.text"}}
        return {'status': None, 'paragrafer': pars, 'forklaring': 'Minst en paragraf saknar beslutad lydelse; se diff.'}

    # ---------- utmaningar ----------
    KAP = souinn['kapitel']; AVS = souinn['avsnitt']
    def kapitelrubrik(k): return {'kapitel': k, 'rubrik': KAP[k], 'kalla': {'text': f'{SOUNR}, innehållsförteckning, kapitel {k}', 'url': SOU_URL}}
    utmaningar = []
    for u in ut0:
        t = dict(u['utmaningstyp'])
        if u['id'] in LOGG:
            assert LOGG[u['id']]['gammal'] == t['primar'], u['id']
            t['primar'] = LOGG[u['id']]['ny']; t['motivering'] = LOGG[u['id']]['motivering']
            if t.get('sekundar') == t['primar']: t['sekundar'] = None
        # Kodarnas motiveringar (inte citat) får inte använda ord som kan läsas som bedömning av om en utmaning är löst/kvarstår;
        # en träff kräver en uttrycklig, loggad omformulering i config korrigeringar.motivering_omformulerad.
        if FORBJUDET.search(t['motivering']):
            if u['id'] not in OMFORM: sys.exit(f"{u['id']}: förbjudet ord i motiveringen utan loggad omformulering i config.")
            t['motivering'] = t['motivering'].replace(*OMFORM[u['id']])
        typ = {'primar': t['primar'], 'sekundar': t.get('sekundar'), 'motivering': t['motivering'], 'tolkning': True,
               'regelprovad': u['id'] in PROVADE, 'andrad_vid_regelprovning': u['id'] in LOGG}
        k = u['koppling']; niva = k['niva']; fids = k['forslag']
        if niva == 'förslag' and len(fids) > 1: niva = 'avsnitt'
        if fids: sou_avs = sorted({BOX[f]['avsnitt'] for f in fids}, key=avsort)
        elif niva == 'kapitel':
            sou_avs = sorted({a for g in k.get('grund', []) for a in re.findall(r'\b(\d{1,2}(?:\.\d{1,2}){1,3})\b', g) if a in AVS}, key=avsort) or None
        else: sou_avs = None
        koppling = {'niva': niva, 'forslag': fids, 'sou_avsnitt': sou_avs, 'kapitel': k.get('kapitel', []), 'tolkning': niva == 'tolkad'}
        if niva in ('förslag', 'avsnitt', 'kapitel'): koppling['grund'] = k.get('grund'); koppling['kalla_for_grund'] = k.get('kalla_for_grund')
        if niva == 'tolkad': koppling['motivering'] = k.get('motivering')
        refs = sorted({r for f in fids for r in F_AVS.get(f, [])}) if niva in ('förslag', 'avsnitt', 'tolkad') else []
        if refs:
            tr = [h for r in refs for h in sok(u['avsandare'], r)]
            def sokt(r):
                hb = PROPS[r.split(':')[0]].get('hoppade_delar_beskrivning')
                return {'text': f"{ptext[r]['proposition']} avsnitt {ptext[r]['avsnitt']} (hela avsnittets text" + (f", utom {hb}" if hb else '') + ')', 'url': ptext[r]['url']}
            namn = {'namngiven': bool(tr), 'propositionsavsnitt': refs, 'traffar': tr, 'sokt_i': [sokt(r) for r in refs],
                    'anm': 'Anger bara om avsändarens namn förekommer i avsnittets text; ingen bedömning av innehållet.'}
        else: namn = None
        utmaningar.append({'id': u['id'], 'avsandare': u['avsandare'], 'fokusgrupp': u['fokusgrupp'], 'grupp': u['grupp'],
                           'citat': u['citat'], 'sida': u['sida'], 'url': u['url'], 'ocr': u['ocr'], 'kalla': u['kalla'], 'citatkontroll': u['citatkontroll'],
                           'utmaningstyp': typ, 'koppling': koppling, 'sakomrade': [kapitelrubrik(x) for x in koppling['kapitel']] or None,
                           'skolform': u['skolform'], 'namngivning_i_propositionen': namn})

    # ---------- utredningsförslag ----------
    forslag = []
    for fid, b in BOX.items():
        forslag.append({'id': fid, 'text': b['text'], 'sou_avsnitt': b['avsnitt'], 'sou_avsnittsrubrik': b['avsnittsrubrik'], 'sou_sida': b['sida'],
                        'kalla': {'text': f"{SOUNR} {b['vol'].replace('volym-', 'volym ')} s. {b['sida']}, förslagsruta i avsnitt {b['avsnitt']}", 'url': SOU_PDF[b['vol']]},
                        'propositionsavsnitt': {'refs': F_AVS[fid], 'matchning': FP[fid]['matchning'], 'grund': REDAKTIONELL_GRUND.get(FP[fid]['matchning']), 'redaktionell': True},
                        'sfs': sfs_for(fid)})

    # ---------- propositionsavsnitt ----------
    REF_AV = {}
    for fid, refs in F_AVS.items():
        for r in refs: REF_AV.setdefault(r, []).append(fid)
    propositionsavsnitt = []
    for a in avv['avsnitt']:
        ref = f"{a['proposition'].split(':')[-1]}:{a['avsnitt']}"
        propositionsavsnitt.append({'ref': ref, 'proposition': a['proposition'], 'avsnitt': a['avsnitt'], 'rubrik': ptext[ref]['rubrik'] if ref in ptext else a['rubrik'],
                                    'overensstammelse': a['overensstammelse'], 'avvikelse_beskriven': a['avvikelse_beskriven'],
                                    'avvikelsetext': a['text'], 'sida': a['sida'], 'url': a['kalla']['url'], 'kalla': a['kalla'],
                                    'kopplade_utredningsforslag': {'forslag': sorted(REF_AV.get(ref, []), key=lambda x: int(x[1:])), 'redaktionell': True}})

    # ---------- avsändare och räkning ----------
    avs = {}
    for u in utmaningar:
        a = avs.setdefault(u['avsandare'], {'namn': u['avsandare'], 'fokusgrupp': u['fokusgrupp'], 'grupp': u['grupp'],
                                            'remissvar': {'text': f"Remissvar från {u['avsandare']} på {SOUNR} ({DNR})", 'url': u['url']}, 'antal_utmaningar': 0})
        a['antal_utmaningar'] += 1
    avsandare = sorted(avs.values(), key=lambda a: a['namn'])
    def rakna(sel):
        return {'antal_avsandare': len({u['avsandare'] for u in sel}), 'antal_utmaningar': len(sel),
                'per_fokusgrupp': {g: {'antal_avsandare': len({u['avsandare'] for u in sel if u['fokusgrupp'] == g}),
                                       'avsandare': sorted({u['avsandare'] for u in sel if u['fokusgrupp'] == g})} for g in FOKUS}}
    SAKKAP = [k for k in sorted(KAP, key=int) if kmin <= int(k) <= kmax]; SAKNAMN = [KAP[k] for k in SAKKAP]
    def har_sak(u, s): return any(x['rubrik'] == s for x in (u['sakomrade'] or []))
    raknning = {'princip': 'Unika avsändare per cell, efter primär utmaningstyp. En utmaning kopplad till flera kapitel räknas i varje kapitel.',
                'totalt': rakna(utmaningar),
                'per_utmaningstyp': {n: rakna([u for u in utmaningar if u['utmaningstyp']['primar'] == n]) for n, _ in TYPER},
                'per_sakomrade': {s: rakna([u for u in utmaningar if har_sak(u, s)]) for s in SAKNAMN},
                'utan_sakomrade': rakna([u for u in utmaningar if not u['sakomrade']]),
                'per_kombination': [dict(utmaningstyp=n, sakomrade=s, **rakna(sel)) for n, _ in TYPER for s in SAKNAMN
                                    if (sel := [u for u in utmaningar if u['utmaningstyp']['primar'] == n and har_sak(u, s)])]}

    # ---------- organisationernas status och kodningsmått (Sprint 17 B5/B6) ----------
    def organisationer():
        """Fokusorganisationerna som hör till reformens remiss (config fokusorganisationer, null = inte med), med status ur
        propositionens förteckning: svarat (remissinstans), spontant yttrande, avstått (publicerat avståendebrev, A2),
        på remisslistan utan svar (förteckningen skiljer inte mellan avstått och inte inkommit), inte på remisslistan."""
        f = rv['forteckning']; ut_ = []
        avst = {N(x['avsandare']): x for x in ((c.get('remissida_kontroll') or {}).get('ej_med_avstaenden') or [])}
        for gid, namn in (c.get('fokusorganisationer') or {}).items():
            if not namn: continue
            i = lambda lst: N(namn).lower() in {N(x).lower() for x in (lst or [])}
            if i(f.get('svarat')): st = 'svarat'
            elif i(f.get('spontant')): st = 'spontant yttrande'
            elif i(f.get('ej_svarat')): st = 'avstått' if N(namn) in avst else 'på remisslistan utan svar'
            else: st = 'inte på remisslistan'
            o = {'id': gid, 'namn': namn, 'status': st, 'kalla': rv['_meta']['kalla_forteckning']}
            if st == 'avstått': o['avstaende'] = {'citat': avst[N(namn)]['citat'], 'kalla': avst[N(namn)]['kalla']}
            if st == 'på remisslistan utan svar': o['anm'] = 'Förteckningen anger "har förklarat sig avstå eller har inte inkommit med yttrande" och skiljer inte mellan de två.'
            ut_.append(o)
        return ut_
    def kodningsmatt():
        def fil(namn):
            p_ = os.path.join(ROT, 'research/remissanalys/reformer', rid, 'kodning', namn)
            return json.load(open(p_, encoding='utf-8')) if os.path.exists(p_) else None
        di = fil('dubbelidentifiering.json'); dk = fil('dubbelkodning.json'); de = fil('dubbelkodning-efter-regelprovning.json')
        KODT = {x['id']: x['primar'] for x in (fil('utmaningstyp.json') or {}).get('kodning', [])}
        m = {'samstammighet_identifiering': {'overens': sum(x['overens'] for x in di['passager']), 'antal': len(di['passager'])} if di else None,
             'samstammighet_typning': {'overens': sum(1 for x in dk['kodning'] if KODT.get(x['id']) == x['primar']), 'antal': len(dk['kodning'])} if dk else None,
             'instruktion': 'research/remissanalys/kedja/KODINSTRUKTION.md'}
        if de: m['samstammighet_typning_efter_regelprovning'] = {'overens': de['_meta']['overens'], 'antal': de['_meta']['antal']}
        if not di: m['anm'] = 'Ingen oberoende identifiering finns för denna kodning.'
        return m

    # ---------- meta ----------
    publ = rv['publicerade']
    grp_i_korpus = []
    for g in FOKUS:
        namn_g = sorted({d['avsandare'] for d in publ if d['kategori'] == g})
        if not namn_g: continue
        grp_i_korpus.append(KORPUSNAMN.get(g) or ', '.join(next((k for k, v in ALIAS.items() if v == x), x) for x in namn_g))
    utan = [d['avsandare'] for d in publ if d['avsandare'] not in avs]
    saknade = [{'avsandare': s['avsandare'], 'fokusgrupp': s['fokusgrupp'], 'grupp': s['grupp'], 'skal': s['skal'], 'kalla': s['kalla']} for s in rv['opublicerade']]
    meta = {'reform': {'id': rid, 'namn': c['namn']}, 'kedja': kravs(c, 'kedja'), 'hamtningsdatum': HAMTAT,
            'korpus': {'publicerade_remissvar': len(publ), 'avsandare_med_utmaningar': len(avsandare), 'utmaningar': len(utmaningar),
                       'beskrivning': f"Publicerade remissvar på regeringen.se från fokusgrupperna ({', '.join(grp_i_korpus)}). "
                                      f"{len(publ)} remissvar är publicerade; {len(publ) - len(utan)} av avsändarna har minst en kodad utmaning"
                                      + (f" ({', '.join(utan)} har ingen)" if utan else '') + '.'
                                      # reformspecifika extra fokusgrupper (config extra_fokusgrupper) utan publicerat remissvar nämns;
                                      # utan nyckeln (alla andra reformer) läggs inget till
                                      + ''.join(f" {FG[g][0]} är fokusgrupp för denna reform men har inget publicerat remissvar." for g in FOKUS
                                                if g not in g0['fokusgrupper'] and not any(d['kategori'] == g for d in publ)),
                       'opublicerade_remissvar_som_saknas': {'antal': len(saknade), 'per_grupp': dict(collections.Counter(s['fokusgrupp'] for s in saknade)), 'avsandare': saknade}},
            'publicerade_avstaenden': [dict(x, kalla=x['kalla']) for x in ((c.get('remissida_kontroll') or {}).get('ej_med_avstaenden') or [])],
            'remissida_kontroll': ({k: v for k, v in c['remissida_kontroll'].items() if k in ('datum', 'regel')} if c.get('remissida_kontroll') else None),
            'organisationer': organisationer(), 'kodning': kodningsmatt(), 'begransningar': c.get('begransningar') or [],
            'tolkning': 'Fält med tolkning: true är tolkning (utmaningstyp; koppling med nivå "tolkad"). Kopplingen mellan utredningsförslag och propositionsavsnitt är redaktionell: true. Övrigt är mekaniskt härlett ur källtext.',
            'ingen_bedomning': 'Inget fält anger om en utmaning har lösts eller om propositionen har bemött den i sak.',
            'kopplingsnivaer': {'förslag': 'remissvarets hänvisning pekar ut exakt ett utredningsförslag', 'avsnitt': 'remissvarets hänvisning pekar ut ett SOU-avsnitt med flera förslag',
                                'kapitel': 'remissvaret anger bara kapitel (eller avsnitt utan förslagsruta); ingen koppling till enskilda förslag',
                                'tolkad': 'ingen egen hänvisning; koppling genom tolkning (tolkning: true)', 'null': 'ingen koppling'},
            'byggd_av': BYGGD_AV}
    data = {'meta': meta, 'utmaningstyper': [{'namn': n, 'definition': d} for n, d in TYPER], 'avgorande_regel': g0['avgorande_regel'],
            'sakomraden': [kapitelrubrik(k) for k in SAKKAP],
            'fokusgrupper': [{'id': g, 'namn': FG[g][0], 'grupp': FG[g][1]} for g in FOKUS],
            'avsandare': avsandare, 'utmaningar': utmaningar, 'propositionsavsnitt': propositionsavsnitt, 'utredningsforslag': forslag,
            'lagparagrafer': lagparagrafer, 'avsandarrakning': raknning}
    os.makedirs(os.path.join(ROT, os.path.dirname(UT)), exist_ok=True)
    with open(os.path.join(ROT, UT), 'w', encoding='utf-8') as fh:
        json.dump(data, fh, ensure_ascii=False, indent=1); fh.write('\n')
    C = collections.Counter
    print('skrev', UT, '| utmaningar', len(utmaningar), '| avsändare', len(avsandare))
    print('nivå', dict(C(u['koppling']['niva'] for u in utmaningar)))
    print('primär', dict(C(u['utmaningstyp']['primar'] for u in utmaningar)))
