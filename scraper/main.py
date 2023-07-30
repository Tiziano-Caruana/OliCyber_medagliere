from itertools import islice
from time import sleep
from bs4 import BeautifulSoup
from requests import *
from selenium import webdriver
from selenium.webdriver.chromium.options import *

# Get da whole thing

driver = webdriver.Chrome()
driver.get("https://olicyber.it/edizioni/2021")


# Wait for all the table elements to load
sleep(5)

page_source = driver.page_source

# BS4

graduatoria = []
partecipante = []
result = ""

soup = BeautifulSoup(page_source, 'html.parser')
participants = soup.find_all('td')

for participant in participants:
    if " " in participant.text and "(" not in participant.text:
        graduatoria.append(partecipante)
        partecipante = []
        partecipante.append(participant.text)
    else:
        partecipante.append(participant.text)


# This works
graduatoria = list(islice(reversed(graduatoria), 0, 136))
graduatoria.reverse()

# Write data in CSV file
for i, partecipante in enumerate(graduatoria):
    scuola = partecipante[2].split('(')[0].strip()
    comune = partecipante[2].split('(')[1].split(',')[0].strip()
    provincia = partecipante[2].split('(')[1].split(',')[1].split(')')[0].strip()
    nome = partecipante[0].split(' ')[0]
    cognome = partecipante[0].split(' ')[1]
    result += f"{i+1}, {nome}, {cognome}, {partecipante[1]}, {scuola}, {comune}, {provincia}, {partecipante[3]}\n"

with open('graduatoria.csv', 'w') as f:
    f.write(result)


