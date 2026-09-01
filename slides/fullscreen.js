/* ══════════════════════════════════════════════════════════════
   CS112 · open a deck straight into full screen
   Linked by every weekNN.html and lab-opening-wNN.html.

   A link ending in ?fs=1 asks for full screen. Browsers refuse
   requestFullscreen() without a user gesture, and the click that
   followed the link does NOT carry across the navigation, so the
   deck waits for the first gesture it gets in its own document,
   the click or keypress you were going to make anyway to advance,
   and goes full screen on that.

   Listeners are passive and capture-phase: they never swallow the
   event, so the same keypress still moves Reveal to the next slide.
   ══════════════════════════════════════════════════════════════ */
(function () {
  if (!/(^|[?&])fs=1(&|$)/.test(window.location.search)) return;

  var hint = document.createElement('div');
  hint.className = 'fs-hint';
  hint.textContent = 'press any key for full screen';

  function go() {
    var el = document.documentElement;
    var req = el.requestFullscreen || el.webkitRequestFullscreen ||
              el.mozRequestFullScreen || el.msRequestFullscreen;
    if (req && !document.fullscreenElement) {
      try { req.call(el); } catch (e) { /* denied: carry on windowed */ }
    }
    window.removeEventListener('keydown', go, true);
    window.removeEventListener('pointerdown', go, true);
    if (hint.parentNode) hint.parentNode.removeChild(hint);
  }

  function arm() {
    document.body.appendChild(hint);
    window.addEventListener('keydown', go, true);
    window.addEventListener('pointerdown', go, true);
    // if nobody touches anything, stop nagging after a while
    setTimeout(function () { hint.classList.add('fs-hint-dim'); }, 6000);
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', arm);
  } else {
    arm();
  }
})();
