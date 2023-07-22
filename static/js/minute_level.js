const form = document.querySelector("form");

window.onload = () => {
  const url = window.location.search;
  const params = new URLSearchParams(url);
  const id = params.get("id");
  console.log(id);
  fetch("/minute_level", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      participant: id,
    }),
  })
    .then((res) => res.text())
    .then((data) => {
      console.log(data);
      const tableContainer = document.querySelector("#table-container");
      tableContainer.innerHTML = data;
    });
};

form.addEventListener("submit", (e) => {
  e.preventDefault();
  const form = e.target;
  const participant = form.querySelector("#participants").value;
  const startDate = form.querySelector("#start_date").value;
  const endDate = form.querySelector("#end_date").value;
  fetch("/minute_level", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      participant: participant,
      start_date: startDate,
      end_date: endDate,
    }),
  })
    .then((res) => res.text())
    .then((data) => {
      const tableContainer = document.querySelector("#table-container");
      tableContainer.innerHTML = data;
    });
});
