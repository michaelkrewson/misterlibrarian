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
//      on any device with no files to host. It reads each verse's English in
//      order, highlights the verse being spoken, and lets the reader pick a
//      voice and a speaking speed (both remembered in localStorage). Nothing is
//      sent anywhere — the speech is synthesized on the reader's own device.
//
// The Listen button lives in the chapter togglebar as #audiotgl. Nothing loads
// or plays until the reader clicks it.

(function () {
  "use strict";

  var PREFERRED_VOICES = [
    // Default to Daniel (British male, en-GB) where available; then warm /
    // natural narrator voices across the other platforms as fallbacks.
    "Daniel", "Daniel (Enhanced)",
    "Google UK English Male", "Microsoft Ryan Online (Natural)",
    "Samantha", "Ava", "Serena", "Allison", "Nathan", "Karen",
    "Google US English", "Microsoft Aria Online (Natural)", "Microsoft Jenny",
    "Microsoft Guy Online (Natural)"
  ];

  function $(sel, root) { return (root || document).querySelector(sel); }

  // The English text of one verse, minus the little "note" superscript link.
  function verseText(vrs) {
    var eng = $(".eng", vrs);
    if (!eng) return "";
    var clone = eng.cloneNode(true);
    clone.querySelectorAll(".notelink").forEach(function (n) { n.remove(); });
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
    note.textContent = "🎙️ Narrated reading";
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
    var play = mkBtn("▶ Play");
    var stop = mkBtn("■ Stop");
    var voiceSel = document.createElement("select");
    voiceSel.className = "audio-voice";
    voiceSel.setAttribute("aria-label", "Reading voice");
    var rate = document.createElement("input");
    rate.type = "range"; rate.min = "0.6"; rate.max = "1.3"; rate.step = "0.05";
    rate.className = "audio-rate";
    rate.value = localStorage.getItem("mtlib_rate") || "0.95";
    rate.setAttribute("aria-label", "Reading speed");
    var hint = document.createElement("span");
    hint.className = "audio-hint";
    hint.textContent = "reads aloud on your device — pick a voice";

    var row = document.createElement("div");
    row.className = "audio-row";
    row.appendChild(play);
    row.appendChild(stop);
    var vlab = document.createElement("label");
    vlab.className = "audio-lab";
    vlab.textContent = "Voice";
    vlab.appendChild(voiceSel);
    row.appendChild(vlab);
    var slab = document.createElement("label");
    slab.className = "audio-lab";
    slab.textContent = "Speed";
    slab.appendChild(rate);
    row.appendChild(slab);
    bar.appendChild(row);
    bar.appendChild(hint);

    function loadVoices() {
      voices = (synth.getVoices() || []).filter(function (v) {
        return /^en/i.test(v.lang);
      });
      if (!voices.length) voices = synth.getVoices() || [];
      voiceSel.innerHTML = "";
      voices.forEach(function (v, i) {
        var o = document.createElement("option");
        o.value = String(i);
        o.textContent = v.name + (/^en-GB/i.test(v.lang) ? " (UK)" : "");
        voiceSel.appendChild(o);
      });
      var saved = localStorage.getItem("mtlib_voice");
      var pick = -1;
      if (saved) pick = voices.findIndex(function (v) { return v.name === saved; });
      if (pick < 0) {
        for (var p = 0; p < PREFERRED_VOICES.length && pick < 0; p++) {
          pick = voices.findIndex(function (v) { return v.name === PREFERRED_VOICES[p]; });
        }
      }
      if (pick < 0) pick = voices.findIndex(function (v) { return /^en-US/i.test(v.lang); });
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
      if (v) { u.voice = v; u.lang = v.lang; }
      u.rate = parseFloat(rate.value) || 1;
      u.onend = function () { if (playing) { idx++; speakCurrent(); } };
      u.onerror = function () { if (playing) { idx++; speakCurrent(); } };
      highlight(true);
      synth.speak(u);
    }

    function start() {
      if (playing) return;
      playing = true;
      play.textContent = "❙❙ Pause";
      if (idx >= verses.length) idx = 0;
      speakCurrent();
      // Chrome silently stops long sessions; nudge it to keep going.
      keepAlive = setInterval(function () {
        if (playing && (synth.speaking || synth.pending)) { synth.pause(); synth.resume(); }
      }, 8000);
    }

    function pause() {
      playing = false;
      play.textContent = "▶ Resume";
      synth.cancel(); // cancel + re-speak-from-idx is more reliable than pause()
      if (keepAlive) { clearInterval(keepAlive); keepAlive = null; }
    }

    function finish() {
      playing = false;
      idx = 0;
      play.textContent = "▶ Play";
      highlight(false);
      if (keepAlive) { clearInterval(keepAlive); keepAlive = null; }
    }

    play.addEventListener("click", function () { playing ? pause() : start(); });
    stop.addEventListener("click", function () { synth.cancel(); finish(); });
    voiceSel.addEventListener("change", function () {
      var v = currentVoice();
      if (v) localStorage.setItem("mtlib_voice", v.name);
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
    bar.innerHTML =
      '<div class="audio-hint">Your browser can’t read this page aloud. ' +
      "Try the latest Safari, Chrome, or Edge.</div>";
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
