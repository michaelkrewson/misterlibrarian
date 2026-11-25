// Reading-progress line: a 3px line across the top of the window that fills as the chapter (or West entry) is read,
// the same idea as the line on Micwyn's books. It measures the <article class="chapter"> only, so the header, the
// footer and anything below the text don't count. A short page, where it would only flicker, doesn't get one (it must be
// more than 1.5 windows tall). It takes the page's own gold/accent colour, is hidden in print, and holds still for
// readers who ask for reduced motion. No network, no storage.
(function () {
  var art = document.querySelector("article.chapter");
  if (!art) return;
  var cs = getComputedStyle(document.documentElement);
  var color = (cs.getPropertyValue("--gold") || cs.getPropertyValue("--accent") || "").trim() || "#e8c968";
  var css = document.createElement("style");
  css.textContent = ".mt-readline{position:fixed;top:0;left:0;right:0;height:3px;z-index:50;pointer-events:none}" +
    ".mt-readline[hidden]{display:none}" +
    ".mt-readline i{display:block;height:100%;transform:scaleX(0);transform-origin:0 50%}" +
    "@media (prefers-reduced-motion:no-preference){.mt-readline i{transition:transform .12s linear}}" +
    "@media print{.mt-readline{display:none!important}}";
  document.head.appendChild(css);
  var line = document.createElement("div"), fill = document.createElement("i"), frame = 0;
  line.className = "mt-readline"; line.setAttribute("aria-hidden", "true"); line.hidden = true;
  fill.style.background = color;
  line.appendChild(fill); document.body.appendChild(line);
  var paint = function () {
    frame = 0;
    var r = art.getBoundingClientRect(), room = r.height - window.innerHeight;
    line.hidden = room < window.innerHeight * 0.5;
    if (!line.hidden) fill.style.transform = "scaleX(" + Math.max(0, Math.min(1, -r.top / room)).toFixed(4) + ")";
  };
  var ask = function () { if (!frame) frame = requestAnimationFrame(paint); };
  window.addEventListener("scroll", ask, { passive: true });
  window.addEventListener("resize", ask);
  window.addEventListener("load", ask);
  ask();
})();
