/* dv-clippy-mount.js — the sprite character standing in for the sphere.

   On every page. dv-avatar.js, the sphere it replaced, is still in the
   repo and still works; nothing loads it.

   Neither drawer — dv-ask.js on the four case studies, dv-ask-chat.js on
   the landing page and Apex — knows or cares what is in the corner. It asks for two
   things by name — setState("thinking") while an answer opens, and
   setState("glitch") when the drawer slides — plus resize() and sense()
   after the panel is laid out, and it finds them on el.__av. The footer
   observer on the page wants onScreen and loop.

   So this is an adapter, not a rewrite: mount a Clippy on every
   [data-avatar], hang the sphere's interface off the same property, and
   both drawers carry on unchanged. Swapping a page back is one script tag.

   Needs clippy/clippy-eyes.js and clippy/dv-clippy.js loaded first.
*/
(function (root) {
  "use strict";

  if (!root.DVClippy) return;

  var BASE = "clippy/";
  var MAX = 128;        /* a frame is 128px tall and goes soft above that */

  root.DVClippy.setBase(BASE);

  /* The sphere was told its size in CSS and filled its box. This takes the
     box the page gives it and fits the character inside, so the launcher
     can keep shrinking at narrow widths without a number repeated here. */
  function fit(el) {
    var r = el.getBoundingClientRect();
    return Math.max(32, Math.min(MAX, Math.round(r.height || MAX)));
  }

  function Shim(el) {
    this.el = el;
    this.c = new root.DVClippy(el, { height: fit(el) });
    el.__av = this;
    var self = this;
    addEventListener("resize", function () { self.resize(); }, { passive: true });
  }

  /* the sphere's vocabulary, in the character's */
  Shim.prototype.setState = function (name, on) {
    if (name === "thinking") {
      if (on) this.c.want("thinking");
      else if (this.c.state === "thinking") this.c.force("idle");
      return;
    }
    if (name === "glitch" && on) {
      /* the drawer fires the same signal opening and closing, so ask it
         which way it just went */
      var open = root.dvAsk && root.dvAsk.open;
      this.c.force(open ? "greeting" : "goodbye", { after: "idle" });
    }
  };

  Shim.prototype.resize = function () { this.c.setHeight(fit(this.el)); this.c.resize(); };
  Shim.prototype.sense = function () {};   /* the sphere read its backdrop to
                                              pick an ink; a sprite has none */

  /* the footer observer sets onScreen on the shim and then hands back the
     clock. The character keeps its own flag, so pass it through */
  Object.defineProperty(Shim.prototype, "onScreen", {
    get: function () { return this.c.onScreen; },
    set: function (v) { this.c.onScreen = v; if (v) root.DVClippy.wake(); }
  });

  Shim.prototype.loop = function () {};    /* the shared clock runs itself */

  function mount() {
    var btn = document.querySelector(".avbtn [data-avatar]");
    var face = document.querySelector(".ask-face [data-avatar]");
    if (btn) new Shim(btn);
    if (face) new Shim(face);

    /* the full sheet is ten times the size of the idle row, so it waits
       until someone shows an interest in the corner */
    var b = document.querySelector(".avbtn");
    if (b) {
      var once = function () {
        root.DVClippy.preload();
        b.removeEventListener("pointerenter", once);
        b.removeEventListener("focus", once);
        b.removeEventListener("click", once);
      };
      b.addEventListener("pointerenter", once);
      b.addEventListener("focus", once);
      b.addEventListener("click", once);
    }
  }

  if (document.readyState === "loading")
    addEventListener("DOMContentLoaded", mount);
  else mount();
})(window);
