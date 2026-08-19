// Chapter audio reader for The MisterLibrarian Bible Project.
//
// Two ways to hear a chapter read aloud, tried in this order:
//
//   1. A pre-generated narration MP3, when one exists for this chapter. The
//      build stamps the Listen button with data-audio="audio/genesis-N.mp3"
//      only when that file is actually present, so every reader hears the same
//      single warm-narrator voice. Generate those files with gen_audio.py.
//
//   2. Browser speech (the Web Speech API) as a zero-cost fallback that works
//      on any device with no files to host. It reads each verse in order,
//      highlights the verse being spoken, and lets the reader pick a voice and a
//      speaking speed (both remembered in localStorage). Nothing is sent
//      anywhere — the speech is synthesized on the reader's own device.
//
// It follows the page's own language. `<html lang="es">` swaps the verse-line
// selector (`.esp`, not `.eng`), the offered voices, the utterance's `lang`, and
// every label — the same one-line detection share.js and reader-notes.js use.
// ⚠ Spanish chapter pages currently ship NO Listen button, so none of this is
// reachable yet; it is wired now so that adding the button is the only step
// left, rather than the day it is added being the day this is found broken
// (reader-notes.js shipped the identical `.eng`-only assumption and silently
// blanked every Spanish share card until 2026-08-19).
//
// The Listen button lives in the chapter togglebar as #audiotgl. Nothing loads
// or plays until the reader clicks it.

(function () {
  "use strict";

  var ES = (document.documentElement.lang || "").toLowerCase().indexOf("es") === 0;

  var STRINGS = {
    en: {
      lineSel: ".eng",
      voiceLang: "en", homeRegion: "GB", defaultVoiceLang: "en-US",
      voiceKey: "mtlib_voice",
      // Default to Daniel (British male, en-GB) where available; then warm /
      // natural narrator voices across the other platforms as fallbacks.
      preferred: [
        "Daniel", "Daniel (Enhanced)",
        "Google UK English Male", "Microsoft Ryan Online (Natural)",
        "Samantha", "Ava", "Serena", "Allison", "Nathan", "Karen",
        "Google US English", "Microsoft Aria Online (Natural)", "Microsoft Jenny",
        "Microsoft Guy Online (Natural)"
      ],
      narrated: "🎙️ Narrated reading",
      play: "▶ Play", pause: "❙❙ Pause", resume: "▶ Resume", stop: "■ Stop",
      voice: "Voice", speed: "Speed",
      voiceAria: "Reading voice", speedAria: "Reading speed",
      hint: "reads aloud on your device — pick a voice",
      unsupported: "Your browser can’t read this page aloud. " +
        "Try the latest Safari, Chrome, or Edge."
    },
    es: {
      lineSel: ".esp",
      voiceLang: "es", homeRegion: "ES", defaultVoiceLang: "es-ES",
      // A separate key: an English voice pick must not carry over to a Spanish
      // page — and the English key keeps its exact name, so nobody loses theirs.
      voiceKey: "mtlib_voice_es",
      preferred: [
        "Mónica", "Monica", "Jorge", "Marisol",
        "Microsoft Elvira Online (Natural)", "Microsoft Alvaro Online (Natural)",
        "Microsoft Helena", "Microsoft Laura", "Microsoft Pablo",
        "Google español", "Paulina", "Juan", "Diego",
        "Google español de Estados Unidos"
      ],
      narrated: "🎙️ Lectura narrada",
      play: "▶ Reproducir", pause: "❙❙ Pausa", resume: "▶ Reanudar",
      stop: "■ Detener",
      voice: "Voz", speed: "Velocidad",
      voiceAria: "Voz de lectura", speedAria: "Velocidad de lectura",
      hint: "se lee en voz alta en tu dispositivo — elige una voz",
      unsupported: "Tu navegador no puede leer esta página en voz alta. " +
        "Prueba con la última versión de Safari, Chrome o Edge."
    }
  };
  var T = ES ? STRINGS.es : STRINGS.en;
  var PREFERRED_VOICES = T.preferred;

  function $(sel, root) { return (root || document).querySelector(sel); }

  // The text of one verse in whichever language this edition is, minus the
  // little "note" superscript link. ⚠ `.eng` alone reads NOTHING on a Spanish
  // page — silently, with no error (see the header note).
  function verseText(vrs) {
    var line = $(T.lineSel, vrs) || $(".eng, .esp", vrs);
    if (!line) return "";
    var clone = line.cloneNode(true);
    // reader-notes.js appends its "⋯" opener — and a saved note, and the editor —
    // INSIDE this same line, so stripping only ".notelink" left the narrator
    // reading the button glyph aloud at the end of every verse, and would have
    // read a reader's private note out loud once they saved one. Same strip list
    // as reader-notes.js's own verseText(). (Pre-existing in English too; caught
    // 2026-08-19 by a test that captured what was actually being spoken.)
    clone.querySelectorAll(".notelink, .xrefs, .vclip, .v-tools, .v-note, .v-editor")
      .forEach(function (n) { n.remove(); });
    return (clone.textContent || "").replace(/\s+/g, " ").trim();
  }

  function chapterVerses() {
    return Array.prototype.slice.call(
      document.querySelectorAll("article.chapter .vrs")
    );
  }

  // ---- The control bar (built lazily on first Listen click) -----------------

  function buildBar(btn) {
    var bar = document.createElement("div");
    bar.className = "audiobar";
    bar.hidden = true;
    btn.closest(".togglebar").insertAdjacentElement("afterend", bar);
    return bar;
  }

  // ---- Pre-generated MP3 path -----------------------------------------------

  function mountMp3(bar, src, onFail) {
    var note = document.createElement("div");
    note.className = "audio-hint";
    note.textContent = T.narrated;
    var audio = document.createElement("audio");
    audio.className = "audio-el";
    audio.controls = true;
    audio.preload = "none";
    audio.src = src;
    bar.appendChild(note);
    bar.appendChild(audio);
    audio.addEventListener("error", function () {
      // File missing or undecodable — fall back to browser speech.
      bar.innerHTML = "";
      onFail();
    });
    audio.play().catch(function () { /* a blocked autoplay is fine; controls remain */ });
    return audio;
  }

  // ---- Browser-speech path --------------------------------------------------

  function SpeechReader(bar) {
    var synth = window.speechSynthesis;
    var verses = chapterVerses();
    var idx = 0;
    var playing = false;
    var voices = [];
    var keepAlive = null;

    function mkBtn(label) {
      var b = document.createElement("button");
      b.type = "button";
      b.className = "audio-btn";
      b.textContent = label;
      return b;
    }

    // --- UI ---
    var play = mkBtn(T.play);
    var stop = mkBtn(T.stop);
    var voiceSel = document.createElement("select");
    voiceSel.className = "audio-voice";
    voiceSel.setAttribute("aria-label", T.voiceAria);
    var rate = document.createElement("input");
    rate.type = "range"; rate.min = "0.6"; rate.max = "1.3"; rate.step = "0.05";
    rate.className = "audio-rate";
    rate.value = localStorage.getItem("mtlib_rate") || "0.95";
    rate.setAttribute("aria-label", T.speedAria);
    var hint = document.createElement("span");
    hint.className = "audio-hint";
    hint.textContent = T.hint;

    var row = document.createElement("div");
    row.className = "audio-row";
    row.appendChild(play);
    row.appendChild(stop);
    var vlab = document.createElement("label");
    vlab.className = "audio-lab";
    vlab.textContent = T.voice;
    vlab.appendChild(voiceSel);
    row.appendChild(vlab);
    var slab = document.createElement("label");
    slab.className = "audio-lab";
    slab.textContent = T.speed;
    slab.appendChild(rate);
    row.appendChild(slab);
    bar.appendChild(row);
    bar.appendChild(hint);

    // Tag a voice from a region other than this language's home one, so a
    // reader can tell "Mónica (ES)" from "Paulina (MX)". English keeps its
    // long-standing "(UK)" tag and nothing else, exactly as before.
    function regionTag(v) {
      var m = /^[a-z]{2}[-_]([A-Za-z]{2})/.exec(v.lang || "");
      if (!m) return "";
      var r = m[1].toUpperCase();
      if (!ES) return r === "GB" ? " (UK)" : "";   // unchanged English behaviour
      return r === T.homeRegion ? "" : " (" + r + ")";
    }

    function loadVoices() {
      var want = new RegExp("^" + T.voiceLang, "i");
      voices = (synth.getVoices() || []).filter(function (v) {
        return want.test(v.lang);
      });
      // No voice installed for this language: offer every voice rather than an
      // empty list, so the reader can at least pick something that speaks.
      if (!voices.length) voices = synth.getVoices() || [];
      voiceSel.innerHTML = "";
      voices.forEach(function (v, i) {
        var o = document.createElement("option");
        o.value = String(i);
        o.textContent = v.name + regionTag(v);
        voiceSel.appendChild(o);
      });
      var saved = localStorage.getItem(T.voiceKey);
      var pick = -1;
      if (saved) pick = voices.findIndex(function (v) { return v.name === saved; });
      if (pick < 0) {
        for (var p = 0; p < PREFERRED_VOICES.length && pick < 0; p++) {
          pick = voices.findIndex(function (v) { return v.name === PREFERRED_VOICES[p]; });
        }
      }
      if (pick < 0) {
        var home = new RegExp("^" + T.defaultVoiceLang, "i");
        pick = voices.findIndex(function (v) { return home.test(v.lang); });
      }
      if (pick < 0) pick = 0;
      voiceSel.value = String(Math.max(0, pick));
    }

    function currentVoice() {
      return voices[parseInt(voiceSel.value, 10)] || null;
    }

    function highlight(on) {
      verses.forEach(function (v) { v.classList.remove("speaking"); });
      if (on && verses[idx]) {
        verses[idx].classList.add("speaking");
        verses[idx].scrollIntoView({ behavior: "smooth", block: "center" });
      }
    }

    function speakCurrent() {
      if (idx >= verses.length) { finish(); return; }
      var text = verseText(verses[idx]);
      if (!text) { idx++; speakCurrent(); return; }
      var u = new SpeechSynthesisUtterance(text);
      var v = currentVoice();
      // Always stamp a lang: with no matching voice installed the engine still
      // has to be told this is Spanish, or it reads it with English phonetics.
      u.lang = (v && v.lang) || T.defaultVoiceLang;
      if (v) u.voice = v;
      u.rate = parseFloat(rate.value) || 1;
      u.onend = function () { if (playing) { idx++; speakCurrent(); } };
      u.onerror = function () { if (playing) { idx++; speakCurrent(); } };
      highlight(true);
      synth.speak(u);
    }

    function start() {
      if (playing) return;
      playing = true;
      play.textContent = T.pause;
      if (idx >= verses.length) idx = 0;
      speakCurrent();
      // Chrome silently stops long sessions; nudge it to keep going.
      keepAlive = setInterval(function () {
        if (playing && (synth.speaking || synth.pending)) { synth.pause(); synth.resume(); }
      }, 8000);
    }

    function pause() {
      playing = false;
      play.textContent = T.resume;
      synth.cancel(); // cancel + re-speak-from-idx is more reliable than pause()
      if (keepAlive) { clearInterval(keepAlive); keepAlive = null; }
    }

    function finish() {
      playing = false;
      idx = 0;
      play.textContent = T.play;
      highlight(false);
      if (keepAlive) { clearInterval(keepAlive); keepAlive = null; }
    }

    play.addEventListener("click", function () { playing ? pause() : start(); });
    stop.addEventListener("click", function () { synth.cancel(); finish(); });
    voiceSel.addEventListener("change", function () {
      var v = currentVoice();
      if (v) localStorage.setItem(T.voiceKey, v.name);
      if (playing) { synth.cancel(); speakCurrent(); } // apply the new voice now
    });
    rate.addEventListener("change", function () {
      localStorage.setItem("mtlib_rate", rate.value);
      if (playing) { synth.cancel(); speakCurrent(); }
    });

    loadVoices();
    if (typeof synth.onvoiceschanged !== "undefined") {
      synth.onvoiceschanged = loadVoices;
    }

    // Stop cleanly if the reader leaves the page.
    window.addEventListener("beforeunload", function () { synth.cancel(); });

    this.autostart = start;
  }

  function unsupported(bar) {
    var d = document.createElement("div");
    d.className = "audio-hint";
    d.textContent = T.unsupported;
    bar.innerHTML = "";
    bar.appendChild(d);
  }

  // ---- Wire the Listen button ----------------------------------------------

  function init() {
    var btn = document.getElementById("audiotgl");
    if (!btn) return; // not a chapter page
    var bar = null;
    var started = false;

    btn.addEventListener("click", function () {
      if (!bar) bar = buildBar(btn);

      // Repeat clicks just toggle the bar's visibility.
      if (started) {
        bar.hidden = !bar.hidden;
        btn.classList.toggle("done", !bar.hidden);
        return;
      }

      started = true;
      bar.hidden = false;
      btn.classList.add("done");

      var mp3 = btn.getAttribute("data-audio");
      function toSpeech() {
        if (!("speechSynthesis" in window)) { unsupported(bar); return; }
        new SpeechReader(bar).autostart();
      }
      if (mp3) mountMp3(bar, mp3, toSpeech);
      else toSpeech();
    });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
