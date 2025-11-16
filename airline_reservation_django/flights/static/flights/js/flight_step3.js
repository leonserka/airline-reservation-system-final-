document.addEventListener("DOMContentLoaded", function () {
    const seats = document.querySelectorAll('.seat');
    const form = document.forms[0];
    const input = document.getElementById('selected_seat_input');

    if (!seats.length || !form || !input) return;

    seats.forEach(seat => {
        seat.addEventListener('click', function () {
            if (seat.classList.contains('occupied')) return;
            seats.forEach(s => !s.classList.contains('occupied') && s.classList.remove('selected'));
            seat.classList.add('selected');
            input.value = seat.dataset.seat;

            if (!form.classList.contains('submitting')) {
                form.classList.add('submitting');
                form.submit();
            }
        });
    });
});
