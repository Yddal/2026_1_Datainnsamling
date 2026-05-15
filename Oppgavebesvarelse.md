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

Dataen som er tiltenkt å hentes inn kommer til å være fra andre land sine vindparker da de anses som stor nok til å påvirke prisene i markedet. En analyse av hvilke vindparker som er mest påvirkende på kraftprisene må gjøres for å finne riktige lokasjoner.
I følge MET har de data fra de fleste lokasjoner i Europa.

NVE brukes fordi det er eneste kilden jeg kjenner til rapportering av statusen til vannmagasinene i Norge som vil påvirke prisen veldig mye. Det er også åpent og gratis.

Utgangspunktet for å velge API som innhentingsmetode er for min egen læring, jeg jobber i en bransje som bruker mye API for henting og utveksling av data. Derfor ønsker jeg å få mer praktisk erfaring innenfor det, men det gjør det også lettere å få strukturert data som enkelt kan bearbeides. Scraping tar ofte mye tid erfarte jeg på tidligere oppgaver vi har hatt og ønsker derfor å unngå det. Info rundt API og retningslinjene på det er også mye enklere å forholde seg til i forhold til limiting og lov om bruksområde.

Under innsamlingen planlegger jeg å sette opp egne regler for hvert API med rate limiting og lagre alt lokalt for å minimere kall til APIet.

## Hvilken data skal hentes
Som en start så tenker jeg å hente data fra Storheia vindpark. I det området er det flere større vindparker som påvirker det nordiske strømmarkedet NO3 og NO4.

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


**MET Frost**
Har krav om Caching, frekvens, store forespørsler og identifikasjon.
De ber generelt om at en lagrer data for å ikke spørre unødvendig mye på dataen. Noe som er en generell regel en alltid bør følge.
De ber også om å splitte store forespørsler på dataset. De spesifiserer ikke tydelig hva ett stort dataset er utenom at forespørsel på 1000 værstasjoner kan splittes i set på 100 stasjoner om gangen. De sier også at lange perioder gjerne kan splittes inn i "N time subranges". De sier derimot ikke hva en lang tidsserie er, om det er en måned eller ett år. I APIet som er laget her har vi begrenset spørringen til 1 måned om gangen som tilsvarer opp til 744 datasett i det som ble sett under testing.
De spesifiserer også at hyppige spørringer som gjennomsnitter mer enn 1 spørring i sekunded bør begrenses. her har jeg implementert spørringer hvert andre sekund som standard.
De ber også om at en skal identifisere seg, dette er sånn sett påkrevd da du må oppgi Client ID. Når du da kjører spørringer mot APIet så ar Client ID regnet som din identifikasjon.

**MET Locationforecast**
MET sitt weather API brukes for å hente værvarsel fremover i tid. De krever 3 hoved ting:
1. Du må identifisere deg
2. Du må unngå unødvendig trafikk mot APIet
    1. De presiserer også at nye spørringer ikke skal skje FØR indikasjonen i response headeren deres er utgått. Dette er ett tidsstempel som en må vente til er forbigått før en henter ny data.
    2. Cache data lokalt og bruke 'If-Modified-Since' request header for å unngå unødvendig nedlastning.
    3. Unngå for detaljert spørring på latitude/longitude. Rund av til max 4 desimaler. 
3. Du må ikke overbelaste serverene deres.
    1. Ikke spør gang på gang etter data som ikke endrer seg, som f.eks CAP filer, bilder, ikoner, osv.
    2. Ikke sett opp for mange spørringer samtidig. Som f.eks flere lokasjoner nøyaktig klokken xx:00. De ber om å legge til ett tilfeldig klokkeslett til spørringen for å variere spørretidspunktet og spre trafikken jevnt utover. Maks 20 requests i sekundet er nevnt.
    3. Unngå kontinuerlige oppdateringer i bakgrunnen på mobilenheter.
4. Bruk HTTPS ikke HTTP.

For å holde oss innenfor disse kravene så gjør jeg følgende:
1. Legger til identifikasjon på spørringen med navn og epost som i eksempel fra de nedenfor.
2. Rate-limiting på spørringen:
    1. Ikke spør oftere enn en time (pluss ett tilfeldig antall minutter 1-5).
    2. Sjekk tidspunkt på forrige data som ble hentet før spørring, er dataen utgått i henhold til forrige response header? Hvis nei, vent 10min og sjekk på nytt.
    3. Cache all data lokalt, ved forspørsel på data, sjekk cache først og sjekk for utløpt dato tidsstempel.
    4. Ta med 'If-Modified-Since' i request header. Pass også på at HEAD er først, ikke GET (eksplisitt nevnt i TermsOfService).
    5. Rund av longitude og latidude til 4 desimaler hvis de er lengre.
3. Hvis vi henter fra flere lokasjoner så splitter vi spørringen opp i flere.
    1. Hvis ikoner, bilder eller annet fra APIet skal brukes, hent det en gang.
    2. Spørringer fordeles over tid hvis det er flere lokasjoner som skal hentes med fast mellomrom på 10 sekunder (godt innenfor 20 i minuttet og greit nok for vår bruk).
    3. Unngå kontinuerlig oppdatering til f.eks mobilenheter som kjører i bakgrunnen. Hent kun når klienten er i aktiv bruk.

Eksempel for identifikasjon fra MET:
"acmeweathersite.com support@acmeweathersite.com"
"AcmeWeatherApp/0.9 github.com/acmeweatherapp"

Vi må også gi heder og ære til hvor dataen kommer fra. Derfor hvis dataen skal publiseres noe sted så skal info være klar og tydelig som følger:
1. Referanse til MET.
2. Link til lisensmodellen deres CC BY 4.0.
3. Hvis endringer ble gjort til dataen så skal det informere om og ikke indikere at endringene er godtatt av MET (som vil si de forbeholder seg retten til å be deg i ettertid ikke gjøre det).

**ENTSO-E**
Begrensninger og Terms of Use må sees nærmere på før en eventuell implementering. De notatene jeg har fra det jeg fant raskt er:
* Rate limit: 400 requests per minute per API token
* Anbefalt rate limit er 6-7 req/sec for å ha en "burst handling".
* Max date range: One-year date range
* Max 100 dokumenter om gangen.

**NVE**
NVE er ikke medtatt i besvarelsen. De andre gjennomgangene av APIer og retningslinjer håper jeg er tilfredsstillende.

### Etisk bruk av dataen
Siden dataen er åpen og ikke inneholder personopplysninger så er det mindre å ta hensyn til ved å benytte seg av dataen, så lenge en holder seg innenfor reglene som er satt hos kildene.

Sett at prosjektet har en minimal innhenting, bruk og videredistribusjon av dataen så kommer jeg ikke til å ta kontakt med institusjonene, men hvis dette var for ett reelt prosjekt som skulle benyttes i jobb eller for å publisere offentlig, så ville jeg tatt kontakt med de for å bekrefte min tolkning av retningslinjene.

I ett reelt prosjekt så ville det vært nødvendig også å oppgi kildene. Ett skriftlig svar fra institusjonene ville derfor vært veldig aktuelt å legge opp på en info/about side for å være åpen om innhenting og bruken.

Hver av institusjonene har sine egne retningslinjer for bruken av dataen og det er viktig å sette seg inn i alle sine krav. Som oftest i åpne dataset så er det krav om å oppgi kilder og lisensavtalen som de er underlagt. 

Prosjektet må også ha kontaktinfo som institusjonene kan kontakte deg på hvis de ønsker å endre på hvordan du bruker dataen.

#### Etisk bruk av dataen ved scraping
Ved scraping av en nettside så finner en som oftest informasjon rundt bruken og hva du har lov å hente i en /robots.txt fil. Der står det informasjon rundt tilganger for AI bots (User-agent) og hvilke mapper du har eller ikke har lov til å scrape.

Når en sier lov eller ikke lov til å scrape så er dette egentlig rent retningslinjer og det er ikke umulig å hente dataen, men det er en advarsel om at om du gjør det kan du bli blokkert.

Denne blokkeringen kan skje rent på den ene nettsiden, men flere og flere nettsider sitter etter hvert bak selskap som f.eks CloudFlare som kan blokkere din IP adresse mot flere nettsider og domener.

Å ignorere Robots.txt sine retningslinjer kan potensielt legge ganske store resursbruk på serverene som hoster sidene. Dette kan medføre store kostnader for firmaet som har siden noe som kan ha store konsekvenser for selskapet i seg selv hvis det er misbrukt nok. Det er derfor en kotyme og regel at en forholder seg til de restriksjonene som er gjort.

Det er også viktig å nevne at selv om det er lov å hente data basert på oppsettet til robots.txt filen, så betyr ikke det at du har lov til å ta i bruk og/eller videreselge informasjonen du har hentet. Data eller informasjon kan fremdeles være inn under en Copyright eller andre rettigheter som står på nettsiden.

#### Personvern
Hvis data eventuelt ville inneholdt detaljer rundt IP adresser, navn, epost, telefonnummer eller annen personlig informasjon fra brukere av tjenesten så ville en måtte hatt en brukeravtale på plass. For meg ville en naturlig del av tjenesten vært å sette opp ett eget API som brukerene hentet data fra for å unngå at eventuelle spørringer kommer direkte fra bruker og derfor vil eventuel data ikke videresendes.

Ved bruk av tjenesten vil en ha tilgang på IP adresse for brukeren samt diverse autentisering som brukeren har i nettleseren sin. Dette er mulig å anonymisere for eksempel, men i vårt tilfelle ville dette vært en tjeneste en ville solgt til brukere. Dette ville behøvd brukerinnlogging og lagring av data.

Det er da viktig at denne dataen håndteres på en sikker måte med begrenset tilgang til dataen slik at det ikke er mulig for utilsiktet adgang til dataen.

GDPR sier at personlig data som navn, epost, osv. ikke kan deles uten samtykke fra brukeren. Derfor er dette veldig viktig i dagens internett verden.

### Før eventuell bruk av data
Før bruk av dataen som er hentet må den sjekkes for hull i datasettene (ingen data på tidsrom). Dette må håndteres i forkant av ett maskinlæringsprosjekt for å ikke sende null verdier inn i algoritmen.

Å ha hull i tidsserien anses som mindre viktig da det er sammenheng av verdiene som er viktigst, ikke at alle tidsseriene er tilstede.

## Problemer underveis i oppgaven
Når jeg startet planleggingen av å hente data så sjekket jeg opp i API kildene og prøvde å forstå om de hadde dataen som jeg trengte for å ferdigstille prosjektet. Der viste det seg underveis at jeg skulle brukt mer tid på å teste om lokasjonene jeg var ute etter var tilgjengelig.

Etter å ha utviklet ferdig løsningen for MET Frost APIet så skulle jeg oppdatere lokasjon fra det som var lagt inn i eksempel fra MET. Det som viste seg da er at nærmeste værstasjon til vindpark jeg så for meg å bruke i Piteå er alt for lang vekke. Jeg har ikke klart å finne ut av enda om det er noe jeg gjør feil i APIet og har derfor gått tilbake til standard lokasjonen for å ha ett fungerende eksempel.

Det kan se ut som at MET Frost sin historikk er hovedsaklig for Norge og enkelte lokasjoner i Europa, men ikke med stor nøyaktighet som trengs for prosjektet.

## AI Prompt 1:
*Info: datokonvertering ble skrevet om senere til å bruke pandas.*
what is the python format for getting days between two dates from 2026-04-01 to 2026-05-07?

### Svar:
date.fromisoformat handles YYYY-MM-DD directly. For full timestamps like 2026-04-01T00:00:00Z, use datetime.fromisoformat (Python 3.11+ accepts the trailing Z).

## AI Prompt 2:
*Info: Readme filen ble kun brukt som utkast/eksempel og har blitt omskrevet og kontrollert*

Bygg en requirements.txt og en readme for å forklare prosjektet og hvordan sette opp miljøet.

### Svar:
```
Requirements.txt:
requests>=2.33,<3
pandas>=3.0,<4
python-dotenv>=1.2,<2

readme line:
pip install -r requirements.txt
```

## AI Prompt 3:
Forklar hva [{}] betyr i følgende kodesnutt: response.get('data', [{}]) jeg fant på nettet

Svar:
```
[{}] er en liste som inneholder én tom dictionary. Det brukes som en fallback-verdi for .get().

Slik fungerer det
response.get('data', [{}]) betyr:

Hvis response har nøkkelen 'data' → returner verdien (forventet en liste med dicts)
Hvis nøkkelen mangler → returner [{}] istedenfor
```

## AI Prompt 4 / Google søk:
python sort files in a list by date in a folder

Svar:

```python

import os

folder_path = '/path/to/your/folder'

# Get list of files in the directory
files = [os.path.join(folder_path, f) for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]

# Sort files by modification time (oldest first)
files.sort(key=os.path.getmtime)

# To sort by newest first, add reverse=True
# files.sort(key=os.path.getmtime, reverse=True)

print(files)
```

## AI Prompt 5:
explain this line of code for me:
            result = cursor.fetchall()
            print('SQLite Version is {}'.format(result[0][0]))

Svar:
```python
After cursor.execute(query) runs a SQL query, the results are held inside the cursor. fetchall() pulls every row of the result set into a Python list.

The shape is a list of tuples, where each tuple is one row:


[(row1_col1, row1_col2, ...), (row2_col1, ...), ...]
For a query like SELECT sqlite_version();, you'd get back something like:


[('3.45.1',)]
— one row, one column (note the trailing comma making it a tuple).

print('SQLite Version is {}'.format(result[0][0]))
This indexes into that list-of-tuples to pull out a single scalar value:

result[0] → the first row, e.g. ('3.45.1',)
result[0][0] → the first column of that first row, e.g. '3.45.1'
Then '... {}'.format(...) substitutes that value into the string, printing SQLite Version is 3.45.1
```

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
[MET LocationWeather Terms of Service](https://api.met.no/doc/TermsOfService)
[MET LocationWeather Getting Started](https://api.met.no/doc/GettingStarted)
[MET LocationWeather HowTo](https://api.met.no/doc/locationforecast/HowTO)


