document.addEventListener("DOMContentLoaded", function () {
    let slides = document.querySelectorAll(".slide");
    let current = 0;

    function showSlide(i) {
        slides[current].classList.remove("active");
        current = (i + slides.length) % slides.length;
        slides[current].classList.add("active");
    }

    document.getElementById("nextSlide").addEventListener("click", () => {
        showSlide(current + 1);
    });

    document.getElementById("prevSlide").addEventListener("click", () => {
        showSlide(current - 1);
    });

    setInterval(() => {
        showSlide(current + 1);
    }, 10000);
});
