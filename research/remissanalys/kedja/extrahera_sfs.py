#!/usr/bin/env python3
"""Steg K4 (deterministiskt, kräver kallor/): konsoliderade författningar (riksdagens öppna data) → sfs.json
  lagar:        per lag paragrafversioner (inkl. framtida lydelser '/Träder i kraft I:…/') i de kapitel som utredningens
                författningskommentar berör (per lag när sou-paragrafer.json har fältet 'lag', dvs. flera lagar), samt övergångsbestämmelserna för ändringslagarna i config lagar[].andringar
  forordningar: per förordning antal träffar på markörerna i config forordning_markor (t.ex. ny betygsbeteckning) och "Ändrad t.o.m."
Förutsättning: sou-paragrafer.json (steg K2). Användning: python3 research/remissanalys/kedja/extrahera_sfs.py <reform-id>"""
import os, re, sys
sys.path.insert(0, os.path.dirname(__file__))
from gemensamt import reform_id, config, mapp, las, skriv, kravs

def versioner(txt):
    L = txt.split('\n')
    end = next((i for i, l in enumerate(L) if l.strip() == 'Övergångsbestämmelser'), len(L)); L = L[:end]
    meta = {'andrad_tom': next((l.split(':', 1)[1].strip() for l in L[:12] if l.startswith('Ändrad:')), None)}
    vers = []; kap = None; cur = None; prev_blank = True
    for l in L:
        s = l.rstrip()
        if not s.strip(): prev_blank = True
        else:
            mk = re.match(r'^(\d+ (?:[a-z] )?kap\.)\s+(\S.*)$', s)
            mp = re.match(r'^(\d+(?: [a-z])?) §(?:\s+/(Träder i kraft I|Upphör att gälla U):(\d{4}-\d{2}-\d{2})/)?\s*(.*)$', s)
            if prev_blank and mk and not s.endswith(('.', ',')) and not re.search(r'§', mk.group(2)):
                kap = mk.group(1).replace(' kap.', '').replace(' ', ''); cur = None
            elif prev_blank and mp and kap:
                cur = {'kap': kap, 'par': mp.group(1).replace(' ', ''), 'ikraft': mp.group(3) if mp.group(2) and mp.group(2).startswith('Träder') else None,
                       'upphor': mp.group(3) if mp.group(2) and mp.group(2).startswith('Upphör') else None, 'rader': [mp.group(4)] if mp.group(4) else []}
                vers.append(cur)
            elif cur is not None: cur['rader'].append(s.strip())
            prev_blank = False
    for v in vers:
        t = re.sub(r'\s+', ' ', ' '.join(v.pop('rader'))).strip()
        m = list(re.finditer(r'(Lag|Förordning) \((\d{4}:\d+)\)\.', t))
        if m: v['lag'] = m[-1].group(2); t = t[:m[-1].start()].strip()
        else: v['lag'] = None
        v['text'] = t
    return meta, vers

def overgang(txt, andringar):
    if not andringar: return []   # lag utan ändringslag (t.ex. diskrimineringslagen för SOU 2025:26: förslaget genomfördes inte)
    t = txt[txt.find('\nÖvergångsbestämmelser'):]; alt = '|'.join(re.escape(a) for a in andringar)
    return [{'kap': 'ikraft', 'par': 'övergångsbestämmelser', 'ikraft': None, 'upphor': None, 'lag': m.group(1), 'text': re.sub(r'\s+', ' ', m.group(2)).strip()}
            for m in re.finditer(r'\n(' + alt + r')\n(.*?)(?=\n\d{4}:\d+\n|\Z)', t, re.S)]

if __name__ == '__main__':
    rid = reform_id(); c = config(rid)
    souparagrafer = las(rid, 'sou-paragrafer.json')['paragrafer']
    lagar = []
    for l in kravs(c, 'lagar'):
        # Kapitlen som författningskommentaren berör. Med flera lagar (config sou.forfattningskommentar som lista) har varje
        # paragraf fältet 'lag' och bara den egna lagens kapitel tas med; med en lag saknas fältet och alla kapitel gäller.
        kaps = {p['kap'] for p in souparagrafer if p['kap'] != 'ikraft' and p.get('lag', l['namn']) == l['namn']}
        txt = open(mapp(rid, 'kallor', 'sfs', l['riksdagen_id'] + '.text'), encoding='utf-8').read()
        meta, vers = versioner(txt)
        lagar.append({'namn': l['namn'], 'riksdagen_id': l['riksdagen_id'], 'url': f"https://data.riksdagen.se/dokument/{l['riksdagen_id']}.text",
                      'andrad_tom': meta['andrad_tom'], 'andringar': l['andringar'],
                      'versioner': [v for v in vers if v['kap'] in kaps], 'overgangsbestammelser': overgang(txt, l['andringar'])})
    markor = c.get('forordning_markor') or []; ford = []
    for f in c.get('forordningar') or []:
        txt = open(mapp(rid, 'kallor', 'sfs', f['riksdagen_id'] + '.text'), encoding='utf-8').read()
        ford.append({'namn': f['namn'], 'riksdagen_id': f['riksdagen_id'], 'url': f"https://data.riksdagen.se/dokument/{f['riksdagen_id']}.text",
                     'andrad_tom': next((x.split(':', 1)[1].strip() for x in txt.split('\n')[:12] if x.startswith('Ändrad:')), None),
                     'markor': {m: txt.count(m) for m in markor}})
    skriv(rid, 'sfs.json', {'_meta': {'hamtningsdatum': c.get('hamtningsdatum'), 'kalla': 'riksdagens öppna data (Källa: Regeringskansliet / Lagrummet)'}, 'lagar': lagar, 'forordningar': ford})
    print(f"{rid}: {sum(len(l['versioner']) for l in lagar)} paragrafversioner, {sum(len(l['overgangsbestammelser']) for l in lagar)} övergångsblock, {len(ford)} förordningar (markörträffar {sum(sum(f['markor'].values()) for f in ford)})")
