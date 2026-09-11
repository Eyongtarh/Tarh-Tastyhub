/**
 * These static JS files are loaded directly via <script> tags in production
 * (no bundler, no ES modules - see DEPLOYMENT.md), so tests load them the
 * same way: read the source and evaluate it in the jsdom global scope.
 *
 * This file lives at the repo root so __dirname is a stable anchor -
 * every relativePath passed to loadScript() is relative to the repo root.
 */
const fs = require("fs");
const path = require("path");

function loadScript(relativePath) {
  const code = fs.readFileSync(path.join(__dirname, relativePath), "utf8");
  // Indirect eval runs in the realm's global scope, so `document`/`window`
  // references inside the script resolve to the real jsdom globals.
  (0, eval)(code);
}

function fireDomContentLoaded() {
  document.dispatchEvent(new Event("DOMContentLoaded"));
}

module.exports = { loadScript, fireDomContentLoaded };
