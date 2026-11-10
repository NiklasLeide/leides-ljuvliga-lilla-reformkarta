"""Steg 3b: kategorier (axial kodning) från öppna koder. Mappningen öppen kod -> kategori är TOLKNING (görs av människa/modell,
här uttryckt som ordnade nyckelordsregler som går att granska)."""
import re
KATEGORIER=[
 ('komvux','Komvux','Utmaningar som huvudmannen pekar ut för kommunal vuxenutbildning: provtillfällen, flexibilitet, utbud, elevflöden och komvux uppdrag.',
   r'komvux|vuxen'),
 ('samrad_sma_enheter','Bedömningssamråd och små enheter','Utmaningar med att organisera bedömningssamråd och kalibrering där skolenheter, program eller ämneslärargrupper är små.',
   r'samråd|samsyn|små skolor|små program|få elever|ensamlärare|sambedömning|lärarsamverkan|lärandegemenskap|bedömningsråd'),
 ('kostnad_finansiering','Kostnader och finansiering','Utmaningar som gäller kostnader för huvudmannen, finansiering, statsbidrag och resurser för genomförandet.',
   r'kostnad|kostsam|finansier|statsbidrag|anslag|utjämning|ekonom|resurs|besparing|investering'),
 ('tidplan_reformtakt','Tidplan och reformtakt','Utmaningar som gäller ikraftträdande, tid för införandet eller samtidighet och samordning med andra reformer och utredningar.',
   r'tid för införande|tidplan|tidsplan|snabbt införande|reform|synk|parallella|upprepad omställning|överlapp|motstridig|helhet mellan|implementeringstid|i god tid|i tid\b|före införande|gy25'),
 ('prov_system','Provgenomförande och system','Utmaningar med att genomföra nationella slutprov och med de tekniska och administrativa system som krävs (provplattform, IT, lokaler, rättning, antagningssystem).',
   r'prov|plattform|it-|system|teknisk|rättning|lokaler|antagningssystem|avidentifiering|fusk|logistik|omräkningsverktyg|analysverktyg|datorer'),
 ('personal_kompetens','Personal, arbetsbelastning och kompetens','Utmaningar som gäller lärares och annan personals tid, arbetsbelastning, kompetensutveckling och kompetensförsörjning.',
   r'lärar|arbetsbörda|arbetsbelastning|kompetens|fortbildning|syv|personal|administrat|dokumentation|tjänstefördelning'),
 ('otydlighet_kommunikation','Otydlighet och kommunikation','Utmaningar som beror på otydliga regler, modeller eller ansvar, eller på behovet att förklara och informera om systemet och få stöd i god tid.',
   r'oklar|otydlig|förklara|kommunic|informat|informera|stödmaterial|stöd|vägledning|komplex|svårbegrip|insyn|riktlinjer|föreskrifter|begrepp|svåröverblick|konkretisering|tolkning|detaljreglering|osäkerhet vid'),
 ('planering_verksamhet','Planering och verksamhet','Utmaningar för huvudmannens planering och verksamhet i övrigt: gymnasieantagning och dimensionering, programutbud, introduktionsprogram, uppföljning och kvalitetsarbete.',
   r'.*'),
]
def kategori_for(kod):
    k=kod.lower()
    for kid,namn,defn,rx in KATEGORIER:
        if re.search(rx,k): return kid
