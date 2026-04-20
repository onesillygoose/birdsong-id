function sortRecordings(columnIndex) {
  const table = document.getElementById("recordingsTable");
  const tbody = table.querySelector("tbody");
  const rows = Array.from(tbody.querySelectorAll("tr"));

  rows.sort((a, b) => {
    let valA = a.cells[columnIndex].textContent.trim();
    let valB = b.cells[columnIndex].textContent.trim();

    if (columnIndex === 0) {
        return valB.localeCompare(valA); // descending
    } else {
        return valA.localeCompare(valB); // ascending
    }
  });
  
  rows.forEach(row => tbody.appendChild(row));
}
