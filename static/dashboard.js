const form = document.querySelector("#participantForm");
const table = document.querySelector("#dataTable");
const tableBody = document.querySelector("tbody");

form.addEventListener("submit", fetchDataFromForm);

async function fetchDataFromForm(e) {
  e.preventDefault();
  let formData = new FormData(e.target);
  const fetchData = await fetch("/dashboardapi", { method: "POST", body: formData });
  const dataJson = await fetchData.json();
  console.log(dataJson);
  displayTable(dataJson);
}

function displayTable(data) {
  const participantIds = Object.keys(data);
  const headers = Object.keys(data[participantIds[0]][0]);
  const headerRow = document.querySelector("thead tr");
  headers.forEach((header) => {
    const th = document.createElement("th");
    th.textContent = header;
    headerRow.appendChild(th);
  });
  participantIds.forEach((id) => {
    data[id].forEach((value) => {
      const row = tableBody.insertRow();
      Object.keys(value).forEach((key) => {
        const cell = row.insertCell();
        cell.textContent = value[key];
      });
    });
  });
}
