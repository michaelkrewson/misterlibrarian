// Permanent (301) redirects for blogs that moved off mistertranslation.com to
// their own m8k.io subdomains (m8k umbrella, 2026-10-10). Bound only to the
// moved folders' routes (see mt-redirects.wrangler.jsonc), so every other path —
// the Bible project, the hub, Dear Mr. Librarian — never touches this Worker.
// To move another blog: add its prefix here AND its two routes in the config.
const MOVED = {
  "/west": "https://west.m8k.io",
};

export default {
  async fetch(request) {
    const url = new URL(request.url);
    for (const [prefix, target] of Object.entries(MOVED)) {
      if (url.pathname === prefix || url.pathname.startsWith(prefix + "/")) {
        const rest = url.pathname.slice(prefix.length) || "/";
        return Response.redirect(target + rest + url.search, 301);
      }
    }
    return fetch(request);   // unreachable with the configured routes; pass through if ever hit
  },
};
