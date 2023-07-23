const table = document.querySelector("#dataTable");
const tableBody = document.querySelector("tbody");
const participantDropdown = document.querySelector("#participant-dropdown");
let data;

participantDropdown.addEventListener("change", () => {
  const id = participantDropdown.value.toLowerCase();
  if (id === "all") {
    displayParticipants(data);
  } else {
    displayParticipants({ [id]: data[id] });
  }
});

window.onpageshow = () => {
  fetchDataOnLoad();
};

async function fetchDataOnLoad() {
  const fetchData = await fetch("/dashboardapi", { method: "GET" });
  const allParticipantJson = await fetchData.json();
  data = allParticipantJson;
  sortDataByDate(data);
  await displayParticipants(allParticipantJson);
  const ageWeight = getAgeWeight();
}
async function getAgeWeight() {
  const res = await fetch("/ageweight", { method: "GET" });
  const data = await res.json();
  return data;
}

async function displayParticipants(participantJson) {
  const promises = [];
  if (tableBody) {
    tableBody.innerHTML = "";
  }
  const participantIds = Object.keys(participantJson);
  participantIds.forEach(async (id) => {
    const info = getParticipantInformation(participantJson, id);
    promises.push(info);
  });
  const results = await Promise.all(promises);
  results.forEach((info) => {
    const row = tableBody.insertRow();
    const headers = document.getElementsByTagName("th");
    for (const key in info) {
      const id = info["Participant ID"].innerText;
      const cell = row.insertCell();
      for (const header of headers) {
        if (header.textContent === key) {
          if (info[key]) {
            info[key].id = id + "-" + key.replace(/ /g, "-").toLowerCase();
            info[key].className = key.replace(/ /g, "-").toLowerCase();
            cell.appendChild(info[key]);
          }
        }
      }
    }
  });
  addEventListeners();
}
function addEventListeners() {
  //minute level listener
  const minuteButtons = document.querySelectorAll(".minute-level-data");
  minuteButtons.forEach((button) => {
    const id = button.id.split("-")[0];
    button.addEventListener("click", () => {
      const participantId = button.id.split("-", 1)[0];
      const URLdata = { id: participantId };
      const query = new URLSearchParams(URLdata).toString();
      window.location.href = "/minute_level?" + query;
    });
  });

  // age event listener
  const ageElements = document.querySelectorAll(".age");
  ageElements.forEach((ele) => {
    const id = ele.id.split("-")[0];
    ele.addEventListener("change", (e) => {
      const age = e.target.value;
      sendAgeWeight(id, age, "age");
      calculateHeartRate(id, age);
    });
  });

  // weight event listener
  const weightElements = document.querySelectorAll(".weight");
  weightElements.forEach((ele) => {
    const id = ele.id.split("-")[0];
    ele.addEventListener("change", (e) => {
      const weight = e.target.value;
      sendAgeWeight(id, weight, "weight");
    });
  });
}
async function sendAgeWeight(id, data, type) {
  try {
    const res = await fetch("/ageweight", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        participantid: id,
        type: type,
        data: data,
      }),
    });
    console.log(res);
  } catch (error) {
    console.log("error", error);
  }
}

// Gets the participant information that will be displayed on the dashboard and returns it in an object
// Each number that needs to be calculated will be stored in an html element
async function getParticipantInformation(json, id) {
  const participantInfo = {
    "Participant ID": getId(id),
    "Minute Level Data": createDownloadButton(),
    Age: createInput(),
    Weight: createInput(),
    "Start Date": getStartTime(json, id),
    "End Date": getEndTime(json, id),
    "HR Peak": getMaxHeartRate(),
    "Current Weather": await getCurrentWeather(id),
  };
  return participantInfo;
}
function sortDataByDate(json) {
  const participants = Object.keys(json);
  participants.forEach((id) => {
    json[id].sort((a, b) => Date.parse(a.time.split(" ")[0]) - Date.parse(b.time.split(" ")[0]));
  });
}
async function getCurrentWeather(id) {
  const locationString = data[id][data[id].length - 1].location;
  let [long, lat] = locationString.split(" ");
  long = parseFloat(long);
  lat = parseFloat(lat);
  const pointResponse = await fetch(`https://api.weather.gov/points/${long},${lat}`);
  const pointInfo = await pointResponse.json();
  const foreCastLink = pointInfo.properties.forecastHourly;
  const weatherResponse = await fetch(foreCastLink);
  const weatherData = await weatherResponse.json();
  const weatherInfo = weatherData.properties.periods[0];
  const temp = weatherInfo.temperature;
  const precipitation = weatherInfo.probabilityOfPrecipitation.value;
  const wind = weatherInfo.windSpeed;
  const humidity = weatherInfo.relativeHumidity.value;
  const container = document.createElement("div");
  container.innerHTML = `
  <div>Temp: ${temp} deg F</div>
  <div>Precipitation: ${precipitation}%</div>
  <div>Wind: ${wind}</div>
  <div>Humidity: ${humidity}</div>
  `;
  return container;
}
function createDownloadButton() {
  const button = document.createElement("button");
  button.innerText = "Minute level data";
  return button;
}
function getMaxHeartRate() {
  const ageElement = document.createElement("div");
  return ageElement;
}
function calculateHeartRate(id, age) {
  const ageInput = document.querySelector(`#${id}-hr-peak`);
  const maxHr = 210 - 0.56 * age - 15.5;
  const roundedHr = Math.round(maxHr * 100) / 100;
  ageInput.innerText = roundedHr;
}
function getId(id) {
  const idElement = document.createElement("div");
  idElement.innerText = id.replace(/^\w/, (char) => char.toUpperCase());
  return idElement;
}
function createInput() {
  const inputBox = document.createElement("input");
  inputBox.setAttribute("type", "number");
  return inputBox;
}

function getStartTime(json, id) {
  const dates = json[id].map((obj) => obj.time.split(" ")[0]);
  const parseDates = dates.map((date) => Date.parse(date));
  const startTimestamp = Math.min(...parseDates);
  const startDate = new Date(startTimestamp).toISOString().split("T")[0];
  const startDateElement = document.createElement("div");
  startDateElement.innerText = startDate;
  return startDateElement;
}
function getEndTime(json, id) {
  const dates = json[id].map((obj) => obj.time.split(" ")[0]);
  const parseDates = dates.map((date) => Date.parse(date));
  const endTimestamp = Math.max(...parseDates);
  const endDate = new Date(endTimestamp).toISOString().split("T")[0];
  const endDateElement = document.createElement("div");
  endDateElement.innerText = endDate;
  return endDateElement;
}
// function convertSingleParticipantJSONtoCSV(jsonData) {
//   const { _id, ...dataWithoutId } = jsonData[0];
//   const headers = Object.keys(dataWithoutId);
//   const csvHeaders = headers.join(",");

//   const csvRows = jsonData.map((row) => {
//     return headers
//       .map((header) => {
//         let cellData = row[header];

//         return cellData;
//       })
//       .join(",");
//   });
//   const csvContent = `${csvHeaders}\n${csvRows.join("\n")}`;

//   return csvContent;
// }
// function downloadCsv(id, csvString) {
//   const blob = new Blob([csvString], { type: "text/csv" });
//   const link = document.createElement("a");

//   const url = URL.createObjectURL(blob);
//   link.setAttribute("href", url);
//   link.setAttribute("download", `${id}-minute-level.csv`);

//   document.body.appendChild(link);
//   link.click();

//   URL.revokeObjectURL(url);
//   document.body.removeChild(link);
// }
