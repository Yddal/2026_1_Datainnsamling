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
import time
import pandas as pd
import requests

load_dotenv()

# === Konstanter ===
# MET Frost API for å hente historisk data om vær og vind.
MET_FROST_BASE_URL = "https://frost.met.no/"
MET_frost_client_ID = os.getenv("MET_frost_client_ID")
# nearest(POINT(20.241 65.578))
MET_frost_parameters = {
    'sources': 'SN71780', # SN71780 Åfjord II - Nærheten av Storheia Vindpark.
    'elements': 'air_temperature,wind_speed',
    'referencetime': '2025-01-01/2026-04-02',
    'timeresolutions': 'PT1H', # Hent data for hver time (PT1H = Period Time 1 Hour)
    'timeoffsets': 'PT0H', # Start klokken 0
    'levels': 'default', # Unngå doble avlesninger fra sensorer på samme høydenivå.
    'qualities': '0,1', # Hent alle data, inkludert de som er merket som "usikre" eller "feilaktige" av METs kvalitetssikringsprosess. Dette gir et mer komplett datasett
}

# MET Weather API for å hente prediksjoner om vær og vind.
# IKKE IMPLEMENTERT ENDA.
# MET_Weather_BASE_URL = "https://api.met.no/weatherapi/locationforecast/2.0/complete"
# MET_Weather_Client_ID = os.getenv("MET_Weather_Client_ID")

# === Funksjoner ===
# Hent data fra MET APIet ved bruk av GET-forespørsel.
# Finner nærmeste værstasjon basert på koordinater og skriver inn ID til 'sources' MET Frost parameters.
# Det er noe filtrering som må implementeres, da ikke alle stasjoner gir samme data. Du får treff, men får ikke hentet observations..
def find_sources(Coordinates: str) -> str:
    url = f"{MET_FROST_BASE_URL}/sources/v0.jsonld?geometry=nearest(POINT({Coordinates}))"
    try:
        response = requests.get(url, auth=(MET_frost_client_ID, ''), timeout=10)
    except requests.RequestException as e:
        print(f"FEIL! Henting av kildedata feilet: {e}")
        return ""

    response.raise_for_status() # Kaster et unntak (HTTPError) hvis status-koden er 4xx eller 5xx. "Fail loudly".
   
    if response.status_code != 200:
        print(f"FEIL! Henting av kildedata feilet: {response.text}")
        return ""
    else:
        data = response.json() # Parser respons-body fra JSON-tekst til en Python-dict for videre behandling.
        print(f"Suksess! Kildedata hentet for koordinater: {Coordinates}")
        print(f"Antall kilder funnet: {data.get('currentItemCount', "Ikke funnet")}")
        for sources in data.get('data', []):
            print(
                f"Kilde ID: {sources.get('id', "Ikke funnet")},\n"
                f"Kilde navn: {sources.get('name', "Ikke funnet")},\n"
                f"Land: {sources.get('country', "Ikke funnet")},\n"
                f"latitude, longitude: {sources.get('geometry', {}).get('coordinates', ['Ikke funnet', 'Ikke funnet'])}")
            print("-" * 40) # Separator for bedre lesbarhet i konsollen.
        # MET_frost_parameters['sources'] = response.json().get('data', [{}])[0].get('id', '') # Oppdater 'sources' i MET Frost parameters med 'id' fra første kilde i data-arrayet, eller en tom streng hvis ingen data.

    #return response.json().get('data', [{}])[0].get('id', '') # Hent 'id' fra første kilde i data-arrayet, eller returner en tom streng hvis ingen data.

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
        print(f"Suksess! Data hentet for: {name}, antall verdier i observations: {len(response.json().get('data', []))}")

    #response_data = response.json() # Parser respons-body fra JSON-tekst til en Python-dict og returnerer den.
    # print(f"Response JSON: {response_data}")  # Debug: Skriv ut hele JSON-responsen for å se strukturen.

    return response.json()

def get_observations(parameters: dict[str, Any]) -> dict[str, Any] | None:
    response = get_data("observations", parameters) # Hent alle observasjoner for angitt sted og tid
    start_date = pd.to_datetime(response.get('data', [{}])[0].get('referenceTime', 'unknown_start')).date() # Hent startdato, 'unknown_start' hvis det ikke kan hentes.
    end_date = pd.to_datetime(response.get('data', [{}])[-1].get('referenceTime', 'unknown_end')).date() # Hent sluttdato, 'unknown_end' hvis det ikke kan hentes.

    with open(f'data/met_frost_observations_{start_date}_{end_date}.json', 'w') as f: # Skriv til fil
        json.dump(response, f) # Dump JSON-data til filen.

def get_long_daterange(parameters: dict[str, Any]) -> None:
    # Split tidsrommet i kortere intervaller (f.eks. 1 måned) for å unngå for store datamengder.
    # Dette er etter METs anbefaling for å håndtere store datamengder og unngå timeouts eller avslag fra APIet.
    # Dette er en forenklet implementering som ikke tar hensyn til månedslengder, skuddår osv. For produksjon

    start_date, end_date = parameters['referencetime'].split('/') # Hent referencetime, som sier hvilket tidsrom vi ønsker data for, og splitt den i start- og sluttdato.

    start_date = pd.to_datetime(start_date).date() # Konverterer startdato til en date-objekt.
    end_date = (pd.to_datetime(end_date) + pd.DateOffset(days=1)).date() # Legg til 1 dag til end_date for å inkludere hele den siste dagen i tidsrommet. APIet henter frem til dato klokken 00:00, så da stopper data dagen før klokken 23:00.

    print(f"Start henting av data for periode: {start_date} til {end_date}")

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
            time.sleep(2) # Legg inn en kort pause mellom hver API-forespørsel for å unngå å overbelaste serveren eller treffe rate limits.

def combine_json_files(folder: str = 'data') -> None:
    
    files = [os.path.join(folder, f) for f in os.listdir(folder)] # Hent alle file i 'data' mappen og lag en liste fullstendige filstier.
    
    if (folder+"/combined_observations.json") in files: # Sjekk om 'combined_observations.json' allerede finnes 'data' mappen.
        print(f"Filen {folder}/combined_observations.json finnes allerede. Sletter den fra loop listen.")
        files.remove(folder+'/combined_observations.json') # Fjern fil for å ikke legge til samme data på nytt.
        print("-" * 40)
    
    files = sorted(files) # Sorter filene alfabetisk for å sikre at de kombineres i riktig rekkefølge.
    
    combined_data = [] # Liste for å samle alle datapunkter fra alle JSON-filene.

    for file in files:
        print(f"Legger inn data fra: {file}")
        with open(file, 'r') as f: # Åpne gjeldende fil for lesing.
            content = json.load(f) # Put innholdet inn i en variabel.
        
        combined_data.extend(content.get('data', [])) # .Extend legger til alle datapunktene fra denne filen som en del av det eksisterende arrayet. Append funksjonen ville gitt flere arrays i JSON filen.
    print(f"Kombinert totalt {len(combined_data)} datapunkter fra {len(files)} filer.")
    print(f"Første datapunkt: {combined_data[0].get('referenceTime')}")
    print(f"Siste datapunkt: {combined_data[-1].get('referenceTime')}")
    with open(f"{folder}/combined_observations.json", 'w') as f:
        json.dump({'data': combined_data}, f) # Skriv ut den kombinerte dataen til en ny JSON-fil.

# Koordinater for Markbygden II Vindpark, nær Piteå i Sverige. Format: "longitude, latitude".
# Bruk denne funksjonen for å finne nærmeste værstasjon.
# Oppdater MET_frost_parameters['sources'] Manuelt hvis du skal endre på oppsettet.
#MET_frost_coordinates = "20.241 65.578" # Format: "longitude latitude". OBS! Google maps gir motsatt (latitude, longitude).
#find_sources(MET_frost_coordinates)


get_long_daterange(MET_frost_parameters) # Legg inn en lang daterange for å teste splitting av tidsrommet i mindre intervaller. Dette er etter METs anbefaling for å håndtere store datamengder og unngå timeouts eller avslag fra APIet.
combine_json_files('data') # Kjør for å kombinere alle JSON-filene i 'data' mappen til en enkelt fil med alle observasjoner samlet.   
