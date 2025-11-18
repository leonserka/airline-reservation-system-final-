document.addEventListener("DOMContentLoaded", () => {
    const fromInput = document.getElementById("fromInput");
    const toInput = document.getElementById("toInput");
    const fromDropdown = document.getElementById("fromDropdown");
    const toDropdown = document.getElementById("toDropdown");
    let selectedFrom = { country: null, city: null };
    let selectedTo = { country: null, city: null };
    const departPicker = flatpickr("#departDate", {
        dateFormat: "Y-m-d",
        minDate: "today",
        enable: []
    });

    const returnPicker = flatpickr("#returnDate", {
        dateFormat: "Y-m-d",
        minDate: "today",
        enable: []
    });

    const tripRadios = document.querySelectorAll('input[name="tripType"]');
    const returnBox = document.getElementById("returnDate");

    tripRadios.forEach(r => {
        r.addEventListener("change", () => {
            if (r.value === "round") {
                returnBox.parentElement.style.display = "block";
            } else {
                returnBox.parentElement.style.display = "none";
                returnBox.value = "";
            }
        });
    });

    function loadAvailableDates() {
        if (!selectedFrom.city || !selectedTo.city) return;

        fetch(`/ajax/available_dates/?type=departure&departure_city=${encodeURIComponent(selectedFrom.city)}&arrival_city=${encodeURIComponent(selectedTo.city)}`)
            .then(res => res.json())
            .then(dates => departPicker.set("enable", dates));

        fetch(`/ajax/available_dates/?type=return&departure_city=${encodeURIComponent(selectedFrom.city)}&arrival_city=${encodeURIComponent(selectedTo.city)}`)
            .then(res => res.json())
            .then(dates => returnPicker.set("enable", dates));
    }

    function checkLoginBeforeOpen() {
        if (!window.isLogged) {
            alert("You must be logged in to select flights.");
            const loginBox = document.getElementById("loginDropdown");
            loginBox.classList.add("show");
            return false;
        }
        return true;
    }

    function loadOriginCountries(panel, callback) {
        fetch("/ajax/origin_countries/")
            .then(res => res.json())
            .then(countries => {

                panel.innerHTML = `
                    <div class="dropdown-columns">
                        <div class="country-list" id="countryCol"></div>
                        <div class="airport-list" id="airportCol">Select a country →</div>
                    </div>
                `;

                const col = panel.querySelector("#countryCol");

                countries.forEach(c => {
                    const div = document.createElement("div");
                    div.className = "country-item";
                    div.textContent = c;
                    div.onclick = () => callback(c, panel);
                    col.appendChild(div);
                });
            });
    }

    function loadOriginAirports(country, panel, callback) {
        const col = panel.querySelector("#airportCol");
        col.innerHTML = "Loading...";

        fetch(`/ajax/airports/?country=${encodeURIComponent(country)}`)
            .then(res => res.json())
            .then(airports => {
                col.innerHTML = "";
                airports.forEach(a => {
                    const div = document.createElement("div");
                    div.className = "airport-item";
                    div.textContent = a;
                    div.onclick = () => callback(a);
                    col.appendChild(div);
                });
            });
    }

    function loadDestCountries(panel, callback) {

        if (!selectedFrom.country || !selectedFrom.city) {
            panel.innerHTML = "Select origin first!";
            return;
        }

        fetch(`/ajax/dest_countries/?origin_country=${encodeURIComponent(selectedFrom.country)}&origin_city=${encodeURIComponent(selectedFrom.city)}`)
            .then(res => res.json())
            .then(countries => {

                panel.innerHTML = `
                    <div class="dropdown-columns">
                        <div class="country-list" id="destCountryCol"></div>
                        <div class="airport-list" id="destAirportCol">Select a country →</div>
                    </div>
                `;

                const col = panel.querySelector("#destCountryCol");
                countries.forEach(c => {
                    const div = document.createElement("div");
                    div.className = "country-item";
                    div.textContent = c;
                    div.onclick = () => callback(c, panel);
                    col.appendChild(div);
                });
            });
    }

    function loadDestAirports(country, panel, callback) {
        const col = panel.querySelector("#destAirportCol");
        col.innerHTML = "Loading...";

        fetch(`/ajax/dest_airports/?origin_country=${encodeURIComponent(selectedFrom.country)}&origin_city=${encodeURIComponent(selectedFrom.city)}&dest_country=${encodeURIComponent(country)}`)
            .then(res => res.json())
            .then(airports => {
                col.innerHTML = "";

                airports.forEach(a => {
                    const div = document.createElement("div");
                    div.className = "airport-item";
                    div.textContent = a;
                    div.onclick = () => callback(a);
                    col.appendChild(div);
                });
            });
    }

    fromInput.onclick = () => {
        if (!checkLoginBeforeOpen()) return;

        toDropdown.classList.remove("show");
        fromDropdown.classList.toggle("show");

        loadOriginCountries(fromDropdown, (country, panel) => {
            loadOriginAirports(country, panel, city => {
                selectedFrom = { country, city };
                fromInput.value = `${city}, ${country}`;
                fromDropdown.classList.remove("show");
                loadAvailableDates();
            });
        });
    };

    toInput.onclick = () => {
        if (!checkLoginBeforeOpen()) return;

        fromDropdown.classList.remove("show");
        toDropdown.classList.toggle("show");

        loadDestCountries(toDropdown, (country, panel) => {
            loadDestAirports(country, panel, city => {
                selectedTo = { country, city };
                toInput.value = `${city}, ${country}`;
                toDropdown.classList.remove("show");
                loadAvailableDates();
            });
        });
    };

    document.getElementById("homeSearchBtn").onclick = () => {

        if (!window.isLogged) {
            alert("You must be logged in to search flights.");
            const loginBox = document.getElementById("loginDropdown");
            loginBox.classList.add("show");
            return;
        }

        if (!selectedFrom.city || !selectedTo.city) {
            alert("Please select both origin and destination.");
            return;
        }

        const tripType = document.querySelector('input[name="tripType"]:checked').value;
        let url = `/flights/?departure_city=${encodeURIComponent(selectedFrom.city)}&arrival_city=${encodeURIComponent(selectedTo.city)}`;
        const dep = document.getElementById("departDate").value;
        const ret = document.getElementById("returnDate").value;

        if (dep) url += `&departure_date=${dep}`;
        if (tripType === "round" && ret) url += `&return_date=${ret}`;

        sessionStorage.setItem("trip_type", tripType);

        window.location.href = url;
    };

});
