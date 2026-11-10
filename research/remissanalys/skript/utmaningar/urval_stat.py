"""Steg 6 (granskningsurval, 25 slumpade kategoriserade passager, seed 20261110) + statistik till rapporten."""
import json,random,collections,sys
S=sys.argv[1]; OUTMD=sys.argv[2]
d=json.load(open(f'{S}/utmaningar-betyg.json')); sd=json.load(open(f'{S}/sfs-diff-betyg.json'))
KN={k['id']:k['namn'] for k in d['kategorier']}
uu=[u for u in d['utmaningar'] if not u['dublett_av']]
rng=random.Random(20261110); urval=sorted(rng.sample(uu,25),key=lambda u:u['id'])
L=['# Granskningsurval — utmaningar, betyg','',
   'Slumpmässigt urval av 25 kategoriserade passager (Python `random.Random(20261110).sample`, bland de 440 utmaningar som inte är dubbletter). Fyll i kolumnen **Omdöme** (t.ex. rätt/fel kategori, rätt/fel koppling, inte en utmaning).','',
   '| # | Id | Avsändare | Sida | Citat | Kategori | Koppling | Omdöme |','|---|---|---|---|---|---|---|---|']
for i,u in enumerate(urval,1):
    k=u['koppling']; ks=f"{k['typ'] or 'ingen'}: {', '.join(k['forslag'])}" if k['forslag'] else (k['typ'] or 'ingen')
    cit=u['citat'].replace('|','\\|').replace('\n',' ')
    L.append(f"| {i} | {u['id']} | {u['avsandare']} | [{u['sida']}]({u['url']}) | {cit} | {KN[u['kategori']]} | {ks} |  |")
open(OUTMD,'w').write('\n'.join(L)+'\n')
C=collections.Counter
st={'antal':len(d['utmaningar']),'ej_dubblett':len(uu),'per_kategori':dict(C(u['kategori'] for u in uu)),'per_grupp':dict(C(u['fokusgrupp'] for u in uu)),
 'kategori_x_grupp':{k:dict(C(u['fokusgrupp'] for u in uu if u['kategori']==k)) for k in KN},
 'koppling':dict(C(u['koppling']['typ'] or 'null' for u in uu)),
 'bemott':dict(C(str(u['bemotande']['bemott_namngiven']) for u in uu)),
 'citat':dict(C(u['citatkontroll']['metod'] for u in d['utmaningar'])),
 'avsandare_med_utmaning':len({u['avsandare'] for u in uu}),'avsandare_per_grupp':{g:len({u['avsandare'] for u in uu if u['fokusgrupp']==g}) for g in ('kommuner','skr','almega','ideburna')}}
uniq={}
for f in sd['forslag']:
    for p in f['paragrafer']: uniq[p['paragraf']]=p
st['sfs']={'forslag':len(sd['forslag']),'status_forslag':dict(C(f['status'] for f in sd['forslag'])),'unika_paragrafer':len(uniq),
  'status_unika_paragrafer':dict(C(p['status'] for p in uniq.values())),
  'auto_sfs':sum(1 for p in uniq.values() if p.get('beslutad') and p['beslutad']['matchning']=='nummer' and p['beslutad']['likhet_mot_sou']>=0.8),
  'auto_prop':sum(1 for p in uniq.values() if p.get('proposition') and p['proposition']['matchning']=='nummer' and p['proposition']['likhet_mot_sou']>=0.8),
  'auto_bada':sum(1 for p in uniq.values() if not p['manuell_granskning'] and (p.get('beslutad') or {}).get('matchning')=='nummer' and (p.get('proposition') or {}).get('matchning')=='nummer'),
  'manuell':sum(1 for p in uniq.values() if p['manuell_granskning']),'prop_saknas':sum(1 for p in uniq.values() if not p.get('proposition')),
  'textmatch_sfs':sum(1 for p in uniq.values() if (p.get('beslutad') or {}).get('matchning')=='textlikhet')}
# andel utmaningar per kategori som rör lagtextförslag med status
FS={f['forslag']:f['status'] for f in sd['forslag']}
st['utmaningar_per_sfsstatus']=dict(C(tuple(sorted({FS[f] for f in u['koppling']['forslag']})) and '/'.join(sorted({FS[f] for f in u['koppling']['forslag']})) or 'ingen koppling' for u in uu))
json.dump(st,open(f'{S}/stat.json','w'),ensure_ascii=False,indent=1)
print(json.dumps(st,ensure_ascii=False,indent=1))
