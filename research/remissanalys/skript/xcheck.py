import json,re
r=json.load(open('rem.json')); b=json.load(open('bilagor.json'))
def norm(s): 
    s=s.lower().replace('–','-'); s=re.sub(r'\s+',' ',s); s=s.replace('göteborg kommun','göteborgs kommun')
    return s.strip(' .')
for k in r:
    L={norm(x) for x in r[k]['remisslista']}
    S={norm(x) for x in b[k]['svarat']}; E={norm(x) for x in (b[k]['ej_svarat'] or [])}; P={norm(x) for x in (b[k]['spontant'] or [])}
    W={norm(x['namn']) for x in r[k]['remissvar']}
    print('=====',k,'lista',len(L),'svarat',len(S),'ej',len(E),'spontant',len(P),'webb',len(W))
    print(' lista - (svarat|ej):',sorted(L-(S|E)))
    print(' (svarat|ej) - lista:',sorted((S|E)-L))
    print(' webb - svarat:',sorted(W-S))
    print(' svarat - webb:',sorted(S-W))
