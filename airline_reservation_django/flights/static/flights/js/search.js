function populateSelect(selectId, options, defaultText = "-- Select --") {
  const select = document.getElementById(selectId);
  select.innerHTML = `<option value="">${defaultText}</option>`;
  options.forEach(opt => {
    const option = document.createElement("option");
    option.value = opt;
    option.textContent = opt;
    select.appendChild(option);
  });
}

document.addEventListener("DOMContentLoaded", function () {
  const depPicker = flatpickr("#departure_date", {
    dateFormat: "Y-m-d",
    minDate: "today",
    enable: []
  });

  const retPicker = flatpickr("#return_date", {
    dateFormat: "Y-m-d",
    minDate: "today",
    enable: []
  });

  fetch("/ajax/origin_countries/")
    .then(res => res.json())
    .then(data => populateSelect("origin_country", data));

  document.getElementById("origin_country").addEventListener("change", function () {
    const airportSelect = document.getElementById("origin_airport");
    airportSelect.disabled = true;
    airportSelect.innerHTML = '<option>Loading...</option>';

    fetch(`/ajax/airports/?country=${encodeURIComponent(this.value)}`)
      .then(res => res.json())
      .then(data => {
        populateSelect("origin_airport", data, "-- Select airport --");
        airportSelect.disabled = false;
      });
  });

  document.getElementById("origin_airport").addEventListener("change", function () {
    const origin_country = document.getElementById("origin_country").value;
    const city = this.value;
    const destSelect = document.getElementById("dest_country");

    destSelect.disabled = true;
    destSelect.innerHTML = '<option>Loading...</option>';

    fetch(`/ajax/dest_countries/?origin_country=${encodeURIComponent(origin_country)}&origin_city=${encodeURIComponent(city)}`)
      .then(res => res.json())
      .then(data => {
        populateSelect("dest_country", data, "-- Select country --");
        destSelect.disabled = false;
      });
  });

  document.getElementById("dest_country").addEventListener("change", function () {
    const origin_country = document.getElementById("origin_country").value;
    const origin_city = document.getElementById("origin_airport").value;
    const dest_country = this.value;
    const airportSelect = document.getElementById("dest_airport");

    airportSelect.disabled = true;
    airportSelect.innerHTML = '<option>Loading...</option>';

    fetch(`/ajax/dest_airports/?origin_country=${encodeURIComponent(origin_country)}&origin_city=${encodeURIComponent(origin_city)}&dest_country=${encodeURIComponent(dest_country)}`)
      .then(res => res.json())
      .then(data => {
        populateSelect("dest_airport", data, "-- Select airport --");
        airportSelect.disabled = false;
      });
  });

  document.getElementById("dest_airport").addEventListener("change", function () {
    const dep = document.getElementById("origin_airport").value;
    const arr = this.value;

    if (!dep || !arr) return;

    fetch(`/ajax/available_dates/?type=departure&departure_city=${encodeURIComponent(dep)}&arrival_city=${encodeURIComponent(arr)}`)
      .then(res => res.json())
      .then(data => depPicker.set("enable", data));

    fetch(`/ajax/available_dates/?type=return&departure_city=${encodeURIComponent(dep)}&arrival_city=${encodeURIComponent(arr)}`)
      .then(res => res.json())
      .then(data => retPicker.set("enable", data));
  });

  document.getElementById("trip_type").addEventListener("change", function () {
    const retDate = document.getElementById("return_date");
    const retLabel = document.getElementById("return_label");
    const isRound = this.value === "round";

    retDate.style.display = retLabel.style.display = isRound ? "inline-block" : "none";
    if (!isRound) retDate.value = "";
  });

  document.getElementById("searchBtn").addEventListener("click", function () {
    sessionStorage.setItem("trip_type", document.getElementById("trip_type").value);

    const dep = document.getElementById("origin_airport").value;
    const arr = document.getElementById("dest_airport").value;
    const depDate = document.getElementById("departure_date").value;
    const retDate = document.getElementById("return_date").value;
    const tripType = document.getElementById("trip_type").value;

    if (!dep || !arr) {
      alert("Please select both origin and destination airports.");
      return;
    }

    let url = `/flights/?departure_city=${encodeURIComponent(dep)}&arrival_city=${encodeURIComponent(arr)}`;
    if (depDate) url += `&departure_date=${encodeURIComponent(depDate)}`;
    if (tripType === "round" && retDate) url += `&return_date=${encodeURIComponent(retDate)}`;
    window.location.href = url;
  });
});

function handleFlightSelection(e) {
  e.preventDefault();
  const dep = document.querySelector('input[name="departure_flight"]:checked');
  const ret = document.querySelector('input[name="return_flight"]:checked');
  const pax = document.getElementById("num_passengers").value || 1;
  const tripType = sessionStorage.getItem("trip_type") || "oneway";

  if (!dep) {
    alert("Please select a departure flight.");
    return false;
  }
  if (tripType === "round" && !ret) {
    alert("Please select a return flight.");
    return false;
  }

  let url = `/book/${dep.value}/step1/?pax=${pax}`;
  if (tripType === "round" && ret) url += `&return_id=${ret.value}`;
  window.location.href = url;
  return false;
}
