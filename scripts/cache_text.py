"""N1 text cache: store readable source text so N2 quotes and N7 review can be checked (review R02).

- DOI sources with an open PMC copy -> NCBI efetch (db=pmc) body text -> sources/cache/fulltext/Sxx.txt
- Official web sources (S01, S02)   -> every URL in manifest `cache_pages` -> sources/cache/pages/Sxx.txt

The cache is git-ignored (third-party text); re-create it with this script.

Usage: python3 scripts/cache_text.py [--only S24 S01]
"""
import argparse
import json
import re
import sys
import time
from html import unescape

from common import ROOT, load_json, save_json
from ingest import http_get

CACHE = ROOT / "sources/cache"


def html_to_text(html):
    html = re.sub(r"(?is)<(script|style|noscript|svg|nav|header|footer)[^>]*>.*?</\1>", " ", html)
    m = re.search(r"(?is)<main[^>]*>(.*)</main>", html)
    html = m.group(1) if m else html
    text = unescape(re.sub(r"<[^>]+>", " ", html))
    return re.sub(r"\s+", " ", text).strip()


def pmc_id(pmid):
    url = ("https://www.ncbi.nlm.nih.gov/pmc/utils/idconv/v1.0/?format=json&tool=dna2pm"
           f"&email=noreply@example.org&ids={pmid}")
    rec = json.loads(http_get(url)[1])["records"][0]
    return rec.get("pmcid")


def pmc_body(pmcid):
    _, xml = http_get(f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pmc&id={pmcid[3:]}")
    m = re.search(r"(?s)<body>(.*)</body>", xml)
    if not m:
        return None
    floats = re.search(r"(?s)<floats-group>(.*)</floats-group>", xml)  # tables and figure legends
    body = m.group(1) + (" " + floats.group(1) if floats else "")
    body = re.sub(r"<xref[^>]*>[^<]*</xref>", "", body)  # drop inline citation numbers
    return re.sub(r"\s+", " ", unescape(re.sub(r"<[^>]+>", " ", body))).strip()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", nargs="*")
    args = ap.parse_args()
    manifest = load_json("sources/manifest.json")
    (CACHE / "fulltext").mkdir(parents=True, exist_ok=True)
    (CACHE / "pages").mkdir(parents=True, exist_ok=True)
    for src in manifest["sources"]:
        if args.only and src["id"] not in args.only:
            continue
        ver = src.setdefault("verification", {})
        if src.get("cache_pages"):
            parts = []
            for url in src["cache_pages"]:
                parts.append(f"=== {url}\n{html_to_text(http_get(url)[1])}")
                time.sleep(0.3)
            (CACHE / "pages" / f"{src['id']}.txt").write_text("\n\n".join(parts) + "\n", encoding="utf-8")
            print(f"[{src['id']}] {len(parts)} pages cached")
        elif ver.get("pmid"):
            try:
                pmcid = ver.get("pmcid") or pmc_id(ver["pmid"])
                body = pmc_body(pmcid) if pmcid else None
            except Exception as exc:  # noqa: BLE001 - keep the existing cache file, report and go on
                print(f"[{src['id']}] fetch failed: {exc}")
                continue
            finally:
                time.sleep(1.0)
            if not body:
                print(f"[{src['id']}] no open PMC full text")
                continue
            ver["pmcid"] = pmcid
            (CACHE / "fulltext" / f"{src['id']}.txt").write_text(
                f"{src['title']}\n\n{body}\n\n(full text via NCBI PMC {pmcid})\n", encoding="utf-8")
            print(f"[{src['id']}] {pmcid}: {len(body)} chars")
    save_json("sources/manifest.json", manifest)
    return 0


if __name__ == "__main__":
    sys.exit(main())
