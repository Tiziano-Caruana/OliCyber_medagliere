from bs4 import BeautifulSoup
from requests import *
import requests
import json

class TooEarlyException(Exception):
    # this happens when trying to extract data for nationals for the current year when they haven't been held yet
    ...

def get_all_editions_data():
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

def craft_csv(edition_data) -> str:
    content = ""
    
    if "nazionale" not in edition_data:
        raise TooEarlyException()

    for contestant_data in edition_data["nazionale"]:
        content += ", ".join([
            str(contestant_data["posizione"]),
            str(contestant_data["nome"]),
            str(contestant_data["cognome"]),
            str(contestant_data["punteggio"]),
            str(contestant_data["scuola"]),
            str(contestant_data["comune"]),
            str(contestant_data["provincia"]),
            str(contestant_data["classe"]),
        ]) + '\n'

    return content

def dump_data():
    editions_data = get_all_editions_data()
    
    for year in editions_data.keys():
        try:
            csv_content = craft_csv(editions_data[year])
        except TooEarlyException:
            continue

        with open(f"../data/{year}/graduatoria.csv", "w") as f:
            f.write(csv_content)

if __name__ == "__main__":
    dump_data()
