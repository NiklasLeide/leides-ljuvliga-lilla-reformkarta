#!/usr/bin/env python3
"""Steg K1 (källsteg, kräver nät): hämtar källorna för en reform till reformer/<id>/kallor/ (cache, checkas inte in).
  sou/<vol>.pdf            utredningsbetänkandets PDF:er (config sou.pdf)
  prop/<kort>.pdf          propositionernas PDF:er (config propositioner[].pdf_url)
  remisssida.html          remissidan på regeringen.se (config remiss.url)
  sfs/<riksdagen_id>.text  konsoliderade författningar från riksdagens öppna data (config lagar, forordningar)
Remissvarens PDF:er hämtas av extrahera_remissvar.py (listan beror på propositionens remissförteckning).
Befintliga filer hämtas inte om. Användning: python3 research/remissanalys/kedja/hamta.py <reform-id> [--om]"""
import os, subprocess, sys
sys.path.insert(0, os.path.dirname(__file__))
from gemensamt import reform_id, config, mapp, kravs

def hamta(url, mal, om=False):
    if os.path.exists(mal) and os.path.getsize(mal) > 0 and not om:
        print('  finns:', os.path.relpath(mal)); return
    os.makedirs(os.path.dirname(mal), exist_ok=True)
    subprocess.run(['curl', '-s', '-L', '--fail', '--max-time', '180', '-o', mal, url], check=True)
    print('  hämtad:', os.path.relpath(mal), os.path.getsize(mal), 'byte')

if __name__ == '__main__':
    rid = reform_id(); c = config(rid); om = '--om' in sys.argv
    for p in kravs(c, 'sou', 'pdf'): hamta(p['url'], mapp(rid, 'kallor', 'sou', p['vol'] + '.pdf'), om)
    for p in kravs(c, 'propositioner'): hamta(kravs(p, 'pdf_url'), mapp(rid, 'kallor', 'prop', p['kort'] + '.pdf'), om)
    hamta(kravs(c, 'remiss', 'url'), mapp(rid, 'kallor', 'remisssida.html'), om)
    for l in (kravs(c, 'lagar') + (c.get('forordningar') or [])):
        hamta(f"https://data.riksdagen.se/dokument/{l['riksdagen_id']}.text", mapp(rid, 'kallor', 'sfs', l['riksdagen_id'] + '.text'), om)
