#!/usr/bin/env python3
"""
layout_audit.py - render the front page at many sizes and report what breaks.

Builds the page with pandoc, wraps it in a harness that reproduces the parts of
the real site that affect layout (Quarto's body font size, the data-fontsize
scale from custom.css, a Bootstrap-ish set of variables), then loads it in a
headless browser at each viewport width and each of the three text sizes and
measures the DOM.

WHAT IT REPORTS, all of it measured rather than eyeballed:

  overflow-x        the page is wider than the window, so it scrolls sideways
  spills            an element sticks out past its container
  wrapped           a line that should be one line has become two, found by
                    comparing the element's height against one line of its own
                    computed line-height

The last one is the interesting one, and it is how "my email breaks" turns from
an impression into a row in a table.
"""

import json
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SITE = Path("/mnt/user-data/uploads/26FA-CS112/website")
OUT = HERE / "audit"
CHROME = "/opt/pw-browsers/chromium-1194/chrome-linux/chrome"

# Real devices, roughly: small phone, large phone, tablet, laptop, desktop.
WIDTHS = [360, 414, 768, 1024, 1280, 1600]
SIZES = ["small", "medium", "large"]

# Elements that are meant to sit on one line. If one of these wraps, the page
# looks broken even though nothing overflows.
ONE_LINERS = [
    ".instructor-detail",
    ".tw-line",
    ".day-time",
    ".day-what",
    ".tw-dates",
    ".sched-room",
]

HARNESS_HEAD = """
<style>
/* Quarto's own body rule, which custom.css sets. Without it every measurement
   is taken at the wrong scale. */
body { font-size: 1.1rem; }
html[data-fontsize="medium"] { font-size: 112.5%; }
html[data-fontsize="large"]  { font-size: 125%; }

/* Enough of Bootstrap for the layout to behave: the variables the page reads,
   and the .btn box model. Colours do not affect geometry. */
:root {
  --bs-body-bg: #fff;
  --bs-border-color: #dee2e6;
  --bs-secondary-color: #6c757d;
  --bs-secondary-bg: #f1f3f5;
  --bs-border-radius-lg: .5rem;
  --calvin-maroon: #6E1C2E;
  --calvin-gold: #C49A2C;
}
* { box-sizing: border-box; }
body {
  font-family: -apple-system, "Helvetica Neue", Helvetica, Arial, sans-serif;
  margin: 0;
  padding: 1rem;
  color: #212529;
  line-height: 1.5;
}
/* Quarto's content column, which is what the page actually sits in. */
main { max-width: 1400px; margin: 0 auto; }
.btn {
  display: inline-block;
  padding: .375rem .75rem;
  font-size: 1rem;
  border: 1px solid transparent;
  border-radius: .375rem;
  text-decoration: none;
  line-height: 1.5;
}
.btn-sm { padding: .25rem .5rem; font-size: .875rem; }
a { color: #0d6efd; }
</style>
"""

PROBE = """
<script>
window.__audit = function () {
  var report = { overflowX: 0, spills: [], wrapped: [] };

  var de = document.documentElement;
  report.overflowX = Math.max(0, de.scrollWidth - de.clientWidth);

  function label(el) {
    var t = (el.textContent || '').trim().replace(/\\s+/g, ' ');
    return (el.className ? '.' + String(el.className).split(' ')[0] : el.tagName)
           + ' "' + t.slice(0, 44) + '"';
  }

  // Something sticking out of its parent, by more than a rounding error.
  document.querySelectorAll('body *').forEach(function (el) {
    var p = el.parentElement;
    if (!p || p === document.body) return;
    // script and style are not painted; measuring them is noise.
    if (/^(SCRIPT|STYLE|META|LINK)$/.test(el.tagName)) return;
    var a = el.getBoundingClientRect(), b = p.getBoundingClientRect();
    if (b.width === 0) return;
    var over = Math.max(a.right - b.right, b.left - a.left);
    if (over > 1.5) report.spills.push({ el: label(el), by: Math.round(over) });
  });

  // A one-line element that is now taller than one line of its own text.
  %ONE_LINERS%.forEach(function (sel) {
    document.querySelectorAll(sel).forEach(function (el) {
      var cs = getComputedStyle(el);
      var lh = parseFloat(cs.lineHeight);
      if (!lh || isNaN(lh)) lh = parseFloat(cs.fontSize) * 1.5;
      var pad = parseFloat(cs.paddingTop) + parseFloat(cs.paddingBottom);
      var lines = Math.round((el.getBoundingClientRect().height - pad) / lh);
      if (lines > 1) report.wrapped.push({ el: label(el), lines: lines });
    });
  });

  return report;
};
</script>
"""


def build_page():
    OUT.mkdir(exist_ok=True)
    html = subprocess.run(
        ["pandoc", "-f", "markdown", "-t", "html5", str(SITE / "index.qmd")],
        capture_output=True, text=True, check=True).stdout
    custom = (SITE / "custom.css").read_text(encoding="utf-8")
    return html, custom


def harness(body, custom, size):
    probe = PROBE.replace("%ONE_LINERS%", json.dumps(ONE_LINERS))
    return (f'<!doctype html><html data-fontsize="{size}"><head>'
            f'<meta charset="utf-8">'
            f'<style>{custom}</style>'
            f'{HARNESS_HEAD}{probe}</head>'
            f'<body><main>{body}</main></body></html>')


def measure(path, width):
    """Load the page at one width and pull the report back out."""
    script = f"""
        const {{ chromium }} = require('playwright');
        (async () => {{
          const b = await chromium.launch();
          const p = await b.newPage({{ viewport: {{ width: {width}, height: 900 }} }});
          await p.goto('file://{path}');
          await p.waitForTimeout(250);
          const r = await p.evaluate(() => window.__audit());
          console.log(JSON.stringify(r));
          await b.close();
        }})();
    """
    js = OUT / "probe.js"
    js.write_text(script, encoding="utf-8")
    res = subprocess.run(["node", str(js)], capture_output=True, text=True)
    if res.returncode != 0:
        return {"error": (res.stderr or "").strip().split("\n")[-1]}
    return json.loads(res.stdout.strip().split("\n")[-1])


def main():
    body, custom = build_page()
    rows = []
    for size in SIZES:
        page = OUT / f"page-{size}.html"
        page.write_text(harness(body, custom, size), encoding="utf-8")
        for width in WIDTHS:
            r = measure(page, width)
            rows.append((size, width, r))

    worst = 0
    print(f"{'text':<8}{'width':>6}  {'scroll':>6}  {'spills':>6}  wrapped")
    print("-" * 78)
    for size, width, r in rows:
        if "error" in r:
            print(f"{size:<8}{width:>6}  ERROR: {r['error']}")
            continue
        wrapped = r["wrapped"]
        worst = max(worst, len(wrapped) + len(r["spills"]) + (r["overflowX"] > 0))
        summary = ", ".join(sorted({w["el"].split(' "')[0] for w in wrapped})) or "-"
        print(f"{size:<8}{width:>6}  {r['overflowX']:>6}  {len(r['spills']):>6}  {summary}")

    print()
    print("DETAIL, elements sticking out of their container")
    seen_s = set()
    for size, width, r in rows:
        for sp in r.get("spills", []):
            if sp["el"] in seen_s:
                continue
            seen_s.add(sp["el"])
            print(f"  {size:<7}{width:>5}  by {sp['by']}px  {sp['el']}")

    print()
    print("DETAIL, the lines that wrapped")
    seen = set()
    for size, width, r in rows:
        for w in r.get("wrapped", []):
            key = (w["el"], w["lines"])
            if key in seen:
                continue
            seen.add(key)
            print(f"  {size:<7}{width:>5}  {w['lines']} lines  {w['el']}")

    sys.exit(1 if worst else 0)


if __name__ == "__main__":
    main()
