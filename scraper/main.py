from bs4 import BeautifulSoup
import requests
import json
import os
import pandas as pd

def get_provinces_mapping() -> dict[str, str]:
	"""
	returns a dict[province_shorthand, region_name]
	this is needed for stats about regions,
	since the olicyber.it dump only shows participant provinces

	the reason why the shortand (RM instead of Roma) is used,
	is because there were a lot of edge cases and inconsistencies in province names
	for example:
	"barletta-andria-trani"	VS	"barletta andria trani"
	"forlì"					VS	"forli"					VS "forli'"
	"monza e brianza"		VS	"monza e della brianza"

	whereas shorthands are unique and they can be pulled from participants' school codes
	"""

	url = "https://it.wikipedia.org/wiki/Province_d'Italia"

	resp = requests.get(url)
	html = resp.text
	soup = BeautifulSoup(html, "html.parser")

	table = soup.select("table.wikitable")[0]
	province_rows = table.select("tbody tr")[1:-1] # the first and last rows are headings

	mapping = {}

	for row in province_rows:
		cells = row.select("td")

		shorthand = cells[1].text.strip()
		region = cells[2].select_one("a").attrs["title"]
		mapping[shorthand] = region

	return mapping

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
	target_script = scripts[5].attrs["src"]

	# get the script itself
	script_url = "https://olicyber.it" + target_script
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

			medal = "oro" if i < n_golds else "argento" if i < n_silvers else "bronzo" if i < n_bronzes else None
			if medal is not None:
				participants[key][medal] += 1

	# convert to list of medaled participants in order from best to worst
	participants = list(participants.values())
	participants.sort(key=lambda x: (x['oro'], x['argento'], x['bronzo'], -x['posizione_migliore']), reverse=True)

	# dump to json
	with open("../data/medagliere.json", "w") as f:
		json.dump(participants, f, indent="	")

	# dump to csv
	dataframe = pd.DataFrame(participants)
	dataframe.to_csv('../data/medagliere.csv', index=False)

def main():
	if not os.path.exists("../frontend/data"):
		os.mkdir("../frontend/data")

	# fetch data for all editions
	editions = fetch_editions()
	with open("../frontend/data/dump.json", "w") as f:
		json.dump(editions, f, indent="	")
	
	province_region_mapping = get_provinces_mapping()
	with open("../frontend/data/provinces.json", "w") as f:
		json.dump(province_region_mapping, f, indent="	")

	# dump all data about all editions
   	# dump_editions(editions)

	# dump general data about all participants
	# dump_participants(editions)

	# dump data about anyone who ever won a medal, and what medal they got
	# dump_medals(editions)

if __name__ == "__main__":
	main()