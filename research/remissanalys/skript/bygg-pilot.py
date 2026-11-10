#!/usr/bin/env python3
"""Bygger pilot/utmaningar/data/utmaningar-betyg.json (Utmaningskartan, pilot betyg).

Sedan Sprint 17 T1 är detta ett tunt omslag kring den parametriska kedjan, som kör de deterministiska stegen
K6–K10 för betyg:
    python3 research/remissanalys/kedja/kor.py betyg
Alla indata ligger incheckade under research/remissanalys/reformer/betyg/ (se research/remissanalys/KEDJA.md).
Sprint 16-versionen, som läste v2/, pilot-betyg.json, sfs-diff-betyg.json och arbetsfiler/, finns i git-historiken.
Utdatan är byte för byte densamma (regressionstestat i Sprint 17 T1). Datafilens meta.byggd_av pekar fortfarande hit.

Körs från repo-roten:  python3 research/remissanalys/skript/bygg-pilot.py"""
import os, subprocess, sys

KOR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'kedja', 'kor.py')
sys.exit(subprocess.run([sys.executable, KOR, 'betyg']).returncode)
