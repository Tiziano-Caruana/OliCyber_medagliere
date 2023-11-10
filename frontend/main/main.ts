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

enum Medal {
	Gold = "oro",
	Silver = "argento",
	Bronze = "bronzo"
};

const N_GOLDS = 5;
const N_SILVERS = 15;
const N_BRONZES = 25;

function calculate_medal(rank: number): Medal | undefined {
	if (rank <= N_GOLDS)
		return Medal.Gold;
	if (rank <= N_SILVERS)
		return Medal.Silver;
	if (rank <= N_BRONZES)
		return Medal.Bronze;
}

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
	partecipazioni: {
		posizione: number,
		anno: number,
		medaglia: Medal | undefined
	}[];
};

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

			const recap: Participant["partecipazioni"][0] = {
				posizione: person.posizione,
				anno: year,
				medaglia: calculate_medal(person.posizione)
			};
			participants[key].partecipazioni.push(recap);
			
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
			
			if (recap.medaglia !== undefined)
				participants[key].medaglie[recap.medaglia]++;
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

	// sort by more golds, then more silvers, then more bronzes, then better best placement, then number of finals participations, then more recent best placement
	as_list.sort((a, b) => {
		if (a.medaglie.oro != b.medaglie.oro)
			return b.medaglie.oro - a.medaglie.oro;
		if (a.medaglie.argento != b.medaglie.argento)
			return b.medaglie.argento - a.medaglie.argento;
		if (a.medaglie.bronzo != b.medaglie.bronzo)
			return b.medaglie.bronzo - a.medaglie.bronzo;
		if (a.piazzamento_migliore.posizione != b.piazzamento_migliore.posizione)
			return a.piazzamento_migliore.posizione - b.piazzamento_migliore.posizione;
		if (a.partecipazioni.length != b.partecipazioni.length)
			return b.partecipazioni.length - a.partecipazioni.length;
		return b.piazzamento_migliore.anno - a.piazzamento_migliore.anno;
	});

	return as_list;
}

async function main() {
	const dump: Dump = await fetch("../data/dump.json")
		.then(resp => resp.json());
	
	const participants = extract_participants(dump);

	const mk_medal_svg = (medal: Medal) => {
		const size = 25;
		const color_map = {
			"oro": "#ffdb19",
			"argento": "#c0c0c0",
			"bronzo": "#cd7f32"
		};

		/* why createElementNS is needed:
		- https://stackoverflow.com/questions/69518311/svg-appended-to-dom-with-js-but-not-visually-rendering
		- https://stackoverflow.com/questions/8173217/createelement-vs-createelementns
		- https://www.brightec.co.uk/blog/svg-wouldnt-render
		*/
		const svg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
		svg.setAttribute("width", `${size}px`);
		svg.setAttribute("height", `${size}px`);
		svg.setAttribute("viewBox", "0 0 1024 1024");
		svg.setAttribute("fill", color_map[medal]);

		const path = document.createElementNS("http://www.w3.org/2000/svg", "path");
		path.setAttribute("d", "M547 304.2h-451l108.2-207.8h481.4z M685.6 754.4c0 95.656-77.544 173.2-173.2 173.2s-173.2-77.544-173.2-173.2c0-95.656 77.544-173.2 173.2-173.2s173.2 77.544 173.2 173.2z M697.8 598.2l230.2-294-138.6-207.8-276.6 415.6c64.6 0 125.4 25.4 171 71 5 5 9.6 10 14 15.2z M411.6 533.2l-107-161.2h-207.8l180.2 323c10.4-42.4 32.2-81.2 64-112.8 20.8-20.6 44.6-37.2 70.6-49z");
		svg.append(path);

		return svg;
	}

	const table = document.querySelector("#medals")!;
	participants.forEach((person, i) => {
		const row = document.createElement("tr");

		const cells = Array.from({length: 7}, () => document.createElement("td"));
		cells[0].textContent = (i+1).toString();
		cells[1].textContent = `${person.nome} ${person.cognome}`;
		cells[2].textContent = `${person.piazzamento_migliore.posizione} (${person.piazzamento_migliore.anno})`;

		const participations = document.createElement("ul");
		person.partecipazioni.sort((a, b) => b.anno - a.anno);
		for (const x of person.partecipazioni) {
			const elem = document.createElement("li");
			elem.textContent = x.anno.toString();

			if (x.medaglia !== undefined)
				elem.append(mk_medal_svg(x.medaglia));

			participations.append(elem);
		}
		cells[3].append(participations);

		cells[4].textContent = (person.medaglie.oro).toString();
		cells[5].textContent = (person.medaglie.argento).toString();
		cells[6].textContent = (person.medaglie.bronzo).toString();

		row.append(...cells);
		table.append(row);
	})
}

main();
