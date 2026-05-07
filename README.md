# 2026_1_Datainnsamling

Innsamling av åpne data for prediksjon av strømpriser i Norge. Prosjektet henter
historiske strømpriser, værdata og vannmagasinstatus fra åpne API-er, og lagrer
dem lokalt for videre analyse.

For en fullstendig beskrivelse av problemstilling, metodevalg og refleksjoner,
se [Oppgavebesvarelse.md](Oppgavebesvarelse.md).

## Datakilder

| Kilde | Innhold | Lisens | Status |
|-------|---------|--------|--------|
| [ENTSO-E Transparency Platform](https://transparency.entsoe.eu/) | Historiske strømpriser og vindproduksjon per prisområde | EU Open Data | Ikke implementert |
| [MET Frost API](https://frost.met.no/) | Historiske værobservasjoner | NLOD | Implementert ([Client_MET_API.py](Client_MET_API.py)) |
| [MET LocationForecast](https://api.met.no/) | Værprognoser | NLOD | Ikke implementert |
| [NVE](https://www.nve.no/) | Status for vannmagasiner | NLOD | Ikke implementert |

## Oppsett

Prosjektet bruker Python 3.11+ og et virtuelt miljø.

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### Miljøvariabler

Opprett en `.env`-fil i prosjektroten med API-nøkler:

```
MET_frost_client_ID=<din-frost-client-id>
MET_Weather_Client_ID=<din-weather-client-id>
```

Frost-nøkkel registreres på [frost.met.no/auth/requestCredentials.html](https://frost.met.no/auth/requestCredentials.html).
`.env` er allerede listet i `.gitignore` slik at nøklene ikke commitres.

## Bruk

### Hente observasjoner fra Frost

[Client_MET_API.py](Client_MET_API.py) henter time-for-time observasjoner og
lagrer dem som JSON i `data/`. Standardparametere ligger øverst i filen
(`MET_frost_parameters`):

- `sources`: stasjons-ID (f.eks. `SN90450`)
- `elements`: hvilke målinger som hentes (f.eks. `air_temperature,wind_speed`)
- `referencetime`: tidsrom på formatet `YYYY-MM-DD/YYYY-MM-DD`
- `timeresolutions`: `PT1H` for time-data, `P1D` for døgn-data

Lange tidsrom splittes i månedlige biter for å unngå timeout:

```python
get_long_daterange(MET_frost_parameters)
```

Hvert intervall lagres som en separat fil:
`data/met_frost_observations_<start>_<end>.json`.

### Hjelpefunksjoner

- `loop_json_data(file_path)` — skriver ut alle observasjoner i én JSON-fil i lesbar form.
- `inspect_data_folder(folder='data')` — viser antall observasjoner og første/siste tidspunkt for hver fil i mappa. Nyttig for å verifisere at innsamlingen dekker hele tidsrommet.

## Prosjektstruktur

```
.
├── Client_MET_API.py         # Klient for MET Frost API
├── Oppgavebesvarelse.md      # Problemstilling, metode og refleksjon
├── data/                     # Lagrede API-responser (JSON)
├── requirements.txt          # Python-avhengigheter
└── README.md
```

## Lagring

Innsamlet data lagres foreløpig som JSON-filer i `data/`. Plan er å migrere til
SQLite for enklere spørringer på tvers av kilder — se Oppgavebesvarelse.md.
