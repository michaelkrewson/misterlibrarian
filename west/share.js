// Share-this-page button for Eight Miles West.
//
// One button, mounted into #shareWidget: triggers the OS's native share sheet
// where the Web Share API is supported (most mobile browsers, and a growing
// number of desktop ones), otherwise copies the page URL to the clipboard and
// shows a brief confirmation. No tracking, no network calls, nothing sent
// anywhere. Identical to the Bible project's share.js, kept as its own copy
// per this site's no-cross-dependency rule (see build_travel.py's header comment).

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
  var btn = document.createElement("button");
  btn.type = "button";
  btn.className = "share-btn";
  btn.textContent = "🔗 Share";
  btn.setAttribute("aria-label", "Share this page");

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
        _shareCopyLink(url, toast, "✓ Link copied", "Couldn’t copy the link");
      });
    } else {
      _shareCopyLink(url, toast, "✓ Link copied", "Couldn’t copy the link");
    }
  });
}

document.addEventListener("DOMContentLoaded", function(){
  // querySelectorAll (not a single getElementById) so every ".share-widget"
  // container on the page gets its own independent button+toast.
  document.querySelectorAll(".share-widget").forEach(function(root){ _shareInit(root); });
});
