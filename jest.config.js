/** @type {import('jest').Config} */
module.exports = {
  testEnvironment: "jsdom",
  testMatch: ["**/__tests__/**/*.test.js"],
  testPathIgnorePatterns: ["/node_modules/", "/.venv/"],
};
