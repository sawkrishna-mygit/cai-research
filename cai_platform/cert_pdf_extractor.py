#!/usr/bin/env python3
"""Extract certification credits from PDFs and compute CAI alignment scores."""

from __future__ import annotations

import json
import re
from datetime import datetime
from io import BytesIO
from pathlib import Path
from typing import Any

import pandas as pd

from cai_core import analyze_single_version

ROOT = Path(__file__).resolve().parent
DEFAULT_KEYWORDS_PATH = ROOT / "data" / "topic_keywords.json"
TOPIC_PRIORITY = ["Acoustics", "Thermal", "Lighting", "Air"]

CREDIT_PATTERNS = [
    re.compile(
        r"(?P<title>[A-Za-z0-9][\w\s\-–—/.,:&()'+]{3,120}?)"
        r"\s*[-–—:]\s*(?P<points>\d+(?:\.\d+)?)\s*(?:points?|pts?)\b",
        re.IGNORECASE,
    ),
    re.compile(
        r"(?P<code>[A-Z]{1,3}[cqfxst]\d+(?:\.\d+)?)\s+"
        r"(?P<title>[\w\s\-–—/.,:&()'+]{3,120}?)"
        r"\s*[-–—]?\s*(?P<points>\d+(?:\.\d+)?)\s*(?:points?|pts?)\b",
        re.IGNORECASE,
    ),
    re.compile(
        r"(?P<title>[\w\s\-–—/.,:&()'+]{3,120}?)"
        r"\s*\(\s*(?P<points>\d+(?:\.\d+)?)\s*(?:points?|pts?)\s*\)",
        re.IGNORECASE,
    ),
    re.compile(
        r"(?P<title>[\w\s\-–—/.,:&()'+]{3,120}?)"
        r"\s+(?:worth|maximum|max(?:imum)?)\s+(?P<points>\d+(?:\.\d+)?)\s*(?:points?|pts?)\b",
        re.IGNORECASE,
    ),
    re.compile(
        r"(?P<title>Feature\s+[A-Z]\d+[:.]?\s*[\w\s\-–—/.,:&()'+]{0,80})"
        r"\s*[-–—]?\s*(?P<points>\d+(?:\.\d+)?)\s*(?:points?|pts?)\b",
        re.IGNORECASE,
    ),
]

SYSTEM_HINTS = {
    "leed": "LEED",
    "well": "WELL",
    "breeam": "BREEAM",
    "fitwel": "Fitwel",
    "green star": "Green Star",
    "casbee": "CASBEE",
}


def load_topic_keywords(path: str | Path | None = None) -> dict[str, list[str]]:
    keywords_path = Path(path) if path else DEFAULT_KEYWORDS_PATH
    with open(keywords_path) as f:
        return json.load(f)


def extract_text_from_pdf(source: str | Path | bytes | BytesIO) -> str:
    try:
        import fitz
    except ImportError as exc:
        raise ImportError(
            "PyMuPDF is required for PDF extraction. Install with: pip install pymupdf"
        ) from exc

    if isinstance(source, (bytes, bytearray)):
        doc = fitz.open(stream=bytes(source), filetype="pdf")
    elif isinstance(source, BytesIO):
        doc = fitz.open(stream=source.getvalue(), filetype="pdf")
    else:
        doc = fitz.open(str(source))

    pages = [page.get_text("text") for page in doc]
    doc.close()

    text = "\n".join(pages).strip()
    if not text:
        raise ValueError(
            "No extractable text found in PDF. Scanned/image-only PDFs are not supported."
        )
    return normalize_text(text)


def normalize_text(text: str) -> str:
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"(\w)-\n(\w)", r"\1\2", text)
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def parse_credits(text: str) -> list[dict[str, Any]]:
    credits: list[dict[str, Any]] = []
    seen: set[tuple[str, float]] = set()

    for line in text.splitlines():
        cleaned = line.strip()
        if len(cleaned) < 8:
            continue

        line_matches: list[dict[str, Any]] = []
        for pattern in CREDIT_PATTERNS:
            for match in pattern.finditer(cleaned):
                title = " ".join(match.group("title").split()).strip(" -–—:")
                points = float(match.group("points"))
                if points <= 0 or len(title) < 3:
                    continue
                line_matches.append(
                    {
                        "title": title,
                        "points": points,
                        "snippet": cleaned[:240],
                        "has_code": "code" in match.groupdict() and match.group("code"),
                    }
                )

        if not line_matches:
            continue

        line_matches.sort(
            key=lambda item: (bool(item["has_code"]), len(item["title"])),
            reverse=True,
        )
        best = line_matches[0]
        key = (best["title"].lower(), best["points"])
        if key in seen:
            continue
        seen.add(key)
        credits.append(
            {
                "title": best["title"],
                "points": best["points"],
                "snippet": best["snippet"],
            }
        )
    return credits


def categorize_credit(text: str, keywords: dict[str, list[str]] | None = None) -> str | None:
    keyword_map = keywords or load_topic_keywords()
    haystack = text.lower()
    scores: dict[str, int] = {}

    for topic in TOPIC_PRIORITY:
        score = 0
        for keyword in keyword_map.get(topic, []):
            if keyword.lower() in haystack:
                score += 1
        if score:
            scores[topic] = score

    if not scores:
        return None

    best_score = max(scores.values())
    candidates = [topic for topic in TOPIC_PRIORITY if scores.get(topic) == best_score]
    return candidates[0]


def classify_credits(
    credits: list[dict[str, Any]],
    keywords: dict[str, list[str]] | None = None,
) -> list[dict[str, Any]]:
    classified = []
    for credit in credits:
        blob = f"{credit['title']} {credit.get('snippet', '')}"
        topic = categorize_credit(blob, keywords)
        classified.append({**credit, "topic": topic})
    return classified


def aggregate_topic_points(
    classified_credits: list[dict[str, Any]],
    topics: list[str] | None = None,
) -> dict[str, float]:
    topic_list = topics or TOPIC_PRIORITY
    totals = {topic: 0.0 for topic in topic_list}
    for credit in classified_credits:
        topic = credit.get("topic")
        if topic in totals:
            totals[topic] += float(credit["points"])
    return totals


def infer_metadata_from_filename(filename: str) -> dict[str, Any]:
    stem = Path(filename).stem.lower().replace("_", " ").replace("-", " ")
    system = "Custom Cert"
    version = "upload"
    year = datetime.now().year

    for hint, label in SYSTEM_HINTS.items():
        if hint in stem:
            system = label
            break

    version_match = re.search(r"\bv?\d+(?:\.\d+)?\b", stem)
    if version_match:
        version = version_match.group(0)
        if not version.startswith("v") and system in {"LEED", "WELL", "BREEAM", "Fitwel"}:
            version = f"v{version}" if version[0].isdigit() else version

    year_match = re.search(r"\b(19|20)\d{2}\b", stem)
    if year_match:
        year = int(year_match.group(0))

    return {"system": system, "version": version, "year": year}


def build_cert_dataframe(
    system: str,
    version: str,
    year: int,
    topic_points: dict[str, float],
    source: str,
) -> pd.DataFrame:
    system_total = sum(topic_points.values())
    if system_total <= 0:
        raise ValueError("No categorized IEQ points found in PDF.")

    rows = []
    for topic in TOPIC_PRIORITY:
        rows.append(
            {
                "badge": system,
                "system": system,
                "version": version,
                "year": int(year),
                "track": "PDF upload",
                "topic": topic,
                "points": float(topic_points.get(topic, 0.0)),
                "system_total": float(system_total),
                "source": source,
            }
        )
    return pd.DataFrame(rows)


def extraction_stats(classified_credits: list[dict[str, Any]]) -> dict[str, Any]:
    categorized = [c for c in classified_credits if c.get("topic")]
    skipped = [c for c in classified_credits if not c.get("topic")]
    topic_hits = {topic: 0 for topic in TOPIC_PRIORITY}
    for credit in categorized:
        topic_hits[credit["topic"]] += 1

    total_points = sum(float(c["points"]) for c in categorized)
    low_confidence = len(categorized) < 4 or total_points <= 0

    return {
        "credits_found": len(classified_credits),
        "credits_categorized": len(categorized),
        "credits_skipped": len(skipped),
        "topic_hits": topic_hits,
        "total_categorized_points": total_points,
        "low_confidence": low_confidence,
        "skipped_examples": [c["title"] for c in skipped[:5]],
    }


def analyze_pdf(
    source: str | Path | bytes | BytesIO,
    occupant_data: dict[str, float],
    system: str | None = None,
    version: str | None = None,
    year: int | None = None,
    filename: str | None = None,
    n_bootstrap: int = 1000,
    keywords: dict[str, list[str]] | None = None,
) -> dict[str, Any]:
    if isinstance(source, (str, Path)) and not isinstance(source, bytes):
        path = Path(source)
        filename = filename or path.name
        pdf_bytes = path.read_bytes()
    elif isinstance(source, BytesIO):
        pdf_bytes = source.getvalue()
        filename = filename or "upload.pdf"
    else:
        pdf_bytes = bytes(source)
        filename = filename or "upload.pdf"

    inferred = infer_metadata_from_filename(filename)
    system = system or inferred["system"]
    version = version or inferred["version"]
    year = year or inferred["year"]

    text = extract_text_from_pdf(pdf_bytes)
    credits = parse_credits(text)
    classified = classify_credits(credits, keywords)
    stats = extraction_stats(classified)
    topic_points = aggregate_topic_points(classified, topics=list(occupant_data.keys()))

    cert_df = build_cert_dataframe(system, version, year, topic_points, filename)
    result = analyze_single_version(cert_df, occupant_data, n_bootstrap=n_bootstrap)

    gaps = {
        topic: {
            "points": topic_points.get(topic, 0.0),
            "cert_pct": result.get(f"{topic}_pct"),
            "occupant_pct": occupant_data[topic],
            "gap": result.get(f"{topic}_gap"),
        }
        for topic in occupant_data
    }

    return {
        "system": system,
        "version": version,
        "year": year,
        "filename": filename,
        "tau": result["Tau"],
        "p_value": result["P_Value"],
        "ci_lower": result["CI_Lower"],
        "ci_upper": result["CI_Upper"],
        "spearman_rho": result["Spearman_Rho"],
        "system_total": result["System_Total"],
        "topic_points": topic_points,
        "gaps": gaps,
        "extraction_stats": stats,
        "classified_credits": classified,
        "cert_dataframe": cert_df,
        "analysis_row": result,
    }


def analyze_text(
    text: str,
    occupant_data: dict[str, float],
    system: str = "Custom Cert",
    version: str = "upload",
    year: int | None = None,
    source: str = "text",
    n_bootstrap: int = 1000,
    keywords: dict[str, list[str]] | None = None,
) -> dict[str, Any]:
    """Analyze pre-extracted text (used by tests)."""
    year = year or datetime.now().year
    credits = parse_credits(normalize_text(text))
    classified = classify_credits(credits, keywords)
    stats = extraction_stats(classified)
    topic_points = aggregate_topic_points(classified, topics=list(occupant_data.keys()))
    cert_df = build_cert_dataframe(system, version, year, topic_points, source)
    result = analyze_single_version(cert_df, occupant_data, n_bootstrap=n_bootstrap)
    return {
        "system": system,
        "version": version,
        "year": year,
        "tau": result["Tau"],
        "topic_points": topic_points,
        "extraction_stats": stats,
        "analysis_row": result,
    }
