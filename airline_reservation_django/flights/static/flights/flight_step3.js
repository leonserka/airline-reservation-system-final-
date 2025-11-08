document.addEventListener("DOMContentLoaded", function () {
    const seats = document.querySelectorAll('.seat');
    const input = document.getElementById('selected_seat_input');

    seats.forEach(seat => {
        seat.addEventListener('click', function () {

            // Ne možeš kliknuti zauzeto
            if (seat.classList.contains('occupied')) return;

            // Samo vizualno makni selekciju svima
            seats.forEach(s => {
                if (!s.classList.contains('occupied')) {
                    s.classList.remove('selected');
                }
            });

            seat.classList.add('selected');

            // Stavi seat ID u hidden input
            input.value = seat.dataset.seat;

            // Submit forme
            document.forms[0].submit();
        });
    });
});
