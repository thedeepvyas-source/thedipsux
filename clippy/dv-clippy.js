/* dv-clippy.js — the sprite character.

   PILOT. Not wired into the portfolio. See lab/README.md.

   One canvas, one sprite sheet, one requestAnimationFrame loop shared by every
   instance on the page. The loop only paints when a frame index actually
   changes, so an idle character at 6fps costs six paints a second, not sixty.

   The sheet is laid out 8 frames across, 12 states down, with a transparent
   gutter around every frame. The gutter is the reason this draws cleanly at
   any display size: without it, scaling samples a sliver of the neighbouring
   frame and you get a stray eyebrow along the top edge.

   Geometry comes from the sheet that lab/build-sheet.py produces. If you
   rebuild the sheet, update SHEET here to match or everything shifts.

   The pupils are not in the sheet on the four loop rows. build-sheet.py rubs
   them out and writes clippy-eyes.js saying where they were; this file draws
   them back in, aimed at the pointer. Load clippy-eyes.js before this one, or
   those rows come out with blank eyes.
*/
(function (root) {
  "use strict";

  /* ---- the sheet ------------------------------------------------------ */

  var SHEET = {
    src: "clippy.webp",       /* all twelve states, fetched on demand */
    idleSrc: "clippy-idle.webp", /* just row 0, small enough to load at once */
    cols: 8,
    rows: 12,
    cellW: 89, cellH: 140,    /* one grid cell, gutter included */
    artW: 77, artH: 128,      /* the drawing inside it */
    pad: 6                    /* gutter on each side */
  };

  /* How far a pupil slides, in the frame's own pixels, when the pointer is
     all the way over. The eyeball is 11px across the radius and the pupil 6,
     so about 5px is the whole of the room there is - and the artist has
     usually spent some of it already. See look() for the clamp. */
  var TRAVEL = 5.0;

  /* ---- the states ------------------------------------------------------

     row      which band of the sheet
     fps      frames a second
     loop     keep going, or stop at the end and hand back to idle
     bounce   play 0..7..0 instead of 0..7|0. Only for loops whose first and
              last frame don't quite meet, where a hard cut would pop
     still    the frame to show when the visitor asked for reduced motion
     rank     who wins when two states are requested at once. See want()
     soft     a loop that is only a backdrop, so anything may replace it.
              thinking is the loop that is not soft: it has to stay up until
              the request it stands for actually resolves
  */

  var STATES = {
    idle:        { row: 0,  fps: 6,  loop: true,  bounce: true,  soft: true, still: 0, rank: 0 },
    greeting:    { row: 1,  fps: 10, loop: false,                still: 4, rank: 40 },
    listening:   { row: 2,  fps: 8,  loop: true,  bounce: true,  soft: true, still: 0, rank: 20 },
    thinking:    { row: 3,  fps: 8,  loop: true,  bounce: true,  still: 3, rank: 80 },
    explaining:  { row: 4,  fps: 8,  loop: true,                 soft: true, still: 2, rank: 30 },
    happy:       { row: 5,  fps: 10, loop: false,                still: 3, rank: 50 },
    confused:    { row: 6,  fps: 8,  loop: false,                still: 3, rank: 70 },
    apologetic:  { row: 7,  fps: 8,  loop: false,                still: 3, rank: 90 },
    surprised:   { row: 8,  fps: 12, loop: false,                still: 3, rank: 55 },
    angry:       { row: 9,  fps: 10, loop: false,                still: 3, rank: 55 },
    celebrating: { row: 10, fps: 12, loop: false,                still: 3, rank: 60 },
    goodbye:     { row: 11, fps: 8,  loop: false,                still: 5, rank: 100 }
  };

  /* ---- loading ---------------------------------------------------------

     Two images. The first is row 0 alone, 41KB, so the collapsed character
     blinks away from the first paint. The full sheet is ten times that and is
     only worth fetching once someone shows an interest, so load() is called on
     first hover or first open, whichever comes first.
  */

  var base = "";                 /* set by DVClippy.setBase() */
  var imgs = { idle: null, full: null };
  var pending = {};

  function load(which, cb) {
    if (imgs[which]) { cb && cb(imgs[which]); return; }
    if (pending[which]) { pending[which].push(cb); return; }
    pending[which] = [cb];
    var im = new Image();
    im.decoding = "async";
    im.onload = function () {
      imgs[which] = im;
      var q = pending[which]; pending[which] = null;
      q.forEach(function (f) { f && f(im); });
      tick();                    /* whatever was waiting can draw now */
    };
    im.onerror = function () {
      pending[which] = null;
      /* a missing sheet must not take the page down with it: the character
         simply never appears, and the panel still works */
      if (root.console) console.warn("dv-clippy: could not load " + im.src);
    };
    im.src = base + SHEET[which === "idle" ? "idleSrc" : "src"];
  }

  /* ---- the pointer -----------------------------------------------------

     One listener for the page, not one per character: the pilot has
     fourteen of these on it at once. Each works out its own aim in the
     clock below, from its own position, so the tiles down the page all
     look at the same place rather than all looking the same way.

     Rects are read in the clock and cached until something could have
     moved them. Reading fourteen of them inside a pointermove handler is
     how you make a page feel heavy.
  */

  var ptr = { x: 0, y: 0, seen: false, at: 0 };
  var rectsStale = true;

  addEventListener("pointermove", function (e) {
    ptr.x = e.clientX; ptr.y = e.clientY; ptr.seen = true; ptr.at = performance.now();
    wake();
  }, { passive: true });
  addEventListener("pointerdown", function (e) {
    ptr.x = e.clientX; ptr.y = e.clientY; ptr.seen = true; ptr.at = performance.now();
    wake();
  }, { passive: true });
  addEventListener("scroll", function () { rectsStale = true; }, { passive: true, capture: true });
  addEventListener("resize", function () { rectsStale = true; }, { passive: true });

  /* ---- the shared clock ------------------------------------------------

     Every instance is advanced by one loop. It stops entirely when nothing
     is animating, when the tab is hidden, or when every character is off
     screen, so a page left open in a background tab costs nothing.
  */

  var live = [];
  var raf = 0;
  var last = 0;

  function tick(now) {
    raf = 0;
    now = now || performance.now();
    var dt = last ? Math.min(now - last, 200) : 16;
    last = now;

    var running = false;
    for (var i = 0; i < live.length; i++) {
      if (live[i].advance(dt, now)) running = true;
    }
    rectsStale = false;
    if (running && !document.hidden) raf = requestAnimationFrame(tick);
    else last = 0;
  }

  function wake() {
    if (!raf && !document.hidden) { last = 0; raf = requestAnimationFrame(tick); }
  }

  document.addEventListener("visibilitychange", function () {
    if (document.hidden) { if (raf) cancelAnimationFrame(raf); raf = 0; last = 0; }
    else wake();
  });

  var reduce = matchMedia("(prefers-reduced-motion: reduce)");

  /* ---- one character ---------------------------------------------------- */

  function Clippy(el, opts) {
    opts = opts || {};
    this.el = el;
    this.height = opts.height || 112;
    /* the state tiles pass track:false, so they keep showing the eyes the
       artist drew. A reference that follows your mouse is not a reference */
    this.track = opts.track !== false;
    this.state = "idle";
    this.frame = 0;
    this.dir = 1;
    this.acc = 0;
    this.onScreen = true;
    this.painted = -1;
    this.paintedRow = -1;
    this.paintedLook = "";
    this.done = null;             /* callback for the current one-shot */

    this.look = [0, 0];           /* where the pupils are pointed, -1..1 */
    this.target = [0, 0];
    this.rest = [0, 0];           /* where the pointer last left them */
    this.rect = null;

    this.canvas = document.createElement("canvas");
    this.canvas.setAttribute("aria-hidden", "true");
    this.ctx = this.canvas.getContext("2d");
    el.appendChild(this.canvas);
    el.__clippy = this;

    this.resize();
    load("idle", this.paint.bind(this));

    /* stop burning frames for a character scrolled out of view */
    var self = this;
    if (root.IntersectionObserver) {
      this.io = new IntersectionObserver(function (es) {
        self.onScreen = es[0].isIntersecting;
        if (self.onScreen) wake();
      });
      this.io.observe(el);
    }

    /* switched on mid-session: the eyes go back to where they were drawn
       rather than freezing wherever the pointer left them */
    this.onReduce = function () {
      self.frame = STATES[self.state].still;
      if (reduce.matches) { self.look = [0, 0]; self.target = [0, 0]; self.rest = [0, 0]; }
      self.paint();
    };
    if (reduce.addEventListener) reduce.addEventListener("change", this.onReduce);

    live.push(this);
    wake();
  }

  Clippy.prototype.resize = function () {
    var dpr = Math.min(root.devicePixelRatio || 1, 2);
    var h = this.height, w = Math.round(h * SHEET.artW / SHEET.artH);
    this.w = w; this.h = h;
    this.canvas.width = Math.round(w * dpr);
    this.canvas.height = Math.round(h * dpr);
    this.canvas.style.width = w + "px";
    this.canvas.style.height = h + "px";
    this.canvas.style.display = "block";
    this.ctx.imageSmoothingEnabled = true;
    this.ctx.imageSmoothingQuality = "high";
    this.painted = -1;
    this.rect = null;
    this.paint();
  };

  Clippy.prototype.setHeight = function (h) {
    if (h === this.height) return;
    this.height = h;
    this.resize();
  };

  /* which image can draw the row we are on. Row 0 is in both, so the small
     one carries the collapsed character until the full sheet arrives */
  Clippy.prototype.source = function () {
    var row = STATES[this.state].row;
    if (imgs.full) return { im: imgs.full, row: row };
    if (imgs.idle && row === 0) return { im: imgs.idle, row: 0 };
    return null;
  };

  Clippy.prototype.paint = function () {
    var s = this.source();
    if (!s) return;
    /* the look is part of what is on screen now, so it has to be part of
       the key, or a pointer move with no frame change would paint nothing.
       Rounded, because a pupil cannot show a hundredth of a pixel */
    var lk = Math.round(this.look[0] * 60) + ":" + Math.round(this.look[1] * 60);
    var key = s.row * 100 + this.frame;
    if (key === this.painted && lk === this.paintedLook) return;
    this.painted = key;
    this.paintedLook = lk;

    var sx = this.frame * SHEET.cellW + SHEET.pad;
    var sy = s.row * SHEET.cellH + SHEET.pad;
    var dpr = this.canvas.width / this.w;
    this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
    this.ctx.drawImage(s.im, sx, sy, SHEET.artW, SHEET.artH,
                       0, 0, this.w * dpr, this.h * dpr);
    this.pupils(s.row, dpr);
  };

  /* ---- the eyes ---------------------------------------------------------

     Only the four loop rows have a table, and only the frames where both
     eyes are open and round. Everything else - every one-shot, every blink,
     every squint - still has the pupils the artist drew and never reaches
     this at all.

     The pupil is drawn from where it was painted, not from the middle of
     the eyeball, so the animation's own eye movement survives and the
     pointer only leans on it. The clamp is the same idea: it will not pull
     a pupil further out than the artist already put one, and it will never
     pull one back in. At rest this draws the frame as it was.
  */

  Clippy.prototype.pupils = function (row, dpr) {
    var E = root.DVClippyEyes;
    if (!E) return;
    var list = E.f[row + "," + this.frame];
    if (!list) return;

    var g = this.ctx;
    var k = (this.w / SHEET.artW) * dpr;     /* frame pixels to canvas pixels */
    for (var i = 0; i < list.length; i++) {
      var e = list[i];
      var bx = e[0], by = e[1], px = e[2], py = e[3], pr = e[4];
      var rest = Math.sqrt((px - bx) * (px - bx) + (py - by) * (py - by));
      var lim = Math.max(E.ballR - pr * 0.5, rest);

      var ox = px - bx + this.look[0] * TRAVEL;
      var oy = py - by + this.look[1] * TRAVEL;
      var m = Math.sqrt(ox * ox + oy * oy);
      if (m > lim) { ox = ox / m * lim; oy = oy / m * lim; }

      var cx = (bx + ox) * k, cy = (by + oy) * k, r = pr * k;

      /* the painted pupil has a soft edge about a pixel wide; a flat arc
         next to it reads as a sticker */
      var body = g.createRadialGradient(cx, cy, Math.max(0, r - 1.1), cx, cy, r + 0.5);
      body.addColorStop(0, E.fill);
      body.addColorStop(0.72, E.fill);
      body.addColorStop(1, "rgba(13,13,13,0)");
      g.fillStyle = body;
      g.beginPath();
      g.arc(cx, cy, r + 0.6, 0, 6.2832);
      g.fill();

      var gx = cx + E.glint[0] * r, gy = cy + E.glint[1] * r, gr = E.glint[2] * r;
      var spec = g.createRadialGradient(gx, gy, 0, gx, gy, gr);
      spec.addColorStop(0, "rgba(255,255,255,.95)");
      spec.addColorStop(0.55, "rgba(255,255,255,.55)");
      spec.addColorStop(1, "rgba(255,255,255,0)");
      g.fillStyle = spec;
      g.beginPath();
      g.arc(gx, gy, gr, 0, 6.2832);
      g.fill();
    }
  };

  /* where this character should be looking, from where it is on the page.

     It should keep watching where you left the pointer rather than snap
     forward the moment your hand stops, so after a long wait it only
     drifts a little around that last look. Same numbers as the sphere on
     the case studies, so the two feel like the same animal. */
  Clippy.prototype.aim = function (now) {
    if (!this.track || !ptr.seen) return;
    if (!this.rect || rectsStale) this.rect = this.el.getBoundingClientRect();
    var r = this.rect;
    if (!r.width) return;
    var reach = Math.max(innerWidth, innerHeight) * 0.42;
    var tx = (ptr.x - (r.left + r.width / 2)) / reach;
    var ty = (ptr.y - (r.top + r.height / 2)) / reach;
    this.rest[0] = this.target[0] = Math.max(-1, Math.min(1, tx));
    this.rest[1] = this.target[1] = Math.max(-1, Math.min(1, ty));

    if (now - ptr.at > 6000) {
      var t = now / 1000 * 0.18;
      this.target[0] = Math.max(-1, Math.min(1, this.rest[0] + Math.sin(t) * 0.17));
      this.target[1] = Math.max(-1, Math.min(1, this.rest[1] + Math.sin(t * 0.63 + 1.1) * 0.10));
    }
  };

  /* returns true while this character still needs the clock */
  Clippy.prototype.advance = function (dt, now) {
    if (!this.onScreen || reduce.matches) return false;
    var st = STATES[this.state];

    this.aim(now);
    this.look[0] += (this.target[0] - this.look[0]) * 0.075;
    this.look[1] += (this.target[1] - this.look[1]) * 0.075;

    this.acc += dt;
    var step = 1000 / st.fps;
    while (this.acc >= step) {
      this.acc -= step;

      if (st.bounce) {
        this.frame += this.dir;
        if (this.frame >= SHEET.cols - 1) { this.frame = SHEET.cols - 1; this.dir = -1; }
        else if (this.frame <= 0) { this.frame = 0; this.dir = 1; }
      } else {
        this.frame++;
        if (this.frame >= SHEET.cols) {
          if (st.loop) this.frame = 0;
          else { this.frame = SHEET.cols - 1; this.finish(); return true; }
        }
      }
    }
    /* paint() is cheap when nothing changed - it compares the frame and the
       look against what is already on the canvas and returns */
    this.paint();
    return true;
  };

  /* a one-shot reached its last frame */
  Clippy.prototype.finish = function () {
    var cb = this.done;
    this.done = null;
    var next = this.after || "idle";
    this.after = null;
    this.force(next);
    if (cb) cb();
  };

  /* ---- asking for a state ----------------------------------------------

     want() is the polite form and obeys rank: a decorative animation cannot
     shove aside an error or a request still in flight. force() is the rude
     form, for the state machine itself when it knows better.
  */

  Clippy.prototype.want = function (name, opts) {
    if (!STATES[name]) return false;
    var cur = STATES[this.state];
    var next = STATES[name];
    /* a running one-shot of equal or higher rank keeps the stage */
    if (!cur.loop && this.frame < SHEET.cols - 1 && next.rank < cur.rank) return false;
    if (cur.loop && !cur.soft && next.rank < cur.rank) return false;
    this.force(name, opts);
    return true;
  };

  Clippy.prototype.force = function (name, opts) {
    opts = opts || {};
    if (!STATES[name]) return;
    if (name === this.state && !opts.restart) return;
    this.state = name;
    this.frame = reduce.matches ? STATES[name].still : 0;
    this.dir = 1;
    this.acc = 0;
    this.done = opts.then || null;
    this.after = opts.after || null;
    this.paint();
    if (!imgs.full && STATES[name].row !== 0) load("full", this.paint.bind(this));
    wake();
  };

  Clippy.prototype.destroy = function () {
    var i = live.indexOf(this);
    if (i > -1) live.splice(i, 1);
    if (this.io) this.io.disconnect();
    if (reduce.removeEventListener) reduce.removeEventListener("change", this.onReduce);
    if (this.canvas.parentNode) this.canvas.parentNode.removeChild(this.canvas);
    this.el.__clippy = null;
  };

  /* ---- exports ---------------------------------------------------------- */

  Clippy.STATES = STATES;
  Clippy.SHEET = SHEET;
  Clippy.setBase = function (p) { base = p; };
  Clippy.wake = wake;          /* for a host that drives onScreen itself */
  Clippy.preload = function () { load("full"); };
  Clippy.reduced = function () { return reduce.matches; };

  root.DVClippy = Clippy;
})(window);
