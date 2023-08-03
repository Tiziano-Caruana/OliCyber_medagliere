from bs4 import BeautifulSoup
import requests
import json
import os
import pandas as pd

def fetch_editions():
    """
    the data we want is hardcoded in a JS file with name `main-es2015.{hex stuff}.js`
    i think that hex stuff is an id which changes on site build, so i'm extracting it from the page html
    """

    # get the site's homepage
    homepage_url = "https://olicyber.it/edizioni/2021" # it loads data for all editions no matter what edition you lookup
    resp = requests.get(homepage_url)
    html = resp.text
    
    # find the src of the target script
    soup = BeautifulSoup(html, "html.parser")
    scripts = soup.select("script")
    target_script = next(filter(lambda tag: tag.attrs["src"].startswith("main"), scripts))

    # get the script itself
    script_url = "https://olicyber.it/" + target_script.attrs["src"]
    resp = requests.get(script_url)
    code = resp.text

    # it's 1 object with data for all editions, in order. the first one was in 2021
    left = code.index('{"2021":{"scolastica')
    right = code.index("')", left)
    data = code[left:right]

    # remove escapes like \\ or \x or \'
    data = data.encode().decode("unicode_escape")

    return json.loads(data)

def dump_editions(data):
    for year, edition in data.items():
        # it's too early. this should only happen with the last (current) year
        if "nazionale" not in edition:
            continue
        
        if not os.path.isdir(f"../data/{year}/"):
            os.mkdir(f"../data/{year}/")

        with open(f"../data/{year}/graduatoria.json", "w") as f:
            json.dump(data[year]["nazionale"], f, indent="	")

        csv_content = ""
        for contestant in edition["nazionale"]:
            csv_content += ", ".join([
                str(contestant["posizione"]),
                contestant["nome"],
                contestant["cognome"],
                str(contestant["punteggio"]),
                contestant["scuola"],
                contestant["comune"],
                contestant["provincia"],
                str(contestant["classe"]),
            ]) + '\n'

        with open(f"../data/{year}/graduatoria.csv", "w") as f:
            f.write(csv_content)

def dump_participants(data):
    """
    if someone participated in more than one edition, they should only be counted once
    initially i used a set with (name, surname) as key, but i've decided it's best to overwrite old data
    and always use the latest info, for example in 2021 school names were abbreviated, in 2022, they weren't
    """
    participants = {}

    keys = ["nome", "cognome", "scuola", "comune", "provincia"]
    for edition in data.values():
        # it's too early. this should only happen with the last (current) year
        if "nazionale" not in edition:
            continue

        for contestant in edition["nazionale"]:
            key = (contestant["nome"], contestant["cognome"])
            participants[key] = {k:contestant[k] for k in keys}
            participants[key]["scuola"] = participants[key]["scuola"].replace('"', '')
    
    participants = list(participants.values())

    # dump to json
    with open("../data/participants.json", "w") as f:
        json.dump(participants, f, indent="	")
    
    # dump to csv
    dataframe = pd.DataFrame(participants)
    dataframe.to_csv('../data/participants.csv', index=False)

def dump_medals(data):
    n_golds = 5
    n_silvers = 15
    n_bronzes = 40

    participants = {}

    for edition in data.values():
        # it's too early. this should only happen with the last (current) year
        if "nazionale" not in edition:
            continue

        # a list of contestants sorted from highest to lowest score
        leaderboard = sorted(edition["nazionale"], key=lambda x: x["punteggio"], reverse=True)

        for i, contestant in enumerate(leaderboard):
            if i >= n_bronzes:
                continue

            key = (contestant["nome"], contestant["cognome"])
            if key not in participants:
                participants[key] = {
                    "nome": contestant["nome"],
                    "cognome": contestant["cognome"],
                    "oro": 0,
                    "argento": 0,
                    "bronzo": 0,
                    "posizione_migliore": contestant["posizione"]
                }
            else:
                participants[key]["posizione_migliore"] = min(
                    participants[key]["posizione_migliore"],
                    contestant["posizione"]
                )
            
            medal = "oro" if i < n_golds else "argento" if i < n_silvers else "bronzo"
            participants[key][medal] += 1
    
    # convert to list of medaled participants in order from best to worst
    participants = list(participants.values())
    participants.sort(key=lambda x: (x['oro'], x['argento'], x['bronzo']),  reverse=True)

    # dump to json
    with open("../data/medagliere.json", "w") as f:
        json.dump(participants, f, indent="	")
    
    # dump to csv
    dataframe = pd.DataFrame(participants)
    dataframe.to_csv('../data/medagliere.csv', index=False)

def main():
    # fetch data for all editions
    editions = fetch_editions()
    with open("../frontend/dump.json", "w") as f:
        json.dump(editions, f, indent="	")

    # dump all data about all editions
    # dump_editions(editions)
    
    # dump general data about all participants
    # dump_participants(editions)

    # dump data about anyone who ever won a medal, and what medal they got
    # dump_medals(editions)

if __name__ == "__main__":
    main()
