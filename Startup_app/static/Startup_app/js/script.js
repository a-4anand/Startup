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

// Loader on form submit
const forms = document.querySelectorAll("form");
const loader = document.getElementById("loading-overlay");

if (loader && forms.length > 0) {
    forms.forEach(form => {
        form.addEventListener("submit", () => {
            // Add the 'visible' class to trigger the CSS transition
            loader.classList.add("visible");
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


src="https://checkout.razorpay.com/v1/checkout.js"

const paymentButton = document.getElementById('rzp-button1');
const loadingOverlay = document.getElementById('loading-overlay');

if (paymentButton) {
    paymentButton.onclick = function(e) {
        e.preventDefault();

        // --- SHOW THE LOADING OVERLAY ---
        loadingOverlay.style.display = 'flex'; // Use flex to match CSS
        setTimeout(() => loadingOverlay.classList.add('visible'), 10); // Fade in

        var options = {
            "key": "{{ razorpay_key }}",
            "amount": "4900", // 49 INR in paise
            "currency": "INR",
            "name": "CUVY Premium",
            "description": "Lifetime Subscription",
            "order_id": "{{ order_id }}",
            "handler": function (response) {
                // The overlay is already visible here.
                // Now, verify the payment.
                $.ajax({
                    type: "POST",
                    url: "{% url 'payment_success' %}",
                    data: JSON.stringify(response),
                    contentType: "application/json",
                    success: function(data) {
                        if (data.status === 'success' && data.redirect_url) {
                            // On successful verification, redirect. The overlay will disappear with the page change.
                            window.location.href = data.redirect_url;
                        } else {
                            alert("Payment successful, but redirection failed. Contact support.");
                            // --- HIDE OVERLAY ON ERROR ---
                            loadingOverlay.classList.remove('visible');
                            setTimeout(() => loadingOverlay.style.display = 'none', 300);
                        }
                    },
                    error: function() {
                        alert("Payment verification failed.");
                        // --- HIDE OVERLAY ON ERROR ---
                        loadingOverlay.classList.remove('visible');
                        setTimeout(() => loadingOverlay.style.display = 'none', 300);
                    }
                });
            },
            "prefill": {
                "name": "{{ request.user.username }}",
                "email": "{{ request.user.email }}",
            },
            "modal": {
                "ondismiss": function() {
                    // This function is called when the user closes the Razorpay modal.
                    console.log("Payment modal dismissed.");
                    // --- HIDE OVERLAY WHEN USER CANCELS ---
                    loadingOverlay.classList.remove('visible');
                    setTimeout(() => loadingOverlay.style.display = 'none', 300);
                }
            },
            "theme": {"color": "#38f9d7"}
        };
        var rzp1 = new Razorpay(options);

        // This handles cases where Razorpay itself fails to open.
        rzp1.on('payment.failed', function (response){
            alert("Payment failed: " + response.error.description);
            // --- HIDE OVERLAY ON PAYMENT FAILURE ---
            loadingOverlay.classList.remove('visible');
            setTimeout(() => loadingOverlay.style.display = 'none', 300);
        });

        rzp1.open();
    }
}