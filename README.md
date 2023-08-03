_Il progetto è nato da pochissimo e necessita di nuove funzionalità e miglioramento del codice. Eventuali contributi sono ben accetti_


## How to run it
First, you need to fetch the data dump.
Enter the `scraper` folder, and run `main.py`:
```bash
cd scraper
python3 main.py
```

Then, you need to compile the frontend typescript.
Enter the `frontend` folder, and run `tsc`:
```bash
cd frontend
tsc
```

Then, host it with a generic web-server, for example:
```bash
cd frontend
python3 -m http.server
```
