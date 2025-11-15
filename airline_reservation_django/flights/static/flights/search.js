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
    .then(data => {
      const select = document.getElementById("origin_country");
      data.forEach(country => {
        const opt = document.createElement("option");
        opt.value = country;
        opt.textContent = country;
        select.appendChild(opt);
      });
    });

  document.getElementById("origin_country").addEventListener("change", function () {
    const airportSelect = document.getElementById("origin_airport");
    airportSelect.disabled = true;
    airportSelect.innerHTML = '<option>Loading...</option>';

    fetch(`/ajax/airports/?country=${encodeURIComponent(this.value)}`)
      .then(res => res.json())
      .then(data => {
        airportSelect.innerHTML = '<option value="">-- Select airport --</option>';
        data.forEach(a => {
          const opt = document.createElement("option");
          opt.value = a;
          opt.textContent = a;
          airportSelect.appendChild(opt);
        });
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
        destSelect.innerHTML = '<option value="">-- Select country --</option>';
        data.forEach(c => {
          const opt = document.createElement("option");
          opt.value = c;
          opt.textContent = c;
          destSelect.appendChild(opt);
        });
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
        airportSelect.innerHTML = '<option value="">-- Select airport --</option>';
        data.forEach(a => {
          const opt = document.createElement("option");
          opt.value = a;
          opt.textContent = a;
          airportSelect.appendChild(opt);
        });
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

    if (this.value === "round") {
      retDate.style.display = "inline-block";
      retLabel.style.display = "inline-block";
    } else {
      retDate.style.display = "none";
      retLabel.style.display = "none";
      retDate.value = "";
    }
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
