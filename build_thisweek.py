#!/usr/bin/env python3
"""
build_thisweek.py - the "this week" block on the front page.

WHAT IT DOES
------------
Reads ``course/planning/course-map.yml``, works out what each week of the
semester actually has on the site (a deck, an assignment page, one outline per
class meeting), and writes the result into ``website/index.qmd`` between two
markers. Run it whenever the schedule or the materials change:

    python3 build_thisweek.py

IT SELF-UPDATES, WITHOUT A REBUILD
----------------------------------
The block carries **every** week as inline JSON and picks the right one in the
browser from the visitor's own clock. That is the whole design decision, and the
alternative is worse: choosing the week at build time would mean the front page
silently showing last week's material until the site is rebuilt, and a site that
is wrong between Friday and the next build is worse than no block at all.

The cost is that the data is only as fresh as the last run of this script, so a
new deck or a new outline still needs a rebuild to appear. What never goes stale
is *which week is showing*, which is the part nobody would remember to fix.

WHAT IT DOES WHEN TODAY IS NOT IN A TEACHING WEEK
-------------------------------------------------
- before the semester: shows the first week, labelled as starting soon
- in a gap, such as a break: shows the next week that starts
- after the last week: shows the last week

There is always something on the page. A block that renders empty for a week in
October reads as a broken site.

WHAT IT CHECKS BEFORE LINKING
-----------------------------
Only files that exist are linked, so a week with no deck yet shows no deck link
rather than a 404. Everything is checked on disk at build time:

    website/slides/weekNN.html          the deck
    website/slides/weekNN.pdf           its PDF, and -bw for the print version
    website/content/assignments/aNN.qmd the assignment page, one or two a week
    website/outlines/CS112-outline-YYYY-MM-DD.pdf   the outline, per meeting

NO CODE FENCES IN THE GENERATED BLOCKS
--------------------------------------
index.qmd is one long ``` ```{=html} ``` region running from near the top of the
file to the bottom. A generated block that opens its own fence closes that
region early and leaves a stray fence behind, and everything after it renders as
literal text. That is exactly what happened on 2026-09-30, and the live site was
broken until it was found.

So these blocks emit raw HTML and nothing else. Inside the raw region on
index.qmd that is already correct, and on checkins.qmd, where the markers sit in
ordinary markdown, Quarto passes block-level HTML through untouched.

MARKERS
-------
The block replaces whatever sits between these two lines in index.qmd, so the
script can be run repeatedly:

    <!-- THISWEEK:START -->
    <!-- THISWEEK:END -->

If the markers are missing, the script says so and changes nothing rather than
guessing where the block belongs.
"""

import json
import os
import re
import sys
from datetime import date
from pathlib import Path

import yaml

HERE = Path(__file__).resolve().parent          # website/
REPO = HERE.parent                              # the project root
COURSE_MAP = REPO / "course" / "planning" / "course-map.yml"
INDEX = HERE / "index.qmd"

START_MARKER = "<!-- THISWEEK:START -->"
END_MARKER = "<!-- THISWEEK:END -->"

CHECKIN_CONFIG = HERE / "checkin-windows.yml"
CHECKINS_PAGE = HERE / "content" / "checkins.qmd"
CHECKIN_START = "<!-- CHECKIN:START -->"
CHECKIN_END = "<!-- CHECKIN:END -->"

MONTHS = ["January", "February", "March", "April", "May", "June", "July",
          "August", "September", "October", "November", "December"]


def iso(d):
    """YAML gives us a date object for some fields and a string for others."""
    return d.isoformat() if hasattr(d, "isoformat") else str(d)


def pretty(d):
    """2026-09-30 -> 30 September. Short, because it sits in a small card."""
    y, m, day = (int(x) for x in iso(d).split("-"))
    return f"{day} {MONTHS[m - 1]}"


def assignment_title(code):
    """Pull the title out of an assignment page's YAML front matter."""
    path = HERE / "content" / "assignments" / f"{code}.qmd"
    if not path.exists():
        return None
    head = path.read_text(encoding="utf-8")[:600]
    m = re.search(r'^title:\s*"?(.+?)"?\s*$', head, re.M)
    if not m:
        return None
    # Pages are titled "Assignment 05: Telemetry" and the chip already says
    # a05, so the prefix would be said twice.
    return re.sub(r'^Assignment\s*\d+\s*[:.-]\s*', '', m.group(1)).strip()


def collect():
    """One entry per teaching week, carrying only what actually exists."""
    data = yaml.safe_load(COURSE_MAP.read_text(encoding="utf-8"))
    weeks = data.get("weeks") or []
    out = []

    for w in weeks:
        n = w.get("n")
        if n is None:
            continue
        nn = f"{int(n):02d}"

        entry = {
            "n": int(n),
            "label": f"Week {int(n)}",
            "topic": w.get("topic") or "",
            "start": iso(w.get("start")),
            "end": iso(w.get("end")),
            "dates": f"{pretty(w.get('start'))} to {pretty(w.get('end'))}",
            "slides": None,
            "assignments": [],
            "outlines": [],
        }

        # --- the deck, and its two PDFs if they were built ------------------
        if (HERE / "slides" / f"week{nn}.html").exists():
            deck = {"html": f"slides/week{nn}.html?fs=1"}
            if (HERE / "slides" / f"week{nn}.pdf").exists():
                deck["pdf"] = f"slides/week{nn}.pdf"
            if (HERE / "slides" / f"week{nn}-bw.pdf").exists():
                deck["bw"] = f"slides/week{nn}-bw.pdf"
            entry["slides"] = deck

        # --- the assignment pages -------------------------------------------
        # A week may carry none, one, or two. The map writes a bare string for
        # one and a list for two, and week 12 writes the string "None", so all
        # three shapes have to be flattened before anything else looks at it.
        raw = w.get("assignment")
        codes = raw if isinstance(raw, list) else [raw]
        for code in codes:
            if not code or str(code).lower() == "none":
                continue
            if not (HERE / "content" / "assignments" / f"{code}.qmd").exists():
                continue
            entry["assignments"].append({
                "code": code,
                "title": assignment_title(code) or code,
                "href": f"content/assignments/{code}.html",
            })

        # --- one outline per class meeting, in whichever form exists --------
        for lec in w.get("lectures") or []:
            d = iso(lec.get("date"))
            linear = HERE / "outlines" / f"CS112-outline-{d}.pdf"
            booklet = HERE / "outlines" / f"CS112-outline-{d}-booklet.pdf"
            if not linear.exists():
                continue
            item = {
                "day": (lec.get("day") or "")[:3],
                "date": pretty(d),
                "read": f"outlines/CS112-outline-{d}.pdf",
            }
            if booklet.exists():
                item["booklet"] = f"outlines/CS112-outline-{d}-booklet.pdf"
            entry["outlines"].append(item)

        out.append(entry)

    return out


def checkin_windows():
    """The booking windows, as the browser will need them.

    A window with no URL yet is kept rather than dropped. A button that
    disappears tells a student nothing, and "#" as a link is exactly how the
    front page ended up with a dead button.
    """
    if not CHECKIN_CONFIG.exists():
        return []
    data = yaml.safe_load(CHECKIN_CONFIG.read_text(encoding="utf-8")) or {}
    out = []
    for w in data.get("windows") or []:
        out.append({
            "n": int(w["n"]),
            "opens": iso(w["opens"]),
            "reference": iso(w["reference"]),
            "closes": iso(w["closes"]),
            "opensLabel": pretty(w["opens"]),
            "referenceLabel": pretty(w["reference"]),
            "closesLabel": pretty(w["closes"]),
            "url": w.get("url") or None,
        })
    return out


CHECKIN_SCRIPT = """
<script>
// One button per check-in window, each showing its own state, worked out in the
// browser from the visitor's clock. Nothing here is decided at build time, so
// the row stops being right only when checkin-windows.yml is wrong.
(function () {
  var WINDOWS = %s;

  function todayISO() {
    var d = new Date();
    return d.getFullYear() + '-' +
           String(d.getMonth() + 1).padStart(2, '0') + '-' +
           String(d.getDate()).padStart(2, '0');
  }

  var LIVE = 'background:#6E1C2E;color:#fff;border-color:#6E1C2E;';
  var MUTED = 'opacity:.55;cursor:default;';

  function button(w, today, fallback) {
    // Open, and the link exists. The only one a student can act on.
    if (w.opens <= today && today <= w.closes && w.url) {
      return '<a href="' + w.url + '" target="_blank" rel="noopener" ' +
             'class="btn btn-sm" style="' + LIVE + '" ' +
             'title="Assessed against ' + w.referenceLabel +
             '. Closes ' + w.closesLabel + '.">' +
             'Book Window ' + w.n + '</a>';
    }

    // Everything else is shown anyway, greyed, so a student can see the shape
    // of the semester rather than wondering what happened to the other windows.
    var label;
    if (today > w.closes)        label = 'Window ' + w.n + ' closed';
    else if (today < w.opens)    label = 'Window ' + w.n + ' opens ' + w.opensLabel;
    else                         label = 'Window ' + w.n + ' link coming';

    return '<a href="' + fallback + '" class="btn btn-sm btn-outline-secondary" ' +
           'style="' + MUTED + '" title="Assessed against ' + w.referenceLabel +
           '.">' + label + '</a>';
  }

  function render() {
    var host = document.getElementById('checkin-book');
    if (!host) return;
    var today = todayISO();
    var fallback = host.getAttribute('data-checkins-href') || 'content/checkins.html';
    host.innerHTML = WINDOWS.map(function (w) {
      return button(w, today, fallback);
    }).join(' ');
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', render);
  } else {
    render();
  }
})();
</script>
"""


def checkin_block(windows, checkins_href):
    """The row of buttons, one per window.

    ``checkins_href`` is where a button with nothing to link to should send a
    student, and it differs per page, so it is written into the span rather
    than hard-coded in the script. Never "#": that is how the front page ended
    up with a button that silently did nothing.
    """
    payload = json.dumps(windows, separators=(",", ":"))
    return "\n".join([
        CHECKIN_START,
        f'<span id="checkin-book" data-checkins-href="{checkins_href}">'
        f'<a href="{checkins_href}" class="btn btn-sm btn-outline-secondary">'
        f'Book a check-in</a></span>',
        (CHECKIN_SCRIPT % payload).strip(),
        CHECKIN_END,
    ])


CSS = """
<style>
/* ── This week ─────────────────────────────────────────────── */
.tw-card {
  border: 1px solid #e3e3e3;
  border-left: 4px solid #6E1C2E;
  border-radius: var(--bs-border-radius-lg, .5rem);
  padding: 1.1rem 1.3rem 1.2rem;
  margin-bottom: 1.5rem;
  background: #fff;
}
.tw-head {
  display: flex; flex-wrap: wrap; align-items: baseline; gap: .6rem;
  margin-bottom: .2rem;
}
.tw-week { font-weight: 700; color: #6E1C2E; font-size: 1.05rem; }
.tw-dates { font-size: .8rem; opacity: .6; }
.tw-topic { font-size: .95rem; margin-bottom: .9rem; }
.tw-note {
  font-size: .8rem; opacity: .7; margin-bottom: .9rem; font-style: italic;
}
/* THREE COLUMNS OR ONE, never two-and-a-widow. Measured from the card rather
   than the window, and in rem, so a bigger text size collapses it the same way
   a narrower window does. */
.tw-card { container-type: inline-size; container-name: twcard; }
.tw-cols {
  display: grid;
  grid-template-columns: 1fr;
  gap: 1rem;
}
@container twcard (min-width: 42rem) {
  .tw-cols { grid-template-columns: repeat(3, 1fr); }
}
@supports not (container-type: inline-size) {
  .tw-cols {
    grid-template-columns: repeat(auto-fit, minmax(min(14rem, 100%), 1fr));
  }
}
.tw-col { min-width: 0; }
.tw-col-label {
  font-size: .7rem; text-transform: uppercase; letter-spacing: .07em;
  opacity: .55; margin-bottom: .35rem;
}
.tw-col a { text-decoration: none; }
.tw-col a:hover { text-decoration: underline; }
/* A date and its links are one line or nothing. */
.tw-line { font-size: .875rem; margin-bottom: .2rem; white-space: nowrap; }
.tw-day { display: inline-block; min-width: 2.6rem; opacity: .65; }
.tw-sep { opacity: .35; margin: 0 .35rem; }
.tw-none { font-size: .85rem; opacity: .45; }
.tw-assign {
  display: inline-block; background: #fdf8ec; border: 1px solid #C49A2C;
  border-radius: .3rem; padding: .15rem .5rem; font-size: .875rem;
}
/* ── Dark mode ───────────────────────────────────────────────
   THE TRIGGER IS .quarto-dark, NOT prefers-color-scheme. This block used the
   media query, which only fires when the READER'S SYSTEM is dark. The site's
   dark mode is a toggle in the display panel, and Quarto signals it by putting
   .quarto-dark on the body. On a light system with dark chosen, the media
   query never matched: the card kept background #fff while the theme switched
   the text to near-white, so the whole week block went invisible at a measured
   1.05:1. Reported 2026-10-05.

   Maroon goes gold on dark, which is what every other accent in custom.css
   already does: #6E1C2E on the card below measures 1.28:1, #C49A2C measures
   5.47:1 against the same surface.

   The card keeps a surface of its own rather than going transparent. It is a
   card; it should read as one in both themes.                            */
.quarto-dark .tw-card {
  background: #2a2a2a;
  border-color: #444;
  border-left-color: var(--calvin-gold, #C49A2C);
}
.quarto-dark .tw-week { color: var(--calvin-gold, #C49A2C); }
/* The pill is a link, so custom.css paints it --calvin-gold. Over a 12% gold
   tint on #2a2a2a that measures 4.26:1, just under the 4.5 AA floor, so the
   pill gets an opaque surface and a lighter gold of its own: 7.72:1. The hover
   rule is here because .quarto-dark a:hover is more specific than a bare class
   pair and would otherwise drop the text to --calvin-gold-dark at 3.17:1. */
.quarto-dark .tw-assign {
  background: #3a3222;
  border-color: var(--calvin-gold, #C49A2C);
  color: #e8c76a;
}
.quarto-dark .tw-assign:hover { color: #f4dc9a; }
</style>
"""

SCRIPT = """
<script>
// The whole semester ships with the page. Which week to show is decided here,
// in the visitor's browser, from their own clock, so the front page is right on
// a Monday morning without anyone having rebuilt the site.
(function () {
  var WEEKS = %s;

  function todayISO() {
    var d = new Date();
    return d.getFullYear() + '-' +
           String(d.getMonth() + 1).padStart(2, '0') + '-' +
           String(d.getDate()).padStart(2, '0');
  }

  // Current week, else the next one to start, else the last one. There is
  // always something to show; an empty block reads as a broken page.
  function pick(today) {
    for (var i = 0; i < WEEKS.length; i++) {
      if (WEEKS[i].start <= today && today <= WEEKS[i].end) {
        return { week: WEEKS[i], state: 'current' };
      }
    }
    for (var j = 0; j < WEEKS.length; j++) {
      if (WEEKS[j].start > today) {
        return { week: WEEKS[j], state: 'upcoming' };
      }
    }
    return { week: WEEKS[WEEKS.length - 1], state: 'past' };
  }

  function esc(s) {
    return String(s).replace(/[&<>"]/g, function (c) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c];
    });
  }

  function column(label, inner) {
    return '<div class="tw-col"><div class="tw-col-label">' + label +
           '</div>' + (inner || '<div class="tw-none">nothing posted yet</div>') +
           '</div>';
  }

  function render() {
    var host = document.getElementById('this-week');
    if (!host) return;
    var chosen = pick(todayISO());
    var w = chosen.week;

    var slides = '';
    if (w.slides) {
      var bits = ['<a href="' + w.slides.html + '" target="_blank" rel="noopener">view online</a>'];
      if (w.slides.pdf) bits.push('<a href="' + w.slides.pdf + '">PDF</a>');
      if (w.slides.bw) bits.push('<a href="' + w.slides.bw + '">print</a>');
      slides = '<div class="tw-line">' +
               bits.join('<span class="tw-sep">·</span>') + '</div>';
    }

    var assign = w.assignments.map(function (a) {
      return '<div class="tw-line"><a class="tw-assign" href="' + a.href +
             '">' + esc(a.code) + ': ' + esc(a.title) + '</a></div>';
    }).join('');

    var outlines = w.outlines.map(function (o) {
      var line = '<div class="tw-line"><span class="tw-day">' + esc(o.day) +
                 '</span><a href="' + o.read + '">' + esc(o.date) + '</a>';
      if (o.booklet) {
        line += '<span class="tw-sep">·</span><a href="' + o.booklet +
                '">booklet</a>';
      }
      return line + '</div>';
    }).join('');

    var note = '';
    if (chosen.state === 'upcoming') note = 'Starting soon.';
    if (chosen.state === 'past') note = 'The last week of the semester.';

    host.innerHTML =
      '<div class="tw-head"><span class="tw-week">' + esc(w.label) +
      '</span><span class="tw-dates">' + esc(w.dates) + '</span></div>' +
      '<div class="tw-topic">' + esc(w.topic) + '</div>' +
      (note ? '<div class="tw-note">' + note + '</div>' : '') +
      '<div class="tw-cols">' +
        column('Slides', slides) +
        column('Assignment', assign) +
        column('Class outlines', outlines) +
      '</div>';
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', render);
  } else {
    render();
  }
})();
</script>
"""


def block(weeks):
    payload = json.dumps(weeks, separators=(",", ":"))
    return "\n".join([
        START_MARKER,
        CSS.strip(),
        # The container carries a plain-text fallback, so a visitor with no
        # JavaScript is pointed at the schedule rather than shown an empty box.
        '<div class="tw-card" id="this-week">',
        '  <div class="tw-topic">This week\'s material is on the '
        '<a href="content/schedule.html">schedule</a>.</div>',
        '</div>',
        (SCRIPT % payload).strip(),
        END_MARKER,
    ])


def main():
    if not COURSE_MAP.exists():
        sys.exit(f"cannot find {COURSE_MAP}")
    if not INDEX.exists():
        sys.exit(f"cannot find {INDEX}")

    weeks = collect()
    if not weeks:
        sys.exit("no weeks found in course-map.yml")

    text = INDEX.read_text(encoding="utf-8")
    if START_MARKER not in text or END_MARKER not in text:
        sys.exit(
            f"{INDEX.name} has no {START_MARKER} / {END_MARKER} pair.\n"
            f"Add both lines where the block belongs, then run this again.")

    new = re.sub(
        re.escape(START_MARKER) + r".*?" + re.escape(END_MARKER),
        lambda _: block(weeks),
        text, flags=re.S)

    windows = checkin_windows()

    # The same row of buttons goes on both pages, so there is one place to edit
    # when a window's link is created. Each page needs its own fallback link,
    # because "the check-ins page" is a different path from each of them.
    targets = [
        (INDEX, new, "content/checkins.html"),
        (CHECKINS_PAGE, None, "checkins.html#how-to-book"),
    ]
    for path, pending, href in targets:
        if path is INDEX:
            body = pending
        elif path.exists():
            body = path.read_text(encoding="utf-8")
        else:
            continue

        if windows and CHECKIN_START in body and CHECKIN_END in body:
            body = re.sub(
                re.escape(CHECKIN_START) + r".*?" + re.escape(CHECKIN_END),
                lambda _: checkin_block(windows, href),
                body, flags=re.S)
            print(f"  booking buttons written into {path.name}")
        elif windows and path is not INDEX:
            print(f"  note: {path.name} has no {CHECKIN_START} / "
                  f"{CHECKIN_END} pair, so it was left alone")

        path.write_text(body, encoding="utf-8")

    today = date.today().isoformat()
    print(f"wrote the this-week block into {INDEX.name}")
    for w in windows:
        state = ("open" if w["opens"] <= today <= w["closes"]
                 else "not yet" if w["opens"] > today else "closed")
        print(f"  check-in window {w['n']}  {state:<8}"
              f"{'link published' if w['url'] else 'NO LINK YET'}")
    print(f"  {len(weeks)} weeks embedded")
    for w in weeks:
        here = " <- today" if w["start"] <= today <= w["end"] else ""
        print(f"  week {w['n']:>2}  "
              f"deck {'yes' if w['slides'] else ' no'}  "
              f"assignments {','.join(a['code'] for a in w['assignments']) or 'none':<9}"
              f"outlines {len(w['outlines'])}{here}")


if __name__ == "__main__":
    main()
