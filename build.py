#!/usr/bin/env python3
"""
DELTA — case-study generator.

Six static pages from one template, so every case study reads the same spine:
Problem → Research → Strategy → Design → Impact → Reflection.

    python3 build.py

Content is quoted from the source case studies. No claim is invented here.
"""
import html, os, re, struct

IMG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "img")

# ── Case-page styles (the shared system lives in css/system.css) ────────
CSS = """
/* ── Case hero ─────────────────────────────────────────────────── */
.back{padding-top:clamp(26px,4vw,44px)}
.back a{font-weight:600;font-size:var(--t-label);letter-spacing:.12em;text-transform:uppercase;color:var(--faint)}
.back a:hover{color:var(--accent)}
.chero{padding-top:clamp(20px,3vw,34px)}
/* pills, as drawn in the Figma master brief, in place of the dotted kicker */
.chero .kick{display:flex;flex-wrap:wrap;align-items:center;gap:8px;margin-bottom:clamp(22px,2.8vw,32px)}
.chero .kick .dot{display:none}
.chero .kick span:not(.dot){font-weight:600;font-size:10.5px;letter-spacing:.14em;
  text-transform:uppercase;color:var(--ink-2);border:1px solid var(--line);
  border-radius:999px;padding:7px 13px;line-height:1}
.chero h1{font-size:clamp(30px,4.45vw,64px);font-weight:600;line-height:1.125;letter-spacing:-.03em}
/* the file sets the headline in one weight and one colour */
.chero h1 em{font-style:normal;font-weight:inherit;color:inherit;letter-spacing:inherit}
.sum2{margin-top:clamp(14px,1.6vw,20px)}
.chero .sum{margin-top:clamp(22px,2.8vw,34px);font-size:clamp(17px,1.6vw,20px);line-height:1.6;color:var(--muted)}
.meta{margin-top:clamp(34px,4vw,52px);display:grid;grid-template-columns:repeat(auto-fit,minmax(176px,1fr));gap:1px;
  background:var(--line-2);border-block:1px solid var(--line-2)}
/* The 1px gaps are divider rules, so every cell needs breathing room on the
   side a rule falls — except the one that opens a row, which stays flush with
   the content edge. The exception moves with the column count. */
.meta div{background:var(--bg);padding:18px 24px 20px 24px}
.meta div:first-child{padding-left:0}
.meta dt{font-weight:600;font-size:10.5px;letter-spacing:.15em;text-transform:uppercase;color:var(--faint);margin-bottom:8px}
.meta dd{font-size:14.5px;line-height:1.5;color:var(--ink);font-weight:450}
.chero-fig{margin-top:clamp(34px,4.4vw,60px)}
/* the case heroes are 16:9; the frame matches so none of them is cropped */
.chero-fig img{width:100%;aspect-ratio:16/9;object-fit:cover;object-position:top center;
  border-radius:var(--r);background:var(--raise)}
.chero-note{font-weight:600;margin-top:14px;font-size:11px;letter-spacing:.06em;color:var(--faint)}
.chero-fig.full img{aspect-ratio:auto;object-fit:contain}
.chero-fig figcaption{font-weight:600;margin-top:12px;font-size:11px;letter-spacing:.06em;color:var(--faint)}

/* ── Outcome bar ───────────────────────────────────────────────── */
.outs{margin-top:clamp(40px,5vw,72px);display:grid;
  grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:clamp(12px,1.3vw,16px)}
.out{background:#FAF9F7;border-radius:var(--r-sm);padding:clamp(20px,2.2vw,28px)}
html[data-theme="dark"] .out{background:#1A1917}
.out .n{font-weight:500;font-size:clamp(24px,2.8vw,36px);letter-spacing:-.045em;color:var(--accent);line-height:1.05}
.out .c{margin-top:10px;font-size:13.5px;line-height:1.5;color:var(--muted)}

/* ── Chapters ──────────────────────────────────────────────────── */
.ch{padding-top:clamp(64px,9vw,120px)}
/* the file writes the section label as one line — "03 · Decision 1 of 3 ·
   Insurance status" — with no rule beneath the heading */
.ch-head{margin-bottom:clamp(20px,2.4vw,30px)}
.ch-head .lbl{display:block;font-weight:600;font-size:12px;letter-spacing:.08em;
  text-transform:uppercase;color:var(--faint);margin-bottom:clamp(10px,1.2vw,16px)}
.ch-head h2{font-size:clamp(24px,2.65vw,38px);font-weight:600;letter-spacing:-.03em;line-height:1.16}
.ch-body{display:grid;grid-template-columns:repeat(12,minmax(0,1fr));gap:var(--gap);align-items:start}
.prose{grid-column:1/8;min-width:0}
/* with nothing in the margin, the paragraph runs the full column, as in the file */
.ch-body.wide .prose{grid-column:1/-1}
.prose p{font-size:16.5px;line-height:1.68;color:var(--muted)}
.prose p+p{margin-top:1.05em}
.prose strong{color:var(--ink);font-weight:500}
.side{grid-column:9/-1;min-width:0}

/* process artefacts — the diagrams that carry a decision. They come from
   the project record and keep their own palette, so they are framed as
   documents rather than restyled to match the site. */
.art{margin:clamp(24px,2.8vw,36px) 0 0}
/* the brief presents every screen on a tinted panel; the exports already carry
   it, so the frame just needs to get out of the way */
/* no stroke: on a white page the export carries its own panel, and the border
   read as a divider between the image and its caption */
.art img{width:100%;height:auto;border-radius:var(--r);background:var(--raise)}
.art figcaption{font-weight:600;margin-top:11px;font-size:11px;letter-spacing:.05em;
  line-height:1.62;color:var(--faint)}
.art.wide{margin-top:clamp(30px,3.4vw,44px)}
/* a zoomed detail is shown at its own size, not stretched to the column */
.art.detail img{max-width:620px}

/* problem-side signals: the numbers the research turned up */
.signals{border-top:1px solid var(--line-2)}
.signal{padding:14px 0;border-bottom:1px solid var(--line-2)}
.signal .n{font-weight:500;font-size:clamp(19px,2vw,24px);letter-spacing:-.04em;color:var(--accent)}
.signal .c{margin-top:5px;font-size:13px;line-height:1.5;color:var(--muted)}

/* numbered findings */
.finds{margin-top:clamp(32px,4vw,52px);border-top:1px solid var(--line-2)}
/* a block that already ends on a rule shouldn't be followed by a second one */
.tbl + .finds,.lessons + .finds{border-top:0;margin-top:0}
.find{display:grid;grid-template-columns:auto 1fr;gap:0 clamp(16px,2.4vw,32px);
  padding:22px 0;border-bottom:1px solid var(--line-2)}
.find .n{font-weight:600;font-size:var(--t-label);letter-spacing:.12em;color:var(--accent);padding-top:.5em}
.find h3{font-size:17px;font-weight:600;letter-spacing:-.02em}
.find p{grid-column:2;margin-top:8px;font-size:14.5px;line-height:1.62;color:var(--muted);max-width:68ch}

/* method cards */
.methods{margin-top:clamp(30px,3.6vw,46px);display:grid;grid-template-columns:repeat(2,1fr);gap:1px;
  background:var(--line-2);border:1px solid var(--line-2);border-radius:var(--r);overflow:hidden}
.method{background:var(--bg);padding:clamp(20px,2.2vw,28px);transition:background-color .3s var(--ease)}
.method:hover{background:var(--surface)}
.method .k{font-weight:600;font-size:10.5px;letter-spacing:.15em;text-transform:uppercase;color:var(--accent)}
.method h3{font-size:16.5px;font-weight:600;letter-spacing:-.02em;margin-top:10px}
.method p{margin-top:9px;font-size:14px;line-height:1.6;color:var(--muted)}

/* quote */
.quote{margin-top:clamp(30px,3.6vw,48px);padding:clamp(24px,3vw,36px);border-radius:var(--r);
  background:var(--accent-soft);border:1px solid var(--line-2)}
.quote p{font-family:var(--display);font-style:italic;font-size:clamp(20px,2.4vw,28px);line-height:1.34;
  letter-spacing:-.015em;color:var(--ink);max-width:40ch}
.quote cite{font-weight:600;display:block;margin-top:16px;font-size:11px;letter-spacing:.12em;
  text-transform:uppercase;color:var(--faint);font-style:normal}

/* criteria */
.crit{list-style:none;counter-reset:c;border-top:1px solid var(--line-2)}
.crit li{counter-increment:c;position:relative;padding:16px 0 16px 42px;border-bottom:1px solid var(--line-2);
  font-size:15.5px;line-height:1.6;color:var(--ink-2)}
.crit li::before{font-weight:600;content:counter(c,decimal-leading-zero);position:absolute;left:0;top:18px;
  font-size:11px;letter-spacing:.1em;color:var(--accent)}

/* decisions */
.dec{padding:clamp(28px,3.2vw,42px) 0;border-bottom:1px solid var(--line-2)}
.dec:first-of-type{border-top:1px solid var(--line)}
/* The chapter head already draws a rule under itself, so a block that opens
   a chapter must not draw a second one below the heading's margin. */
.ch-head + .dec,.ch-head + .lessons{border-top:0}
.dec-grid{display:grid;grid-template-columns:repeat(12,minmax(0,1fr));gap:var(--gap);align-items:start}
.dec .k{font-weight:600;grid-column:1/4;font-size:10.5px;letter-spacing:.15em;text-transform:uppercase;color:var(--accent);padding-top:6px}
.dec .b{grid-column:4/-1;min-width:0}
.dec h3{font-size:clamp(19px,2.1vw,25px);font-weight:600;letter-spacing:-.028em;line-height:1.22;max-width:26ch}
.dec p{margin-top:12px;font-size:15.5px;line-height:1.65;color:var(--muted);max-width:66ch}

/* gallery */
.gal{margin-top:clamp(34px,4vw,54px);display:grid;grid-template-columns:repeat(4,1fr);gap:clamp(14px,1.8vw,24px) clamp(12px,1.6vw,20px);align-items:start}
.gal figure{margin:0}
/* Four to a row, so each one is a thumbnail: enough to recognise the screen,
   with the magnifier there for anyone who wants to read it. One fixed 3:2 box
   keeps the captions on a common baseline, and contain means nothing is cropped
   — these run from 0.46 (a phone screen) to 1.69 (a desktop table). */
.gal img{width:100%;aspect-ratio:3/2;object-fit:contain;padding:6px;
  border-radius:var(--r-sm);background:var(--raise);
  transition:background-color .3s var(--ease)}
.gal figure:hover img{background:var(--line-3)}
.gal figcaption{margin-top:10px;font-size:12.5px;line-height:1.55;color:var(--muted)}
.gal figcaption b{display:block;font-weight:500;color:var(--ink);margin-bottom:3px;font-size:13.5px;letter-spacing:-.01em}


/* zoom affordance + lightbox — built by js/system.js around every case-study
   screenshot, so the markup below stays plain <figure><img>. */
/* The screenshot itself is the control — no visible chrome, but a real button
   so it's reachable by keyboard and can take focus back when the lightbox closes. */
.zoomwrap{position:relative;display:block;line-height:0;width:100%;
  padding:0;border:0;background:none;cursor:zoom-in;text-align:inherit;font:inherit;color:inherit}
.zoomwrap:focus-visible{outline:2px solid var(--accent);outline-offset:4px;border-radius:var(--r-sm)}

.lb{position:fixed;inset:0;z-index:150;display:flex;flex-direction:column;align-items:center;
  justify-content:center;gap:16px;padding:clamp(18px,4vw,52px);
  background:rgba(8,9,12,.9);backdrop-filter:blur(7px);
  opacity:0;visibility:hidden;
  /* visibility flips instantly on open so the close button can take focus in the
     same tick; on close it waits for the fade */
  transition:opacity .3s var(--ease),visibility 0s linear .3s}
.lb.on{opacity:1;visibility:visible;transition:opacity .3s var(--ease),visibility 0s}
.lb-x:focus-visible{outline:2px solid #fff;outline-offset:3px}
.lb img{max-width:100%;max-height:80vh;object-fit:contain;border-radius:var(--r-sm);
  background:#fff;box-shadow:0 30px 90px rgba(0,0,0,.55);
  transform:scale(.975);transition:transform .32s var(--ease)}
.lb.on img{transform:scale(1)}
.lb-cap{text-align:center;color:#D7D9DE;font-size:14px;line-height:1.55;max-width:74ch}
.lb-cap b{display:block;color:#fff;font-weight:500;margin-bottom:3px}
.lb-x{position:absolute;top:clamp(14px,2vw,22px);right:clamp(14px,2vw,22px);
  width:40px;height:40px;border-radius:999px;display:grid;place-items:center;color:#fff;
  border:1px solid rgba(255,255,255,.3);transition:background-color .22s var(--ease)}
.lb-x:hover{background:rgba(255,255,255,.14)}
.lb-x svg{width:17px;height:17px}
@media (prefers-reduced-motion:reduce){.lb,.lb img{transition:none}.lb img{transform:none}}

/* ── Extended chapter blocks ───────────────────────────────────
   Three components the longer case studies need: a rules table, a column of
   outcome tiers, and the six-part anatomy of a decision. All built from the
   same hairline-grid vocabulary as .meta and .outs. */
/* The evidence table, as the file draws it: one tinted panel, column labels
   coloured by what they are (saw / changed / still unproven), and the source
   of each observation set under it rather than run into the sentence. */
.tbl{--tbl-line:#EBE7E2;--tbl-blue:#2E5A94;margin-top:clamp(34px,4vw,54px);
  background:#FAF9F7;border-radius:var(--r);overflow:hidden}
html[data-theme="dark"] .tbl{--tbl-line:rgba(255,255,255,.1);--tbl-blue:#8FB3E0;background:#15171B}
.tbl{--tbl-cols:repeat(3,minmax(0,1fr))}
.tbl.c3{--tbl-cols:minmax(0,440fr) minmax(0,360fr) minmax(0,352fr)}
.tbl.c2{--tbl-cols:minmax(0,.84fr) minmax(0,1fr)}
.tbl.c4{--tbl-cols:minmax(0,.8fr) repeat(3,minmax(0,1fr))}
.tbl.c5{--tbl-cols:minmax(0,1fr) minmax(0,1.1fr) minmax(0,.5fr) minmax(0,1fr) minmax(0,.5fr)}
.tbl .r{display:grid;grid-template-columns:var(--tbl-cols);
  gap:0 24px;padding:23px 24px;border-bottom:1px solid var(--tbl-line);align-items:start}
.tbl .r:last-child{border-bottom:0}
.tbl .r.hd{padding-top:16px;padding-bottom:16px}
.tbl .r.hd span{font-size:11px;font-weight:600;letter-spacing:.08em;text-transform:uppercase;
  font-family:var(--sans);line-height:1.5}
.tbl .r.hd span{color:var(--faint)}
/* the evidence table colours its labels by what they are */
.tbl.ev .r.hd span:nth-child(1){color:var(--good)}
.tbl.ev .r.hd span:nth-child(2){color:var(--tbl-blue)}
.tbl.ev .r.hd span:nth-child(3){color:var(--warn)}
.tbl .r b{font-size:15px;font-weight:600;letter-spacing:-.015em;color:var(--ink);line-height:1.45}
.tbl .r .src{display:block;margin-top:7px;font-size:12.5px;font-weight:400;
  letter-spacing:0;color:var(--faint)}
.tbl .r span{font-size:14.5px;line-height:1.55;color:var(--muted)}
.tnote{margin-top:clamp(16px,1.8vw,22px);font-size:14px;line-height:1.6;color:var(--muted)}
@media(max-width:760px){
  .tbl .r{grid-template-columns:minmax(0,1fr);gap:10px 0}
  .tbl .r.hd{display:none}
}

.tiers{margin-top:clamp(26px,3vw,38px);display:grid;grid-template-columns:repeat(3,minmax(0,1fr));
  gap:clamp(14px,1.6vw,20px);align-items:start}
.tier{background:var(--tint);border-radius:var(--r-sm);padding:clamp(20px,2.2vw,28px)}
.tier:first-child{background:var(--inverse)}
.tier h3{font-size:16px;font-weight:600;letter-spacing:-.022em;padding-bottom:14px;
  border-bottom:1px solid var(--tint-line)}
.tier:first-child h3{color:var(--bg);border-bottom-color:rgba(255,255,255,.16)}
.tier ul{list-style:none;display:flex;flex-direction:column}
.tier li{font-size:14px;line-height:1.5;color:var(--ink-2);padding:14px 0;
  border-bottom:1px solid var(--tint-line)}
.tier li:last-child{border-bottom:0;padding-bottom:0}
.tier:first-child li{color:rgba(255,255,255,.82);border-bottom-color:rgba(255,255,255,.12)}

/* a chapter can run prose → table → prose; the later ones need their own gap */
.ch-body:not(:first-child){margin-top:clamp(28px,3.2vw,42px)}
/* a decision statement followed by its own anatomy shouldn't be ruled off from it */
.dec:has(+ .dstory){border-bottom:0;padding-bottom:0}
/* The six-part decision, as drawn in the master brief: the decision itself is a
   black panel, the trade-off is flagged amber and the result green. */
.dstory{margin-top:clamp(22px,2.6vw,32px);display:grid;grid-template-columns:repeat(3,minmax(0,1fr));
  gap:1px;background:var(--line-2);border:1px solid var(--line-2);border-radius:var(--r);overflow:hidden}
.dcell{background:var(--bg);padding:clamp(18px,2.1vw,26px)}
.dcell h4{font-size:10px;letter-spacing:.15em;text-transform:uppercase;
  color:var(--faint);font-weight:400}
.dcell p{margin-top:10px;font-size:14.5px;line-height:1.55;color:var(--muted)}
.dcell.warn h4{color:var(--warn)}
.dcell.good h4{color:var(--good)}
.dcell.pick{background:var(--inverse)}
.dcell.pick h4{color:color-mix(in srgb,var(--bg) 72%,transparent)}
.dcell.pick p{color:var(--bg);font-weight:500}

/* ── Story blocks ──────────────────────────────────────────────
   Three formats that exist to break the page's rhythm: a full-width
   statement for a turn in the argument, a from→to list for things that
   moved, and the opening summary a scanner reads instead of the page. */
.stmt{margin:clamp(42px,5.4vw,76px) 0 clamp(36px,4.4vw,60px);
  font-size:clamp(23px,2.9vw,38px);line-height:1.22;letter-spacing:-.032em;
  font-weight:500;color:var(--ink);max-width:24ch;text-wrap:balance}
.stmt em{font-family:var(--display);font-style:italic;font-weight:400;color:var(--accent);letter-spacing:-.01em}

.shift{margin-top:clamp(26px,3vw,38px);display:grid;gap:1px;background:var(--line-2);
  border:1px solid var(--line-2);border-radius:var(--r);overflow:hidden}
.shift .row{background:var(--bg);display:grid;grid-template-columns:minmax(0,1fr) auto minmax(0,1fr);
  gap:clamp(14px,2vw,28px);align-items:center;padding:clamp(15px,1.8vw,21px) clamp(18px,2vw,24px)}
.shift .was{font-size:14.5px;line-height:1.5;color:var(--muted)}
.shift .arw{color:var(--line);font-size:15px}
.shift .now{font-size:14.5px;line-height:1.5;color:var(--ink);font-weight:500}
.shift .lbl{font-weight:600;background:var(--raise);padding:9px clamp(18px,2vw,24px);display:grid;
  grid-template-columns:minmax(0,1fr) auto minmax(0,1fr);gap:clamp(14px,2vw,28px);
  font-size:10px;letter-spacing:.15em;text-transform:uppercase;color:var(--faint)}
.shift .lbl span:nth-child(2){visibility:hidden}

/* the opening summary: everything a 30-second reader needs */
/* The 60-second version, as the file draws it: two tinted cards with a gap
   between them rather than a hairline grid, and labels set in the text face. */
.brief{margin-top:clamp(52px,6vw,86px)}
.brief > .k{font-size:13px;font-weight:600;letter-spacing:.1em;
  text-transform:uppercase;color:var(--muted);display:block;margin-bottom:clamp(20px,2.4vw,28px)}
.brief-grid{--tint:#FAF9F7;display:grid;grid-template-columns:repeat(2,minmax(0,1fr));
  gap:clamp(14px,1.6vw,22px)}
html[data-theme="dark"] .brief-grid{--tint:#15171B}
.brief-col{background:var(--tint);border-radius:var(--r);padding:clamp(24px,2.8vw,36px)}
.brief-col h3{font-size:12.5px;font-weight:600;letter-spacing:.09em;text-transform:uppercase;
  color:var(--muted);margin-bottom:clamp(18px,2vw,26px)}
.brief-col dl{display:grid;grid-template-columns:minmax(0,118px) minmax(0,1fr);
  gap:16px clamp(16px,2vw,28px);align-items:baseline}
.brief-col dt{font-size:14.5px;font-weight:600;letter-spacing:-.012em;color:var(--ink)}
.brief-col dd{font-size:14.5px;line-height:1.55;color:var(--ink-2)}
/* the impact card stacks: each label sits over its own line */
.brief-col.stack dl{grid-template-columns:minmax(0,1fr);gap:0}
.brief-col.stack dt{margin-top:22px}
.brief-col.stack dt:first-of-type{margin-top:0}
.brief-col.stack dd{margin-top:6px;color:var(--muted)}
.brief-note{margin-top:26px;font-size:13.5px;line-height:1.55;color:var(--faint)}
/* the three decisions, as the file draws them: black cards with a gap, a large
   muted number, and the point in white */
.picks-k{font-size:13px;font-weight:600;letter-spacing:.1em;text-transform:uppercase;
  color:var(--muted);display:block;margin:clamp(34px,4vw,52px) 0 clamp(16px,1.8vw,22px)}
.picks-h{font-size:clamp(22px,2.3vw,30px);font-weight:600;letter-spacing:-.03em;
  line-height:1.2;margin:clamp(8px,1vw,12px) 0 clamp(18px,2vw,26px)}
.picks{margin-top:clamp(26px,3vw,38px);display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:clamp(14px,1.6vw,22px)}
.pick-c{background:#1C1B1A;border-radius:var(--r);padding:clamp(22px,2.6vw,32px)}
html[data-theme="dark"] .pick-c{border:1px solid rgba(255,255,255,.1)}
.pick-c .n{display:block;font-size:clamp(24px,2.4vw,30px);font-weight:600;letter-spacing:-.03em;
  color:rgba(255,255,255,.46);font-family:inherit}
.pick-c h3,.pick-c h4{margin-top:clamp(18px,2vw,26px);font-size:17px;font-weight:600;letter-spacing:-.022em;
  line-height:1.3;color:#FFFFFF}
.pick-c p{margin-top:11px;font-size:14px;line-height:1.6;color:rgba(255,255,255,.64)}
@media(max-width:860px){.brief-grid{grid-template-columns:minmax(0,1fr)}}
@media(max-width:760px){.picks{grid-template-columns:minmax(0,1fr)}}

/* ── Art direction ─────────────────────────────────────────────
   Three devices that give the page gears: a composed hero where the screens
   step rather than line up, a tone on a chapter so a turning point reads
   darker, and a full-bleed image for the moments worth the whole width. */
.stage{margin-top:clamp(34px,4.4vw,58px);display:grid;
  grid-template-columns:repeat(4,minmax(0,1fr));align-items:start;
  gap:clamp(12px,2.5vw,31px);
  padding:clamp(24px,4vw,50px) clamp(20px,5.5vw,69px);
  background:#EDF2F9;border-radius:var(--r)}
html[data-theme="dark"] .stage{background:#161A24}
.stage figure{margin:0;min-width:0}
.stage img{width:100%;height:auto;display:block;border-radius:12px}
.stage figcaption{margin-top:16px;font-size:13.5px;line-height:1.5;color:var(--muted)}
@media(min-width:561px) and (max-width:900px){
  /* cap the track instead of dividing the width, or a two-up grid on a tablet
     draws the phones bigger than the file ever does */
  .stage{grid-template-columns:repeat(2,minmax(0,256px));justify-content:center;
    row-gap:clamp(26px,4vw,38px)}
}
@media(max-width:560px){
  /* four stacked phones cost ~2000px of scroll, so the row becomes swipeable
     and keeps the file's proportions. js/system.js adds the tab stop only
     while it really overflows. */
  .stage{display:flex;overflow-x:auto;scroll-snap-type:x mandatory;
    overscroll-behavior-x:contain;-webkit-overflow-scrolling:touch;
    gap:14px;padding:22px 16px;scrollbar-width:none}
  .stage::-webkit-scrollbar{display:none}
  .stage figure:nth-child(n){flex:0 0 68%;scroll-snap-align:center}
  .stage:focus-visible{outline:2px solid var(--accent);outline-offset:3px}
}

/* Section 07 as the file draws it: a row of tinted cards, three outcome
   cards with the delivered one inverted, and the two plans side by side. */
.cardrow,.plan,.tiers{--tint:#FAF9F7;--tint-blue:#EDF2F9;--tint-line:rgba(28,27,26,.1)}
html[data-theme="dark"] .cardrow,html[data-theme="dark"] .plan,html[data-theme="dark"] .tiers{
  --tint:#15171B;--tint-blue:#161A24;--tint-line:rgba(255,255,255,.1)}

.cardrow{margin-top:clamp(30px,3.6vw,46px);display:grid;
  grid-template-columns:repeat(4,minmax(0,1fr));gap:clamp(12px,1.3vw,16px)}
.crd{background:var(--tint);border-radius:var(--r-sm);padding:clamp(18px,1.8vw,24px)}
.crd .k{display:block;font-weight:600;font-size:10.5px;letter-spacing:.11em;
  text-transform:uppercase;color:var(--faint);margin-bottom:10px}
.crd h3{font-size:15px;font-weight:600;letter-spacing:-.02em;line-height:1.3}
.crd p{margin-top:10px;font-size:13.5px;line-height:1.55;color:var(--muted)}
.crd p.kv b{display:block;font-weight:600;font-size:11px;letter-spacing:.08em;
  text-transform:uppercase;color:var(--faint);margin-bottom:4px}

.plan.one{grid-template-columns:minmax(0,1fr)}
.plan{margin-top:clamp(26px,3vw,38px);display:grid;
  grid-template-columns:repeat(2,minmax(0,1fr));gap:clamp(14px,1.6vw,20px);align-items:start}
.pcard{background:var(--tint);border-radius:var(--r-sm);padding:clamp(22px,2.4vw,32px)}
.pcard.blue{background:var(--tint-blue)}
.pcard .k{font-weight:600;display:block;font-size:10.5px;letter-spacing:.14em;
  text-transform:uppercase;color:var(--faint);margin-bottom:20px}
.pcard.blue .k{color:var(--accent)}
.prow+.prow{margin-top:18px}
.pcard:not(.blue) .prow+.prow{border-top:1px solid var(--tint-line);padding-top:18px}
.prow b{display:block;font-size:14.5px;font-weight:600;letter-spacing:-.015em;color:var(--ink)}
.prow p{margin-top:6px;font-size:13.5px;line-height:1.6;color:var(--muted)}
.prow .how{margin-top:7px;font-size:12.5px;color:var(--faint)}
.pcard .note{margin-top:22px;font-size:13px;line-height:1.6;color:var(--faint)}

.sub{margin-top:clamp(40px,4.6vw,62px)}
.sub h3{font-size:clamp(19px,1.8vw,23px);font-weight:600;letter-spacing:-.025em}
.sub p{margin-top:10px;font-size:15px;line-height:1.62;color:var(--muted)}

@media(max-width:900px){.cardrow{grid-template-columns:repeat(2,minmax(0,1fr))}}
@media(max-width:620px){.cardrow,.plan{grid-template-columns:minmax(0,1fr)}}

/* Section rail: these pages run past 20,000px, so the sections get a named
   index in the left margin. Where it shows, the page is pushed right by the
   rail's width rather than the rail sitting over the text. */
.srail{display:none}
@media(min-width:1180px){
  :root{--rail:clamp(186px,13.5vw,228px)}
  body{padding-left:var(--rail)}
  /* the gutter gives way first, so the column keeps as much width as it can */
  .wrap,:root{--pad:clamp(20px,2.6vw,48px)}
  .srail{display:block;position:fixed;left:0;top:var(--nav-h);bottom:0;width:var(--rail);
    padding:clamp(22px,2.6vw,40px) 18px clamp(22px,2.6vw,40px) clamp(18px,1.9vw,30px);
    overflow-y:auto;overscroll-behavior:contain;z-index:40;
    display:flex;flex-direction:column;justify-content:center}
}
.srail ol{list-style:none}
.srail a{position:relative;display:grid;grid-template-columns:24px minmax(0,1fr);
  gap:0 10px;align-items:start;padding:7px 0 7px 10px;color:var(--muted);
  text-decoration:none;border-left:1.5px solid var(--line);
  transition:color .22s var(--ease),border-color .22s var(--ease)}
.srail .d{font-weight:600;font-size:11px;letter-spacing:.06em;color:var(--faint);
  padding-top:1px;transition:color .22s var(--ease)}
.srail .t{font-size:12.5px;line-height:1.35;text-wrap:balance}
.srail a:hover{color:var(--ink);border-left-color:var(--line-strong)}
.srail a[aria-current]{color:var(--ink);border-left-color:var(--ink);font-weight:600}
.srail a[aria-current] .d{color:var(--ink)}
.srail a:focus-visible{outline:2px solid var(--accent);outline-offset:2px;border-radius:3px}
@media (prefers-reduced-motion:reduce){.srail a,.srail .d{transition:none}}
@media print{.srail{display:none}body{padding-left:0}}

/* The journey with the checks that pile up at one step: each step carries what
   was verified there, and most steps carry nothing. */
.steps{margin-top:clamp(26px,3vw,38px);display:grid;
  grid-template-columns:repeat(auto-fit,minmax(230px,1fr));gap:clamp(12px,1.3vw,16px)}
.stp{background:#FAF9F7;border-radius:var(--r-sm);padding:clamp(18px,1.8vw,24px)}
html[data-theme="dark"] .stp{background:#1A1917}
.stp.hot{background:var(--risk-fill);}
.stp .n{display:block;font-weight:600;font-size:10.5px;letter-spacing:.11em;
  text-transform:uppercase;color:var(--faint);margin-bottom:10px}
.stp.hot .n{color:var(--risk)}
.stp h3{font-size:15px;font-weight:600;letter-spacing:-.02em;line-height:1.3}
.stp p{margin-top:8px;font-size:13.5px;line-height:1.55;color:var(--muted)}
.stp ul{list-style:none;margin-top:14px;padding-top:12px;border-top:1px solid var(--line)}
.stp li{font-size:13px;line-height:1.5;color:var(--ink-2);padding:4px 0}
.stp .none{font-size:13px;color:var(--faint);margin-top:14px;padding-top:12px;
  border-top:1px solid var(--line)}

/* Which rule to fix first: each rule, the step where the patient found out,
   who can fix it, and where it is handled now. */
.rmap{margin-top:clamp(26px,3vw,38px);background:#FAF9F7;border-radius:var(--r);overflow:hidden}
html[data-theme="dark"] .rmap{background:#15171B}
.rmap .hd,.rmap .rrow{display:grid;
  grid-template-columns:28px minmax(0,1.5fr) minmax(0,1.5fr) minmax(0,1fr) minmax(0,1.3fr);
  gap:0 clamp(14px,1.6vw,24px);padding:20px 24px;align-items:start}
.rmap .hd{padding-bottom:12px}
.rmap .hd span{font-weight:600;font-size:11px;letter-spacing:.08em;text-transform:uppercase;color:var(--faint)}
.rmap .rrow{border-top:1px solid var(--line)}
.rmap .rank{font-weight:600;font-size:14px;color:var(--faint)}
.rmap b{display:block;font-size:14.5px;font-weight:600;letter-spacing:-.015em;color:var(--ink);line-height:1.35}
.rmap .cost{display:block;margin-top:6px;font-size:13px;line-height:1.5;color:var(--muted)}
.rmap .who{font-size:13.5px;line-height:1.5;color:var(--muted)}
.rmap .now{font-size:13.5px;line-height:1.5;color:var(--ink-2)}
.rmap .dec{display:block;margin-top:6px;font-weight:600;font-size:11px;letter-spacing:.08em;
  text-transform:uppercase;color:var(--accent)}
.track{display:flex;align-items:center;gap:0;margin-top:2px}
.track i{flex:1 1 0;position:relative;font-style:normal;font-size:11px;letter-spacing:.04em;
  text-transform:uppercase;color:var(--faint);padding-top:16px;text-align:center}
.track i::before{content:"";position:absolute;top:4px;left:50%;transform:translateX(-50%);
  width:7px;height:7px;border-radius:50%;background:var(--line-strong)}
.track i::after{content:"";position:absolute;top:7px;left:50%;width:100%;height:1px;background:var(--line)}
.track i:last-child::after{display:none}
.track i.on{color:var(--risk);font-weight:600}
.track i.on::before{width:13px;height:13px;top:1px;background:var(--risk);
  box-shadow:0 0 0 4px var(--risk-fill)}
@media(max-width:900px){
  .rmap .hd{display:none}
  .rmap .rrow{grid-template-columns:28px minmax(0,1fr);row-gap:14px}
  .rmap .rrow > :nth-child(n+3){grid-column:2}
}

/* A sequence: the file draws before/after, the scope argument and the delivery
   pipeline all as steps with an arrow between them. */
.flow{margin-top:clamp(26px,3vw,38px)}
.flow + .flow{margin-top:clamp(14px,1.6vw,20px)}
.flow .k{display:block;font-weight:600;font-size:11px;letter-spacing:.1em;text-transform:uppercase;
  color:var(--faint);margin-bottom:12px}
/* flex, not grid: with equal grid tracks the arrows took a full column each
   and squeezed every step into two-word lines */
.flow-row{display:flex;align-items:stretch}
.fstep{flex:1 1 0;background:#FAF9F7;border-radius:var(--r-sm);padding:clamp(16px,1.7vw,22px);min-width:0}
html[data-theme="dark"] .fstep{background:#1A1917}
.fstep b{display:block;font-size:14.5px;font-weight:600;letter-spacing:-.015em;color:var(--ink);line-height:1.35}
.fstep span{display:block;margin-top:6px;font-size:13px;line-height:1.5;color:var(--muted)}
.farr{flex:0 0 auto;display:flex;align-items:center;justify-content:center;padding:0 clamp(6px,.9vw,14px);
  color:var(--faint);font-size:15px;line-height:1}
@media(max-width:900px){
  .flow-row{flex-direction:column}
  .farr{padding:8px 0;transform:rotate(90deg)}
}

/* A strip of equal cells: the file uses it to show which days are still in the
   analyzer's memory and which have been overwritten. */
.strip{margin-top:clamp(26px,3vw,38px)}
.strip .k{display:block;font-weight:600;font-size:11px;letter-spacing:.1em;text-transform:uppercase;
  color:var(--faint);margin-bottom:12px}
.strip-row{display:grid;grid-template-columns:repeat(auto-fit,minmax(96px,1fr));gap:clamp(6px,.7vw,10px)}
.scell{background:#FAF9F7;border-radius:var(--r-sm);padding:clamp(12px,1.2vw,16px);min-width:0}
html[data-theme="dark"] .scell{background:#1A1917}
.scell b{display:block;font-size:13px;font-weight:600;letter-spacing:-.01em;color:var(--ink)}
.scell span{display:block;margin-top:5px;font-size:12px;line-height:1.4;color:var(--muted)}
.scell.gone{background:transparent;border:1px dashed var(--line)}
.scell.gone b,.scell.gone span{color:var(--faint)}
.strip .note{margin-top:14px;font-size:14px;line-height:1.6;color:var(--muted)}

/* The information architecture, before and after, each with the number the
   round produced. */
.ia{margin-top:clamp(26px,3vw,38px);display:grid;grid-template-columns:repeat(2,minmax(0,1fr));
  gap:clamp(14px,1.6vw,20px);align-items:start}
.ia-c{background:#FAF9F7;border-radius:var(--r);padding:clamp(22px,2.4vw,30px)}
html[data-theme="dark"] .ia-c{background:#1A1917}
.ia-c .k{display:block;font-weight:600;font-size:11px;letter-spacing:.1em;text-transform:uppercase;
  color:var(--faint);margin-bottom:16px}
.ia-c ul{list-style:none}
.ia-c li{font-size:14.5px;line-height:1.5;color:var(--ink-2);padding:7px 0}
.ia-c li.branch{padding-left:18px;color:var(--muted);font-size:14px}
.ia-c li.branch::before{content:"└";margin-right:9px;color:var(--faint)}
.ia-c .fig{margin-top:18px;padding-top:16px;border-top:1px solid var(--line)}
.ia-c .fig b{display:block;font-size:clamp(26px,2.8vw,34px);font-weight:600;letter-spacing:-.04em;
  line-height:1.05;color:var(--accent)}
.ia-c .fig span{display:block;margin-top:7px;font-size:13px;line-height:1.5;color:var(--muted)}
@media(max-width:760px){.ia{grid-template-columns:minmax(0,1fr)}}

/* images lift very slightly on hover, so they read as openable */
.zoomwrap img{transition:transform .32s var(--ease),box-shadow .32s var(--ease)}
.zoomwrap:hover img{transform:translateY(-2px)}
@media (prefers-reduced-motion:reduce){.zoomwrap img{transition:none}.zoomwrap:hover img{transform:none}}

/* caveat */
.caveat{margin-top:clamp(28px,3vw,40px);padding:20px 22px;border-left:2px solid var(--accent);
  background:var(--raise);border-radius:0 var(--r-sm) var(--r-sm) 0;font-size:15px;line-height:1.62;color:var(--ink-2)}
.caveat b{display:block;font-size:10px;letter-spacing:.16em;text-transform:uppercase;
  color:var(--faint);font-weight:400;margin-bottom:8px}

/* lessons */
.lessons{border-top:1px solid var(--line)}
.lesson{display:grid;grid-template-columns:minmax(0,4fr) minmax(0,6fr);gap:clamp(16px,3vw,44px);
  padding:24px 0;border-bottom:1px solid var(--line-2);align-items:start}
.lesson h3{font-size:17px;font-weight:600;letter-spacing:-.022em;line-height:1.3}
.lesson p{font-size:15px;line-height:1.64;color:var(--muted)}

/* next */
.nextnav{margin-top:clamp(64px,8vw,110px);padding:clamp(30px,3.6vw,46px) 0 clamp(50px,6vw,80px);
  border-top:1px solid var(--line);display:flex;flex-wrap:wrap;align-items:center;justify-content:space-between;gap:20px}
.nextnav .lbl{font-weight:600;font-size:var(--t-label);letter-spacing:.15em;text-transform:uppercase;color:var(--faint);display:block;margin-bottom:10px}
.nextnav a.big{font-size:clamp(24px,3.4vw,44px);font-weight:600;letter-spacing:-.038em;
  display:inline-flex;align-items:center;gap:14px;transition:color .25s var(--ease);
  white-space:nowrap}   /* hyphenated names like Flint-Link must not break across lines */
/* the arrow carries no intrinsic size, so as a flex item it shrinks to nothing
   once the name refuses to wrap — size it in em so it tracks the name. */
.nextnav a.big svg{flex:0 0 auto;width:.58em;height:.58em}
.nextnav a.big:hover{color:var(--accent)}
.nextnav .r{text-align:right}

@media(max-width:980px){
  .gal{grid-template-columns:repeat(3,1fr)}
  /* the brief cards and the decision row hold their shape longer than the
     gallery does — see the queries after this block */
  .tiers{grid-template-columns:repeat(2,minmax(0,1fr))}
  .tier:first-child{grid-column:span 2}
  @media(max-width:620px){.tiers{grid-template-columns:minmax(0,1fr)}
    .tier:first-child{grid-column:span 1}}
  .dstory{grid-template-columns:repeat(2,minmax(0,1fr))}
  /* the items go full-width here, but a 12-track grid still reserves 11 gaps —
     at 320px that's more gap than container. Collapse the grid itself. */
  .ch-body,.dec-grid{grid-template-columns:minmax(0,1fr)}
  .prose,.side,.dec .k,.dec .b{grid-column:1}
  .side{margin-top:8px}
  .meta{grid-template-columns:repeat(2,1fr)}
  .meta div{padding-left:24px}
  .meta div:nth-child(2n+1){padding-left:0}
  .outs{grid-template-columns:repeat(2,1fr)}
  .dec .k,.dec .b{grid-column:1/-1}
  .dec .k{padding-top:0;margin-bottom:12px}
}
@media(max-width:720px){
  .methods{grid-template-columns:1fr}
  .shift .row,.shift .lbl{grid-template-columns:1fr;gap:6px}
  .shift .arw,.shift .lbl{display:none}
  .shift .was{text-decoration:line-through;text-decoration-color:var(--line)}
  .brief-col dl{grid-template-columns:minmax(0,1fr);gap:0}
  .brief-col dt{margin-top:18px}
  .brief-col dt:first-of-type{margin-top:0}
  .brief-col dd{margin-top:5px}
  .tbl.c2 .r,.tbl.c3 .r{grid-template-columns:1fr;gap:4px}
  .tbl .r.hd{display:none}
  .tiers,.dstory{grid-template-columns:1fr}
  .gal{grid-template-columns:repeat(2,1fr)}
  .lesson{grid-template-columns:1fr;gap:8px}
  /* a wide dashboard screenshot cropped to a phone-width box is unreadable —
     letterbox it against the surface instead of cropping the interface away */
  .chero-fig img{object-fit:contain;background:var(--raise)}
  .chero-fig img{aspect-ratio:16/9}
  .nextnav{flex-direction:column;align-items:flex-start}
  .nextnav .r{text-align:left}
}
@media(max-width:480px){
  .gal{grid-template-columns:1fr}
  .gal img{aspect-ratio:auto;padding:0}
  .meta,.outs{grid-template-columns:1fr}
  .meta div{padding-left:0}
  .find{grid-template-columns:1fr}
  .find p{grid-column:1}
}
"""

# ── Content ────────────────────────────────────────────────────────────
CASES = [
{
 "slug":"teleconsult", "name":"myAster", "client":"Aster, UAE",
 "kick":["Healthcare","B2C mobile app","UAE","iOS and Android"],
 "title":'myAster: telling patients what their insurance allows <em>before they book</em>, not after',
 "sum":"Aster&rsquo;s patient app for the UAE: consults, medicines, packages and records on one account, for patients who often pay with insurance.",
 "meta":[("My role","Lead UI/UX Designer"),
         ("Team","Four designers, with Aster&rsquo;s product and business teams"),
         ("Duration","8 to 12 months"),
         ("Output","297 screens, 161 shared components")],
 "hero":("tc-hero-screens.jpg","Four myAster screens: find a doctor, one checkout for every service, the waiting room, and medicines"),
 "stage":[("tc-screen-1.jpg","Find a doctor"),
          ("tc-screen-2.jpg","One checkout for every service"),
          ("tc-screen-3.jpg","Wait for the call"),
          ("tc-screen-4.jpg","Medicines follow the visit")],
 "herocap":"Four screens from the approved file. Illustrative data; patient names are anonymised.",
 "gallery":[],
 "chapters":[

 {"slug":"problem","lbl":"01 &middot; The problem","title":"The problem",
  "h":"Insured patients picked a doctor and a time, then found out they couldn&rsquo;t book.",
  "blocks":[
   ("cardrow",[("Who","Patients booking for themselves or family, many paying with insurance."),
               ("What went wrong","Policy, ID, profile and referral rules appeared only after a time was picked. The fee came after booking."),
               ("Why it mattered","Six or more states ended in &ldquo;please contact our call center&rdquo;. Unverified policies risked rejected claims."),
               ("The UX challenge","Show a hospital&rsquo;s booking rules while the patient can still change their choice.")]),
   ("steps",[("Step 1","Find a doctor","Specialty, language, the next free slot.",[]),
             ("Step 2","Pick a time","The slot is held for 09:59 while they pay.",[]),
             ("Step 3 &middot; where it stopped","Checkout","Patient, payment method, then Book.",
              ["New policy still being verified","Emirates ID has expired",
               "Profile blocked or under review","Specialty needs a GP visit first"]),
             ("Step 4","After booking","Booked, but the price isn&rsquo;t known yet.",
              ["Fee created only after the insurer replies"])]),
   ("note","Several of those checks ended in &ldquo;Please contact our call center&rdquo;, with the doctor and the time already chosen. Nothing was checked while the patient was still choosing. Every rule waited until a time was picked, or later."),
  ]},

 {"slug":"understanding","lbl":"02 &middot; Understanding the problem","title":"Understanding the problem",
  "h":"What patients actually saw",
  "blocks":[
   ("prose",["Every rule reached the patient after the decision was made. These are the approved screens; the red outline marks the message."]),
   ("art",("tc-patients-saw.jpg","Four approved screens: a policy still pending, with the doctor and time already set and a note to switch to Self Pay; an expired Emirates ID, with a banner asking for an update before a video consult; a blocked profile, shown on the doctor page once a time is picked, pointing to the call center; and a GP referral needed, with an insurance popup asking for a referral letter.","nocap")),
   ("art",("tc-evidence.jpg","Six or more approved states end with some version of &ldquo;please contact our call center&rdquo;. Among them: a profile under review on a video booking, the same message on an in-person booking, and a technical failure offering Call Now as the only way forward.","nocap")),
  ]},

 {"slug":"research","lbl":"03 &middot; Research and insights","title":"Research and insights",
  "h":"The screens worked. The order didn&rsquo;t.",
  "blocks":[
   ("prose",["I ran the scope discussions with Aster&rsquo;s teams and audited every approved state. The rules lived with three teams, and no one could see the whole booking."]),
   ("cardrow",[("Teleconsult","GP hours, and which specialties need a GP first"),
               ("Insurance","Policy rules, and when a new policy is verified"),
               ("Registration","When a profile goes into review or gets blocked")]),
   ("note","I put every rule in one list, next to where the patient finds out. Each screen was fine. Each rule arrived too late."),
   ("cardrow",[("Scope discussions","Teleconsult, Insurance and Registration teams"),
               ("State audit","Every approved state, screen by screen"),
               ("Not available","Usability sessions, analytics, call-center logs")]),
   ("table",(["Evidence","Insight","Design decision"],
     [[("Five rules reached patients at checkout, or after booking.","Audit of approved states"),
       "Patients committed before the app knew whether they could book.",
       ("Check each rule where it can still change the choice.","Decision 1 and the rule map")],
      [("Six or more states ended in &ldquo;please contact our call center&rdquo;.","Same audit"),
       "The app treated a problem the patient could fix like one only staff could fix.",
       ("Route each blocker by who can fix it.","Decision 2")],
      [("The hospital system creates the fee only after the insurer replies.","Constraint from the scope discussions"),
       "The price can&rsquo;t be a condition for booking. It has to be a state.",
       ("Show Under Process, then send the fee as a notification.","The final experience")],
      [("Five service flows needed the same identity, insurance and checkout.","Project scope"),
       "Rules designed flow by flow would drift apart.",
       ("Design checkout once and let services add to it.","Decision 3")]],"ev")),
  ]},

 {"slug":"strategy","lbl":"04 &middot; UX strategy","title":"UX strategy",
  "h":"One principle, three decisions",
  "blocks":[
   ("caveat",("The principle","Check each rule at the first moment it can still change the patient&rsquo;s choice.")),
   ("picks",[("Insurance states you can read","Valid, Pending or Not covered, always as a word with a next step. Pending visits more than four hours away book normally; closer ones are steered to Self Pay."),
             ("A next step for every blocker","If the patient can fix a blocker, the app gives them the button. If only a person can, it says so and points to them."),
             ("One checkout pattern, shared by every service","The patient, the payment switch and the payment list sit in the same place in every service, so a rule designed once works everywhere.")]),
   ("sub",("Which rule to fix first","")),
   ("rulemap",(["","The rule","Where patients found out","Who can fix it","Where it&rsquo;s handled now"],
     [("A new policy isn&rsquo;t verified yet","Cost: a lost consult, or a claim that gets rejected","Checkout",
       "The insurer, on its own clock","Before Book, with a four-hour line","Decision 1"),
      ("The Emirates ID has expired","Cost: a phone call for something the patient could do","Checkout",
       "The patient, in the app","A banner with Update Now","Decision 2"),
      ("The profile is blocked or under review","Cost: a dead end with no next step","Checkout",
       "Hospital staff only","Says so, and names the call center","Decision 2"),
      ("The specialty needs a GP visit first","Cost: a doctor and a time chosen for nothing","Time",
       "The patient, by seeing a GP","Filters the doctor list","Section 06"),
      ("The fee doesn&rsquo;t exist yet","Cost: committing without knowing the price","After",
       "The hospital system","Under Process, then a fee notice","Still unresolved")])),
   ("note","Three rules are still checked at checkout, but now before Book and with a next step. One moved up to the doctor list. The fee still arrives after booking. Gender and age rules, like Ob/Gyn and Pediatrics under 12, already filtered the doctor list."),
  ]},

 {"slug":"insurance","lbl":"05 &middot; Design decision 1 of 3 &middot; Insurance status","title":"Insurance status","h":"Every insurance state says what happens next",
  "blocks":[
   ("prose",["A new policy can take hours for the insurer to verify, outside Aster. The risk depends on the clock: a visit three days out leaves time for a reply, a video call in the next hour doesn&rsquo;t. So the line sits at four hours, and every state gets a word, a color and a next step."]),
   ("sub",("Options I weighed","")),
   ("cardrow",[("Not chosen","Block every pending policy","Safe for claims, but a patient with a new policy couldn&rsquo;t book at all until the insurer replied, which can take hours."),
               ("Not chosen","Let every pending policy through","Simple and fast, but a video call in the next hour could leave Aster with a claim the insurer later rejects."),
               ("Chosen","Draw the line by time until the visit","More than four hours away, book now and the fee follows. Closer than that, steer to Self Pay. The cost: one more rule patients have to understand.")]),
   ("art",("tc-ins-flow.jpg","Four real insurance states from the approved file, as one decision. Every branch ends with something the patient can do.")),
   ("art",("tc-a11y.jpg","Reading status without color. Pending is a word and an icon, not just orange. That matters more than it looks: the orange measures 2.6:1 against its badge, well under the 4.5:1 small text needs, so the word is doing the work for anyone who can&rsquo;t tell the colors apart. I&rsquo;d still fix the color: #9A4A00 on the same badge measures 5.9:1.","nocap")),
  ]},

 {"slug":"blockers","lbl":"05 &middot; Design decision 2 of 3 &middot; Blockers","title":"Blockers","h":"Who can fix it decides what the screen offers",
  "blocks":[
   ("prose",["An expired ID, a blocked profile and a server failure all stopped a booking at the same point. One generic error would have sent patients to the phone for an ID they could fix in a minute."]),
   ("sub",("Options I weighed","")),
   ("cardrow",[("Not chosen","One error, one phone number","Easy to build and consistent, but it sends patients to the phone for an ID they could update themselves in a minute."),
               ("Not chosen","A retry or appeal on every blocker","Feels helpful, but a button that fails the same way twice, or an appeal nobody reads, is worse than an honest dead end."),
               ("Chosen","Route by who can fix it","The patient can: give them the button. Only staff can: say so and name the call center. The app failed: offer a call. Three patterns instead of one, so more states to design and QA.")]),
   ("art",("tc-blockers.jpg","Same point in the flow, three different answers &mdash; and no button that promises something the app can&rsquo;t deliver.")),
  ]},

 {"slug":"checkout","lbl":"05 &middot; Design decision 3 of 3 &middot; One checkout pattern","title":"One checkout pattern","h":"One checkout, so a rule only had to be designed once",
  "blocks":[
   ("prose",["Five service flows were about to start, each needing to know who the booking was for, how they&rsquo;d pay, and what to do when insurance said no. I designed checkout first, and the services built on it."]),
   ("sub",("Options I weighed","")),
   ("cardrow",[("Not chosen","Each service designs its own checkout","The fastest start, since every designer could work in parallel. Patients would have met the insurance rules several different ways."),
               ("Not chosen","One identical checkout, no exceptions","The most consistent, but packages really do need Pay at Clinic. Forcing them into a video-consult screen would have broken them."),
               ("Chosen","A shared core that services add to","Patient, payment switch and payment list stay fixed. A service can add an option but not replace the pattern. The price: checkout had to be designed before any service flow could finish.")]),
   ("art",("tc-shared.jpg","Not every service uses every block. Records don&rsquo;t need checkout, and the package checkout in the file has no insurance step. But no service builds its own version of one.","nocap")),
   ("art",("tc-checkout.jpg","Three decisions fixed in one place: name the patient first, one payment switch, and a list services add to rather than replace.")),
   ("art",("tc-status-lang.jpg","One status language, wherever it appears. The same parts every time: a tint, an icon, a plain word, and an action when the patient can take one. Someone who learns it on an insurance card can read it on their profile.","nocap")),
   
  ]},

 {"slug":"journey","lbl":"06 &middot; The final experience","title":"The final experience","h":"One booking, end to end",
  "blocks":[
   ("prose",["An insured patient booking a video consult, with every rule checked while they can still act on it."]),
   ("art",("tc-journey.jpg","Read along the bottom: by checkout there is nothing left to discover.")),
   ("sub",("After booking, the price arrives on its own",
           "The hospital system creates the fee only after the insurer replies. Checkout shows the co-pay as Under Process, and the rest happens in notifications. Patients still commit without knowing the amount, which is the part I&rsquo;m least happy with.")),
   ("art",("tc-notify.jpg","The cancellation at the end is what makes it safe to let someone book without a price &mdash; an unpaid booking doesn&rsquo;t hold a slot another patient could use.")),
   ("note","Notification copy is shown exactly as approved, including its placeholder doctor name."),
  ]},

 {"slug":"validation","lbl":"07 &middot; Validation","title":"Validation",
  "h":"What was checked, and what still needs proving",
  "blocks":[
   ("prose",["No usability testing was run on this project. Here is what was checked instead, and how I&rsquo;d test the rest."]),
   ("cardrow",[("Design review","One checkout state disabled Book and put the reason further up the screen. We kept Book enabled and put the error beside it. Not covered still disables Book, and I&rsquo;d bring it in line."),
               ("Accessibility","Book Appointment passes at 4.6:1 and 60px tall. The coverage text (3.4:1), Valid (4.1:1) and Self Pay (4.3:1) fall short. Pending is covered in Decision 1. Screen readers and text scaling can&rsquo;t be checked in a design file."),
               ("Build QA","I checked the build against the approved screens. The miss: 27 buttons reached handoff still labeled &ldquo;Primary Button&rdquo;. A shared component doesn&rsquo;t bring its label with it.")]),
   ("sub",("Still unproven, and how I&rsquo;d check","")),
   ("table",(["What I can&rsquo;t claim","How I&rsquo;d check it"],
     [["Whether this is where insured patients dropped.","A booking funnel split by payment type."],
      ["How often patients hit each blocker.","Call-center contact reasons."],
      ["Whether patients understand &ldquo;Under Process&rdquo;.","The moderated test."],
      ["Whether one checkout made new services faster.","Build times, which I don&rsquo;t have."]])),
   ("card",("Before launch &middot; moderated usability test",
     [("The question","Do patients understand Pending, Under Process and the blocker messages without help?"),
      ("Who","8 UAE residents with health insurance who&rsquo;ve booked a doctor online in the last six months. At least three booking for a family member, two with a recently added policy."),
      ("Why 8","It&rsquo;s one flow and one question. Five to eight people usually surface the comprehension problems worth fixing. I&rsquo;d fix those, then run a smaller second round."),
      ("Tasks","Book a video consult in the next hour with a pending policy. Book a check-up for a parent. Recover from an expired Emirates ID. Explain what Under Process means at checkout."),
      ("What counts as success","They finish without help and can say, in their own words, why they were sent to Self Pay. A Single Ease Question after each task shows which one felt hardest."),
      ("What would change the design","If several people can&rsquo;t explain the four-hour rule, the copy on that screen changes before anything else does.")])),
  ]},

 {"slug":"delivery","lbl":"08 &middot; Results and impact","title":"Results and impact","h":"What shipped, and how we&rsquo;d know it worked",
  "blocks":[
   ("prose",["There&rsquo;s no post-launch data, so delivery, design changes and expected outcomes are kept apart."]),
   ("tiers",[("Delivered",["297 final screens","Six services on one account","161 shared components","Approved for build, handed off and QA&rsquo;d"]),
             ("Changed in the design",["Rules checked before checkout","A next step for every blocker","One insurance pattern and one checkout","Price as a state, not a blocker"]),
             ("Expected for Aster",["Fewer bookings ending in a phone call","More consults finished in the app","More pharmacy and lab orders per consult","Faster builds for new services"])]),
   ("card",("After launch &middot; what I would measure",
     [("Insured bookings confirmed","Out of patients who picked a time with insurance on. The number I would hold the work to.","How: Booking funnel, split by payment type"),
      ("Call-center contacts per 100 bookings","Split by reason. Tests whether fixable blockers stopped reaching the phone.","How: Call-center contact tags"),
      ("Pending bookings that end in a rejected claim","Tests whether four hours is the right line.","How: Aster&rsquo;s claims data"),
      ("Bookings cancelled for an unpaid fee","Tests whether the fee notification and reminder are enough.","How: Booking status events")])),
   ("note","No baseline exists yet, so there are no targets. The first month after launch sets one."),
   ("sub",("What I owned, what I influenced, and what we did together","")),
   ("cardrow",[("I owned","The shared layer: identity, family profiles, insurance states and checkout. A review gate, so only APPROVED screens reached engineering. Screen names QA could test. Handoff and build QA."),
               ("I influenced","Where each rule is checked. Moving a check earlier meant Aster&rsquo;s systems had to answer sooner, so it was a joint decision, not a screen change. The four-hour line is a business rule as much as a design one, so it wasn&rsquo;t mine to set alone."),
               ("We delivered together","Six services, designed by a team of four and built by Aster&rsquo;s engineers. Insurers, the hospital system and the call center sat outside the app and outside my control.")]),
  ]},

 {"slug":"reflection","lbl":"09 &middot; Reflection","title":"Reflection","h":"Three things I&rsquo;d take from this project",
  "blocks":[
   ("cardrow",[("I&rsquo;d do it again","Building the shared parts first","The rest of the team was waiting to start five services. Settling identity, family profiles, insurance and checkout first meant they all built on one set of rules, not five versions of them."),
               ("Still unresolved","Fees that don&rsquo;t exist at booking","Under Process is honest, but patients still book without knowing what they&rsquo;ll pay. I&rsquo;d want checkout to show the most they could be charged, once the hospital system can give us that number."),
               ("What I&rsquo;d test next","Whether &ldquo;pending&rdquo; makes sense","I&rsquo;d ask eight insured patients to book a video consult in the next hour with a pending policy. If they can&rsquo;t say why they were sent to Self Pay, the four-hour line needs a better explanation, not just a better screen.")]),
   ("note","After handoff I walked the flow as one patient. Insurance still took six screens, because each had passed review on its own. I&rsquo;ve since sketched a three-screen version, made after the project with AI assistance. It&rsquo;s a proposal, not shipped work."),
   ("art",("tc-refine.jpg","Three screens doing what six did: coverage checked on the doctor page, checkout with the policy already chosen, and adding a policy by looking it up first.","nocap")),
   ("caveat",("The habit I&rsquo;d least like to lose","Every insurance screen in this project passed review on its own, and the flow was still six screens long. Now I walk the whole journey as one patient before I sign anything off. Of everything here, that&rsquo;s the habit I&rsquo;d least like to lose.")),
  ]},

 ]},
{
 "slug":"flintlink", "name":"Flint-Link", "client":"Flint Group",
 "kick":["B2B portal","Desktop and mobile web","Print and packaging","Flint Group"],
 "title":'Flint-Link: a customer portal that answers before anyone has to email',
 "sum":"Flint Group&rsquo;s portal for printers and packaging converters: orders, consignment stock, invoices, certificates and support in one place.",
 "meta":[("My role","Lead UI/UX Designer, agency side"),
         ("Client","Flint Group"),
         ("Platform","Desktop and mobile web"),
         ("Research","14 interviews, 2 site visits, 2 usability rounds"),
         ("Status","Launched, then maintenance releases")],
 "hero":("fl-hero.jpg","Flint-Link on desktop and on a phone: orders, consignment stock, invoices and support in one portal"),
 "herofull":True,
 "herocap":"",
 "gallery":[],
 "chapters":[

 {"slug":"problem","lbl":"01 &middot; The problem","title":"The problem",
  "h":"When a press waited on a certificate, the customer waited on an email.",
  "blocks":[
   ("cardrow",[("Who","Printers and packaging converters who order, stock and pay for ink."),
               ("What went wrong","Every certificate, order update, invoice and stock count went through an account manager."),
               ("Why it mattered","A compliance document took 24 to 48 hours. On one visit, production stopped 3 times in 2 hours."),
               ("The UX challenge","Let customers answer their own after-order questions, starting from the order they hold.")]),
   ("flow",("The loop",[("Needs a certificate","Or an order update, or an invoice copy"),
                        ("Emails the account manager","Then calls to chase it"),
                        ("Account manager searches","Internal systems and inboxes"),
                        ("Reply by email","A PDF or a status update"),
                        ("24 to 48 h","for one compliance document")])),
   ("note","Every one of those requests was account-manager time spent finding files instead of selling."),
  ]},

 {"slug":"understanding","lbl":"02 &middot; Understanding the existing experience","title":"Understanding the existing experience",
  "h":"Every friction point came after the order",
  "blocks":[
   ("prose",["We mapped the customer journey. All 11 friction points we found came after the order was placed."]),
   ("outs",[("11","friction points on the journey map. All of them after the order."),
            ("14 of 14","interviewed customers raised documents and status updates, unprompted"),
            ("20+","emails in a typical thread about one consignment"),
            ("3 in 2 h","production interruptions on one site visit, waiting for a certificate")]),
  ]},

 {"slug":"research","lbl":"03 &middot; Research and insights","title":"Research and insights",
  "h":"Research on the factory floor, not only in meeting rooms",
  "blocks":[
   ("prose",["Interviews told us what customers asked for. Site visits showed what happened when they didn&rsquo;t get it. Two usability rounds told us which structure worked."]),
   ("cardrow",[("14 interviews","Customers, after the order"),
               ("2 site visits","On the factory floor"),
               ("5 competitor portals","Reviewed before design"),
               ("Journey map","11 friction points"),
               ("3 co-design sessions","With customers"),
               ("2 usability rounds","Then acceptance testing")]),
   ("table",(["Evidence","Insight","Design decision"],
     [[("14 of 14 customers raised documents and status, unprompted.","Interviews"),
       "The real work starts after the order is placed.",
       ("Five self-serve jobs at the center of the portal.","The strategy")],
      [("Nobody found their last certificate in the library.","Usability, Round 1"),
       "Customers think in orders, not document types.",
       ("Start from the order.","Decision 01")],
      [("A typical thread about one consignment ran past 20 emails.","Interviews and journey map"),
       "Stock updates were one job, split across many messages.",
       ("One screen, one submit, a status per product.","Decision 02")],
      [("4 of 12 participants named support first, unprompted.","Testing feedback"),
       "A problem on the press can&rsquo;t wait for an email.",
       ("Chat answers plus tracked tickets.","Decision 03")],
      [("Large PDFs on slow, shared factory networks.","Engineering flow review"),
       "A download that sits at zero looks broken.",
       ("Three download states on every file.","Decision 04")]],"ev")),
  ]},

 {"slug":"strategy","lbl":"04 &middot; UX strategy","title":"UX strategy",
  "h":"One principle, four decisions",
  "blocks":[
   ("caveat",("The principle","Start from what the customer already holds: an order, a shipment, a batch.")),
   ("picks",[("Start from the order, not a document library",""),
             ("Put consignment stock on one screen",""),
             ("Argue support into scope",""),
             ("Make downloads look alive","")]),
   ("sub",("The journey we designed for","")),
   ("flow",("The portal",[("Needs a certificate","The same questions"),
                          ("Opens the order","Orders, stock, invoices, support"),
                          ("Requests or downloads it","By site, product and batch"),
                          ("Follows the status","Requests and tickets show progress"),
                          ("Self-serve","no account manager in the loop")])),
  ]},

 {"slug":"architecture","lbl":"05 &middot; Decision 1 of 4 &middot; Information architecture","title":"Information architecture",
  "h":"Start from the order, not a document library",
  "blocks":[
   ("prose",["The brief asked for a document library. In Round 1, nobody found their last certificate in it. Customers knew their order, so I rebuilt the structure around it."]),
   ("ia",[("Round 1 &middot; What the brief asked for",
           ["Documents",">Certificates of Analysis",">Safety Data Sheets",">Technical Data Sheets",">Find it by product code and batch"],
           "0%","found the certificate for their last delivery"),
          ("Round 2 &middot; Start from the order",
           ["Orders",">Order 0004779279",">Shipment 8003006002 &middot; View PDF, Download, Track",">Certificates of Analysis",">Request by site &rsaquo; product &rsaquo; batch"],
           "100%","found it in Round 2")]),
   ("art",("fl-order.jpg","The order screen, annotated: the status sits beside the product name, shipments are listed under the order, and each shipment carries its own documents.","nocap")),
   ("cardrow",[("Status on the order","The status sits beside the product name."),
               ("Shipments under the order","One order, several deliveries, each with its own row."),
               ("Documents where the delivery is","View PDF, Download and Track live on the shipment.")]),
   ("caveat",("What it cost","Three sprints of rework, late. The library stayed only for documents not tied to an order, like technical data sheets.")),
  ]},

 {"slug":"consignment","lbl":"05 &middot; Decision 2 of 4 &middot; Screen design","title":"Screen design",
  "h":"Put consignment stock on one screen, with one submit",
  "blocks":[
   ("prose",["Consignment stock is ink that sits at the customer&rsquo;s site until it&rsquo;s used. Keeping Flint&rsquo;s count current took a long email thread, so I put it on one screen with one submit."]),
   ("art",("fl-consign.jpg","The consignment screen, annotated: calculated stock beside the customer&rsquo;s usage, one switch for what is being entered, one submit for every product, deliveries in the same row, a status per product, and a full history.","nocap")),
   ("caveat",("Trade-off","It&rsquo;s a dense screen. The per-product status and the full history carry that weight, so the screen can show everything without anyone having to remember what they sent.")),
  ]},

 {"slug":"support","lbl":"05 &middot; Decision 3 of 4 &middot; Scope","title":"Scope",
  "h":"Support wasn&rsquo;t in the brief, so I made the case for it",
  "blocks":[
   ("prose",["Support stayed with account managers in the brief. In testing, 4 of 12 named it first, unprompted, so I wrote a business case for it."]),
   ("flow",("",[("What we heard","4 of 12 named support first, unprompted"),
                ("What I proposed","A business case for chat answers plus tracked tickets"),
                ("What we agreed","Technical Support Agent and Support Hub, in scope"),
                ("What it costs","More scope, late, and answers Flint&rsquo;s team must keep current")])),
   ("art",("fl-support.jpg","Ask the agent first, where common printing problems come first. Not solved? Raise a ticket and follow it to resolved.","nocap")),
   ("caveat",("Honest gap","The file doesn&rsquo;t show what stakeholders pushed back on. The cost I can speak to: Flint&rsquo;s team has to keep the answers current.")),
  ]},

 {"slug":"downloads","lbl":"05 &middot; Decision 4 of 4 &middot; Interaction states","title":"Interaction states",
  "h":"Make large downloads look alive on slow networks",
  "blocks":[
   ("prose",["Before build, the engineering lead flagged what I&rsquo;d missed: large PDFs on slow factory networks look stuck at zero. So every download got the same three states."]),
   ("art",("fl-download.jpg","Tap Download on any certificate, data sheet or invoice: State 1 downloading, with progress that keeps moving; State 2 downloaded, with the file name; State 3 failed, which says what went wrong and offers Try again, straight back to State 1.","nocap")),
   ("cardrow",[("Icon-only buttons need names","No visible label. Each needs a name, like &ldquo;Download certificate for batch 5055461&rdquo;."),
               ("The green is too light","White on #25B67C is 2.6:1. #17805A reaches 4.9:1."),
               ("Download states must be announced","Downloading, Downloaded and Failed go in a polite live region.")]),
   ("note","Measured with the WCAG formula from the file&rsquo;s colors. A design review, not a live audit."),
  ]},

 {"slug":"system","lbl":"06 &middot; The final experience","title":"The final experience",
  "h":"One portal, from the desk to the press",
  "blocks":[
   ("prose",["At the desk, the dashboard opens on what&rsquo;s open: invoices, orders and consignment. Next to the press, the same data arrives on a phone, with nothing removed."]),
   ("art",("fl-dash.jpg","The dashboard, annotated: open work first, with invoices and orders and their amounts; each row links straight to its detail; and every job is one level deep in the sidebar.","nocap")),
   ("art",("fl-tablecard.jpg","Desktop: an invoice is one wide row. Mobile: the same invoice as a card.","nocap")),
   ("art",("fl-phone.jpg","On a phone: the same fields in the same order as a card, the status as a word on a tag rather than color alone, and the two most-used actions, View Details and Download, within thumb reach.","nocap")),
  ]},

 {"slug":"validation","lbl":"07 &middot; Validation and iteration","title":"Validation and iteration",
  "h":"What testing changed, and what it still has to prove",
  "blocks":[
   ("prose",["Each round of review changed the design. These are the real changes."]),
   ("table",(["Design","Finding","Improvement","Result"],
     [["A document library, as briefed","Usability Round 1: nobody found the certificate for their last delivery.","Rebuilt the structure around the order.","Round 2: 100% found it."],
      ["Support left with account managers","Testing: 4 of 12 named support first, unprompted.","Technical Support Agent and Support Hub, argued in with a business case.","Signed off in acceptance testing."],
      ["Downloads with no visible state","Engineering review: large PDFs on slow, shared networks look stuck.","Three states: downloading, downloaded, failed with Try again.","After launch, the fix customers praised most."],
      ["One delivery to confirm per product","Real sites get several deliveries for one product.","Each delivery confirmed on its own.","Reworked in a maintenance release."]])),
   ("note","Row four is read from the file: the maintenance page reworks the delivery confirmation."),
   ("sub",("One delivery per product was the wrong model",
           "We assumed one delivery per product. Real sites get several. Later designs confirm each delivery on its own. Walking customers through a real delivery week on the site visits would have caught it.")),
   ("sub",("The status tags say the right words in colors that are too faint",
           "Every tag carries a word, so color is never the only signal. But none of them reach 4.5:1. This is the first thing I would fix.")),
   ("table",(["In the file","Where it appears","Contrast","Proposed","Contrast"],
     [["Not Submitted","Consignment rows","2.4:1","Not Submitted","4.9:1"],
      ["Open","Invoices","2.9:1","Open","5.2:1"],
      ["Closed","Invoices, and the same blue for Picked and Delivered","2.7:1","Closed","4.9:1"],
      ["Submitted","Consignment rows","3.0:1","Submitted","5.4:1"]])),
   ("sub",("Still unproven, and how I&rsquo;d check","")),
   ("table",(["What I can&rsquo;t claim","How I&rsquo;d check it"],
     [["Whether fewer requests reach account managers.","One month of tagged inboxes."],
      ["Whether the order-first structure holds with real accounts.","Time from order opened to PDF downloaded."],
      ["Whether the download states work on real factory networks.","Failed vs completed downloads, by site."],
      ["Whether the portal works on a phone, at the press.","Moderated test: 6 customers, 3 sites."]])),
  ]},

 {"slug":"results","lbl":"08 &middot; Results and impact","title":"Results and impact",
  "h":"What was signed off, and what nobody measured",
  "blocks":[
   ("prose",["Customers signed off all three success criteria in acceptance testing. That proves the portal does the jobs. Whether fewer emails reached account managers was never tracked."]),
   ("cardrow",[("Signed off","Documents without asking","Customers get a Certificate of Analysis or a Safety Data Sheet without contacting Flint."),
               ("Signed off","Orders and stock without emailing","Customers check orders, deliveries and consignment stock themselves."),
               ("Signed off","Support with a status","Customers raise a ticket and follow it to resolved inside the portal.")]),
   ("outs",[("0 &rarr; 100%","finding the certificate, usability Rounds 1 and 2"),
            ("3 of 4","pilot organizations stopped keeping their own invoice spreadsheets within 30 days"),
            ("Not tracked","document and status requests still reaching account managers after launch")]),
   ("sub",("Who did what","")),
   ("cardrow",[("I owned","The information architecture, screen and interaction design, the support business case, and flow reviews with engineering."),
               ("Flint Group owned","Business rules, data and sign-off. Account managers and support told us what customers actually ask for."),
               ("Engineering owned","The build and the integrations with Flint&rsquo;s systems. Their review is where the download states came from.")]),
   ("sub",("How I&rsquo;d measure it now",
           "The number I&rsquo;d hold it to: the share of document and status requests that never reach an account manager. Baseline: one month of account-manager inboxes before launch, tagged by request type. No targets until that baseline exists.")),
  ]},

 {"slug":"reflection","lbl":"09 &middot; Reflection","title":"Reflection",
  "h":"What I&rsquo;d keep, what&rsquo;s still hard, what I&rsquo;d change",
  "blocks":[
   ("cardrow",[("Keep","Start from what the customer already holds. The library tested at zero because customers don&rsquo;t think in document types."),
               ("Still hard","New accounts can wait 48+ hours for approval. I designed a waiting state; the wait itself wasn&rsquo;t solved."),
               ("Change","Set the after-launch number on day one. Ours was never tracked.")]),
   ("sub",("Where the next designs go: the first two days","")),
   ("art",("fl-next.jpg","Complete the profile while the account is being approved, and a waiting state that says how far approval has got, with a way to raise a request.","nocap")),
   ("note","Designs in the file, not shipped work."),
   ("prose",["The best idea in this portal came from a test that failed. Customers think in orders, not document types.",
             "Now I start every structure from what the customer holds, and ask for the after-launch number on day one."]),
  ]},

 ]},
{
 "slug":"pettrackr", "name":"PetTrackr", "client":"Universal Biosensors",
 "kick":["Pet health","Mobile app","iOS and Android","Universal Biosensors"],
 "title":'PetTrackr: diabetes care for one hand at 7am',
 "sum":"A companion app for Universal Biosensors&rsquo; PETRACKR&reg; glucose analyzer, for people caring for a diabetic cat or dog.",
 "meta":[("My role","Lead UI/UX Designer, the only designer"),
         ("Client","Universal Biosensors"),
         ("Platform","iOS and Android"),
         ("Research","10 interviews, a 14-day diary, 3 test rounds"),
         ("Output","100+ screens and a design system")],
 "hero":("pt-hero.jpg",""),
 "herofull":True,
 "herocap":"",
 "gallery":[],
 "chapters":[

 {"slug":"problem","lbl":"01 &middot; The problem","title":"The problem",
  "h":"Readings lived in three or four places, and the analyzer forgot them after a week.",
  "blocks":[
   ("cardrow",[("Who","Owners of diabetic cats and dogs, testing at home every morning and evening."),
               ("What went wrong","Readings went on paper, into notes or a spreadsheet, then got photographed for the vet."),
               ("Why it mattered","The analyzer keeps seven days. Miss a week of syncing and the readings a vet needs are gone."),
               ("The UX challenge","Make logging a one-hand, few-second job, and get every reading to the vet before it is lost.")]),
   ("flow",("Before",[("Reading at 7am","One hand on the meter, one on the pet"),
                      ("Written down somewhere","Paper, notes or a spreadsheet, in 3 or 4 places"),
                      ("Photographed","Pages gathered before the visit"),
                      ("Vet sees numbers","No trend, no context"),
                      ("30+ min","to prepare a vet visit")])),
  ]},

 {"slug":"understanding","lbl":"02 &middot; Understanding the existing experience","title":"Understanding the existing experience",
  "h":"Where the 7am routine broke down",
  "blocks":[
   ("prose",["We mapped the daily care routine end to end and found nine friction points."]),
   ("outs",[("30+ min","to prepare one vet visit from paper, notes and photos."),
            ("7 of 10","owners kept readings on paper, in phone notes or spreadsheets"),
            ("6 of 6","diary participants ignored generic phone alarms after week 1"),
            ("9","friction points across the daily care routine")]),
   ("strip",("The constraint we couldn&rsquo;t change: a seven-day memory",
     [("Day 1","Overwritten","gone"),("Day 2","Overwritten","gone"),
      ("Day 3","In memory"),("Day 4","In memory"),("Day 5","In memory"),
      ("Day 6","In memory"),("Day 7","In memory"),("Day 8","In memory"),("Day 9","In memory")],
     "Not synced for nine days: days 1 and 2 are gone, including readings a vet needs to set insulin doses.")),
  ]},

 {"slug":"research","lbl":"03 &middot; Research and insights","title":"Research and insights",
  "h":"Research in people&rsquo;s homes, at 7am",
  "blocks":[
   ("prose",["I started where the testing happens: in homes, before work. Then vets told us what the readings were for."]),
   ("cardrow",[("10 in-home interviews","Owners, at 7am"),
               ("14-day diary study","The real routine"),
               ("3 vet interviews","What readings are for"),
               ("4 competitor apps","Reviewed before design"),
               ("Journey map","9 friction points"),
               ("3 usability rounds","Rebuilt after Round 1")]),
   ("table",(["Evidence","Insight","Design decision"],
     [[("60% finished onboarding. 4 of 5 failed Bluetooth pairing.","Usability, Round 1"),
       "Setup stood between people and the reason they came.",
       ("A first reading before any setup.","Decision 1")],
      [("One hand on the meter, one on the pet.","Diary study"),
       "Logging competes with a restless pet.",
       ("Pre-fill everything, ask for one number.","Decision 2")],
      [("The analyzer keeps seven days, then overwrites.","Hardware constraint"),
       "Owners need to know if their data is current.",
       ("Last sync shown wherever it matters.","Decision 3")],
      [("Vets read trends against a target range.","Vet interviews"),
       "A number means nothing without the pet&rsquo;s range.",
       ("Zones from the pet&rsquo;s own range.","Decision 4")],
      [("6 of 6 ignored generic phone alarms after week 1.","Diary study"),
       "A generic alarm is easy to dismiss.",
       ("Reminders per pet, per task, by name.","Decision 5")],
      [("Most clinics don&rsquo;t use shared apps.","Vet interviews"),
       "The report has to fit how clinics already work.",
       ("A PDF, sent by email or messaging.","Decision 6")]],"ev")),
  ]},

 {"slug":"strategy","lbl":"04 &middot; UX strategy","title":"UX strategy",
  "h":"One principle, six decisions",
  "blocks":[
   ("caveat",("The principle","Fit every task into the 7am moment: one pet, one hand, a few seconds.")),
   ("picks",[("A first win before anything else",""),("One hand, under 30 seconds",""),
             ("Designing around a seven-day memory",""),("Colour zones, not numbers",""),
             ("Reminders that name the pet",""),("A PDF for the vet, the portal later","")]),
   ("sub",("The journey we designed for","")),
   ("flow",("After",[("Reading at 7am","Same meter, same moment"),
                     ("Synced or logged","From the analyzer, or under 30 seconds"),
                     ("Charted in zones","Low, in range or high at a glance"),
                     ("PDF for the vet","Shared by email or messaging"),
                     ("&lt; 1 min","to prepare a vet visit")])),
  ]},

 {"slug":"onboarding","lbl":"05 &middot; Decision 1 of 6 &middot; Onboarding","title":"Onboarding",
  "h":"A first win before anything else",
  "blocks":[
   ("prose",["Seven setup steps lost 40% of people in Round 1. I put one glucose reading first and moved setup after it."]),
   ("ia",[("Round 1 &middot; seven steps",
           ["Create account",">Pet profile",">Species",">Target range",">Insulin dose",">Bluetooth pairing",">Notifications"],
           "60%","finished in Round 1"),
          ("After the rebuild",
           ["Intro &mdash; 3 short screens, each with Skip",">First win &mdash; log one blood glucose reading",">Later &mdash; pet details, pairing and reminders, when needed"],
           "89%","finished after the rebuild")]),
   ("card",("The decision",
     [("Options","Shorter forms for every step &middot; let people skip everything &middot; one useful action first"),
      ("Decision","One reading first. Everything else after."),
      ("Trade-off","The app starts with less: no pet details, no pairing, no reminders until people come back for them."),
      ("Result","Onboarding completion went from 60% to 89%, above the 85% target set at kickoff.")])),
   ("art",("pt-d1.jpg","Intro 1 of 3. Skip is always there. Intro 2 of 3. The first win: one blood glucose reading.","nocap")),
  ]},

 {"slug":"logging","lbl":"05 &middot; Decision 2 of 6 &middot; Logging","title":"Logging",
  "h":"One hand, under 30 seconds",
  "blocks":[
   ("prose",["One hand on the meter, one on a restless pet. So logging is a confirmation, not a form: one number, everything else pre-filled."]),
   ("card",("The decision",
     [("Options","A full entry form &middot; a quick-add button &middot; a confirmation with smart defaults"),
      ("Decision","Pre-fill everything the app already knows. Ask for one number."),
      ("Trade-off","Food, stress or activity is optional, so some readings arrive without context."),
      ("Result","Logging a reading went from 3 to 5 minutes on paper to under 30 seconds.")])),
   ("art",("pt-d2.jpg","One number, one large field. Date and time already filled in. The selected pet is always visible. Every entry lands in that pet&rsquo;s logbook.","nocap")),
  ]},

 {"slug":"sync","lbl":"05 &middot; Decision 3 of 6 &middot; Sync","title":"Sync",
  "h":"Designing around a seven-day memory",
  "blocks":[
   ("prose",["The analyzer keeps seven days, and fully automatic sync didn&rsquo;t ship as planned. So I made sync visible everywhere it matters."]),
   ("card",("The decision",
     [("Options","Background sync &middot; sync on app open &middot; visible sync status with reconnect"),
      ("Decision","Show the last sync everywhere it matters, and make failures obvious."),
      ("Trade-off","Syncing is still something owners have to remember. Fully automatic sync didn&rsquo;t ship as planned."),
      ("Result","Owners always know whether their data is current, and what to do if it isn&rsquo;t.")])),
   ("art",("pt-d3.jpg","Each analyzer shows its last sync time. Do you have an analyzer? Pairing comes after the first win. No analyzer yet: how to connect one.","nocap")),
  ]},

 {"slug":"zones","lbl":"05 &middot; Decision 4 of 6 &middot; Data visualization","title":"Data visualization",
  "h":"Colour zones, not numbers",
  "blocks":[
   ("prose",["Nobody could tell whether 140 was good. Vets read glucose against a range, so the chart does too."]),
   ("card",("The decision",
     [("Options","A table of readings &middot; a line chart &middot; a chart with the pet&rsquo;s range as zones"),
      ("Decision","Zones from the pet&rsquo;s own target range, with meals and insulin on the same line."),
      ("Trade-off","The chart depends on the owner entering the pet&rsquo;s target range, so the pet profile asks for it."),
      ("Result","In testing, reading the chart went from 22 seconds to 7.")])),
   ("art",("pt-d4.jpg","Daily chart: low, in range and high at a glance. The pet&rsquo;s target range, from the vet, drives the zones. Weekly view: the same zones, with min, average and max.","nocap")),
  ]},

 {"slug":"reminders","lbl":"05 &middot; Decision 5 of 6 &middot; Reminders","title":"Reminders",
  "h":"Reminders that name the pet",
  "blocks":[
   ("prose",["Every diary participant who tried generic phone alarms dropped them within a week. So reminders name the pet and the task."]),
   ("card",("The decision",
     [("Options","Use the phone&rsquo;s alarms &middot; one daily reminder &middot; per-pet, per-task reminders"),
      ("Decision","Per pet, per task, with the pet&rsquo;s name and the task in every notification."),
      ("Trade-off","Reminders follow rules the owner sets. Adaptive reminders that learn the routine didn&rsquo;t ship."),
      ("Result","Owners with several pets get one clear schedule per animal.")])),
   ("art",("pt-d5.jpg","Today&rsquo;s reminders for the selected pet, with Mark as Done. Notifications name the pet and the task.","nocap")),
  ]},

 {"slug":"report","lbl":"05 &middot; Decision 6 of 6 &middot; Vet report","title":"Vet report",
  "h":"A PDF for the vet, and the portal waits",
  "blocks":[
   ("prose",["Universal Biosensors planned a vet portal. The vets I spoke to wanted a file, not another app. The PDF shipped first, and the portal moved to phase 2."]),
   ("cardrow",[("Universal Biosensors planned","A portal for every vet",""),
               ("We shipped first","A PDF in the vet&rsquo;s inbox",""),
               ("Vets wanted","A file, not another app",""),
               ("The trade-off","Vets can&rsquo;t see readings between visits","They see what the owner sends. The portal, which would have shown them everything, moved to phase 2."),
               ("The result","Vet-visit prep: 30+ minutes down to under 1 minute","No photos of paper, no manual entry: the report is built from the logbook.")]),
   ("art",("pt-d6.jpg","Pick a time frame. The start date follows from it. Shared by email, files or messaging.","nocap")),
  ]},

 {"slug":"final","lbl":"06 &middot; The final experience","title":"The final experience",
  "h":"One pet, one day, four screens",
  "blocks":[
   ("prose",["Every screen opens on the selected pet, so the right animal is always in view."]),
   ("art",("pt-final.jpg","Home: the selected pet&rsquo;s latest readings and today&rsquo;s reminders. Logbook: every entry, for every pet. Reminders, per pet and per task. A report for the vet, for any time frame.","nocap")),
  ]},

 {"slug":"validation","lbl":"07 &middot; Validation and iteration","title":"Validation and iteration",
  "h":"Three test rounds, and what each one changed",
  "blocks":[
   ("prose",["Every row below is a real change, from usability rounds, the diary study or client review."]),
   ("table",(["Design","Finding","Improvement","Result"],
     [["Seven-step onboarding","Round 1: 60% finished, and 4 of 5 failed pairing.","A first reading before setup. Pairing after, with three guidance screens.","89% finished after the rebuild."],
      ["Readings as a list of numbers","Owners couldn&rsquo;t tell whether 140 was good.","Zones from the pet&rsquo;s own target range.","Reading the chart: 22 s down to 7 s."],
      ["Generic phone alarms","Diary: 6 of 6 stopped using them after week 1.","Reminders per pet and per task, by name.","Shipped. Not measured on its own."],
      ["Client review rounds","Universal Biosensors&rsquo; comments came back as a numbered list.","Each change placed beside the screen it changed.","Every item checkable in one pass."]])),
   ("sub",("What we got wrong, or left too late","")),
   ("cardrow",[("Deferred","Reminders that don&rsquo;t learn","Adaptive reminders, which would follow each pet&rsquo;s real routine, were planned and didn&rsquo;t ship. Reminders are rule-based: the owner sets the time."),
               ("Not fixed","Three typefaces in one system","The design system carries Roboto, Montserrat and Gilroy. It grew as the screens did, and I never consolidated it before handoff.")]),
   ("sub",("How client review came back",
           "One item from a review round with Universal Biosensors, as it sits in the file.")),
   ("art",("pt-review.jpg","How client review came back. One item from a review round with Universal Biosensors, as it sits in the file. The numbered change: the client&rsquo;s comment, numbered, above the screen it applies to. The screen, with the change made: the updated screen sits under its comment, so every item could be checked in one pass.","nocap")),
   ("sub",("Still unproven, and how I&rsquo;d check","")),
   ("table",(["What I can&rsquo;t claim","How I&rsquo;d check it"],
     [["Whether owners keep logging.","7-day retention, the target with no number."],
      ["Whether visible sync saves readings.","Days between syncs, per analyzer."],
      ["Whether vets use the PDF.","Reports generated and shared, per pet."],
      ["Whether reminders get done.","Done vs scheduled, per task."]])),
  ]},

 {"slug":"results","lbl":"08 &middot; Results and impact","title":"Results and impact",
  "h":"Three of four targets met, and one not measured",
  "blocks":[
   ("prose",["Three of four kickoff targets were met in testing. Retention has no number yet."]),
   ("cardrow",[("Met","Onboarding completion &ge; 85%","89%, up from 60% in Round 1"),
               ("Met","Log a reading in under 60 s","Under 30 s, down from 3 to 5 min on paper"),
               ("Met","Vet reports with no manual entry","Under 1 min, down from 30+ min of photos"),
               ("Not measured","7-day retention above paper","No number yet")]),
   ("sub",("The number I&rsquo;d hold the next release to",
           "Owners still logging for each pet, 7 days after their first reading, compared with how long paper tracking lasted in the diary study.")),
   ("sub",("Who did what","")),
   ("cardrow",[("I designed","As the only designer, every design decision on the product was mine to make and defend.",
                "Research and testing &middot; Every screen, iOS and Android &middot; The design system &middot; Handoff and design QA"),
               ("I ran","The conversations that set what the app could and couldn&rsquo;t do.",
                "Design discussions with Universal Biosensors &middot; Scope for each release &middot; Interviews with three vets"),
               ("The team owned","What I worked with, but didn&rsquo;t own.",
                "Universal Biosensors: the analyzer, its limits and product sign-off &middot; The development team: the build, Bluetooth sync and the app stores &middot; Vets: what a useful report looks like")]),
   ("flow",("",[("Understand","10 in-home interviews, a 14-day diary study, 4 competitor apps and 3 vets."),
                ("Map the journey","Nine friction points across the daily care routine."),
                ("Design and test","Three usability rounds, five people each."),
                ("Rebuild","Onboarding rebuilt around a first win after Round 1."),
                ("Ship","100+ screens for iOS and Android, with handoff and design QA.")])),
  ]},

 {"slug":"reflection","lbl":"09 &middot; Reflection","title":"Reflection",
  "h":"Four things I do differently now",
  "blocks":[
   ("table",(["Then, on this project","Now"],
     [[("Give people a first win before asking for anything","Seven sensible setup steps lost 40% of people in Round 1."),
       "I find the one useful action and put it before setup."],
      [("Design for the moment, not the screen","The 7am diary entries changed more screens than any design review did."),
       "I test where and when the product is used, not only at a desk."],
      [("Specific beats generic","Generic phone alarms were ignored within a week."),
       "Every reminder and notification says who it&rsquo;s for and what&rsquo;s due."],
      [("Agree how to measure retention before launch","Retention was the one kickoff target with no number at the end."),
       "I agree the retention event with engineering before design starts."]])),
   ("sub",("Where the next designs go: log before you sign up","")),
   ("art",("pt-next.jpg","Start as a guest: just a country, then log. Sign up later, and the app finds the guest data. It merges the guest data into the new account, and shows progress while it syncs.","nocap")),
   ("note","Designs in the file, not shipped work."),
  ]},

 ]},
{
 "slug":"aip", "name":"Apex Insights", "client":"Apex Insights",
 "kick":["Case study","Healthcare operations","Desktop web and Power BI"],
 "title":'Every facility&rsquo;s numbers, and a nudge when one slips',
 "sum":"A group of skilled nursing facilities had Power BI reports for census, staffing, payroll, revenue cycle and finance, but no front door. Finding the right report meant knowing where it lived, and nothing told anyone when a number moved. I led the design of Apex Insights, the portal that wraps those reports.",
 "sum2":"This case study follows four decisions: one place for every action, a home that gives reports the room, reports and alerts that come to people, and one layout for every Power BI report. There&rsquo;s no usage data, so it ends with how I&rsquo;d measure it.",
 "meta":[("My role","Lead UI/UX Designer"),
         ("Users","Executives, facility administrators and directors of nursing"),
         ("Scope","Portal, alerts, subscriptions, admin, and the Power BI report layouts"),
         ("Process","Two wireframe rounds with the client (26 and 29 March), themes, final screens"),
         ("Status","Final screens and layouts approved. No usage data")],
 "hero":("ax-hero.jpg","Apex Insights: the portal home with module tiles, a Power BI report in the shared layout, and the alerts list"),
 "herofull":True,
 "herocap":"",
 "gallery":[],
 "brief":{
   "k":"If you only have a minute",
   "pickh":"Four decisions carry this project",
   "picks":[("One place for every action","Round 1 had portal buttons and Power BI controls side by side. Now every report has one action area."),
            ("Give the reports the room","Wider tiles and a sidebar that collapses, tried in the 29 March revision and kept."),
            ("Bring the numbers to people","Subscriptions for the routine, threshold alerts for the exceptions."),
            ("One layout for every report","Last refresh, filters, chips and drill-through in the same place, whoever built the report.")]},
 "chapters":[

 {"slug":"problem","lbl":"01 &middot; The problem","title":"The problem",
  "h":"The reports existed. Getting to the right one didn&rsquo;t.",
  "blocks":[
   ("prose",["Skilled nursing facilities run on a few numbers checked every morning: census, or how many beds are filled; staffing, measured in hours per patient day (HPPD); overtime and agency hours; payroll; and the revenue cycle. Executives look across every facility. Administrators and directors of nursing look at their own.",
             "Each of those numbers lived in its own Power BI report. To check one facility&rsquo;s staffing, someone had to know which report held it, open it, filter it, and often export it for whoever asked. A number that drifted on Monday could go unnoticed until someone looked again."]),
   ("flow",("Before",[("A number is needed","Today&rsquo;s staffing at one facility"),
                      ("Find the report","Know where it lives in Power BI"),
                      ("Filter and export","Then send it to whoever asked"),
                      ("Nobody is told","Until someone looks again")])),
   ("flow",("After",[("Open Apex Insights","Every module from one home"),
                     ("Same layout everywhere","Last refresh, filters, drill-through"),
                     ("Pinned to My Dashboard","Each person&rsquo;s own numbers"),
                     ("Alerts and schedules","When a line is crossed, or on time")])),
  ]},

 {"slug":"questions","lbl":"02 &middot; Questions before screens","title":"Questions before screens",
  "h":"The first review was mostly questions",
  "blocks":[
   ("prose",["The brief named features: alerts, file storage, dashboards, subscriptions. It didn&rsquo;t say what any of them were for. So I wrote my questions on the 26 March wireframes, and the client&rsquo;s answers set the scope. These are the questions as they sit in the file."]),
   ("table",(["The question","Why it mattered","What it became"],
     [["&ldquo;What is alerts? What kind of content comes under it?&rdquo;","Without an answer, alerts would be a bell with nothing in it.","Three levels, informational, warning and critical, each tied to a threshold."],
      ["&ldquo;What is file storage?&rdquo;","It sounded like a document folder nobody needs.","Where scheduled report runs land, with their status."],
      ["&ldquo;Why are there two action buttons? Can actions live with the Power BI frame?&rdquo;","The same action in two places means two behaviors to learn.","Decision 01: one place for every action."],
      ["&ldquo;Do we really need all actions when someone clicks a dashboard widget?&rdquo;","Widgets were turning into mini reports.","A widget opens its report. Actions stay on the report."],
      ["&ldquo;Will the dashboard tab have only one interactive dashboard?&rdquo;","One shared dashboard can&rsquo;t suit an executive and a director of nursing.","My Dashboard, built by each person from pinned charts."]])),
  ]},

 {"slug":"actions","lbl":"Decision 01 &middot; Interaction model","title":"Interaction model",
  "h":"One place for every action",
  "blocks":[
   ("prose",["In the first wireframes, a report had the portal&rsquo;s buttons and Power BI&rsquo;s own controls. Some actions appeared twice, with different buttons in different places. I asked the client why, in writing on the frame, and pushed for one place.",
             "In the final screens every report has the same corner: pin and full screen as icons, and everything else in one menu. Export, print, subscribe, create a subscription for other users, favorite, refresh, and, for people allowed to, edit and delete."]),
   ("ia",[("Round 1 &middot; Two sets",
           ["Portal",">Favorite",">Clone",">Rename",">Subscribe","Power BI",">Export",">Clone",">Rename",">Print"],
           "","The same action in two places means two behaviors to learn, and nobody knows which one is &ldquo;real&rdquo;."),
          ("Final &middot; One corner",
           ["Every report",">Pin",">Full screen",">⋮ Menu"],
           "","One corner, the same on every report. Widgets on a dashboard open their report; they don&rsquo;t carry their own actions.")]),
   ("note","Simplified from the Round 1 wireframes. Clone and rename are the documented duplicates."),
   ("art",("ax-actions.jpg","A report in the final layout, annotated: pin and full screen as icons, then one menu holding export, print, subscribe, favorite, refresh, and edit and delete for admins.","nocap")),
   ("cardrow",[("Pin and full screen","The two actions people use while reading stay visible as icons."),
               ("Get it out","Export and print, for the person who still has to send a file."),
               ("Subscribe","For yourself, or create a subscription for your team."),
               ("Admin only","Edit and delete sit at the bottom, apart from everything else.")]),
   ("caveat",("Trade-off","Some Power BI options stay hidden from everyday users. That was deliberate: the portal decides what a report can do, not the report.")),
  ]},

 {"slug":"layout","lbl":"Decision 02 &middot; Layout, across two rounds","title":"Layout, across two rounds",
  "h":"Give the reports the room",
  "blocks":[
   ("prose",["The first home was a dense grid with a fixed sidebar. Power BI tables need width, and a fixed sidebar takes it on every screen. In the 29 March revision I tried wide module tiles with the sidebar as an overlay. The final home keeps that idea as a collapsed icon rail that expands when needed."]),
   ("art",("ax-evolution.jpg","26 March, Round 1: a fixed sidebar with labels, and tiles that show dashboard and report counts. 29 March, Round 2: wider tiles, and the sidebar shrinks to icons; the report list also lost its last and next run columns. Final: a collapsed icon rail, color-coded module tiles, and Add Report for admins.","nocap")),
   ("caveat",("Trade-off","Navigation is one move away instead of always visible. For people who live in one module all day, that&rsquo;s a fair price for a report that fits on screen.")),
  ]},

 {"slug":"push","lbl":"Decision 03 &middot; Service design","title":"Service design",
  "h":"Bring the numbers to people",
  "blocks":[
   ("prose",["Most leaders don&rsquo;t want to open a portal to find out whether something is wrong. So the portal pushes. Subscriptions deliver a report on a schedule and can be paused. File storage keeps every run with its status. Alerts fire when a facility crosses a threshold.",
             "The routine goes on a schedule. Only the exceptions interrupt anyone."]),
   ("flow",("The routine",[("Data refresh","Census, staffing and payroll refresh overnight"),
                           ("Subscription","A report on a schedule, to one person or a team"),
                           ("File storage","Every run: in queue, in progress, completed or error")])),
   ("flow",("The exception",[("Threshold","Set per facility, like an HPPD target"),
                             ("Alert","Informational, warning or critical"),
                             ("The right leader","Same day, in the portal and by email")])),
   ("art",("ax-alerts.jpg","The alerts list, annotated: levels as tabs with a count each; each alert naming the facility, the number and the line it crossed; a flag per severity alongside an icon and words; and Mark all as read. Facility names and thresholds are sample data in the screens, not the client&rsquo;s real targets.","nocap")),
   ("art",("ax-subs.jpg","Subscriptions: last and next run, Paused when switched off. File storage: every run with its status, and an error that says why.","nocap")),
   ("caveat",("Trade-off","Thresholds have to be agreed per facility, or alerts turn into noise. The design gives them levels, but someone at the client has to own the numbers.")),
  ]},

 {"slug":"reports","lbl":"Decision 04 &middot; Report design system","title":"Report design system",
  "h":"One layout for every Power BI report",
  "blocks":[
   ("prose",["The reports were built by different people, in Power BI. I designed one layout for all of them, so that learning one report means you can read the rest. The same header, the same filters, the same chips, and drill-throughs that always have a way back."]),
   ("art",("ax-census.jpg","The census report in the shared layout, annotated: last refresh at the top, report tabs, filters as chips, headline numbers before any table, and rows that expand in place.","nocap")),
   ("cardrow",[("Last refresh","When the data was last updated, at the top of every report."),
               ("Report tabs","Dashboard or reports, then the pages of this report."),
               ("Filters as chips","Applied filters stay visible and clear in one click."),
               ("Headline numbers first","The few numbers that matter, before any table."),
               ("Rows that expand","Each facility opens to its detail in place.")]),
   ("art",("ax-drill.jpg","Drill-through, with a way back. Staffing breaks HPPD down by shift and position, the way a director of nursing thinks about a shift. The header stays the same, and Back returns to the summary with the filters kept.","nocap")),
   ("caveat",("Trade-off","Report builders give up some freedom in how a page looks. In return, a user who learns one report can read all of them.")),
  ]},

 {"slug":"system","lbl":"03 &middot; The system","title":"The system",
  "h":"Personal where it helps, governed where it matters",
  "blocks":[
   ("prose",["An executive and a director of nursing need different numbers on the same morning, so any chart can be pinned to My Dashboard, to an existing dashboard or a new one. Administrators decide whether reports and interactive dashboards can be pinned at all, how long a session lasts, and who can see each report."]),
   ("art",("ax-pin.jpg","Pin any chart to an existing or a new dashboard; My Dashboard holds each person&rsquo;s own charts and can be set as their default; and admins decide what can be pinned at all.","nocap")),
   ("sub",("Accessibility: what I&rsquo;d fix before build",
           "Measured from the colors in the file with the WCAG contrast formula. A design review, not an audit of a built product.")),
   ("table",(["In the file","Where it appears","Contrast","Proposed","Contrast"],
     [["370","Over-budget values in staffing tables. Red is the only signal, so it also needs a sign or icon","4.2:1","&#9650; 370","5.5:1"],
      ["Completed","File storage status","3.8:1","Completed","5.2:1"],
      ["In Queue","File storage status","4.1:1","In Queue","5.2:1"],
      ["Today, 8:12 AM","Alert timestamps on unread rows","3.5:1","Today, 8:12 AM","4.9:1"]])),
  ]},

 {"slug":"leading","lbl":"04 &middot; Leading the work","title":"Leading the work",
  "h":"Decisions made in the file, not in someone&rsquo;s memory of a meeting",
  "blocks":[
   ("prose",["Every round went to the client as wireframes with my questions written on them. The answers, and the changes they caused, stayed next to the screens. The client&rsquo;s BI team owned the data models and the logic inside each report. Engineering owned the portal build, sign-on and the Power BI embedding. Facility leaders told us which numbers they check, and when."]),
   ("flow",("",[("Questions","What alerts, file storage and dashboards are for"),
                ("Round 1 &middot; 26 March","Wireframes with questions on the frames"),
                ("Round 2 &middot; 29 March","Wider tiles, fewer columns"),
                ("Themes","Visual themes for sign-off"),
                ("Final screens","Portal flows, admin and settings"),
                ("Reports and system","Power BI layouts and shared components")])),
   ("cardrow",[("Ask what a feature is for","Alerts and file storage were names in a brief until I asked. The answers set the scope."),
               ("One home for each action","I map every action to one place before laying out a screen."),
               ("Design the reports, not only the portal","The portal is only as clear as the reports inside it, so the Power BI layouts got the same system.")]),
  ]},

 {"slug":"results","lbl":"05 &middot; How I&rsquo;d know it works","title":"How I&rsquo;d know it works",
  "h":"Approved, and not yet measured",
  "blocks":[
   ("prose",["The final screens and report layouts were approved in the file. I don&rsquo;t have usage data, so I won&rsquo;t claim a result. This is what I&rsquo;d hold the portal to, and how I&rsquo;d test it before launch."]),
   ("sub",("The number I&rsquo;d hold it to",
           "Staffing alerts acted on the same day. A number noticed on Friday is a week of overtime or short shifts. No target until there&rsquo;s a first month of data.")),
   ("table",(["Metric","What it tells us","How"],
     [["Time to find a report","Whether one home and one layout make reports easy to reach","Search or home to report open"],
      ["Alerts read vs ignored, by level","Whether thresholds are tuned or turning into noise","Read, flagged and ignored per level"],
      ["Active vs paused subscriptions","Whether scheduled reports are still wanted","Running vs paused, per report"],
      ["Report runs that fail","Whether file storage is a place to trust","Error vs completed in file storage"]])),
   ("card",("Proposed, not run &middot; a test I&rsquo;d run before launch: one morning, three roles",
     [("Who","6 people: 2 executives, 2 facility administrators and 2 directors of nursing. Two per role shows whether the same screens work for different jobs. It isn&rsquo;t enough for percentages, so I&rsquo;d report what broke."),
      ("Tasks","1. Find yesterday&rsquo;s HPPD for one facility. 2. Act on a critical staffing alert. 3. Subscribe your team to the weekly census. 4. Pin one chart to your own dashboard."),
      ("Success, and what would change","Done without help, and the person can say where the number came from and when it was refreshed. If people miss alerts, levels move higher on home.")])),
  ]},

 {"slug":"reflection","lbl":"06 &middot; Looking back","title":"Looking back",
  "h":"What I&rsquo;d keep, what slipped, what I&rsquo;d change",
  "blocks":[
   ("cardrow",[("Keep","Questions on the frames before any visual design. The client&rsquo;s answers set the scope, and they&rsquo;re still in the file."),
               ("Slipped","Placeholder copy and typos reached approved screens: lorem ipsum in report descriptions, &ldquo;Exceutive&rdquo; on home, &ldquo;Unable to Complie&rdquo; in file storage, and &ldquo;Agnecy&rdquo;, &ldquo;Buget&rdquo;, &ldquo;Deparmental&rdquo; and &ldquo;Veiw&rdquo; in Power BI layouts."),
               ("Change","Agree the one number to track in the same meeting as sign-off. The screens were approved with no way to see if they worked.")]),
   ("sub",("Where the next designs go: one sign-in for both portals",
           "The client runs a second portal for day-to-day management. The next design in the file joins the two behind one sign-in, so a leader moves from a number to an action without logging in twice. The weekly staffing module, with drill-throughs for HPPD, overtime, agency and spend, is already designed in the same layout.")),
   ("flow",("",[("Apex Insights","Dashboards, reports, alerts"),
                ("One sign-in","Single sign-on across both"),
                ("Management portal","Day-to-day operations")])),
   ("note","Designs in the file, not shipped work."),
   ("prose",["The most useful thing I drew on this project was a question mark.",
             "Asking what alerts and file storage were for shaped more of the portal than any screen did. Now my first review is always questions, and the last one ends with the number we&rsquo;ll track."]),
  ]},

 ]},
]



# ── Template ───────────────────────────────────────────────────────────
ARROW = ('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" '
         'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M5 12h14M13 6l6 6-6 6"/></svg>')

NAV = """<header class="nav" id="nav">
  <div class="nav-in">
    <a class="brand" href="index.html" aria-label="Deep Vyas — home"><img class="mark" src="d-logo.svg" alt="" width="28" height="28"> Deep Vyas</a>
    <nav class="nav-links" aria-label="Sections">
      <a href="index.html#work">Work</a>
      <a href="index.html#about">About</a>
      <a href="index.html#contact">Contact</a>
    </nav>
    <div class="nav-act">
      <button class="icon-btn" id="theme" aria-label="Switch colour theme">
        <svg class="diya" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><defs><linearGradient id="dvFlame" x1="12" y1="2.8" x2="12" y2="13.7" gradientUnits="userSpaceOnUse"><stop offset="0" stop-color="#FF5A12"/><stop offset=".45" stop-color="#FF9A15"/><stop offset="1" stop-color="#FFD948"/></linearGradient></defs><g class="flame"><path class="f-out" d="M12 2.8c2.7 3.4 4 5.1 4 6.9a4 4 0 0 1-8 0c0-1.8 1.3-3.5 4-6.9z" fill="url(#dvFlame)" stroke="none"/><path class="f-core" d="M12 7.2c1.3 1.7 1.9 2.5 1.9 3.3a1.9 1.9 0 0 1-3.8 0c0-.8.6-1.6 1.9-3.3z" fill="#FFF6D6" stroke="none"/></g><g class="smoke" stroke="#9AA0AC" stroke-width="1.25" fill="none" stroke-linecap="round"><path class="s1" d="M12 13.4c-1.7-1.7-1.7-3.2 0-4.6s1.7-2.9 0-4.6"/><path class="s2" d="M12 13.4c1.5-1.4 1.6-2.7.2-3.9"/></g><path d="M12 15.1v-1.1"/><path d="M20.4 15.1a8.4 4.6 0 0 1-16.8 0z"/></svg>
      </button>
      <a class="nav-cv" href="cv-deep-vyas-uiux.pdf" target="_blank" rel="noopener noreferrer">CV &nearr;</a>
    </div>
    <div class="prog" id="prog" aria-hidden="true"></div>
  </div>
</header>"""

def dim(name):
    """ width/height attributes read from the JPEG itself.

    Every case-study image is sized in CSS by width alone, so without the
    intrinsic ratio the browser reserves no height for a lazy image and the
    page jumps as you scroll. Read the SOF marker rather than trusting a
    hand-typed number, which is how the hero ended up claiming 1400x600 for a
    1400x786 file."""
    path = os.path.join(IMG_DIR, name)
    try:
        with open(path, "rb") as f:
            if f.read(2) != b"\xff\xd8":
                return ""
            while True:
                b = f.read(1)
                while b and b != b"\xff":
                    b = f.read(1)
                while b == b"\xff":
                    b = f.read(1)
                if not b:
                    return ""
                m = b[0]
                if m in (0xD8, 0x01) or 0xD0 <= m <= 0xD7:
                    continue
                ln = struct.unpack(">H", f.read(2))[0]
                if 0xC0 <= m <= 0xCF and m not in (0xC4, 0xC8, 0xCC):
                    f.read(1)
                    h, w = struct.unpack(">HH", f.read(4))
                    return ' width="%d" height="%d"' % (w, h)
                f.seek(ln - 2, 1)
    except OSError:
        return ""



def esc(t):
    """Plain-text escape for attributes and <title>.

    Captions are authored as HTML, so they already carry entities and the odd
    <strong>. Decoding and stripping first stops &mdash; turning into the
    literal text "&mdash;" inside an alt attribute."""
    return html.escape(html.unescape(re.sub(r"<[^>]+>", "", t)), quote=True)

def strip_tags(t):
    import re
    return re.sub(r"<[^>]+>", "", t)

def art(spec, wide=True):
    """A process artefact: the picture that carries the claim.

    An optional third element adds a class — "detail" shows a zoomed crop at
    its own size instead of stretching it across the column, and "nocap" is for
    an export that already carries its own heading and body text, where a
    caption would set the same words twice. The text stays in the alt."""
    if not spec:
        return ''
    f, cap = spec[0], spec[1]
    extra = spec[2] if len(spec) > 2 else ''
    bare = extra == 'nocap'
    cls = ('art wide rv' if wide else 'art rv') + (('' if bare else ' ' + extra) if extra else '')
    return (f'  <figure class="{cls}"><img src="img/{f}" alt="{esc(cap)}"{dim(f)} '
            f'loading="lazy" decoding="async">' +
            ('' if bare else f'<figcaption>{cap}</figcaption>') + '</figure>')


def blocks(items):
    """Render a chapter body from a list of (type, payload) blocks.

    Cases that need more than the standard six chapters declare a "chapters"
    list instead, and each chapter is built from these pieces."""
    out = []
    for kind, data in items:
        if kind == "prose":
            side = ""
            if isinstance(data, dict):
                paras, crit = data["p"], data.get("crit")
                if crit:
                    side = '<div class="side"><ol class="crit">' + ''.join(
                        f'<li>{x}</li>' for x in crit) + '</ol></div>'
            else:
                paras = data
            out.append('  <div class="ch-body rv' + ('' if side else ' wide') +
                       '"><div class="prose">' +
                       ''.join(f'<p>{x}</p>' for x in paras) + '</div>' + side + '</div>')
        elif kind == "art":
            out.append(art(data))
        elif kind == "finds":
            out.append('  <div class="finds rv">' + ''.join(
                f'<div class="find"><span class="n">{i+1:02d}</span><h3>{h}</h3>' +
                (f'<p>{b}</p>' if b else '') + '</div>'
                for i, (h, b) in enumerate(data)) + '</div>')
        elif kind == "methods":
            out.append('  <div class="methods rv">' + ''.join(
                f'<div class="method"><span class="k">{k}</span><h3>{h}</h3><p>{b}</p></div>'
                for k, h, b in data) + '</div>')
        elif kind == "table":
            head, rows = data[0], data[1]
            mod = data[2] if len(data) > 2 else ""   # "ev" colours the labels
            cls = f"c{len(head)}" + ((" " + mod) if mod else "")
            r = ['<div class="r hd">' + ''.join(f'<span>{h}</span>' for h in head) + '</div>']
            def cell(x, tag):
                if isinstance(x, tuple):
                    return f'<{tag}>{x[0]}<span class="src">{x[1]}</span></{tag}>'
                return f'<{tag}>{x}</{tag}>'
            for row in rows:
                r.append('<div class="r">' + cell(row[0], 'b') +
                         ''.join(cell(x, 'span') for x in row[1:]) + '</div>')
            out.append(f'  <div class="tbl {cls} rv">' + ''.join(r) + '</div>')
        elif kind == "steps":
            cells = []
            for lbl, title, sub, checks in data:
                hot = ' hot' if checks else ''
                body = (('<ul>' + ''.join(f'<li>{c}</li>' for c in checks) + '</ul>')
                        if checks else '<p class="none">Nothing checked yet</p>')
                cells.append(f'<div class="stp{hot}"><span class="n">{lbl}</span>'
                             f'<h3>{title}</h3><p>{sub}</p>{body}</div>')
            out.append('  <div class="steps rv">' + ''.join(cells) + '</div>')
        elif kind == "rulemap":
            head, rows = data
            STEPS = ("Find", "Time", "Checkout", "After")
            r = ['<div class="hd">' + ''.join(f'<span>{h}</span>' for h in head) + '</div>']
            for i, (rule, cost, found, who, now, dec) in enumerate(rows, 1):
                track = ''.join(
                    f'<i class="{"on" if st == found else ""}">{st}</i>' for st in STEPS)
                r.append(f'<div class="rrow"><span class="rank">{i}</span>'
                         f'<span><b>{rule}</b><span class="cost">{cost}</span></span>'
                         f'<span class="track">{track}</span>'
                         f'<span class="who">{who}</span>'
                         f'<span class="now">{now}<span class="dec">{dec}</span></span></div>')
            out.append('  <div class="rmap rv">' + ''.join(r) + '</div>')
        elif kind == "flow":
            label, steps = data
            row = ('<span class="farr" aria-hidden="true">&rarr;</span>').join(
                f'<div class="fstep"><b>{t}</b><span>{sub}</span></div>' for t, sub in steps)
            out.append('  <div class="flow rv">' +
                       (f'<span class="k">{label}</span>' if label else '') +
                       f'<div class="flow-row">{row}</div></div>')
        elif kind == "strip":
            label, cells, note = data
            row = ''.join(
                f'<div class="scell{" gone" if len(c) > 2 else ""}"><b>{c[0]}</b>'
                f'<span>{c[1]}</span></div>' for c in cells)
            out.append('  <div class="strip rv">' +
                       (f'<span class="k">{label}</span>' if label else '') +
                       f'<div class="strip-row">{row}</div>' +
                       (f'<p class="note">{note}</p>' if note else '') + '</div>')
        elif kind == "ia":
            cols = ''
            for label, lines, fig, figcap in data:
                li = ''.join(
                    f'<li class="branch">{x[1:]}</li>' if x.startswith('>') else f'<li>{x}</li>'
                    for x in lines)
                cols += (f'<div class="ia-c"><span class="k">{label}</span><ul>{li}</ul>'
                         '<div class="fig">' +
                         (f'<b>{fig}</b>' if fig else '') +
                         f'<span>{figcap}</span></div></div>')
            out.append(f'  <div class="ia rv">{cols}</div>')
        elif kind == "picks":
            out.append('  <div class="picks rv">' + ''.join(
                f'<div class="pick-c"><span class="n">{i+1:02d}</span><h3>{h}</h3>' +
                (f'<p>{t}</p>' if t else '') + '</div>'
                for i, (h, t) in enumerate(data)) + '</div>')
        elif kind == "cardrow":
            cards = []
            for item in data:
                k, h, b = item if len(item) == 3 else ("", item[0], item[1])
                body = (''.join(f'<p class="kv"><b>{lbl}</b>{txt}</p>' for lbl, txt in b)
                        if isinstance(b, (list, tuple)) else (f'<p>{b}</p>' if b else ''))
                cards.append(f'<div class="crd">' +
                             (f'<span class="k">{k}</span>' if k else '') +
                             f'<h3>{h}</h3>{body}</div>')
            out.append('  <div class="cardrow rv">' + ''.join(cards) + '</div>')
        elif kind == "note":
            out.append(f'  <p class="tnote rv">{data}</p>')
        elif kind == "sub":
            h, b = (data, "") if isinstance(data, str) else data
            out.append(f'  <div class="sub rv"><h3>{h}</h3>' +
                       (f'<p>{b}</p>' if b else '') + '</div>')
        elif kind == "card":
            title, rows = data
            body = ''.join(
                f'<div class="prow"><b>{row[0]}</b><p>{row[1]}</p>' +
                (f'<p class="how">{row[2]}</p>' if len(row) > 2 else '') + '</div>'
                for row in rows)
            out.append('  <div class="plan rv one">'
                       f'<div class="pcard blue"><span class="k">{title}</span>{body}</div></div>')
        elif kind == "plan":
            (bt, brows), (at, arows, note) = data
            b = ''.join(f'<div class="prow"><b>{k}</b><p>{v}</p></div>' for k, v in brows)
            a = ''.join(f'<div class="prow"><b>{k}</b><p>{v}</p><p class="how">{how}</p></div>'
                        for k, v, how in arows)
            out.append('  <div class="plan rv">'
                       f'<div class="pcard blue"><span class="k">{bt}</span>{b}</div>'
                       f'<div class="pcard"><span class="k">{at}</span>{a}'
                       f'<p class="note">{note}</p></div></div>')
        elif kind == "tiers":
            out.append('  <div class="tiers rv">' + ''.join(
                f'<div class="tier"><h3>{h}</h3><ul>' + ''.join(f'<li>{x}</li>' for x in li) +
                '</ul></div>' for h, li in data) + '</div>')
        elif kind == "dstory":
            # the file's fixed order: challenge, options, trade-off / decision,
            # reasoning, result — with the trade-off, decision and result marked
            MARK = {2: " warn", 3: " pick", 5: " good"}
            cells = [f'<div class="dcell{MARK.get(i, "")}"><h4>{lbl}</h4><p>{body}</p></div>'
                     for i, (lbl, body) in enumerate(data)]
            out.append('  <div class="dstory rv">' + ''.join(cells) + '</div>')
        elif kind == "statement":
            out.append(f'  <p class="stmt rv">{data}</p>')
        elif kind == "shift":
            head, rows = data
            r = ['<div class="lbl"><span>%s</span><span>→</span><span>%s</span></div>' % (head[0], head[1])]
            for was, now in rows:
                r.append(f'<div class="row"><span class="was">{was}</span>'
                         f'<span class="arw">&rarr;</span><span class="now">{now}</span></div>')
            out.append('  <div class="shift rv">' + ''.join(r) + '</div>')
        elif kind == "outs":
            out.append('  <div class="outs rv" style="margin-top:clamp(30px,3.6vw,46px)">' + ''.join(
                f'<div class="out"><p class="n">{n}</p><p class="c">{cap}</p></div>'
                for n, cap in data) + '</div>')
        elif kind == "quote":
            q, cite = data
            out.append(f'  <blockquote class="quote rv"><p>&ldquo;{q}&rdquo;</p><cite>{cite}</cite></blockquote>')
        elif kind == "caveat":
            lbl, body = data
            out.append(f'  <p class="caveat rv"><b>{lbl}</b>{body}</p>')
        elif kind == "lessons":
            out.append('  <div class="lessons rv">' + ''.join(
                f'<div class="lesson"><h3>{h}</h3><p>{b}</p></div>' for h, b in data) + '</div>')
        elif kind == "dec":
            k, h = data[0], data[1]
            b = f'<p>{data[2]}</p>' if len(data) > 2 and data[2] else ''
            out.append(f'  <article class="dec rv"><div class="dec-grid"><span class="k">{k}</span>'
                       f'<div class="b"><h3>{h}</h3>{b}</div></div></article>')
        elif kind == "gallery":
            out.append('  <div class="gal rv">' + ''.join(
                f'<figure><img src="img/{img}" alt="{esc(alt)}"{dim(img)} loading="lazy" decoding="async">'
                f'<figcaption><b>{t}</b>{cap}</figcaption></figure>' for img, alt, t, cap in data) + '</div>')
        else:
            raise ValueError("unknown block type: " + kind)
    return "\n".join(out)


def chapter(idx, title, heading, inner, tone="", lbl=None):
    cls = "ch wrap" + (" " + tone if tone else "")
    label = lbl if lbl else f"{idx[0]} &middot; {title}"
    return (f'<section class="{cls}" id="{idx[1]}">\n'
            f'  <div class="ch-head rv">'
            f'<span class="lbl">{label}</span>'
            f'<h2>{heading}</h2></div>\n'
            f'{inner}\n</section>')

def tail(c, prev, nxt):
    """Everything after the last chapter — shared by both chapter paths."""
    return "\n".join([
        '<nav class="nextnav wrap" aria-label="More work">',
        f'  <div><span class="lbl">Previous</span><a class="big" href="{prev["slug"]}.html">{prev["name"]}</a></div>',
        f'  <div class="r"><span class="lbl">Next case study</span>'
        f'<a class="big" href="{nxt["slug"]}.html">{nxt["name"]} {ARROW}</a></div>',
        '</nav>',
        '</main>',
        '<footer>',
        '<div class="wrap foot-in">'
        f'<span>&copy; 2026 Deep Vyas &mdash; {c["name"]} &middot; {c["client"]}</span>'
        '<a href="index.html#contact">Have a role in mind? &rarr;</a>'
        '<a href="#top">Back to top &uarr;</a>'
        '</div></footer>',
        '<script src="js/system.js" defer></script>',
        '</body>\n</html>',
    ])


def render(c, prev, nxt):
    out = []
    A = out.append

    # ── head
    plain_title = strip_tags(c["title"]).replace("&nbsp;", " ")
    A('<!DOCTYPE html>\n<html lang="en" data-theme="light">\n<head>')
    A('<meta charset="utf-8">')
    A('<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">')
    A(f'<title>{esc(c["name"])} — {esc(c["client"])} · Deep Vyas</title>')
    A(f'<meta name="description" content="{esc(strip_tags(c["sum"])[:180])}">')
    A('<meta name="theme-color" content="#FFFFFF">')
    A(f'<meta property="og:title" content="{esc(c["name"])} — {esc(plain_title)}">')
    A('<link rel="icon" href="d-logo.svg">')
    A('<script>/* light is the default; the OS preference does not decide it. '
      'a stored choice from the toggle always wins. */'
      'try{var t=localStorage.getItem("dv26-theme");'
      'if(t)document.documentElement.setAttribute("data-theme",t);}catch(e){}</script>')
    A('<link rel="preconnect" href="https://fonts.googleapis.com">')
    A('<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>')
    A('<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter:wght@300..700&family=Newsreader:ital,opsz,wght@1,6..72,400..500&display=swap">')
    A('<link rel="stylesheet" href="css/system.css">')
    A('<style>' + CSS + '</style>')
    A('</head>\n<body>')
    A('<a class="skip" href="#problem">Skip to the case study</a>')
    A(NAV)
    A('<main id="top">')

    # ── hero
    A('<div class="back wrap"><a href="index.html#work">&larr; All work</a></div>')
    A('<header class="chero wrap">')
    A('  <div class="kick rv">' + '<span class="dot"></span>'.join(
        f'<span class="label">{k}</span>' for k in c["kick"]) + '</div>')
    A(f'  <h1 class="rv">{c["title"]}</h1>')
    A(f'  <p class="sum rv">{c["sum"]}</p>')
    if c.get("sum2"):
        A(f'  <p class="sum sum2 rv">{c["sum2"]}</p>')
    if c["meta"]:
        A('  <dl class="meta rv">' + ''.join(
            f'<div><dt>{k}</dt><dd>{v}</dd></div>' for k, v in c["meta"]) + '</dl>')
    if c.get("stage"):
        A('  <div class="stage rv">' + ''.join(
            f'<figure><img src="img/{f}" alt="{esc(cap)}"{dim(f)} '
            f'loading="eager" decoding="async"><figcaption>{cap}</figcaption></figure>'
            for f, cap in c["stage"]) + '</div>')
        A(f'  <p class="chero-note rv">{c["herocap"]}</p>')
    else:
        A(f'  <figure class="chero-fig{" full" if c.get("herofull") else ""} rv">'
          f'<img src="img/{c["hero"][0]}" alt="{esc(c["hero"][1])}"'
          f'{dim(c["hero"][0])} loading="eager" decoding="async">' +
          (f'<figcaption>{c["herocap"]}</figcaption>' if c["herocap"] else '') +
          '</figure>')
    if c.get("brief"):
        b = c["brief"]
        picks = ''.join(
            f'<div class="pick-c"><span class="n">{i+1:02d}</span><h4>{h}</h4><p>{t}</p></div>'
            for i, (h, t) in enumerate(b["picks"]))
        grid = ''
        if b.get("glance"):
            glance = ''.join(f'<dt>{k}</dt><dd>{v}</dd>' for k, v in b["glance"])
            impact = ''.join(f'<dt>{k}</dt><dd>{v}</dd>' for k, v in b["impact"])
            grid = ('<div class="brief-grid">'
                    f'<div class="brief-col"><h3>Project at a glance</h3><dl>{glance}</dl></div>'
                    f'<div class="brief-col stack"><h3>Impact at a glance</h3><dl>{impact}</dl>'
                    f'<p class="brief-note">{b["note"]}</p></div></div>')
        head = (f'<h3 class="picks-h">{b["pickh"]}</h3>' if b.get("pickh")
                else f'<h3 class="picks-k">{b["pickk"]}</h3>')
        A('  <section class="brief rv" aria-labelledby="brief-h">'
          f'<h2 class="k" id="brief-h">{b["k"]}</h2>'
          f'{grid}{head}<div class="picks">{picks}</div>'
          '</section>')
    A('</header>')

    # ── chapters
    # A case can declare its own chapter list when six isn't enough; the five
    # that don't still run the standard Problem → Reflection path below.
    if c.get("chapters"):
        # a rail of the sections, in the left margin, for a page this long
        A('<nav class="srail" aria-label="Sections in this case study"><ol>' + ''.join(
            f'<li><a href="#{ch["slug"]}" data-nav><span class="d">{i:02d}</span>'
            f'<span class="t">{ch["title"]}</span></a></li>'
            for i, ch in enumerate(c["chapters"], 1)) + '</ol></nav>')
        for i, ch in enumerate(c["chapters"], 1):
            # some files number their own sections (01, then Decision 01), so a
            # chapter can give the label verbatim instead of taking the count
            lbl = ch.get("lbl")
            A(chapter((f"{i:02d}", ch["slug"]), ch["title"], ch["h"],
                      blocks(ch["blocks"]), ch.get("tone", ""), lbl))
        A(tail(c, prev, nxt))
        return "\n".join(out)

    # ── 01 problem
    p = c["problem"]
    side = ''
    if p.get("signals"):
        side = ('<div class="side"><div class="signals">' + ''.join(
            f'<div class="signal"><p class="n">{n}</p><p class="c">{c}</p></div>' for n, c in p["signals"]) +
            '</div></div>')
    inner = ['  <div class="ch-body rv"><div class="prose">' + ''.join(f'<p>{x}</p>' for x in p["p"]) + '</div>' + side + '</div>']
    if p.get("art"): inner.append(art(p["art"]))
    inner.append('  <div class="finds rv">' + ''.join(
        f'<div class="find"><span class="n">{i+1:02d}</span><h3>{h}</h3><p>{b}</p></div>'
        for i, (h, b) in enumerate(p["finds"])) + '</div>')
    A(chapter(("01", "problem"), "The problem", p["h"], "\n".join(inner)))

    # ── 02 research
    r = c["research"]
    inner = ['  <div class="ch-body rv"><div class="prose">' + ''.join(f'<p>{x}</p>' for x in r["p"]) + '</div></div>']
    inner.append('  <div class="methods rv">' + ''.join(
        f'<div class="method"><span class="k">{k}</span><h3>{h}</h3><p>{b}</p></div>'
        for k, h, b in r["methods"]) + '</div>')
    if r.get("art"): inner.append(art(r["art"]))
    if r.get("quote"):
        q, cite = r["quote"]
        inner.append(f'  <blockquote class="quote rv"><p>&ldquo;{q}&rdquo;</p><cite>{cite}</cite></blockquote>')
    A(chapter(("02", "research"), "Research", r["h"], "\n".join(inner)))

    # ── 03 strategy
    s = c["strategy"]
    inner = ['  <div class="ch-body rv"><div class="prose">' + ''.join(f'<p>{x}</p>' for x in s["p"]) +
             '</div><div class="side"><ol class="crit">' + ''.join(f'<li>{x}</li>' for x in s["crit"]) +
             '</ol></div></div>']
    if s.get("art"): inner.append(art(s["art"]))
    A(chapter(("03", "strategy"), "Strategy", s["h"], "\n".join(inner)))

    # ── 04 design
    inner = []
    for d in c["decisions"]:
        k, h, b = d[0], d[1], d[2]
        fig = ''
        if len(d) > 3 and d[3]:
            fig = (f'<figure class="art"><img src="img/{d[3]}" alt="{esc(d[4])}"{dim(d[3])} loading="lazy" '
                   f'decoding="async"><figcaption>{d[4]}</figcaption></figure>')
        inner.append(f'  <article class="dec rv"><div class="dec-grid"><span class="k">{k}</span>'
                     f'<div class="b"><h3>{h}</h3><p>{b}</p>{fig}</div></div></article>')
    if c["gallery"]:
        inner.append('  <div class="gal rv">' + ''.join(
            f'<figure><img src="img/{img}" alt="{esc(alt)}"{dim(img)} loading="lazy" decoding="async">'
            f'<figcaption><b>{t}</b>{cap}</figcaption></figure>' for img, alt, t, cap in c["gallery"]) + '</div>')
    A(chapter(("04", "design"), "Design", "The decisions, and what each one cost.", "\n".join(inner)))

    # ── 05 impact
    im = c["impact"]
    inner = ['  <div class="ch-body rv"><div class="prose">' + ''.join(f'<p>{x}</p>' for x in im["p"]) + '</div></div>']
    inner.append('  <div class="outs rv" style="margin-top:clamp(30px,3.6vw,46px)">' + ''.join(
        f'<div class="out"><p class="n">{n}</p><p class="c">{cap}</p></div>' for n, cap in im["outs"]) + '</div>')
    if im.get("art"): inner.append(art(im["art"]))
    if im.get("caveat"):
        lbl, body = im["caveat"]
        inner.append(f'  <p class="caveat rv"><b>{lbl}</b>{body}</p>')
    A(chapter(("05", "impact"), "Impact", im["h"], "\n".join(inner)))

    # ── 06 reflection
    rf = c["reflection"]
    inner = ['  <div class="lessons rv">' + ''.join(
        f'<div class="lesson"><h3>{h}</h3><p>{b}</p></div>' for h, b in rf["lessons"]) + '</div>']
    inner.append(f'  <p class="caveat rv"><b>What I&rsquo;d do differently</b>{rf["diff"]}</p>')
    A(chapter(("06", "reflection"), "Reflection", "What it taught me.", "\n".join(inner)))

    A(tail(c, prev, nxt))
    return "\n".join(out)


if __name__ == "__main__":
    here = os.path.dirname(os.path.abspath(__file__))
    n = len(CASES)
    # pettrackr.html is no longer generated. It is written by hand, straight from
    # the Figma frame 53947:500, with its own stylesheet and a layout per section
    # — the shared components here flattened every frame into the same cards.
    # Its prev/next links still come from this list, so the order below matters.
    HAND_WRITTEN = {"pettrackr", "teleconsult", "flintlink", "aip", "myaster", "apex"}
    for i, c in enumerate(CASES):
        if c["slug"] in HAND_WRITTEN:
            print(f"  - {c['slug']}.html  (hand-written, skipped)")
            continue
        page = render(c, CASES[(i - 1) % n], CASES[(i + 1) % n])
        path = os.path.join(here, c["slug"] + ".html")
        with open(path, "w", encoding="utf-8") as f:
            f.write(page)
        print(f"  ✓ {c['slug']}.html  ({len(page):,} bytes)")
    print(f"\n{n} case studies built.")
