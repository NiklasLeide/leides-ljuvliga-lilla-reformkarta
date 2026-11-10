#!/usr/bin/env python3
"""Kör kedjans deterministiska steg från repot (inga nätverksanrop, inga filer utanför repot) för en reform:
  K6 segmentera → K7 utmaningar → K8 sfs_diff → K9 avvikelser → K10 bygg
Förutsättning: källstegens utdata (K2–K5) och modellkodningen (M1–M3, R1) är incheckade under research/remissanalys/reformer/<id>/.
Stoppar vid första fel. Valideringen (K11–K12) körs separat, se KEDJA.md.
Användning: python3 research/remissanalys/kedja/kor.py <reform-id>"""
import os, subprocess, sys
sys.path.insert(0, os.path.dirname(__file__))
from gemensamt import reform_id

STEG = ['segmentera.py', 'utmaningar.py', 'sfs_diff.py', 'avvikelser.py', 'bygg.py']
if __name__ == '__main__':
    rid = reform_id()
    for s in STEG:
        print(f'== {s} {rid}', flush=True)
        r = subprocess.run([sys.executable, os.path.join(os.path.dirname(__file__), s), rid])
        if r.returncode: sys.exit(f'{s} misslyckades (kod {r.returncode}); kedjan stoppad.')
