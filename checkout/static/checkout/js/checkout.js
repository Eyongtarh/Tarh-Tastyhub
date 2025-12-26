/**
 * checkout.js
 * - Initializes Stripe Elements for card input.
 * - Shows/hides pickup time based on delivery type.
 * - Validates pickup time according to opening hours and 15-min buffer.
 * - Submits checkout form with billing details, delivery info, and metadata.
 * - Displays full-page loading overlay during submission.
 */
document.addEventListener("DOMContentLoaded", function () {
    // Full-page loading overlay
    let loadingOverlay = document.getElementById("loading-overlay");
    if (!loadingOverlay) {
        loadingOverlay = document.createElement("div");
        loadingOverlay.id = "loading-overlay";
        loadingOverlay.style.position = "fixed";
        loadingOverlay.style.top = "0";
        loadingOverlay.style.left = "0";
        loadingOverlay.style.width = "100%";
        loadingOverlay.style.height = "100%";
        loadingOverlay.style.backgroundColor = "rgba(0,0,0,0.5)";
        loadingOverlay.style.display = "none";
        loadingOverlay.style.justifyContent = "center";
        loadingOverlay.style.alignItems = "center";
        loadingOverlay.style.zIndex = "9999";
        loadingOverlay.innerHTML = '<div class="spinner-border text-light" role="status"></div>';
        document.body.appendChild(loadingOverlay);
    }
    // Stripe keys
    const stripePublicKey = JSON.parse(document.getElementById("id_stripe_public_key")?.textContent || '""');
    const clientSecret = JSON.parse(document.getElementById("id_client_secret")?.textContent || '""');
    if (!stripePublicKey || !clientSecret) {
        console.error("Stripe keys missing!");
        return;
    }
    const stripe = Stripe(stripePublicKey);
    const elements = stripe.elements();
    const style = {
        base: {
            color: "#000",
            fontFamily: '"Helvetica Neue", Helvetica, sans-serif',
            fontSize: window.innerWidth < 576 ? "14px" : "16px",
            "::placeholder": { color: "#aab7c4" },
        },
        invalid: { color: "#dc3545", iconColor: "#dc3545" },
    };
    // Stripe card element
    const cardElementDiv = document.getElementById("card-element");
    if (!cardElementDiv) return;
    const card = elements.create("card", { style });
    card.mount("#card-element");
    card.on("focus", () => {
        if (window.innerWidth < 576) {
            cardElementDiv.scrollIntoView({ behavior: "smooth", block: "center" });
        }
    });
    card.on("change", function (event) {
        const errorDiv = document.getElementById("card-errors");
        errorDiv.textContent = event.error ? event.error.message : "";
    });
    // Delivery type & pickup time
    const deliveryRadios = document.querySelectorAll('input[name="delivery_type"]');
    const pickupTimeContainer = document.getElementById('pickup-time-container');
    const pickupTimeInput = document.querySelector('input[name="pickup_time"]');
    function togglePickupTime() {
        const selected = document.querySelector('input[name="delivery_type"]:checked')?.value;
        if (pickupTimeContainer) pickupTimeContainer.style.display = selected === 'pickup' ? 'block' : 'none';
    }
    togglePickupTime();
    deliveryRadios.forEach(radio => radio.addEventListener('change', togglePickupTime));
    // Validate pickup time
    function isValidPickupTime(dateTimeStr) {
        if (!dateTimeStr) return false;
        const pickupDate = new Date(dateTimeStr);
        if (isNaN(pickupDate)) return false;
        const now = new Date();
        const minPickup = new Date(now.getTime() + 15 * 60000);
        if (pickupDate < minPickup) return false;
        const day = pickupDate.getDay();
        const time = pickupDate.getHours() + pickupDate.getMinutes() / 60;
        if (day >= 1 && day <= 5) {
            return time >= 7 && time <= 22;
        } else {
            return time >= 7 && time <= 21;
        }
    }
    // Set min attribute for datetime-local input
    if (pickupTimeInput) {
        const now = new Date();
        now.setMinutes(now.getMinutes() + 15);
        const isoStr = now.toISOString().slice(0,16);
        pickupTimeInput.min = isoStr;
    }
    // Form submission
    const form = document.getElementById("payment-form");
    if (!form) return;
    form.addEventListener("submit", async function (ev) {
        ev.preventDefault();
        const submitBtn = document.getElementById("submit-button");
        loadingOverlay.style.display = "flex";
        submitBtn.disabled = true;
        const saveInfo = document.getElementById("id-save-info")?.checked || false;
        const csrfToken = document.querySelector("input[name='csrfmiddlewaretoken']").value;
        const selectedDeliveryType = document.querySelector('input[name="delivery_type"]:checked')?.value;
        const pickupTime = pickupTimeInput?.value || "";
        // Validate pickup time if pickup selected
        if (selectedDeliveryType === 'pickup' && !isValidPickupTime(pickupTime)) {
            alert("Invalid pickup time. Must be at least 15 minutes from now and within opening hours.");
            loadingOverlay.style.display = "none";
            submitBtn.disabled = false;
            return;
        }
        const postData = new FormData();
        postData.append("csrfmiddlewaretoken", csrfToken);
        postData.append("client_secret", clientSecret);
        postData.append("save_info", saveInfo);
        postData.append("email", form.email.value.trim());
        postData.append("delivery_type", selectedDeliveryType);
        postData.append("pickup_time", pickupTime);
        try {
            // Cache checkout data for Stripe webhook
            await fetch("/checkout/cache_checkout_data/", { method: "POST", body: postData });
            // Confirm payment
            const result = await stripe.confirmCardPayment(clientSecret, {
                payment_method: {
                    card: card,
                    billing_details: {
                        name: form.full_name.value.trim(),
                        phone: form.phone_number.value.trim(),
                        email: form.email.value.trim(),
                        address: {
                            line1: form.street_address1.value.trim(),
                            line2: form.street_address2.value.trim(),
                            city: form.town_or_city.value.trim(),
                            state: form.county.value.trim(),
                        },
                    },
                },
                payment_intent_data: {
                    metadata: {
                        delivery_type: selectedDeliveryType,
                        pickup_time: pickupTime,
                        email: form.email.value.trim(),
                    },
                },
            });
            if (result.error) {
                document.getElementById("card-errors").textContent = result.error.message;
                loadingOverlay.style.display = "none";
                submitBtn.disabled = false;
            } else if (result.paymentIntent?.status === "succeeded") {
                form.submit();
            }
        } catch (error) {
            console.error(error);
            location.reload();
        }
    });
    // Order status colors
    const statusColors = {
        "Pending": "#ffc107",
        "Preparing": "#0d6efd",
        "Out for Delivery": "#0dcaf0",
        "Completed": "#198754"
    };
    document.querySelectorAll('.status-dropdown').forEach(dropdown => {
        dropdown.style.backgroundColor = statusColors[dropdown.value] || "#6c757d";
        dropdown.style.color = "white";
        dropdown.addEventListener('change', function() {
            const newStatus = this.value;
            this.style.backgroundColor = statusColors[newStatus] || "#6c757d";
        });
    });
});
