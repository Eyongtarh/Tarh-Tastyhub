document.addEventListener("DOMContentLoaded", function () {
    const loadingOverlay = document.getElementById("loading-overlay");
    if (loadingOverlay) loadingOverlay.style.display = "none";

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

    const deliveryRadios = document.querySelectorAll('input[name="delivery_type"]');
    const pickupTimeContainer = document.getElementById('pickup-time-container');

    function togglePickupTime() {
        const selected = document.querySelector('input[name="delivery_type"]:checked')?.value;
        if (pickupTimeContainer) pickupTimeContainer.style.display = selected === 'pickup' ? 'block' : 'none';
    }

    togglePickupTime();
    deliveryRadios.forEach(radio => radio.addEventListener('change', togglePickupTime));

    const form = document.getElementById("payment-form");
    if (!form) return;

    form.addEventListener("submit", async function (ev) {
        ev.preventDefault();
        const submitBtn = document.getElementById("submit-button");
        loadingOverlay.style.display = "flex";
        submitBtn.disabled = true;

        const saveInfo = document.getElementById("id-save-info")?.checked || false;
        const csrfToken = document.querySelector("input[name='csrfmiddlewaretoken']").value;

        const postData = new FormData();
        postData.append("csrfmiddlewaretoken", csrfToken);
        postData.append("client_secret", clientSecret);
        postData.append("save_info", saveInfo);
        postData.append("email", form.email.value.trim());

        try {
            await fetch("/checkout/cache_checkout_data/", { method: "POST", body: postData });
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

    function getCSRFToken() {
        return document.cookie.split('; ').find(row => row.startsWith('csrftoken='))?.split('=')[1] || '';
    }

    const feedbackTbody = document.getElementById('feedback-tbody');
    if (!feedbackTbody) return;

    feedbackTbody.addEventListener('click', function(e) {
        const target = e.target;
        const id = target.dataset.fbId;
        if (!id) return;

        let form = document.createElement('form');
        form.method = 'POST';
        form.action = '';

        const csrfInput = document.createElement('input');
        csrfInput.type = 'hidden';
        csrfInput.name = 'csrfmiddlewaretoken';
        csrfInput.value = getCSRFToken();
        form.appendChild(csrfInput);

        if (target.classList.contains('fb-mark-handled-btn')) {
            form.action = `/feedback/mark-handled/${id}/`;
        } else if (target.classList.contains('fb-mark-unhandled-btn')) {
            form.action = `/feedback/mark-unhandled/${id}/`;
        } else return;

        document.body.appendChild(form);
        form.submit();
    });
});
