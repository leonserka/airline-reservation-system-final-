document.addEventListener("DOMContentLoaded", function () {
    const btn = document.getElementById("loginDropdownBtn");
    const box = document.getElementById("loginDropdown");
    const close = document.getElementById("closeLoginDropdown");

    if (btn) {
        btn.addEventListener("click", () => {
            box.classList.toggle("hidden");
        });
    }

    if (close) {
        close.addEventListener("click", () => {
            box.classList.add("hidden");
        });
    }

    document.addEventListener("click", function (e) {
        if (box && !box.contains(e.target) && e.target !== btn) {
            box.classList.add("hidden");
        }
    });
});
