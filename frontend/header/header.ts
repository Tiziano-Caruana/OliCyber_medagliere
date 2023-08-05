const header_src_elem = document.querySelector("div[auto-header]")!;
const header_src = header_src_elem.getAttribute("auto-header")!;

fetch(header_src)
	.then(resp => resp.text())
	.then(header_html => header_src_elem.innerHTML = header_html);
