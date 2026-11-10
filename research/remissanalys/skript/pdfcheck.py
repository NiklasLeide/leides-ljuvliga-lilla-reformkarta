import json,subprocess,os,sys
d=json.load(open('rem.json')); out={}
tmp='dl/tmp.pdf'
for k,v in d.items():
    for x in v['remissvar']:
        r=subprocess.run(['curl','-s','-L','--max-time','60','-o',tmp,x['url']])
        try:
            info=subprocess.run(['pdfinfo',tmp],capture_output=True,text=True).stdout
            pages=int([l for l in info.split('\n') if l.startswith('Pages:')][0].split()[1])
            txt=subprocess.run(['pdftotext',tmp,'-'],capture_output=True,text=True).stdout
            fonts=subprocess.run(['pdffonts',tmp],capture_output=True,text=True).stdout.count('\n')-2
            chars=len(txt.strip())
            typ='text' if chars/pages>200 else ('inskannad' if fonts<=0 else 'oklar')
            out[x['url']]={'reform':k,'namn':x['namn'],'sidor':pages,'tecken':chars,'fonter':fonts,'typ':typ,'avstar':('avstår' in txt.lower() or 'inga synpunkter' in txt.lower() or 'inte några synpunkter' in txt.lower()) and chars<2500,'utdrag':txt.strip()[:400]}
        except Exception as e:
            out[x['url']]={'reform':k,'namn':x['namn'],'fel':str(e)}
        if os.path.exists(tmp): os.remove(tmp)
json.dump(out,open('pdfcheck.json','w'),ensure_ascii=False,indent=1)
print('klart',len(out))
