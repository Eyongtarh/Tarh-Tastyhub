const { loadScript } = require("../../../jsTestUtils");

describe("base.js", () => {
  function clearAllCookies() {
    document.cookie.split(";").forEach((c) => {
      const name = c.split("=")[0].trim();
      if (name) {
        document.cookie = `${name}=;expires=Thu, 01 Jan 1970 00:00:00 UTC;path=/`;
      }
    });
  }

  beforeEach(() => {
    document.body.innerHTML = "";
    clearAllCookies();
    delete window.getCSRFToken;
    delete window.showToast;
    delete window.bootstrap;
    jest.useRealTimers();
    loadScript("static/js/base.js");
  });

  describe("getCSRFToken", () => {
    test("reads the csrftoken cookie", () => {
      document.cookie = "csrftoken=abc123";
      expect(window.getCSRFToken()).toBe("abc123");
    });

    test("returns null when the cookie is absent", () => {
      expect(window.getCSRFToken()).toBeNull();
    });

    test("finds the cookie among several others", () => {
      document.cookie = "sessionid=xyz";
      document.cookie = "csrftoken=found-me";
      document.cookie = "other=1";
      expect(window.getCSRFToken()).toBe("found-me");
    });
  });

  describe("showToast", () => {
    test("falls back to the simple toast when Bootstrap is unavailable", () => {
      window.showToast("Hello there", "success", 0);
      const toast = document.getElementById("notification-toast");
      expect(toast).not.toBeNull();
      expect(toast.textContent).toBe("Hello there");
      expect(toast.className).toContain("show");
    });

    test("renders the message as text, not HTML, guarding against XSS", () => {
      window.showToast("<img src=x onerror=alert(1)>", "danger", 0);
      const toast = document.getElementById("notification-toast");
      expect(toast.querySelector("img")).toBeNull();
      expect(toast.textContent).toBe("<img src=x onerror=alert(1)>");
    });

    test("uses the Bootstrap toast container when bootstrap.Toast is present", () => {
      document.body.innerHTML = '<div id="toast-container"></div>';
      const show = jest.fn();
      const hide = jest.fn();
      window.bootstrap = {
        Toast: jest.fn().mockImplementation(() => ({ show, hide })),
      };

      window.showToast("Order placed", "success", 0);

      const container = document.getElementById("toast-container");
      const toastEl = container.querySelector(".toast");
      expect(toastEl).not.toBeNull();
      expect(toastEl.querySelector(".toast-body").textContent).toBe(
        "Order placed"
      );
      expect(show).toHaveBeenCalled();
    });

    test("does not inject the message as HTML in the Bootstrap path", () => {
      document.body.innerHTML = '<div id="toast-container"></div>';
      window.bootstrap = {
        Toast: jest.fn().mockImplementation(() => ({
          show: jest.fn(),
          hide: jest.fn(),
        })),
      };

      window.showToast("<b>bold</b> message", "info", 0);

      const body = document
        .getElementById("toast-container")
        .querySelector(".toast-body");
      expect(body.querySelector("b")).toBeNull();
      expect(body.textContent).toBe("<b>bold</b> message");
    });
  });
});
