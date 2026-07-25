#!/usr/bin/env python3
"""Tests for PDF certification extraction and classification."""

import json
import unittest
from pathlib import Path

from cert_pdf_extractor import (
    aggregate_topic_points,
    analyze_text,
    build_cert_dataframe,
    categorize_credit,
    classify_credits,
    extraction_stats,
    infer_metadata_from_filename,
    load_topic_keywords,
    normalize_text,
    parse_credits,
)

DATA_DIR = Path(__file__).resolve().parent / "data"


class TestCertPdfExtractor(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.occupant = json.loads((DATA_DIR / "occupant_data.json").read_text())
        cls.keywords = load_topic_keywords()

    def test_parse_leed_style_credit(self):
        text = "EQc1 Acoustic Performance — 2 points"
        credits = parse_credits(text)
        self.assertEqual(len(credits), 1)
        self.assertEqual(credits[0]["points"], 2.0)

    def test_parse_well_style_credit(self):
        text = "Feature S03: Sound masking - 3 pts"
        credits = parse_credits(text)
        self.assertEqual(len(credits), 1)
        self.assertEqual(credits[0]["points"], 3.0)

    def test_parse_parenthetical_points(self):
        text = "Enhanced Indoor Air Quality Strategies (4 points)"
        credits = parse_credits(text)
        self.assertEqual(len(credits), 1)
        self.assertEqual(credits[0]["points"], 4.0)

    def test_categorize_acoustic_credit(self):
        topic = categorize_credit("Acoustic Performance and speech privacy", self.keywords)
        self.assertEqual(topic, "Acoustics")

    def test_categorize_air_credit(self):
        topic = categorize_credit("Enhanced ventilation and indoor air quality", self.keywords)
        self.assertEqual(topic, "Air")

    def test_categorize_unknown_credit(self):
        topic = categorize_credit("Construction waste management plan", self.keywords)
        self.assertIsNone(topic)

    def test_aggregate_topic_points(self):
        classified = [
            {"title": "Acoustic Performance", "points": 2.0, "topic": "Acoustics"},
            {"title": "Thermal Comfort", "points": 1.0, "topic": "Thermal"},
            {"title": "Daylight", "points": 3.0, "topic": "Lighting"},
            {"title": "Ventilation", "points": 4.0, "topic": "Air"},
            {"title": "Site selection", "points": 5.0, "topic": None},
        ]
        totals = aggregate_topic_points(classified)
        self.assertEqual(totals["Acoustics"], 2.0)
        self.assertEqual(totals["Air"], 4.0)

    def test_build_cert_dataframe_shape(self):
        topic_points = {
            "Acoustics": 1.0,
            "Thermal": 1.0,
            "Lighting": 6.0,
            "Air": 8.0,
        }
        df = build_cert_dataframe("LEED", "v4", 2013, topic_points, "leed_v4.pdf")
        self.assertEqual(len(df), 4)
        self.assertEqual(df["system_total"].iloc[0], 16.0)

    def test_infer_metadata_from_filename(self):
        meta = infer_metadata_from_filename("leed_v5_2025.pdf")
        self.assertEqual(meta["system"], "LEED")
        self.assertEqual(meta["version"], "v5")
        self.assertEqual(meta["year"], 2025)

    def test_extraction_stats_low_confidence(self):
        classified = classify_credits(
            parse_credits("Random prerequisite worth 1 point"),
            self.keywords,
        )
        stats = extraction_stats(classified)
        self.assertTrue(stats["low_confidence"])

    def test_analyze_text_end_to_end(self):
        text = normalize_text(
            """
            EQc1 Acoustic Performance — 1 point
            Thermal Comfort — 1 point
            Interior Lighting and Daylight — 6 points
            Enhanced Indoor Air Quality Strategies — 8 points
            """
        )
        result = analyze_text(
            text,
            self.occupant,
            system="LEED",
            version="v4",
            year=2013,
            n_bootstrap=200,
        )
        self.assertIn("tau", result)
        self.assertLess(result["tau"], 0)
        self.assertEqual(result["topic_points"]["Lighting"], 6.0)


if __name__ == "__main__":
    unittest.main()
