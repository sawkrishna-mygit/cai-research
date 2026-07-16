#!/usr/bin/env python3
"""Export analysis results and web JSON from cai_core."""

import json
from pathlib import Path

import pandas as pd

from cai_core import CAIAnalyzer

ROOT = Path(__file__).resolve().parent
DATA_DIR = ROOT / "data"
WEB_DATA_DIR = ROOT / "web" / "assets" / "data"


def main():
    cert_df = pd.read_csv(DATA_DIR / "certification_points_complete.csv")
    with open(DATA_DIR / "occupant_data.json") as f:
        occupant_data = json.load(f)

    analyzer = CAIAnalyzer(cert_df, occupant_data)
    results = analyzer.analyze()
    summary = analyzer.get_summary()
    gaps = analyzer.get_gaps_by_topic()

    results_out = results.copy()
    results_out.to_csv(DATA_DIR / "results_comprehensive.csv", index=False)

    systems = []
    for _, row in results.iterrows():
        systems.append({
            "name": f"{row['System']} {row['Version']}",
            "system": row["System"],
            "version": row["Version"],
            "year": int(row["Year"]),
            "ac": float(row["Acoustics_pts"]),
            "th": float(row["Thermal_pts"]),
            "li": float(row["Lighting_pts"]),
            "air": float(row["Air_pts"]),
            "total": int(row["System_Total"]),
            "tau": round(float(row["Tau"]), 3),
            "ci_lower": round(float(row["CI_Lower"]), 3) if pd.notna(row["CI_Lower"]) else None,
            "ci_upper": round(float(row["CI_Upper"]), 3) if pd.notna(row["CI_Upper"]) else None,
            "acGap": round(float(row["Acoustics_gap"]), 1),
            "thGap": round(float(row["Thermal_gap"]), 1),
            "liGap": round(float(row["Lighting_gap"]), 1),
            "airGap": round(float(row["Air_gap"]), 1),
        })

    WEB_DATA_DIR.mkdir(parents=True, exist_ok=True)
    payload = {
        "summary": {
            "avg_tau": round(summary["avg_tau"], 3),
            "n_systems": summary["n_systems"],
            "n_versions": summary["n_versions"],
            "years_span": summary["years_span"],
        },
        "occupant": occupant_data,
        "gaps_by_topic": {
            topic: {
                "avg_gap": round(info["avg_gap"], 1),
                "occupant_pct": info["occupant_pct"],
                "cert_pct": round(info["cert_pct"], 1),
            }
            for topic, info in gaps.items()
        },
        "systems": systems,
    }
    with open(WEB_DATA_DIR / "systems.json", "w") as f:
        json.dump(payload, f, indent=2)

    print(f"Wrote {DATA_DIR / 'results_comprehensive.csv'}")
    print(f"Wrote {WEB_DATA_DIR / 'systems.json'}")
    print(f"Average tau: {summary['avg_tau']:.3f}")


if __name__ == "__main__":
    main()
