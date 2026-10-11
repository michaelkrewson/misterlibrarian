// Shared Worker for every blog moved to an m8k.io subdomain (2026-10-10).
//
// The blogs are served as static assets with html_handling "none", so every URL
// keeps its .html exactly as it did on GitHub Pages (Cloudflare's default
// handling would 307/308 /x.html -> /x and break canonicals, sitemaps and old
// links). The one thing "none" drops is directory indexes, so a request for a
// path ending in "/" is answered with that directory's index.html here.
// Exact asset matches never reach this code — assets are served first.
export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    if (url.pathname.endsWith("/")) {
      url.pathname += "index.html";
      return env.ASSETS.fetch(new Request(url, request));
    }
    return env.ASSETS.fetch(request);
  },
};
