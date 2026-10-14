// Shared Worker for every blog moved to an m8k.io subdomain (2026-10-10).
//
// The blogs are served as static assets with html_handling "none", so every URL
// keeps its .html exactly as it did on GitHub Pages (Cloudflare's default
// handling would 307/308 /x.html -> /x and break canonicals, sitemaps and old
// links). The one thing "none" drops is directory indexes, so a request for a
// path ending in "/" is answered with that directory's index.html here.
//
// Agorai launch, 2026-10-14: the blogs' entries moved to Agorai. env.BLOG (set in
// each blog's wrangler config, with assets.run_worker_first so this runs before the
// files are served) picks that blog's map in agorai-redirects.json: an old entry URL
// gets a 301 to its article. A blog in HOME moved whole, so its other pages (home,
// tags, about) go to the matching place on Agorai; images, feeds and sitemaps still
// serve. The Ledger is not in HOME: its live boards stay here. West has no BLOG.
import MOVED from "./agorai-redirects.json";

const AGORAI = "https://agorai.m8k.io";
const HOME = { notebook: "/u/TheLibrarian", regimen: "/s/health", abroad: "/s/food" };

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    const blog = env.BLOG || "";
    const to = (MOVED[blog] || {})[url.pathname];
    if (to) return Response.redirect(AGORAI + to, 301);
    if (HOME[blog] && (url.pathname.endsWith("/") || url.pathname.endsWith(".html"))) {
      return Response.redirect(AGORAI + HOME[blog], 301);
    }
    if (url.pathname.endsWith("/")) {
      url.pathname += "index.html";
      return env.ASSETS.fetch(new Request(url, request));
    }
    return env.ASSETS.fetch(request);
  },
};
