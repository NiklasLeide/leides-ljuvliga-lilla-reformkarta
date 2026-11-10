import re,html,json,sys
out={}
for line in open(sys.argv[1]):
    k,u=line.split()
    t=open(f'{sys.argv[2]}/rem_{k}.html',encoding='utf-8').read()
    body=t[t.find('<main'):]
    body=body[:body.find('Genvägar')]
    title=re.sub('<[^>]+>','',html.unescape(re.search(r'<h1[^>]*>(.*?)</h1>',body,re.S).group(1))).strip()
    sec=None; lista=[]; svar=[]
    for m in re.finditer(r'<h[2-4][^>]*>(.*?)</h[2-4]>|href="([^"]*\.(?:pdf|PDF|zip|docx?))"[^>]*>([^<]*)',body,re.S):
        if m.group(1): sec=re.sub('<[^>]+>','',html.unescape(m.group(1))).strip(); continue
        url=m.group(2); url=url if url.startswith('http') else 'https://www.regeringen.se'+url
        name=html.unescape(m.group(3)).strip()
        name=re.sub(r'\s*\((pdf|PDF|docx?)[^)]*\)\s*$','',name).strip()
        (lista if sec and 'Remissinstanser' in sec else svar).append({'namn':name,'url':url,'sektion':sec})
    # datum / svar senast
    txt=re.sub('<[^>]+>',' ',html.unescape(body))
    pub=re.search(r'Publicerad\s+(\d+ \w+ \d{4})',txt)
    sista=re.search(r'(senast[^.]{0,80}\d{4})',txt)
    out[k]={'remiss_url':u,'titel':title,'publicerad':pub.group(1) if pub else None,'sista_svar':sista.group(1) if sista else None,'remisslista_pdf':lista,'remissvar':svar,'sektioner':sorted(set(x['sektion'] or '' for x in svar))}
json.dump(out,open(sys.argv[3],'w'),ensure_ascii=False,indent=1)
for k,v in out.items(): print(k,len(v['remissvar']),v['publicerad'],'|',v['sista_svar'],'|',v['sektioner'],[x['namn'] for x in v['remisslista_pdf']])
