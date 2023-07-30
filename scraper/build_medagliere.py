import csv
import json
import os

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
        #Se tra i primi 40 indici e non è già presente salva il partecipante
        if participant['cognome'] not in aux:
            partecipante.append(participant['nome'])
            partecipante.append(participant['cognome'])
            partecipante.append(0)
            partecipante.append(0)
            partecipante.append(0)
            medagliere.append(partecipante)
            aux.append(participant['cognome'])

        for i2, medagliato in enumerate(medagliere):
            if participant['cognome'] in medagliato:
                if i < 5:
                    medagliere[i2][2] = medagliere[i2][2] + 1
                elif i < 15:
                    medagliere[i2][3] = medagliere[i2][3] + 1
                elif i < 40:
                    medagliere[i2][4] = medagliere[i2][4] + 1

# Write json data to file
with open(f'../data/medagliere.json', 'w') as f:
    json.dump(medagliere, f, indent=1)