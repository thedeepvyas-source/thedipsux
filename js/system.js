/* ═══════════════════════════════════════════════════════════════
   DELTA behaviour layer — theme, sticky nav, scroll progress,
   active section, reveal-on-enter. Shared by every page.
   ═══════════════════════════════════════════════════════════════ */
(function(){
  "use strict";
  "use strict";
  var reduce = matchMedia("(prefers-reduced-motion: reduce)").matches;

  /* ── Theme ─────────────────────────────────────────────────── */
  var root = document.documentElement, tBtn = document.getElementById("theme");

  /* keep the browser chrome on the theme the page is actually showing, not on
     the one the OS prefers — run it at startup too, for a returning visitor
     who saved dark. */
  function syncThemeColor(){
    var m = document.querySelector('meta[name="theme-color"]');
    if(!m){ m = document.createElement("meta"); m.name = "theme-color"; document.head.appendChild(m); }
    m.content = root.getAttribute("data-theme") === "dark" ? "#0A0B0D" : "#FCFCFD";
  }
  syncThemeColor();

  tBtn.addEventListener("click", function(){
    var next = root.getAttribute("data-theme") === "dark" ? "light" : "dark";
    root.setAttribute("data-theme", next);
    try{ localStorage.setItem("dv26-theme", next); }catch(e){}
    syncThemeColor();
  });

  /* ── Nav: sticky border + scroll progress + active section ─── */
  var nav = document.getElementById("nav"), prog = document.getElementById("prog");

  /* The hero fills the first screen via calc(100svh - var(--nav-h)). Measure
     the nav rather than trusting a hard-coded token, so changing the logo or
     type size can't silently push the next section above the fold. The CSS
     value stays as the no-JS fallback. */
  function syncNavHeight(){
    document.documentElement.style.setProperty("--nav-h", nav.getBoundingClientRect().height + "px");
  }
  if(nav){
    syncNavHeight();
    addEventListener("resize", syncNavHeight, {passive:true});
    addEventListener("load", syncNavHeight);          /* fonts can change its height */
    if(window.ResizeObserver) new ResizeObserver(syncNavHeight).observe(nav);
  }
  var navLinks = [].slice.call(document.querySelectorAll("[data-nav]"));
  var sections = navLinks.map(function(a){ return document.querySelector(a.getAttribute("href")); });
  var ticking = false;

  function onScroll(){
    var y = window.scrollY;
    nav.classList.toggle("stuck", y > 8);
    var max = document.documentElement.scrollHeight - innerHeight;
    prog.style.width = (max > 0 ? (y / max) * 100 : 0) + "%";

    var current = -1, line = y + innerHeight * 0.32;
    for(var i = 0; i < sections.length; i++){
      if(sections[i] && sections[i].offsetTop <= line) current = i;
    }
    navLinks.forEach(function(a, i){
      if(i === current) a.setAttribute("aria-current", "true");
      else a.removeAttribute("aria-current");
    });
    ticking = false;
  }
  addEventListener("scroll", function(){
    if(!ticking){ ticking = true; requestAnimationFrame(onScroll); }
  }, {passive:true});
  onScroll();

  /* ── Reveal on enter ───────────────────────────────────────── */
  var rv = [].slice.call(document.querySelectorAll(".rv"));
  if(reduce || !("IntersectionObserver" in window)){
    rv.forEach(function(el){ el.classList.add("in"); });
  } else {
    var io = new IntersectionObserver(function(entries){
      entries.forEach(function(e){
        if(!e.isIntersecting) return;
        e.target.classList.add("in");
        io.unobserve(e.target);
      });
    }, {rootMargin:"0px 0px -8% 0px", threshold:0.06});
    rv.forEach(function(el, i){
      el.style.transitionDelay = Math.min(i % 4, 3) * 60 + "ms";
      io.observe(el);
    });
  }

  /* ── Screenshot lightbox ───────────────────────────────────────
     Every case-study screenshot gets a magnifier and opens full size.
     The button and the overlay are built here, so the page markup stays a
     plain <figure><img> and the feature degrades to a normal image
     without JS. */
  var shots = [].slice.call(
    document.querySelectorAll(".gal figure img, .art img, .chero-fig img"));

  if(shots.length){
    var MAG = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" ' +
      'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">' +
      '<circle cx="10.5" cy="10.5" r="7"/><path d="M20 20l-4.4-4.4M10.5 7.5v6M7.5 10.5h6"/></svg>';
    var EX  = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" ' +
      'stroke-linecap="round" aria-hidden="true"><path d="M6 6l12 12M18 6L6 18"/></svg>';

    var lb = document.createElement("div");
    lb.className = "lb";
    lb.setAttribute("role", "dialog");
    lb.setAttribute("aria-modal", "true");
    lb.setAttribute("aria-label", "Enlarged screenshot");
    lb.innerHTML = '<button class="lb-x" type="button" aria-label="Close">' + EX + '</button>' +
                   '<img alt=""><p class="lb-cap"></p>';
    document.body.appendChild(lb);

    var lbImg = lb.querySelector("img"),
        lbCap = lb.querySelector(".lb-cap"),
        lbX   = lb.querySelector(".lb-x"),
        opener = null;

    function open(img){
      var fig = img.closest("figure"),
          cap = fig && fig.querySelector("figcaption");
      lbImg.src = img.currentSrc || img.src;
      lbImg.alt = img.alt || "";
      lbCap.innerHTML = cap ? cap.innerHTML : (img.alt || "");
      lb.classList.add("on");
      document.body.style.overflow = "hidden";
      lbX.focus();
    }
    function close(){
      lb.classList.remove("on");
      document.body.style.overflow = "";
      if(opener){ opener.focus(); opener = null; }
    }

    shots.forEach(function(img){
      var wrap = document.createElement("span");
      wrap.className = "zoomwrap";
      img.parentNode.insertBefore(wrap, img);
      wrap.appendChild(img);

      var btn = document.createElement("button");
      btn.type = "button";
      btn.className = "zoom-btn";
      btn.innerHTML = MAG;
      btn.setAttribute("aria-label", "Enlarge: " + (img.alt || "screenshot"));
      wrap.appendChild(btn);

      btn.addEventListener("click", function(){ opener = btn; open(img); });
      img.addEventListener("click", function(){ opener = btn; open(img); });
    });

    lbX.addEventListener("click", close);
    lb.addEventListener("click", function(e){ if(e.target === lb || e.target === lbCap) close(); });
    addEventListener("keydown", function(e){
      if(e.key === "Escape" && lb.classList.contains("on")) close();
    });
  }
})();
