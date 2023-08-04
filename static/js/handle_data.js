const pathName = window.location.pathname.split("/")[1];
const form = document.querySelector("form");

window.onload = () => {
  const url = window.location.search;
  const params = new URLSearchParams(url);
  let id = params.get("id");
  if (!id) {
    id = "all";
  }
  fetchAndUpdateTable(id);
  const participantDropdown = document.querySelector("#participants");
  participantDropdown.value = id;
  const tableContainer = document.querySelector("#table-container");
  const button = tableContainer.querySelector("button");
  button.addEventListener("click", () => {
    downloadCsv();
  });
};

form.addEventListener("submit", (e) => {
  e.preventDefault();
  const form = e.target;
  const participant = form.querySelector("#participants").value;
  const startDate = form.querySelector("#start_date").value;
  const endDate = form.querySelector("#end_date").value;
  fetchAndUpdateTable(participant, startDate, endDate);
});

async function fetchAndUpdateTable(id, start = undefined, end = undefined) {
  try {
    const res = await fetch(`/${pathName}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ participant: id, start_date: start, end_date: end }),
    });
    const data = await res.text();
    console.log('DONE');
    const dataContainer = document.querySelector("#data-container");
    dataContainer.innerHTML = data;
    const firstHeader = document.querySelector("thead > tr > th");
    firstHeader.innerText = "Participant Id";
    console.log('Done 2');
  } catch (error) {
    console.log("Error: ", error);
  }
  // countData();
}
function countData() {
  const enmos = document.querySelectorAll(".enmo");
  let count = 0
  enmos.forEach(() => {
    count++
  });
  console.log(count)
}
// function formatXYZ() {
//   const xyzs = document.querySelectorAll(".accelerometery");
//   xyzs.forEach((xyz) => {
//     const parent = xyz.parentNode;
//     const cl = xyz.className;
//     const vals = xyz.innerText.split(" ");
//     for (let i = 0; i < vals.length; i++) {
//       vals[i] = vals[i].split(":")[1];
//     }
//     const y = document.createElement("td");
//     const z = document.createElement("td");
//     y.classList.add(cl);
//     z.classList.add(cl);
//     xyz.innerText = vals[0];
//     y.innerText = vals[1];
//     z.innerText = vals[2];
//     parent.insertBefore(y, xyz.nextSibling);
//     parent.insertBefore(z, y.nextSibling);
//   });
// }
// function updateENMOColors() {
//   const enmos = document.querySelectorAll(".enmo");
//   let count = 0
//   enmos.forEach((enmo) => {
//     count++
//
//     const val = enmo.textContent;
//     if (val === "0") {
//       enmo.classList.add("zero");
//     } else if (val < 35.6) {
//       enmo.classList.add("sedentary");
//     } else if (val < 201.4) {
//       enmo.classList.add("light");
//     } else if (val < 707) {
//       enmo.classList.add("moderate");
//     } else {
//       enmo.classList.add("vigorous");
//     }
//   });
//   console.log(count)
// }
function downloadCsv() {
  const id = document.querySelector("#participants").value;
  const csvString = getCsvString();
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
function getCsvString() {
  const table = document.querySelector("table");
  const rows = Array.from(table.querySelectorAll("tr"));

  return rows
    .map((row) => {
      const cells = Array.from(row.querySelectorAll("th,td"));
      return cells.map((cell) => cell.innerText).join(",");
    })
    .join("\n");
}
