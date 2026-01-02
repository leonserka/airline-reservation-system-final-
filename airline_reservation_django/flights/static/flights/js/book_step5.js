// Dohvati CSRF token (za svaki slučaj, ako nije definiran u HTML-u)
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

const csrftoken = getCookie('csrftoken') || CSRF_TOKEN;

paypal.Buttons({
    style: {
        color: 'gold',
        shape: 'rect',
        label: 'paypal',
        layout: 'vertical'
    },

    createOrder: function(data, actions) {
        return actions.order.create({
            purchase_units: [{
                description: 'Flight booking - Airline Reservation System',
                amount: { value: TOTAL_PRICE }
            }]
        });
    },

    onApprove: function(data, actions) {
        // Prikaži loading overlay dok se obrađuje
        document.getElementById("loading-overlay").style.display = "flex";

        return actions.order.capture().then(function(details) {
            fetch("", {  // Šalje na trenutni URL (book_step5)
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": csrftoken
                },
                body: JSON.stringify({
                    orderID: data.orderID,
                    payment_status: "COMPLETED",
                    details: details
                })
            })
            .then(response => response.json())
            .then(result => {
                document.getElementById("loading-overlay").style.display = "none";

                if (result.status === "ok") {
                    // USPJEH: Preusmjeri na stranicu potvrde
                    // alert("✅ Payment completed by " + details.payer.name.given_name); // Možeš maknuti alert ako želiš brži prijelaz
                    window.location.href = BOOK_SUCCESS_URL;

                } else if (result.status === "seat_taken") {
                    // GREŠKA: Sjedalo zauzeto
                    alert(`⚠️ Seat ${result.seat} was just taken by someone else! Please choose another seat.`);
                    window.location.href = `/book/${FLIGHT_ID}/step3/`;

                } else {
                    // OSTALE GREŠKE
                    alert("❌ Error: " + (result.msg || "An unexpected error occurred."));
                    // Ako je greška kritična, možda je bolje vratiti na početak ili step3
                    window.location.href = `/book/${FLIGHT_ID}/step3/`;
                }
            })
            .catch(err => {
                document.getElementById("loading-overlay").style.display = "none";
                console.error("Fetch Error:", err);
                alert("Network error occurred. Please try again or contact support.");
            });
        });
    },

    onCancel: function () {
        alert('Payment cancelled.');
    },

    onError: function (err) {
        console.error('PayPal Error:', err);
        alert('An error occurred with PayPal. Please try again.');
    }

}).render('#paypal-button-container');