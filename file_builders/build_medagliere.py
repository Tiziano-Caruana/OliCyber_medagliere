import json
import pandas as pd

edizioni = ["2021", "2022"]
medagliere = []
aux = []

for edizione in edizioni:
    with open(f'../data/{edizione}/graduatoria.json', 'r') as f:
        json_data = json.load(f)

    for i, participant in enumerate(json_data):
        if(i == 40):
            break
        partecipante = []
        if participant['cognome'] not in aux:
            medagliere.append({
            "nome": participant['nome'],
            "cognome": participant['cognome'],
            "oro": 0,
            "argento": 0,
            "bronzo": 0
        })
            aux.append(participant['cognome'])

        for medagliato in medagliere:
            if participant['cognome'] in medagliato['cognome']:
                if i < 5:
                    medagliato['oro'] += 1
                elif i < 15:
                    medagliato['argento'] += 1
                elif i < 40:
                    medagliato['bronzo'] += 1

with open(f'../data/medagliere.json', 'w') as f:
    json.dump(medagliere, f, indent=1)

with open(f'../data/medagliere.json', 'r') as f:
    json_data = json.load(f)

df = pd.DataFrame(json_data)
df.to_csv('../data/medagliere.csv', index=False)