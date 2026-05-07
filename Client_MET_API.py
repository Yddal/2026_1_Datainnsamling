"""

Client for MET API.



"""

# Environment setup
import os
from urllib import response
from dotenv import load_dotenv
import argparse
import json
from typing import Any
from datetime import date


import pandas as pd

import requests

load_dotenv()

# === Konstanter ===
# MET Frost API for å hente historisk data om vær og vind.
MET_FROST_BASE_URL = "https://frost.met.no/"
MET_frost_client_ID = os.getenv("MET_frost_client_ID")


# MET Weather API for å hente prediksjoner om vær og vind.
MET_Weather_Client_ID = os.getenv("MET_Weather_Client_ID")



def get_data(name: str,parameters: dict[str, Any]) -> dict[str, Any] | None: 
    url = f"{MET_FROST_BASE_URL}/{name}/v0.jsonld"
    try:
        response = requests.get(url, parameters, auth=(MET_frost_client_ID, ''), timeout=10)
    except requests.RequestException as e:
        print(f"FEIL! Henting av data feilet for: {name}: {e}")
        return None

    response.raise_for_status() # Kaster et unntak (HTTPError) hvis status-koden er 4xx eller 5xx. "Fail loudly".
    
    if response.status_code != 200:
        print(f"FEIL! Henting av data feilet for: {name}: {response.text}")
        return None
    else:
        print(f"Suksess! Data hentet for: {name}")

    
    response_data = response.json() # Parser respons-body fra JSON-tekst til en Python-dict og returnerer den.
    # print(f"Response JSON: {response_data}")  # Debug: Skriv ut hele JSON-responsen for å se strukturen.

    return response.json()


MET_frost_parameters = {
    'sources': 'SN90450',
    'elements': 'air_temperature,wind_speed',
    'referencetime': '2026-01-01/2026-04-02',
    'timeresolutions': 'PT1H', # Hent data for hver time (PT1H = Period Time 1 Hour)
    'timeoffsets': 'PT0H', # Start klokken 0
    'levels': 'default', # Unngå doble avlesninger fra sensorer på samme høydenivå.
    'qualities': '0,1', # Hent alle data, inkludert de som er merket som "usikre" eller "feilaktige" av METs kvalitetssikringsprosess. Dette gir et mer komplett datasett
}

MET_frost_coordinates = "65.57838632358961, 20.24106911253074" # Koordinater for Markbygden II Vindpark, nær Piteå i Sverige. Format: "latitude, longitude".

def get_observations(parameters: dict[str, Any]) -> dict[str, Any] | None:
    response = get_data("observations", parameters) # Hent alle observasjoner for angitt sted og tid
    start_date, end_date = parameters['referencetime'].split('/') # Hent referencetime, som sier hvilket tidsrom vi ønsker data for, og splitt den i start- og sluttdato.
    with open(f'data/met_frost_observations_{start_date}_{end_date}.json', 'w') as f: # Skriv til fil
        json.dump(response, f) # Dump JSON-data til filen.

def get_long_daterange(parameters: dict[str, Any]) -> None:
    # Split tidsrommet i kortere intervaller (f.eks. 1 måned) for å unngå for store datamengder.
    # Dette er etter METs anbefaling for å håndtere store datamengder og unngå timeouts eller avslag fra APIet.
    # Dette er en forenklet implementering som ikke tar hensyn til månedslengder, skuddår osv. For produksjon

    start_date, end_date = parameters['referencetime'].split('/') # Hent referencetime, som sier hvilket tidsrom vi ønsker data for, og splitt den i start- og sluttdato.

    start_date = pd.to_datetime(start_date).date() # Konverterer startdato til en date-objekt.
    end_date = pd.to_datetime(end_date).date()

    if start_date >= end_date:
        print("FEIL! Startdato må være før sluttdato.")
        return
    elif (end_date - start_date).days <= 31: # Hvis tidsrommet er 31 dager eller mindre, hent data for hele perioden uten splitting.
        print("Tidsrommet er kort nok, ingen splitting nødvendig.")
        #get_observations(parameters) # Hent data for det angitte tidsrommet.
        return
    else:
        print("Tidsrommet er for langt, splitter i mindre intervaller.")
        
        while start_date < end_date:
            interval_end_date = (start_date + pd.DateOffset(months=1)).date() # Legg til 1 måned til startdato for å hente en måned.
            if interval_end_date > end_date: # Sjekk 'end_date' mot 'interval_end_date'. Hvis vi har forbigått 'end_date', så bruk den.
                interval_end_date = end_date
            parameters['referencetime'] = f"{start_date}/{interval_end_date}" # Oppdater parameters med det nye tidsrommet.
            print(f"Henter data for periode: {parameters['referencetime']}") # Debug: Skriv ut tidsrommet vi henter data for.
            start_date = interval_end_date
            get_observations(parameters) # Hent data for det angitte tidsrommet.
    parameters['referencetime'] = f"{start_date}/{end_date}" # Oppdater parameters med det nye tidsrommet.

def combine_json_files(folder: str = 'data') -> None:
    from pathlib import Path

    files = sorted(Path(folder).glob('*.json'))
    combined_data = [] # Liste for å samle alle datapunkter fra alle JSON-filene.
    for path in files:
        with open(path, 'r') as f:
            content = json.load(f)
        combined_data.extend(content.get('data', [])) # .Extend legger til alle datapunktene fra denne filen som en del av det eksisterende arrayet. Append funksjonen ville gitt flere arrays i JSON filen.

    with open(f'{folder}/combined_observations.json', 'w') as f:
        json.dump({'data': combined_data}, f) # Skriv ut den kombinerte dataen til en ny JSON-fil.

# --------------------------------
# Ikke lengre brukte funksjoner  |
# --------------------------------
# Brukt for å verifisere en og en json fil i Early-testing.
def loop_json_data(file_path: str) -> None:
    with open(file_path, 'r') as f:
        data = json.load(f)
    for value in data.get('data', []): # Iterer gjennom alle datapunkter i responsen
        print(f"Time: {value.get('referenceTime')}")
        for observations in value.get('observations', []): # Hent ut observasjoner for hver tidsreferanse
            print(f"Element: {observations.get('elementId')}, Value: {observations.get('value')}, Unit: {observations.get('unit')}")
        print("-" * 40) # Separator for lesbarhet

    print(f"SourceID: {data.get('data', [{}])[0].get('sourceId') if data.get('data') else 'N/A'}") # Hent sourceId fra første datapunkt, eller 'N/A' hvis ingen data.
    # I data.get('data', [{}]) så står [{}] for default verdi hvis 'data' skulle vært tom eller ikke finnnes. Dette forhindrer KeyError når vi prøver å hente 'SourceID'.
    print(f"Link: {data.get('currentLink')}") # Hent link som sendes til APIet.


# get_observations(MET_frost_parameters) Kjør for å hente data og lagre i JSON-fil

# get_long_daterange(MET_frost_parameters) # Legg inn en lang daterange for å teste splitting av tidsrommet i mindre intervaller. Dette er etter METs anbefaling for å håndtere store datamengder og unngå timeouts eller avslag fra APIet.
# Legg inn splitting av dato range i mindre serier.

combine_json_files() # Kjør for å kombinere alle JSON-filene i 'data' mappen til en enkelt fil med alle observasjoner samlet.   


"""
AI Magic prompt:
Can you make a function to check the files inside the "data" folder and get the first and last value in 'data' ?
"""
def inspect_data_folder(folder: str = 'data') -> None:
    from pathlib import Path

    files = sorted(Path(folder).glob('*.json'))
    if not files:
        print(f"Ingen JSON-filer funnet i '{folder}'.")
        return

    for path in files:
        with open(path, 'r') as f:
            content = json.load(f)
        entries = content.get('data', [])
        print(f"--- {path.name} ---")
        if not entries:
            print("  (tom)")
            continue
        print(f"  Antall: {len(entries)}")
        print(f"  Første: {entries[0].get('referenceTime')}")
        print(f"  Siste:  {entries[-1].get('referenceTime')}")

# inspect_data_folder() # Kjør for å dobbelsjekke innholdet som er hentet.