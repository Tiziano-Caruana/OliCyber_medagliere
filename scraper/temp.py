scuola = 'IS A.SCARPA (MOTTA DI LIVENZA, TREVISO)'

# dalla stringa prendi solo il nome della scuola
squola = scuola.split('(')[0].strip()
print(squola)

# dalla stringa prendi solo il comune
comune = scuola.split('(')[1].split(',')[0].strip()
print(comune)

# dalla stringa prendi solo la provincia
provincia = scuola.split('(')[1].split(',')[1].split(')')[0].strip()
print(provincia)