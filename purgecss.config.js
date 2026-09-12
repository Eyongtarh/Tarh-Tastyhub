/**
 * Purges unused rules out of the vendored Bootstrap stylesheet.
 *
 * Bootstrap's own JS (bootstrap.bundle.min.js) adds/removes a fixed set of
 * classes at runtime (dropdown, modal, offcanvas, collapse, toast, form
 * validation, ...) that never appear literally in our templates or JS, so
 * they can't be discovered by scanning content alone. Rather than trying to
 * enumerate every one of those exactly, the safelist below keeps whole
 * families of them by pattern - safer than a byte-optimal purge, but this
 * is a live e-commerce site and breaking a dropdown or the checkout modal
 * is a much worse outcome than a few extra KB of CSS.
 *
 * Regenerate after any Bootstrap version bump or if a new Bootstrap
 * component (accordion, carousel, tooltip, popover, ...) gets used
 * somewhere, since those aren't currently in the safelist at all:
 *   npm run purge-css
 */
module.exports = {
  content: [
    "**/templates/**/*.html",
    "templates/**/*.html",
    "static/js/*.js",
    "checkout/static/checkout/js/*.js",
    "static/css/*.css",
    "dishes/static/dishes/css/*.css",
    "checkout/static/checkout/css/*.css",
  ],
  css: ["static/vendor/bootstrap/bootstrap.min.css"],
  output: "static/vendor/bootstrap/",
  safelist: {
    standard: [
      "html",
      "body",
      /^btn/,
      /^col/,
      /^row/,
      /^container/,
    ],
    greedy: [
      // Components whose JS toggles classes not present in our own
      // templates: dropdown, modal, offcanvas, collapse/navbar-collapse,
      // toast, alert, form validation states, focus/visibility utilities.
      /show/,
      /showing/,
      /hiding/,
      /hide/,
      /fade/,
      /collaps/,
      /^modal/,
      /^offcanvas/,
      /^dropdown/,
      /^toast/,
      /^alert/,
      /^navbar/,
      /^backdrop/,
      /^was-validated/,
      /-valid$/,
      /-invalid$/,
      /^is-valid/,
      /^is-invalid/,
      /^focus/,
      /^active/,
      /^disabled/,
      /^visually-hidden/,
      /^visible/,
      /^invisible/,
      /^spinner/,
      /^progress/,
      /^badge/,
      /^pagination/,
      /^page-/,
    ],
  },
};
