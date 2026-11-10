"""Steg 1: hämta publicerade remissvar från fokusgrupperna (pilot betyg), text per sida; OCR för inskannade."""
import json,subprocess,os,re,unicodedata,sys
S=sys.argv[1]; OUT=sys.argv[2]
p=json.load(open('research/remissanalys/pilot-betyg.json'))
rem=json.load(open(f'{S}/rem.json'))['betyg']['remissvar']
def key(s): return re.sub(r's? kommun$',' kommun',unicodedata.normalize('NFC',s).lower().replace('.pdf','').strip())
webb={key(x['namn']):x['url'] for x in rem}
korpus=[]; saknade=[]
for a in p['remissvar_fokusgrupper']:
    url=a['url'] or webb.get(key(a['namn']))
    if not url:
        saknade.append({'namn':a['namn'],'kategori':a['kategori'],'typ':a['typ'],'skal':a.get('url_anm')}); continue
    did=re.sub(r'[^a-z0-9]+','-',unicodedata.normalize('NFKD',a['namn'].lower()).encode('ascii','ignore').decode()).strip('-')
    pdf=f'{S}/korpus/{did}.pdf'
    if not os.path.exists(pdf): subprocess.run(['curl','-s','-L','--max-time','90','-o',pdf,url],check=True)
    n=int(re.search(r'Pages:\s+(\d+)',subprocess.run(['pdfinfo',pdf],capture_output=True,text=True).stdout).group(1))
    pages=[]; ocr=False
    for i in range(1,n+1):
        t=subprocess.run(['pdftotext','-f',str(i),'-l',str(i),pdf,'-'],capture_output=True,text=True).stdout
        pages.append(t)
    if sum(len(x.strip()) for x in pages) < 50*n:   # inskannad: OCR
        ocr=True; pages=[]
        for i in range(1,n+1):
            img=f'{S}/korpus/{did}-{i}'
            subprocess.run(['pdftoppm','-r','300','-f',str(i),'-l',str(i),'-png','-singlefile',pdf,img],check=True)
            t=subprocess.run(['tesseract',img+'.png','-','-l','swe'],capture_output=True,text=True).stdout
            pages.append(t)
    korpus.append({'id':did,'avsandare':a['namn'],'kategori':a['kategori'],'typ':a['typ'],'url':url,'url_kalla':'pilot-betyg.json' if a['url'] else 'regeringen.se-remissidan (namnvariant "%s")'%next(x['namn'] for x in rem if x['url']==url),'sidor':n,'ocr':ocr,'text_per_sida':pages})
    print(did,n,'OCR' if ocr else '',sum(len(x) for x in pages))
json.dump({'korpus':korpus,'saknade':saknade},open(OUT,'w'),ensure_ascii=False,indent=1)
print('dokument',len(korpus),'saknade',len(saknade))
