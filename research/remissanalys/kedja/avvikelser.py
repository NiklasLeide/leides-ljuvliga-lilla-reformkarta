#!/usr/bin/env python3
"""Steg K9 (deterministiskt): avvikelser.json — propositionens stycke om utredningens förslag per propositionsavsnitt, ordagrant,
med propositionens exakta fras om överensstämmelse ("stämmer [i huvudsak/delvis] överens") och om stycket beskriver avvikelser
(mekaniskt: fler meningar än den inledande). Kontrollen mot PDF-texten görs i K3 (prop-avsnitt.json) och följer med.
Konfiguration: propositioner[].utredningens_forslag_rubrik. Förutsättning: prop-avsnitt.json (K3), forslag-propositionsavsnitt.json (R1).
Användning: python3 research/remissanalys/kedja/avvikelser.py <reform-id>"""
import collections, os, re, sys
sys.path.insert(0, os.path.dirname(__file__))
from gemensamt import reform_id, config, las, skriv, kravs

if __name__ == '__main__':
    rid = reform_id(); c = config(rid)
    PA = las(rid, 'prop-avsnitt.json')['propositioner']
    F_PER_AVS = {}
    for f in las(rid, 'forslag-propositionsavsnitt.json')['forslag']:
        for r in f['propositionsavsnitt']: F_PER_AVS.setdefault(r, []).append(f['id'])
    out = []
    for pk in kravs(c, 'propositioner'):
        kort = pk['kort']; pr = PA[kort]; labels = pk['utredningens_forslag_rubrik']
        for s in pr['avsnitt']:
            # Vid valda avsnitt (inte 'alla') tas bara avsnitt med stycket om utredningens förslag med.
            if pk['avsnitt'] != 'alla' and not any(l in s['delar'] for l in labels): continue
            lab = next((l for l in labels if l in s['delar']), None)
            post = {'proposition': pr['proposition'], 'avsnitt': s['avsnitt'], 'rubrik': s['rubrik'], 'forslag_i_avsnittet': F_PER_AVS.get(f"{kort}:{s['avsnitt']}", [])}
            if not lab:
                post.update(text=None, overensstammelse=None, avvikelse_beskriven=None, kalla=None, anm='Stycket saknas i avsnittet.'); out.append(post); continue
            d = s['delar'][lab]; t = d['text']
            m = re.search(r'stämmer (?:också )?(?:i huvudsak |delvis )?överens', t)
            first = re.match(r'(.+?\.)(\s|$)', t)
            if not m and first:
                # Sprint 17 A3: propositionens formulering som den står, utan krav på ordföljd, i första meningen:
                # verbet (över)ensstämmer/stämmer och eventuella bestämningar fram till "överens" eller "med"
                # (t.ex. "Överensstämmer i huvudsak", "stämmer inte överens", "överensstämmer i sak").
                m = re.search(r'\b(?:[Öö]verensstämmer|[Ss]tämmer)\b(?:\s+(?!med\b)[\wåäöÅÄÖ]+){0,4}?(?:\s+överens\b|(?=\s+med\b))', first.group(1))
            rest = t[first.end():].strip() if first else ''
            post.update(rubrik_i_propositionen=lab, text=t, overensstammelse=m.group(0) if m else None, avvikelse_beskriven=bool(rest),
                        kalla={'text': f"{pr['proposition']} s. {', '.join(map(str, d['sidor']))}, avsnitt {s['avsnitt']} ”{lab}”", 'url': pr['url']}, sida=d['sidor'], kontroll=d['kontroll'])
            out.append(post)
    rub = ' (' + '; '.join(f"prop. {p['kort']}: \"{p['utredningens_forslag_rubrik'][0]}\"" for p in c['propositioner'][1:]) + ')' if len(c['propositioner']) > 1 else ''
    skriv(rid, 'avvikelser.json', {'_meta': {'beskrivning': f'Propositionens stycke "{c["propositioner"][0]["utredningens_forslag_rubrik"][0]}"{rub} per avsnitt med regeringens förslags-/bedömningsruta, ordagrant fram till nästa underrubrik.',
                                            'overensstammelse': 'propositionens exakta fras (verbet stämmer/överensstämmer med bestämningar, som det står)', 'avvikelse_beskriven': 'true om stycket innehåller fler meningar än den inledande om överensstämmelse (mekaniskt)'}, 'avsnitt': out})
    print(f"{rid}: {len(out)} avsnitt, stycke saknas i {sum(1 for o in out if not o['text'])}; {dict(collections.Counter(o['overensstammelse'] for o in out))}; kontroll ej hela: {[o['avsnitt'] for o in out if o.get('kontroll') and not o['kontroll']['hela_stycket']]}")
