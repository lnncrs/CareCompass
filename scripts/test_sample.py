"""Validação da amostra e da ligação entre registros e fontes preservadas."""

import json
import unittest
from collections import Counter

from build_sample import ROOT, build


class SampleTests(unittest.TestCase):
    def setUp(self):
        self.sample = json.loads(
            (ROOT / "data/processed/services.sample.json").read_text(encoding="utf-8")
        )

    def test_counts_mix_and_unique_ids(self):
        records = self.sample["services"]
        self.assertEqual(len(records), 40)
        self.assertEqual(len({item["id"] for item in records}), 40)
        for zone in ("centro", "leste", "norte", "sul", "oeste"):
            local = [item for item in records if item["zone"] == zone]
            self.assertEqual(
                Counter(item["category"] for item in local),
                {
                    "food": 2,
                    "shelter": 2,
                    "mental_health": 3,
                    "social_assistance": 1,
                },
            )
            self.assertEqual(
                {item["type"] for item in local if item["category"] == "mental_health"},
                {"caps_adulto", "caps_ad", "caps_ij"},
            )
        for item in records:
            self.assertTrue(item["address"].strip())
            self.assertIn(item["address"], item["provenance"]["evidence_text"])

    def test_rebuild_matches_and_verifies_source_hashes(self):
        # build() exige âncoras únicas e hashes corretos dos originais.
        self.assertEqual(self.sample, build())


if __name__ == "__main__":
    unittest.main()
