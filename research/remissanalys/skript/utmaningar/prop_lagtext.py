"""Propositionens lagförslag (kap. 2 Lagtext): föreslagen lydelse per paragraf ur tvåspaltig layout via ordkoordinater (pdftotext -bbox)."""
import re,json,sys,subprocess,html
S,pdf,first,last,out,propnr=sys.argv[1],sys.argv[2],int(sys.argv[3]),int(sys.argv[4]),sys.argv[5],sys.argv[6]
bb=subprocess.run(['pdftotext','-bbox','-f',str(first),'-l',str(last),pdf,'-'],capture_output=True,text=True).stdout
pages=bb.split('<page ')[1:]
pend=[]
lagforslag=[]; cur_lf=None; kap=None; par=None; state='full'
def flush_line(words,rc,lm):
    """Returnerar ('full'|'two'|'left'|'right', vänstertext, högertext)."""
    ws=sorted(words)
    right=[w for w in ws if w[0]>=rc-1.5]; left=[w for w in ws if w[0]<rc-1.5]
    if not right: return 'left',' '.join(w[2] for w in left),''
    if not left: return 'right','',' '.join(w[2] for w in right)
    gap=right[0][0]-max(w[1] for w in left)
    if gap>=7: return 'two',' '.join(w[2] for w in left),' '.join(w[2] for w in right)
    return 'full',' '.join(w[2] for w in ws),' '.join(w[2] for w in ws)
for pi,pg in enumerate(pages):
    pno=first+pi
    words=[(float(a),float(c),html.unescape(t),float(b)) for a,b,c,t in re.findall(r'xMin="([\d.]+)" yMin="([\d.]+)" xMax="([\d.]+)" yMax="[\d.]+">([^<]*)<',pg)]
    body=[w for w in words if 30<w[3]<640 and not re.fullmatch(r'Prop\.|20\d\d/\d\d:\d+',w[2])]
    if not body: continue
    # vänstermarginal = vanligaste x för radens första ord (marginaltexten 'Prop. …' ligger längre ut och ignoreras)
    from collections import Counter
    firsts={}
    for x,x2,t,y in body: firsts.setdefault(round(y),[]).append(x)
    lm=Counter(round(min(v)) for v in firsts.values()).most_common(1)[0][0]
    allbody=body
    body=[w for w in body if w[0]>=lm-3 or w[2].startswith('2.')]
    rc=lm+154.0
    lines={}
    for x,x2,t,y in body: lines.setdefault(round(y),[]).append((x,x2,t))
    for y in sorted(lines):
        ws=lines[y]; txt=' '.join(w[2] for w in sorted(ws)).strip()
        if re.match(r'^(Prop\. 20\d\d/\d\d:\d+)$',txt) or re.fullmatch(r'\d{1,3}',txt): continue
        m=re.match(r'^2\.(\d)\s+Förslag till lag om ändring i (.*)$',txt)
        if m: cur_lf={'lagforslag':'2.'+m.group(1),'titel':'Förslag till lag om ändring i '+m.group(2),'paragrafer':[]}; lagforslag.append(cur_lf); continue
        if cur_lf is None: continue
        if re.match(r'^(Nuvarande lydelse|Lydelse enligt .*?) Föreslagen lydelse$',txt): state='two'; continue
        mk=re.fullmatch(r'(\d+ (?:[a-z] )?)kap\.',txt)
        if mk: kap=mk.group(1).replace(' ',''); continue
        mp=re.fullmatch(r'(\d+(?: [a-z])?) §(?:\s*\d{1,3})?',txt) or re.fullmatch(r'(\d+(?: [a-z])?) §',txt)
        if mp and kap:
            if pend and par is not None:
                (par['nuvarande'].extend(pend) if len(pend)>=2 or state=='two' else (par['foreslagen'].extend(pend),par['nuvarande'].extend(pend)))
            pend.clear(); state='full'
            par={'kap':kap,'par':mp.group(1).replace(' ',''),'sida':pno,'foreslagen':[],'nuvarande':[]}; cur_lf['paragrafer'].append(par); continue
        if re.match(r'^(1\. )?(Denna lag|Lagen) träder i kraft',txt) and cur_lf is not None:
            if pend and par is not None:
                (par['nuvarande'].extend(pend) if len(pend)>=2 or state=='two' else (par['foreslagen'].extend(pend),par['nuvarande'].extend(pend)))
            pend.clear(); state='full'
            par={'kap':'ikraft','par':'övergångsbestämmelser','sida':pno,'foreslagen':[],'nuvarande':[]}; cur_lf['paragrafer'].append(par)
        if par is None: continue
        if re.match(r'^\d{1,3}\s+Senaste lydelse',txt) or txt.startswith(('Senaste lydelse','Ändringen innebär')): continue
        kind,lt,rt=flush_line(ws,rc,lm)
        # vänster-endast rader buffras: en följd av >=2 sådana rader måste vara vänsterspalt (nuvarande lydelse),
        # eftersom ett helbrett stycke bara har en kort (sista) rad
        if kind=='left':
            pend.append(lt); continue
        if pend:
            if len(pend)>=2 or state=='two': par['nuvarande'].extend(pend)
            else: par['foreslagen'].extend(pend); par['nuvarande'].extend(pend)
            pend.clear()
        if kind=='full':
            state='full'; par['foreslagen'].append(rt); par['nuvarande'].append(rt)
        elif kind=='two': state='two'; par['nuvarande'].append(lt); par['foreslagen'].append(rt)
        elif kind=='right': par['foreslagen'].append(rt)
def clean(a):
    t=' '.join(a); t=re.sub(r'(\w)- (?=[a-zåäö])',r'\1',t); return re.sub(r'\s+',' ',t).strip()
for lf in lagforslag:
    for p in lf['paragrafer']:
        p['foreslagen']=clean(p['foreslagen']); p['nuvarande']=clean(p['nuvarande'])
json.dump({'proposition':propnr,'lagforslag':lagforslag},open(out,'w'),ensure_ascii=False,indent=1)
for lf in lagforslag: print(lf['lagforslag'],lf['titel'][:50],len(lf['paragrafer']))
