document.addEventListener("DOMContentLoaded", function () {
    // ✅ Initialize AOS animations
    if (typeof AOS !== "undefined") {
        AOS.init();
    }

    // ✅ ATS Score Animation
    const scoreElement = document.getElementById("ats-score2");
    if (scoreElement) {
        const finalScore = parseInt(scoreElement.getAttribute("data-score"), 10);
        let currentScore = 0;
        const duration = 1500;
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

    // ✅ Scroll animations
    const atsBox = document.getElementById("ats_score");
    if (atsBox) {
        atsBox.scrollIntoView({ behavior: "smooth", block: "start" });
        setTimeout(() => atsBox.classList.add("show"), 500);
    }

    const suggestionsBox = document.getElementById("suggestions-section");
    if (suggestionsBox) {
        suggestionsBox.scrollIntoView({ behavior: "smooth", block: "start" });
        setTimeout(() => suggestionsBox.classList.add("show"), 500);
    }

    // ✅ Loader on form submit
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


document.addEventListener("DOMContentLoaded", () => {
  const menuToggle = document.getElementById("menu-toggle");
  const navLinks = document.getElementById("nav-links");

  if (!menuToggle || !navLinks) return;

  menuToggle.addEventListener("click", (e) => {
    e.stopPropagation();
    navLinks.classList.toggle("active");
  });

  // Close nav when clicking outside
  document.addEventListener("click", (e) => {
    if (!navLinks.contains(e.target) && !menuToggle.contains(e.target)) {
      navLinks.classList.remove("active");
    }
  });
});

const overlay = document.getElementById("loading-overlay");
const btn = document.getElementById("start-btn");

btn.addEventListener("click", () => {
  overlay.style.display = "flex"; // Show overlay
  // Simulate resume analysis
  setTimeout(() => {
    overlay.style.display = "none"; // Hide overlay after 3s
    alert("Resume analysis complete!");
  }, 3000);
});