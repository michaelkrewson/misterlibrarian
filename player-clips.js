// Per-verse video clip player for The MisterLibrarian Bible Project.
//
// A plain YouTube iframe's ?start=&end= URL parameters are unreliable at
// actually seeking to the right start point and at stopping playback at the
// right end point. So every clip marked up as
//   <div class="vclip" data-video="ID" data-start="S" data-end="E">
//     <div class="ytp"></div>
//   </div>
// is instead driven through the YouTube IFrame Player API, which explicitly
// seeks on ready and hard-pauses once playback crosses the intended end time.
// Add a new clip by giving its wrapper those three data attributes plus the
// nested .ytp mount div — no JS changes needed here.
function onYouTubeIframeAPIReady(){
  document.querySelectorAll(".vclip[data-video]").forEach(function(wrap){
    var mount = wrap.querySelector(".ytp");
    if (!mount) return;
    var vid = wrap.getAttribute("data-video");
    var start = parseInt(wrap.getAttribute("data-start"), 10) || 0;
    var endAttr = wrap.getAttribute("data-end");
    var end = endAttr ? parseInt(endAttr, 10) : null;
    var poll = null;
    var player = new YT.Player(mount, {
      videoId: vid,
      playerVars: {start: start, end: end || undefined, rel: 0, modestbranding: 1},
      events: {
        onReady: function(e){ e.target.seekTo(start, true); },
        onStateChange: function(e){
          if (poll){ clearInterval(poll); poll = null; }
          if (e.data === YT.PlayerState.PLAYING && end){
            poll = setInterval(function(){
              if (player.getCurrentTime() >= end){
                player.pauseVideo();
                clearInterval(poll); poll = null;
              }
            }, 250);
          }
        }
      }
    });
  });
}
