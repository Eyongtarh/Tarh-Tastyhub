document.addEventListener("DOMContentLoaded", () => {
    const stripePublicKey = JSON.parse(
        document.getElementById("id_stripe_public_key").textContent
    );
    const clientSecret = JSON.parse(
        document.getElementById("id_client_secret").textContent
    );

    const stripe = Stripe(stripePublicKey);
    const elements = stripe.elements();

    // Mount the card element
    const card = elements.create("card");
    card.mount("#card-element");

    // Display card errors
    card.on("change", (event) => {
        document.getElementById("card-errors").textContent =
            event.error ? event.error.message : "";
    });

    const form = document.getElementById("payment-form");

    if (form) {
        form.addEventListener("submit", async (e) => {
            e.preventDefault();

            // Disable button and show loader
            const submitButton = document.getElementById("submit-button");
            const loadingOverlay = document.getElementById("loading-overlay");
            submitButton.disabled = true;
            loadingOverlay.style.display = "flex";

            const csrfToken = document.querySelector(
                "input[name='csrfmiddlewaretoken']"
            ).value;

            const email = form.email.value.trim();
            const deliveryType = document.querySelector(
                "input[name='delivery_type']:checked"
            )?.value || "delivery";
            const pickupTime = form.pickup_time?.value || "";

            // Cache checkout data in Django session / Stripe metadata
            const cacheData = new FormData();
            cacheData.append("csrfmiddlewaretoken", csrfToken);
            cacheData.append("client_secret", clientSecret);
            cacheData.append("delivery_type", deliveryType);
            cacheData.append("pickup_time", pickupTime);
            cacheData.append("email", email);

            try {
                await fetch("/checkout/cache_checkout_data/", {
                    method: "POST",
                    body: cacheData,
                });
            } catch (err) {
                console.error("Failed to cache checkout data:", err);
            }

            // Confirm the payment with Stripe
            const result = await stripe.confirmCardPayment(clientSecret, {
                payment_method_data: {
                    type: "card",
                    card: card,
                    billing_details: {
                        name: form.full_name.value,
                        email: email,
                        phone: form.phone_number.value,
                        address: {
                            line1: form.street_address1.value,
                            line2: form.street_address2.value,
                            city: form.town_or_city.value,
                            state: form.county.value,
                            postal_code: form.postcode.value,
                            country: "US",
                        },
                    },
                },
            });

            if (result.error) {
                document.getElementById("card-errors").textContent =
                    result.error.message;
                submitButton.disabled = false;
                loadingOverlay.style.display = "none";
            } else if (result.paymentIntent.status === "succeeded") {
                // Add hidden input with Stripe PaymentIntent ID and submit form
                const pidInput = document.createElement("input");
                pidInput.type = "hidden";
                pidInput.name = "stripe_pid";
                pidInput.value = result.paymentIntent.id;
                form.appendChild(pidInput);
                form.submit();
            }
        });
    }

    /* ============================
       ADMIN ORDER STATUS COLORS
       ============================ */

    const statusColors = {
        Pending: "#ffc107",
        Preparing: "#0d6efd",
        "Out for Delivery": "#0dcaf0",
        Completed: "#198754",
        Cancelled: "#dc3545",
    };

    document.querySelectorAll(".status-dropdown").forEach((dropdown) => {
        const applyColor = () => {
            dropdown.style.backgroundColor =
                statusColors[dropdown.value] || "#6c757d";
            dropdown.style.color = "#fff";
        };

        applyColor();
        dropdown.addEventListener("change", applyColor);
    });

    /* ============================
       SHOW PICKUP TIME FIELD DYNAMICALLY
       ============================ */
    const deliveryRadios = document.querySelectorAll("input[name='delivery_type']");
    const pickupContainer = document.getElementById("pickup-time-container");

    deliveryRadios.forEach((radio) => {
        radio.addEventListener("change", () => {
            if (radio.value === "pickup") {
                pickupContainer.style.display = "block";
            } else {
                pickupContainer.style.display = "none";
            }
        });

        // Initialize on page load
        if (radio.checked && radio.value === "pickup") {
            pickupContainer.style.display = "block";
        }
    });
});
