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

def innehall(P, sidor):
    toc = []; buf = ''
    for p in P[sidor[0] - 1:sidor[1]]:
        for l in p.split('\n'):
            s = l.strip()
            if not s: continue
            m = re.match(r'^(\d{1,2}(?:\.\d{1,2}){0,4})\s+(.*)$', s)
            if m: buf = s
            elif buf: buf += ' ' + s
            else: continue
            mm = re.match(r'^(\d{1,2}(?:\.\d{1,2}){0,4})\s+(.*?)\s*\.{3,}\s*(\d{1,4})$', buf)
            if mm: toc.append({'avsnitt': mm.group(1), 'rubrik': re.sub(r'\s+', ' ', mm.group(2)), 'sida': int(mm.group(3))}); buf = ''
    return toc

def printed(p):
    lines = [l.strip() for l in p.strip().split('\n') if l.strip()]
    for l in lines[-1:] + lines[:1]:
        if re.fullmatch(r'\d{1,4}', l): return int(l)
    return None

def rutor(Pvol, sounr):
    hdr = re.compile(r'^\s*' + re.escape(sounr) + r'\s*$')
    out = []
    for vol, P in Pvol:
        sec = None; sectitle = None
        for i, p in enumerate(P):
            lines = p.split('\n')
            for j, l in enumerate(lines):
                m = re.match(r'^\s{0,25}(\d{1,2}(?:\.\d{1,2}){1,4})\s{1,6}([A-ZÅÄÖ].{3,90})$', l)
                if m and not re.search(r'\.{4,}|\s\d+$', l): sec = m.group(1); sectitle = m.group(2).strip()
                mb = re.match(r'^\s*(Förslag|Bedömning):\s*(.*)$', l)
                if mb:
                    ind = len(l) - len(l.lstrip())
                    txt = [mb.group(2).strip()]; k = j + 1; blank = 0; pp = i; LL = lines
                    while True:
                        if k >= len(LL):
                            pp += 1
                            if pp >= len(P): break
                            LL = P[pp].split('\n'); k = 0; continue
                        s = LL[k]
                        if not s.strip():
                            blank += 1
                            if blank >= 1 and len(txt) > 1: break
                            k += 1; continue
                        if re.match(r'^\s*(Förslag|Bedömning):', s): break
                        if hdr.match(s.strip()) or re.match(r'^\s*\d{1,4}\s*$', s): k += 1; continue
                        blank = 0; txt.append(re.sub(r'\s{3,}.*$', '', s.strip()) if ind < 5 else s.strip()); k += 1
                    t = ' '.join(txt); t = re.sub(r'(\w)- (?=[a-zåäö])', r'\1', t)
                    out.append({'vol': vol, 'pdfsida': i + 1, 'sida': printed(p), 'avsnitt': sec, 'avsnittsrubrik': sectitle, 'typ': mb.group(1), 'text': t})
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
            if hp != -1 and (pos == -1 or hp < pos): chosen = t; break
        b['avsnitt'] = chosen['avsnitt'] if chosen else None; b['avsnittsrubrik'] = chosen['rubrik'] if chosen else None
    n = 0; out = []
    for b in boxes:
        if b['typ'] != 'Förslag': continue
        n += 1; out.append(dict(b, id=f'F{n:02d}'))
    return out

def paragrafer(Praw, toc, fk, sounr):
    sid = {t['avsnitt']: t['sida'] for t in toc}
    start, slut = sid[fk['avsnitt']], sid[fk['slut_avsnitt']]
    rubrik_fk = 'Författningskommentar'
    rows = []
    for pg in range(start, slut + 1):
        for l in Praw[pg - 1].split('\n'):
            s = l.strip()
            if s in (sounr, rubrik_fk) or re.fullmatch(r'\d{3}', s): continue
            rows.append((pg, s))
    out = []; kap = None; cur = None; mode = None
    HEAD = re.compile(r'^(\d+(?: [a-z])?) ?§$')
    for pg, s in rows:
        if re.fullmatch(r'\d+(?: [a-z])? kap\.', s): kap = s.replace(' kap.', ''); continue
        if s.startswith('Ikraftträdande och övergångsbestämmelser'):
            cur = {'kap': 'ikraft', 'par': 'övergångsbestämmelser', 'sida': pg, 'text': [], 'kommentar': []}; out.append(cur); mode = 'text'; continue
        if s == fk['slut_avsnitt']: break
        m = HEAD.match(s)
        if m and kap:
            cur = {'kap': kap, 'par': m.group(1), 'sida': pg, 'text': [], 'kommentar': []}; out.append(cur); mode = 'text'; continue
        if cur is None: continue
        if mode == 'text' and re.match(r'^(Paragrafen|Bestämmelsen|Paragrafens|I paragrafen|Ändringen|Första stycket|Andra stycket|Övervägandena)\b', s):
            mode = 'komm'
        (cur['text'] if mode == 'text' else cur['kommentar']).append(s)
    for c in out:
        t = ' '.join(c['text']); t = re.sub(r'(\w)-\s(?=[a-zåäö])', r'\1', t); t = re.sub(r'\s+', ' ', t).strip()
        k = re.sub(r'\s+', ' ', ' '.join(c['kommentar']))
        c['text'] = t
        c['avsnitt'] = sorted(set(re.findall(r'(\d{1,2}(?:\.\d{1,2}){1,3})', ' '.join(re.findall(r'(?:behandlas i avsnitt|Övervägandena finns i avsnitt|övervägandena finns i avsnitt|behandlas i avsnitten)[^.]*(?:\.\d[^.]*)*', k)))))
        c['upphavs'] = bool(re.search(r'upphävs|ska upphöra att gälla', k)) and not t
        c['kommentar'] = k[:400]
    return out

if __name__ == '__main__':
    rid = reform_id(); c = config(rid); s = c['sou']
    vols = kravs(c, 'sou', 'pdf'); sounr = s['nr']
    Pvol = [(v['vol'], text(mapp(rid, 'kallor', 'sou', v['vol'] + '.pdf'), True)) for v in vols]
    P1raw = text(mapp(rid, 'kallor', 'sou', vols[0]['vol'] + '.pdf'), False)
    toc = innehall(Pvol[0][1], kravs(c, 'sou', 'innehall_sidor'))
    kmin, kmax = kravs(c, 'sou', 'forslagskapitel')
    kapitel = {t['avsnitt']: t['rubrik'] for t in toc if '.' not in t['avsnitt'] and t['avsnitt'].isdigit()}
    avsn = {t['avsnitt']: {'rubrik': t['rubrik'], 'sida': t['sida']} for t in toc if t['avsnitt'].split('.')[0].isdigit() and kmin <= int(t['avsnitt'].split('.')[0]) <= kmax}
    url1 = vols[0]['url']
    skriv(rid, 'sou-innehall.json', {'_meta': {'kalla': {'text': f'{sounr}, innehållsförteckning', 'url': url1}, 'forslagskapitel': [kmin, kmax]},
                                     'lista': toc, 'kapitel': kapitel, 'avsnitt': avsn})
    f = tilldela_avsnitt(rutor(Pvol, sounr), toc, Pvol)
    skriv(rid, 'sou-forslag.json', {'_meta': {'kalla': {'text': f'{sounr}, förslagsrutor ("Förslag:")', 'url': url1}, 'pdf': {v['vol']: v['url'] for v in vols}}, 'forslag': f})
    p = paragrafer(P1raw, toc, kravs(c, 'sou', 'forfattningskommentar'), sounr)
    skriv(rid, 'sou-paragrafer.json', {'_meta': {'kalla': {'text': f"{sounr}, författningskommentar {s['forfattningskommentar']['avsnitt']}", 'url': url1}, 'lag': s['forfattningskommentar']['lag']}, 'paragrafer': p})
    print(f'{rid}: innehåll {len(toc)} poster, {len(f)} förslagsrutor, {len(p)} paragrafer')
