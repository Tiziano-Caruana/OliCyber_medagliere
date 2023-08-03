interface DumpYear {
	// might not have been held yet
	"scolastica"?: [string, string, string, string, string, string, string, number][];
	// 2021 had no regionals
	"territoriale"?: [string, string, string, string, string, string, string, number][];
	// might not have been held yet
	"nazionale"?: {
		posizione: number,
		nome: string,
		cognome: string,
		punteggio: number,
		codice_scuola: string,
		scuola: string,
		comune: string,
		provincia: string,
		classe: number
	}[];
	// only 2021 had trainers
	"trainers"?: {[ctf_team: string]: [string, string]};
	// TODO!
	"sponsors": unknown[];
};

type Dump = {[year: string]: DumpYear};

interface Participant {
	nome: string;
	cognome: string;
	medaglie: {
		oro: number;
		argento: number;
		bronzo: number;
	};
	piazzamento_migliore: {
		posizione: number;
		anno: number;
	};
	partecipazioni: {[year: number]: number}; // year: rank
};

const N_GOLDS = 5;
const N_SILVERS = 15;
const N_BRONZES = 25;

function extract_participants(dump: Dump): Participant[] {
	const participants: {[id: string]: Participant} = {};

	const mk_placeholder_participant = (nome: string, cognome: string): Participant => ({
		nome,
		cognome,
		medaglie: {
			oro: 0,
			argento: 0,
			bronzo: 0
		},
		piazzamento_migliore: {
			posizione: -1,
			anno: -1
		},
		partecipazioni: []
	});

	for (const year_str in dump) {
		const edition = dump[year_str].nazionale;
		if (edition === undefined) continue;

		const year = parseInt(year_str);

		for (const person of edition) {
			const key = `${person.nome} ${person.cognome}`;
			participants[key] ||= mk_placeholder_participant(person.nome, person.cognome);
			participants[key].partecipazioni[year] = person.posizione;
			
			if (participants[key].piazzamento_migliore.posizione == -1 ||
				person.posizione < participants[key].piazzamento_migliore.posizione ||
				// prioritize most recent rankings
				(person.posizione == participants[key].piazzamento_migliore.posizione &&
					year < participants[key].piazzamento_migliore.anno)
				)
				participants[key].piazzamento_migliore = {
					posizione: person.posizione,
					anno: year
				};
			
			if (person.posizione <= N_GOLDS)
				participants[key].medaglie.oro++;
			else if (person.posizione <= N_SILVERS)
				participants[key].medaglie.argento++;
			else if (person.posizione <= N_BRONZES)
				participants[key].medaglie.bronzo++;
		}
	}

	const as_list = Object.values(participants);

	// sort by medals:
	/*
	as_list.sort((a, b) => {
		if (a.medaglie.oro != b.medaglie.oro)
			return b.medaglie.oro - a.medaglie.oro;
		if (a.medaglie.argento != b.medaglie.argento)
			return b.medaglie.argento - a.medaglie.argento;
		return b.medaglie.bronzo - a.medaglie.bronzo;
	});
	*/

	// sort by best rank:
	as_list.sort((a, b) => {
		if (a.piazzamento_migliore.posizione != b.piazzamento_migliore.posizione)
			return a.piazzamento_migliore.posizione - b.piazzamento_migliore.posizione;
		return a.piazzamento_migliore.anno - b.piazzamento_migliore.anno;
	});

	return as_list;
}

async function main() {
	const dump: Dump = await fetch("dump.json")
		.then(resp => resp.json());
	
	const participants = extract_participants(dump);

	const table = document.querySelector("#medals")!;
	participants.forEach((person, i) => {
		const row = document.createElement("tr");
		
		const values = [
			i+1,
			`${person.nome} ${person.cognome}`,
			`${person.piazzamento_migliore.posizione} (${person.piazzamento_migliore.anno})`,
			person.medaglie.oro,
			person.medaglie.argento,
			person.medaglie.bronzo
		];

		const cells = values.map(x => {
			const cell = document.createElement("td");
			cell.textContent = x.toString();
			return cell;
		})

		row.append(...cells);
		table.append(row);
	})
}

main();
