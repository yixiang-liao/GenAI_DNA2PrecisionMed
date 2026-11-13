"""Shared paths and loaders. Standard library only."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

DOMAINS = [
    ("molecular", "分子生物學基礎", "Molecular Biology Foundations"),
    ("sequencing", "定序與變異分析", "Sequencing & Variant Analysis"),
    ("transcriptomics", "轉錄體學", "Transcriptomics"),
    ("gwas", "GWAS 與統計遺傳學", "GWAS & Statistical Genetics"),
    ("prs", "多基因風險分數", "Polygenic Risk Score"),
    ("multiomics", "多體學整合", "Multi-Omics Integration"),
    ("precision", "精準醫療", "Precision Medicine"),
]
DOMAIN_IDS = [d[0] for d in DOMAINS]

CLASSIFICATIONS = {"consensus", "single_study", "uncertain"}
CLAIM_STATUSES = {"verified", "pending_verification"}
SOURCE_STATUSES = {"pending", "verified", "failed", "rejected"}
SOURCE_TYPES = {"journal_article", "official_document", "textbook", "database"}
SOURCE_REQUIRED = [
    "id", "title", "authors", "year", "type", "topics",
    "batch", "ingestion_status", "access_date", "notes",
]


def load_json(rel):
    with open(ROOT / rel, encoding="utf-8") as f:
        return json.load(f)


def save_json(rel, data):
    path = ROOT / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")


def load_sources(root=ROOT):
    with open(root / "sources/manifest.json", encoding="utf-8") as f:
        return json.load(f)["sources"]


def load_concepts(root=ROOT):
    """Return all concepts from content/concepts/<domain>.json, in domain order."""
    concepts = []
    for domain in DOMAIN_IDS:
        path = root / "content/concepts" / f"{domain}.json"
        if not path.exists():
            continue
        with open(path, encoding="utf-8") as f:
            for c in json.load(f)["concepts"]:
                c.setdefault("domain", domain)
                concepts.append(c)
    return concepts


def load_optional(root, rel, default):
    path = root / rel
    if not path.exists():
        return default
    with open(path, encoding="utf-8") as f:
        return json.load(f)
