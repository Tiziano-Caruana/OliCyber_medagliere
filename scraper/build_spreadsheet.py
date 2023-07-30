# Build json data from spreadsheet

import csv
import json

edizioni = ["2021", "2022"]

for edizione in edizioni:
    with open(f'../data/{edizione}/graduatoria.csv', 'r') as f:
        reader = csv.reader(f)
        data = list(reader)

    # Build json data
    json_data = []

    for row in data:
        json_data.append({
            "posizione": row[0],
            "nome": row[1].strip(),
            "cognome": row[2].strip(),
            "punteggio": row[3].strip(),
            "scuola": row[4].strip().replace('"', ''),
            "comune": row[5].strip(),
            "provincia": row[6].strip(),
            "anno": row[7].strip()
        })

    # Write json data to file
    with open(f'../data/{edizione}/graduatoria.json', 'w') as f:
        json.dump(json_data, f, indent=1)