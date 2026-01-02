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
        document.getElementById("loading-overlay").style.display = "flex";

        return actions.order.capture().then(function(details) {
            fetch("", {  
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
                    window.location.href = BOOK_SUCCESS_URL;

                } else if (result.status === "seat_taken") {
                    alert(`⚠️ Seat ${result.seat} was just taken by someone else! Please choose another seat.`);
                    window.location.href = `/book/${FLIGHT_ID}/step3/`;

                } else {
                    alert("❌ Error: " + (result.msg || "An unexpected error occurred."));
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