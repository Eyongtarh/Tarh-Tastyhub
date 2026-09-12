/** @type {import('jest').Config} */
module.exports = {
  testEnvironment: "jsdom",
  testMatch: ["**/__tests__/**/*.test.js"],
  testPathIgnorePatterns: [
    "/node_modules/",
    "/.venv/",
    // Django's collectstatic output - a gitignored, regeneratable copy
    // of static/, which would otherwise duplicate every test it copies.
    "/staticfiles/",
  ],
};
