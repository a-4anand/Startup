document.getElementById("menu-toggle").addEventListener("click", function () {
    document.getElementById("nav-links").classList.toggle("show");
});


AOS.init();

src = "https://cdn.jsdelivr.net/npm/aos@2.3.4/dist/aos.js"

document.getElementById("menu-toggle").addEventListener("click", function () {
    document.getElementById("nav-links").classList.toggle("show");
});


document.addEventListener("DOMContentLoaded", function () {
    const scoreElement = document.getElementById("ats-score2");

    if (scoreElement) {
        const finalScore = parseInt(scoreElement.getAttribute("data-score"), 10);
        let currentScore = 0;
        const duration = 1500; // animation time in ms
        const increment = finalScore / (duration / 30);

        const timer = setInterval(() => {
            currentScore += increment;
            if (currentScore >= finalScore) {
                currentScore = finalScore;
                clearInterval(timer);
            }
            scoreElement.textContent = Math.floor(currentScore) + "/100";
        }, 30);
    }
});

document.addEventListener("DOMContentLoaded", function () {
    const suggestionsBox = document.getElementById("ats_score");
    if (suggestionsBox) {
        suggestionsBox.scrollIntoView({
            behavior: "smooth",
            block: "start"
        });

        // Small delay so scroll happens first, then animation
        setTimeout(() => {
            suggestionsBox.classList.add("show");
        }, 500);
    }
});

document.addEventListener("DOMContentLoaded", function () {
    const suggestionsBox = document.getElementById("suggestions-section");
    if (suggestionsBox) {
        suggestionsBox.scrollIntoView({
            behavior: "smooth",
            block: "start"
        });

        // Small delay so scroll happens first, then animation
        setTimeout(() => {
            suggestionsBox.classList.add("show");
        }, 500);
    }
});
document.addEventListener("DOMContentLoaded", function () {
    const forms = document.querySelectorAll("form");
    const loader = document.getElementById("loading-overlay");

    forms.forEach(form => {
        form.addEventListener("submit", function () {
            loader.style.display = "flex";
        });
    });
});

