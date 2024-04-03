const table = document.querySelector("#dataTable");
const tableBody = document.querySelector("tbody");
const participantDropdown = document.querySelector("#participant-dropdown");

// Filering the table based on the participant
participantDropdown.addEventListener("change", (e) => {
  const rows = document.querySelectorAll("tbody > tr");
  const val = e.target.value;
  if (val === "all") {
    rows.forEach((row) => {
      row.classList.remove("none");
    });
  } else {
    rows.forEach((row) => {
      row.classList.remove("none");
      const id = row.querySelector(".id").textContent;
      if (id !== val) {
        row.classList.add("none");
      }
    });
  }
});

window.onpageshow = async () => {
  await renderTable();
  const data = await fetchDataOnLoad();
  updateTable(data);
};
function updateTable(data) {
  const rows = document.querySelectorAll("tbody > tr");
  rows.forEach((row) => {
    const id = row.querySelector(".id").textContent;
    updateInputData(row, data, id);
    updateStartEndDate(row, data, id);
    addEventListenerToButton(row, id);
    updateMaxHr(row);
  });
}
// Event listeners to change page on click
function addEventListenerToButton(row, id) {
  const buttons = row.querySelectorAll(".minute_level button, .halfhour_level button");
  buttons.forEach(button => {
    button.addEventListener("click", () => {
      const type = button.parentNode.className
      const URLdata = { id: id };
      const query = new URLSearchParams(URLdata).toString();
      window.location.href = `/${type}?` + query;
    });
  });
}
// Creates eventListeners to update the age and weight data in the database
function updateInputData(row, data, id) {
  const ageInput = row.querySelector(".age > input");
  const weightInput = row.querySelector(".weight > input");
  ageInput.addEventListener("change", (e) => {
    const age = e.target.value;
    sendInputData(id, age, "age");
    updateMaxHr(row);
  });
  weightInput.addEventListener("change", (e) => {
    const weight = e.target.value;
    sendInputData(id, weight, "weight");
  });
  if (data[id]) {
    if (data[id]["age"]) {
      ageInput.value = data[id]["age"];
    }
    if (data[id]["weight"]) {
      weightInput.value = data[id]["weight"];
    }
  }
}
function updateStartEndDate(row, data, id) {
  const start = row.querySelector(".start");
  const end = row.querySelector(".end");
  start.textContent = data[id]["earliest_date"].split(" ")[0];
  end.textContent = data[id]["most_recent_date"].split(" ")[0];
}
function updateMaxHr(row) {
  const input = row.querySelector(".age > input");
  const age = input.value;
  if (age) {
    const maxHr = 210 - 0.56 * age - 15.5;
    const roundedHr = Math.round(maxHr * 100) / 100;
    const hr = row.querySelector(".hrpeak");
    hr.innerText = roundedHr;
  }
}

async function renderTable() {
  const res = await fetch("/dashboard", { method: "POST" });
  const data = await res.text();
  const tableContainer = document.querySelector("#data-container");
  tableContainer.innerHTML = data;
}
async function fetchDataOnLoad() {
  const fetchData = await fetch("/api/dashboard", { method: "GET" });
  const data = await fetchData.json();
  return data;
}
async function getInputData() {
  const res = await fetch("/api/dashboard", { method: "GET" });
  const data = await res.json();
  return data;
}

async function sendInputData(id, data, type) {
  try {
    await fetch("/api/dashboard", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        participantid: id,
        type: type,
        data: data,
      }),
    });
  } catch (error) {
    console.log("error", error);
  }
}
