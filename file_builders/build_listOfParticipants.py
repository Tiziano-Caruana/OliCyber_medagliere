import pandas as pd
import json

edizioni = ["2021", "2022"]
participants = []

for edizione in edizioni:
    with open(f'../data/{edizione}/graduatoria.json', 'r') as f:
        json_data = json.load(f)

    for participant in json_data:
        participants.append(participant)

participants = list({v['nome']+v['cognome']:v for v in participants}.values())

result = ""

for participant in participants:
    result += f"{participant['nome']}, {participant['cognome']}, {participant['scuola']}, {participant['comune']}, {participant['provincia']}\n"

with open(f'../data/participants.csv', 'w') as f:
    f.write(result)

json_data = []

for participant in participants:
    json_data.append({
        "nome": participant['nome'],
        "cognome": participant['cognome'],
        "scuola": participant['scuola'].replace('"', ''),
        "comune": participant['comune'],
        "provincia": participant['provincia']
    })

with open(f'../data/participants.json', 'w') as f:
    json.dump(json_data, f, indent=1)

with open(f'../data/participants.json', 'r') as f:
    json_data = json.load(f)

df = pd.DataFrame(json_data)
df.to_csv('../data/participants.csv', index=False)





