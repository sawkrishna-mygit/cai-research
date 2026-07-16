#!/usr/bin/env python3
"""Generate publication figures for the CAI portfolio website."""

import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

from cai_core import CAIAnalyzer

ROOT = Path(__file__).resolve().parent
DATA_DIR = ROOT / "data"
FIG_DIR = ROOT / "web" / "assets" / "figures"

COLORS = {"LEED": "#1f77b4", "WELL": "#ff7f0e", "BREEAM": "#2ca02c", "Fitwel": "#d62728"}
MARKERS = {"LEED": "o", "WELL": "s", "BREEAM": "^", "Fitwel": "D"}


def load_analyzer():
    cert_df = pd.read_csv(DATA_DIR / "certification_points_complete.csv")
    with open(DATA_DIR / "occupant_data.json") as f:
        occupant_data = json.load(f)
    analyzer = CAIAnalyzer(cert_df, occupant_data)
    analyzer.analyze()
    return analyzer


def fig1_alignment_trajectories(results: pd.DataFrame, out: Path):
    fig, ax = plt.subplots(figsize=(10, 6))
    for system in results["System"].unique():
        system_data = results[results["System"] == system].sort_values("Year")
        yerr = [
            system_data["Tau"] - system_data["CI_Lower"],
            system_data["CI_Upper"] - system_data["Tau"],
        ]
        ax.errorbar(
            system_data["Year"],
            system_data["Tau"],
            yerr=yerr,
            fmt=MARKERS.get(system, "o"),
            color=COLORS.get(system, "#666666"),
            markersize=8,
            capsize=4,
            capthick=2,
            label=system,
            alpha=0.85,
        )
    ax.axhline(0, color="black", linewidth=0.5, alpha=0.5)
    ax.set_xlabel("Year")
    ax.set_ylabel("Kendall τ")
    ax.set_title("Alignment Trajectories Over Time")
    ax.legend()
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(out, dpi=300, bbox_inches="tight")
    plt.close(fig)


def fig2_topic_gaps(results: pd.DataFrame, topics: list, out: Path):
    latest = results.loc[results.groupby("System")["Year"].idxmax()]
    n = len(latest)
    fig, axes = plt.subplots(1, n, figsize=(3.2 * n, 4), sharey=True)
    if n == 1:
        axes = [axes]
    for ax, (_, row) in zip(axes, latest.iterrows()):
        gaps = [row[f"{t}_gap"] for t in topics]
        colors = ["#d62728" if g > 0 else "#1f77b4" for g in gaps]
        y_pos = np.arange(len(topics))
        ax.barh(y_pos, gaps, color=colors, alpha=0.75)
        ax.set_yticks(y_pos)
        ax.set_yticklabels(topics)
        ax.set_xlabel("Gap (%)")
        ax.set_title(f"{row['System']} {row['Version']}")
        ax.axvline(0, color="black", linewidth=1)
        ax.grid(True, alpha=0.3, axis="x")
    fig.suptitle("Topic-Level Gaps (Latest Versions)", y=1.02)
    fig.tight_layout()
    fig.savefig(out, dpi=300, bbox_inches="tight")
    plt.close(fig)


def fig3_heatmap(results: pd.DataFrame, topics: list, out: Path):
    rows = []
    for _, row in results.iterrows():
        for topic in topics:
            rows.append({
                "label": f"{row['System']} {row['Version']}",
                "topic": topic,
                "gap": row[f"{topic}_gap"],
            })
    gap_df = pd.DataFrame(rows)
    pivot = gap_df.pivot(index="label", columns="topic", values="gap")
    pivot = pivot[topics]
    fig, ax = plt.subplots(figsize=(8, 10))
    sns.heatmap(
        pivot,
        cmap="RdBu_r",
        center=0,
        annot=True,
        fmt=".1f",
        linewidths=0.5,
        cbar_kws={"label": "Gap (Cert% - Occupant%)"},
        ax=ax,
    )
    ax.set_title("Gap Heatmap: All Systems × Topics")
    ax.set_xlabel("")
    ax.set_ylabel("")
    fig.tight_layout()
    fig.savefig(out, dpi=300, bbox_inches="tight")
    plt.close(fig)


def fig4_occupant_vs_cert(analyzer: CAIAnalyzer, topics: list, out: Path):
    gaps = analyzer.get_gaps_by_topic()
    occupant = [gaps[t]["occupant_pct"] for t in topics]
    cert = [gaps[t]["cert_pct"] for t in topics]
    x = np.arange(len(topics))
    width = 0.35
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.bar(x - width / 2, occupant, width, label="Occupant dissatisfaction %", color="#1f77b4", alpha=0.85)
    ax.bar(x + width / 2, cert, width, label="Avg certification emphasis %", color="#ff7f0e", alpha=0.85)
    ax.set_ylabel("Percentage")
    ax.set_title("Occupant Priorities vs Certification Emphasis")
    ax.set_xticks(x)
    ax.set_xticklabels(topics)
    ax.legend()
    ax.grid(True, alpha=0.3, axis="y")
    fig.tight_layout()
    fig.savefig(out, dpi=300, bbox_inches="tight")
    plt.close(fig)


def main():
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    sns.set_theme(style="whitegrid")
    analyzer = load_analyzer()
    results = analyzer.results
    topics = analyzer.topics

    fig1_alignment_trajectories(results, FIG_DIR / "fig1_alignment_trajectories.png")
    fig2_topic_gaps(results, topics, FIG_DIR / "fig2_topic_gaps.png")
    fig3_heatmap(results, topics, FIG_DIR / "fig3_heatmap_all_systems.png")
    fig4_occupant_vs_cert(analyzer, topics, FIG_DIR / "fig4_occupant_vs_cert.png")

    print(f"Figures written to {FIG_DIR}")


if __name__ == "__main__":
    main()
