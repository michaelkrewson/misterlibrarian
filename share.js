// Share-this-page button, used site-wide.
//
// One button, mounted into #shareWidget: triggers the OS's native share sheet
// where the Web Share API is supported (most mobile browsers, and a growing
// number of desktop ones), otherwise copies the page URL to the clipboard and
// shows a brief confirmation. No tracking, no network calls, nothing sent
// anywhere.

function _shareFlash(toast, msg){
  toast.textContent = msg;
  toast.classList.add("show");
  clearTimeout(toast._hideTimer);
  toast._hideTimer = setTimeout(function(){ toast.classList.remove("show"); }, 1800);
}

function _shareLegacyCopy(url, toast, copiedMsg, failMsg){
  var ta = document.createElement("textarea");
  ta.value = url;
  ta.setAttribute("readonly", "");
  ta.style.position = "fixed";
  ta.style.top = "-1000px";
  ta.style.opacity = "0";
  document.body.appendChild(ta);
  ta.select();
  ta.setSelectionRange(0, url.length);
  var ok = false;
  try { ok = document.execCommand("copy"); } catch (e) { ok = false; }
  document.body.removeChild(ta);
  _shareFlash(toast, ok ? copiedMsg : failMsg);
}

function _shareCopyLink(url, toast, copiedMsg, failMsg){
  if (navigator.clipboard && navigator.clipboard.writeText){
    navigator.clipboard.writeText(url)
      .then(function(){ _shareFlash(toast, copiedMsg); })
      .catch(function(){ _shareLegacyCopy(url, toast, copiedMsg, failMsg); });
  } else {
    _shareLegacyCopy(url, toast, copiedMsg, failMsg);
  }
}

function _shareInit(root){
  // The Spanish edition sets <html lang="es">; every other page on either
  // site is lang="en", so this is the one place the label needs to branch.
  var es = (document.documentElement.lang || "").toLowerCase().indexOf("es") === 0;
  var label = es ? "🔗 Compartir" : "🔗 Share";
  var ariaLabel = es ? "Compartir esta página" : "Share this page";
  var copiedMsg = es ? "✓ Enlace copiado" : "✓ Link copied";
  var failMsg = es ? "No se pudo copiar el enlace" : "Couldn’t copy the link";

  var btn = document.createElement("button");
  btn.type = "button";
  btn.className = "share-btn";
  btn.textContent = label;
  btn.setAttribute("aria-label", ariaLabel);

  var toast = document.createElement("span");
  toast.className = "share-toast";
  toast.setAttribute("role", "status");
  toast.setAttribute("aria-live", "polite");

  root.appendChild(btn);
  root.appendChild(toast);

  btn.addEventListener("click", function(){
    var url = location.href;
    var title = document.title;
    if (navigator.share){
      navigator.share({title: title, url: url}).catch(function(err){
        // AbortError just means the reader closed the native share sheet.
        if (err && err.name === "AbortError") return;
        _shareCopyLink(url, toast, copiedMsg, failMsg);
      });
    } else {
      _shareCopyLink(url, toast, copiedMsg, failMsg);
    }
  });
}

document.addEventListener("DOMContentLoaded", function(){
  // querySelectorAll (not a single getElementById) because the mobile nav menu
  // duplicates this widget alongside the desktop nav's copy -- every ".share-widget"
  // container on the page gets its own independent button+toast.
  document.querySelectorAll(".share-widget").forEach(function(root){ _shareInit(root); });
});
