// Initialize AOS after DOM load
document.addEventListener("DOMContentLoaded", function () {

    // Initialize AOS animations
    AOS.init();

    // Menu toggle
    const menuToggle = document.getElementById("menu-toggle");
    const navLinks = document.getElementById("nav-links");
    if (menuToggle && navLinks) {
        menuToggle.addEventListener("click", () => {
            navLinks.classList.toggle("show");
        });
    }

    // ATS Score Animation
    const scoreElement = document.getElementById("ats-score2");
    if (scoreElement) {
        const finalScore = parseInt(scoreElement.getAttribute("data-score"), 10);
        let currentScore = 0;
        const duration = 1500; // ms
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

    // Scroll to ATS score
    const atsBox = document.getElementById("ats_score");
    if (atsBox) {
        atsBox.scrollIntoView({ behavior: "smooth", block: "start" });
        setTimeout(() => atsBox.classList.add("show"), 500);
    }

    // Scroll to suggestions
    const suggestionsBox = document.getElementById("suggestions-section");
    if (suggestionsBox) {
        suggestionsBox.scrollIntoView({ behavior: "smooth", block: "start" });
        setTimeout(() => suggestionsBox.classList.add("show"), 500);
    }

    // Loader on form submit
    const forms = document.querySelectorAll("form");
    const loader = document.getElementById("loading-overlay");
    if (loader) {
        forms.forEach(form => {
            form.addEventListener("submit", () => {
                loader.style.display = "flex";
            });
        });
    }
});
