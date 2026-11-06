#!/usr/bin/env python3
"""
build-ask-index.py — what the drawer knows about the rest of the site.

    python3 build-ask-index.py

The drawer's written answers live in each page's <ul class="ask-q">, and they
only ever covered the page they sit on. Ask "who is Deep" on a case study and
there was nothing to match, although the answer is sitting in #about on the
landing page.

So this walks every page that is linked from the site, splits each into its
sections, and writes ask-index.json: for every section, the page it is on,
its anchor, its heading, and its sentences. The drawer loads that file the
first time someone types, and when none of the written answers fit, it
answers out of the section that does.

Nothing is written here. Every sentence in the index is a sentence already
on a page, and the drawer shows them as they are, with a link to the section
they came from. That is the whole point: a question answered out of this
file cannot say anything the site does not already say.

Re-run it after editing any page's copy.
"""
import html as _html
import json
import os
import re
import datetime

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "ask-index.json")

# Linked from the nav or from #work. The orphans (aip, teleconsult, the
# pettrackr drafts) are left out on purpose: they are not reachable from the
# site, and the drawer should not be the thing that reveals them.
PAGES = [
    ("index.html",      "Deep Vyas"),
    ("apex.html",       "Apex Insights"),
    ("igel.html",       "IGEL Licence Portal"),
    ("myaster.html",    "myAster"),
    ("pettrackr.html",  "PetTrackr"),
    ("flintlink.html",  "Flint-Link"),
]

# Chrome, not content: the drawer itself, the nav, the footer, the section
# rail, the launcher. Indexing the drawer would feed it its own answers back.
DROP = [
    r'<script\b.*?</script\s*>',
    r'<style\b.*?</style\s*>',
    r'<svg\b.*?</svg\s*>',
    r'<noscript\b.*?</noscript\s*>',
    r'<aside\b[^>]*class="[^"]*\bask\b[^"]*".*?</aside\s*>',
    r'<header\b.*?</header\s*>',
    r'<footer\b.*?</footer\s*>',
    r'<nav\b.*?</nav\s*>',
    r'<[^>]*class="[^"]*\b(srail|avbtn|back|skip)\b[^"]*"[^>]*>.*?</\w+\s*>',
]

# The tag pills over a case hero — "Healthcare operations · B2B desktop web
# · Power BI · Skilled nursing" — read as gibberish inside a sentence, but
# they are the words a visitor searches a portfolio with. So they come out
# of the prose and go into the section's keywords, which are matched on and
# never read back.
CHIPS = re.compile(r'<div\b[^>]*class="[^"]*\b(?:chips|kick)\b[^"]*"[^>]*>(.*?)</div\s*>',
                   re.S | re.I)

BLOCK = re.compile(
    r'</?(p|div|section|article|li|ul|ol|h[1-6]|td|tr|th|table|figcaption|dt|dd|blockquote)\b[^>]*>',
    re.I)
# a <br> breaks a line, not a sentence: "An engineer by training,<br>working
# in UI/UX since 2014." is one sentence and has to stay one
BR = re.compile(r'<br\b[^>]*>', re.I)

# the eyebrow over every section heading — "03 About" on the landing page,
# "02 · The problem" on a case page. A label, not a sentence.
EYEBROW = re.compile(r'^\d{1,2}(?!\d)\s*(?:·|\.|—|-)?\s*\S.{0,44}$')


def text_of(frag):
    """Tags out, entities back, whitespace collapsed — with block tags left
    as newlines so sentences from different paragraphs do not run together."""
    # a block tag ends a line; a newline in the source does not, or a
    # headline set over three source lines comes back as three sentences
    frag = BR.sub(" ", frag)
    frag = BLOCK.sub("\x00", frag)
    frag = re.sub(r'<[^>]+>', " ", frag)
    frag = _html.unescape(frag)
    # the copy uses word joiners and non-breaking hyphens; a reader should
    # not meet them as question marks in a chat bubble
    frag = frag.replace("⁠", "").replace("‑", "-").replace(" ", " ")
    lines = [re.sub(r'\s+', " ", l).strip() for l in frag.split("\x00")]
    return "\n".join(l for l in lines if l)


def sentences(txt):
    out = []
    for line in txt.split("\n"):
        # a full stop followed by a space and a capital, or the end of a line
        parts = re.split(r'(?<=[.!?…])\s+(?=[A-Z“(])', line)
        for p in parts:
            p = p.strip()
            if len(p) < 2 or p.isdigit() or EYEBROW.match(p):
                continue
            out.append(p)
    return out


def strip_chrome(doc):
    for pat in DROP:
        doc = re.sub(pat, " ", doc, flags=re.S | re.I)
    return doc


def unnumber(h):
    """Drop a leading section number — but never the 15 of "150+"."""
    return re.sub(r'^\s*\d{1,2}(?!\d)\s*(?:·|\.|—|-)?\s+', "", h).strip()


def heading_of(frag):
    """What to call this section in a chat reply. The landing page keeps the
    name in its eyebrow — <p class="lab"><span class="n">03</span>About</p> —
    and puts a statement in the h2; a case page keeps both in the eyebrow."""
    m = re.search(r'<p\b[^>]*class="[^"]*\blab\b[^"]*"[^>]*>(.*?)</p\s*>', frag, re.S | re.I)
    if m:
        lab = re.sub(r'<span\b[^>]*class="[^"]*\bn\b[^"]*"[^>]*>.*?</span\s*>', " ",
                     m.group(1), flags=re.S | re.I)
        lab = text_of(lab).replace("\n", " ").strip()
        if lab:
            return unnumber(lab)
    m = re.search(r'<h[1-6]\b[^>]*>(.*?)</h[1-6]\s*>', frag, re.S | re.I)
    if not m:
        return ""
    return unnumber(text_of(m.group(1)).replace("\n", " ").strip())


def sections(doc):
    """Every <section id="..."> that carries prose, in page order. Sections
    nest on some pages, so an outer one keeps only the text its children do
    not already claim."""
    found = []
    for m in re.finditer(r'<section\b([^>]*)>', doc, re.I):
        attrs = m.group(1)
        idm = re.search(r'\bid="([a-z0-9][\w-]*)"', attrs, re.I)
        if idm:
            sid = idm.group(1)
        elif re.search(r'class="[^"]*\bhero\b', attrs, re.I):
            # the hero carries the one-line answer to "what is this?" and
            # has no id, because nothing ever needed to link to the top
            sid = ""
        else:
            continue
        start = m.start()
        # walk to the matching close
        depth, i = 0, start
        for t in re.finditer(r'<(/?)section\b[^>]*>', doc[start:], re.I):
            depth += -1 if t.group(1) else 1
            if depth == 0:
                i = start + t.end()
                break
        else:
            i = len(doc)
        found.append((sid, start, i, doc[start:i]))

    out = []
    for sid, a, b, frag in found:
        inner = [(x, y) for (_, x, y, _) in found if x > a and y <= b]
        body = frag
        for x, y in sorted(inner, reverse=True):
            body = body[: x - a] + " \n " + body[y - a:]
        tags = " ".join(text_of(m.group(1)).replace("\n", " ")
                        for m in CHIPS.finditer(body)).strip()
        body = CHIPS.sub(" \n ", body)
        out.append((sid, heading_of(frag), text_of(body), tags))
    return out


def main():
    pages, secs = [], []
    for pi, (fn, label) in enumerate(PAGES):
        path = os.path.join(HERE, fn)
        if not os.path.exists(path):
            print("  skipped (missing): %s" % fn)
            continue
        doc = strip_chrome(io_read(path))
        pages.append({"u": fn, "t": label})
        n = 0
        for sid, head, body, tags in sections(doc):
            sents = sentences(body)
            # a heading and three words is a divider, not an answer
            if sum(len(s) for s in sents) < 140:
                continue
            rec = {
                "p": len(pages) - 1,
                "a": sid,
                "h": head or (sid.replace("-", " ") if sid else "Overview"),
                "s": sents,
            }
            if tags:
                rec["k"] = tags
            secs.append(rec)
            n += 1
        print("  %-16s %2d sections" % (fn, n))

    data = {
        "built": datetime.date.today().isoformat(),
        "pages": pages,
        "secs": secs,
    }
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, separators=(",", ":"))

    size = os.path.getsize(OUT)
    words = sum(len(" ".join(s["s"]).split()) for s in secs)
    print("\nask-index.json  %d sections, %d words, %.0f KB"
          % (len(secs), words, size / 1024.0))


def io_read(p):
    with open(p, encoding="utf-8") as f:
        return f.read()


if __name__ == "__main__":
    main()
