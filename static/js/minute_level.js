const form = document.querySelector("form");

window.onload = () => {
  const url = window.location.search;
  const params = new URLSearchParams(url);
  let id = params.get("id");
  if (!id) {
    id = "all";
  }
  updateTable(id);
  const participantDropdown = document.querySelector("#participants");
  participantDropdown.value = id;
};

form.addEventListener("submit", (e) => {
  e.preventDefault();
  const form = e.target;
  const participant = form.querySelector("#participants").value;
  const startDate = form.querySelector("#start_date").value;
  const endDate = form.querySelector("#end_date").value;
  updateTable(participant, startDate, endDate);
});

async function updateTable(id, start = undefined, end = undefined) {
  const res = await fetch("/minute_level", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      participant: id,
      start_date: start,
      end_date: end,
    }),
  });
  const data = await res.text();
  const tableContainer = document.querySelector("#table-container");
  tableContainer.innerHTML = data;
  const button = tableContainer.querySelector("button");
  button.addEventListener("click", () => {
    downloadCsv(id);
  });
}
function downloadCsv(id) {
  const csvString = getCsvString();
  const blob = new Blob([csvString], { type: "text/csv" });
  const link = document.createElement("a");
  const url = URL.createObjectURL(blob);
  link.setAttribute("href", url);
  link.setAttribute("download", `${id}-minute-level.csv`);

  document.body.appendChild(link);
  link.click();

  URL.revokeObjectURL(url);
  document.body.removeChild(link);
}
function getCsvString() {
  const table = document.querySelector("table");
  const rows = Array.from(table.querySelectorAll("tr"));

  return rows
    .map((row) => {
      const cells = Array.from(row.querySelectorAll("th,td"));
      return cells.map((cell) => cell.textContent).join(",");
    })
    .join("\n");
}
