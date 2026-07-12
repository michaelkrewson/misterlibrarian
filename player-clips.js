// Click-to-play video clips for The MisterLibrarian Bible Project.
//
// Every clip marked up as
//   <div class="vclip" data-video="ID" data-start="S" data-end="E">
//     <div class="ytp"></div>
//   </div>
// (data-start/data-end optional — omit data-end to play to the video's own end)
// starts collapsed to a placeholder (a play symbol + "Video"). Nothing loads
// or plays until the reader clicks it — only then is the real YouTube IFrame
// Player API embed built, seeked to the right start point, and (if data-end
// is set) hard-paused the instant playback crosses the end second, since a
// plain iframe's ?start=&end= URL params are unreliable for both of those.
//
// Add a new clip by giving its wrapper those data attributes plus the nested
// .ytp mount div — no JS changes needed here.

var _ytApiReady = false;
var _ytApiQueue = [];

function onYouTubeIframeAPIReady(){
  _ytApiReady = true;
  _ytApiQueue.forEach(function(fn){ fn(); });
  _ytApiQueue = [];
}

function _vclipBuildPlayer(wrap, mount, vid, start, end){
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
  var mount = wrap.querySelector(".ytp");
  if (!mount) return;
  var vid = wrap.getAttribute("data-video");
  var start = parseInt(wrap.getAttribute("data-start"), 10) || 0;
  var endAttr = wrap.getAttribute("data-end");
  var end = endAttr ? parseInt(endAttr, 10) : null;

  var ph = document.createElement("div");
  ph.className = "vclip-ph";
  ph.setAttribute("role", "button");
  ph.setAttribute("tabindex", "0");
  ph.setAttribute("aria-label", "Play video");
  ph.innerHTML = '<span class="vclip-play">▶</span><span class="vclip-label">Video</span>';
  wrap.insertBefore(ph, mount);

  function activate(){
    ph.remove();
    if (_ytApiReady) _vclipBuildPlayer(wrap, mount, vid, start, end);
    else _ytApiQueue.push(function(){ _vclipBuildPlayer(wrap, mount, vid, start, end); });
  }
  ph.addEventListener("click", activate);
  ph.addEventListener("keydown", function(e){
    if (e.key === "Enter" || e.key === " "){ e.preventDefault(); activate(); }
  });
}

document.addEventListener("DOMContentLoaded", function(){
  document.querySelectorAll(".vclip[data-video]").forEach(_vclipInit);
});
