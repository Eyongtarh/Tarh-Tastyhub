const { loadScript, fireDomContentLoaded } = require("../../../jsTestUtils");

function jsonResponse(body, ok = true) {
  return Promise.resolve({
    ok,
    status: ok ? 200 : 400,
    json: () => Promise.resolve(body),
  });
}

function flushPromises() {
  return new Promise((resolve) => setTimeout(resolve, 0));
}

describe("bag.js", () => {
  let toastSpy;

  // bag.js is loaded once for the whole file: its top-level
  // document.addEventListener('DOMContentLoaded', ...) registration does a
  // live querySelectorAll every time the event fires, so re-firing
  // DOMContentLoaded per test (against fresh DOM content) is all that's
  // needed - reloading the script itself would register a second,
  // independent listener on the same long-lived jsdom `document` and
  // double up every click handler.
  beforeAll(() => {
    window.getCSRFToken = jest.fn(() => "test-csrf-token");
    loadScript("static/js/bag.js");
  });

  beforeEach(() => {
    document.body.innerHTML = "";
    toastSpy = jest.fn();
    window.showToast = toastSpy;
    global.fetch = jest.fn();
  });

  test("increment button posts the new quantity to /bag/adjust/", async () => {
    document.body.innerHTML = `
      <div class="bag-item">
        <div class="card-body">
          <button class="bag-qty-decrement" data-portion-id="1">-</button>
          <input class="dish-qty" value="2" data-portion-id="1" />
          <button class="bag-qty-increment" data-portion-id="1">+</button>
          <p class="line-total" data-portion-id="1">Total: <strong>$0.00</strong></p>
        </div>
      </div>`;
    fireDomContentLoaded();
    global.fetch.mockReturnValueOnce(
      jsonResponse({
        success: true,
        bag_count: 3,
        line_total: "27.00",
        subtotal: "27.00",
        delivery_fee: "4.00",
        delivery_fee_display: "$4.00",
        grand_total: "31.00",
      })
    );

    document.querySelector(".bag-qty-increment").click();
    await flushPromises();

    expect(global.fetch).toHaveBeenCalledTimes(1);
    expect(global.fetch).toHaveBeenCalledWith(
      "/bag/adjust/1/",
      expect.objectContaining({ method: "POST" })
    );
    const [, options] = global.fetch.mock.calls[0];
    expect(options.headers["X-CSRFToken"]).toBe("test-csrf-token");
    expect(options.body.get("quantity")).toBe("3");
  });

  test("decrementing to zero removes the item and shows a warning toast", async () => {
    document.body.innerHTML = `
      <div class="bag-item">
        <div class="card-body">
          <button class="bag-qty-decrement" data-portion-id="1">-</button>
          <input class="dish-qty" value="1" data-portion-id="1" />
          <button class="bag-qty-increment" data-portion-id="1">+</button>
        </div>
      </div>`;
    fireDomContentLoaded();
    global.fetch.mockReturnValueOnce(
      jsonResponse({
        success: true,
        bag_count: 0,
        line_total: "0.00",
        subtotal: "0.00",
        delivery_fee: "4.00",
        delivery_fee_display: "$4.00",
        grand_total: "4.00",
      })
    );

    document.querySelector(".bag-qty-decrement").click();
    await flushPromises();

    expect(global.fetch).toHaveBeenCalledTimes(1);
    expect(global.fetch).toHaveBeenCalledWith(
      "/bag/remove/1/",
      expect.objectContaining({ method: "POST" })
    );
    expect(document.querySelector(".bag-item")).toBeNull();
    expect(toastSpy).toHaveBeenCalledWith(
      "Item removed from bag.",
      "warning"
    );
  });

  test("add-to-bag button posts the quantity for the selected portion", async () => {
    document.body.innerHTML = `
      <div class="card">
        <select class="portion-select">
          <option value="7" selected>Regular</option>
        </select>
        <input class="dish-qty" value="2" />
        <button class="add-to-bag" data-id="99">Add to Bag</button>
      </div>`;
    fireDomContentLoaded();
    global.fetch.mockReturnValueOnce(
      jsonResponse({
        success: true,
        bag_count: 2,
        line_total: "18.00",
        subtotal: "18.00",
        delivery_fee: "4.00",
        delivery_fee_display: "$4.00",
        grand_total: "22.00",
      })
    );

    document.querySelector(".add-to-bag").click();
    await flushPromises();

    expect(global.fetch).toHaveBeenCalledTimes(1);
    expect(global.fetch).toHaveBeenCalledWith(
      "/bag/add/7/",
      expect.objectContaining({ method: "POST" })
    );
    expect(toastSpy).toHaveBeenCalledWith("Added to bag!", "success");
  });

  test("remove-from-bag button posts to /bag/remove/ and removes the card", async () => {
    document.body.innerHTML = `
      <div class="bag-item">
        <button class="remove-from-bag" data-portion-id="42">Remove</button>
      </div>`;
    fireDomContentLoaded();
    global.fetch.mockReturnValueOnce(
      jsonResponse({
        success: true,
        bag_count: 0,
        subtotal: "0.00",
        delivery_fee: "4.00",
        delivery_fee_display: "$4.00",
        grand_total: "4.00",
      })
    );

    document.querySelector(".remove-from-bag").click();
    await flushPromises();

    expect(global.fetch).toHaveBeenCalledTimes(1);
    expect(global.fetch).toHaveBeenCalledWith(
      "/bag/remove/42/",
      expect.objectContaining({ method: "POST" })
    );
    expect(document.querySelector(".bag-item")).toBeNull();
  });

  test("a network failure surfaces a toast instead of throwing", async () => {
    document.body.innerHTML = `
      <div class="bag-item">
        <button class="remove-from-bag" data-portion-id="1">Remove</button>
      </div>`;
    fireDomContentLoaded();
    global.fetch.mockReturnValueOnce(Promise.reject(new Error("offline")));

    document.querySelector(".remove-from-bag").click();
    await flushPromises();

    expect(toastSpy).toHaveBeenCalledWith(
      expect.stringContaining("Network error"),
      "danger"
    );
  });

  test("evaluating the script a second time (two <script> tags) is a no-op", async () => {
    // Simulates the page accidentally including bag.js twice. The
    // window.dishBagJSLoaded guard set on the first load (in beforeAll)
    // should stop this second evaluation from registering a duplicate
    // top-level DOMContentLoaded listener.
    loadScript("static/js/bag.js");

    document.body.innerHTML = `
      <div class="bag-item">
        <button class="remove-from-bag" data-portion-id="1">Remove</button>
      </div>`;
    fireDomContentLoaded();

    global.fetch.mockReturnValueOnce(
      jsonResponse({ success: true, bag_count: 0, subtotal: "0.00" })
    );
    document.querySelector(".remove-from-bag").click();
    await flushPromises();

    // If the guard failed, a second click listener would have been
    // attached and this would fire two fetch calls instead of one.
    expect(global.fetch).toHaveBeenCalledTimes(1);
  });
});
