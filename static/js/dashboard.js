const table = document.querySelector("#dataTable");
const tableBody = document.querySelector("tbody");
const participantDropdown = document.querySelector("#participant-dropdown");

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
  await renderTemplate();
  const data = await fetchDataOnLoad();
  const inputData = await getInputData();
  updateTable(data, inputData);
};
function updateTable(data, inputData) {
  const rows = document.querySelectorAll("tbody > tr");
  rows.forEach((row) => {
    const id = row.querySelector(".id").textContent;
    updateInputData(row, inputData, id);
    updateStartEndDate(row, data, id);
    addEventListenerToButton(row, id);
    updateMaxHr(row);
    // displayWeather(row, data, id);
  });
}
// async function displayWeather(row, data, id) {
//   const weatherSquare = row.querySelector(".weather");
//   const locationString = data[id]["location"];
//   let [long, lat] = locationString.split(" ");
//   long = parseFloat(long);
//   lat = parseFloat(lat);
//   try {
//     const pointResponse = await fetch(`https://api.weather.gov/points/${long},${lat}`);
//     const pointInfo = await pointResponse.json();
//     const foreCastLink = pointInfo.properties.forecastHourly;
//     const weatherResponse = await fetch(foreCastLink);
//     const weatherData = await weatherResponse.json();
//     const weatherInfo = weatherData.properties.periods[0];
//     const temp = weatherInfo.temperature;
//     const precipitation = weatherInfo.probabilityOfPrecipitation.value;
//     const wind = weatherInfo.windSpeed;
//     const humidity = weatherInfo.relativeHumidity.value;
//     weatherSquare.innerHTML = `
//   <div>Temp: ${temp} Deg F</div>
//   <div>Precipitation: ${precipitation}%</div>
//   <div>Wind: ${wind}</div>
//   <div>Humidity: ${humidity}</div>
//   `;
//   } catch (error) {
//     console.log("error", error);
//   }
// }
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
function toggleActiveInput(e) {
  e.target.disabled = !e.target.disabled;
}
function updateInputData(row, data, id) {
  const inputs = row.querySelectorAll(".age, .weight");
  inputs.forEach((input) => {
    input.addEventListener("dblclick", (e) => {
      e.target.disabled = false
    });
  });
  const ageInput = row.querySelector(".age > input");
  const weightInput = row.querySelector(".weight > input");
  ageInput.addEventListener("keypress", (e) => {
    if (e.keycode === 13 || e.which === 13) {
      const age = e.target.value;
      toggleActiveInput(e);
      sendInputData(id, age, "age");
      updateMaxHr(row);
    }
  });
  weightInput.addEventListener("keypress", (e) => {
    if (e.keycode === 13 || e.which === 13) {
      const weight = e.target.value;
      toggleActiveInput(e);
      sendInputData(id, weight, "weight");
    }
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

async function renderTemplate() {
  const res = await fetch("/dashboard", { method: "POST" });
  const data = await res.text();
  const tableContainer = document.querySelector("#data-container");
  tableContainer.innerHTML = data;
}
async function fetchDataOnLoad() {
  const fetchData = await fetch("/dashboardapi", { method: "GET" });
  const data = await fetchData.json();
  return data;
}
async function getInputData() {
  const res = await fetch("/inputdata", { method: "GET" });
  const data = await res.json();
  return data;
}

async function sendInputData(id, data, type) {
  try {
    const res = await fetch("/inputdata", {
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
