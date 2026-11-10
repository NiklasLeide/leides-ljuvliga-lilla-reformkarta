#!/usr/bin/env python3
"""Steg K2 (deterministiskt, kräver kallor/): utredningsbetänkandet → mellanfiler.
  sou-innehall.json   innehållsförteckningen (lista + kapitel + avsnitt inom förslagskapitlen)
  sou-forslag.json    förslagsrutorna ("Förslag:") med id F01…, volym, tryckt sida, avsnitt och ordagrann text
  sou-paragrafer.json författningskommentarens återgivna paragrafer med "behandlas i avsnitt …" (+ ikraftträdande)
Konfiguration: sou.pdf, sou.innehall_sidor, sou.forslagskapitel, sou.forfattningskommentar.
Användning: python3 research/remissanalys/kedja/extrahera_sou.py <reform-id>"""
import os, re, subprocess, sys
sys.path.insert(0, os.path.dirname(__file__))
from gemensamt import reform_id, config, mapp, skriv, kravs

def text(pdf, layout):
    ut = pdf[:-4] + ('.txt' if layout else '-r.txt')
    if not os.path.exists(ut):
        subprocess.run(['pdftotext'] + (['-layout'] if layout else []) + [pdf, ut], check=True)
    return open(ut, encoding='utf-8').read().split('\f')

def innehall(P, sidor, kort_utfyllnad=False):
    """kort_utfyllnad: config sou.innehall_kort_utfyllnad (av som standard): utfyllnaden före sidnumret får också vara två
    punkter (SOU 2021:33 avsnitt 5.2.9: "Nationella prov i årskurs 4(5), 7(8) och 10(11) .. 297")."""
    toc = []; buf = ''
    utf = r'\.{2,}' if kort_utfyllnad else r'\.{3,}'
    for p in P[sidor[0] - 1:sidor[1]]:
        for l in p.split('\n'):
            s = l.strip()
            if not s: continue
            m = re.match(r'^(\d{1,2}(?:\.\d{1,2}){0,4})\s+(.*)$', s)
            if m: buf = s
            elif buf: buf += ' ' + s
            else: continue
            # utfyllnaden före sidnumret är normalt "....", men kan vara en enda punkt när rubriken fyller raden (SOU 2025:8 kap. 4)
            mm = re.match(r'^(\d{1,2}(?:\.\d{1,2}){0,4})\s+(.*?)\s*(?:' + utf + r'|(?<=\s)\.)\s*(\d{1,4})$', buf)
            if mm: toc.append({'avsnitt': mm.group(1), 'rubrik': re.sub(r'\s+', ' ', mm.group(2)), 'sida': int(mm.group(3))}); buf = ''
    return toc

def printed(p):
    lines = [l.strip() for l in p.strip().split('\n') if l.strip()]
    for l in lines[-1:] + lines[:1]:
        if re.fullmatch(r'\d{1,4}', l): return int(l)
    return None

def rutor(Pvol, sounr, ruta_rubriker=None, over_sidbrytning=False, bindestreck_skydd=False, slutrader=None, kant_tolerans=1):
    """Förslags-/bedömningsrutor. Standard (SOU 2025:18): "Förslag:"/"Bedömning:" med texten på samma rad.
    Config sou.ruta_rubriker = {"Förslag": regex, "Bedömning": regex} för betänkanden med andra rutrubriker (t.ex. SOU 2025:8:
    "Utredningens förslag" på egen rad + punktlista). Då avslutas rutan också vid en ensam siffra som inte är sidnumret
    (fotnot direkt under rutan, utan blankrad).
    Config sou.ruta_over_sidbrytning (av som standard): rutor som löper över blankrader och sidbrytningar (SOU 2025:19, där
    rutorna har flera stycken och ofta fortsätter på nästa sida). Rutan slutar då först vid nästa rutrubrik, vid en numrerad
    avsnittsrubrik eller vid en rad efter blankrad som börjar till vänster om rutans vänsterkant på sidan (brödtexten står
    längre ut än den indragna rutan). En ensam siffra som inte är sidnumret är en fotnotsmarkör: resten av sidan hoppas
    över. Sidnummer och sidhuvuden ("SOU 2025:19   Läsning") hoppas över. På en ny sida sätts vänsterkanten av första raden.
    Config sou.ruta_bindestreck_skydd (av som standard): avstavningsfogningen rör inte "betygs- och", "-eller", "-samt"
    (som i extrahera_prop.py); utan skyddet blir det "betygsoch".
    Config sou.ruta_slutrader (tom som standard, bara med ruta_over_sidbrytning): regexar för rader som alltid avslutar rutan,
    t.ex. "Skälen för utredningens" i SOU 2025:9, där brödtexten efter en ruta som slutar längst ned på sidan börjar på nästa
    sida (och vänsterkanten där inte kan skilja rutan från brödtexten).
    Config sou.ruta_kant_tolerans (1 som standard, bara med ruta_over_sidbrytning): en rad efter blankrad avslutar rutan om
    den börjar mer än så många tecken till vänster om rutans vänsterkant. SOU 2025:9 (0): brödtexten står bara ett tecken
    längre ut än rutan."""
    hdr = re.compile(r'^\s*' + re.escape(sounr) + r'\s*$')
    RR = ruta_rubriker or {'Förslag': 'Förslag:', 'Bedömning': 'Bedömning:'}
    LABEL = re.compile(r'^\s*(?:' + '|'.join(f'(?P<{"F" if k == "Förslag" else "B"}>{v})' for k, v in RR.items()) + r')\s*(?P<T>.*)$')
    RUBRIK = re.compile(r'^\s{0,25}(\d{1,2}(?:\.\d{1,2}){1,4})\s{1,12}([A-ZÅÄÖ].{3,90})$')   # numrerad avsnittsrubrik (bara over_sidbrytning)
    out = []
    for vol, P in Pvol:
        sec = None; sectitle = None
        for i, p in enumerate(P):
            lines = p.split('\n')
            for j, l in enumerate(lines):
                m = re.match(r'^\s{0,25}(\d{1,2}(?:\.\d{1,2}){1,4})\s{1,6}([A-ZÅÄÖ].{3,90})$', l)
                if m and not re.search(r'\.{4,}|\s\d+$', l): sec = m.group(1); sectitle = m.group(2).strip()
                mb = LABEL.match(l)
                if mb:
                    typ = 'Förslag' if mb.group('F') is not None else 'Bedömning'
                    ind = len(l) - len(l.lstrip())
                    txt = [mb.group('T').strip()]; k = j + 1; blank = 0; pp = i; LL = lines
                    sidan = i; marg = ind   # over_sidbrytning: rutans sida och vänsterkant
                    while True:
                        if k >= len(LL):
                            pp += 1
                            if pp >= len(P): break
                            LL = P[pp].split('\n'); k = 0; continue
                        s = LL[k]
                        if not s.strip():
                            blank += 1
                            if blank >= 1 and len(txt) > 1 and not over_sidbrytning: break
                            k += 1; continue
                        if LABEL.match(s): break
                        if over_sidbrytning:
                            st = s.strip(); ind_s = len(s) - len(s.lstrip())
                            if re.fullmatch(r'\d{1,3}', st) and int(st) != printed(P[pp]): k = len(LL); continue   # fotnoter till sidans slut
                            if re.fullmatch(r'\d{1,4}', st) or hdr.match(st) or (sounr in st and re.search(r'\s{3,}', st)): k += 1; continue
                            if RUBRIK.match(s) and not re.search(r'\.{4,}', s): break
                            if slutrader and any(re.match(r, st) for r in slutrader): break
                            if pp != sidan: sidan = pp; marg = ind_s
                            elif blank and ind_s < marg - kant_tolerans: break
                            marg = min(marg, ind_s); blank = 0
                            txt.append(re.sub(r'\s{3,}.*$', '', st) if ind < 5 else st); k += 1; continue
                        if ruta_rubriker and re.fullmatch(r'\d{1,3}', s.strip()) and int(s.strip()) != printed(P[pp]) and len(txt) > 1: break
                        if hdr.match(s.strip()) or re.match(r'^\s*\d{1,4}\s*$', s): k += 1; continue
                        blank = 0; txt.append(re.sub(r'\s{3,}.*$', '', s.strip()) if ind < 5 else s.strip()); k += 1
                    t = ' '.join(txt); t = re.sub(r'(\w)- (?!och |eller |samt )(?=[a-zåäö])' if bindestreck_skydd else r'(\w)- (?=[a-zåäö])', r'\1', t)
                    out.append({'vol': vol, 'pdfsida': i + 1, 'sida': printed(p), 'avsnitt': sec, 'avsnittsrubrik': sectitle, 'typ': typ, 'text': t})
    return out

def tilldela_avsnitt(boxes, toc, Pvol):
    """Avsnitt för varje ruta ur innehållsförteckningen (sista avsnitt som börjar på eller före rutans sida)."""
    P = dict(Pvol); norm = lambda s: re.sub(r'\s+', ' ', s)
    for b in boxes:
        pg = b['sida']; page = norm(P[b['vol']][b['pdfsida'] - 1]); pos = page.find(b['text'][:40])
        chosen = None
        for t in reversed([t for t in toc if t['sida'] <= pg]):
            if t['sida'] < pg: chosen = t; break
            hp = page.find(t['rubrik'][:25])
            # hp == pos: rutans text börjar med samma ord som avsnittsrubriken (SOU 2025:9 8.1.12, "Möjligheten att läsa
            # svenska …"), så find() hittar rubriken även för rutan; rubriken står då före rutan
            if hp != -1 and (pos == -1 or hp <= pos): chosen = t; break
        b['avsnitt'] = chosen['avsnitt'] if chosen else None; b['avsnittsrubrik'] = chosen['rubrik'] if chosen else None
    n = 0; out = []
    for b in boxes:
        if b['typ'] != 'Förslag': continue
        n += 1; out.append(dict(b, id=f'F{n:02d}'))
    return out

def paragrafer(Praw, toc, fk, sounr, forskjutning=0):
    """forskjutning: config sou.pdf_sidforskjutning (0 som standard) = PDF-sida minus tryckt sida. Innehållsförteckningens
    sidor är tryckta; i SOU 2021:33 är omslaget PDF-sida 1, så tryckt sida s står på PDF-sida s + 1. Paragrafernas 'sida'
    är fortfarande den tryckta sidan.
    Config sou.forfattningskommentar.borja_vid_rubrik (av som standard): rader på startsidan före raden som är exakt
    avsnittsnumret (t.ex. "9.2") hoppas över, när föregående avsnitt (9.1, en annan lag) slutar på samma sida."""
    sid = {t['avsnitt']: t['sida'] for t in toc}
    # slut_avsnitt är normalt ett numrerat avsnitt i innehållsförteckningen; är det en onumrerad rubrik (t.ex. "Referenser")
    # anges dess tryckta sida i config sou.forfattningskommentar.slut_sida
    start, slut = sid[fk['avsnitt']], (sid[fk['slut_avsnitt']] if fk['slut_avsnitt'] in sid else kravs(fk, 'slut_sida'))
    rubrik_fk = 'Författningskommentar'
    rows = []
    # config sou.forfattningskommentar.radkorrigeringar: {"rad i pdftotext": ["rad 1", "rad 2", ...]} för rader där pdftotext
    # har slagit ihop två rader (t.ex. SOU 2025:8: "Övervägandena finns i avsnitt 4.1.14 §" = slutet av 13 c § + rubriken 14 §)
    # eller tappat mellanslag i en paragrafrubrik ("5a§" → "5 a §")
    korr = fk.get('radkorrigeringar') or {}
    vantar_rubrik = bool(fk.get('borja_vid_rubrik'))
    for pg in range(start, slut + 1):
        for l0 in Praw[pg - 1 + forskjutning].split('\n'):
          if vantar_rubrik:
            if l0.strip() == fk['avsnitt']: vantar_rubrik = False
            continue
          for l in korr.get(l0.strip(), [l0]):
            s = l.strip()
            if s in (sounr, rubrik_fk) or re.fullmatch(r'\d{3}', s): continue
            rows.append((pg, s))
    out = []; kap = None; cur = None; mode = None
    HEAD = re.compile(r'^(\d+(?: [a-z])?) ?§$')
    # config sou.forfattningskommentar.inline_rubriker (av som standard): kapitelrubriken står på samma rad som kapitlets namn
    # ("3 kap. Barns och elevers utveckling mot målen") och paragrafens text börjar på rubrikraden ("1 § I detta kapitel …"),
    # som i SOU 2025:44. Paragrafrubriken kräver versal efter "§" (annars är det en hänvisning mitt i en mening, "16 § och …").
    INLINE = bool(fk.get('inline_rubriker'))
    KAP_I = re.compile(r'^(\d+(?: [a-z])?) kap\.\s+[A-ZÅÄÖ][^§]*$'); HEAD_I = re.compile(r'^(\d+(?: [a-z])?) § ([A-ZÅÄÖ].*)$')
    for pg, s in rows:
        if re.fullmatch(r'\d+(?: [a-z])? kap\.', s): kap = s.replace(' kap.', ''); continue
        if INLINE and KAP_I.match(s): kap = KAP_I.match(s).group(1); continue
        if s.startswith('Ikraftträdande och övergångsbestämmelser'):
            cur = {'kap': 'ikraft', 'par': 'övergångsbestämmelser', 'sida': pg, 'text': [], 'kommentar': []}; out.append(cur); mode = 'text'; continue
        if s == fk['slut_avsnitt']: break
        m = HEAD.match(s)
        if m and kap:
            cur = {'kap': kap, 'par': m.group(1), 'sida': pg, 'text': [], 'kommentar': []}; out.append(cur); mode = 'text'; continue
        mi = HEAD_I.match(s) if INLINE else None
        if mi and kap:
            cur = {'kap': kap, 'par': mi.group(1), 'sida': pg, 'text': [mi.group(2)], 'kommentar': []}; out.append(cur); mode = 'text'; continue
        if cur is None: continue
        if mode == 'text' and re.match(r'^(Paragrafen|Bestämmelsen|Paragrafens|I paragrafen|Ändringen|Första stycket|Andra stycket|Övervägandena)\b', s):
            mode = 'komm'
        (cur['text'] if mode == 'text' else cur['kommentar']).append(s)
    # config sou.forfattningskommentar.hanvisningsfraser (tom som standard): fler fraser som inleder hänvisningen till avsnittet
    # med övervägandena, t.ex. "Överväganden finns i avsnitt" (SOU 2025:44, utan bestämd form)
    FRASER = ''.join('|' + re.escape(f) for f in fk.get('hanvisningsfraser') or [])
    for c in out:
        t = ' '.join(c['text']); t = re.sub(r'(\w)-\s(?=[a-zåäö])', r'\1', t); t = re.sub(r'\s+', ' ', t).strip()
        k = re.sub(r'\s+', ' ', ' '.join(c['kommentar']))
        c['text'] = t
        c['avsnitt'] = sorted(set(re.findall(r'(\d{1,2}(?:\.\d{1,2}){1,3})', ' '.join(re.findall(r'(?:behandlas i avsnitt|Övervägandena finns i avsnitt|övervägandena finns i avsnitt|behandlas i avsnitten' + FRASER + r')[^.]*(?:\.\d[^.]*)*', k)))))
        c['upphavs'] = bool(re.search(r'upphävs|ska upphöra att gälla', k)) and not t
        c['kommentar'] = k[:400]
    return out

if __name__ == '__main__':
    rid = reform_id(); c = config(rid); s = c['sou']
    vols = kravs(c, 'sou', 'pdf'); sounr = s['nr']
    Pvol = [(v['vol'], text(mapp(rid, 'kallor', 'sou', v['vol'] + '.pdf'), True)) for v in vols]
    P1raw = text(mapp(rid, 'kallor', 'sou', vols[0]['vol'] + '.pdf'), False)
    toc = innehall(Pvol[0][1], kravs(c, 'sou', 'innehall_sidor'), bool(s.get('innehall_kort_utfyllnad')))
    kmin, kmax = kravs(c, 'sou', 'forslagskapitel')
    kapitel = {t['avsnitt']: t['rubrik'] for t in toc if '.' not in t['avsnitt'] and t['avsnitt'].isdigit()}
    avsn = {t['avsnitt']: {'rubrik': t['rubrik'], 'sida': t['sida']} for t in toc if t['avsnitt'].split('.')[0].isdigit() and kmin <= int(t['avsnitt'].split('.')[0]) <= kmax}
    url1 = vols[0]['url']
    skriv(rid, 'sou-innehall.json', {'_meta': {'kalla': {'text': f'{sounr}, innehållsförteckning', 'url': url1}, 'forslagskapitel': [kmin, kmax]},
                                     'lista': toc, 'kapitel': kapitel, 'avsnitt': avsn})
    f = tilldela_avsnitt(rutor(Pvol, sounr, s.get('ruta_rubriker'), bool(s.get('ruta_over_sidbrytning')), bool(s.get('ruta_bindestreck_skydd')),
                           s.get('ruta_slutrader'), s.get('ruta_kant_tolerans', 1)), toc, Pvol)
    skriv(rid, 'sou-forslag.json', {'_meta': {'kalla': {'text': f'{sounr}, förslagsrutor ("Förslag:")', 'url': url1}, 'pdf': {v['vol']: v['url'] for v in vols}}, 'forslag': f})
    fks = kravs(c, 'sou', 'forfattningskommentar')
    if isinstance(fks, list):
        # Flera lagar (config sou.forfattningskommentar som lista, en post per lag i samma ordning som config lagar, t.ex.
        # SOU 2025:26: 12.1 diskrimineringslagen, 12.2 skollagen). Varje paragraf får fältet 'lag' (= postens 'lag', samma
        # namn som lagar[].namn) så att K4/K8 kan hålla isär lagarna. Med en enda lag (dict) är utdata oförändrade.
        p = [dict(x, lag=fk['lag']) for fk in fks for x in paragrafer(P1raw, toc, fk, sounr, s.get('pdf_sidforskjutning', 0))]
        skriv(rid, 'sou-paragrafer.json', {'_meta': {'kalla': {'text': f"{sounr}, författningskommentar {', '.join(fk['avsnitt'] for fk in fks)}", 'url': url1}, 'lag': [fk['lag'] for fk in fks]}, 'paragrafer': p})
    else:
        p = paragrafer(P1raw, toc, fks, sounr, s.get('pdf_sidforskjutning', 0))
        skriv(rid, 'sou-paragrafer.json', {'_meta': {'kalla': {'text': f"{sounr}, författningskommentar {s['forfattningskommentar']['avsnitt']}", 'url': url1}, 'lag': s['forfattningskommentar']['lag']}, 'paragrafer': p})
    print(f'{rid}: innehåll {len(toc)} poster, {len(f)} förslagsrutor, {len(p)} paragrafer')
