// Mister Translation as an app (Michael 2026-10-22).
// 1. Offline reading: registers sw.js (pages from the network first; kept copies only when offline).
// 2. Getting the app: phones and tablets see a small bar from their second visit on, until they install
//    it or wave it away (30 days). Where the browser can install in one tap (Chrome, Edge, Android) the
//    bar's Install does that; on iPhone and iPad, which only install through Share > Add to Home Screen,
//    it opens a card with those steps. Never shown inside the installed app. English or Spanish, by page.
(function () {
  "use strict";
  if ("serviceWorker" in navigator) {
    window.addEventListener("load", function () {
      navigator.serviceWorker.register("/sw.js", { scope: "/" }).catch(function () {});
    });
  }

  var es = (document.documentElement.lang || "").slice(0, 2) === "es";

  // The tab bar's Continue (build.py tab_bar): the last chapter read on this device, one per language.
  // A chapter page remembers itself; every page points Continue there. While typing, the bar steps aside.
  (function () {
    var key = es ? "mt-last-es" : "mt-last-en";
    try {
      if (document.querySelector("article.chapter")) localStorage.setItem(key, location.pathname);
      var last = localStorage.getItem(key), c = document.querySelector(".mt-tabbar [data-continue]");
      if (c && last && /^\/[a-z0-9-]+\.html$/.test(last)) c.setAttribute("href", last);
      if (c && document.querySelector("article.chapter")) { c.classList.add("on"); c.setAttribute("aria-current", "page"); }
    } catch (x) { /* storage off: Continue stays on Genesis 1 */ }
    var typing = function (el) { return el && (el.isContentEditable || /^(TEXTAREA|SELECT)$/.test(el.tagName) || (el.tagName === "INPUT" && !/^(checkbox|radio|button|submit|range)$/.test(el.type))); };
    document.addEventListener("focusin", function (e) { if (typing(e.target)) document.documentElement.classList.add("mt-typing"); });
    document.addEventListener("focusout", function () { setTimeout(function () { if (!typing(document.activeElement)) document.documentElement.classList.remove("mt-typing"); }, 50); });
  })();
  var W = es ? {
    title: "Mister Translation en tu pantalla de inicio",
    sub: "Su propio icono, a pantalla completa, y los capítulos que lees también sin conexión.",
    install: "Instalar", notNow: "Ahora no", close: "Cerrar",
    steps: "Para instalarla en iPhone o iPad:",
    s1: "Toca <b>Compartir</b> <svg class=\"mt-share\" viewBox=\"0 0 24 24\" width=\"18\" height=\"18\" aria-hidden=\"true\"><path d=\"M12 3v12M7.5 7.5 12 3l4.5 4.5M6 11H5v10h14V11h-1\" fill=\"none\" stroke=\"currentColor\" stroke-width=\"1.8\" stroke-linecap=\"round\" stroke-linejoin=\"round\"/></svg> en la barra de Safari.",
    s2: "Elige <b>Añadir a pantalla de inicio</b> (desliza hacia abajo si no lo ves).",
    s3: "Deja activado <b>Abrir como app web</b> y toca <b>Añadir</b>.",
    note: "Apple no permite que un sitio se instale con un solo toque, así que son estos tres pasos."
  } : {
    title: "Get Mister Translation on your Home Screen",
    sub: "Its own icon, full screen, and the chapters you read work offline too.",
    install: "Install", notNow: "Not now", close: "Close",
    steps: "To install it on iPhone or iPad:",
    s1: "Tap <b>Share</b> <svg class=\"mt-share\" viewBox=\"0 0 24 24\" width=\"18\" height=\"18\" aria-hidden=\"true\"><path d=\"M12 3v12M7.5 7.5 12 3l4.5 4.5M6 11H5v10h14V11h-1\" fill=\"none\" stroke=\"currentColor\" stroke-width=\"1.8\" stroke-linecap=\"round\" stroke-linejoin=\"round\"/></svg> in Safari's bar.",
    s2: "Choose <b>Add to Home Screen</b> (scroll down if you don't see it).",
    s3: "Leave <b>Open as Web App</b> on, then tap <b>Add</b>.",
    note: "Apple doesn't let a website install in one tap, so it's these three steps."
  };

  var standalone = (window.matchMedia && matchMedia("(display-mode: standalone)").matches) || navigator.standalone === true;
  if (standalone) return;
  var store = function (k, v) { try { if (v === undefined) return localStorage.getItem(k); localStorage.setItem(k, v); } catch (x) { return null; } };
  try { if (!sessionStorage.getItem("mt-visit")) { sessionStorage.setItem("mt-visit", "1"); store("mt-visits", String((+store("mt-visits") || 0) + 1)); } } catch (x) { /* private mode */ }

  var deferred = null, bar = null;
  var touch = window.matchMedia && matchMedia("(pointer: coarse)").matches;

  var steps = function () {
    var back = document.createElement("div");
    back.className = "mt-app-sheet-back";
    back.innerHTML = '<div class="mt-app-sheet" role="dialog" aria-modal="true" aria-label="' + W.title + '">' +
      '<img src="/icons/icon-192.png" width="56" height="56" alt="">' +
      '<p class="mt-app-sheet-h">' + W.steps + '</p><ol><li>' + W.s1 + '</li><li>' + W.s2 + '</li><li>' + W.s3 + '</li></ol>' +
      '<p class="mt-app-sheet-note">' + W.note + '</p><button type="button" class="btn">' + W.close + '</button></div>';
    var shut = function () { back.remove(); };
    back.addEventListener("click", function (e) { if (e.target === back || e.target.closest("button")) shut(); });
    document.addEventListener("keydown", function k(e) { if (e.key === "Escape") { shut(); document.removeEventListener("keydown", k); } });
    document.body.appendChild(back);
  };
  var install = function () {
    if (!deferred) { steps(); return; }
    deferred.prompt();
    deferred.userChoice.then(function (c) { if (c && c.outcome === "accepted" && bar) bar.remove(); deferred = null; });
  };
  var show = function () {
    if (bar || store("mt-installed")) return;
    if (Date.now() - (+store("mt-install-dismissed") || 0) < 30 * 864e5) return;
    if ((+store("mt-visits") || 0) < 2 || !(touch || deferred)) return;
    bar = document.createElement("div");
    bar.className = "mt-app-bar";
    bar.setAttribute("role", "region");
    bar.setAttribute("aria-label", W.title);
    bar.innerHTML = '<img src="/icons/icon-192.png" width="40" height="40" alt="">' +
      '<span class="mt-app-text"><strong>' + W.title + '</strong><span>' + W.sub + '</span></span>' +
      '<button type="button" class="btn" data-go>' + W.install + '</button>' +
      '<button type="button" class="mt-app-x" data-x aria-label="' + W.notNow + '">×</button>';
    bar.querySelector("[data-go]").addEventListener("click", install);
    bar.querySelector("[data-x]").addEventListener("click", function () { bar.remove(); store("mt-install-dismissed", String(Date.now())); });
    document.body.appendChild(bar);
  };
  window.addEventListener("beforeinstallprompt", function (e) { e.preventDefault(); deferred = e; show(); });
  window.addEventListener("appinstalled", function () { if (bar) bar.remove(); store("mt-installed", "1"); });
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", show); else show();
})();
