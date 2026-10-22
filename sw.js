// Mister Translation's service worker: offline reading, nothing more (Michael 2026-10-22).
//
// Pages always come from the network first, so nothing is ever stale; each page that loads is kept,
// and only when there is no network does a kept copy stand in (or offline.html, which lists what's
// kept). The site's own versioned files (style.css?v=…, scripts, icons) are kept and reused. Nothing
// from other sites (verse cards on S3, YouTube, stats) and no audio is touched. Every path falls back
// to a plain fetch if anything here goes wrong, so this can never be what stops a page loading.
const PAGES = "mt-pages-v1";
const FILES = "mt-files-v1";
const KEEP = [PAGES, FILES];
const OFFLINE = "/offline.html";
const MAX_PAGES = 400;
const MAX_FILES = 300;   // pictures add up: the oldest go first

self.addEventListener("install", (e) => {
  e.waitUntil(caches.open(PAGES).then((c) => c.addAll([OFFLINE, "/"])).catch(() => {}).then(() => self.skipWaiting()));
});

self.addEventListener("activate", (e) => {
  e.waitUntil((async () => {
    for (const k of await caches.keys()) if (k.startsWith("mt-") && !KEEP.includes(k)) await caches.delete(k);
    if (self.registration.navigationPreload) await self.registration.navigationPreload.enable().catch(() => {});
    await self.clients.claim();
  })());
});

// A page is kept under its address without the query or #part (a chapter is the same chapter).
const pageKey = (url) => { const u = new URL(url); u.search = ""; u.hash = ""; return u.href; };

async function keepPage(url, res) {
  try {
    const c = await caches.open(PAGES);
    await c.put(pageKey(url), res);
    const keys = await c.keys();
    for (let i = 0; i < keys.length - MAX_PAGES; i++) await c.delete(keys[i]);   // the oldest go first
  } catch (e) { /* storage full or refused: reading still works */ }
}

async function page(e) {
  try {
    const res = (await e.preloadResponse) || (await fetch(e.request));
    if (res && res.ok && res.type === "basic") e.waitUntil(keepPage(e.request.url, res.clone()));
    return res;
  } catch (err) {
    const kept = await caches.match(pageKey(e.request.url), { cacheName: PAGES }).catch(() => null);
    if (kept) return kept;
    const off = await caches.match(OFFLINE, { cacheName: PAGES }).catch(() => null);
    return off || new Response("You're offline.", { headers: { "Content-Type": "text/plain; charset=utf-8" } });
  }
}

// The site's own files: reused when the address carries a version (?v=…), otherwise fetched fresh and kept.
async function file(e) {
  const url = new URL(e.request.url);
  try {
    const c = await caches.open(FILES);
    if (url.searchParams.has("v")) {
      const hit = await c.match(e.request);
      if (hit) return hit;
    }
    const res = await fetch(e.request);
    if (res && res.ok && res.type === "basic") e.waitUntil(c.put(e.request, res.clone()).then(() => c.keys())
      .then((keys) => Promise.all(keys.slice(0, Math.max(0, keys.length - MAX_FILES)).map((k) => c.delete(k)))).catch(() => {}));
    return res;
  } catch (err) {
    const hit = await caches.match(e.request, { ignoreSearch: true, cacheName: FILES }).catch(() => null);
    if (hit) return hit;
    throw err;
  }
}

self.addEventListener("fetch", (e) => {
  const req = e.request;
  if (req.method !== "GET") return;
  const url = new URL(req.url);
  if (url.origin !== self.location.origin) return;
  if (req.mode === "navigate") { e.respondWith(page(e).catch(() => fetch(req))); return; }
  if (req.headers.has("range") || /\.(mp3|m4a|mp4|webm|wav|ogg)$/i.test(url.pathname)) return;   // audio and video: the browser's own way
  if (/\.(css|js|woff2?|png|svg|jpe?g|webp|gif|ico|json|webmanifest)$/i.test(url.pathname)) e.respondWith(file(e).catch(() => fetch(req)));
});
