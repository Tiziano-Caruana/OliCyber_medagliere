async function main() {
	const medalists = await fetch("../data/medagliere.json")
		.then(resp => resp.json());

	const table = document.querySelector("#medals");
	medalists.forEach((person, i) => {
		const row = document.createElement("tr");
		
		const values = [
			i+1,
			`${person.nome} ${person.cognome}`,
			person.oro,
			person.argento,
			person.bronzo
		];

		const cells = values.map(x => {
			const cell = document.createElement("td");
			cell.textContent = x;
			return cell;
		})

		row.append(...cells);
		table.append(row);
	})
}

main()
