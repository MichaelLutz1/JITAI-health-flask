const pathName = window.location.pathname.split("/")[1];
const form = document.querySelector("form");
let offset = 0
let page = 1

window.onload = () => {
  const url = window.location.search;
  const params = new URLSearchParams(url);
  let id = params.get("id");
  if (!id) {
    id = "all";
  }
  fetchAndUpdateTable(id, undefined, undefined, true);
  const participantDropdown = document.querySelector("#participants");
  participantDropdown.value = id;
  const tableContainer = document.querySelector("#table-container");
  const button = tableContainer.querySelector("button");
  button.addEventListener("click", () => {
    downloadCsv();
  });
};

const leftArrow = document.querySelector('.left-arrow')
leftArrow.addEventListener('click', () => {
  changeOffset(-10);
})
const rightArrow = document.querySelector('.right-arrow')
rightArrow.addEventListener('click', () => {
  changeOffset(10);
})
function changeOffset(amount) {
  offset += amount
  const numRows = document.querySelector('.num-rows');
  if (offset < 0) {
    offset = 0
    return
  }
  if (offset >= numRows.innerText) {
    offset -= amount
    return
  }
  amount < 0 ? page-- : page++
  const form = document.querySelector('#form');
  const participant = form.querySelector("#participants").value;
  const startDate = form.querySelector("#start_date").value;
  const endDate = form.querySelector("#end_date").value;
  const pageNumber = document.querySelector('.curr-page');
  pageNumber.innerText = page
  fetchAndUpdateTable(participant, startDate, endDate, false);
}


form.addEventListener("submit", (e) => {
  e.preventDefault();
  const form = e.target;
  const participant = form.querySelector("#participants").value;
  const startDate = form.querySelector("#start_date").value;
  const endDate = form.querySelector("#end_date").value;
  offset = 0
  fetchAndUpdateTable(participant, startDate, endDate, true);
});

async function fetchAndUpdateTable(id, start = undefined, end = undefined, shouldReloadNumRows) {
  try {
    const res = await fetch(`/${pathName}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ participant: id, start_date: start, end_date: end, offset: offset }),
    });
    const data = await res.text();
    const dataContainer = document.querySelector("#data-container");
    dataContainer.innerHTML = data;
    const firstHeader = document.querySelector("thead > tr > th");
    firstHeader.innerText = "Participant Id";
    if (shouldReloadNumRows) {
      const numRows = dataContainer.querySelector('.num-rows').innerText;
      const numPagesElement = document.querySelector('.num-pages')
      const overflow = numRows % 10
      const numPages = Math.floor(numRows / 10)
      numPagesElement.innerText = numPages + (overflow > 0 ? 1 : 0)
      page = 1
      const pageNumber = document.querySelector('.curr-page');
      pageNumber.innerText = page
    }
  } catch (error) {
    console.log("Error: ", error);
  }
  // countData();
  formatXYZ();
}

function formatXYZ() {
  const xyzs = document.querySelectorAll(".acceleration");
  xyzs.forEach((xyz) => {
    const parent = xyz.parentNode;
    const cl = xyz.className;
    const vals = xyz.innerText.split(" ");
    for (let i = 0; i < vals.length; i++) {
      vals[i] = vals[i].split(":")[1];
    }
    const y = document.createElement("td");
    const z = document.createElement("td");
    y.classList.add(cl);
    z.classList.add(cl);
    xyz.innerText = vals[0];
    y.innerText = vals[1];
    z.innerText = vals[2];
    parent.insertBefore(y, xyz.nextSibling);
    parent.insertBefore(z, y.nextSibling);
  });
}

function countData() {
  const enmos = document.querySelectorAll(".enmo");
  let count = 0
  enmos.forEach(() => {
    count++
  });
}
async function downloadCsv() {
  const id = document.querySelector("#participants").value;
  const csvString = await getCsvString(id);
  const blob = new Blob([csvString], { type: "text/csv" });
  const link = document.createElement("a");
  const url = URL.createObjectURL(blob);
  link.setAttribute("href", url);
  link.setAttribute("download", `${id}_${pathName}.csv`);

  document.body.appendChild(link);
  link.click();

  URL.revokeObjectURL(url);
  document.body.removeChild(link);
}
async function getCsvString(id) {
  const res = await fetch(`/api/processed_data?id=${id}&path=${pathName}`)
  const data = await res.json()
  const rows = []
  headers = Object.keys(data[0])
  rows.push(headers.join(','))
  data.forEach(obj => {
    const values = headers.map(header => {
      if (header === 'weather' && obj[header]) {
        return 'Temp: ' + obj[header]['temp'] + ' Precipitation: ' + obj[header]['precipitation'] + ' Wind: ' + obj[header]['wind'] + ' Humidity: ' + obj[header]['humidity']
      }
      return obj[header]
    });
    rows.push(values.join(','));
  });
  return rows.join('\n')
}
