const { loadScript, fireDomContentLoaded } = require("../../../../../jsTestUtils");

function jsonScript(id, value) {
  const el = document.createElement("script");
  el.type = "application/json";
  el.id = id;
  el.textContent = JSON.stringify(value);
  document.body.appendChild(el);
}

function buildCard() {
  return {
    mount: jest.fn(),
    on: jest.fn(),
  };
}

function buildStripeMock(card) {
  const elements = { create: jest.fn(() => card) };
  const stripeInstance = {
    elements: jest.fn(() => elements),
    confirmCardPayment: jest.fn(),
  };
  const Stripe = jest.fn(() => stripeInstance);
  return { Stripe, stripeInstance, elements };
}

function basicFormHtml() {
  return `
    <div id="card-element"></div>
    <div id="card-errors"></div>
    <form id="payment-form">
      <input name="email" value="jane@example.com" />
      <input name="full_name" value="Jane Doe" />
      <input name="phone_number" value="12345" />
      <input name="street_address1" value="1 Test St" />
      <input name="street_address2" value="" />
      <input name="town_or_city" value="Testville" />
      <input name="county" value="" />
      <input name="postcode" value="AB1 2CD" />
      <input type="radio" name="delivery_type" value="delivery" checked />
      <input type="radio" name="delivery_type" value="pickup" />
      <input name="pickup_time" value="" />
      <button id="submit-button" type="submit">Pay Now</button>
      <div id="loading-overlay" style="display:none;"></div>
    </form>
    <div id="pickup-time-container" style="display: none;" aria-hidden="true"></div>
  `;
}

describe("checkout.js", () => {
  let consoleErrorSpy;

  beforeEach(() => {
    document.body.innerHTML = "";
    global.fetch = jest.fn();
    consoleErrorSpy = jest.spyOn(console, "error").mockImplementation(() => {});
  });

  afterEach(() => {
    consoleErrorSpy.mockRestore();
    delete window.Stripe;
  });

  test("logs an error and does nothing when the Stripe config elements are missing", () => {
    // No #id_stripe_public_key / #id_client_secret in the DOM at all.
    document.body.innerHTML = basicFormHtml();
    window.Stripe = jest.fn();

    loadScript("checkout/static/checkout/js/checkout.js");
    fireDomContentLoaded();

    expect(window.Stripe).not.toHaveBeenCalled();
    expect(consoleErrorSpy).toHaveBeenCalledWith(
      expect.stringContaining("Stripe configuration elements are missing")
    );
  });

  test("logs an error and does nothing when the Stripe config JSON is malformed", () => {
    document.body.innerHTML = basicFormHtml();
    const badScript = document.createElement("script");
    badScript.type = "application/json";
    badScript.id = "id_stripe_public_key";
    badScript.textContent = "{not valid json";
    document.body.appendChild(badScript);
    jsonScript("id_client_secret", "pi_abc_secret_xyz");
    window.Stripe = jest.fn();

    loadScript("checkout/static/checkout/js/checkout.js");
    fireDomContentLoaded();

    expect(window.Stripe).not.toHaveBeenCalled();
    expect(consoleErrorSpy).toHaveBeenCalledWith(
      expect.stringContaining("Failed to parse Stripe configuration"),
      expect.any(Error)
    );
  });

  test("initialises Stripe Elements and mounts the card element", () => {
    document.body.innerHTML = basicFormHtml();
    jsonScript("id_stripe_public_key", "pk_test_123");
    jsonScript("id_client_secret", "pi_abc_secret_xyz");
    const card = buildCard();
    const { Stripe, stripeInstance, elements } = buildStripeMock(card);
    window.Stripe = Stripe;

    loadScript("checkout/static/checkout/js/checkout.js");
    fireDomContentLoaded();

    expect(Stripe).toHaveBeenCalledWith("pk_test_123");
    expect(stripeInstance.elements).toHaveBeenCalled();
    expect(elements.create).toHaveBeenCalledWith("card");
    expect(card.mount).toHaveBeenCalledWith("#card-element");
  });

  describe("payment form submission", () => {
    function setUpForm() {
      document.body.innerHTML = basicFormHtml();
      jsonScript("id_stripe_public_key", "pk_test_123");
      jsonScript("id_client_secret", "pi_abc_secret_xyz");
      const card = buildCard();
      const { Stripe, stripeInstance } = buildStripeMock(card);
      window.Stripe = Stripe;

      loadScript("checkout/static/checkout/js/checkout.js");
      fireDomContentLoaded();

      const form = document.getElementById("payment-form");
      return { form, stripeInstance };
    }

    function submitForm(form) {
      form.dispatchEvent(
        new Event("submit", { bubbles: true, cancelable: true })
      );
    }

    async function flushMicrotasks() {
      await Promise.resolve();
      await Promise.resolve();
      await Promise.resolve();
      await Promise.resolve();
    }

    test("caches checkout data, confirms payment, then submits the form on success", async () => {
      const { form, stripeInstance } = setUpForm();
      const submitSpy = jest.spyOn(form, "submit").mockImplementation(() => {});
      global.fetch.mockResolvedValueOnce({ ok: true });
      stripeInstance.confirmCardPayment.mockResolvedValueOnce({
        paymentIntent: { status: "succeeded", id: "pi_confirmed_123" },
      });

      submitForm(form);
      await flushMicrotasks();

      expect(global.fetch).toHaveBeenCalledWith(
        "/checkout/cache_checkout_data/",
        expect.objectContaining({ method: "POST" })
      );
      expect(stripeInstance.confirmCardPayment).toHaveBeenCalledWith(
        "pi_abc_secret_xyz",
        expect.any(Object)
      );
      expect(submitSpy).toHaveBeenCalledTimes(1);
      const hiddenPidInput = form.querySelector(
        "input[name='stripe_pid']"
      );
      expect(hiddenPidInput).not.toBeNull();
      expect(hiddenPidInput.value).toBe("pi_confirmed_123");
    });

    test("shows an error and restores the UI when cache_checkout_data fails", async () => {
      const { form, stripeInstance } = setUpForm();
      global.fetch.mockResolvedValueOnce({ ok: false });

      submitForm(form);
      await flushMicrotasks();

      expect(document.getElementById("card-errors").textContent).toContain(
        "Failed to cache checkout data"
      );
      expect(document.getElementById("submit-button").disabled).toBe(false);
      expect(document.getElementById("loading-overlay").style.display).toBe(
        "none"
      );
      expect(stripeInstance.confirmCardPayment).not.toHaveBeenCalled();
    });

    test("shows the Stripe error message and re-enables the button when payment fails", async () => {
      const { form, stripeInstance } = setUpForm();
      global.fetch.mockResolvedValueOnce({ ok: true });
      stripeInstance.confirmCardPayment.mockResolvedValueOnce({
        error: { message: "Your card was declined." },
      });

      submitForm(form);
      await flushMicrotasks();

      expect(document.getElementById("card-errors").textContent).toBe(
        "Your card was declined."
      );
      expect(document.getElementById("submit-button").disabled).toBe(false);
    });
  });

  describe("pickup/delivery toggle", () => {
    test("selecting pickup reveals the pickup-time field and clears aria-hidden", () => {
      document.body.innerHTML = basicFormHtml();
      jsonScript("id_stripe_public_key", "pk_test_123");
      jsonScript("id_client_secret", "pi_abc_secret_xyz");
      window.Stripe = buildStripeMock(buildCard()).Stripe;

      loadScript("checkout/static/checkout/js/checkout.js");
      fireDomContentLoaded();

      const pickupRadio = document.querySelector(
        "input[name='delivery_type'][value='pickup']"
      );
      pickupRadio.checked = true;
      pickupRadio.dispatchEvent(new Event("change"));

      const container = document.getElementById("pickup-time-container");
      expect(container.style.display).toBe("block");
      expect(container.getAttribute("aria-hidden")).toBe("false");
    });

    test("selecting delivery hides the pickup-time field and sets aria-hidden", () => {
      document.body.innerHTML = basicFormHtml();
      jsonScript("id_stripe_public_key", "pk_test_123");
      jsonScript("id_client_secret", "pi_abc_secret_xyz");
      window.Stripe = buildStripeMock(buildCard()).Stripe;

      loadScript("checkout/static/checkout/js/checkout.js");
      fireDomContentLoaded();

      const deliveryRadio = document.querySelector(
        "input[name='delivery_type'][value='delivery']"
      );
      deliveryRadio.checked = true;
      deliveryRadio.dispatchEvent(new Event("change"));

      const container = document.getElementById("pickup-time-container");
      expect(container.style.display).toBe("none");
      expect(container.getAttribute("aria-hidden")).toBe("true");
    });
  });
});
