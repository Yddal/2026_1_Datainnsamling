# 2026_1_Datainnsamling
Innsamling av åpnen data fra værtjenester, historisk værdata og strømpriser for prediksjon av strømpriser i Norge.
Prosjektet henter historiske strømpriser, værdata og vannmagasinstatus fra åpne API-er, og lagrer det lokalt for å brukes videre i ett eventuelt maskinlæringsprosjekt.

For en fullstendig oppgavebeskrivelse, problemstilling og refleksjoner se[Oppgavebesvarelse.md](Oppgavebesvarelse.md).

## Datakilder som utgangspunkt i oppgaven

| Kilde | Innhold | Lisens | Status |
|-------|---------|--------|--------|
| [ENTSO-E Transparency Platform](https://transparency.entsoe.eu/) | Historiske strømpriser og vindproduksjon per prisområde | EU Open Data | Ikke implementert |
| [MET Frost API](https://frost.met.no/) | Historisk værdata | NLOD & CC BY 4.0 | Implementert* ([Client_MET_API.py](Client_MET_API.py)) |
| [MET LocationForecast](https://api.met.no/) | Værprognoser | NLOD & CC BY 4.0 | Ikke implementert |
| [NVE](https://www.nve.no/) | Status for vannmagasiner | NLOD & CC BY 3.0 | Ikke implementert |

*Implementert, men kan se ut som at data i Europa er ganske begrenset for historisk bruk. Oppløsning på lokasjoner kan være for dårlig til å brukes i ett maskinlæringsprosjekt.

## Oppsett

Prosjektet bruker Python 3.11+ og et virtuelt miljø.
For å sette opp og installere nødvendige pakker bruk følgende kommandoer for å hente fra requirements.txt fil.

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### Miljøvariabler
For å bruke MET Frost APIet så må du registrere deg på [frost.met.no/auth/requestCredentials.html](https://frost.met.no/auth/requestCredentials.html).
For å bruke APIet trenger du kun Client ID som legges inn i `.env` filen.

```
MET_frost_client_ID="din-frost-client-id"
```

`.env` filen er allerede listet i `.gitignore` slik at nøklene ikke comittes til git.

## Bruk

### Hente observasjoner fra Frost

[Client_MET_API.py](Client_MET_API.py) henter time-for-time observasjoner og lagrer de i JSON format under `data/` mappen. Standardparametere ligger øverst i filen i variabel `MET_frost_parameters`:

Lange tidsrom splittes i månedlige forespørsler for å unngå å nå grense for spørringer:

```python
get_long_daterange(MET_frost_parameters)
```

Hvert intervall lagres som en separat fil:
`data/met_frost_observations_<start>_<end>.json`.
og kombineres til en komplett datafil:
`data/combined_observations.json`.

## Prosjektstruktur

```
.
├── .env                      # Miljøvariabler som Client ID til API.
├── .gitignore                # Git ignore fil.
├── Client_MET_API.py         # Klient for MET Frost API
├── Oppgavebesvarelse.md      # Oppgavebesvarelse, problemstilling og refleksjon
├── data/                     # Lagrede API-responser (JSON)
├── requirements.txt          # Python-avhengigheter for å sette opp virtuelt miljø
├── sqlite.db                 # SQLite databasefil
├── SQLite.py                 # Script for innlesing av data fra JSON resultat til databasen
└── README.md
```