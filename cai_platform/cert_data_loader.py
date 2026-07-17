#!/usr/bin/env python3
"""Load and normalize certification point data for the CAI platform."""

from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent
DATA_DIR = ROOT / "data"
DEFAULT_RAW_PATH = DATA_DIR / "certification_points_raw.csv"
DEFAULT_OUTPUT_PATH = DATA_DIR / "certification_points.csv"

TOPIC_ALIASES = {
    "acoustics": "Acoustics",
    "thermal": "Thermal",
    "lighting": "Lighting",
    "air quality": "Air",
    "air": "Air",
}


def _normalize_topic(value: str) -> str:
    key = " ".join(str(value).split()).strip().lower()
    if key not in TOPIC_ALIASES:
        raise ValueError(f"Unknown topic value: {value!r}")
    return TOPIC_ALIASES[key]


def _to_numeric_points(value) -> float | None:
    text = str(value).strip()
    if not text or text.lower() == "bundled":
        return None
    return float(text)


def load_certification_points(source: str | Path | pd.DataFrame | None = None) -> pd.DataFrame:
    """
    Load certification points from the raw source CSV and return the
    normalized schema used by CAIAnalyzer.
    """
    if source is None:
        source = DEFAULT_RAW_PATH
    raw = pd.read_csv(source) if not isinstance(source, pd.DataFrame) else source.copy()
    raw.columns = [col.strip() for col in raw.columns]

    frame = pd.DataFrame(
        {
            "badge": raw["Badge"].astype(str).str.strip(),
            "system": raw["Badge"].astype(str).str.strip(),
            "version": raw["version"].astype(str).str.strip(),
            "year": pd.to_numeric(raw["year"], errors="coerce").astype(int),
            "track": raw["track"].astype(str).str.strip(),
            "topic": raw["topic"].apply(_normalize_topic),
            "points_raw": raw["points"],
            "rows_included": raw["rows_included"],
            "has_prerequisite": raw["has_prerequistie"],
            "has_measured_target": raw["Has_measured_target"],
            "group_total": pd.to_numeric(raw["group_total"], errors="coerce"),
            "system_total": pd.to_numeric(raw["system_total"], errors="coerce"),
            "source": raw["source_file"].astype(str).str.strip(),
        }
    )

    resolved = []
    for (_, _), group in frame.groupby(["system", "version"], sort=False):
        group = group.copy()
        numeric_points = group["points_raw"].map(_to_numeric_points)
        explicit_sum = numeric_points.dropna().sum()
        bundled_mask = numeric_points.isna()
        bundled_count = int(bundled_mask.sum())
        group_total = float(group["group_total"].iloc[0])

        if bundled_count:
            share = max((group_total - explicit_sum) / bundled_count, 0.0)
            group["points"] = numeric_points.fillna(share)
        else:
            group["points"] = numeric_points

        resolved.append(group)

    normalized = pd.concat(resolved, ignore_index=True)
    columns = [
        "badge",
        "system",
        "version",
        "year",
        "track",
        "topic",
        "points",
        "group_total",
        "system_total",
        "rows_included",
        "has_prerequisite",
        "has_measured_target",
        "source",
    ]
    return normalized[columns].sort_values(["system", "year", "topic"]).reset_index(drop=True)


def write_certification_points(
    raw_path: str | Path | None = None,
    output_path: str | Path | None = None,
) -> pd.DataFrame:
    """Normalize the raw certification CSV and write the app-ready file."""
    output = Path(output_path) if output_path else DEFAULT_OUTPUT_PATH
    frame = load_certification_points(raw_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    frame.to_csv(output, index=False)
    return frame


def load_certification_data(path: str | Path | None = None) -> pd.DataFrame:
    """Load certification data from raw or normalized CSV."""
    source = Path(path) if path else DEFAULT_OUTPUT_PATH
    preview = pd.read_csv(source, nrows=1)
    preview.columns = [col.strip() for col in preview.columns]
    if "Badge" in preview.columns:
        return load_certification_points(source)
    return pd.read_csv(source)


if __name__ == "__main__":
    df = write_certification_points()
    print(f"Wrote {DEFAULT_OUTPUT_PATH} ({len(df)} rows, {df['system'].nunique()} systems)")
