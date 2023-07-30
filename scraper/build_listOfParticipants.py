# Get data from json files

import json
import os

edizioni = ["2021", "2022"]

# Take data from json files and build a list of participants without duplicates
participants = []

for edizione in edizioni:
    with open(f'../data/{edizione}/graduatoria.json', 'r') as f:
        json_data = json.load(f)

    for participant in json_data:
        participants.append(participant)

# Remove duplicates
participants = list({v['nome']+v['cognome']:v for v in participants}.values())

# Write data to file
result = ""

for participant in participants:
    result += f"{participant['nome']}, {participant['cognome']}, {participant['scuola']}, {participant['comune']}, {participant['provincia']}\n"

with open(f'../data/participants.csv', 'w') as f:
    f.write(result)

# Build json data
json_data = []

for participant in participants:
    json_data.append({
        "nome": participant['nome'],
        "cognome": participant['cognome'],
        "scuola": participant['scuola'].replace('"', ''),
        "comune": participant['comune'],
        "provincia": participant['provincia']
    })

# Write json data to file
with open(f'../data/participants.json', 'w') as f:
    json.dump(json_data, f, indent=1)





