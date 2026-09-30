# CS 112, Data Structures (Fall 2026)

Course website for CS 112, Introduction to Data Structures, at Calvin University.
Built with [Quarto](https://quarto.org).

## Local preview

```bash
quarto preview
```

## Build

```bash
quarto render
```

The site is deployed automatically to GitHub Pages on every push to `main`.
Make sure your GitHub Pages settings are set to deploy via **GitHub Actions**.

## Before pushing

A pre-push hook renders every page and refuses the push if one is broken. It is
versioned in `hooks/`, but git does not use a versioned hooks directory unless
it is told to, so **run this once per clone**:

    git config core.hooksPath hooks

To check by hand at any time:

    python3 check_pages.py

It needs pandoc, which Quarto ships. The hook skips quietly rather than blocking
if pandoc is missing, so a machine without it can still push.

`git push --no-verify` bypasses the hook. The check has been wrong zero times so
far and the front page has been broken once, so prefer fixing the page.
