#!/usr/bin/env python3
"""
Lightweight source fetcher for Nyāya dataset research notes.

Usage (Windows PowerShell):
  python nyaya/Datasets/scripts/fetch_source.py --url <URL> --provider sep --slug speech-acts \
    --outdir nyaya/Datasets/sources/sep

Notes
- Saves a note file with metadata header and extracted readable text (best-effort).
- Respects copyrights by storing for internal research; prefer writing your own summary in the note file after fetch.
- Dependencies: requests, beautifulsoup4, readability-lxml (optional)
"""
import argparse
import datetime as dt
import os
import re
import sys
from pathlib import Path

import requests
from bs4 import BeautifulSoup

try:
    from readability import Document  # type: ignore
    HAVE_READABILITY = True
except Exception:
    HAVE_READABILITY = False

UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
)

def sanitize_filename(name: str) -> str:
    name = name.lower().strip()
    name = re.sub(r"[^a-z0-9\-]+", "-", name)
    name = re.sub(r"-+", "-", name).strip("-")
    return name or "source"

def fetch_html(url: str) -> str:
    r = requests.get(url, headers={"User-Agent": UA}, timeout=30)
    r.raise_for_status()
    return r.text

def extract_text(html: str) -> tuple[str, str]:
    title = ""
    try:
        soup = BeautifulSoup(html, "lxml")
        title = (soup.title.string or "").strip() if soup.title else ""
    except Exception:
        pass

    # Prefer readability if available
    if HAVE_READABILITY:
        try:
            doc = Document(html)
            title = doc.short_title() or title
            content_html = doc.summary(html_partial=True)
            soup = BeautifulSoup(content_html, "lxml")
            text = soup.get_text("\n", strip=True)
            return title, text
        except Exception:
            pass

    # Fallback: heuristic main content extraction
    try:
        soup = BeautifulSoup(html, "lxml")
        # Choose the largest text block among article/main/content containers
        candidates = soup.select("article, main, #content, .content, #main, .entry-content")
        blocks = candidates or [soup.body or soup]
        best_text = ""
        best_len = 0
        for b in blocks:
            t = b.get_text("\n", strip=True)
            if len(t) > best_len:
                best_text, best_len = t, len(t)
        return title, best_text
    except Exception:
        return title, ""

def write_note(outdir: Path, provider: str, slug: str, url: str, title: str, text: str) -> Path:
    date = dt.datetime.utcnow().strftime("%Y%m%d")
    base = f"{sanitize_filename(slug)}_{sanitize_filename(provider)}_{date}.txt"
    path = outdir / base
    header = [
        f"URL: {url}",
        f"Provider: {provider}",
        f"Title: {title}",
        f"Fetched-At-UTC: {dt.datetime.utcnow().isoformat()}",
        "",
        "--- Extracted text (best-effort) ---",
        "",
    ]
    content = "\n".join(header) + (text or "[No text extracted]")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return path

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--url", required=True)
    p.add_argument("--provider", required=True, help="sep|iep|other")
    p.add_argument("--slug", required=True, help="short identifier, e.g., speech-acts")
    p.add_argument("--outdir", default="nyaya/Datasets/sources", help="output dir")
    args = p.parse_args()

    outdir = Path(args.outdir)
    if outdir.name not in {"sources", "sep", "iep"}:
        # Allow both nyaya/Datasets/sources and a nested provider dir
        outdir.mkdir(parents=True, exist_ok=True)
    if outdir.name == "sources":
        outdir = outdir / args.provider

    html = fetch_html(args.url)
    title, text = extract_text(html)
    note_path = write_note(outdir, args.provider, args.slug, args.url, title, text)
    print(f"Saved: {note_path}")

if __name__ == "__main__":
    sys.exit(main())
