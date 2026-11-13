"""N1 Source Ingestion: verify one batch of sources against Crossref / the official URL.

Usage:
    python3 scripts/ingest.py --batch 1
    python3 scripts/ingest.py --batch 1 --dry-run   # report only, do not write manifest
"""
import argparse
import datetime as dt
import difflib
import json
import os
import re
import ssl
import sys
import time
import urllib.parse
import urllib.request

from common import ROOT, SOURCE_REQUIRED, load_json, save_json

UA = "GenAI_DNA2PrecisionMed/1.0 (course project; +https://github.com/yixiang-liao/GenAI_DNA2PrecisionMed)"
DOI_RE = re.compile(r"^10\.\d{4,9}/\S+$")
TITLE_THRESHOLD = 0.85


def ssl_context():
    """python.org macOS builds ship without a CA bundle (execution-log E02); fall back explicitly."""
    for cafile in (os.environ.get("SSL_CERT_FILE"), "/etc/ssl/cert.pem"):
        if cafile and os.path.exists(cafile):
            return ssl.create_default_context(cafile=cafile)
    try:
        import certifi
        return ssl.create_default_context(cafile=certifi.where())
    except ImportError:
        return ssl.create_default_context()


SSL_CTX = ssl_context()


def http_get(url, timeout=25):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=timeout, context=SSL_CTX) as resp:
        return resp.status, resp.read().decode("utf-8", errors="replace")


def norm(text):
    text = re.sub(r"<[^>]+>", "", text or "")
    return re.sub(r"[^a-z0-9]+", " ", text.lower()).strip()


def title_similarity(a, b):
    return round(difflib.SequenceMatcher(None, norm(a), norm(b)).ratio(), 3)


def check_crossref(src):
    status, body = http_get("https://api.crossref.org/works/" + urllib.parse.quote(src["doi"]))
    msg = json.loads(body)["message"]
    resolved_title = (msg.get("title") or [""])[0]
    # Online-first and print dates can fall in different years (execution-log E03); accept either.
    years = {}
    for key in ("issued", "published-print", "published-online"):
        parts = (msg.get(key) or {}).get("date-parts", [[None]])
        if parts[0][0]:
            years[key] = parts[0][0]
    resolved_year = years.get("issued")
    sim = title_similarity(src["title"], resolved_title)
    errors = []
    if sim < TITLE_THRESHOLD:
        errors.append(f"title mismatch (similarity {sim}): Crossref says '{resolved_title}'")
    if src["year"] not in years.values():
        errors.append(f"year mismatch: manifest {src['year']}, Crossref {years}")
    return {
        "resolver": "crossref",
        "http_status": status,
        "resolved_title": resolved_title,
        "resolved_year": resolved_year,
        "resolved_years": years,
        "resolved_container": (msg.get("container-title") or [""])[0],
        "title_similarity": sim,
    }, errors


def check_url(src):
    status, body = http_get(src["url"])
    m = re.search(r"<title[^>]*>(.*?)</title>", body, re.S | re.I)
    page_title = re.sub(r"\s+", " ", m.group(1)).strip() if m else ""
    errors = [] if status == 200 else [f"HTTP {status}"]
    return {"resolver": "http", "http_status": status, "resolved_title": page_title}, errors


def cache_pubmed_abstract(src):
    """Best effort: store the PubMed abstract for N2/N7 checks. Never fails the batch."""
    if not src.get("doi"):
        return None
    base = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"
    try:
        _, body = http_get(base + "esearch.fcgi?db=pubmed&retmode=json&term="
                           + urllib.parse.quote(src["doi"] + "[doi]"))
        ids = json.loads(body)["esearchresult"]["idlist"]
        if not ids:
            return cache_openalex_abstract(src)
        time.sleep(0.4)  # NCBI rate limit without API key: 3 req/s
        _, text = http_get(base + f"efetch.fcgi?db=pubmed&id={ids[0]}&rettype=abstract&retmode=text")
        cache = ROOT / "sources/cache"
        cache.mkdir(parents=True, exist_ok=True)
        (cache / f"{src['id']}.txt").write_text(text, encoding="utf-8")
        return ids[0]
    except Exception as exc:  # noqa: BLE001 - cache is optional
        print(f"  (abstract cache skipped: {exc})")
        return None


def cache_openalex_abstract(src):
    """Fallback for journals PubMed does not index (e.g. Nat Rev Methods Primers)."""
    _, body = http_get("https://api.openalex.org/works/doi:" + src["doi"])
    inv = json.loads(body).get("abstract_inverted_index") or {}
    if not inv:
        return None
    words = sorted((p, w) for w, ps in inv.items() for p in ps)
    text = f"{src['title']}\n\n{' '.join(w for _, w in words)}\n\n(abstract via OpenAlex)\n"
    (ROOT / "sources/cache").mkdir(parents=True, exist_ok=True)
    (ROOT / "sources/cache" / f"{src['id']}.txt").write_text(text, encoding="utf-8")
    return "openalex"


def metadata_errors(src, seen_ids):
    errors = [f"missing field '{k}'" for k in SOURCE_REQUIRED if src.get(k) in (None, "", [])]
    if not src.get("doi") and not src.get("url"):
        errors.append("needs a DOI or URL")
    if src.get("doi") and not DOI_RE.match(src["doi"]):
        errors.append(f"invalid DOI syntax '{src['doi']}'")
    if src.get("url") and not src["url"].startswith("https://"):
        errors.append("URL must be https")
    if src["id"] in seen_ids:
        errors.append(f"duplicate id {src['id']}")
    return errors


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--batch", type=int, required=True)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    manifest = load_json("sources/manifest.json")
    batch = [s for s in manifest["sources"] if s.get("batch") == args.batch]
    if not 3 <= len(batch) <= 5:
        print(f"batch {args.batch} has {len(batch)} sources; must be 3-5")
        return 2

    seen, failed = set(), 0
    for s in manifest["sources"]:
        if s.get("batch") != args.batch:
            seen.add(s["id"])
    now = dt.datetime.now().astimezone().isoformat(timespec="seconds")

    for src in batch:
        print(f"[{src['id']}] {src['title'][:70]}")
        errors = metadata_errors(src, seen)
        seen.add(src["id"])
        detail = {}
        if not errors:
            try:
                detail, errors = check_crossref(src) if src.get("doi") else check_url(src)
            except Exception as exc:  # noqa: BLE001 - network errors are a recorded failure
                errors = [f"resolution failed: {exc}"]
            time.sleep(0.3)
        if not errors:
            pmid = cache_pubmed_abstract(src)
            if pmid:
                detail["pmid"] = pmid
        detail["checked_at"] = now
        detail["errors"] = errors
        src["verification"] = detail
        src["ingestion_status"] = "failed" if errors else "verified"
        failed += bool(errors)
        print("  " + ("FAIL: " + "; ".join(errors) if errors else
                      f"OK ({detail.get('resolver')}, sim={detail.get('title_similarity', '-')})"))

    if not args.dry_run:
        save_json("sources/manifest.json", manifest)
    print(f"batch {args.batch}: {len(batch) - failed}/{len(batch)} verified")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
