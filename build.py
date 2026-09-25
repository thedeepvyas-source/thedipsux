#!/usr/bin/env python3
"""
DELTA — case-study generator.

Six static pages from one template, so every case study reads the same spine:
Problem → Research → Strategy → Design → Impact → Reflection.

    python3 build.py

Content is quoted from the source case studies. No claim is invented here.
"""
import html, os, struct

IMG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "img")

# ── Case-page styles (the shared system lives in css/system.css) ────────
CSS = """
/* ── Case hero ─────────────────────────────────────────────────── */
.back{padding-top:clamp(26px,4vw,44px)}
.back a{font-family:var(--mono);font-size:var(--t-label);letter-spacing:.12em;text-transform:uppercase;color:var(--faint)}
.back a:hover{color:var(--accent)}
.chero{padding-top:clamp(20px,3vw,34px)}
.chero .kick{display:flex;flex-wrap:wrap;align-items:center;gap:8px 14px;margin-bottom:clamp(20px,2.6vw,30px)}
.chero .kick .dot{width:4px;height:4px;border-radius:50%;background:var(--accent)}
.chero h1{font-size:clamp(29px,5.4vw,74px);font-weight:600;line-height:1.01;letter-spacing:-.045em;max-width:18ch;text-wrap:balance}
.chero h1 em{font-family:var(--display);font-style:italic;font-weight:400;color:var(--accent);letter-spacing:-.01em}
.chero .sum{margin-top:clamp(22px,2.8vw,34px);font-size:clamp(17px,1.6vw,20px);line-height:1.6;color:var(--muted);max-width:62ch}
.meta{margin-top:clamp(34px,4vw,52px);display:grid;grid-template-columns:repeat(4,1fr);gap:1px;
  background:var(--line-2);border-block:1px solid var(--line-2)}
/* The 1px gaps are divider rules, so every cell needs breathing room on the
   side a rule falls — except the one that opens a row, which stays flush with
   the content edge. The exception moves with the column count. */
.meta div{background:var(--bg);padding:18px 24px 20px 24px}
.meta div:first-child{padding-left:0}
.meta dt{font-family:var(--mono);font-size:10.5px;letter-spacing:.15em;text-transform:uppercase;color:var(--faint);margin-bottom:8px}
.meta dd{font-size:14.5px;line-height:1.5;color:var(--ink);font-weight:450}
.chero-fig{margin-top:clamp(34px,4.4vw,60px)}
/* the case heroes are 16:9; the frame matches so none of them is cropped */
.chero-fig img{width:100%;aspect-ratio:16/9;object-fit:cover;object-position:top center;
  border-radius:var(--r);border:1px solid var(--line-2);background:var(--raise)}
.chero-fig figcaption{margin-top:12px;font-family:var(--mono);font-size:11px;letter-spacing:.06em;color:var(--faint)}

/* ── Outcome bar ───────────────────────────────────────────────── */
.outs{margin-top:clamp(40px,5vw,72px);display:grid;grid-template-columns:repeat(3,1fr);gap:1px;
  background:var(--line-2);border:1px solid var(--line-2);border-radius:var(--r);overflow:hidden}
.out{background:var(--bg);padding:clamp(22px,2.4vw,30px)}
.out .n{font-family:var(--mono);font-weight:500;font-size:clamp(24px,2.8vw,36px);letter-spacing:-.045em;color:var(--accent);line-height:1.05}
.out .c{margin-top:10px;font-size:13.5px;line-height:1.5;color:var(--muted)}

/* ── Chapters ──────────────────────────────────────────────────── */
.ch{padding-top:clamp(64px,9vw,120px)}
.ch-head{display:grid;grid-template-columns:auto 1fr;gap:0 clamp(18px,3vw,40px);
  padding-bottom:22px;border-bottom:1px solid var(--line);margin-bottom:clamp(30px,3.6vw,48px)}
.ch-head .idx{font-family:var(--mono);font-size:var(--t-label);letter-spacing:.14em;color:var(--accent);padding-top:.55em}
.ch-head .ttl{font-family:var(--mono);font-size:var(--t-label);letter-spacing:.17em;text-transform:uppercase;color:var(--faint);padding-top:.55em}
.ch-head h2{grid-column:2;font-size:clamp(24px,3.2vw,40px);font-weight:600;letter-spacing:-.035em;
  line-height:1.1;max-width:22ch;margin-top:12px;text-wrap:balance}
.ch-body{display:grid;grid-template-columns:repeat(12,minmax(0,1fr));gap:var(--gap);align-items:start}
.prose{grid-column:1/8;min-width:0}
.prose p{font-size:16.5px;line-height:1.68;color:var(--muted)}
.prose p+p{margin-top:1.05em}
.prose strong{color:var(--ink);font-weight:500}
.side{grid-column:9/-1;min-width:0}

/* process artefacts — the diagrams that carry a decision. They come from
   the project record and keep their own palette, so they are framed as
   documents rather than restyled to match the site. */
.art{margin:clamp(24px,2.8vw,36px) 0 0}
.art img{width:100%;height:auto;border-radius:var(--r-sm);border:1px solid var(--line);background:#fff}
.art figcaption{margin-top:11px;font-family:var(--mono);font-size:11px;letter-spacing:.05em;
  line-height:1.62;color:var(--faint);max-width:78ch}
.art.wide{margin-top:clamp(30px,3.4vw,44px)}

/* problem-side signals: the numbers the research turned up */
.signals{border-top:1px solid var(--line-2)}
.signal{padding:14px 0;border-bottom:1px solid var(--line-2)}
.signal .n{font-family:var(--mono);font-weight:500;font-size:clamp(19px,2vw,24px);letter-spacing:-.04em;color:var(--accent)}
.signal .c{margin-top:5px;font-size:13px;line-height:1.5;color:var(--muted)}

/* numbered findings */
.finds{margin-top:clamp(32px,4vw,52px);border-top:1px solid var(--line-2)}
.find{display:grid;grid-template-columns:auto 1fr;gap:0 clamp(16px,2.4vw,32px);
  padding:22px 0;border-bottom:1px solid var(--line-2)}
.find .n{font-family:var(--mono);font-size:var(--t-label);letter-spacing:.12em;color:var(--accent);padding-top:.5em}
.find h3{font-size:17px;font-weight:600;letter-spacing:-.02em}
.find p{grid-column:2;margin-top:8px;font-size:14.5px;line-height:1.62;color:var(--muted);max-width:68ch}

/* method cards */
.methods{margin-top:clamp(30px,3.6vw,46px);display:grid;grid-template-columns:repeat(2,1fr);gap:1px;
  background:var(--line-2);border:1px solid var(--line-2);border-radius:var(--r);overflow:hidden}
.method{background:var(--bg);padding:clamp(20px,2.2vw,28px);transition:background-color .3s var(--ease)}
.method:hover{background:var(--surface)}
.method .k{font-family:var(--mono);font-size:10.5px;letter-spacing:.15em;text-transform:uppercase;color:var(--accent)}
.method h3{font-size:16.5px;font-weight:600;letter-spacing:-.02em;margin-top:10px}
.method p{margin-top:9px;font-size:14px;line-height:1.6;color:var(--muted)}

/* quote */
.quote{margin-top:clamp(30px,3.6vw,48px);padding:clamp(24px,3vw,36px);border-radius:var(--r);
  background:var(--accent-soft);border:1px solid var(--line-2)}
.quote p{font-family:var(--display);font-style:italic;font-size:clamp(20px,2.4vw,28px);line-height:1.34;
  letter-spacing:-.015em;color:var(--ink);max-width:40ch}
.quote cite{display:block;margin-top:16px;font-family:var(--mono);font-size:11px;letter-spacing:.12em;
  text-transform:uppercase;color:var(--faint);font-style:normal}

/* criteria */
.crit{list-style:none;counter-reset:c;border-top:1px solid var(--line-2)}
.crit li{counter-increment:c;position:relative;padding:16px 0 16px 42px;border-bottom:1px solid var(--line-2);
  font-size:15.5px;line-height:1.6;color:var(--ink-2)}
.crit li::before{content:counter(c,decimal-leading-zero);position:absolute;left:0;top:18px;
  font-family:var(--mono);font-size:11px;letter-spacing:.1em;color:var(--accent)}

/* decisions */
.dec{padding:clamp(28px,3.2vw,42px) 0;border-bottom:1px solid var(--line-2)}
.dec:first-of-type{border-top:1px solid var(--line)}
/* The chapter head already draws a rule under itself, so a block that opens
   a chapter must not draw a second one below the heading's margin. */
.ch-head + .dec,.ch-head + .lessons{border-top:0}
.dec-grid{display:grid;grid-template-columns:repeat(12,minmax(0,1fr));gap:var(--gap);align-items:start}
.dec .k{grid-column:1/4;font-family:var(--mono);font-size:10.5px;letter-spacing:.15em;text-transform:uppercase;color:var(--accent);padding-top:6px}
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
  border-radius:var(--r-sm);border:1px solid var(--line-2);background:var(--raise);
  transition:border-color .3s var(--ease)}
.gal figure:hover img{border-color:var(--line)}
.gal figcaption{margin-top:10px;font-size:12.5px;line-height:1.55;color:var(--muted)}
.gal figcaption b{display:block;font-weight:500;color:var(--ink);margin-bottom:3px;font-size:13.5px;letter-spacing:-.01em}
/* the magnifier is sized for a full-width figure; scale it to the thumbnail */
.gal .zoom-btn{right:7px;bottom:7px;width:27px;height:27px}
.gal .zoom-btn svg{width:12px;height:12px}


/* zoom affordance + lightbox — built by js/system.js around every case-study
   screenshot, so the markup below stays plain <figure><img>. */
.zoomwrap{position:relative;display:block;line-height:0}
.zoomwrap img{cursor:zoom-in}
/* Solid rather than translucent: it sits over arbitrary screenshots, and a
   backdrop-filter is one more thing that can fail to composite. */
.zoom-btn{position:absolute;right:10px;bottom:10px;width:34px;height:34px;border-radius:999px;
  display:grid;place-items:center;cursor:zoom-in;color:var(--ink-2);
  background:var(--bg);border:1px solid var(--line);
  box-shadow:0 2px 10px rgba(11,12,15,.14);opacity:.92;
  transition:opacity .24s var(--ease),transform .24s var(--ease),color .24s var(--ease)}
.zoom-btn svg{width:15px;height:15px}
.zoomwrap:hover .zoom-btn,.zoom-btn:hover,.zoom-btn:focus-visible{opacity:1;transform:scale(1.07);color:var(--accent)}

.lb{position:fixed;inset:0;z-index:150;display:flex;flex-direction:column;align-items:center;
  justify-content:center;gap:16px;padding:clamp(18px,4vw,52px);
  background:rgba(8,9,12,.9);backdrop-filter:blur(7px);
  opacity:0;visibility:hidden;transition:opacity .3s var(--ease),visibility .3s var(--ease)}
.lb.on{opacity:1;visibility:visible}
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
@media (prefers-reduced-motion:reduce){.lb,.lb img,.zoom-btn{transition:none}.lb img{transform:none}}

/* caveat */
.caveat{margin-top:clamp(28px,3vw,40px);padding:20px 22px;border-left:2px solid var(--accent);
  background:var(--raise);border-radius:0 var(--r-sm) var(--r-sm) 0;font-size:15px;line-height:1.62;color:var(--ink-2)}
.caveat b{display:block;font-family:var(--mono);font-size:10px;letter-spacing:.16em;text-transform:uppercase;
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
.nextnav .lbl{font-family:var(--mono);font-size:var(--t-label);letter-spacing:.15em;text-transform:uppercase;color:var(--faint);display:block;margin-bottom:10px}
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
  .prose,.side{grid-column:1/-1}
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
  .gal{grid-template-columns:repeat(2,1fr)}
  .lesson{grid-template-columns:1fr;gap:8px}
  .ch-head{grid-template-columns:1fr}
  .ch-head h2{grid-column:1;margin-top:10px}
  .ch-head .ttl{padding-top:0;margin-top:6px}
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
 "kick":["Aster, UAE","Native app · Six services","Team of four"],
 "title":'One healthcare app for six services, where the patient sets up <em>only once</em>.',
 "sum":"Aster runs six healthcare services in the UAE: consultations by video or in person, an online pharmacy, health packages, chronic care, homecare and records. myAster puts all six in one native app, each with its own rules — insurance approvals, controlled medicines, eligibility. I led four designers from concept to approved final designs, on one account and one checkout shared by every service.",
 "meta":[("Role on this project","Lead UI/UX Designer · Led a team of four"),("Project type","Native mobile app, new product"),
         ("Client","Aster — UAE"),("Timeline","8–12 months")],
 "hero":("teleconsult-hero.jpg","myAster app home screen showing six healthcare services"),
 "herocap":"Illustrative data. Names are anonymised.",
  "problem":{"art":("tc-problem.jpg","The eight steps of one consultation. The video call is one of them; everything around it is where the design work sat."),"h":"Six services, one patient.",
  "signals":[("6","Services, each with its own operational rules"),("1","Account, checkout and identity model to serve all of them"),("5","Distinct insurance outcomes a patient can hit at checkout")],
  "p":["None of which is the patient's problem. They shouldn't have to learn six apps, or enter their family, ID and insurance six times over. <strong>The hard part was never any one service. It was everything the six had to share.</strong>"],
  "finds":[("Insurance isn't a yes or no","Covered outright, a co-pay, outside the default policy, or a GP referral needed first. A binary approved/declined screen sends a real patient to a dead end."),
           ("Controlled medicines can't be delivered","Delivery is off the table. The app has to say why, and where to collect with an Emirates ID, within 7 days."),
           ("Identity rules differ by person","Emirates ID for residents, passport for tourists, documents that expire. And people book for their children and parents, not only themselves."),
           ("Six setups, one patient","Without shared foundations, profiles, identity and insurance get configured six separate times.")]},
 "research":{"h":"Where the requirements came from.",
  "p":["Aster's business team supplied the operational rules, and every design went through a client walkthrough before it moved."],
  "methods":[("Interviews","Patients and doctors","Both sides of the consultation: the person booking and the person delivering care."),
             ("Product audit","The existing product","How people were already using myAster, before we added five more services on top."),
             ("Competitive","Regional healthcare apps","What patients in the UAE had already been taught to expect."),
             ("Cadence","Twice-monthly working sessions","Plus a client walkthrough of every flow, which is where most of the operational rules surfaced.")]},
 "strategy":{"h":"Build the shared foundations once. Let every service inherit them.",
  "p":["Not six service designs. One decision, taken once, about what profiles, identity, insurance and checkout do — so every service added later starts from something that already works."],
  "crit":["One account for the whole family, with every profile showing its status up front: verified, pending, incomplete, or an Emirates ID that has expired.",
          "Every insurance outcome carries a next step, self-pay included, so no checkout ends in a dead end.",
          "One checkout and one set of identity rules carry all six services."]},
 "decisions":[
  ("Foundation 01 · Profiles","One account for the whole family","Every profile wears its status openly — verified, verification pending, incomplete, or an expired Emirates ID — and tourists use a passport instead. You see it before booking starts, not at checkout.","tc-decision4.jpg","Profile status, shown before a booking starts."),
  ("Foundation 02 · Insurance","Give every insurance outcome a next step","Each of the five outcomes says plainly what happened and offers a way forward, self-pay included. Nobody reaches a screen with nothing to do next.","tc-decision3.jpg","The five insurance outcomes at checkout."),
  ("Service 01 · Consultations","The video call was the easy part","Everything around the call is the work: finding a doctor, the right patient profile, identity and insurance, a prescription afterwards. Two ways in — the next available GP with the wait time, or a filtered list by specialty, language and clinic. A waiting room with a countdown then collects vital signs, health questions, documents and the delivery address, so the doctor's time goes to care.","tc-decision1.jpg","The two ways into a consultation."),
  ("Service 02 · Pharmacy","Medicines that follow the patient","Patients pre-order medicines at booking, straight from the home screen, and confirm the delivery address while they wait — so the prescription goes out soon after the call ends.","tc-decision5.jpg","Pre-ordered at booking, dispatched after the call."),
  ("Services 03–05","Each service keeps its own rules without breaking the shared model","Health packages are bought first and booked later, with the clinic calling within 24 hours. Chronic care replaces separate bookings with one care plan holding appointments, medicines and monitoring labs. Homecare shows duration, price and next slot, and one booking can hold several visits on different dates.","tc-packages.jpg","Health packages: price and inclusions up front, booked after the clinic calls.")],
 "gallery":[],
  "impact":{"art":("tc-outcomes.jpg","What was delivered: 297 screens across six services, five insurance outcomes each with a next step, and one shared component system."),"h":"297 screens, approved for build.",
  "p":["<strong>In a multi-service app, the shared parts are the product.</strong> Profiles, insurance and checkout decided whether any individual service worked at all — and whatever Aster adds next starts from something that already works."],
  "outs":[("297","Screens across six services, approved for build"),
          ("18 + 161","Core and product components in one shared system"),
          ("5","Insurance outcomes, each with a next step")]},
 "reflection":{"lessons":[
   ("The shared parts are the product","Getting profiles, insurance and checkout right once made every service after them easier to build. The sixth cost less than the second."),
   ("Leading four designers means holding one model","Six service teams each wanted their own version of the same screen. Most of the job was telling a real difference from a preference, and saying so.")],
  "diff":"Agree the success metrics before design starts. We shipped 297 approved screens with no measurement plan behind them."}
},
{
 "slug":"flintlink", "name":"Flint-Link", "client":"Flint Group",
 "kick":["Flint Group","B2B portal · Self-serve","6 months, 2024"],
 "title":'Replacing email chaos with a self-serve portal for a <em>global B2B supply chain</em>.',
 "sum":"Flint Group supplies printing inks and coatings in 100+ countries. To get a certificate, an order update or support, its customers emailed their account manager and waited a day or two. I led the design of Flint-Link, a self-serve portal organised around the order rather than the document. All three success criteria passed acceptance testing at four customer organisations.",
 "meta":[("Role on this project","Lead UI/UX Designer · End to end, incl. acceptance testing"),
         ("Project type","B2B customer portal"),
         ("Domain","Printing inks and coatings"),
         ("Timeline","6 months (2024)")],
 "hero":("flintlink-hero.jpg","Flint-Link customer portal dashboard"),
 "herocap":"Illustrative data. Customer names are anonymised.",
  "problem":{"art":("flint-problem.jpg","Before: every request went to an account manager, who found the document and emailed it back a day or two later."),"h":"Every urgent request went through an account manager.",
  "signals":[("14","People asked to walk through their last urgent request"),("Every one","Answered with a person's name, never a system"),("6&ndash;10 hrs","Per week per account manager, spent retrieving documents")],
  "p":["I asked 14 people to walk me through the last time they urgently needed something from Flint. <strong>Every answer was a person's name, never a system.</strong>",
       "Documents, deliveries, invoices and support all funnelled through account managers by email — six to ten hours a week of retrieval for them, a day or two of waiting for the customer."],
  "finds":[("The portal category didn't match the mental model","Every competitor had a document-type IA, so I built one too. It fell apart the first time someone looked for a document tied to a delivery."),
           ("Consignment updates took four or more touchpoints","A single stock update meant several rounds with an account manager before anything was confirmed."),
           ("Unresolved issues became account-manager work","A customer with a common printing problem had nowhere to get an answer, so every question turned into an email."),
           ("Customers kept shadow spreadsheets","They couldn't count on a document coming back in time, so they kept their own parallel records.")]},
  "research":{"art":("flint-research.jpg","All 14 interviewees raised document retrieval unprompted, across three regions and two site visits."),"h":"14 interviews, two site visits, and one printed folder that explained everything.",
  "p":["The research question wasn't 'what features do you want.' It was 'walk me through the last time you urgently needed something' — a question that surfaces the workaround rather than the wish list."],
  "methods":[("Discover","14 interviews across 3 regions","Customers, account managers and internal support, spread deliberately so the answer wasn't one market's habit."),
             ("Discover","Two site visits","Seeing the printed CoA folder on someone's desk is what made the trust problem concrete."),
             ("Validate","Two rounds of usability testing","Round 1 exposed the IA failure. Round 2 confirmed the rebuild."),
             ("Validate","Customer acceptance testing","12 participants across four customer organisations, tested against three criteria agreed up front.")],
  "quote":("I keep a printed folder of CoA emails because I can't count on getting them back in time.","QA Lead · Site visit")},
  "strategy":{"art":("flint-goal.jpg","The five things customers used to email an account manager for, and where each one now lives in the portal."),"h":"Give customers a single place to find everything about an order, without asking a person.",
  "p":["The moves that mattered were structural: reframe the portal around the order rather than the document type, pin down the three criteria acceptance testing would run against, and argue one unbudgeted module into scope."],
  "crit":["A customer can find any document tied to a specific delivery without contacting anyone.",
          "Consignment stock updates and delivery confirmation happen on one screen, in a single pass.",
          "All three criteria signed off in customer acceptance testing at four organisations."]},
 "decisions":[
  ("Decision 01 · IA","Rebuild the information architecture mid-project","'Find the CoA for your last delivery' was the most-failed task in Round 1 — every participant failed it. I proposed rebuilding the IA around the order; the PM agreed the same day. In Round 2, every participant completed it. <strong>Not everyone was sold beforehand, so we tested it instead of arguing about it.</strong>","flint-decision1.jpg","Before: a document library browsed by type, where nothing connected to a delivery. After: everything about an order in one place."),
  ("Decision 02 · Consignment","Stock updates and delivery confirmation on one screen","Four or more touchpoints with an account manager became one pass: update stock, submit, confirm delivery.","flint-decision2.jpg","The consignment screen, in a single pass."),
  ("Decision 03 · Scope","Argue the Support Hub into scope","It wasn't in the brief. My case was simple: every unresolved issue turns into account-manager work — the exact cost the project existed to remove. A chat now answers common printing problems and hands off to a ticket when it can't. In pilot feedback it was the most-mentioned feature.","flint-decision3.jpg","The support flow, escalating to a ticket only when the chat can't answer."),
  ("Decision 04 · States","Design the failure states alongside the main flows","Download progress, success and failure states came out of an engineering review, not a polish pass at the end. In a portal whose whole promise is 'you'll get the document,' a silent failure breaks the product.","flint-engineer.jpg","In progress, complete, and failed with retry.")],
 "gallery":[("flint-orders.jpg","Flint-Link orders view","Orders","The spine of the rebuilt IA."),
            ("flint-documents.jpg","Flint-Link certificates of analysis","Certificates of analysis","The most-failed task in Round 1, now reached through the order rather than a document-type folder."),
            ("flint-invoices.jpg","Flint-Link invoices","Invoices","One of six report categories, now in one portal instead of six email threads."),
            ("flint-downloads.jpg","Flint-Link download centre","Download centre","The download states, designed alongside the flow rather than after it.")],
  "impact":{"art":("flint-outcomes.jpg","All three criteria, signed off."),"h":"All three success criteria signed off.",
  "p":["Acceptance testing ran with 12 participants across four customer organisations. Early pilot feedback showed fewer document requests reaching account managers, and the Support Hub came up more often than anything else.",
       ],
  "outs":[("0 → 100%","The most-failed task, now unanimous"),
          ("6–10 hrs/week","Account manager time freed up"),
          ("3 of 4","Pilot orgs dropped their shadow spreadsheets")]},
 "reflection":{"lessons":[
   ("Watching one person fail beats any report","I built a document-type IA because every competitor had one. A single test session — one person hunting for a delivery's certificate — was worth more than the entire competitive audit."),
   ("Test the disagreement instead of winning it","Rebuilding the IA mid-project wasn't a popular proposal. Putting it in front of users settled it in a day, for less than the argument would have cost.")],
  "diff":"Put customers from different industries in the same co-design session, so the tension between pharma packaging and commercial print surfaces early instead of turning up in acceptance testing."}
},
{
 "slug":"pettrackr", "name":"PetTrackr", "client":"Universal Biosensors",
 "kick":["Universal Biosensors","Mobile · iOS &amp; Android","6 months, 2022–23"],
 "title":'A daily companion for a diabetic pet, under constraints that <em>ruled out most design choices</em>.',
 "sum":"PetTrackr is Universal Biosensors' companion app for a Bluetooth glucose analyser, used by people managing a diabetic cat or dog. I designed it end to end: 100+ screens across iOS and Android in six months. Two constraints shaped nearly every decision — the analyser holds only seven days of readings, and owners log at 7am with one hand on a restless animal.",
 "meta":[("Role on this project","Lead UI/UX Designer · Only designer, research to handoff"),
         ("Project type","iOS and Android app, hardware-connected"),
         ("Domain","Pet health"),
         ("Timeline","6 months (2022–2023)")],
 "hero":("pettrackr-hero.jpg","PetTrackr app screens for logging and reviewing glucose readings"),
 "herocap":"Illustrative data.",
  "problem":{"art":("pet-constraint.jpg","The constraint that shaped everything: the analyser holds seven days. At nine days without a sync, two days of readings are already gone."),"h":"Managing a diabetic pet ran on paper and memory.",
  "signals":[("7 days","Analyser memory — miss a week of syncing and the data is gone"),("7 steps","In the onboarding I designed first, which 40% never finished"),("10","In-home interviews, plus a 14-day diary study")],
  "p":["Rather than ask about pain points, I asked owners to walk me through yesterday morning from start to finish. What came back was a routine held together by notebooks, phone alarms and remembering.",
       "<strong>And one constraint that couldn't be designed around:</strong> seven days of analyser memory. Miss a week of syncing and the data is simply gone."],
  "finds":[("Seven days of analyser memory","A hardware limit, not a preference. Syncing, reminders and device status all had to be built around a window that closes."),
           ("Logging happens one-handed, at 7am","With a restless animal in the other hand. Any flow assuming a calm, two-handed user fails in the room where it gets used."),
           ("A number means nothing without a range","A reading of 140 tells you nothing unless you know the pet's range — and owners are not clinicians."),
           ("Generic alarms get dismissed","Every diary participant had abandoned generic phone alarms by the end of week one. The ones managing several pets on different schedules gave up first.")]},
  "research":{"art":("pet-research.jpg","7 of 10 owners were tracking on paper, phone notes or memory."),"h":"Ten homes and a fourteen-day diary study.",
  "p":["In-home interviews put the routine in context. The diary study caught what interviews never do: what people quietly stop doing in week two."],
  "methods":[("Discover","10 in-home interviews","Walking through yesterday morning in the actual kitchen, with the actual animal."),
             ("Discover","14-day diary study","Where the generic-alarm failure showed up — not on day one, but by the end of week one."),
             ("Validate","3 rounds of usability testing","Round 1 is where my own onboarding design failed, at 60% completion."),
             ("Specialist","Vet consultation","Brought in at week six, and it reshaped the reporting feature.")],
  "quote":("I can never remember if I've done the reading. I have 3 dogs and they're all on different schedules.","Pet owner · In-home interview")},
 "strategy":{"h":"Design for 7am, one hand, and a person who is frightened.",
  "p":["I set four testable targets before the first wireframe. The call that mattered most came after Round 1: the problem wasn't the interface, it was the emotional state. Someone who has just learned their pet is diabetic doesn't want setup. They want reassurance the animal will be okay."],
  "crit":["Onboarding completion of at least 85% in usability testing.",
          "Logging a single reading in under 30 seconds, one-handed.",
          "A chart a non-clinical owner can interpret without training."]},
 "decisions":[
  ("Decision 01 · Onboarding","Cut onboarding to one first win","I designed a seven-step onboarding and I believed in it. In Round 1, only 60% finished. The rebuild came down to one question: what single action makes the app feel worth it? Logging one reading and seeing it land on the chart. Completion reached 89%. <strong>Every step of the original had a reason — and someone who leaves at step 4 doesn't care how well steps 5 to 7 were designed.</strong>","pet-decision1.jpg","Before: seven onboarding steps, 60% completed. After: three skippable intros and one first win — 89%."),
  ("Decision 02 · Logging","Make logging a confirmation, not data entry","The active pet, date and time come pre-filled, so the app assumes the most likely answer instead of asking for it. One reading, under 30 seconds, one hand.","pet-decision2.jpg","The Add Blood Glucose screen."),
  ("Decision 03 · Charts","Let the chart say what the number means","Colour zones for low, in range and high cut time-to-understand from 22 seconds to 7.","pet-decision3.jpg","Before: a list of readings with no context. After: colour zones."),
  ("Decision 04 · Reminders","Reminders specific to the pet and the task","Each pet carries its own schedule by type, and notifications name the pet and what's due.","pet-decision4.jpg","Before: a generic 7:00 AM phone alarm. After: per-pet reminders that name the pet and the task."),
  ("Decision 05 · Reports","Build reports for the vet's inbox, not for the app","Vets wanted two-week trends before adjusting insulin, and most clinics don't use shared apps. Owners pick a time frame and share a PDF — which is how the clinic actually works.","pet-decision5.jpg","Reports: 7, 14 or 30 days, or a year.")],
 "gallery":[("pet-profile.jpg","PetTrackr pet profile setup","Pet profile","Species, breed, glucose range and insulin dose, set once per pet — what makes every later reading readable."),
            ("pet-logbook.jpg","PetTrackr logbook","Logbook","Every reading, meal, insulin dose and exercise for the day, per pet."),
            ("pet-myanalyzer.jpg","PetTrackr analyser status screen","My analysers","Last sync and connection state per analyser. One is nine days out — past the seven-day memory, so that data is gone."),
            ("pet-states.jpg","PetTrackr empty and error states","States","Designed alongside the main flows, because a hardware-connected app spends real time in them.")],
  "impact":{"art":("pet-outcomes.jpg","Results against the four targets."),"h":"89% completion, against an 85% target.",
  "p":["The pairing guide came out of the same testing: four of five testers failed analyser pairing in Round 1, before any step-by-step guide existed."],
  "outs":[("60 → 89%","Onboarding completion after the first-win rebuild"),
          ("3–5 min → &lt;30s","To log a single glucose reading"),
          ("22 → 7 sec","Chart comprehension with colour zones")]},
 "reflection":{"lessons":[
   ("Being right about the details and wrong about the priorities is still a failure","Every step of the seven-step onboarding had a good reason behind it. None of that mattered to the people who left at step four."),
   ("The interface wasn't the problem — the emotional state was","It took a diary study, not a usability metric, to show that people who had just learned their pet was diabetic wanted reassurance before setup.")],
  "diff":"Treat vets as users from week one. I brought them in at week six as specialist input, and it cost two sprints of rework on reporting."}
},
{
 "slug":"kidneylink", "name":"KidneyLink", "client":"U.S. Renal Care",
 "kick":["U.S. Renal Care","Clinical · Enterprise UX","6 months"],
 "title":'The data was there. <em>Getting to it</em> was the problem.',
 "sum":"U.S. Renal Care runs one of the largest kidney care networks in the country. Across 400+ locations, clinical teams tracked patients in spreadsheets, on sticky notes and through workarounds layered onto aging EHRs. KidneyLink replaced all of it with one portal: eGFR trajectories, high-risk-hospitalisation flags, provider scorecards and secure messaging. Every feature traces back to a research finding.",
 "meta":[("Role on this project","Lead UI/UX Designer · Research · IA · Design · System · Handoff"),
         ("Project type","Enterprise UX · Proactive intelligence"),
         ("Domain","Clinical operations"),
         ("Timeline","6 months · 1 PM, 1 clinical researcher, 6 engineers")],
 "hero":("kidneylink-hero.jpg","KidneyLink patient roster dashboard"),
 "herocap":"Illustrative data. Patient names are anonymised.",
 "problem":{"h":"Providers started every morning reconciling spreadsheets before they could do anything clinical.",
  "signals":[("40+","Min/day lost to data reconciliation, self-reported by all 18 providers and corroborated by 12h of observation"),("4&ndash;6","Browser windows open during a single patient review, observed live at 3 clinic sites"),("14","Care handoff points with identified information-loss risk, across 7 clinical stages"),("0","Existing tools with proactive HRH or eGFR risk flagging, confirmed in competitive audit")],
  "p":["The data existed; there was just no one place to read it. HRH flags arrived after the fact, eGFR trends sat buried in charts, and care handoffs left no audit trail. Nobody could see risk coming.",
       "<strong>USRC's payer contracts are increasingly tied to outcomes</strong> — CMS rewards networks that catch deterioration early and prevent avoidable hospitalisations. That is what let clinical leadership fund the work."],
  "finds":[("No unified patient roster","Patient lists lived in personal spreadsheets and across 3+ EHR modules, none of them in sync. Morning rounds opened with 40+ minutes of reconciliation rather than care planning — raised unprompted by every provider we interviewed."),
           ("eGFR data buried in charts","The most critical prognostic signal for CKD patients sat 4–5 clicks deep, with no trend visualisation and no alert thresholds. Providers knew it was in there. They couldn't act on it."),
           ("High-risk hospitalisation blind spots","Usually discovered after admission. Nothing flagged at-risk patients during the 30-day window where intervention can still prevent one."),
           ("IDT communication gaps","Phone calls, faxes and EHR notes — no audit trail, no read receipts, no shared patient context across roles.")]},
 "research":{"h":"Six methods. Four phases. Several assumptions that turned out to be wrong.",
  "p":["We spent the first few weeks in clinics, before drawing anything."],
  "methods":[("Discover","Stakeholder interviews","Nephrologists, IDT members, coordinators and clinical leadership, at 6 locations across 3 regions. The 40+ min/day in reconciliation came up unprompted in all 18."),
             ("Discover","Contextual inquiry","12 hours shadowing morning rounds and IDT meetings at 3 sites. Every patient review ran with 4–6 browser windows open — more than anyone admitted in interview."),
             ("Define","Journey mapping","CKD diagnosis through to ESKD transition. 14 handoff points where information loss caused care gaps, and HRH signals surfacing 2–3 weeks late — after the intervention window had closed."),
             ("Define","Competitive & heuristic audit","Epic, Cerner, IQVIA and two nephrology platforms among them. 31 heuristic violations, and no eGFR trend visualisation in any of the six."),
             ("Design","Co-design sessions","4 sprints with 22 clinical staff. Providers rejected card layouts unanimously — they wanted spreadsheet density, not a 'nicer' UX. Secure messaging came out of these sessions and nowhere else."),
             ("Validate","Moderated usability testing","3 rounds, 8 providers each, every round going after the last one's failures instead of re-validating the same design.")],
  "quote":("I start every morning opening three different tabs before I can see anything useful about my patients. By the time I'm done, I've already lost 40 minutes.","Nephrologist · Southwest Regional Clinic · Interview 3")},
 "strategy":{"h":"Give clinical teams one place to act on patient risk, without reconciling spreadsheets first.",
  "p":["Three testable outcomes, agreed at kickoff and measured in moderated testing rather than claimed afterwards."],
  "crit":["Task completion at or above 85% on core clinical workflows in moderated testing.",
          "Zero critical failures in the final usability round.",
          "Providers able to complete a full morning patient review without switching to any external tool."]},
 "decisions":[
  ("Decision 01 · The pivot","Round 1 came back at 61%, and the hypothesis was wrong","Our plan had been to surface everything and let providers filter. Four of eight told us it was too much information. We turned it around: less data, clearer prioritisation. <strong>Most of what defines the final design came from that pivot, not from the original brief.</strong>"),
  ("Decision 02 · Density","Density serves clinicians — cards don't","Providers turned down sparse, card-based layouts in every test. They wanted the density of their own spreadsheets: everything visible at once, organised by hierarchy rather than spread over clicks. A worse screenshot, a better tool."),
  ("Decision 03 · The cut","We cut the eGFR visualisation we'd spent two sprints refining","Multi-point plotting, customisable date ranges, comparative overlays — providers skipped all of it in testing. We replaced the lot with one line: <em>eGFR declining at 4 mL/min/yr, ESKD transition likely within 18 months.</em> Comprehension went from 38% to 91%."),
  ("Decision 04 · Vocabulary","'Filter' failed. 'Narrow by' didn't","One participant put it plainly: the word 'Filter' didn't read as an action. Renaming the control lifted task completion by 40% in Round 2. Clinical staff use precise language, and the interface has to match it."),
  ("Decision 05 · Constraint","An engineering constraint that made the design better","Live filtering fired up to nine parallel API calls, and the lead engineer flagged race conditions on slow clinic networks. Rather than cut the filters back, we changed the interaction: apply on explicit confirm, with a badge previewing how many patients match. Providers came away feeling more in control, not less.")],
 "gallery":[("usrc-insights.jpg","KidneyLink patient insights view","Patient insights","Where the detailed eGFR chart used to sit. One sentence replaced it."),
            ("usrc-scorecard.jpg","KidneyLink provider scorecard","Provider scorecard","eGFR slope averages, ESKD progression and HRH frequency, benchmarked against clinic average and network median."),
            ("usrc-carepathway.jpg","KidneyLink care pathway view","Care pathway","CKD diagnosis through to ESKD transition, with all 14 handoff points made shared and traceable."),
            ("usrc-filter.jpg","KidneyLink advanced filtering","Filtering","Up to nine stacked filters — the redesign that came out of the engineering constraint."),
            ("usrc-openitems.jpg","KidneyLink open items overlay","Open items","Unresolved care items, pending lab reviews and overdue IDT actions, assignable by role with a full audit trail."),
            ("usrc-messaging.jpg","KidneyLink secure messaging","Secure messaging","Patient-linked, HIPAA-compliant threads in place of phone tag and faxes."),],
 "impact":{"h":"Three rounds of testing backed the approach. Sixty days in, it still held.",
  "p":["By 60 days post-launch, HRH flagging and open items were central to the daily workflow, and the paper printouts we had seen at all three observation sites had gone. Coordinators called it <strong>the first morning review tool they actually trusted</strong>.",
       "Secure messaging, which wasn't in the brief and came entirely out of co-design, had the highest adoption rate of any feature."],
  "outs":[("61 → 94%","Task completion, Round 1 to final round, with 8 practising nephrologists"),
          ("0","Critical failures in the final usability round"),
          ("3×","Faster morning review, with no external tool required")],
  "caveat":("Honest caveat","We never captured reconciliation time — we proposed tracking it post-launch, but the EHR access was never scoped into the engagement. It's the gap I would close first.")},
 "reflection":{"lessons":[
   ("Interface confusion in clinical software carries real risk","A confusing UI in a clinical setting isn't just friction — it feeds into care decisions."),
   ("Providers needed a sentence, not a chart","The more complete artefact lost to the more useful one. Comprehension rose by taking work away, not adding it."),
   ("Scope what research makes obvious, not what the brief allows","Secure messaging wasn't in the brief. Four participatory sessions surfaced it, and it ended up the highest-adoption feature post-launch.")],
  "diff":"Run Round 1 in the clinic, not the lab. Ours was lab-based: quiet room, no distractions, clean data — and half the truth. Round 2 ran in an actual clinic, with morning-round interruptions and live EHR context, and exposed failures the lab couldn't produce."}
},
{
 "slug":"rxagile", "name":"RxAgile", "client":"RxAgile Inc.",
 "kick":["RxAgile Inc.","PBM · Greenfield","8 months"],
 "title":'Designing the backbone of a pharmacy benefits platform, by first learning <em>what I didn\'t know</em>.',
 "sum":"The first interview told me I was in trouble. The operator used nine terms I didn't fully understand, and I nodded through about half of them. RxAgile was building a PBM administration platform from scratch: tenants, pharmacy networks, pricing contracts, spread analytics. One designer, eight months. I spent the first eight weeks getting fluent before drawing a wireframe.",
 "meta":[("Role on this project","Lead UI/UX Designer · Only designer, research to handoff"),
         ("Project type","Enterprise UX · Workflow systems · Complex domain"),
         ("Domain","Pharmacy Benefits Management (PBM)"),
         ("Timeline","8 months · 1 PM, 1 business analyst, engineering")],
 "hero":("rxagile-hero.jpg","RxAgile claim adjudication and client configuration interface"),
 "herocap":"Illustrative data. Client names are anonymised.",
 "problem":{"h":"I walked in assuming a UX problem. It wasn't one.",
  "signals":[("5","Interdependent entities to configure before a claim can adjudicate"),("14","Decision points where operators had to look something up or guess"),("3","Disconnected systems a single onboarding spanned before the platform"),("90+","Interview observations, clustered into three underlying problems")],
  "p":["I arrived with the usual assumption: complex enterprise software means too much data, too many fields, confusing navigation. I had the mental model before reading a single document.",
       "Forty pages into the domain docs I hit a wall — not because the documents were unclear, but because I didn't know what claim adjudication meant on the floor. <strong>I knew the words. I didn't know what the person at the screen was trying to do.</strong> Ninety interview observations later, 'confusing software' had resolved into four specific failures."],
  "finds":[("Context collapse","Operators lost track of which account they were configuring, then entered data into the wrong tenant with nothing to warn them. It surfaced later, and rarely quietly."),
           ("Invisible cascade","A pricing change ripples into network tiers and client rules, and nothing showed it. Operators found out from the adjudication logs, after the fact and under pressure."),
           ("Unenforced sequence","Configuration follows a rigid dependency order the tools never enforced. Skip a step and the blocker lands three modules later, during claim processing, in front of clients."),
           ("No hierarchy in dense tables","Dense by necessity, rendered flat, everything weighted equally. Real — but downstream of the other three.")]},
 "research":{"h":"I didn't run a research process. I ran an investigation.",
  "p":["To have a useful conversation with anyone, I first had to understand the answers — eight weeks of learning the domain before a single wireframe."],
  "methods":[("Chapter 1","Reading the documentation","120+ pages of regulatory documents, contract templates, NDC formulary structures and claim flow diagrams, read twice. Not to become an expert — to stop being a liability in conversations. A claim can't adjudicate until five interdependent entities are configured, in order."),
             ("Chapter 2","The interviews","8 sessions with operators, implementation consultants and account managers. I went in convinced the problem was density. That started coming apart around interview three."),
             ("Chapter 3","The workflow map","Drawing tenant creation through to live claim adjudication made plain what no interview had said out loud: all five modules had a dependency order, and the tools enforced none of it."),
             ("Dead end","The false lead","Still fixated on density, I built collapsible panels and progressive disclosure. The PM liked it. It kept feeling like a symptom, so I audited Salesforce, Stripe, NetSuite and Benefytt. The one pattern across all four was persistent context — and density was downstream of it."),
             ("Chapter 4","Affinity synthesis","Clustered by what was going wrong underneath the complaint, not by user role or feature area."),
             ("Validation","Concept walkthroughs","Low-fidelity IA and navigation, before a single high-fidelity screen. I wanted the model confirmed before the work started.")],
  "quote":("Every morning I open three browser tabs just to remember which client I'm configuring. By the time I've found the right network tier, I've second-guessed myself twice about whether I'm even in the right tenant.","PBM implementation consultant · Week 4 interview")},
 "strategy":{"h":"An information architecture that mirrors the dependency sequence — and enforces it.",
  "p":["The domain already had a rigid order; the tools had never expressed it. Making it visible, and holding progress until each step is ready, was the whole strategy: <strong>Tenant → Network → Pricing → Client → Spread.</strong> The three criteria below were agreed with the PM before any design started."],
  "crit":["A new tenant configured from scratch, without external documentation.",
          "Configuration error rate below 5% in usability sessions.",
          "Operators describe the interface as thinking the way they do."]},
 "decisions":[
  ("Decision 01 · The plot twist","Six weeks in, I found a user type I had designed nothing for","Someone mentioned in passing that once they finish the config, it goes to a colleague for sign-off. I stopped the interview. Who? The account manager who reviews it before production. How often? Every client, always. I had designed five modules for the operators who build configurations and not one screen for the people who authorise them. That conversation cost two unplanned sprints. <strong>The approval summary screen we built is now the highest-traffic screen in the platform.</strong>"),
  ("Decision 02 · Context","A persistent tenant badge fixed more errors than any redesign","Always visible in the header, on every module. That's the whole intervention. Context collapse — the biggest single source of errors — fell further from this one element than from any module redesign."),
  ("Decision 03 · Cascade","Show the downstream impact before the save, not in the logs","Pricing in PBM is a matrix of AWP discounts, MAC overrides, dispensing fees and formulary tiers. The module now previews which clients will be affected and what will change, before you save. An operator asked for it unprompted in a concept walkthrough; it became one of the most-mentioned features in satisfaction feedback."),
  ("Decision 04 · Sequence","Make the required order visible and mandatory","Operators used to configure employer groups, benefit plans and eligibility rules in whatever order felt right, then hit blockers at claim processing. A guided checklist now holds progression until dependencies are met."),
  ("Decision 05 · Placement","Spread analytics was placed last and consulted most","Operators kept breaking off mid-setup to check margins in a separate tool, so I moved spread onto a persistent dashboard. Not a new feature — a placement decision.")],
 "gallery":[("pbm-tenant-detail.jpg","RxAgile tenant configuration view","Tenant management","The persistent tenant badge, progress tracker, and role-based access with inheritance preview."),
            ("pbm-pricing.jpg","RxAgile pricing and contracts module","Pricing & contracts","Contract segments, effective dates, and the impact preview that names affected clients before a save."),
            ("pbm-tenant-list.jpg","RxAgile tenant list","Tenant list","One-click switching with confirmation, and a tracker showing which modules still need configuring."),
            ("pbm-pharmacy-network.jpg","RxAgile pharmacy network","Pharmacy network","Tier grouping, bulk NPI import with conflict detection, and inherited versus overridden pricing rules side by side — the #1 source of configuration errors, now visible."),
            ("pbm-client-network.jpg","RxAgile client and adjudication","Client & adjudication","Enforcing a sequence that had never been encoded."),],
 "impact":{"h":"All three criteria held at launch.",
  "p":["Client onboarding errors fell 60%, tenant configuration ran 3× faster, and operator satisfaction came in at 4.6/5 post-launch.",
       "<strong>Once you know the real problems, the answers become obvious.</strong> The six weeks of investigation were the hard part."],
  "outs":[("60%","Reduction in client onboarding errors"),
          ("3×","Faster tenant configuration"),
          ("4.6/5","Operator satisfaction post-launch")],
  "caveat":("Honest caveat","I validated that operators could complete configurations, but never how long it took them — there was no setup-time benchmark. That is the first thing I would define next time.")},
 "reflection":{"lessons":[
   ("Domain fluency is a design deliverable","In PBM software, terminology is trust. A field with the wrong name tells an operator the designer didn't understand the work — and they stop trusting everything else on the screen."),
   ("The complaint is rarely the problem","'Too much data' was real, but it was the fourth problem, downstream of three others. Fixing visual hierarchy first would have been a well-executed answer to the wrong question."),
   ("Ask who sees this next","Six weeks and eight interviews, and I still missed an entire user type. I now ask what happens to the work after this person finishes it, in every interview.")],
  "diff":"Define a setup-time benchmark alongside the error-rate criterion. I proved operators could do the work. I can't prove how much faster they did it, beyond what the client reported."}
},
{
 "slug":"aip", "name":"Apex Insights Portal", "client":"LTC Analytics",
 "kick":["Apex Insights","Analytics · 0 → 1","126 screens"],
 "title":'Turning fragmented care data into <em>decisions that get made</em>.',
 "sum":"Long-term care executives were making staffing decisions from reports an analyst assembled by hand out of four systems — and those reports arrived 3+ days late. I led the design of a portal built on embedded Power BI, organised around the decisions administrators make every morning. The prototype helped win a ~$100k engagement before production started, and at the pilot client report turnaround dropped to same day.",
 "meta":[("Role on this project","Lead UI/UX Designer · Discovery to handoff"),
         ("Project type","Power BI analytics portal · 0 → 1"),
         ("Client","Apex Insights — long-term care analytics"),
         ("Timeline","8 months")],
 "hero":("aip-hero.jpg","Apex Insights Portal staffing dashboard"),
 "herocap":"Illustrative data. Facility names are anonymised.",
  "problem":{"art":("aip-problem-pipeline.jpg","Before: four separate systems, assembled into a report by hand, arriving 3+ days after the decision it was meant to inform."),"h":"The data existed. It reached decision-makers days late.",
  "signals":[("4","Systems the analyst was assembling each report from, by hand"),("3+ days","Report latency, against a decision made every morning"),("12","Stakeholder interviews across three facility types")],
  "p":["By the time a report landed, the decision it was meant to inform had already been made.",
       "<strong>This is a strategy problem wearing an analytics costume.</strong> The reports weren't wrong. They were organised around where the data came from, rather than around what anyone had to decide."],
  "finds":[("No early warning on staffing compliance","HPPD — hours per patient day, the main staffing compliance measure — was only ever reported after the fact, so leaders saw a compliance problem too late to fix it."),
           ("Alerts with no priority","Where alerts existed at all, they carried no priority and no context — everything at once, with nothing to say what mattered first."),
           ("Reports grouped by data source","The first IA mirrored how the systems were built. In testing, nobody could find anything — because nobody thinks in source systems at 8am."),
           ("Two audiences, one product","Executives wanted a handful of numbers. Finance analysts wanted the full data with filters. One product had to serve both without confusing either.")]},
  "research":{"art":("aip-research-stats.jpg","Research findings across 12 stakeholder interviews and four observed morning reviews."),"h":"Every facility had an analyst whose main job was assembling reports.",
  "p":["We watched the morning decision get made before designing anything for it."],
  "methods":[("Discover","12 stakeholder interviews","Executive directors, administrators, and the analysts doing the assembly work."),
             ("Discover","4 observed morning reviews","Watching the decision get made, instead of asking about it afterwards."),
             ("Define","Decision-flow mapping","The questions became the information architecture."),
             ("Validate","Usability testing","Run against the rebuilt IA, where the time to find a report halved in the following round.")],
  "quote":("By the time a report reaches me, I've already made the decision without it. I can't wait three days for data I needed this morning.","Executive Director · Regional LTC Network · Interview 7")},
  "strategy":{"art":("aip-goal-morning-questions.jpg","The three questions administrators asked every morning. These became the information architecture."),"h":"Give administrators self-serve answers to the questions they ask every morning, without an analyst.",
  "p":["One of the three criteria put design on the hook for a commercial outcome."],
  "crit":["Administrators can run any report without help from an analyst.",
          "An executive can understand a dashboard summary in under 2 minutes, without training.",
          "The prototype is strong enough to win a client commitment before production starts."]},
 "decisions":[
  ("Decision 01 · IA","Organise reports around decisions, not data sources","Our first IA grouped reports by source system. In testing, nobody could find anything. We regrouped around the decisions administrators make each morning, and time to find a report halved in the next round. <strong>The rebuild cost two weeks of unplanned work and an awkward conversation about the timeline — which was mine to have.</strong>","aip-ia-before-after-v2.jpg","The same morning question, before and after the IA rebuild."),
  ("Decision 02 · Alerts","Make severity visible, and don't let people hide it from themselves","The old list gave every alert equal weight, so a staffing shortfall CMS would care about looked like routine noise. Every alert now carries one of three tiers — Critical, Warning, Informational — with tabs to filter and a link to the report behind it. I considered letting administrators build their own filters and chose fixed tiers instead: a filter nobody remembers to set up can hide a compliance risk.","aip-alerts-before-after-v2.jpg","The same morning's alerts, before and after severity tiers. The 'before' is a recreation."),
  ("Decision 03 · The shell","Make embedded Power BI feel like part of the product","I drew four ways to frame the embedded reports and chose an icon sidebar, because an embedded report needs every pixel of width. The shell adds tabs, filters and a freshness label. Power BI takes 3 to 8 seconds to render, so we designed the loading states around that wait rather than pretending it isn't there.","aip-shell-options.jpg","Four shell options from the wireframes, drawn to scale, and the final shell. The dashed line marks the embedded Power BI report."),
  ("Decision 04 · Restraint","Leave most of Power BI's options unused","Complex filter chains, heavy tooltips and drillthrough on every chart all stayed out. Each omission made the reports easier to understand in testing.")],
 "gallery":[("aip-screen-alert-center.jpg","Apex Insights alert centre","Alert centre","Every alert shows its severity, tabs filter by tier, and cleared alerts go to history for compliance."),
            ("aip-screen-staffing-reports.jpg","Apex Insights staffing reports","Staffing reports","Favourite, subscribe or run on demand — the self-serve criterion, made concrete."),
            ("aip-screen-subscriptions.jpg","Apex Insights subscriptions","Subscriptions","Scheduled delivery with pause and resume, so the analyst is no longer the distribution mechanism.")],
  "impact":{"art":("aip-outcomes-scorecard.jpg","Results against the three criteria agreed with the client at kickoff, before any wireframes."),"h":"Design carried the pitch.",
  "p":["The prototype, not a deck, helped win a ~$100k engagement before a production product existed. At the pilot client, report turnaround went from 3+ days to same day, and five administrators self-reported roughly 60% less time to reach cross-system reports. All three kickoff criteria held."],
  "outs":[("~$100k","Engagement won from a prototype, pre-production"),
          ("3+ days → same day","Report turnaround at the pilot client"),
          ("~60%","Less time to reach cross-system reports")],
  "caveat":("Honest caveat","Participants reached critical alerts faster once tiers and report links were in place, but we never captured a timed baseline beforehand. The 60% figure is self-reported by five administrators — it isn't instrumented.")},
 "reflection":{"lessons":[
   ("Executives and analysts needed different views of the same product","I now map each audience's first question before designing shared navigation, and test the executive and analyst paths as separate tasks."),
   ("A prototype is a commercial instrument","Making 'wins a client commitment' an explicit design criterion changed both what we built and how early we built it.")],
  "diff":"Involve the economic buyer far earlier. We tested thoroughly with administrators and barely at all with the executives who would fund the tool. Next time, a monthly session with them from day one."}
},
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
    """Plain-text escape for attributes and <title>."""
    return html.escape(t, quote=True)

def strip_tags(t):
    import re
    return re.sub(r"<[^>]+>", "", t)

def art(spec, wide=True):
    """A process artefact: the picture that carries the claim."""
    if not spec:
        return ''
    f, cap = spec
    cls = 'art wide rv' if wide else 'art rv'
    return (f'  <figure class="{cls}"><img src="img/{f}" alt="{esc(cap)}"{dim(f)} '
            f'loading="lazy" decoding="async"><figcaption>{cap}</figcaption></figure>')


def chapter(idx, title, heading, inner):
    return (f'<section class="ch wrap" id="{idx[1]}">\n'
            f'  <div class="ch-head rv"><span class="idx">{idx[0]}</span>'
            f'<span class="ttl">{title}</span><h2>{heading}</h2></div>\n'
            f'{inner}\n</section>')

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
    A('<meta name="theme-color" content="#FCFCFD">')
    A(f'<meta property="og:title" content="{esc(c["name"])} — {esc(plain_title)}">')
    A('<link rel="icon" href="d-logo.svg">')
    A('<script>/* light is the default; the OS preference does not decide it. '
      'a stored choice from the toggle always wins. */'
      'try{var t=localStorage.getItem("dv26-theme");'
      'if(t)document.documentElement.setAttribute("data-theme",t);}catch(e){}</script>')
    A('<link rel="preconnect" href="https://fonts.googleapis.com">')
    A('<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>')
    A('<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter+Tight:ital,wght@0,300..700;1,400&family=Newsreader:ital,opsz,wght@1,6..72,400..500&family=JetBrains+Mono:wght@400;500&display=swap">')
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
    A('  <dl class="meta rv">' + ''.join(
        f'<div><dt>{k}</dt><dd>{v}</dd></div>' for k, v in c["meta"]) + '</dl>')
    A(f'  <figure class="chero-fig rv"><img src="img/{c["hero"][0]}" alt="{esc(c["hero"][1])}"'
      f'{dim(c["hero"][0])} loading="eager" decoding="async">'
      f'<figcaption>{c["herocap"]}</figcaption></figure>')
    A('</header>')

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

    # ── next / prev
    A('<nav class="nextnav wrap" aria-label="More work">')
    A(f'  <div><span class="lbl">Previous</span><a class="big" href="{prev["slug"]}.html">{prev["name"]}</a></div>')
    A(f'  <div class="r"><span class="lbl">Next case study</span><a class="big" href="{nxt["slug"]}.html">{nxt["name"]} {ARROW}</a></div>')
    A('</nav>')
    A('</main>')

    A('<footer>')
    A('<div class="wrap foot-in">'
      f'<span>&copy; 2026 Deep Vyas &mdash; {c["name"]} &middot; {c["client"]}</span>'
      '<a href="index.html#contact">Have a role in mind? &rarr;</a>'
      '<a href="#top">Back to top &uarr;</a>'
      '</div></footer>')
    A('<script src="js/system.js" defer></script>')
    A('</body>\n</html>')
    return "\n".join(out)


if __name__ == "__main__":
    here = os.path.dirname(os.path.abspath(__file__))
    n = len(CASES)
    for i, c in enumerate(CASES):
        page = render(c, CASES[(i - 1) % n], CASES[(i + 1) % n])
        path = os.path.join(here, c["slug"] + ".html")
        with open(path, "w", encoding="utf-8") as f:
            f.write(page)
        print(f"  ✓ {c['slug']}.html  ({len(page):,} bytes)")
    print(f"\n{n} case studies built.")
