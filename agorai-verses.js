// agorai-verses.js — public discussion of a verse, or a few verses, on Micwyn.
//
// reader-notes.js is the reader's PRIVATE margin (highlights and notes kept in this browser).
// This is the public one, hosted on Micwyn (micwyn.com): every chapter has one conversation,
// and any verse or run of verses can have its own.
//
//  - Each verse's ⋯ menu (reader-notes.js) gets "💬 Discuss" when this page carries an
//    Micwyn target (build.py's _note_nudge: data-agorai-page / -square / -ref). Choosing it
//    selects that verse and opens a bar at the bottom of the screen; tapping other verses
//    stretches the selection (always one unbroken run, first to last), then "Discuss" opens
//    Micwyn's page for exactly that passage (/discuss?url=<chapter>#verses-15-17). Micwyn
//    reads the verses from this page itself, so the link can't put words in a verse's mouth.
//  - Verses that already have a conversation get a small 💬 count after their ⋯, and the
//    chapter's own button shows how many have joined in (from Micwyn's /api/discussed).
//  - Under the last verse (above the Translator's Notes), a "Conversations about <chapter>" box
//    (2026-10-19): how many people are talking, the latest few comments one line each, and a
//    "Write a comment…" box. It's a WINDOW, not a copy: the conversation lives on Micwyn, and
//    posting carries the typed text there (in the address's #draft= part) where it goes up as a
//    guest, no account needed (Micwyn allows 3 guest comments, then asks them to sign in). This
//    page never hosts anyone's comments: Google credits them to Micwyn, and AdSense, which judges
//    a whole site, never sees a heated thread here. Loaded by script, so nothing here is indexed.
//
// No-ops unless the page has both verses and an Micwyn target (so Spanish pages, which have
// no target yet, and every non-chapter page are untouched).
(function () {
  "use strict";
  var host = document.querySelector("[data-agorai-page]");
  var verses = document.querySelectorAll(".vrs[id]");
  if (!host || !verses.length) return;

  var AGORAI = "https://micwyn.com";
  var PAGE = host.getAttribute("data-agorai-page");          // https://mistertranslation.com/genesis-6.html
  var SQUARE = host.getAttribute("data-agorai-square") || "scripture";
  var REF = host.getAttribute("data-agorai-ref") || "";       // "Genesis 6"
  var MAX = 40;                                               // Micwyn's limit for one passage

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
    ".agv-bub:hover{background:rgba(94,179,214,.12)}" +
    ".agv-convo{max-width:760px;margin:30px auto 8px;padding:18px 20px;background:var(--bg1,#0a0f1a);border:1px solid var(--border,rgba(255,255,255,.08));" +
      "border-radius:14px;font:14px/1.6 system-ui,-apple-system,sans-serif;color:var(--text,#e2e8f0)}" +
    ".agv-convo h2{margin:0 0 4px;font-size:11px;letter-spacing:.12em;text-transform:uppercase;color:var(--muted,#94a3b8)}" +
    ".agv-convo .agv-count{margin:0 0 12px;font-size:15px;font-weight:650}" +
    ".agv-convo ol{list-style:none;margin:0 0 12px;padding:0}" +
    ".agv-convo li{padding:9px 0;border-top:1px solid var(--border,rgba(255,255,255,.08))}" +
    ".agv-convo li:first-child{border-top:0}" +
    ".agv-who{font-weight:650;margin-right:6px}.agv-when{color:var(--muted,#94a3b8);font-size:12.5px}" +
    ".agv-ai{display:inline-block;margin-right:6px;padding:0 6px;border-radius:6px;font-size:11px;font-weight:700;background:rgba(94,179,214,.16);color:#5eb3d6}" +
    ".agv-line{display:block;color:var(--text,#e2e8f0)}" +
    ".agv-read{display:inline-block;margin:0 0 14px;color:var(--gold,#e8c968);font-weight:650;text-decoration:none}" +
    ".agv-read:hover{text-decoration:underline}" +
    ".agv-convo textarea{box-sizing:border-box;width:100%;min-height:84px;padding:10px 12px;border-radius:10px;resize:vertical;" +
      "font:15px/1.5 system-ui,-apple-system,sans-serif;color:var(--text,#e2e8f0);background:var(--bg2,#0d1520);border:1px solid var(--border,rgba(255,255,255,.12))}" +
    ".agv-convo textarea:focus{outline:2px solid rgba(232,201,104,.5);outline-offset:1px}" +
    ".agv-row{display:flex;flex-wrap:wrap;align-items:center;gap:10px 14px;margin-top:10px}" +
    ".agv-post{background:var(--gold,#e8c968);color:#0b1929;border:0;border-radius:999px;padding:9px 18px;font-weight:700;font-size:14px;cursor:pointer}" +
    ".agv-post[disabled]{opacity:.5;cursor:default}" +
    ".agv-fine{color:var(--muted,#94a3b8);font-size:12.5px}" +
    ".agv-jump{margin-left:10px;font-size:13px;color:var(--muted,#94a3b8);text-decoration:none;align-self:center}" +
    ".agv-jump:hover{color:var(--text,#e2e8f0)}";
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
    bar.setAttribute("aria-label", "Discuss verses on Micwyn");
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
  // ------------------------------------------ the conversation under the chapter ---
  function ago(t) {
    var s = Math.max(0, Date.now() / 1000 - t);
    if (s < 3600) return Math.max(1, Math.round(s / 60)) + " min ago";
    if (s < 86400) return Math.round(s / 3600) + " h ago";
    if (s < 86400 * 30) { var d = Math.round(s / 86400); return d + (d === 1 ? " day ago" : " days ago"); }
    return new Date(t * 1000).toLocaleDateString(undefined, { month: "short", day: "numeric", year: "numeric" });
  }
  function el(tag, cls, text) {
    var e = document.createElement(tag);
    if (cls) e.className = cls;
    if (text != null) e.textContent = text;
    return e;
  }
  // The conversation box, built from Micwyn's preview (d.chapter: url, people, latest[]) or empty.
  function convoBox(chapter, verseCount) {
    var box = el("section", "agv-convo");
    box.id = "conversation";
    box.setAttribute("aria-label", "Conversations about " + REF);
    box.appendChild(el("h2", null, "Conversations about " + REF));
    var latest = (chapter && chapter.latest) || [];
    if (chapter && latest.length) {
      var n = chapter.people || 1;
      box.appendChild(el("p", "agv-count", "💬 " + n + (n === 1 ? " person is" : " people are") + " talking about this chapter"));
      var ol = el("ol");
      latest.forEach(function (p) {
        var li = el("li");
        if (p.ai) li.appendChild(el("span", "agv-ai", "AI"));
        li.appendChild(el("span", "agv-who", p.name || "Someone"));
        li.appendChild(el("span", "agv-when", ago(p.at)));
        li.appendChild(el("span", "agv-line", p.text));
        ol.appendChild(li);
      });
      box.appendChild(ol);
      var read = el("a", "agv-read", "Read the whole conversation →");
      read.href = chapter.url; read.target = "_blank"; read.rel = "noopener";
      box.appendChild(read);
    } else {
      box.appendChild(el("p", "agv-count", "No one has started talking about " + REF + " yet."));
    }
    var ta = el("textarea");
    ta.setAttribute("aria-label", "Write a comment");
    ta.placeholder = latest.length ? "Add your thoughts…" : "What stood out to you in this chapter? Start the conversation…";
    ta.maxLength = 4000;
    box.appendChild(ta);
    var row = el("div", "agv-row");
    var post = el("button", "agv-post", "Post on Micwyn →");
    post.type = "button";
    post.disabled = true;
    row.appendChild(post);
    row.appendChild(el("span", "agv-fine", "No account needed. It opens on Micwyn, our discussion forum, ready to post."));
    box.appendChild(row);
    if (verseCount) {
      box.appendChild(el("p", "agv-fine", "Plus " + verseCount + (verseCount === 1 ? " conversation" : " conversations") +
        " about single verses (marked 💬). Tap a verse's ⋯ to start one."));
    }
    ta.addEventListener("input", function () { post.disabled = !ta.value.trim(); });
    post.addEventListener("click", function () {
      var text = ta.value.trim();
      if (!text) return;
      // Micwyn sends the chapter's conversation (or its start page) and fills the reply box from #draft=.
      var url = AGORAI + "/discuss?url=" + encodeURIComponent(PAGE) + "&title=" + encodeURIComponent(REF) +
        "&s=" + encodeURIComponent(SQUARE) + "#draft=" + encodeURIComponent(text);
      window.open(url, "_blank", "noopener");
      ta.value = ""; post.disabled = true;
    });
    return box;
  }
  function placeBox(box) {
    var last = verses[verses.length - 1];
    last.insertAdjacentElement("afterend", box);
  }

  var placed = false;
  fetch(AGORAI + "/api/discussed?url=" + encodeURIComponent(PAGE))
    .then(function (r) { return r.ok ? r.json() : null; })
    .then(function (d) {
      if (!d) return;
      placeBox(convoBox(d.chapter, (d.verses || []).length));
      placed = true;
      if (d.chapter) {
        var btn = host.querySelector("[data-agorai-chapter]");
        if (btn) btn.textContent += " · " + d.chapter.posts;
        // Near the top: a way down to the comments, for readers who'd rather read them first.
        if (d.chapter.latest && d.chapter.latest.length && btn) {
          var jump = el("a", "agv-jump", "Read the comments ↓");
          jump.href = "#conversation";
          btn.insertAdjacentElement("afterend", jump);
        }
      }
      (d.verses || []).forEach(function (t) {
        var v = byNum[t.from];
        if (!v) return;
        var anchor = v.querySelector(".v-tools") || v.querySelector(".eng") || v;
        var b = bubble(t.url, t.posts, label(t.from, t.to) + " on Micwyn");
        if (anchor.classList && anchor.classList.contains("v-tools")) anchor.insertAdjacentElement("afterend", b);
        else anchor.appendChild(b);
      });
    })
    .catch(function () { /* Micwyn unreachable: no counts, and the box below offers a fresh start */ })
    .then(function () { if (!placed) placeBox(convoBox(null, 0)); });
})();
