// Personal Rundown ordering: up/down/hide/restore/reset controls for the
// rundown box's sections, mounted into any "[data-rundown]" container.
// This file is duplicated byte-for-byte at notebook/rundown.js, per this
// site's no-cross-dependency rule (see build_travel.py's header comment) --
// the hub mirrors the Notebook's rundown box verbatim, so both copies of
// this script stay identical too. Edit one, copy it onto the other.
//
// No accounts, no server, no sync across devices. A reader's choices are
// saved only in THEIR OWN browser (localStorage) -- the exact same
// mechanism whether the reader is Michael himself or anyone else who ever
// finds the arrows. There is no way for the site to know who made a change
// or to see what any given visitor picked.
//
// Blocks are keyed by their section LABEL text (data-rdkey), not position,
// so a saved preference like "put Bitcoin first" survives from one day's
// box to the next even though the actual items underneath change daily. A
// label the reader has never seen before (a new section) is appended after
// their known ones rather than dropped or inserted somewhere surprising.

var RD_KEY = "rundownPrefs.v1";

function _rdLoad(){
  try {
    var raw = localStorage.getItem(RD_KEY);
    if (!raw) return {order: [], hidden: []};
    var parsed = JSON.parse(raw);
    return {
      order: Array.isArray(parsed.order) ? parsed.order : [],
      hidden: Array.isArray(parsed.hidden) ? parsed.hidden : []
    };
  } catch (e) {
    return {order: [], hidden: []};
  }
}

function _rdSave(state){
  try {
    localStorage.setItem(RD_KEY, JSON.stringify(state));
  } catch (e) {
    // Private browsing / storage disabled / quota exceeded -- the box still
    // works, it just won't remember this reader's ordering next time.
  }
}

function _rdEsc(s){
  var d = document.createElement("div");
  d.textContent = s;
  return d.innerHTML;
}

function _rdBlocks(container){
  return Array.prototype.slice.call(container.querySelectorAll(".rdblock"));
}

function _rdCurrentOrder(container){
  return _rdBlocks(container).map(function(b){ return b.getAttribute("data-rdkey"); });
}

function _rdPrevVisible(el){
  var p = el.previousElementSibling;
  while (p && p.style.display === "none") p = p.previousElementSibling;
  return p;
}

function _rdNextVisible(el){
  var n = el.nextElementSibling;
  while (n && n.style.display === "none") n = n.nextElementSibling;
  return n;
}

function _rdRenderHidden(container, state){
  var host = container.querySelector(".rdhidden");
  if (!host) return;
  if (!state.hidden.length){
    host.innerHTML = "";
    return;
  }
  var chips = state.hidden.map(function(label){
    return '<button type="button" class="rdrestore" data-rdkey="' + _rdEsc(label) +
      '" aria-label="Show ' + _rdEsc(label) + ' again">' + _rdEsc(label) + " ✕</button>";
  });
  host.innerHTML = "Hidden: " + chips.join(" ");
}

function _rdApply(container, state){
  var wrap = container.querySelector(".rdblocks");
  if (!wrap) return;
  var blocks = _rdBlocks(container);
  var byKey = {};
  blocks.forEach(function(b){ byKey[b.getAttribute("data-rdkey")] = b; });
  var seen = {};
  var ordered = [];
  state.order.forEach(function(key){
    if (byKey[key] && !seen[key]){ ordered.push(byKey[key]); seen[key] = true; }
  });
  blocks.forEach(function(b){
    var key = b.getAttribute("data-rdkey");
    if (!seen[key]){ ordered.push(b); seen[key] = true; }
  });
  ordered.forEach(function(b){ wrap.appendChild(b); });
  blocks.forEach(function(b){
    var key = b.getAttribute("data-rdkey");
    b.style.display = state.hidden.indexOf(key) === -1 ? "" : "none";
  });
  _rdRenderHidden(container, state);
}

function _rdInit(container){
  // Capture the natural, as-published order once, before any saved
  // preference is applied, so "Reset order" has something to reset TO.
  var natural = _rdCurrentOrder(container);
  _rdApply(container, _rdLoad());

  container.addEventListener("click", function(ev){
    var btn = ev.target.closest ? ev.target.closest("button") : null;
    if (!btn) return;
    var block = btn.closest(".rdblock");
    var state = _rdLoad();

    if (btn.classList.contains("rdup") && block){
      var prev = _rdPrevVisible(block);
      if (prev) block.parentNode.insertBefore(block, prev);
      state.order = _rdCurrentOrder(container);
      _rdSave(state);
    } else if (btn.classList.contains("rddown") && block){
      var next = _rdNextVisible(block);
      if (next) block.parentNode.insertBefore(next, block);
      state.order = _rdCurrentOrder(container);
      _rdSave(state);
    } else if (btn.classList.contains("rdhide") && block){
      var key = block.getAttribute("data-rdkey");
      if (state.hidden.indexOf(key) === -1) state.hidden.push(key);
      _rdSave(state);
      _rdApply(container, state);
    } else if (btn.classList.contains("rdrestore")){
      var rkey = btn.getAttribute("data-rdkey");
      state.hidden = state.hidden.filter(function(k){ return k !== rkey; });
      _rdSave(state);
      _rdApply(container, state);
    } else if (btn.classList.contains("rdreset")){
      var fresh = {order: natural, hidden: []};
      _rdSave(fresh);
      _rdApply(container, fresh);
    }
  });
}

document.addEventListener("DOMContentLoaded", function(){
  document.querySelectorAll("[data-rundown]").forEach(function(container){
    _rdInit(container);
  });
});
