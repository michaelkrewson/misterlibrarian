// Click-to-play video clips for The MisterLibrarian Bible Project.
//
// Every clip marked up as
//   <div class="vclip" data-video="ID" data-start="S" data-end="E"></div>
// (data-start/data-end optional — omit data-end to play to the video's own end)
// renders as a small inline "Video" tag, about the size of a line of text —
// nothing loads or reserves any real estate until the reader clicks it. Only
// then does this script build the full 16:9 frame and the real YouTube
// IFrame Player API embed in its place (autoplaying, seeked to the right
// start point, hard-paused the instant playback crosses data-end, since a
// plain iframe's ?start=&end= URL params are unreliable for both of those).
//
// Add a new clip by giving its div those data attributes — no JS changes
// needed here, and no nested markup required.

var _ytApiReady = false;
var _ytApiQueue = [];

function onYouTubeIframeAPIReady(){
  _ytApiReady = true;
  _ytApiQueue.forEach(function(fn){ fn(); });
  _ytApiQueue = [];
}

function _vclipBuildPlayer(mount, vid, start, end){
  var poll = null;
  new YT.Player(mount, {
    videoId: vid,
    playerVars: {start: start, end: end || undefined, rel: 0, modestbranding: 1, autoplay: 1},
    events: {
      onReady: function(e){ e.target.seekTo(start, true); e.target.playVideo(); },
      onStateChange: function(e){
        if (poll){ clearInterval(poll); poll = null; }
        if (e.data === YT.PlayerState.PLAYING && end){
          poll = setInterval(function(){
            if (e.target.getCurrentTime() >= end){
              e.target.pauseVideo();
              clearInterval(poll); poll = null;
            }
          }, 250);
        }
      }
    }
  });
}

function _vclipInit(wrap){
  var vid = wrap.getAttribute("data-video");
  if (!vid) return;
  var start = parseInt(wrap.getAttribute("data-start"), 10) || 0;
  var endAttr = wrap.getAttribute("data-end");
  var end = endAttr ? parseInt(endAttr, 10) : null;

  var ph = document.createElement("div");
  ph.className = "vclip-ph";
  ph.setAttribute("role", "button");
  ph.setAttribute("tabindex", "0");
  ph.setAttribute("aria-label", "Play video");
  ph.innerHTML = '<span class="vclip-play">▶</span><span>Video</span>';
  wrap.appendChild(ph);

  function activate(){
    ph.remove();
    var frame = document.createElement("div");
    frame.className = "vclip-frame";
    var mount = document.createElement("div");
    mount.className = "ytp";
    frame.appendChild(mount);
    wrap.appendChild(frame);
    if (_ytApiReady) _vclipBuildPlayer(mount, vid, start, end);
    else _ytApiQueue.push(function(){ _vclipBuildPlayer(mount, vid, start, end); });
  }
  ph.addEventListener("click", activate);
  ph.addEventListener("keydown", function(e){
    if (e.key === "Enter" || e.key === " "){ e.preventDefault(); activate(); }
  });
}

document.addEventListener("DOMContentLoaded", function(){
  document.querySelectorAll(".vclip[data-video]").forEach(_vclipInit);
});
