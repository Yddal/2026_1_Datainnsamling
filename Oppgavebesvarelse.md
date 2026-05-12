## Problemstilling
Strømnettet i Norge har i dag en forutsigbarhetsproblem. Priser for neste dag publiseres mellom kl. 13 til 14 hver dag. Dette gir bedrifter ett kort handlingsrom til å justere produksjon eller å planlegge oppvarming av bygg. Ved å trene opp en algoritme på strømpriser og værmeldinger så kan en predikere mer nøyaktig hva prisene kommer til å bli fremover i tid.
Dette gjør det mulig for større verft til å planlegge produksjon, store varmeanlegg til å lagre varme i energibrønner eller for eksempel gi batterifabrikker muligheten til å vente med oppladning av batterier før utsending. Det kan også insentivere installasjonen av batterier i bygg for å bruke det for å fordele ut lasten ved å gi større besparelser på investeringen.

## Innsamlingsmetode
Data hentes via API fra følgende kilder:
*Siden oppgaven er stor på innsamlingssiden så er det mulig ikke alle blir implementert*
* ENTSO-E - Gir historiske strømpriser og vindproduksjon per prisområde
* Meteorologisk Institutt (MET) - Historisk og fremtidig værdata, Frost API for historisk og LocationForecast for fremtidig
* Norges vassdrags- og energidirektorat (NVE) - Data på vannmagasinene til Norge

ENTSO-E brukes fordi det er åpen informasjon og gratis. Nordpool ligger bak en betalingsmur og jeg fant etter noe søking en norsk nettside som distribuerer data for Norge ved å hente data fra ENTSO-E. For å ha muligheten til å hente priser fra andre sektorer i fremtiden så gikk jeg for å hente direkte fra ENTSO-E.

MET brukes fordi jeg tidligere har sett på Yr sitt API, YR henter data fra MET og ser ut til å ha lagt ned store deler av APIet og henviser istedet direkte til MET. Det er også gratis og åpent.

NVE brukes fordi det er eneste kilden jeg kjenner til rapportering av statusen til vannmagasinene i Norge som vil påvirke prisen veldig mye. Det er også åpent og gratis.

Utgangspunktet for å velge API som innhentingsmetode er for min egen læring, jeg jobber i en bransje som bruker mye API for henting og utveksling av data. Derfor ønsker jeg å få mer praktisk erfaring innenfor det, men det gjør det også lettere å få strukturert data som enkelt kan bearbeides. Scraping tar ofte mye tid erfarte jeg på tidligere oppgaver vi har hatt og ønsker derfor å unngå det. Info rundt API og retningslinjene på det er også mye enklere å forholde seg til i forhold til limiting og lov om bruksområde.

Under innsamlingen planlegger jeg å sette opp egne regler for hvert API med rate limiting og lagre alt lokalt for å minimere kall til APIet.

## Database
All data skal lagres i SQLite-database. For å forenkle opprettelsen av databasen. SQLite er litt enklere etter min mening og trenger ikke kompleksiteten med å sette opp en egen server. Det er også lettere å dele i forbindelse med innleveringen.

Utgangspunktet for innhentingen blir å skaffe ett dataset som går over året 2025 for å få alle årstidene.

## Refleksjon
### Hvem eier dataen?
**ENTSO-E** er en europeisk organisasjon for kraftoverføring og dataen er åpent tilgjengelig under EU sin "open data-lisens".

**MET** er en Norsk statsinstitusjon og publiserer data under den Norske lisensen for offentlige data (NLOD).

**NVE** er også en Norsk statsinstitusjon som publiserer under NLOD.

Siden alle 3 selskapene oppfordrer til åpenhet og bruken av data for at den skal være tilgjengelig for alle så regnes dataen som "allemanns-eie" og oppfordrer til fri bruk av dataen til analyse og forskning så lenge kildene oppgis.

### Hvilken belastning legges på kildene
Alle leverandørene av data har retningslinjer for belastning og innhentingen som må sees på for å holde seg innenfor.

**ENTSO-E**
Rate limit: 400 requests per minute per API token
Anbefalt rate limit er 6-7 req/sec for å ha en "burst handling".

Max date range: One-year date range
Max 100 dokumenter om gangen.

**MET Frost**
Har krav om Caching, frekvens, store forespørsler og identifikasjon.
De ber generelt om at en lagrer data for å ikke spørre unødvendig mye på dataen. Noe som er en generell regel en alltid bør følge.
De ber også om å splitte store forespørsler på dataset. De spesifiserer ikke tydelig hva ett stort dataset er utenom at forespørsel på 1000 værstasjoner kan splittes i set på 100 stasjoner om gangen. De sier også at lange perioder gjerne kan splittes inn i "N time subranges". De sier derimot ikke hva en lang tidsserie er, om det er en måned eller ett år. I APIet som er laget her har vi begrenset spørringen til 1 måned om gangen som tilsvarer opp til 744 datasett i det som ble sett under testing.
De spesifiserer også at hyppige spørringer som gjennomsnitter mer enn 1 spørring i sekunded bør begrenses. her har jeg implementert spørringer hvert andre sekund som standard.
De ber også om at en skal identifisere seg, dette er sånn sett påkrevd da du må oppgi Client ID. Når du da kjører spørringer mot APIet så ar Client ID regnet som din identifikasjon.

**MET Locationforecast**
MET sitt weather API har en 

**NVE**

### Etisk bruk av dataen
Siden dataen er åpen og ikke inneholder personopplysninger så er det mindre å ta hensyn til ved å benytte seg av dataen, så lenge en holder seg innenfor reglene som er satt hos kildene.

TEKST OM PERSONVERN

Sett at prosjektet har en minimal innhenting, bruk og videredistribusjon av dataen så kommer jeg ikke til å ta kontakt med institusjonene, men hvis dette var for ett reelt prosjekt som skulle benyttes i jobb eller for å publisere offentlig, så ville jeg tatt kontakt med de for å bekrefte min tolkning av retningslinjene. 

I ett reelt prosjekt så ville det vært nødvendig også å oppgi kildene. Ett skriftlig svar fra institusjonene ville derfor vært veldig aktuelt å legge opp på en info/about side for å være åpen om innhenting og bruken.


## AI Prompt 1:
what is the python format for getting days between two dates from 2026-04-01 to 2026-05-07?

### Svar:
date.fromisoformat handles YYYY-MM-DD directly. For full timestamps like 2026-04-01T00:00:00Z, use datetime.fromisoformat (Python 3.11+ accepts the trailing Z).

## AI Prompt 2:
bygg en requirements.txt og oppdater readme til å inkludere den i oppsettet

### Svar:
Requirements.txt:
requests>=2.33,<3
pandas>=3.0,<4
python-dotenv>=1.2,<2

readme line:
pip install -r requirements.txt

## Kilder
**ENTSO-E**
* [Power system asset management / Opne kodesnuttar / ENTSO-e transparency platform API · GitLab](https://gitlab.sintef.no/power-system-asset-management/opne-kodesnuttar/entso-e-transparency-platform-api)
* [Transparency Platform Restful API](https://documenter.getpostman.com/view/7009892/2s93JtP3F6)
* [How to get security token? – Transparency Platform](https://transparencyplatform.zendesk.com/hc/en-us/articles/12845911031188-How-to-get-security-token)
* [Sitemap for Restful API Integration – Transparency Platform](https://transparencyplatform.zendesk.com/hc/en-us/articles/15692855254548-Sitemap-for-Restful-API-Integration)

**MET FROST**
* [Frost MET - Terms Of Use](https://frost.met.no/termsofuse2.html)
* [Frost MET - Python example script](https://frost.met.no/python_example.html)

**MET LocationWeather**
[MET LocationWeather API Documentation](https://api.met.no/weatherapi/locationforecast/2.0/documentation)




