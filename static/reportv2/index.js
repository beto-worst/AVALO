function applyIntermitentColoring() {
    const tableRows = document.querySelectorAll('tr');

    for(let i = 0; i<= tableRows.length; i++) {
        if(i%2 === 0) {
            tableRows[i].classList.add('colored')
        }
    }
}
applyIntermitentColoring()