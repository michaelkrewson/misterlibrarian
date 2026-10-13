// agorai-verses.js — public discussion of a verse, or a few verses, on Agorai.
//
// reader-notes.js is the reader's PRIVATE margin (highlights and notes kept in this browser).
// This is the public one, hosted on Agorai (agorai.m8k.io): every chapter has one conversation,
// and any verse or run of verses can have its own.
//
//  - Each verse's ⋯ menu (reader-notes.js) gets "💬 Discuss" when this page carries an
//    Agorai target (build.py's _note_nudge: data-agorai-page / -square / -ref). Choosing it
//    selects that verse and opens a bar at the bottom of the screen; tapping other verses
//    stretches the selection (always one unbroken run, first to last), then "Discuss" opens
//    Agorai's page for exactly that passage (/discuss?url=<chapter>#verses-15-17). Agorai
//    reads the verses from this page itself, so the link can't put words in a verse's mouth.
//  - Verses that already have a conversation get a small 💬 count after their ⋯, and the
//    chapter's own button shows how many have joined in (from Agorai's /api/discussed).
//
// No-ops unless the page has both verses and an Agorai target (so Spanish pages, which have
// no target yet, and every non-chapter page are untouched).
(function () {
  "use strict";
  var host = document.querySelector("[data-agorai-page]");
  var verses = document.querySelectorAll(".vrs[id]");
  if (!host || !verses.length) return;

  var AGORAI = "https://agorai.m8k.io";
  var PAGE = host.getAttribute("data-agorai-page");          // https://mistertranslation.com/genesis-6.html
  var SQUARE = host.getAttribute("data-agorai-square") || "scripture";
  var REF = host.getAttribute("data-agorai-ref") || "";       // "Genesis 6"
  var MAX = 40;                                               // Agorai's limit for one passage

  window.mlAgorai = true;                                     // reader-notes.js shows "💬 Discuss" when set

  function numOf(vrs) {
    var n = vrs.querySelector(".vnum");
    var v = parseInt(n ? n.textContent : "", 10);
    if (v) return v;
    var m = /(\d+)$/.exec(vrs.id);
    return m ? +m[1] : 0;
  }
  var byNum = {};
  verses.forEach(function (v) { var n = numOf(v); if (n && !byNum[n]) byNum[n] = v; });

  function discussUrl(a, b) {
    var frag = a === b ? "#verse-" + a : "#verses-" + a + "-" + b;
    return AGORAI + "/discuss?url=" + encodeURIComponent(PAGE + frag) + "&s=" + encodeURIComponent(SQUARE);
  }
  function label(a, b) { return REF + ":" + a + (b > a ? "–" + b : ""); }

  // ------------------------------------------------------------------ styles ---
  var css = document.createElement("style");
  css.textContent =
    ".vrs.agv-sel{background:rgba(94,179,214,.13);box-shadow:inset 3px 0 0 #5eb3d6;border-radius:6px}" +
    ".agv-on .vrs{cursor:pointer}" +
    ".agv-bar{position:fixed;left:50%;bottom:16px;transform:translateX(-50%);z-index:60;display:flex;align-items:center;gap:10px;" +
      "max-width:calc(100% - 24px);padding:10px 12px 10px 16px;border-radius:14px;background:#0e1a2b;color:#e8eef7;" +
      "border:1px solid rgba(94,179,214,.45);box-shadow:0 10px 30px rgba(0,0,0,.45);font:15px/1.35 system-ui,-apple-system,sans-serif}" +
    ".agv-bar b{font-weight:650;white-space:nowrap}.agv-bar small{display:block;opacity:.7;font-size:12.5px}" +
    ".agv-bar .agv-go{background:#13d993;color:#04140d;border:0;border-radius:999px;padding:8px 14px;font-weight:700;cursor:pointer;white-space:nowrap}" +
    ".agv-bar .agv-x{background:none;border:0;color:#e8eef7;opacity:.7;font-size:20px;cursor:pointer;padding:2px 4px}" +
    ".agv-bub{display:inline-flex;align-items:center;gap:3px;margin-left:6px;padding:1px 7px;border-radius:999px;font-size:12.5px;" +
      "line-height:1.6;text-decoration:none;color:#5eb3d6;border:1px solid rgba(94,179,214,.4);vertical-align:middle;white-space:nowrap}" +
    ".agv-bub:hover{background:rgba(94,179,214,.12)}";
  document.head.appendChild(css);

  // -------------------------------------------------------- selecting verses ---
  var sel = null;                                  // { a, b }
  var bar = null;

  function paint() {
    verses.forEach(function (v) { v.classList.remove("agv-sel"); });
    if (!sel) return;
    for (var n = sel.a; n <= sel.b; n++) if (byNum[n]) byNum[n].classList.add("agv-sel");
    bar.querySelector(".agv-ref").textContent = label(sel.a, sel.b);
    bar.querySelector(".agv-tip").textContent = sel.b - sel.a + 1 >= MAX
      ? "That's the most one conversation can hold."
      : "Tap other verses to add them.";
  }

  function stop() {
    sel = null; paint();
    if (bar) { bar.remove(); bar = null; }
    document.documentElement.classList.remove("agv-on");
    document.removeEventListener("click", onTap, true);
    document.removeEventListener("keydown", onKey, true);
  }
  function onKey(e) { if (e.key === "Escape") stop(); }

  function onTap(e) {
    if (!sel || (bar && bar.contains(e.target))) return;
    var v = e.target.closest && e.target.closest(".vrs[id]");
    if (!v) return;
    if (e.target.closest("a, button, .v-menu, .v-editor")) return;   // links and tools keep working
    e.preventDefault(); e.stopPropagation();
    var n = numOf(v);
    if (!n) return;
    if (n === sel.a && n === sel.b) return;
    if (n >= sel.a && n <= sel.b) {                 // tapping inside the run shortens it to end there
      if (n - sel.a < sel.b - n) sel.a = n; else sel.b = n;
    } else if (n < sel.a) sel.a = Math.max(n, sel.b - MAX + 1);
    else sel.b = Math.min(n, sel.a + MAX - 1);
    paint();
  }

  function start(n) {
    stop();
    sel = { a: n, b: n };
    bar = document.createElement("div");
    bar.className = "agv-bar";
    bar.setAttribute("role", "dialog");
    bar.setAttribute("aria-label", "Discuss verses on Agorai");
    bar.innerHTML = '<span aria-hidden="true">💬</span><span><b class="agv-ref"></b><small class="agv-tip"></small></span>' +
      '<button type="button" class="agv-go">Discuss →</button><button type="button" class="agv-x" aria-label="Cancel">×</button>';
    document.body.appendChild(bar);
    bar.querySelector(".agv-go").addEventListener("click", function () {
      var url = discussUrl(sel.a, sel.b);
      stop();
      window.open(url, "_blank", "noopener");
    });
    bar.querySelector(".agv-x").addEventListener("click", stop);
    document.documentElement.classList.add("agv-on");
    setTimeout(function () {
      document.addEventListener("click", onTap, true);
      document.addEventListener("keydown", onKey, true);
    }, 0);
    paint();
  }

  document.addEventListener("ml:discuss", function (e) {
    var v = document.getElementById(e.detail && e.detail.verseId);
    var n = v ? numOf(v) : 0;
    if (n) start(n);
  });

  // ------------------------------------------------- what's already discussed ---
  function bubble(href, count, title) {
    var a = document.createElement("a");
    a.className = "agv-bub";
    a.href = href; a.target = "_blank"; a.rel = "noopener";
    a.title = title;
    a.textContent = "💬 " + count;
    return a;
  }
  fetch(AGORAI + "/api/discussed?url=" + encodeURIComponent(PAGE))
    .then(function (r) { return r.ok ? r.json() : null; })
    .then(function (d) {
      if (!d) return;
      if (d.chapter) {
        var btn = host.querySelector("[data-agorai-chapter]");
        if (btn) btn.textContent += " · " + d.chapter.posts;
      }
      (d.verses || []).forEach(function (t) {
        var v = byNum[t.from];
        if (!v) return;
        var anchor = v.querySelector(".v-tools") || v.querySelector(".eng") || v;
        var b = bubble(t.url, t.posts, label(t.from, t.to) + " on Agorai");
        if (anchor.classList && anchor.classList.contains("v-tools")) anchor.insertAdjacentElement("afterend", b);
        else anchor.appendChild(b);
      });
    })
    .catch(function () { /* Agorai unreachable: the page simply shows no counts */ });
})();
