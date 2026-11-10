#!/usr/bin/env python3
"""Steg K5 (deterministiskt; hämtar remissvarens PDF:er om de saknas i kallor/): remissvar.json
  forteckning:  propositionens förteckning över remissinstanserna (svarat / spontant / avstått), ordagrant uppdelad
  publicerade:  fokusgruppernas remissvar som finns på remissidan, med text per sida (pdftotext; OCR med tesseract för inskannade)
  opublicerade: fokusgruppernas remissvar som enligt förteckningen finns men inte är publicerade (spontana yttranden)
Konfiguration: propositioner[].forteckning_remissinstanser_sida / forteckning_bilaga, forteckning_korrigeringar.
Förutsättning: kallor/remisssida.html och kallor/prop/<kort>.pdf (steg K1). Användning: python3 research/remissanalys/kedja/extrahera_remissvar.py <reform-id>"""
import html, os, re, subprocess, sys, unicodedata
sys.path.insert(0, os.path.dirname(__file__))
from gemensamt import reform_id, config, gemensamt, mapp, skriv, kravs, kategori, GRUPP, N, slug

def clean(s):
    s = re.sub(r'Prop\. \d{4}/\d{2}:\d+\s*', '', s); s = re.sub(r'Bilaga \d+\s*', '', s); s = re.sub(r'\n\s*\d{1,3}\s*\n', '\n', s)
    s = re.sub(r'\s+', ' ', s)
    s = re.sub(r'(\w)-(?!och\b|eller\b|samt\b)(?=[a-zåäö])', r'\1', s); s = re.sub(r'(\w)-(och|eller) ', r'\1- \2 ', s)
    s = re.sub(r'(\w)- (?!och |eller |samt )(?=[a-zåäö])', r'\1', s)
    return s.strip()

def dela(s):
    s = s.strip().rstrip('.'); parts = [p.strip() for p in re.split(r',\s*(?![^()]*\))', s)]; out = []
    for i, p in enumerate(parts):
        p = re.sub(r'^(samt|och)\s+', '', p)
        m = re.match(r'(.+?[^-])\s+(samt|och)\s+([A-ZÅÄÖ].*)$', p)
        if m and (i == len(parts) - 1 or m.group(2) == 'samt'): out += [m.group(1), m.group(3)]
        else: out.append(p)
    return [o for o in out if o]

def forteckning(raw_pages, pg, korr):
    txt = ''; pmap = []
    for i in range(pg - 1, pg + 3):
        p = raw_pages[i]
        if i > pg - 1 and ('Förteckning över remissinstanserna' in p or 'Lagrådsremissens' in p or 'Lagrådets yttrande' in p or 'Sammanfattning' in p[:300]):
            cut = min([p.find(h) for h in ['Förteckning över remissinstanserna', 'Lagrådsremissens', 'Lagrådets', 'Sammanfattning'] if p.find(h) >= 0])
            txt += p[:cut]; pmap.append(i + 1); break
        txt += p + '\n'; pmap.append(i + 1)
    body = clean(txt[txt.find('Efter remiss har yttranden'):])
    for pn in pmap: body = re.sub(r'\s%d\s' % pn, ' ', body)
    MARK = [('svarat', r'Efter remiss har yttranden kommit in från'),
            ('spontant', r'(?:Därutöver|Dessutom) har (?:spontana )?yttranden (?:inkommit|lämnats|kommit in) från|Spontana yttranden har därutöver inkommit från'),
            ('privatpersoner', r'[A-ZÅÄÖ][a-zåäö]+ spontana yttranden har inkommit från privatpersoner'),
            ('ej_svarat', r'Följande remissinstanser har [^:]*:')]
    hits = sorted((m.start(), m.end(), n) for n, rx in MARK for m in re.finditer(rx, body))
    g = {'svarat': [], 'spontant': [], 'ej_svarat': [], 'privatpersoner': None, 'pdfsidor': pmap}
    for i, (st, en, n) in enumerate(hits):
        seg_end = hits[i + 1][0] if i + 1 < len(hits) else len(body)
        g[n + '_text'] = body[st:seg_end].strip()
        if n == 'privatpersoner': g[n] = body[st:seg_end].strip(); continue
        g[n] = [x for nm in dela(body[en:seg_end].strip()) for x in korr.get(nm, [nm])]
    return g

def remissida(htmltext):
    body = htmltext[htmltext.find('<main'):]; body = body[:body.find('Genvägar')]
    sec = None; svar = []
    for m in re.finditer(r'<h[2-4][^>]*>(.*?)</h[2-4]>|href="([^"]*\.(?:pdf|PDF|zip|docx?))"[^>]*>([^<]*)', body, re.S):
        if m.group(1): sec = re.sub('<[^>]+>', '', html.unescape(m.group(1))).strip(); continue
        url = m.group(2); url = url if url.startswith('http') else 'https://www.regeringen.se' + url
        namn = re.sub(r'\s*\((pdf|PDF|docx?)[^)]*\)\s*$', '', html.unescape(m.group(3)).strip()).strip()
        if not (sec and 'Remissinstanser' in sec) and not re.match(r'Remiss(miss)?instanser', namn): svar.append({'namn': namn, 'url': url})
    return svar

def nyckel(s):   # som förstudie 1/2: skiftläge, .pdf, "Kristianstad kommun" ~ "Kristianstads kommun", "Göteborg kommun" ~ "Göteborgs kommun"
    k = re.sub(r'\s+', ' ', N(s).lower().replace('–', '-')).strip(' .'); k = re.sub(r'\.pdf$', '', k)
    return re.sub(r's? kommun$', ' kommun', k)

def sidtext(pdf, rid, did):
    n = int(re.search(r'Pages:\s+(\d+)', subprocess.run(['pdfinfo', pdf], capture_output=True, text=True).stdout).group(1))
    pages = [subprocess.run(['pdftotext', '-f', str(i), '-l', str(i), pdf, '-'], capture_output=True, text=True).stdout for i in range(1, n + 1)]
    ocr = False
    if sum(len(x.strip()) for x in pages) < 50 * n:   # inskannad: OCR
        ocr = True; pages = []
        for i in range(1, n + 1):
            img = mapp(rid, 'kallor', 'ocr', f'{did}-{i}')
            subprocess.run(['pdftoppm', '-r', '300', '-f', str(i), '-l', str(i), '-png', '-singlefile', pdf, img], check=True)
            pages.append(subprocess.run(['tesseract', img + '.png', '-', '-l', 'swe'], capture_output=True, text=True).stdout)
    return n, ocr, pages

if __name__ == '__main__':
    rid = reform_id(); c = config(rid); g0 = gemensamt()
    huvud = next(p for p in kravs(c, 'propositioner') if p.get('forteckning_remissinstanser_sida'))
    rawp = mapp(rid, 'kallor', 'prop', huvud['kort'] + '-r.txt')
    if not os.path.exists(rawp): subprocess.run(['pdftotext', mapp(rid, 'kallor', 'prop', huvud['kort'] + '.pdf'), rawp], check=True)
    f = forteckning(open(rawp, encoding='utf-8').read().split('\f'), huvud['forteckning_remissinstanser_sida'], c.get('forteckning_korrigeringar') or {})
    webb = {nyckel(x['namn']): x['url'] for x in remissida(open(mapp(rid, 'kallor', 'remisssida.html'), encoding='utf-8').read())}
    kalla_f = {'text': f"{huvud['nr']} bilaga {huvud['forteckning_bilaga']} (förteckning över remissinstanserna)", 'url': huvud['pdf_url']}
    publ = []; opubl = []
    for grp, typ in (('svarat', 'remissinstans'), ('spontant', 'spontant')):
        for namn in f[grp]:
            namn = N(namn)
            if namn == 'privatpersoner' or 'privatperson' in namn: continue
            kat = kategori(namn, g0)
            if kat not in GRUPP: continue
            url = webb.get(nyckel(namn))
            if not url:
                opubl.append({'avsandare': namn, 'fokusgrupp': kat, 'grupp': GRUPP[kat], 'svarat_som': 'spontant yttrande' if typ == 'spontant' else 'remissinstans',
                              'skal': 'Spontana yttranden publiceras inte på regeringen.se ("Övriga yttranden finns tillgängliga i departementet"); inte inhämtade enligt spikens avgränsning.' if typ == 'spontant'
                                      else 'Remissvaret hittades inte på remissidan.', 'kalla': kalla_f}); continue
            did = slug(namn); pdf = mapp(rid, 'kallor', 'remissvar', did + '.pdf')
            if not os.path.exists(pdf): subprocess.run(['curl', '-s', '-L', '--fail', '--max-time', '90', '-o', pdf, url], check=True)
            n, ocr, pages = sidtext(pdf, rid, did)
            publ.append({'id': did, 'avsandare': namn, 'kategori': kat, 'typ': typ, 'url': url, 'sidor': n, 'ocr': ocr, 'text_per_sida': pages})
            print(f'  {did}: {n} s.' + (' OCR' if ocr else ''))
    skriv(rid, 'remissvar.json', {'_meta': {'kalla_forteckning': kalla_f, 'kalla_remissida': {'text': f"Remiss {c['remiss']['diarienummer']} på regeringen.se", 'url': c['remiss']['url']}},
                                  'forteckning': f, 'publicerade': publ, 'opublicerade': opubl})
    print(f'{rid}: {len(publ)} publicerade, {len(opubl)} opublicerade remissvar från fokusgrupperna')
