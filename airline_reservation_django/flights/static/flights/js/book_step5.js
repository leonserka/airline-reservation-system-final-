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
        document.getElementById("loading-overlay").style.display = "flex";

        return actions.order.capture().then(function(details) {
            fetch("", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": CSRF_TOKEN
                },
                body: JSON.stringify({
                    orderID: data.orderID,
                    details: details
                })
            })
            .then(response => response.json())
            .then(result => {
                document.getElementById("loading-overlay").style.display = "none";

                if (result.status === "ok") {
                    alert("✅ Payment completed by " + details.payer.name.given_name);
                    window.location.href = BOOK_SUCCESS_URL;

                } else if (result.status === "seat_taken") {
                    alert(`Seat ${result.seat} is no longer available. Please choose another seat.`);
                    window.location.href = `/book/${FLIGHT_ID}/step3/`;

                } else {
                    alert("❌ Error saving your booking. Please choose your seats again.");
                    window.location.href = `/book/${FLIGHT_ID}/step3/`;
                }
            })
            .catch(err => {
                document.getElementById("loading-overlay").style.display = "none";
                console.error(err);
                alert("Unexpected error occurred. Redirecting to seat selection.");
                window.location.href = `/book/${FLIGHT_ID}/step3/`;
            });
        });
    },

    onCancel: function () {
        alert('❌ Payment cancelled.');
        window.location.href = `/book/${FLIGHT_ID}/step3/`; 
    },

    onError: function (err) {
        console.error('PayPal Error:', err);
        alert('An error occurred while processing your payment. Redirecting to seat selection.');
        window.location.href = `/book/${FLIGHT_ID}/step3/`;
    }

}).render('#paypal-button-container');
