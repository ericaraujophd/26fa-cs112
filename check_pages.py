#!/usr/bin/env python3
"""
check_pages.py - catch a broken page before it reaches the site.

Run it before pushing:

    python3 check_pages.py            # every .qmd in the site
    python3 check_pages.py index.qmd  # or just the ones you touched

WHY THIS EXISTS
---------------
On 2026-09-30 a generated block opened a ``` fence inside index.qmd's single
```{=html} region. That closed the region early and left a stray fence behind,
so everything below the hero rendered as literal text and the live site was
broken until somebody happened to look at it.

Nothing about the source looked wrong. The file parsed, the block was where it
belonged, and the mistake was only visible in the rendered output. So this
script renders, and then checks the result rather than the source.

WHAT IT CHECKS
--------------
  fences balance              an odd number of ``` lines means one is unclosed,
                              which is the failure above, seen at the source
  the page renders            pandoc parses it without an error
  no literal ``` survives     the reliable symptom of a fence gone wrong: raw
                              backticks in the HTML output
  no raw <div or <span text   HTML escaped into visible text, the other way a
                              raw block goes wrong
  markers are paired          THISWEEK and CHECKIN each need both ends, or
                              build_thisweek.py silently writes nothing
  local links resolve         an href to a file in the repo that is not there,
                              checked for .pdf, .qmd and .html targets

WHAT IT DOES NOT CHECK
----------------------
Quarto's own extensions. Pandoc is close enough to catch structural damage,
which is what this is for, and it is available without a Quarto install.
Callouts and shortcodes may parse differently; that is not what breaks pages.
"""

import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent

MARKER_PAIRS = [
    ("<!-- THISWEEK:START -->", "<!-- THISWEEK:END -->"),
    ("<!-- CHECKIN:START -->", "<!-- CHECKIN:END -->"),
]


def check_source(path, text):
    """The things visible without rendering."""
    problems = []

    fences = [ln for ln in text.split("\n") if ln.startswith("```")]
    if len(fences) % 2:
        problems.append(
            f"{len(fences)} lines start with ```, which is odd, so one fence "
            f"is never closed. This is what breaks a page.")

    for start, end in MARKER_PAIRS:
        if (start in text) != (end in text):
            problems.append(
                f"{start if start in text else end} appears without its pair")

    return problems


def check_rendered(path, html):
    """The things only the output shows."""
    problems = []

    if "```" in html:
        n = html.count("```")
        problems.append(
            f"{n} literal ``` in the rendered HTML: a fence was treated as text")

    # Raw HTML that got escaped instead of passed through. &lt;div is the tell.
    for needle in ("&lt;div", "&lt;span", "&lt;script", "&lt;style"):
        if needle in html:
            problems.append(
                f'"{needle}" in the rendered HTML: raw HTML was escaped into '
                f"visible text rather than passed through")
            break

    return problems


def check_links(path, html):
    """Local hrefs that point at nothing. Remote links are left alone."""
    problems = []
    base = path.parent

    for href in set(re.findall(r'href="([^"#?]+)"', html)):
        if href.startswith(("http://", "https://", "mailto:", "#", "data:")):
            continue
        if not href.endswith((".pdf", ".html", ".qmd", ".png", ".jpg", ".svg")):
            continue

        target = (base / href).resolve()
        if target.exists():
            continue
        # A .html link is written before Quarto renders the .qmd beside it.
        if href.endswith(".html") and target.with_suffix(".qmd").exists():
            continue
        problems.append(f"link to {href}, which is not in the repository")

    return problems


def check(path):
    if not path.exists():
        return [f"no such file: {path}"]
    text = path.read_text(encoding="utf-8")
    problems = check_source(path, text)

    render = subprocess.run(
        ["pandoc", "-f", "markdown", "-t", "html5", str(path)],
        capture_output=True, text=True)
    if render.returncode != 0:
        first = (render.stderr or "").strip().split("\n")[0]
        problems.append(f"pandoc could not render it: {first}")
        return problems

    problems += check_rendered(path, render.stdout)
    problems += check_links(path, render.stdout)
    return problems


def main():
    if len(sys.argv) > 1:
        pages = [Path(a).resolve() for a in sys.argv[1:]]
    else:
        pages = sorted(p for p in HERE.rglob("*.qmd")
                       if "_book" not in p.parts and "_site" not in p.parts)

    if subprocess.run(["which", "pandoc"], capture_output=True).returncode != 0:
        sys.exit("pandoc is not installed, so nothing can be rendered.\n"
                 "Quarto ships one: try PATH=\"$(dirname "
                 "$(dirname $(which quarto)))/bin/tools:$PATH\"")

    failed = False
    for page in pages:
        rel = page.relative_to(HERE) if HERE in page.parents else page.name
        problems = check(page)
        if problems:
            failed = True
            print(f"FAIL  {rel}")
            for p in problems:
                print(f"        {p}")
        else:
            print(f"ok    {rel}")

    if failed:
        print("\nDo not push. A page that renders wrong is live until somebody "
              "notices.")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
