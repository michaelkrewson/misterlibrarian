// Shared Worker for every blog moved to an m8k.io subdomain (2026-10-10).
//
// The blogs are served as static assets with html_handling "none", so every URL
// keeps its .html exactly as it did on GitHub Pages (Cloudflare's default
// handling would 307/308 /x.html -> /x and break canonicals, sitemaps and old
// links). The one thing "none" drops is directory indexes, so a request for a
// path ending in "/" is answered with that directory's index.html here.
//
// Micwyn launch, 2026-10-14: the blogs' entries moved to Micwyn. env.BLOG (set in
// each blog's wrangler config, with assets.run_worker_first so this runs before the
// files are served) picks that blog's map in agorai-redirects.json: an old entry URL
// gets a 301 to its article. A blog in HOME moved whole, so its other pages (home,
// tags, about) go to the matching place on Micwyn; images, feeds and sitemaps still
// serve. The Ledger is not in HOME: its live boards stay here. West's BLOG has no map.
import MOVED from "./agorai-redirects.json";

const AGORAI = "https://micwyn.com";
const HOME = { notebook: "/u/TheLibrarian", regimen: "/s/health", abroad: "/s/food" };

// Paths Google kept asking for that never existed here (Search Console 404s, 2026-10-25):
// sent to the nearest real page on the same host.
const STRAY = { west: { "/west": "/" }, ledger: { "/mempool": "/bitcoin.html" } };

// Does this blog answer the path with a redirect instead of a page?
const redirects = (blog, path) =>
  !!(MOVED[blog] || {})[path] || (!!HOME[blog] && (path.endsWith("/") || path.endsWith(".html")));

// A sitemap lists only pages that are really here: a URL that 301s to Micwyn is
// dropped as the file is served (Search Console flags "Page with redirect" for any
// that stay listed), so the builders' sitemaps can stay as they are.
async function sitemap(request, env, blog) {
  const res = await env.ASSETS.fetch(request);
  if (!res.ok) return res;
  const xml = (await res.text()).replace(/[ \t]*<url>[\s\S]*?<\/url>\s*/g, (block) => {
    const loc = /<loc>([^<]*)<\/loc>/.exec(block);
    return loc && redirects(blog, new URL(loc[1]).pathname) ? "" : block;
  });
  const headers = new Headers(res.headers);
  headers.delete("content-length");
  return new Response(xml, { headers });
}

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    const blog = env.BLOG || "";
    const stray = (STRAY[blog] || {})[url.pathname];
    if (stray) return Response.redirect(url.origin + stray, 301);
    if (url.pathname === "/sitemap.xml" && (MOVED[blog] || HOME[blog])) return sitemap(request, env, blog);
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
