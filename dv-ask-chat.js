/* dv-ask-chat.js — the ask drawer as a conversation.

   On the landing page and Apex. The other four case studies still run
   dv-ask.js, the accordion this grew out of.

   The accordion made you open and shut answers one at a time and gave you
   nothing to read back: close an answer and it was as if you had never
   asked. This keeps what you asked and what you were told, in order, the
   way every assistant anyone has used in the last two years behaves.

   It invents no content. The questions and answers are the same ones
   already written into the page's <ul class="ask-q">, read out of the DOM
   on boot, so the markup stays the single source and a page with no
   JavaScript still carries every answer for a crawler to find. Free text
   is matched against those same answers; nothing matched says so and
   offers email.

   The character in the corner is driven through el.__av, exactly as the
   accordion drove it, so this does not care whether that is the sphere or
   the sprite.
*/
(function (root) {
  "use strict";

  var MAIL = "thedeepvyas@gmail.com";
  var OPEN_CLASS = "askopen";

  /* how fast an answer writes itself out, in characters a second */
  var CPS = 190;

  /* ---- matching ---------------------------------------------------------
     Lifted from the accordion unchanged. Question and keyword hits say what
     an answer is about; body text only corroborates.
  */

  var STOP = (" a about an and any are as at be been but by can could did do does for from "
    + "had has have how i if in into is it its just like me much my of on or so than that the "
    + "their them then there these they this to too was were what when where which who why "
    + "will with would you your "
    /* Added for the site search. These carry no subject, and left in they
       do real harm: "he" is in every section, so "what car does he drive"
       scored; "anywhere" is on no page, so "is there usability testing
       anywhere" looked like a question about something off-site. */
    + "also am anyone anything anywhere been being else even ever everyone everything he "
    + "her him his really she somewhere still us we your yourself "
    /* The verbs a question is built out of. They are not what it is about,
       and left in they steer the whole search: "tell me his hobby" found
       myAster, whose headline begins "Telling patients what their
       insurance allows". The subject was "hobby"; "tell" was grammar. */
    + "describe explain find give help know let list look make need please "
    + "say see share show talk tell want write ").split(" ");

  function terms(q) {
    var raw = q.toLowerCase().replace(/[^a-z0-9]+/g, " ").split(" ");
    var out = [], seen = {};
    for (var i = 0; i < raw.length; i++) {
      var t = raw[i];
      if (t.length < 2 || seen[t] || STOP.indexOf(t) > -1) continue;
      seen[t] = 1; out.push(t);
    }
    return out;
  }
  function hay(s) { return " " + s.toLowerCase().replace(/[^a-z0-9]+/g, " ") + " "; }
  function esc(s) {
    return String(s).replace(/&/g, "&amp;").replace(/</g, "&lt;")
                    .replace(/>/g, "&gt;").replace(/"/g, "&quot;");
  }
  function stem(t) { return t.replace(/ied$/, "y").replace(/(ing|ed|es|s)$/, ""); }
  /* A word has to be a whole word, give or take an ordinary ending. The
     accordion matched on a prefix, which is forgiving and was fine for a
     list of fourteen; across fifteen thousand words it is not, because
     "car" finds "career" and the drawer answers a question about his car
     with a line about mentoring. */
  function hasw(h, t) {
    if (new RegExp("\\s" + t + "(s|es|ed|ing)?\\s").test(h)) return true;
    var s = stem(t);
    return s.length >= 4 && s !== t
      && new RegExp("\\s" + s + "(s|es|ed|ing|y|ies)?\\s").test(h);
  }

  /* ---- the rest of the site ---------------------------------------------
     The written answers above only ever covered the page they sit on, so
     "who is Deep" had nowhere to land although the answer is in #about on
     the landing page.

     ask-index.json, built by build-ask-index.py, is every section of every
     linked page: its heading, its anchor, and its sentences. When none of
     the written answers fit, we search that and reply with the sentences
     themselves — his words, unaltered, with a link to where they live.
     Nothing is composed, so nothing can be invented. The cost is that it
     retrieves rather than reasons: it will find the passage that answers
     you, not write you a new paragraph that draws two pages together.
  */

  var Site = {
    url: "ask-index.json",
    data: null,
    tried: false,
    loading: null
  };

  Site.load = function () {
    if (Site.data || Site.tried) return Site.loading || Promise.resolve(Site.data);
    if (typeof fetch !== "function") { Site.tried = true; return Promise.resolve(null); }
    Site.loading = fetch(Site.url, { credentials: "same-origin" })
      .then(function (r) { return r.ok ? r.json() : null; })
      .then(function (d) { Site.tried = true; Site.data = d && d.secs ? Site.prep(d) : null; return Site.data; })
      .catch(function () { Site.tried = true; return null; });
    return Site.loading;
  };

  /* one pass at load: the searchable form of every section, and how common
     each word is across all of them, so "design" counts for less than
     "ahmedabad" */
  Site.prep = function (d) {
    var df = {};
    d.pages.forEach(function (p) { p.ht = hay(p.t); });
    d.secs.forEach(function (s) {
      s.hh = hay(s.h);
      s.hs = s.s.map(hay);
      /* the hero's tag words ("Healthcare operations", "iOS and Android")
         are searched on but never read back, so they live outside s.s */
      s.hb = " " + (s.hs.join(" ") + " " + hay(s.k || ""))
        .replace(/\s+/g, " ").replace(/^ | $/g, "") + " ";
      var seen = {};
      s.hb.split(" ").forEach(function (w) {
        if (!w || seen[w]) return;
        seen[w] = 1; df[w] = (df[w] || 0) + 1;
      });
    });
    d.df = df;
    d.n = d.secs.length;
    return d;
  };

  /* Does the question name a project other than the one we are standing on?
     Only the distinctive words count: every page title contains "portal" or
     "designer" somewhere, and those name nothing. */
  Site.namesOtherPage = function (q) {
    var d = Site.data;
    if (!d) return false;
    var here = (location.pathname.split("/").pop() || "index.html");
    var hq = hay(q);
    return d.pages.some(function (p) {
      if (p.u === here || p.u === "index.html") return false;
      return terms(p.t).some(function (t) {
        return Site.weight(d, t) >= 1.5 && hasw(hq, t);
      });
    });
  };

  Site.weight = function (d, t) {
    var n = d.df[t] || d.df[stem(t)] || 0;
    /* in every section, so it separates nothing; in one, so it decides it */
    return Math.max(0.25, Math.log((d.n + 1) / (n + 1)));
  };

  /* A handful of questions are about Deep rather than about any wording on
     the page — "who is Deep", "what's his background", "how do I hire him".
     Word overlap cannot answer those, because the words they use ("who",
     "background", "hire") are not the words the section is written in. So
     these few route straight to the section that holds the answer. They are
     routes, not answers: what comes back is still the page's own sentences.
  */
  var ROUTES = [
    { at: "index.html#about",
      re: /\b(who\s+(is|are)\s+(deep|you|he|the designer)|tell me about (deep|you|him|yourself)|what'?s? (deep'?s?|your|his) (background|story|bio)|introduce (yourself|deep))\b|^\s*(about )?deep( vyas)?\s*\??$|\b(biography|where (do you|does he|is he|are you) (live|based|from)|how many years|years? of experience|how long have (you|he) been|which city|r[ée]sum[ée])\b|\b(stud(y|ied|ies)|degree|university|college|education)\b|\b(where (did|have) (you|he) work|(previous|past|earlier) (job|role|company|employer)|which companies|employment history|worked (at|for) (which|what))\b/i },
    { at: "index.html#how",
      re: /\b(how do(es)? (you|he) (work|design|lead)|(your|his) (process|approach|method|way of working)|what'?s? (your|his) process)\b/i },
    { at: "index.html#work",
      re: /\b(what (projects|work|case studies)|show me (your|his|the) (work|projects)|portfolio|all (five|5) (projects|case studies))\b/i },
    { at: "index.html#mentoring",
      re: /\b(mentor(ing|ship)?|adplist|portfolio review)\b/i },
    { at: "index.html#contact",
      re: /\b(hire|hiring|available for|availability|notice period|freelance|contact|get in touch|reach (you|him)|your email|linkedin|phone|mobile number|whatsapp|call (you|him))\b/i }
  ];

  /* Things a portfolio does not talk about.

     Several of these words are on the site in another sense — "pet" is a
     product, "blood" is glucose in a diabetic cat, "drive" is something a
     decision does — so word matching finds them a confident answer about
     something else entirely. Asked about his pet, the honest reply is
     that this is not on the site. */
  var OFFTOPIC = {};
  (" age astrology birthday blood born bike car caste child children cricket ctc cuisine "
   + "dob drink drive family father film food football gender girlfriend height horoscope "
   + "husband joke kids marriage married mother movie music parents pet pets politics "
   + "religion salary sibling siblings song sport sports tall vegetarian weight wife zodiac "
  ).trim().split(/\s+/).forEach(function (w) { OFFTOPIC[w] = 1; });

  /* Asked as a phrase rather than carried by one word. "Old" cannot go in
     the list above — IGEL's portal is ten years old, and that is a fair
     thing to ask — but "how old is he" is not a question about a portal. */
  var OFFTOPIC_RE = /\bhow old (is|are) (he|you|deep)\b|\b(his|your|deep'?s) age\b|\bdate of birth\b|\bwhere (was|were) (he|you) born\b|\bhow much (do|does) (he|you) (earn|make|charge)\b/i;

  Site.offTopic = function (q) {
    if (OFFTOPIC_RE.test(q)) return true;
    return terms(q).some(function (t) {
      return OFFTOPIC[t] || OFFTOPIC[stem(t)];
    });
  };

  Site.routed = function (q) {
    for (var i = 0; i < ROUTES.length; i++) if (ROUTES[i].re.test(q)) return ROUTES[i].at;
    return null;
  };
  function routed(q) { return Site.routed(q); }

  /* The one word in a question that most decides what it is about: the
     rarest. "Do you know Python" is about Python, not about knowing, and
     "python" is nowhere on the site — so neither is the answer. Whatever we
     are about to say has to contain this word, or we are answering a
     different question from the one asked. */
  /* A visitor's word for something the site calls something else. "What is
     Deep's hobby" is a fair question and the site answers it — in the
     sentence about running a UX community outside client work — but the
     word "hobby" is nowhere on it.

     Only words where the content really exists go in here. A synonym that
     points at nothing is worse than an honest miss, because it turns "I
     can't find that" into a confident paragraph about something else. */
  var SYN = {
    hobby:      ["outside", "community", "mentor"],
    hobbies:    ["outside", "community", "mentor"],
    interest:   ["outside", "community", "mentor"],
    interests:  ["outside", "community", "mentor"],
    pastime:    ["outside", "community"],
    passion:    ["outside", "community"],
    bio:        ["engineer", "ahmedabad", "studied"],
    cv:         ["resume"],
    speciality: ["research", "strategy", "screens"],
    specialty:  ["research", "strategy", "screens"],
    expertise:  ["research", "strategy", "screens"],
    strengths:  ["research", "strategy", "screens"],
    city:       ["ahmedabad"],
    country:    ["india"],
    located:    ["ahmedabad", "india"],
    location:   ["ahmedabad", "india"],
    teaching:   ["mentor"],
    teach:      ["mentor"],
    coaching:   ["mentor"],
    coach:      ["mentor"],
    enterprise: ["b2b"],
    consumer:   ["b2c"],
    /* the only project whose name is two words on the page and usually one
       word when someone types it */
    flintlink:  ["flint", "link"]
  };

  /* every word to search for, and what each is worth. A synonym the
     visitor did not actually type counts for less than one they did. */
  Site.expand = function (q) {
    var d = Site.data, out = [], seen = {};
    terms(q).forEach(function (t) {
      if (!seen[t]) { seen[t] = 1; out.push({ t: t, w: Site.weight(d, t), from: t }); }
      (SYN[t] || SYN[stem(t)] || []).forEach(function (sy) {
        if (seen[sy]) return;
        seen[sy] = 1;
        /* "from" is the word the visitor typed. A synonym standing in for
           it still covers it — otherwise "what are his hobbies" matches
           the right sentence and is then thrown away for not containing
           the word "hobbies". */
        out.push({ t: sy, w: Site.weight(d, sy) * 0.7, from: t });
      });
    });
    return out;
  };

  Site.rarest = function (q) {
    var d = Site.data;
    if (!d) return null;
    var best = null, bw = 0;
    Site.expand(q).forEach(function (x) {
      if (!(d.df[x.t] || d.df[stem(x.t)])) return;    /* not on the site */
      if (x.w > bw && x.w >= 1.2) { bw = x.w; best = x.t; }
    });
    return best;
  };

  /* A word of substance that appears nowhere on the site, and nowhere in
     the answers written for this page either. "Do you know Python" has one,
     and the honest reply is that there is nothing here about it — better
     than the closest paragraph about knowing something else. */
  Site.hasUnknown = function (q, extra) {
    var d = Site.data;
    if (!d) return false;
    return terms(q).some(function (t) {
      if (t.length < 3) return false;
      if (d.df[t] || d.df[stem(t)]) return false;
      if (SYN[t] || SYN[stem(t)]) return false;   /* the site says it differently */
      return !(extra && hasw(extra, t));
    });
  };

  /* the best section for a question, and the sentences in it that answer it */
  Site.find = function (q) {
    var d = Site.data;
    if (!d) return null;
    var ts = Site.expand(q), route = routed(q);
    if (!ts.length && !route) return null;

    /* The rarest word steers the search rather than vetoing it afterwards.
       Ask "have you worked in healthcare" and "worked" is everywhere while
       "healthcare" is in one section: rank over the whole site and "worked"
       wins a section that is not about healthcare at all. So the sections
       holding the rare word are the only ones considered — plus whatever a
       route points at, which was chosen deliberately. */
    var rare = Site.rarest(q);
    var known = !!rare;

    var pool = d.secs;
    if (known) {
      pool = d.secs.filter(function (s) {
        return hasw(s.hb, rare) || hasw(d.pages[s.p].ht, rare)
          || (route && d.pages[s.p].u + "#" + s.a === route);
      });
      if (!pool.length) pool = d.secs;
    }

    var best = null;
    pool.forEach(function (s) {
      var page = d.pages[s.p];
      var at = page.u + "#" + s.a;
      var sc = 0, got = {};
      ts.forEach(function (x) {
        var hit = false;
        if (hasw(s.hh, x.t)) { sc += 3 * x.w; hit = true; }
        else if (hasw(s.hb, x.t)) { sc += x.w; hit = true; }
        /* naming the project is naming the page it is on */
        if (hasw(page.ht, x.t)) { sc += 2.5; hit = true; }
        if (hit) got[x.from] = 1;
      });
      /* coverage counts the words the visitor typed that this section
         answers, whether directly or through a synonym */
      var cov = 0;
      for (var g in got) if (got.hasOwnProperty(g)) cov++;
      /* A route was declared by hand for a question word overlap cannot
         answer, so it has to outweigh word overlap. At +6 it did not:
         "how many years of experience" lost to the IGEL hero, whose
         heading happens to say "twice a year". */
      if (route && at === route) { sc += 12; cov = ts.length; }
      if (!best || sc > best.sc)
        best = { s: s, sc: sc, cov: cov, at: at, page: page };
    });
    if (!best) return null;

    /* Two ways to be wrong here, and the second is the dangerous one. A
       weak best match is not an answer, it is the least bad paragraph on
       the site. And a question where only one word in four landed anywhere
       is a question about something else: "what car does he drive" must not
       be answered with the mentoring section because both say "he". So the
       match has to be strong AND it has to cover half of what was asked. */
    /* Half the words the visitor typed have to land somewhere. Requiring
       all of them for a short question was tried, to stop "blood type"
       finding PetTrackr's blood-glucose sentence, and it cost more than it
       saved: "have you worked in healthcare" and "did you do interviews on
       PetTrackr" both went unanswered, which is the failure that matters. */
    var typed = terms(q).length;
    var need = Math.max(1, Math.ceil(typed / 2));
    if (best.sc < (route ? 12 : 1.8)) return null;
    if (typed && best.cov < need) return null;

    var sents = best.s.s, pick;
    if ((route && best.at === route) || best.s.a === "") {
      /* the question is about the section as a whole — or about the page,
         and this is its hero — so read from the top */
      pick = [0, 1, 2].filter(function (i) { return i < sents.length; });
    } else {
      var ranked = sents.map(function (_, i) {
        var h = best.s.hs[i], sc = 0;
        ts.forEach(function (x) { if (hasw(h, x.t)) sc += x.w; });
        return { i: i, sc: sc };
      }).filter(function (r) { return r.sc > 0; })
        .sort(function (a, b) { return b.sc - a.sc; })
        .slice(0, 3)
        .sort(function (a, b) { return a.i - b.i; });
      pick = ranked.map(function (r) { return r.i; });
      if (!pick.length) pick = [0];
    }

    /* three sentences is a reply; ten is the page, and they can read that
       by following the link */
    var out = [], chars = 0;
    for (var k = 0; k < pick.length; k++) {
      var t = sents[pick[k]];
      if (chars && chars + t.length > 420) break;
      out.push(t); chars += t.length;
    }
    return { lines: out, at: best.at, head: best.s.h, page: best.page, sc: best.sc };
  };

  /* ---- the drawer -------------------------------------------------------- */

  function Chat(btn, panel) {
    this.btn = btn;
    this.panel = panel;
    this.open = false;
    this.turn = 0;
    this.asked = 0;
    this.used = {};        /* questions already put to it, by their text */
    this.streaming = null;
    this.harvest();
    this.build();
    this.bind();
  }

  /* every question the page already carries, read straight out of it */
  Chat.prototype.harvest = function () {
    var self = this;
    this.kb = [];
    [].forEach.call(this.panel.querySelectorAll(".ask-q > li"), function (li) {
      var b = li.querySelector("button");
      var a = li.querySelector(".ask-a");
      if (!b || !a) return;
      self.kb.push({
        q: b.textContent.trim(),
        k: li.getAttribute("data-k") || "",
        html: a.innerHTML,
        start: !li.classList.contains("ask-more"),
        hq: hay(b.textContent),
        hk: hay(li.getAttribute("data-k") || ""),
        ha: hay(a.textContent)
      });
    });

    /* everything this page's own answers say, in one string. The site
       index does not contain the drawer, so a word that lives only in a
       written answer would otherwise look like a word that is nowhere. */
    this.allHay = " " + this.kb.map(function (e) {
      return e.hq + e.hk + e.ha;
    }).join(" ").replace(/\s+/g, " ").replace(/^ | $/g, "") + " ";
  };

  Chat.prototype.build = function () {
    var p = this.panel;

    /* the face goes into the scroll flow rather than sitting in a band of
       its own: it is a greeting, not a header, and it should scroll away
       once there is a conversation to read */
    var scroll = p.querySelector(".ask-scroll");
    var face = p.querySelector(".ask-face");
    if (face && scroll) scroll.insertBefore(face, scroll.firstChild);

    /* the written markup stays in the page for anything that cannot run
       this, and stops being the interface */
    [].forEach.call(p.querySelectorAll(".ask-q, .ask-lbl"), function (n) {
      n.setAttribute("hidden", "");
    });

    var opener = document.createElement("div");
    opener.className = "ask-start";
    this.kb.filter(function (e) { return e.start; }).forEach(function (e) {
      var b = document.createElement("button");
      b.type = "button";
      b.className = "ask-start-q";
      b.textContent = e.q;
      opener.appendChild(b);
    });
    scroll.appendChild(opener);
    this.opener = opener;

    var log = document.createElement("div");
    log.className = "ask-log";
    log.setAttribute("role", "log");
    log.setAttribute("aria-live", "polite");
    log.setAttribute("aria-label", "Questions and answers");
    scroll.appendChild(log);
    this.log = log;
    this.scroll = scroll;

    /* start over, next to close, once there is something to start over from */
    var reset = document.createElement("button");
    reset.type = "button";
    reset.className = "ask-reset";
    reset.setAttribute("aria-label", "Start over");
    reset.hidden = true;
    reset.innerHTML = '<svg viewBox="0 0 16 16" width="16" height="16" fill="none" '
      + 'stroke="currentColor" stroke-width="1.5" stroke-linecap="round" '
      + 'stroke-linejoin="round" aria-hidden="true">'
      + '<path d="M13.5 8a5.5 5.5 0 1 1-1.9-4.2"/><path d="M13.5 2v3.2h-3.2"/></svg>';
    var x = p.querySelector(".ask-x");
    x.parentNode.insertBefore(reset, x);
    this.reset = reset;

    this.input = p.querySelector(".ask-find input");
    this.note = p.querySelector(".ask-note");
    this.hint = p.querySelector(".ask-hint");
  };

  /* ---- the character ----------------------------------------------------- */

  Chat.prototype.avatars = function () {
    var out = [];
    var a = this.btn.querySelector("[data-avatar]");
    var b = this.panel.querySelector("[data-avatar]");
    if (a && a.__av) out.push(a.__av);
    if (b && b.__av) out.push(b.__av);
    return out;
  };

  Chat.prototype.face = function (name, on) {
    this.avatars().forEach(function (av) {
      try { av.setState(name, on); } catch (e) {}
    });
  };

  /* ---- opening and closing ----------------------------------------------- */

  Chat.prototype.setOpen = function (on) {
    if (on === this.open) return;
    this.open = on;
    var self = this;

    this.btn.setAttribute("aria-expanded", String(on));
    this.btn.classList.toggle("hid", on);
    document.documentElement.classList.toggle(OPEN_CLASS, on);

    /* the rest of the site is a 90 KB file nobody who never opens the
       drawer should pay for. Opening it is the first sign they might ask
       something, so fetch it then, not on page load. */
    if (on) Site.load();

    /* on a narrow screen the drawer covers the page instead of pushing it,
       and a dialog you cannot see past is a modal one */
    var covers = matchMedia("(max-width: 860px)").matches;
    var page = document.querySelector(".page");

    if (on) {
      this.panel.hidden = false;
      this.modal = covers;
      if (covers) {
        this.panel.setAttribute("aria-modal", "true");
        if (page && "inert" in HTMLElement.prototype) page.inert = true;
      }
      /* a hidden element has no box, so the panel's character mounted at
         1px. It needs its size read once it is actually laid out */
      requestAnimationFrame(function () {
        self.panel.classList.add("on");
        self.avatars().forEach(function (av) {
          if (av.resize) av.resize();
          if (av.sense) av.sense();
        });
        self.face("glitch", true);
        self.panel.focus();
      });
    } else {
      this.panel.removeAttribute("aria-modal");
      if (page && "inert" in HTMLElement.prototype) page.inert = false;
      this.modal = false;
      this.panel.classList.remove("on");
      this.face("glitch", true);
      var ms = this.panel.classList.contains("noanim") ? 0 : 420;
      clearTimeout(this.hideTimer);
      this.hideTimer = setTimeout(function () { self.panel.hidden = true; }, ms);
      this.btn.focus();
    }
  };

  /* ---- asking ------------------------------------------------------------ */

  Chat.prototype.match = function (query) {
    var ts = terms(query);

    /* Some questions are made entirely of the words a question is made of.
       "What do you do?" is six stopwords and nothing else, and it is one of
       the suggestions on the landing page — typing a question that is
       written on the panel in front of you has to work. So when nothing is
       left to score, fall back to matching the question itself. */
    if (!ts.length) {
      var nq = hay(query).replace(/^ | $/g, "");
      if (nq.length < 3) return [];
      var same = [];
      this.kb.forEach(function (e) {
        if (e.hq.indexOf(" " + nq + " ") > -1) same.push({ e: e, s: 9 });
      });
      return same.slice(0, 3);
    }
    var hits = [];
    this.kb.forEach(function (e) {
      var s = 0;
      ts.forEach(function (t) {
        if (hasw(e.hq, t) || hasw(e.hk, t)) s += 3;
        else if (hasw(e.ha, t)) s += 1;
      });
      /* one strong hit stands on its own; otherwise every word typed has to
         land somewhere, so a long question is not answered by one stray
         body word */
      if (s >= 3 || s >= ts.length) hits.push({ e: e, s: s });
    });
    if (hits.some(function (h) { return h.s >= 3; }))
      hits = hits.filter(function (h) { return h.s >= 3; });
    hits.sort(function (a, b) { return b.s - a.s; });
    return hits.slice(0, 3);
  };

  Chat.prototype.row = function (role, html) {
    var d = document.createElement("div");
    d.className = "ask-row ask-" + role;
    var inner = document.createElement("div");
    inner.className = "ask-bub";
    inner.innerHTML = html;
    d.appendChild(inner);
    this.log.appendChild(d);
    this.scroll.scrollTop = this.scroll.scrollHeight;
    return d;
  };

  /* Each question carries its own dots and takes them away itself. One
     shared pair went wrong the moment two questions overlapped: the second
     one's handler cleared the first one's. */
  Chat.prototype.waiting = function () {
    var d = document.createElement("div");
    d.className = "ask-row ask-reply ask-wait";
    d.innerHTML = '<span class="ask-dots" aria-hidden="true"><i></i><i></i><i></i></span>';
    this.log.appendChild(d);
    this.scroll.scrollTop = this.scroll.scrollHeight;
    return d;
  };

  Chat.prototype.send = function (text, entry) {
    var q = (text || "").replace(/\s+/g, " ").trim();
    if (!q) { this.input.focus(); return; }

    if (this.streaming) this.streaming.finish();
    var turn = ++this.turn;
    var self = this;

    /* the opening block has done its job the moment there is a real
       conversation to read */
    if (!this.asked) {
      this.opener.hidden = true;
      if (this.hint) this.hint.hidden = true;
      this.reset.hidden = false;
      this.panel.classList.add("talking");
    }
    this.asked++;
    this.input.value = "";

    this.row("you", "").querySelector(".ask-bub").textContent = q;
    var dots = this.waiting();
    this.face("thinking", true);
    this.note.textContent = "Looking…";

    var hits = entry ? [{ e: entry, s: 99 }] : this.match(q);
    /* whatever this turned out to be about is now spent: a conversation
       that keeps offering you the thing you just asked is not listening */
    if (entry) this.used[entry.q] = 1;
    else if (hits.length) this.used[hits[0].e.q] = 1;
    /* a pause, because an answer that lands the instant you ask reads as a
       lookup rather than a reply. It is a lookup, but it is a real one */
    setTimeout(function () {
      /* no turn guard here: a question asked over the top of another must
         still get its answer, or the first one is left hanging with a
         bubble and nothing under it */
      if (dots.parentNode) dots.parentNode.removeChild(dots);
      self.face("thinking", false);

      function written() {
        var top = hits[0].e;
        var more = hits.slice(1).map(function (h) { return h.e; });
        var row = self.row("reply", "");
        self.face("explaining", true);
        /* the line said "Looking..." while the answer was already arriving */
        self.note.textContent = "";
        self.stream(row, top.html, turn, function () {
          self.face("explaining", false);
          self.note.textContent = "Answered.";
          /* only the newest answer carries the suggestions; an older one
             finishing late must not drag them back up the page */
          if (turn === self.turn) self.offer(more);
        });
      }

      /* A tapped suggestion is not a search: it already is the answer. */
      if (entry) { written(); return; }

      /* Otherwise the page's written answers and the rest of the site both
         get a say, and two things decide between them.

         A written answer wins when the question or its keywords matched
         (a score of 3 or more), because then Deep has written an answer to
         this exact question and it is better than any paragraph retrieval
         can find. A body-only match is just a word that happened to appear,
         and the site usually beats it.

         And naming another project overrules both: ask "what is IGEL" here
         and the Apex answer that mentions IGEL in passing is not what you
         wanted, however well it scores. */
      Site.load().then(function () {
        /* asked about his car, his pet or his salary, the only honest
           answer is that the site does not say — never the paragraph that
           happens to share a word with the question */
        if (Site.offTopic(q)) { self.noAnswer(q); return; }

        var rare = Site.rarest(q);
        var kbCovers = hits.length && (!rare || hasw(
          " " + hits[0].e.hq + " " + hits[0].e.hk + " " + hits[0].e.ha + " ", rare));
        var strong = hits.length && hits[0].s >= 3 && kbCovers;
        var isRouted = !!Site.routed(q);
        var elsewhere = Site.namesOtherPage(q);

        /* a word of substance that is on no page and in no written answer:
           the question is about something this site does not cover, and
           the closest paragraph would be a guess dressed as an answer */
        if (!isRouted && Site.hasUnknown(q, self.allHay)) { self.noAnswer(q); return; }

        var found = null;
        if (!strong || elsewhere || isRouted) {
          try { found = Site.find(q); } catch (e) { found = null; }
        }
        if (found && (elsewhere || isRouted || !strong)) {
          self.fromSite(found, turn);
          return;
        }
        if (hits.length && kbCovers) { written(); return; }
        self.noAnswer(q);
      });
    }, 260 + Math.random() * 220);
  };

  /* What is worth asking next: whatever else matched, then the openers,
     then anything at all - and never something already asked. Running out
     is a real state and says so rather than looping the same four.
  */
  /* an answer taken from another part of the site: his sentences as they
     are written there, and a link to read the rest in place */
  Chat.prototype.fromSite = function (found, turn) {
    var self = this;
    var here = (location.pathname.split("/").pop() || "index.html");
    var at = found.at.replace(/#$/, "");     /* a hero has no anchor */
    var href = at.indexOf(here + "#") === 0 ? at.slice(here.length) : at;
    var html = "";
    found.lines.forEach(function (t) { html += "<p>" + esc(t) + "</p>"; });
    /* "The problem, on Apex Insights" tells you where you are going; on the
       landing page the page's name is his own, and "About, on Deep Vyas"
       reads like a filing error */
    html += '<p class="ask-jump"><a href="' + esc(href) + '">' + esc(found.head)
          + (found.page.u === "index.html" ? "" : ", on " + esc(found.page.t))
          + " →</a></p>";

    var row = this.row("reply", "");
    this.face("explaining", true);
    this.note.textContent = "";
    this.stream(row, html, turn, function () {
      self.face("explaining", false);
      self.note.textContent = "Answered from " + found.page.t + ".";
      if (turn === self.turn) self.offer([]);
    });
  };

  Chat.prototype.noAnswer = function (q) {
    var miss = this.row("reply", "");
    var p = document.createElement("p");
    p.textContent = "I can’t find that anywhere on the site, and I’d rather "
      + "not guess. ";
    var a = document.createElement("a");
    a.href = "mailto:" + MAIL + "?subject="
      + encodeURIComponent((this.panel.getAttribute("data-case") || document.title)
        + " — a question")
      + "&body=" + encodeURIComponent(q + "\n\n");
    a.textContent = "Send it to Deep";
    p.appendChild(a);
    p.appendChild(document.createTextNode(" and he’ll reply."));
    miss.querySelector(".ask-bub").appendChild(p);
    this.note.textContent = "No answer for that one yet.";
    this.scroll.scrollTop = this.scroll.scrollHeight;
  };

  Chat.prototype.offer = function (list) {
    if (this.more && this.more.parentNode) this.more.parentNode.removeChild(this.more);
    this.more = null;
    var self = this;
    var fresh = function (e) { return !self.used[e.q]; };

    var pool = (list || []).filter(fresh);
    var add = function (xs) {
      xs.filter(fresh).forEach(function (e) {
        if (pool.length < 3 && pool.indexOf(e) < 0) pool.push(e);
      });
    };
    add(this.kb.filter(function (e) { return e.start; }));
    add(this.kb);

    var d = document.createElement("div");
    d.className = "ask-more-q";

    if (!pool.length) {
      var p = document.createElement("p");
      p.className = "ask-spent";
      p.textContent = "That is everything written for this one. ";
      var a = document.createElement("a");
      a.href = "mailto:" + MAIL + "?subject="
        + encodeURIComponent((this.panel.getAttribute("data-case") || document.title)
          + " \u2014 a question");
      a.textContent = "Anything else is better over email";
      p.appendChild(a);
      p.appendChild(document.createTextNode("."));
      d.appendChild(p);
    } else {
      pool.forEach(function (e) {
        var b = document.createElement("button");
        b.type = "button";
        b.className = "ask-start-q";
        b.textContent = e.q;
        d.appendChild(b);
      });
    }

    this.log.appendChild(d);
    this.more = d;
    this.scroll.scrollTop = this.scroll.scrollHeight;
  };

  /* ---- writing the answer out --------------------------------------------

     Walk the built DOM and fill its text nodes in order. Slicing the HTML
     string instead would show half a tag. The screen reader gets the whole
     answer once, from a copy that is there from the start, rather than a
     stutter of fragments.
  */

  Chat.prototype.stream = function (row, html, turn, done) {
    var self = this;
    var bub = row.querySelector(".ask-bub");

    var vis = document.createElement("div");
    vis.innerHTML = html;
    var sr = document.createElement("p");
    sr.className = "ask-sr";
    sr.textContent = vis.textContent;
    vis.setAttribute("aria-hidden", "true");
    bub.appendChild(vis);
    bub.appendChild(sr);

    var nodes = [], total = 0;
    (function walk(n) {
      for (var c = n.firstChild; c; c = c.nextSibling) {
        if (c.nodeType === 3) { nodes.push({ n: c, t: c.nodeValue }); total += c.nodeValue.length; c.nodeValue = ""; }
        else if (c.nodeType === 1) walk(c);
      }
    })(vis);

    var caret = document.createElement("span");
    caret.className = "ask-caret";
    caret.setAttribute("aria-hidden", "true");

    function finish() {
      if (self.streaming) self.streaming = null;
      nodes.forEach(function (x) { x.n.nodeValue = x.t; });
      if (caret.parentNode) caret.parentNode.removeChild(caret);
      self.scroll.scrollTop = self.scroll.scrollHeight;
      done();
    }

    var still = matchMedia("(prefers-reduced-motion: reduce)").matches;
    if (!total || still) { finish(); return; }

    var t0 = performance.now(), shown = 0, at = -1;
    this.streaming = { finish: finish, turn: turn };
    (function step(now) {
      if (!self.streaming || self.turn !== turn) return;
      var want = Math.min(total, Math.round((now - t0) / 1000 * CPS));
      if (want > shown) {
        var left = want, head = 0;
        for (var i = 0; i < nodes.length; i++) {
          var len = nodes[i].t.length;
          if (left >= len) { nodes[i].n.nodeValue = nodes[i].t; left -= len; head = i; }
          else { nodes[i].n.nodeValue = nodes[i].t.slice(0, left); if (left > 0) head = i; left = 0; }
        }
        if (head !== at) {
          at = head;
          var n = nodes[head].n;
          n.parentNode.insertBefore(caret, n.nextSibling);
        }
        shown = want;
        self.scroll.scrollTop = self.scroll.scrollHeight;
      }
      if (shown < total) requestAnimationFrame(step); else finish();
    })(performance.now());
  };

  /* ---- start over --------------------------------------------------------- */

  Chat.prototype.clear = function () {
    this.turn++;
    this.streaming = null;
    this.log.textContent = "";
    this.more = null;
    this.asked = 0;
    this.used = {};
    this.opener.hidden = false;
    if (this.hint) this.hint.hidden = false;
    this.reset.hidden = true;
    this.panel.classList.remove("talking");
    this.note.textContent = "Cleared.";
    this.input.value = "";
    this.scroll.scrollTop = 0;
    this.input.focus();
  };

  /* ---- wiring -------------------------------------------------------------- */

  Chat.prototype.bind = function () {
    var self = this;

    this.btn.addEventListener("click", function () { self.setOpen(!self.open); });
    this.reset.addEventListener("click", function () { self.clear(); });
    this.panel.querySelector(".ask-x").addEventListener("click", function () {
      self.setOpen(false);
    });

    this.panel.querySelector(".ask-find").addEventListener("submit", function (e) {
      e.preventDefault();
      self.send(self.input.value);
    });

    this.panel.addEventListener("click", function (e) {
      var t = e.target;

      var q = t.closest(".ask-start-q");
      if (q) {
        var text = q.textContent;
        var hit = null;
        for (var i = 0; i < self.kb.length; i++)
          if (self.kb[i].q === text) { hit = self.kb[i]; break; }
        self.send(text, hit);
        if (!self.modal) self.input.focus();
        return;
      }

      /* an answer still arriving: show the rest of it rather than make
         someone wait out an animation they have already read past */
      if (self.streaming && t.closest(".ask-reply")) { self.streaming.finish(); return; }

      /* a link into the page works as it is while the drawer only pushes
         the page aside. Once the drawer covers it, the page behind is
         inert, so get out of the way first and let the hash do its work */
      if (t.closest(".ask-jump a") && self.modal) { self.setOpen(false); }
    });

    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape" && self.open) { e.stopPropagation(); self.setOpen(false); }
    });
  };

  Chat.mount = function () {
    var btn = document.querySelector(".avbtn");
    var panel = document.getElementById("ask");
    if (!btn || !panel) return null;
    panel.hidden = true;
    panel.classList.remove("on");
    return new Chat(btn, panel);
  };

  if (document.readyState === "loading")
    addEventListener("DOMContentLoaded", function () { root.dvAsk = Chat.mount(); });
  else root.dvAsk = Chat.mount();

  root.DVAskChat = Chat;
  Chat.Site = Site;          /* the site index, for tests */
})(window);
