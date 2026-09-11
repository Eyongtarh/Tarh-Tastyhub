const { loadScript, fireDomContentLoaded } = require("../../../jsTestUtils");

describe("search.js", () => {
  beforeEach(() => {
    document.body.innerHTML = "";
    loadScript("static/js/search.js");
  });

  test("pressing Enter in the search input submits the search form", () => {
    document.body.innerHTML = `
      <form id="search-form">
        <input type="text" id="search-input" name="q" />
      </form>`;
    const form = document.getElementById("search-form");
    // jsdom does not implement real form submission navigation; spy on
    // submit() to confirm the handler calls it.
    form.submit = jest.fn();
    fireDomContentLoaded();

    const input = document.getElementById("search-input");
    const event = new KeyboardEvent("keydown", {
      key: "Enter",
      cancelable: true,
    });
    input.dispatchEvent(event);

    expect(form.submit).toHaveBeenCalledTimes(1);
    expect(event.defaultPrevented).toBe(true);
  });

  test("other keys do not submit the form", () => {
    document.body.innerHTML = `
      <form id="search-form">
        <input type="text" id="search-input" name="q" />
      </form>`;
    const form = document.getElementById("search-form");
    form.submit = jest.fn();
    fireDomContentLoaded();

    document
      .getElementById("search-input")
      .dispatchEvent(new KeyboardEvent("keydown", { key: "a" }));

    expect(form.submit).not.toHaveBeenCalled();
  });

  test("changing the portion select updates the displayed price and portion id", () => {
    document.body.innerHTML = `
      <div class="card-body">
        <select class="portion-select">
          <option value="1" data-price="9.99">Regular</option>
          <option value="2" data-price="14.99" selected>Large</option>
        </select>
        <input class="dish-qty" value="2" data-portion-id="1" />
        <p class="dish-price">$0.00</p>
      </div>`;
    fireDomContentLoaded();

    const select = document.querySelector(".portion-select");
    select.value = "2";
    select.dispatchEvent(new Event("change"));

    expect(document.querySelector(".dish-price").textContent).toBe("$29.98");
    expect(document.querySelector(".dish-qty").dataset.portionId).toBe("2");
  });

  test("does nothing when the quantity input or price element is missing", () => {
    document.body.innerHTML = `
      <div class="card-body">
        <select class="portion-select">
          <option value="1" data-price="9.99" selected>Regular</option>
        </select>
      </div>`;
    // Should not throw even though .dish-qty/.dish-price are absent.
    expect(() => {
      fireDomContentLoaded();
      document
        .querySelector(".portion-select")
        .dispatchEvent(new Event("change"));
    }).not.toThrow();
  });
});
