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
// It speaks whichever language the page is in: `<html lang="es">` swaps the whole
// string table (see T) AND the verse-line selector (`.esp` rather than `.eng`).
// A verse is one verse in both editions, so a note taken on either side of the
// 🌐 toggle is the same note (see KEY_PATH).
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

  // ⚠ PATH is the page; KEY_PATH is the VERSE. Sharing must link to the edition
  // you are actually reading, but a note belongs to the verse, not to the
  // language you happened to read it in — so storage drops the ".es". Until
  // 2026-08-19 the key was PATH itself, which gave the same verse two separate
  // notebooks and made the 🌐 toggle look like it had wiped the reader's margin.
  var KEY_PATH = PATH.replace(/\.es\.html$/, ".html");

  function loadAll() {
    try { return JSON.parse(localStorage.getItem(STORE_KEY)) || {}; }
    catch (e) { return {}; }
  }
  function saveAll(obj) {
    try { localStorage.setItem(STORE_KEY, JSON.stringify(obj)); return true; }
    catch (e) { return false; } // quota / private-mode — fail quietly, never throw
  }
  var data = loadAll();

  function keyFor(verseId) { return KEY_PATH + "#" + verseId; }
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
  // ---- one-time migration: two per-edition notebooks -> one per verse -------
  // LOSSLESS BY CONSTRUCTION. Where only one edition holds a row it simply moves
  // across. Where BOTH do, the newer one leads and the older is kept underneath
  // it rather than dropped — a reader must never lose words they wrote to a
  // migration they did not ask for. Nothing is deleted from the merged store, so
  // reverting this commit only hides the Spanish rows behind the English key
  // again; it cannot destroy them.
  function mergeRows(a, b) {
    var newer = (a.updated || 0) >= (b.updated || 0) ? a : b;
    var older = newer === a ? b : a;
    var out = Object.assign({}, older, newer);   // newer wins field by field
    if (older.note && newer.note && older.note !== newer.note) {
      out.note = newer.note + "\n\n" + older.note;
    }
    return out;
  }
  (function migrateEditionKeys() {
    var legacy = Object.keys(data).filter(function (k) { return k.indexOf(".es.html#") > -1; });
    if (!legacy.length) return;
    legacy.forEach(function (k) {
      var to = k.replace(".es.html#", ".html#");
      var row = data[k];
      data[to] = data[to] ? mergeRows(row, data[to]) : row;
      delete data[k];
    });
    saveAll(data);   // a failed write (quota / private mode) just retries next load
  })();

  var CHAPTER_ID = "chapter";
  function getChapter() { return (data[keyFor(CHAPTER_ID)] || {}).note || ""; }

  // ------------------------------------------------------------------ i18n ---
  // The Spanish edition sets <html lang="es">; every other page on either site
  // is lang="en" (share.js branches on this same one line). The Spanish site is
  // a first-class page, not a courtesy translation, so EVERYTHING a reader can
  // see here is in T — labels, toasts, aria-labels, the shared text and the image
  // card's wordmark. What deliberately does NOT branch: the localStorage keys,
  // the /v/ stub URLs and the download filenames, which stay language-neutral so
  // the two editions can never disagree about an identity.
  var ES = (document.documentElement.lang || "").toLowerCase().indexOf("es") === 0;

  var STRINGS = {
    en: {
      brand: "Mister Translation",
      markA: "MiSTeR ", markB: "Translation",
      colors: [
        { id: "amber",  label: "Gold" },
        { id: "green",  label: "Green" },
        { id: "blue",   label: "Blue" },
        { id: "rose",   label: "Rose" },
        { id: "purple", label: "Violet" }
      ],
      highlightAs: function (c) { return "Highlight " + c; },
      noHighlight: "No highlight",
      removeHighlight: "Remove highlight",
      toolsFor: function (r) { return "Notes & sharing for " + r; },
      edit: "edit",
      noteOn: function (r) { return "Your note on " + r + "…"; },
      save: "Save", del: "Delete", cancel: "Cancel",
      noteSaved: "Note saved", noteDeleted: "Note deleted",
      addNote: "Add note", editNote: "Edit note",
      share: "🔗 Share",
      shareImage: "🖼 Share as image",
      copyVerse: "📋 Copy verse",
      highlighted: "Highlighted", highlightCleared: "Highlight removed",
      copied: "Copied", verseCopied: "Verse copied", linkCopied: "Link copied",
      chapterLinkCopied: "Chapter link copied",
      cardAlt: function (r) { return r + " — shareable card"; },
      cardCap: function (r) { return r + " · save or share this card"; },
      shareBtn: "Share", download: "Download", close: "Close",
      imageDownloaded: "Image downloaded",
      myNotesFor: function (r) { return "My notes for " + r; },
      chapterThought: "A thought on the whole chapter…",
      saved: "Saved",
      shareChapter: "🔗 Share chapter",
      localOnly: "Your notes &amp; highlights live only in this browser. ",
      exportBackup: "Export a backup", importBackup: "Import",
      nHighlights: function (n) { return n + " highlight" + (n > 1 ? "s" : ""); },
      nNotes: function (n) { return n + " note" + (n > 1 ? "s" : ""); },
      chapterNote: "chapter note",
      backupDownloaded: "Backup downloaded",
      imported: function (n) { return "Imported " + n + " item" + (n === 1 ? "" : "s"); },
      unreadable: "That file couldn't be read"
    },
    es: {
      brand: "La Traducción Mister",
      markA: "La Traducción ", markB: "Mister",
      colors: [
        { id: "amber",  label: "Oro" },
        { id: "green",  label: "Verde" },
        { id: "blue",   label: "Azul" },
        { id: "rose",   label: "Rosa" },
        { id: "purple", label: "Violeta" }
      ],
      highlightAs: function (c) { return "Resaltar en " + c.toLowerCase(); },
      noHighlight: "Sin resaltado",
      removeHighlight: "Quitar el resaltado",
      toolsFor: function (r) { return "Notas y compartir: " + r; },
      edit: "editar",
      noteOn: function (r) { return "Tu nota sobre " + r + "…"; },
      save: "Guardar", del: "Borrar", cancel: "Cancelar",
      noteSaved: "Nota guardada", noteDeleted: "Nota borrada",
      addNote: "Añadir una nota", editNote: "Editar la nota",
      share: "🔗 Compartir",
      shareImage: "🖼 Compartir como imagen",
      copyVerse: "📋 Copiar el versículo",
      highlighted: "Resaltado", highlightCleared: "Resaltado quitado",
      copied: "Copiado", verseCopied: "Versículo copiado",
      linkCopied: "Enlace copiado",
      chapterLinkCopied: "Enlace del capítulo copiado",
      cardAlt: function (r) { return r + " — tarjeta para compartir"; },
      cardCap: function (r) { return r + " · guarda o comparte esta tarjeta"; },
      shareBtn: "Compartir", download: "Descargar", close: "Cerrar",
      imageDownloaded: "Imagen descargada",
      myNotesFor: function (r) { return "Mis notas de " + r; },
      chapterThought: "Una idea sobre todo el capítulo…",
      saved: "Guardado",
      shareChapter: "🔗 Compartir el capítulo",
      localOnly: "Tus notas y resaltados viven solo en este navegador. ",
      exportBackup: "Exportar una copia", importBackup: "Importar",
      nHighlights: function (n) { return n + (n > 1 ? " resaltados" : " resaltado"); },
      nNotes: function (n) { return n + (n > 1 ? " notas" : " nota"); },
      chapterNote: "nota del capítulo",
      backupDownloaded: "Copia de seguridad descargada",
      imported: function (n) { return n + (n === 1 ? " elemento importado" : " elementos importados"); },
      unreadable: "No se pudo leer ese archivo"
    }
  };
  var T = ES ? STRINGS.es : STRINGS.en;

  // The verse line: ".eng" on the English edition, ".esp" on the Spanish one.
  // Before this existed the widget looked only for ".eng", so on EVERY Spanish
  // page "Copy verse" copied a reference with no verse attached to it and
  // "Share as image" rendered an empty card (found 2026-08-19).
  var LINE_SEL = ES ? ".esp" : ".eng";
  function verseLine(vrs) {
    return vrs.querySelector(LINE_SEL) || vrs.querySelector(".eng, .esp");
  }

  // ------------------------------------------------------------- references ---
  var COLORS = T.colors;

  // "/genesis-1.html" -> { book:"Genesis", ch:1 }; the verse number comes from the id.
  // The Spanish twin of a chapter is served as "<stem>.es.html", so the raw
  // filename stem is "jeremiah-23.es". Strip that suffix before parsing: without
  // it every Spanish page read its chapter as "23.es" (wrong ref on every note
  // label and share title) AND built its per-verse share link as
  // /v/jeremiah-23.es-5.html, which is a 404 — the real stubs are language-neutral
  // (/v/jeremiah-23-5.html). Found 2026-07-29 by looking at a rendered ES page.
  function baseStem() {
    return PATH.replace(/^.*\//, "").replace(/\.html$/, "").replace(/\.es$/, "");
  }
  function bookChapter() {
    var stem = baseStem();                                       // "genesis-1"
    var i = stem.lastIndexOf("-");
    var bookSlug = i < 0 ? stem : stem.slice(0, i);
    var ch = i < 0 ? "" : stem.slice(i + 1);
    var book = bookSlug.replace(/(^|-)([a-z])/g, function (_, sep, c) {
      return (sep ? " " : "") + c.toUpperCase();
    });
    return { book: book, ch: ch };
  }
  var BC = bookChapter();
  // The reference a reader SEES. The Spanish page's own <title> already carries
  // the localized book name ("Números 14 — La Traducción Mister"), so read it from
  // there rather than duplicating build.py's 66-entry ES_BOOK map in JS, where a
  // copy could silently drift. BC stays the source of truth for URLs and storage
  // keys. Falls back to BC unless the title's head really does end in this
  // chapter's number — which also quietly fixes the English side's slug-derived
  // "Song Of Solomon" to the title's own "Song of Solomon".
  var REF = (function () {
    var fallback = BC.book + " " + BC.ch;
    var head = (document.title || "").split("—")[0].trim();
    if (!head || !/^\d+$/.test(BC.ch)) return fallback;
    return new RegExp("(^|\\s)" + BC.ch + "$").test(head) ? head : fallback;
  })();
  function verseNum(verseId) {
    var m = /(\d+)$/.exec(verseId); // "v3" -> 3, "v11-5" -> 5
    return m ? m[1] : "";
  }
  function refOf(verseId) {
    var v = verseNum(verseId);
    return REF + (v ? ":" + v : "");
  }
  // Share the /v/ stub, not the raw #fragment: the stub carries this verse's own
  // Open Graph tags so the link unfurls with the verse text, then redirects a human
  // straight to the chapter anchor. STEM matches build.py's chapter_filename stem.
  var STEM = baseStem();                                       // "genesis-1"
  function urlFor(verseId) {
    return location.origin + "/" + "v/" + STEM + "-" + verseNum(verseId) + ".html";
  }

  // Clean text of a verse, in whichever language this edition is — drops the
  // "note" link and any cross-ref chips, keeps the words (including linked
  // entity words), collapses whitespace.
  function verseText(vrs) {
    var line = verseLine(vrs);
    if (!line) return "";
    var clone = line.cloneNode(true);
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
    var done = function () { toast(okMsg || T.copied); };
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
      '<span class="v-note-edit">' + T.edit + "</span>";
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

  // The inline note editor (textarea + save / delete).
  function openEditor(vrs, verseId) {
    closeMenu();
    var body = vrs.querySelector(".vbody") || vrs;
    if (vrs.querySelector(".v-editor")) return;
    var rec = get(verseId) || {};
    var wrap = document.createElement("div");
    wrap.className = "v-editor";
    wrap.innerHTML =
      '<textarea class="v-ta" rows="3" placeholder="' +
        T.noteOn(refOf(verseId)).replace(/"/g, "&quot;") + '"></textarea>' +
      '<div class="v-ed-row">' +
        '<button class="v-btn v-save">' + T.save + "</button>" +
        '<button class="v-btn v-del">' + T.del + "</button>" +
        '<button class="v-btn v-cancel">' + T.cancel + "</button>" +
      "</div>";
    body.appendChild(wrap);
    var ta = wrap.querySelector(".v-ta");
    ta.value = rec.note || "";
    ta.focus();
    ta.setSelectionRange(ta.value.length, ta.value.length);
    wrap.querySelector(".v-save").addEventListener("click", function () {
      set(verseId, { note: ta.value.trim() });
      wrap.remove(); renderNote(vrs, verseId); toast(T.noteSaved);
    });
    wrap.querySelector(".v-del").addEventListener("click", function () {
      set(verseId, { note: "" });
      wrap.remove(); renderNote(vrs, verseId); toast(T.noteDeleted);
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
        '" title="' + c.label + '" aria-label="' + T.highlightAs(c.label) + '"></button>';
    }).join("");
    var clearOn = rec.color ? "" : " v-sw-off";
    swatches += '<button class="v-sw v-sw-clear' + clearOn + '" data-color="" title="' +
      T.noHighlight + '" aria-label="' + T.removeHighlight + '">✕</button>';

    menu.innerHTML =
      '<div class="v-menu-ref">' + refOf(verseId).replace(/</g, "&lt;") + "</div>" +
      '<div class="v-sw-row">' + swatches + "</div>" +
      '<div class="v-menu-acts">' +
        '<button class="v-mi" data-act="note">📝 ' + (rec.note ? T.editNote : T.addNote) + "</button>" +
        '<button class="v-mi" data-act="share">' + T.share + "</button>" +
        '<button class="v-mi" data-act="image">' + T.shareImage + "</button>" +
        '<button class="v-mi" data-act="copytext">' + T.copyVerse + "</button>" +
      "</div>";

    document.body.appendChild(menu);
    positionMenu(trigger);

    menu.querySelectorAll(".v-sw").forEach(function (b) {
      b.addEventListener("click", function () {
        var color = b.getAttribute("data-color");
        set(verseId, { color: color });
        applyColor(vrs, color); refreshTrigger(vrs, verseId);
        closeMenu();
        toast(color ? T.highlighted : T.highlightCleared);
      });
    });
    menu.querySelectorAll(".v-mi").forEach(function (b) {
      b.addEventListener("click", function () {
        var act = b.getAttribute("data-act");
        closeMenu();
        if (act === "note") openEditor(vrs, verseId);
        else if (act === "share") shareVerse(vrs, verseId);
        else if (act === "image") shareImage(vrs, verseId);
        else if (act === "copytext") {
          copyText(verseText(vrs) + "\n— " + refOf(verseId) + ", " + T.brand + "\n" + urlFor(verseId),
            T.verseCopied);
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
        title: ref + " — " + T.brand,
        text: txt + "\n— " + ref,
        url: url
      }).catch(function () {}); // user cancelled — ignore
    } else {
      copyText(url, T.linkCopied);
    }
  }

  // ------------------------------------------------- share as an image card --
  function wrapLines(ctx, text, maxW) {
    var words = text.split(/\s+/), lines = [], cur = "";
    for (var i = 0; i < words.length; i++) {
      var t = cur ? cur + " " + words[i] : words[i];
      if (cur && ctx.measureText(t).width > maxW) { lines.push(cur); cur = words[i]; }
      else cur = t;
    }
    if (cur) lines.push(cur);
    return lines;
  }
  function roundRect(ctx, x, y, w, h, r) {
    ctx.beginPath();
    ctx.moveTo(x + r, y);
    ctx.arcTo(x + w, y, x + w, y + h, r);
    ctx.arcTo(x + w, y + h, x, y + h, r);
    ctx.arcTo(x, y + h, x, y, r);
    ctx.arcTo(x, y, x + w, y, r);
    ctx.closePath();
  }

  // Draw the verse + reference onto a themed canvas card (dark bg, gold accent,
  // this edition's own wordmark + the shared domain) sized to the verse's length.
  function renderCard(text, ref) {
    var S = 2, W = 1080, pad = 96, cw = W - pad * 2;
    var len = text.length;
    var vf = len <= 90 ? 54 : len <= 170 ? 48 : len <= 300 ? 42 : len <= 460 ? 36 : 32;
    var lh = Math.round(vf * 1.46);
    var canvas = document.createElement("canvas");
    var ctx = canvas.getContext("2d");
    var verseFont = vf + 'px Georgia, "Times New Roman", serif';
    ctx.font = verseFont;
    var lines = wrapLines(ctx, text, cw);

    var topPad = 104, verseH = lines.length * lh, afterVerse = 34, dividerH = 3,
        afterDivider = 30, refH = 42, footerGap = 74, brandH = 46, afterBrand = 10,
        domainH = 30, bottomPad = 84;
    var H = topPad + verseH + afterVerse + dividerH + afterDivider + refH +
            footerGap + brandH + afterBrand + domainH + bottomPad;
    if (H < 760) { topPad += (760 - H) / 2; H = 760; }
    H = Math.round(H);
    canvas.width = W * S; canvas.height = H * S;
    ctx.scale(S, S);

    // background + gold glow + frame
    var bg = ctx.createLinearGradient(0, 0, 0, H);
    bg.addColorStop(0, "#0d1520"); bg.addColorStop(1, "#060b14");
    ctx.fillStyle = bg; ctx.fillRect(0, 0, W, H);
    var glow = ctx.createRadialGradient(W / 2, -40, 30, W / 2, -40, W * 0.85);
    glow.addColorStop(0, "rgba(232,201,104,0.14)"); glow.addColorStop(1, "rgba(232,201,104,0)");
    ctx.fillStyle = glow; ctx.fillRect(0, 0, W, H);
    ctx.strokeStyle = "rgba(232,201,104,0.28)"; ctx.lineWidth = 2;
    roundRect(ctx, 26, 26, W - 52, H - 52, 22); ctx.stroke();

    // verse
    ctx.fillStyle = "#f2ecda";
    ctx.font = verseFont;
    ctx.textAlign = "center"; ctx.textBaseline = "top";
    var y = topPad;
    lines.forEach(function (ln) { ctx.fillText(ln, W / 2, y); y += lh; });

    // gold divider
    y += afterVerse;
    ctx.fillStyle = "rgba(232,201,104,0.75)";
    ctx.fillRect(W / 2 - 34, y, 68, dividerH);
    y += dividerH + afterDivider;

    // reference
    ctx.fillStyle = "#e8c968";
    ctx.font = '700 30px -apple-system, "Segoe UI", Roboto, Helvetica, Arial, sans-serif';
    try { ctx.letterSpacing = "3px"; } catch (e) {}
    ctx.fillText(ref.toUpperCase(), W / 2, y);
    try { ctx.letterSpacing = "0px"; } catch (e) {}

    // brand wordmark (two-tone) + domain, pinned to the bottom
    var domainTop = H - bottomPad - domainH;
    var brandTop = domainTop - afterBrand - brandH;
    ctx.font = '700 34px Georgia, "Times New Roman", serif';
    var p1 = T.markA, p2 = T.markB;
    var w1 = ctx.measureText(p1).width, w2 = ctx.measureText(p2).width;
    var startX = W / 2 - (w1 + w2) / 2;
    ctx.textAlign = "left"; ctx.textBaseline = "top";
    ctx.fillStyle = "#f7f2e2"; ctx.fillText(p1, startX, brandTop);
    ctx.fillStyle = "#e8c968"; ctx.fillText(p2, startX + w1, brandTop);
    ctx.textAlign = "center";
    ctx.fillStyle = "#7c8aa0";
    ctx.font = '400 22px -apple-system, "Segoe UI", Roboto, Helvetica, Arial, sans-serif';
    ctx.fillText("mistertranslation.com", W / 2, domainTop + 4);

    return canvas;
  }

  function shareImage(vrs, verseId) {
    var ref = refOf(verseId);
    var canvas = renderCard(verseText(vrs), ref);
    // Name the download off the language-neutral stem, not the visible
    // reference: byte-identical to the old English filenames
    // ("genesis-1-1.png"), and it stops a Spanish card saving as
    // "n-meros-14-1.png" once the accents are stripped.
    showImageModal(canvas, ref, STEM + "-" + verseNum(verseId) + ".png");
  }

  // A small preview overlay: shows the rendered card with share / download / close.
  function showImageModal(canvas, ref, fname) {
    var overlay = document.createElement("div");
    overlay.className = "ml-modal";
    var box = document.createElement("div");
    box.className = "ml-modal-box";
    var img = document.createElement("img");
    img.className = "ml-modal-img";
    img.alt = T.cardAlt(ref);
    img.src = canvas.toDataURL("image/png");
    var cap = document.createElement("div");
    cap.className = "ml-modal-cap";
    cap.textContent = T.cardCap(ref);
    var row = document.createElement("div");
    row.className = "ml-modal-row";
    function withBlob(cb) { canvas.toBlob(function (b) { if (b) cb(b); }, "image/png"); }

    var canShareFiles = false;
    try {
      canShareFiles = !!(navigator.canShare && navigator.share &&
        navigator.canShare({ files: [new File([new Blob()], fname, { type: "image/png" })] }));
    } catch (e) {}
    if (canShareFiles) {
      var shareBtn = document.createElement("button");
      shareBtn.className = "v-btn"; shareBtn.textContent = T.shareBtn;
      shareBtn.addEventListener("click", function () {
        withBlob(function (b) {
          navigator.share({ files: [new File([b], fname, { type: "image/png" })],
            title: ref + " — " + T.brand }).catch(function () {});
        });
      });
      row.appendChild(shareBtn);
    }
    var dl = document.createElement("button");
    dl.className = "v-btn"; dl.textContent = T.download;
    dl.addEventListener("click", function () {
      withBlob(function (b) {
        var a = document.createElement("a");
        a.href = URL.createObjectURL(b); a.download = fname;
        document.body.appendChild(a); a.click(); a.remove();
        setTimeout(function () { URL.revokeObjectURL(a.href); }, 1000);
        toast(T.imageDownloaded);
      });
    });
    row.appendChild(dl);
    var close = document.createElement("button");
    close.className = "v-btn v-cancel"; close.textContent = T.close;
    close.addEventListener("click", function () { teardown(); });
    row.appendChild(close);

    box.appendChild(img); box.appendChild(cap); box.appendChild(row);
    overlay.appendChild(box);
    document.body.appendChild(overlay);
    function teardown() { overlay.remove(); document.removeEventListener("keydown", onKey, true); }
    function onKey(e) { if (e.key === "Escape") teardown(); }
    overlay.addEventListener("click", function (e) { if (e.target === overlay) teardown(); });
    document.addEventListener("keydown", onKey, true);
  }

  // -------------------------------------------------- build per-verse tools --
  verses.forEach(function (vrs) {
    var verseId = vrs.id;
    // The opener flows INLINE at the end of the verse line (after any "note"
    // link) so it never overlaps the right-aligned Hebrew above it.
    var anchor = verseLine(vrs) || vrs.querySelector(".vbody") || vrs;
    var t = document.createElement("button");
    t.className = "v-tools";
    t.type = "button";
    t.setAttribute("aria-label", T.toolsFor(refOf(verseId)));
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
        '<span class="cn-ic">📓</span> ' + T.myNotesFor(REF) +
        '<span class="cn-count"></span><span class="cn-caret">›</span>' +
      "</button>" +
      '<div class="cn-body" hidden>' +
        '<textarea class="cn-ta" rows="4" placeholder="' + T.chapterThought + '"></textarea>' +
        '<div class="cn-row">' +
          '<button class="v-btn cn-save">' + T.save + "</button>" +
          '<span class="cn-saved"></span>' +
          '<span class="cn-spacer"></span>' +
          '<button class="v-btn cn-share">' + T.shareChapter + "</button>" +
        "</div>" +
        '<div class="cn-backup">' +
          T.localOnly +
          '<button class="cn-link cn-export">' + T.exportBackup + "</button> · " +
          '<button class="cn-link cn-import">' + T.importBackup + "</button>" +
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
      var prefix = KEY_PATH + "#";
      Object.keys(data).forEach(function (k) {
        if (k.indexOf(prefix) !== 0) return;
        if (k === keyFor(CHAPTER_ID)) return;
        var r = data[k];
        if (r.color) hl++;
        if (r.note) notes++;
      });
      var parts = [];
      if (hl) parts.push(T.nHighlights(hl));
      if (notes) parts.push(T.nNotes(notes));
      if (getChapter()) parts.push(T.chapterNote);
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
      savedEl.textContent = T.saved; setTimeout(function () { savedEl.textContent = ""; }, 1500);
      updateCount();
    });
    box.querySelector(".cn-share").addEventListener("click", function () {
      var url = location.origin + PATH;
      var title = REF + " — " + T.brand;
      if (navigator.share) navigator.share({ title: title, url: url }).catch(function () {});
      else copyText(url, T.chapterLinkCopied);
    });

    // ---- export / import (whole-site backup) ----
    box.querySelector(".cn-export").addEventListener("click", function () {
      var blob = new Blob([JSON.stringify(data, null, 2)], { type: "application/json" });
      var a = document.createElement("a");
      a.href = URL.createObjectURL(blob);
      a.download = "mister-translation-notes.json";
      document.body.appendChild(a); a.click(); a.remove();
      setTimeout(function () { URL.revokeObjectURL(a.href); }, 1000);
      toast(T.backupDownloaded);
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
          toast(T.imported(added));
          setTimeout(function () { location.reload(); }, 700); // re-render with merged notes
        } catch (e) { toast(T.unreadable); }
      };
      reader.readAsText(f);
      fileInput.value = "";
    });
  })();
})();
