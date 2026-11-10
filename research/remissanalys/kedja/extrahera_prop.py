#!/usr/bin/env python3
"""Steg K3 (deterministiskt, kräver kallor/): propositionerna → mellanfiler.
  prop-avsnitt.json               avsnitt med regeringens förslags-/bedömningsruta: varje underrubrik (del) med text och sidor;
                                  delen om utredningens förslag kontrolleras ordagrant mot PDF-texten (kontroll)
  propositionsavsnitt-text.json   samma avsnitt med text per tryckt sida (för namnsökning); rubriker följs över flera rader
  propositioner-innehall.json     propositionernas innehållsförteckning (för kontroll av rubrikerna)
  prop-lagtext.json               lagförslagen (kap. 2) ur tvåspaltig layout via ordkoordinater: föreslagen lydelse per paragraf
Konfiguration: propositioner[] (pdf_url, kort, avsnitt, utredningens_forslag_rubrik, ovriga_delrubriker, lagtext_sidor,
flerradiga_delrubriker, lagforslag_rubrik), layout.spaltforskjutning_pt, layout.ord_y_intervall_pt, layout.rensa_marginal_i_delar,
layout.rubrik_over_blankrad, layout.vanstermarginal_pt, layout.lagtext_tolerant.
Användning: python3 research/remissanalys/kedja/extrahera_prop.py <reform-id>"""
import html, os, re, subprocess, sys, unicodedata
from collections import Counter
sys.path.insert(0, os.path.dirname(__file__))
from gemensamt import reform_id, config, mapp, skriv, kravs

BAS = ['Regeringens förslag', 'Regeringens bedömning', 'Utredningens förslag', 'Utredningens bedömning', 'Promemorians förslag', 'Remissinstanserna']
PROPNR = r'Prop\. \d{4}/\d{2}:\d+'

def text(pdf, layout):
    ut = pdf[:-4] + ('.txt' if layout else '-r.txt')
    if not os.path.exists(ut): subprocess.run(['pdftotext'] + (['-layout'] if layout else []) + [pdf, ut], check=True)
    return open(ut, encoding='utf-8').read().split('\f')

def lab_regex(c):
    extra = []
    for p in c['propositioner']:
        extra += [r for r in (p.get('utredningens_forslag_rubrik') or []) if r not in BAS] + (p.get('ovriga_delrubriker') or [])
    alts = [re.escape(x) for x in dict.fromkeys(extra + BAS)] + [r'Skälen för regeringens.*', 'Lagrådet']
    return re.compile(r'^\s*(' + '|'.join(alts) + r')\s*$')

HEAD = re.compile(r'^\s{0,25}((?:1?\d)(?:\.\d{1,2}){0,3})\s{2,}([A-ZÅÄÖ].*)$')
RENSA_MARGINAL = False   # config layout.rensa_marginal_i_delar (av för betyg: identisk Sprint 16-fil)
RUBRIK_OVER_BLANKRAD = False   # config layout.rubrik_over_blankrad (av som standard): i avsnitt_text följs avsnittsrubriken även
                               # över blankrader fram till första underrubriken (prop. 2025/26:196 avsnitt 6: "Tiden för
                               # undervisningsuppdraget ska" / blankrad / "regleras"). Avsnitt utan regeringens ruta, vars
                               # brödtext då hamnar i rubriken, tas ändå bort; avsnitt med ruta har underrubriken direkt efter.
def printed(p, i=None):
    L = [l.strip() for l in p.split('\n') if l.strip()]
    for l in L[-3:] + L[:3]:
        m = re.fullmatch(r'(\d{1,3})(\s+Prop\..*)?', l) or re.fullmatch(r'Prop\. \S+\s+(\d{1,3})', l) or re.match(r'^(\d{1,3})\s{5,}', l)
        if m: return int(m.group(1))
    return None if i is None else i + 1

def avsnitt_delar(P, LAB):
    """Avsnitt med underrubriker (som i förstudie 1, prop_sec): text per del och sidor."""
    rows = []
    for i, p in enumerate(P):
        pg = printed(p) or (i + 1)
        for l in p.split('\n'):
            l2 = re.sub(r'^\s*' + PROPNR + r'\s{2,}', '', l); l2 = re.sub(r'\s{2,}' + PROPNR + r'\s*$', '', l2)
            if RENSA_MARGINAL:   # som i avsnitt_text: sidnummer/marginaltext på samma rad som brödtext (prop. 2025/26:193)
                                 # (bör slås på även för betyg vid en medveten omgenerering; ändrar då 24 delar i prop-avsnitt.json)
                l2 = re.sub(r'\s+' + PROPNR + r'\s*$', '', l2)
                mp = re.match(r'^\s*(\d{1,3})\s{3,}(\S.*)$', l2)
                if mp and abs(int(mp.group(1)) - pg) <= 1: l2 = mp.group(2)
                mt = re.match(r'^(.*\S)\s{3,}(\d{1,3})\s*$', l2)
                if mt and abs(int(mt.group(2)) - pg) <= 1: l2 = mt.group(1)
            rows.append((pg, l2))
    secs = []; cur = None; lab = None
    for pg, l in rows:
        if re.fullmatch(r'\s*\d{1,3}\s*', l): continue
        m = HEAD.match(l)
        if m and not re.search(r'\.{4,}', l):
            cur = {'avsnitt': m.group(1), 'rubrik': m.group(2).strip(), 'sida': pg, 'delar': {}}; secs.append(cur); lab = None; continue
        m = LAB.match(l)
        if m and cur is not None:
            lab = m.group(1)
            if lab in cur['delar']:
                n = 2
                while f'{lab}#{n}' in cur['delar']: n += 1
                lab = f'{lab}#{n}'
            cur['delar'][lab] = {'sida': pg, 'rader': []}; continue
        if cur is not None and lab:
            cur['delar'][lab]['rader'].append(l.strip()); cur['delar'][lab].setdefault('sidor', set()).add(pg)
    for s in secs:
        for k, d in s['delar'].items():
            t = re.sub(r'\s+', ' ', ' '.join(d.pop('rader'))); t = re.sub(r'(\w)- (?!och |eller |samt )(?=[a-zåäö])', r'\1', t)
            d['text'] = t.strip(); d['sidor'] = sorted(d.get('sidor', []))
        s['har_box'] = any(k.startswith('Regeringens') for k in s['delar'])
    return [s for s in secs if s['har_box']]

def avsnitt_text(P, LAB, want):
    """Avsnittens text per tryckt sida (som Sprint 16 T3/T5 forbered_arbetsfiler): sidnummer och marginaltext rensas,
    underrubriker inne i en del tas bort, rubriker följs över flera rader."""
    out = {}; cur = None; lab = None; secs = []; prev_blank = False; prev_text = ''; in_sub = False; rub_fort = False
    for i, p in enumerate(P):
        pg = printed(p, i); rader = p.split('\n')
        for ri, l in enumerate(rader):
            nasta = next((r.strip() for r in rader[ri + 1:] if r.strip()), '')
            l2 = re.sub(r'^\s*' + PROPNR + r'\s{2,}', '', l); l2 = re.sub(r'\s+' + PROPNR + r'\s*$', '', l2); l2 = re.sub(r'\s+Prop\.\s*$', '', l2); l2 = re.sub(r'^\s*\d{4}/\d{2}:\d+\s{2,}', '', l2)
            mp = re.match(r'^\s*(\d{1,3})\s{3,}(\S.*)$', l2)
            if mp and abs(int(mp.group(1)) - pg) <= 1: l2 = mp.group(2)
            mt = re.match(r'^(.*\S)\s{3,}(\d{1,3})\s*$', l2)
            if mt and abs(int(mt.group(2)) - pg) <= 1: l2 = mt.group(1)
            if re.fullmatch(r'\s*\d{1,3}\s*', l2): continue
            if in_sub and l2.strip() and not re.search(r'[.,:;-]$', l2.strip()) and re.match(r'[A-ZÅÄÖ]', re.sub(r'^' + PROPNR + r'\s+', '', nasta)) and not LAB.match(l2) and not HEAD.match(l2):
                continue
            in_sub = False
            if prev_blank and prev_text.endswith(('.', ':')) and l2.strip() and len(l2.strip()) < 70 and not re.search(r'[.,:;]$', l2.strip()) and lab and not LAB.match(l2) and not HEAD.match(l2):
                prev_blank = False; in_sub = True; continue
            prev_blank = not l2.strip()
            if l2.strip(): prev_text = l2.strip()
            m = HEAD.match(l2)
            if m and not re.search(r'\.{4,}', l2):
                cur = {'avsnitt': m.group(1), 'rubrik': m.group(2).strip(), 'delar': []}; secs.append(cur); lab = None; rub_fort = True; continue
            if rub_fort:
                if RUBRIK_OVER_BLANKRAD and not l2.strip(): continue   # rubriken fortsätter efter blankrad (se konstanten)
                if l2.strip() and not LAB.match(l2):
                    cur['rubrik'] = re.sub(r'(\w)- (?!och |eller |samt )(?=[a-zåäö])', r'\1', cur['rubrik'] + ' ' + l2.strip()); continue
                rub_fort = False
            m = LAB.match(l2)
            if m and cur is not None:
                lab = m.group(1); cur['delar'].append({'del': lab, 'sidor': {}}); continue
            if cur is not None and lab and l2.strip():
                cur['delar'][-1]['sidor'].setdefault(str(pg), []).append(l2.strip())
    for s in secs:
        if not any(d['del'].startswith('Regeringens') for d in s['delar']): continue
        if want and s['avsnitt'] not in want: continue
        out[s['avsnitt']] = {'rubrik': s['rubrik'], 'delar': [{'del': d['del'], 'sidor': [{'sida': int(k), 'text': re.sub(r'\s+', ' ', re.sub(r'(\w)- (?!och |eller |samt )(?=[a-zåäö])', r'\1', ' '.join(v))).strip()} for k, v in d['sidor'].items()]} for d in s['delar']]}
    return out

def innehall(P):
    toc = {}; buf = ''
    for p in P[:8]:
        for l in p.split('\n'):
            l2 = re.sub(r'^\s*' + PROPNR + r'\s+', '', l); l2 = re.sub(r'\s+' + PROPNR + r'\s*$', '', l2).strip()
            if not l2: continue
            if re.match(r'^(\d{1,2}(?:\.\d{1,2}){0,3})\s+\S', l2) and not buf: buf = l2
            elif buf: buf += ' ' + l2
            else: continue
            mm = re.match(r'^(\d{1,2}(?:\.\d{1,2}){0,3})\s+(.*?)\s*\.{3,}\s*(\d{1,3})$', buf)
            if mm:
                toc.setdefault(mm.group(1), {'titel': re.sub(r'(\w)- (?!och |eller |samt )(?=[a-zåäö])', r'\1', re.sub(r'\s+', ' ', mm.group(2))), 'sida': int(mm.group(3))}); buf = ''
            elif len(buf) > 400: buf = ''
    return toc

def foga_rubriker(P, rubriker):
    """Config propositioner[].flerradiga_delrubriker (tom/saknas som standard: P oförändrad): underrubriker som i PDF:en
    bryts över två rader, t.ex. prop. 2025/26:196 avsnitt 8–9 "Förslag från Utredningen om minskad administration och om" /
    "reglering av förskollärares och lärares tid (SOU 2025:26)". Två på varandra följande rader som tillsammans (efter att
    blanksteg och marginaltext "Prop. …" rensats) är exakt en sådan rubrik slås ihop till en rad, så att rubriken känns igen
    som del (den måste också stå i utredningens_forslag_rubrik eller ovriga_delrubriker)."""
    if not rubriker: return P
    def rensa(l): return re.sub(r'\s{2,}' + PROPNR + r'\s*$', '', re.sub(r'^\s*' + PROPNR + r'\s{2,}', '', l)).strip()
    ut = []
    for p in P:
        L = p.split('\n'); ny = []; i = 0
        while i < len(L):
            if i + 1 < len(L) and rensa(L[i]) and rensa(L[i]) + ' ' + rensa(L[i + 1]) in rubriker:
                ny.append(L[i][:len(L[i]) - len(L[i].lstrip())] + rensa(L[i]) + ' ' + rensa(L[i + 1])); i += 2; continue
            ny.append(L[i]); i += 1
        ut.append('\n'.join(ny))
    return ut

LAGFORSLAG_RUBRIK = r'^2\.(\d)\s+Förslag till lag om ändring i (.*)$'

def lagtext(pdf, forsta, sista, spalt, yint, rubrik=None, marginal=None, tolerant=False):
    """Föreslagen lydelse per paragraf ur kap. 2 (som Sprint 16 T3 prop_lagtext).
    rubrik: config propositioner[].lagforslag_rubrik, regex för lagförslagets rubrik (grupp 1 = nummer efter "2.", får saknas;
    grupp 2 = lagens namn). Standard "2.x Förslag till lag om ändring i …"; prop. 2025/26:193 har ett enda lagförslag som hela kap. 2.
    marginal: config layout.vanstermarginal_pt {"jamn": x, "udda": x} — fast vänstermarginal per sidparitet i stället för den
    vanligaste radstarten (som blir högerspalten på sidor med bara nya paragrafer, prop. 2025/26:193 s. 12–13).
    tolerant: config layout.lagtext_tolerant — paragrafrubriker utan mellanslag ("6a§", "2§") och "N kap." räknas bara som
    kapitelrubrik om raden inte börjar i vänster- eller högerspalten (annars är det slutet av en mening, "… i 21 och / 22 kap.")."""
    bb = subprocess.run(['pdftotext', '-bbox', '-f', str(forsta), '-l', str(sista), pdf, '-'], capture_output=True, text=True).stdout
    pages = bb.split('<page ')[1:]
    pend = []; lagforslag = []; cur_lf = None; kap = None; par = None; state = 'full'
    def flush_line(words, rc):
        ws = sorted(words); right = [w for w in ws if w[0] >= rc - 1.5]; left = [w for w in ws if w[0] < rc - 1.5]
        if not right: return 'left', ' '.join(w[2] for w in left), ''
        if not left: return 'right', '', ' '.join(w[2] for w in right)
        if right[0][0] - max(w[1] for w in left) >= 7: return 'two', ' '.join(w[2] for w in left), ' '.join(w[2] for w in right)
        return 'full', ' '.join(w[2] for w in ws), ' '.join(w[2] for w in ws)
    def toma(par, state):
        if pend and par is not None:
            if len(pend) >= 2 or state == 'two': par['nuvarande'].extend(pend)
            else: par['foreslagen'].extend(pend); par['nuvarande'].extend(pend)
        pend.clear()
    for pi, pg in enumerate(pages):
        pno = forsta + pi
        words = [(float(a), float(c_), html.unescape(t), float(b)) for a, b, c_, t in re.findall(r'xMin="([\d.]+)" yMin="([\d.]+)" xMax="([\d.]+)" yMax="[\d.]+">([^<]*)<', pg)]
        body = [w for w in words if yint[0] < w[3] < yint[1] and not re.fullmatch(r'Prop\.|\d{4}/\d{2}:\d+', w[2])]
        if not body: continue
        firsts = {}
        for x, x2, t, y in body: firsts.setdefault(round(y), []).append(x)
        lm = Counter(round(min(v)) for v in firsts.values()).most_common(1)[0][0]
        if marginal: lm = marginal['jamn' if pno % 2 == 0 else 'udda']
        body = [w for w in body if w[0] >= lm - 3 or w[2].startswith('2.')]
        rc = lm + spalt; lines = {}
        for x, x2, t, y in body: lines.setdefault(round(y), []).append((x, x2, t))
        for y in sorted(lines):
            ws = lines[y]; txt = ' '.join(w[2] for w in sorted(ws)).strip()
            if re.match(r'^(' + PROPNR + r')$', txt) or re.fullmatch(r'\d{1,3}', txt): continue
            m = re.match(rubrik or LAGFORSLAG_RUBRIK, txt)
            if m: cur_lf = {'lagforslag': '2.' + m.group(1) if m.group(1) else '2', 'titel': 'Förslag till lag om ändring i ' + m.group(2), 'paragrafer': []}; lagforslag.append(cur_lf); continue
            if cur_lf is None: continue
            if re.match(r'^(Nuvarande lydelse|Lydelse enligt .*?) Föreslagen lydelse$', txt): state = 'two'; continue
            mk = re.fullmatch(r'(\d+ (?:[a-z] )?)kap\.', txt)
            if mk and tolerant and any(abs(min(w[0] for w in ws) - x0) <= 3 for x0 in (lm, rc)): mk = None
            if mk: kap = mk.group(1).replace(' ', ''); continue
            mp = re.fullmatch(r'(\d+(?: [a-z])?) §(?:\s*\d{1,3})?', txt) or re.fullmatch(r'(\d+(?: [a-z])?) §', txt)
            if not mp and tolerant:   # även rad med nuvarande och föreslagen beteckning ("4e§ 4 d §4"): föreslagen (högra) gäller
                mp = re.fullmatch(r'(\d+(?: ?[a-z])?) ?§(?:\s*\d{1,3})?', txt) or re.fullmatch(r'\d+(?: ?[a-z])? ?§\s+(\d+(?: ?[a-z])?) ?§(?:\s*\d{1,3})?', txt)
            if mp and kap:
                toma(par, state); state = 'full'
                par = {'kap': kap, 'par': mp.group(1).replace(' ', ''), 'sida': pno, 'foreslagen': [], 'nuvarande': []}; cur_lf['paragrafer'].append(par); continue
            if re.match(r'^(1\. )?(Denna lag|Lagen) träder i kraft', txt) and cur_lf is not None:
                toma(par, state); state = 'full'
                par = {'kap': 'ikraft', 'par': 'övergångsbestämmelser', 'sida': pno, 'foreslagen': [], 'nuvarande': []}; cur_lf['paragrafer'].append(par)
            if par is None: continue
            if re.match(r'^\d{1,3}\s+Senaste lydelse', txt) or txt.startswith(('Senaste lydelse', 'Ändringen innebär')): continue
            kind, lt, rt = flush_line(ws, rc)
            if kind == 'left': pend.append(lt); continue
            if pend:
                if len(pend) >= 2 or state == 'two': par['nuvarande'].extend(pend)
                else: par['foreslagen'].extend(pend); par['nuvarande'].extend(pend)
                pend.clear()
            if kind == 'full': state = 'full'; par['foreslagen'].append(rt); par['nuvarande'].append(rt)
            elif kind == 'two': state = 'two'; par['nuvarande'].append(lt); par['foreslagen'].append(rt)
            elif kind == 'right': par['foreslagen'].append(rt)
    clean = lambda a: re.sub(r'\s+', ' ', re.sub(r'(\w)- (?=[a-zåäö])', r'\1', ' '.join(a))).strip()
    for lf in lagforslag:
        for p in lf['paragrafer']: p['foreslagen'] = clean(p['foreslagen']); p['nuvarande'] = clean(p['nuvarande'])
    return lagforslag

if __name__ == '__main__':
    rid = reform_id(); c = config(rid); LAB = lab_regex(c)
    RENSA_MARGINAL = bool((c.get('layout') or {}).get('rensa_marginal_i_delar'))
    RUBRIK_OVER_BLANKRAD = bool((c.get('layout') or {}).get('rubrik_over_blankrad'))
    spalt = kravs(c, 'layout', 'spaltforskjutning_pt'); yint = kravs(c, 'layout', 'ord_y_intervall_pt')
    pav = {}; ptx = {}; pin = {}; plag = {}
    for p in kravs(c, 'propositioner'):
        k = p['kort']; pdf = mapp(rid, 'kallor', 'prop', k + '.pdf')
        P = foga_rubriker(text(pdf, True), p.get('flerradiga_delrubriker')); RAW = text(pdf, False)
        want = None if p['avsnitt'] == 'alla' else set(p['avsnitt'])
        secs = [s for s in avsnitt_delar(P, LAB) if want is None or s['avsnitt'] in want]
        raw = re.sub(r'[\s\-­–]', '', unicodedata.normalize('NFC', re.sub(PROPNR + r'|\n\d{1,3}\n', '', '\f'.join(RAW))))
        for s in secs:
            for lab in p.get('utredningens_forslag_rubrik') or []:
                d = s['delar'].get(lab)
                if d:
                    nt = re.sub(r'[\s\-­–]', '', unicodedata.normalize('NFC', d['text'])); ch = [nt[i:i + 60] for i in range(0, len(nt), 60)]
                    d['kontroll'] = {'metod': 'automatisk mot pdftotext (blanksteg/bindestreck normaliserade)', 'hela_stycket': nt in raw,
                                     'delar_utan_traff': sum(1 for x in ch if x not in raw), 'delar': len(ch)}
        pav[k] = {'proposition': p['nr'], 'url': p['pdf_url'], 'avsnitt': secs}
        for av, x in avsnitt_text(P, LAB, want).items():
            ptx[f'{k}:{av}'] = {'proposition': p['nr'], 'avsnitt': av, 'rubrik': x['rubrik'], 'url': p['pdf_url'], 'delar': x['delar']}
        pin[k] = {'proposition': p['nr'], 'url': p['pdf_url'], 'innehallsforteckning': innehall(P)}
        if p.get('lagtext_sidor'):
            plag[k] = {'proposition': p['nr'], 'url': p['pdf_url'], 'lagforslag': lagtext(pdf, p['lagtext_sidor'][0], p['lagtext_sidor'][1], spalt, yint, p.get('lagforslag_rubrik'),
                                                                           c['layout'].get('vanstermarginal_pt'), bool(c['layout'].get('lagtext_tolerant')))}
    skriv(rid, 'prop-avsnitt.json', {'_meta': {'beskrivning': 'Avsnitt med regeringens förslags-/bedömningsruta; text per underrubrik.'}, 'propositioner': pav})
    skriv(rid, 'propositionsavsnitt-text.json', {'_meta': {'beskrivning': 'Avsnittens text per underrubrik och tryckt sida (pdftotext -layout); används för namnsökning.'}, 'avsnitt': ptx})
    skriv(rid, 'propositioner-innehall.json', {'_meta': {'beskrivning': 'Propositionernas innehållsförteckning; används för att kontrollera att avsnittsrubrikerna är fullständiga.'}, 'propositioner': pin})
    skriv(rid, 'prop-lagtext.json', {'_meta': {'beskrivning': 'Lagförslag (kap. 2) ur tvåspaltig layout via ordkoordinater; föreslagen lydelse per paragraf.'}, 'propositioner': plag})
    print(f"{rid}: {sum(len(v['avsnitt']) for v in pav.values())} avsnitt, {len(ptx)} avsnitt med sidtext, {sum(len(lf['paragrafer']) for v in plag.values() for lf in v['lagforslag'])} lagparagrafer")
