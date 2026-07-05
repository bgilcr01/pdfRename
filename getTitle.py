"""Extract DOI from a PDF, fetch metadata from Crossref, and rename the file by title.

Usage: python getTitle.py <path-to-pdf>
"""

import argparse
import os
import re
import sys
from pathlib import Path
import tkinter.messagebox
from tkinter import Tk, filedialog

import pdfplumber
import requests

DOI_PATTERN = re.compile(r"\b(10\.\d{4,}/[^\s>\"'<]+)", re.IGNORECASE)
CROSSREF_URL = "https://api.crossref.org/works/{doi}"
CROSSREF_AGENT = "pdfRename/1.0 (mailto:user@example.com)"


def extract_doi_from_pdf(pdf_path: str) -> str | None:
    """Return the first DOI found on the first page of the PDF, or None."""
    with pdfplumber.open(pdf_path) as pdf:
        if not pdf.pages:
            return None
        text = pdf.pages[0].extract_text()
        if not text:
            return None
        match = DOI_PATTERN.search(text)
        return match.group(0) if match else None


def fetch_title(doi: str) -> str | None:
    """Query Crossref for the work title by DOI."""
    headers = {"User-Agent": CROSSREF_AGENT}
    resp = requests.get(CROSSREF_URL.format(doi=doi), headers=headers, verify=False, timeout=15)
    # if beyond corporate firewall, set verify=False and ensure you have the certifi package installed
    if resp.status_code != 200:
        return None
    data = resp.json()
    title_list = data.get("message", {}).get("title", [])
    return title_list[0] if title_list else None


def sanitize_filename(title: str, max_len: int = 200) -> str:
    """Convert a title into a safe filename stem."""
    safe = title.replace("\n", " ").replace("\r", "")
    safe = re.sub(r'[<>:"/\\|?*]', "-", safe)
    safe = re.sub(r"\s+", " ", safe).strip()
    if len(safe) > max_len:
        safe = safe[:max_len].rsplit(" ", 1)[0]
    return safe or "untitled"



def rename_pdf(pdf_path: str, title: str, dry_run: bool = False) -> str:
    """Rename the PDF based on the title. Returns the new path."""
    src = Path(pdf_path)
    stem = sanitize_filename(title)
    dest = src.with_name(f"{stem}.pdf")

    if dest == src:
        return str(src)

    # Avoid overwriting an existing file
    counter = 1
    base = dest.with_suffix("")
    while dest.exists() and dest != src:
        dest = Path(f"{base} ({counter}).pdf")
        counter += 1

    if dry_run:
        print(f"[DRY RUN] Rename: {src.name}  →  {dest.name}")
    else:
        os.rename(src, dest)

    return str(dest)


def select_files():
    root = Tk()
    root.withdraw()
    return filedialog.askopenfilenames(title="Select PDF file(s)")


def main():
    parser = argparse.ArgumentParser(
        description="Rename a PDF file using its title from Crossref."
    )
    parser.add_argument("--path", nargs="+", default=[], help="Path(s) to PDF file(s)")
    parser.add_argument(
        "--dry-run", action="store_true", help="Print renames without applying them"
    )
    args = parser.parse_args()

    if not args.path:
        files = select_files()
    else:  
        files = args.path


    for pdf_path in files:
        print(f"\n--- {pdf_path} ---")

        if not os.path.isfile(pdf_path):
            print(f"  ERROR: file not found")
            continue

        doi = extract_doi_from_pdf(pdf_path)
        if not doi:
            print("  Skipped: no DOI found on first page")
            doi = input("Enter DOI manually: ").strip()
            if not doi:
                continue

        print(f"  DOI:  {doi}")

        title = fetch_title(doi)
        if not title:
            print(f"  Skipped: could not fetch title from Crossref")
            title = "Untitled"
        print(f"  Title: {title}")

        new_path = rename_pdf(pdf_path, title, dry_run=args.dry_run)
        if new_path != pdf_path:
            print(f"  Renamed → {Path(new_path).name}")
        else:
            print(f"  (already named correctly)")

    print("\nDone.")


if __name__ == "__main__":
    main()
