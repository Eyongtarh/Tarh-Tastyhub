/* jshint esversion: 11 */
/* global Stripe */
document.addEventListener("DOMContentLoaded", () => {
  /*
     PICKUP TIME TOGGLE - runs immediately, doesn't need Stripe
  */
  const deliveryRadios = document.querySelectorAll("input[name='delivery_type']");
  const pickupContainer = document.getElementById("pickup-time-container");
  const togglePickup = () => {
    const selected =
      document.querySelector("input[name='delivery_type']:checked")?.value;
    const isPickup = selected === "pickup";
    pickupContainer.style.display = isPickup ? "block" : "none";
    pickupContainer.setAttribute("aria-hidden", isPickup ? "false" : "true");
  };
  deliveryRadios.forEach((radio) => {
    radio.addEventListener("change", togglePickup);
  });
  togglePickup();

  /*
     STRIPE SETUP - the PaymentIntent is created on demand here rather
     than server-side while rendering the page, so loading /checkout/
     doesn't block on a network round trip to Stripe just to learn a
     client secret nothing above the payment form needs yet.
  */
  const stripeKeyEl = document.getElementById("id_stripe_public_key");
  const cardElementDiv = document.getElementById("card-element");
  const cardErrorsEl = document.getElementById("card-errors");
  if (!stripeKeyEl || !cardElementDiv) {
    console.error("Stripe configuration elements are missing from the page.");
    return;
  }
  let stripePublicKey;
  try {
    stripePublicKey = JSON.parse(stripeKeyEl.textContent);
  } catch (err) {
    console.error("Failed to parse Stripe configuration:", err);
    return;
  }
  const stripe = Stripe(stripePublicKey);
  let clientSecret;

  /*
     PAYMENT FORM SUBMISSION - attached once the client secret above
     has actually loaded; clientSecret is read via closure, so this
     always sees the value by the time a real submit can happen.
  */
  function attachSubmitHandler(card) {
    const form = document.getElementById("payment-form");
    if (!form) {
      return;
    }
    form.addEventListener("submit", async (e) => {
      e.preventDefault();
      const submitButton = document.getElementById("submit-button");
      const loadingOverlay = document.getElementById("loading-overlay");
      submitButton.disabled = true;
      loadingOverlay.style.display = "flex";
      const email = form.email?.value?.trim() || "";
      const deliveryType =
        document.querySelector("input[name='delivery_type']:checked")?.value || "delivery";
      const pickupTime = form.pickup_time?.value || "";
      /*
         CACHE CHECKOUT DATA
      */
      const stripePid = clientSecret.split("_secret")[0];
      const cacheData = new FormData();
      cacheData.append("stripe_pid", stripePid);
      cacheData.append("delivery_type", deliveryType);
      cacheData.append("pickup_time", pickupTime);
      cacheData.append("email", email);
      try {
        const response = await fetch("/checkout/cache_checkout_data/", {
          method: "POST",
          body: cacheData,
        });
        if (!response.ok) {
          throw new Error("Failed to cache checkout data");
        }

      } catch (err) {
        console.error(err);
        document.getElementById("card-errors").textContent =
          "Failed to cache checkout data. Please try again.";
        submitButton.disabled = false;
        loadingOverlay.style.display = "none";
        return;
      }
      /*
         CONFIRM PAYMENT WITH STRIPE
      */
      try {
        const result = await stripe.confirmCardPayment(clientSecret, {
          payment_method: {
            card: card,
            billing_details: {
              name: form.full_name?.value || "",
              email: email,
              phone: form.phone_number?.value || "",
              address: {
                line1: form.street_address1?.value || "",
                line2: form.street_address2?.value || "",
                city: form.town_or_city?.value || "",
                state: form.county?.value || "",
                postal_code: form.postcode?.value || "",
                country: "US",
              },
            },
          },
        });
        if (result.error) {
          document.getElementById("card-errors").textContent = result.error.message;
          submitButton.disabled = false;
          loadingOverlay.style.display = "none";
          return;
        }
        if (result.paymentIntent?.status === "succeeded") {
          const pidInput = document.createElement("input");
          pidInput.type = "hidden";
          pidInput.name = "stripe_pid";
          pidInput.value = result.paymentIntent.id;
          form.appendChild(pidInput);
          form.submit();
        }
      } catch (err) {
        console.error("Stripe payment failed:", err);
        document.getElementById("card-errors").textContent =
          "Payment failed. Please try again.";
        submitButton.disabled = false;
        loadingOverlay.style.display = "none";
      }
    });
  }

  (async () => {
    try {
      const response = await fetch("/checkout/create-payment-intent/", {
        method: "POST",
      });
      const data = await response.json();
      if (!response.ok || !data.client_secret) {
        throw new Error(data.error || "Failed to set up payment.");
      }
      clientSecret = data.client_secret;
    } catch (err) {
      console.error("Failed to create payment intent:", err);
      if (cardErrorsEl) {
        cardErrorsEl.textContent =
          "Unable to load the payment form. Please refresh the page.";
      }
      return;
    }

    const elements = stripe.elements();
    const card = elements.create("card");
    card.mount("#card-element");
    card.on("change", (event) => {
      cardErrorsEl.textContent = event.error ? event.error.message : "";
    });
    attachSubmitHandler(card);
  })();
});
