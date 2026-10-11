// Permanent (301) redirects for blogs that moved off mistertranslation.com to
// their own m8k.io subdomains (m8k umbrella, 2026-10-10). Bound only to the
// moved folders' routes (see mt-redirects.wrangler.jsonc), so every other path —
// the Bible project, Dear Mr. Librarian — never touches this Worker.
// To move another blog: add its prefix here AND its two routes in the config.
// Also: /bible.html → / (2026-10-10) — the Bible home became the site's front page.
const MOVED = {
  "/finance": "https://ledger.m8k.io",
  "/notebook": "https://notebook.m8k.io",
  "/health": "https://regimen.m8k.io",
  "/west": "https://west.m8k.io",
  "/travel": "https://abroad.m8k.io",
};

export default {
  async fetch(request) {
    const url = new URL(request.url);
    if (url.pathname === "/bible.html") {
      return Response.redirect(url.origin + "/" + url.search, 301);
    }
    for (const [prefix, target] of Object.entries(MOVED)) {
      if (url.pathname === prefix || url.pathname.startsWith(prefix + "/")) {
        const rest = url.pathname.slice(prefix.length) || "/";
        return Response.redirect(target + rest + url.search, 301);
      }
    }
    return fetch(request);   // unreachable with the configured routes; pass through if ever hit
  },
};
