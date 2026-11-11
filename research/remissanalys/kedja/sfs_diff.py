#!/usr/bin/env python3
"""Steg K8 (deterministiskt): sfs-diff.json — per utredningsförslag (urval nedan):
SOU:ns föreslagna paragraf (författningskommentaren) → propositionens lagförslag → beslutad lydelse (konsoliderad SFS).
Paragrafer knyts till förslag via författningskommentarens avsnittshänvisningar (avsnittsnivå). Matchning: kapitel + nummer,
annars högst textlikhet inom kapitlet; likhet < 0,80 ⇒ manuell_granskning. Statusvärdet är mekaniskt.

BESLUTAD LYDELSE kommer bara från reformens egna ändrings-SFS (config lagar[].andringar, belagda i lagar[].andringar_kalla;
sfs.json från K4 innehåller bara sådana versioner). Lydelser från andra SFS-nummer genomför andra riksdagsbeslut och används
inte, inte heller som "gällande lydelse": en paragraf utan version från de egna SFS-numren får beslutad = null, status 'ej med'
och en status_kalla som säger att paragrafen inte ändras genom reformens SFS-nummer (Sprint 17, A1; ersätter nuvarande_sfs).
Textlikhetsmatchningen mot en annan paragraf i kapitlet används bara när paragrafnumret inte finns alls i den konsoliderade texten
(sfs.json paragrafer_i_lagen), dvs. när utredningens paragraf kan ha införts under ett annat nummer. Finns paragrafen men saknar
version från reformens SFS-nummer blir den 'ej med' i stället för att matchas mot en annan paragraf.

URVAL: alla utredningsförslag (standard; alla sju reformer sedan Sprint 17). Med config sfs_urval = "kodade" gäller i stället legacy-regeln från Sprint 16 (används inte längre): förslag som någon kodad utmaning (dubbletter inräknade) pekar på via
passagens förankring i förstudie 2 (passager.json forankrade_forslag, där en avsnittshänvisning utan förslagsruta faller tillbaka på
förälderavsnittet) eller paragrafhänvisning; saknas sådan används den tolkade kopplingen. Regeln behålls för att betygsfilen ska bli
identisk; för nya reformer bör urvalet i stället bli alla förslag (se KEDJA.md).

Konfiguration: sou.nr, sou.forfattningskommentar (dict för en lag, lista för flera), lagar (en eller flera), forordning_markor, hamtningsdatum.
Förutsättning: sou-forslag/sou-paragrafer (K2), prop-lagtext (K3), sfs (K4), passager (K6), kodning/utmaningar + tolkad-koppling (M1, M3).
Användning: python3 research/remissanalys/kedja/sfs_diff.py <reform-id>"""
import collections, difflib, os, re, sys
sys.path.insert(0, os.path.dirname(__file__))
from gemensamt import reform_id, config, las, skriv, kravs

EJ_LAGTEXT = r'ska ges i uppgift|ges i uppdrag|ska ge Statens skolverk i uppdrag|ska ansvara för|instruktion'
def n(t): return re.sub(r'[\s\-–­]', '', t.lower())
def sim(a, b): return difflib.SequenceMatcher(None, n(a), n(b), autojunk=False).ratio()
def wdiff(a, b):
    A = a.split(); B = b.split(); out = []
    for op, i1, i2, j1, j2 in difflib.SequenceMatcher(None, A, B, autojunk=False).get_opcodes():
        if op != 'equal': out.append({'op': {'replace': 'ersatt', 'delete': 'struken', 'insert': 'tillagd'}[op], 'fore': ' '.join(A[i1:i2]) or None, 'efter': ' '.join(B[j1:j2]) or None})
    return out
def match(cands, text):
    best = None
    for c in cands:
        r = sim(text, c['text'])
        if best is None or r > best[0]: best = (r, c)
    return best
def sfs_lista(a):
    """['2026:1242','2026:1243'] → '2026:1242/1243' (samma år), annars '/'-separerat."""
    ar = {x.split(':')[0] for x in a}
    return a[0] + ''.join('/' + x.split(':')[1] for x in a[1:]) if len(ar) == 1 else '/'.join(a)

if __name__ == '__main__':
    rid = reform_id(); c = config(rid)
    HAMTAT = kravs(c, 'hamtningsdatum'); SOUNR = kravs(c, 'sou', 'nr'); FK = kravs(c, 'sou', 'forfattningskommentar')
    lagar = kravs(c, 'lagar')
    # Flera lagar (config lagar med flera poster och sou.forfattningskommentar som lista, en post per lag med samma 'lag' som
    # lagar[].namn; sou-paragrafer.json har då fältet 'lag'): varje paragraf jämförs med sin egen lags lagförslag (rubriken
    # innehåller lagens bestamd_form), ändringslagar och konsoliderade text. Paragrafraderna får 'lag' och lagnamnet i 'paragraf'
    # ("2 kap. 7 § diskrimineringslagen") så att samma beteckning i två lagar inte krockar i bygg.py. Med en lag är allt som förut.
    FLERA = len(lagar) > 1
    if FLERA and not isinstance(FK, list): sys.exit('Flera lagar kräver sou.forfattningskommentar som lista (en post per lag).')
    for i_, L_ in enumerate(lagar):
        if not L_.get('bestamd_form'): sys.exit(f'lagar[{i_}].bestamd_form saknas i konfigurationen.')
    LAG = lagar[0]; LAGNAMN = LAG['namn']; LAG_BEST = LAG.get('bestamd_form') or sys.exit('lagar[0].bestamd_form saknas i konfigurationen.'); ANDR = tuple(LAG['andringar'])
    boxes = las(rid, 'sou-forslag.json'); U_SOU = boxes['_meta']['pdf']; boxes = {b['id']: b for b in boxes['forslag']}
    sou = las(rid, 'sou-paragrafer.json')['paragrafer']
    sfsd = las(rid, 'sfs.json'); sl = sfsd['lagar'][0]; sfs = sl['versioner'] + sl['overgangsbestammelser']; U_SFS = sl['url']
    FKS = {fk['lag']: fk for fk in FK} if FLERA else {LAGNAMN: FK}
    SL = {x['namn']: x for x in sfsd['lagar']}
    # per lag: namn, bestämd form, ändringslagar, konsoliderad text (versioner + övergångsblock), url, författningskommentarens avsnitt
    LI = {L_['namn']: {'namn': L_['namn'], 'best': L_['bestamd_form'], 'andr': tuple(L_['andringar']), 'sl': SL[L_['namn']],
                       'sfs': SL[L_['namn']]['versioner'] + SL[L_['namn']]['overgangsbestammelser'], 'url': SL[L_['namn']]['url'], 'fk': FKS[L_['namn']]}
          for L_ in lagar}
    FORORD = [(f['namn'], f['url'], f['markor']) for f in sfsd['forordningar']]
    props = list(las(rid, 'prop-lagtext.json')['propositioner'].values()); U_P = {p['proposition']: p['url'] for p in props}
    # --- urval (legacy-regel, se docstring) ---
    P = {p['id']: p for p in las(rid, 'passager.json')['passager']}
    KT = {x['uid']: x for x in las(rid, 'kodning/tolkad-koppling.json')['kopplingar']}
    PAR = {(p['kap'], p['par'].replace(' ', '')): p['avsnitt'] for p in sou if p['kap'] != 'ikraft'}
    f_exact = lambda sec: [b['id'] for b in boxes.values() if b['avsnitt'] == sec or b['avsnitt'].startswith(sec + '.')]
    FIDS = set()
    URVAL = c.get('sfs_urval') or 'alla'
    if URVAL == 'alla': FIDS = set(boxes)
    for x in (las(rid, 'kodning/utmaningar.json')['utmaningar'] if URVAL == 'kodade' else []):
        p = P[x['id']]
        fids = set(p['forankrade_forslag']) | {f for m in re.finditer(r'(\d{1,2}) kap\.\s*(\d{1,3}(?:\s?[a-z])?)\s*§', p['text'])
                                              for k in [(m.group(1), m.group(2).replace(' ', ''))] if k in PAR for a in PAR[k] for f in f_exact(a)}
        FIDS |= fids if fids else set((KT.get(x['uid']) or {}).get('forslag') or [])
    # --- jämförelse ---
    andr_txt = sfs_lista(list(ANDR)) if not FLERA else '; '.join(f"{x['best']}: {sfs_lista(list(x['andr'])) if x['andr'] else 'ingen'}" for x in LI.values())
    FK_AVS = FK['avsnitt'] if not FLERA else ', '.join(fk['avsnitt'] for fk in FK)          # i texter om författningskommentaren
    LAG_BEST_ALLA = LAG_BEST if not FLERA else ' eller '.join(x['best'] for x in LI.values())
    def paragrafer_for(f):
        a = boxes[f]['avsnitt']
        return [p for p in sou if any(x == a or x.startswith(a + '.') or a.startswith(x + '.') for x in p['avsnitt'])]
    res = []
    for f in sorted(FIDS, key=lambda x: int(x[1:])):
        b = boxes[f]; pp = paragrafer_for(f)
        post = {'forslag': f, 'sou_avsnitt': b['avsnitt'], 'forslag_kalla': {'text': f"{SOUNR} s. {b['sida']}", 'url': U_SOU[b['vol']]}, 'paragrafer': []}
        if pp and not any(p['text'].strip() for p in pp):
            # Författningskommentaren återger inte paragraftexten (t.ex. SOU 2021:33): ingen textjämförelse är möjlig,
            # så status null med förklaring i stället för meningslösa likhetsvärden (Sprint 17).
            post.update(status=None, status_kalla={'text': f"SOU:ns författningskommentar ({FK_AVS}) hänvisar paragraferna " + ', '.join(f"{p['kap']} kap. {p['par']} §" for p in pp if p['kap'] != 'ikraft') + ' till avsnitt ' + b['avsnitt'] + ' men återger inte deras föreslagna lydelse; ingen maskinell jämförelse med beslutad lydelse är gjord.', 'url': U_SOU[b['vol']]})
            res.append(post); continue
        pp = [p for p in pp if p['text'].strip()]
        if not pp:
            if re.search(EJ_LAGTEXT, b['text']):
                post.update(status='ej lagtext', status_kalla={'text': f"Förslaget gäller uppdrag/ansvar för myndighet; ingen paragraf i SOU:ns författningskommentar till {LAG_BEST_ALLA} (avsnitt {FK_AVS}) hänvisar till avsnitt " + b['avsnitt'], 'url': U_SOU[b['vol']]})
            else:
                if not FORORD:
                    post.update(status=None, status_kalla={'text': f"Ingen paragraf i SOU:ns författningskommentar till {LAG_BEST_ALLA} ({FK_AVS}) hänvisar till avsnitt " + b['avsnitt'] + '; inga förordningar är angivna för jämförelse i konfigurationen.', 'url': U_SOU[b['vol']]})
                    res.append(post); continue
                mk = '; '.join(f'{sum(fo[2].get(m, 0) for fo in FORORD)} träffar på "{m}"' for m in c.get('forordning_markor') or [])
                traffar = sum(sum(fo[2].values()) for fo in FORORD)
                if not mk or traffar:
                    # Utan markör (eller med träffar) går det inte att avgöra mekaniskt om förslaget finns i förordningen:
                    # status null med förklaring i stället för ett obelagt "ej i SFS" (Sprint 17).
                    post.update(status=None, status_kalla={'text': f"Ingen paragraf i SOU:ns författningskommentar till {LAG_BEST_ALLA} ({FK_AVS}) hänvisar till avsnitt " + b['avsnitt'] + ' — förslaget avser förordningsnivå (eller annan reglering). '
                                + ('Ingen textmarkör är angiven, så' if not mk else f'Markörerna har träffar ({mk}), så') + ' det är inte maskinellt avgjort om förslaget har genomförts i förordningarna: ' + '; '.join(x[0] for x in FORORD) + '.', 'url': FORORD[0][1]})
                    res.append(post); continue
                post.update(status=f'ej i SFS per {HAMTAT}', status_kalla={'text': f"Ingen paragraf i SOU:ns författningskommentar till {LAG_BEST_ALLA} ({FK_AVS}) hänvisar till avsnitt " + b['avsnitt'] + ' — förslaget avser förordningsnivå. Konsoliderade förordningar hämtade ' + HAMTAT + (f" innehåller inte {kravs(c, 'forordning_markor_beskrivning')} ({mk})" if mk else ' (jämförda; ingen markör angiven)') + ': ' + '; '.join(x[0] for x in FORORD),
                                                                              'url': FORORD[0][1], 'ovriga_urler': [x[1] for x in FORORD[1:]]})
            res.append(post); continue
        stats = []
        for p in pp:
            L = LI[p.get('lag', LAGNAMN)]; fk_ = L['fk']; sl = L['sl']; sfs = L['sfs']; U_SFS = L['url']; LAGNAMN_ = L['namn']; ANDR_ = L['andr']
            fk_text = f"författningskommentar {fk_['avsnitt']}"
            rad = {'paragraf': f"{p['kap']} kap. {p['par']} §" + (f" {L['best']}" if FLERA else ''), 'sou': {'text': p['text'], 'kalla': {'text': f"{SOUNR} s. {p['sida']} ({fk_text})", 'url': U_SOU[fk_.get('vol') or ('volym-1' if 'volym-1' in U_SOU else next(iter(U_SOU)))]}}}
            if FLERA: rad['lag'] = LAGNAMN_
            pc = [dict(text=q['foreslagen'], kap=q['kap'], par=q['par'], sida=q['sida'], prop=pr['proposition'], lf=lf['lagforslag']) for pr in props for lf in pr['lagforslag'] for q in lf['paragrafer'] if q['kap'] == p['kap']
                  and (not FLERA or L['best'] in lf['titel'])]
            same = [x for x in pc if x['par'] == p['par'].replace(' ', '')]
            m = match(same, p['text']) or match(pc, p['text'])
            if m:
                r, x = m
                rad['proposition'] = {'text': x['text'], 'paragraf': f"{x['kap']} kap. {x['par']} §", 'likhet_mot_sou': round(r, 3), 'kalla': {'text': f"{x['prop']} s. {x['sida']}, lagförslag {x['lf']}", 'url': U_P[x['prop']]},
                                      'matchning': 'nummer' if x['par'] == p['par'].replace(' ', '') else 'textlikhet', 'manuell_granskning': r < 0.8}
            else: rad['proposition'] = None
            sc = [v for v in sfs if v['kap'] == p['kap'] and v['lag'] in ANDR_]
            same = [v for v in sc if v['par'] == p['par'].replace(' ', '')]
            finns = f"{p['kap']}:{p['par'].replace(' ', '')}" in set(sl.get('paragrafer_i_lagen') or [])
            # Samma nummer från egna SFS → nummermatchning. Annars textlikhet inom kapitlet bara om paragrafnumret saknas i lagen.
            ms = match(same, p['text']) or (None if finns else match(sc, p['text']))
            if ms:
                r, v = ms
                rad['beslutad'] = {'text': v['text'], 'paragraf': f"{v['kap']} kap. {v['par']} §", 'sfs': v['lag'], 'ikraft': v['ikraft'], 'likhet_mot_sou': round(r, 3),
                                   'kalla': {'text': f"{LAGNAMN_} {v['kap']} kap. {v['par']} § i lydelse enligt SFS {v['lag']}" + (f", träder i kraft {v['ikraft']}" if v['ikraft'] else '') + f"; konsoliderad text hämtad {HAMTAT} ({sl['andrad_tom']})", 'url': U_SFS},
                                   'matchning': 'nummer' if v['par'] == p['par'].replace(' ', '') else 'textlikhet', 'manuell_granskning': r < 0.8}
                if r >= 0.999: st = 'oförändrad'
                else: st = 'ändrad'; rad['diff_sou_mot_beslutad'] = wdiff(p['text'], v['text'])
            else:
                rad['beslutad'] = None
                # Ingen version i kapitlet från reformens egna ändrings-SFS. Gällande lydelse från andra SFS-nummer redovisas inte
                # (den genomför andra beslut); förklaringen anger vilka SFS-nummer som har prövats.
                egna_txt = sfs_lista(list(ANDR_)) if ANDR_ else 'inga'
                if finns: vad = f"{LAGNAMN_} {p['kap']} kap. {p['par']} § finns i den konsoliderade texten hämtad {HAMTAT} ({sl['andrad_tom']}), men ingen av dess lydelser är införd genom reformens ändrings-SFS ({egna_txt})"
                else: vad = f"{LAGNAMN_} {p['kap']} kap. {p['par']} § finns inte i den konsoliderade texten hämtad {HAMTAT} ({sl['andrad_tom']}), och {p['kap']} kap. har ingen lydelse införd genom reformens ändrings-SFS ({egna_txt})"
                rad['status_kalla'] = {'text': vad + '; paragrafen ändras alltså inte genom dessa SFS-nummer. Lydelser införda genom andra SFS-nummer används inte eftersom de genomför andra riksdagsbeslut.', 'url': U_SFS}
                st = 'ej med'
            rad['status'] = st; stats.append(st)
            rad['manuell_granskning'] = bool((rad.get('proposition') or {}).get('manuell_granskning') or (rad.get('beslutad') or {}).get('manuell_granskning'))
            post['paragrafer'].append(rad)
        us = set(stats)
        post['status'] = stats[0] if len(us) == 1 else 'blandad'
        post['status_per_paragraf'] = {s: stats.count(s) for s in dict.fromkeys(stats)}   # första förekomst: deterministisk ordning
        post['status_kalla'] = {'text': f'Härledd per paragraf: SOU:ns föreslagna lydelse jämförd med beslutad lydelse (SFS {andr_txt}). Statusvärdet är mekaniskt (textlikhet), inte en bedömning.', 'url': U_SFS if not FLERA else LI[pp[0].get('lag')]['url']}
        res.append(post)
    blk = (f"{LAGNAMN} konsoliderad, riksdagens öppna data (Källa: Regeringskansliet / Lagrummet), " + LI[LAGNAMN]['sl']['andrad_tom']) if not FLERA else \
          '; '.join(f"{x['namn']} konsoliderad, " + x['sl']['andrad_tom'] for x in LI.values()) + ' (riksdagens öppna data, Källa: Regeringskansliet / Lagrummet)'
    meta = {'hamtningsdatum': HAMTAT, 'beslutad_lydelse_kalla': blk + '. Ändrings-SFS i original (svenskforfattningssamling.se) nåddes inte från miljön.',
            'statusregler': {'oförändrad': 'SOU:ns föreslagna paragraf = beslutad lydelse (normaliserad textlikhet ≥ 0,999)', 'ändrad': 'beslutad lydelse finns men skiljer sig; ordagrann ord-diff sparas',
                             'ej med': f'ingen version införd genom SFS {andr_txt} för paragrafen (lydelser från andra SFS-nummer används inte)', 'ej lagtext': 'förslaget är inte författningstext (uppdrag/ansvar)', f'ej i SFS per {HAMTAT}': 'förslaget avser förordning som ännu inte finns i SFS'},
            'matchning': 'Paragrafer matchas på kapitel + nummer bland lydelser införda genom reformens ändrings-SFS; saknas paragrafnumret helt i den konsoliderade texten används högst textlikhet inom kapitlet (bland samma lydelser). Likhet < 0,80 ⇒ manuell_granskning: true.',
            'forslag_till_paragraf': 'Paragrafer knyts till förslag via SOU:ns författningskommentar ("Bestämmelsen behandlas i avsnitt …"), dvs. på avsnittsnivå — flera förslag i samma avsnitt delar paragrafer.'}
    skriv(rid, 'sfs-diff.json', {'_meta': meta, 'forslag': res})
    rows = [x for r in res for x in r['paragrafer']]
    print(f"{rid}: förslag {len(res)} {dict(collections.Counter(r['status'] for r in res))}; paragrafrader {len(rows)}, manuell granskning {sum(x['manuell_granskning'] for x in rows)}")
