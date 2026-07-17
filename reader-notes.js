// reader-notes.js — the reader's own margin.
//
// Lets a visitor highlight verses in colour, keep a private note on any verse or
// on the whole chapter, and share/copy a verse (link or text, native share sheet
// on mobile). EVERYTHING lives in the reader's own browser via localStorage —
// nothing is uploaded, no account, no server. An "Export / Import" pair backs the
// notes up to a file, since localStorage is per-browser and dies if site data is
// cleared.
//
// It runs on every page but no-ops instantly unless the page actually has verses
// (`.vrs[id]`), so the Library/Encyclopedia/About pages are untouched.
//
// All storage goes through the tiny load/save/get/set interface below, so a future
// cross-device sync (e.g. a Supabase-backed account) is a drop-in swap of those
// four functions — the UI never touches localStorage directly.
(function () {
  "use strict";

  var verses = document.querySelectorAll(".vrs[id]");
  if (!verses.length) return; // not a chapter page — do nothing

  // ---------------------------------------------------------------- storage ---
  var STORE_KEY = "ml-annotations-v1";
  var PATH = location.pathname; // e.g. "/genesis-1.html" — portable, matches the share URL

  function loadAll() {
    try { return JSON.parse(localStorage.getItem(STORE_KEY)) || {}; }
    catch (e) { return {}; }
  }
  function saveAll(obj) {
    try { localStorage.setItem(STORE_KEY, JSON.stringify(obj)); return true; }
    catch (e) { return false; } // quota / private-mode — fail quietly, never throw
  }
  var data = loadAll();

  function keyFor(verseId) { return PATH + "#" + verseId; }
  function get(verseId) { return data[keyFor(verseId)] || null; }
  function set(verseId, patch) {
    var k = keyFor(verseId);
    var next = Object.assign({}, data[k] || {}, patch, { updated: Date.now() });
    if (!next.note) delete next.note;
    if (!next.color) delete next.color;
    if (!next.note && !next.color) { delete data[k]; } // fully cleared → drop the row
    else data[k] = next;
    saveAll(data);
  }
  var CHAPTER_ID = "chapter";
  function getChapter() { return (data[keyFor(CHAPTER_ID)] || {}).note || ""; }

  // ------------------------------------------------------------- references ---
  var COLORS = [
    { id: "amber",  label: "Gold" },
    { id: "green",  label: "Green" },
    { id: "blue",   label: "Blue" },
    { id: "rose",   label: "Rose" },
    { id: "purple", label: "Violet" }
  ];

  // "/genesis-1.html" -> { book:"Genesis", ch:1 }; the verse number comes from the id.
  function bookChapter() {
    var stem = PATH.replace(/^.*\//, "").replace(/\.html$/, ""); // "genesis-1"
    var i = stem.lastIndexOf("-");
    var bookSlug = i < 0 ? stem : stem.slice(0, i);
    var ch = i < 0 ? "" : stem.slice(i + 1);
    var book = bookSlug.replace(/(^|-)([a-z])/g, function (_, sep, c) {
      return (sep ? " " : "") + c.toUpperCase();
    });
    return { book: book, ch: ch };
  }
  var BC = bookChapter();
  function verseNum(verseId) {
    var m = /(\d+)$/.exec(verseId); // "v3" -> 3, "v11-5" -> 5
    return m ? m[1] : "";
  }
  function refOf(verseId) {
    var v = verseNum(verseId);
    return BC.book + " " + BC.ch + (v ? ":" + v : "");
  }
  function urlFor(verseId) { return location.origin + PATH + "#" + verseId; }

  // Clean English text of a verse — drops the "note" link and any cross-ref chips,
  // keeps the words (including linked entity words), collapses whitespace.
  function verseText(vrs) {
    var eng = vrs.querySelector(".eng");
    if (!eng) return "";
    var clone = eng.cloneNode(true);
    clone.querySelectorAll(".notelink, .xrefs, .vclip, .v-tools, .v-note, .v-editor")
      .forEach(function (n) { n.remove(); });
    return (clone.textContent || "").replace(/\s+/g, " ").trim();
  }

  // ---------------------------------------------------------------- toast ----
  var toastEl = null, toastTimer = null;
  function toast(msg) {
    if (!toastEl) {
      toastEl = document.createElement("div");
      toastEl.className = "ml-toast";
      document.body.appendChild(toastEl);
    }
    toastEl.textContent = msg;
    toastEl.classList.add("show");
    clearTimeout(toastTimer);
    toastTimer = setTimeout(function () { toastEl.classList.remove("show"); }, 1700);
  }
  function copyText(text, okMsg) {
    var done = function () { toast(okMsg || "Copied"); };
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(text).then(done, function () { legacyCopy(text, done); });
    } else { legacyCopy(text, done); }
  }
  function legacyCopy(text, done) {
    var ta = document.createElement("textarea");
    ta.value = text; ta.style.position = "fixed"; ta.style.opacity = "0";
    document.body.appendChild(ta); ta.select();
    try { document.execCommand("copy"); done(); } catch (e) {}
    document.body.removeChild(ta);
  }

  // ------------------------------------------------------- per-verse UI ------
  function applyColor(vrs, color) {
    if (color) vrs.setAttribute("data-hl", color);
    else vrs.removeAttribute("data-hl");
  }

  // Render (or refresh) the saved-note block that shows under a verse.
  function renderNote(vrs, verseId) {
    var body = vrs.querySelector(".vbody") || vrs;
    var existing = vrs.querySelector(".v-note");
    var rec = get(verseId);
    var noteText = rec && rec.note;
    if (!noteText) { if (existing) existing.remove(); refreshTrigger(vrs, verseId); return; }
    if (!existing) {
      existing = document.createElement("div");
      existing.className = "v-note";
      existing.addEventListener("click", function () { openEditor(vrs, verseId); });
      body.appendChild(existing);
    }
    existing.innerHTML = '<span class="v-note-ic">📝</span><span class="v-note-tx"></span>' +
      '<span class="v-note-edit">edit</span>';
    existing.querySelector(".v-note-tx").textContent = noteText;
    refreshTrigger(vrs, verseId);
  }

  // The little "⋯" opener button appended to each verse.
  function refreshTrigger(vrs, verseId) {
    var t = vrs.querySelector(".v-tools");
    if (!t) return;
    var rec = get(verseId);
    t.classList.toggle("has-note", !!(rec && rec.note));
    t.classList.toggle("has-hl", !!(rec && rec.color));
  }

  // The inline note editor (textarea + Save / Delete).
  function openEditor(vrs, verseId) {
    closeMenu();
    var body = vrs.querySelector(".vbody") || vrs;
    if (vrs.querySelector(".v-editor")) return;
    var rec = get(verseId) || {};
    var wrap = document.createElement("div");
    wrap.className = "v-editor";
    wrap.innerHTML =
      '<textarea class="v-ta" rows="3" placeholder="Your note on ' +
        refOf(verseId).replace(/"/g, "&quot;") + '…"></textarea>' +
      '<div class="v-ed-row">' +
        '<button class="v-btn v-save">Save</button>' +
        '<button class="v-btn v-del">Delete</button>' +
        '<button class="v-btn v-cancel">Cancel</button>' +
      "</div>";
    body.appendChild(wrap);
    var ta = wrap.querySelector(".v-ta");
    ta.value = rec.note || "";
    ta.focus();
    ta.setSelectionRange(ta.value.length, ta.value.length);
    wrap.querySelector(".v-save").addEventListener("click", function () {
      set(verseId, { note: ta.value.trim() });
      wrap.remove(); renderNote(vrs, verseId); toast("Note saved");
    });
    wrap.querySelector(".v-del").addEventListener("click", function () {
      set(verseId, { note: "" });
      wrap.remove(); renderNote(vrs, verseId); toast("Note deleted");
    });
    wrap.querySelector(".v-cancel").addEventListener("click", function () { wrap.remove(); });
    ta.addEventListener("keydown", function (e) {
      if (e.key === "Escape") wrap.remove();
      if ((e.metaKey || e.ctrlKey) && e.key === "Enter") wrap.querySelector(".v-save").click();
    });
  }

  // ----------------------------------------------------- shared popover ------
  var menu = null;
  function closeMenu() {
    if (menu) { menu.remove(); menu = null; }
    document.removeEventListener("keydown", onMenuKey, true);
    document.removeEventListener("click", onOutside, true);
  }
  function onMenuKey(e) { if (e.key === "Escape") closeMenu(); }
  function onOutside(e) { if (menu && !menu.contains(e.target) && !e.target.closest(".v-tools")) closeMenu(); }

  function openMenu(trigger, vrs, verseId) {
    closeMenu();
    var rec = get(verseId) || {};
    menu = document.createElement("div");
    menu.className = "v-menu";

    // colour swatches
    var swatches = COLORS.map(function (c) {
      var on = rec.color === c.id ? " on" : "";
      return '<button class="v-sw v-sw-' + c.id + on + '" data-color="' + c.id +
        '" title="' + c.label + '" aria-label="Highlight ' + c.label + '"></button>';
    }).join("");
    var clearOn = rec.color ? "" : " v-sw-off";
    swatches += '<button class="v-sw v-sw-clear' + clearOn + '" data-color="" title="No highlight" aria-label="Remove highlight">✕</button>';

    menu.innerHTML =
      '<div class="v-menu-ref">' + refOf(verseId).replace(/</g, "&lt;") + "</div>" +
      '<div class="v-sw-row">' + swatches + "</div>" +
      '<div class="v-menu-acts">' +
        '<button class="v-mi" data-act="note">📝 ' + (rec.note ? "Edit note" : "Add note") + "</button>" +
        '<button class="v-mi" data-act="share">🔗 Share</button>' +
        '<button class="v-mi" data-act="copytext">📋 Copy verse</button>' +
      "</div>";

    document.body.appendChild(menu);
    positionMenu(trigger);

    menu.querySelectorAll(".v-sw").forEach(function (b) {
      b.addEventListener("click", function () {
        var color = b.getAttribute("data-color");
        set(verseId, { color: color });
        applyColor(vrs, color); refreshTrigger(vrs, verseId);
        closeMenu();
        toast(color ? "Highlighted" : "Highlight removed");
      });
    });
    menu.querySelectorAll(".v-mi").forEach(function (b) {
      b.addEventListener("click", function () {
        var act = b.getAttribute("data-act");
        closeMenu();
        if (act === "note") openEditor(vrs, verseId);
        else if (act === "share") shareVerse(vrs, verseId);
        else if (act === "copytext") {
          copyText(verseText(vrs) + "\n— " + refOf(verseId) + ", MiSTeR Translation\n" + urlFor(verseId),
            "Verse copied");
        }
      });
    });

    setTimeout(function () {
      document.addEventListener("keydown", onMenuKey, true);
      document.addEventListener("click", onOutside, true);
    }, 0);
  }

  function positionMenu(trigger) {
    var r = trigger.getBoundingClientRect();
    var mw = menu.offsetWidth, mh = menu.offsetHeight;
    var top = window.scrollY + r.bottom + 6;
    var left = window.scrollX + r.right - mw;
    if (left < 8) left = 8;
    var maxLeft = window.scrollX + document.documentElement.clientWidth - mw - 8;
    if (left > maxLeft) left = maxLeft;
    // flip above if it would run off the bottom of the viewport
    if (r.bottom + mh + 10 > window.innerHeight && r.top - mh - 6 > 0) {
      top = window.scrollY + r.top - mh - 6;
    }
    menu.style.top = top + "px";
    menu.style.left = left + "px";
  }

  function shareVerse(vrs, verseId) {
    var url = urlFor(verseId);
    var ref = refOf(verseId);
    var txt = verseText(vrs);
    if (navigator.share) {
      navigator.share({
        title: ref + " — MiSTeR Translation",
        text: txt + "\n— " + ref,
        url: url
      }).catch(function () {}); // user cancelled — ignore
    } else {
      copyText(url, "Link copied");
    }
  }

  // -------------------------------------------------- build per-verse tools --
  verses.forEach(function (vrs) {
    var verseId = vrs.id;
    // The opener flows INLINE at the end of the English line (after any "note"
    // link) so it never overlaps the right-aligned Hebrew above it.
    var anchor = vrs.querySelector(".eng") || vrs.querySelector(".vbody") || vrs;
    var t = document.createElement("button");
    t.className = "v-tools";
    t.type = "button";
    t.setAttribute("aria-label", "Notes & sharing for " + refOf(verseId));
    t.innerHTML = "⋯";
    t.addEventListener("click", function (e) {
      e.stopPropagation();
      if (menu) { closeMenu(); return; }
      openMenu(t, vrs, verseId);
    });
    anchor.appendChild(t);

    var rec = get(verseId);
    if (rec && rec.color) applyColor(vrs, rec.color);
    if (rec && rec.note) renderNote(vrs, verseId);
    else refreshTrigger(vrs, verseId);
  });

  // ---------------------------------------------------- chapter-note panel ---
  // Insert a compact "my notes for this chapter" block at the top of the verse area.
  (function chapterPanel() {
    var first = verses[0];
    var host = first.parentNode; // the .panel that wraps the verses
    var box = document.createElement("div");
    box.className = "chap-notes";
    box.innerHTML =
      '<button class="cn-toggle" type="button">' +
        '<span class="cn-ic">📓</span> My notes for ' + BC.book + " " + BC.ch +
        '<span class="cn-count"></span><span class="cn-caret">›</span>' +
      "</button>" +
      '<div class="cn-body" hidden>' +
        '<textarea class="cn-ta" rows="4" placeholder="A thought on the whole chapter…"></textarea>' +
        '<div class="cn-row">' +
          '<button class="v-btn cn-save">Save</button>' +
          '<span class="cn-saved"></span>' +
          '<span class="cn-spacer"></span>' +
          '<button class="v-btn cn-share">🔗 Share chapter</button>' +
        "</div>" +
        '<div class="cn-backup">' +
          "Your notes &amp; highlights live only in this browser. " +
          '<button class="cn-link cn-export">Export a backup</button> · ' +
          '<button class="cn-link cn-import">Import</button>' +
          '<input type="file" class="cn-file" accept="application/json,.json" hidden>' +
        "</div>" +
      "</div>";
    host.insertBefore(box, first);

    var toggle = box.querySelector(".cn-toggle");
    var bodyEl = box.querySelector(".cn-body");
    var ta = box.querySelector(".cn-ta");
    var savedEl = box.querySelector(".cn-saved");
    ta.value = getChapter();

    function updateCount() {
      var hl = 0, notes = 0;
      var prefix = PATH + "#";
      Object.keys(data).forEach(function (k) {
        if (k.indexOf(prefix) !== 0) return;
        if (k === keyFor(CHAPTER_ID)) return;
        var r = data[k];
        if (r.color) hl++;
        if (r.note) notes++;
      });
      var parts = [];
      if (hl) parts.push(hl + " highlight" + (hl > 1 ? "s" : ""));
      if (notes) parts.push(notes + " note" + (notes > 1 ? "s" : ""));
      if (getChapter()) parts.push("chapter note");
      var c = box.querySelector(".cn-count");
      c.textContent = parts.length ? "  ·  " + parts.join(", ") : "";
    }
    updateCount();

    toggle.addEventListener("click", function () {
      var open = bodyEl.hasAttribute("hidden");
      if (open) { bodyEl.removeAttribute("hidden"); box.classList.add("open"); ta.focus(); }
      else { bodyEl.setAttribute("hidden", ""); box.classList.remove("open"); }
    });
    box.querySelector(".cn-save").addEventListener("click", function () {
      set(CHAPTER_ID, { note: ta.value.trim() });
      savedEl.textContent = "Saved"; setTimeout(function () { savedEl.textContent = ""; }, 1500);
      updateCount();
    });
    box.querySelector(".cn-share").addEventListener("click", function () {
      var url = location.origin + PATH;
      var title = BC.book + " " + BC.ch + " — MiSTeR Translation";
      if (navigator.share) navigator.share({ title: title, url: url }).catch(function () {});
      else copyText(url, "Chapter link copied");
    });

    // ---- export / import (whole-site backup) ----
    box.querySelector(".cn-export").addEventListener("click", function () {
      var blob = new Blob([JSON.stringify(data, null, 2)], { type: "application/json" });
      var a = document.createElement("a");
      a.href = URL.createObjectURL(blob);
      a.download = "mister-translation-notes.json";
      document.body.appendChild(a); a.click(); a.remove();
      setTimeout(function () { URL.revokeObjectURL(a.href); }, 1000);
      toast("Backup downloaded");
    });
    var fileInput = box.querySelector(".cn-file");
    box.querySelector(".cn-import").addEventListener("click", function () { fileInput.click(); });
    fileInput.addEventListener("change", function () {
      var f = fileInput.files && fileInput.files[0];
      if (!f) return;
      var reader = new FileReader();
      reader.onload = function () {
        try {
          var incoming = JSON.parse(reader.result);
          if (!incoming || typeof incoming !== "object") throw 0;
          var added = 0;
          Object.keys(incoming).forEach(function (k) {
            var inc = incoming[k], cur = data[k];
            // merge: newer 'updated' wins; brand-new keys are added
            if (!cur || (inc.updated || 0) >= (cur.updated || 0)) { data[k] = inc; added++; }
          });
          saveAll(data);
          toast("Imported " + added + " item" + (added === 1 ? "" : "s"));
          setTimeout(function () { location.reload(); }, 700); // re-render with merged notes
        } catch (e) { toast("That file couldn't be read"); }
      };
      reader.readAsText(f);
      fileInput.value = "";
    });
  })();
})();
