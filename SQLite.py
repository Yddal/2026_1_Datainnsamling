"""
Script for å opprette og lage SQL databasen for prosjektet.
"""

# Environment setup
import sqlite3
import json

# ===   SQLite   ===
database_name = 'sqlite.db'
filename_data_to_push = 'data/combined_observations.json'

def execute_query(database_name:str, query:str) -> None:
    try :
        connection = sqlite3.connect(database_name)
        print("DB Initialisert")
        cursor = connection.cursor() # Cursor object for å kjøre SQL Queries på databasen.
        cursor.execute(query)
        result = cursor.fetchall()
        # if result: # Print kun hvis result ikke er tom.
            # print(f'SQLite response: {result}')
        connection.commit()
    except sqlite3.Error as error:
        print('Error occurred: ', error)
    finally:
        if connection:
            connection.close()
            print("SQLite connection closed)")
    return result

def execute_queries(database_name:str, queries:list) -> None:
    results = []
    try :
        connection = sqlite3.connect(database_name)
        print("DB Initialisert")
        cursor = connection.cursor() # Cursor object for å kjøre SQL Queries på databasen.
        for query in queries:
            cursor.execute(query)
            result = cursor.fetchall()
            if result: # Print kun hvis result ikke er tom.
                results.append(result[-1][0])
                # print('SQLite response: {}'.format(result[-1][0]))
        connection.commit()
    except sqlite3.Error as error:
        print('Error occurred: ', error)
    finally:
        if connection:
            connection.close()
            print("SQLite connection closed)")
    return results

def create_database(database_name:str):
    execute_query(database_name, """
              CREATE TABLE IF NOT EXISTS observations (
              ID INTEGER PRIMARY KEY AUTOINCREMENT,
              sourceId      TEXT    NOT NULL,
              referenceDate DATE    NOT NULL,
              referenceTime TEXT    NOT NULL,
              elementId     TEXT    NOT NULL,
              value         REAL,
              unit          TEXT
              ) 
              """)
    execute_query(database_name, "SELECT * FROM observations LIMIT 10")

def re_create_database(database_name:str):
    # Drop tabell og opprett på nytt.
    execute_query(database_name, "DROP TABLE observations")
    create_database(database_name)


def testing(database_name:str):
    ## Test av queries mot databasen og funksjon som er laget.
    queries = [
        "SELECT sqlite_version()",
        "SELECT sqlite_version()",
    ]
    print(execute_query(database_name, "SELECT sqlite_version()"))
    
    print("---" * 20)
    for results in execute_queries(database_name, queries):
        print(results)


def push_data_to_SQL(database_name:str, filename:str):
    # Les json data fra fil
    with open (filename, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Build queries
    queries = []
    for datapoint in data['data']:
        source = datapoint['sourceId']
        time = datapoint['referenceTime']
        time = time.split("T") # Lager ett array med dato i [0] og tid i [1], senere så sender vi kun første 5 i [1] arrayet. Dette gir oss tidsstempel som 03:00 i referansetid.
        for observation in datapoint['observations']:
            queries.append(
                f"INSERT INTO observations (sourceId, referenceDate, ReferenceTime, elementId, value, unit) VALUES"
                f"('{source}', '{time[0]}', '{time[1][:5]}', '{observation['elementId']}', '{observation['value']}', '{observation['unit']}')"
            )

    execute_queries(database_name,queries)

    print(f"Inserted {len(queries)} rows.")

def statisticsFromDatabase():
    statistics_queries = [
        "SELECT MIN(referenceDate) FROM observations",
        "SELECT MAX(referenceDate) FROM observations",
        "SELECT COUNT(*) FROM observations",
    ]

    databaseData = execute_queries(database_name, statistics_queries)
    print(databaseData)
    for data in databaseData:
        print(data)
    
    database_lines = execute_query(database_name, "SELECT * FROM observations LIMIT 10")
    for line in database_lines:
        print(line)


# testing(database_name)

# create_database(database_name)
# re_create_database(database_name) # Slett tabell observations, og lag den på nytt. Dette må gjøres hvis push data to SQL har kjørt flere ganger med samme data.
# push_data_to_SQL(database_name,filename_data_to_push)

statisticsFromDatabase()