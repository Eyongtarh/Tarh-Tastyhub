document.addEventListener("DOMContentLoaded", () => {
    const stripePublicKey = JSON.parse(
        document.getElementById("id_stripe_public_key").textContent
    );
    const clientSecret = JSON.parse(
        document.getElementById("id_client_secret").textContent
    );

    const stripe = Stripe(stripePublicKey);
    const elements = stripe.elements();

    const card = elements.create("card");
    card.mount("#card-element");

    card.on("change", (event) => {
        document.getElementById("card-errors").textContent =
            event.error ? event.error.message : "";
    });

    const form = document.getElementById("payment-form");

    if (form) {
        form.addEventListener("submit", async (e) => {
            e.preventDefault();

            document.getElementById("submit-button").disabled = true;
            document.getElementById("loading-overlay").style.display = "flex";

            const csrfToken = document.querySelector(
                "input[name='csrfmiddlewaretoken']"
            ).value;

            const email = form.email.value.trim();

            const cacheData = new FormData();
            cacheData.append("csrfmiddlewaretoken", csrfToken);
            cacheData.append("client_secret", clientSecret);
            cacheData.append(
                "delivery_type",
                document.querySelector("input[name='delivery_type']:checked")?.value
            );
            cacheData.append("pickup_time", form.pickup_time?.value || "");
            cacheData.append("email", email);

            await fetch("/checkout/cache_checkout_data/", {
                method: "POST",
                body: cacheData,
            });

            const result = await stripe.confirmCardPayment(clientSecret, {
                payment_method: {
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
                document.getElementById("submit-button").disabled = false;
                document.getElementById("loading-overlay").style.display = "none";
            } else if (result.paymentIntent.status === "succeeded") {
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
});
