"""Tests du normaliseur de flux réseau (CICFlowMeter) vers le schéma commun."""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src" / "logminer"))

from normalizers.network_flow import normalize_flows  # noqa: E402
from schema.columns import COLUMNS  # noqa: E402


class NetworkFlowNormalizerTests(unittest.TestCase):
    def test_cse_cic_columns_are_projected(self):
        raw = pd.DataFrame({
            "Dst Port": ["80", "21"], "Protocol": ["6", "17"],
            "Timestamp": ["16/02/2018 08:27:23", "16/02/2018 13:05:01"],
            "TotLen Fwd Pkts": ["120", "0"], "Label": ["DoS attacks-Hulk", "Benign"],
        })
        out = normalize_flows(raw, dataset="cse_cic_ids2018", filepath="f.csv")
        self.assertEqual(list(out.columns), COLUMNS)
        self.assertEqual(out["dst_port"].tolist(), ["80", "21"])
        self.assertEqual(out["proto"].tolist(), ["6", "17"])
        self.assertEqual(out["timestamp_iso"].tolist(), ["2018-02-16T08:27:23", "2018-02-16T13:05:01"])
        self.assertEqual(out["bytes_sent"].tolist(), ["120", "0"])
        self.assertEqual(out["subtype"].tolist(), ["network_flow"] * 2)

    def test_cicids2017_ml_columns_with_leading_spaces(self):
        raw = pd.DataFrame({" Destination Port": ["443"], "Total Length of Fwd Packets": ["60"], " Label": ["BENIGN"]})
        out = normalize_flows(raw, dataset="cicids2017", filepath="g.csv")
        self.assertEqual(out.loc[0, "dst_port"], "443")
        self.assertEqual(out.loc[0, "bytes_sent"], "60")
        self.assertEqual(out.loc[0, "timestamp_iso"], "")
        self.assertEqual(out.loc[0, "src_ip"], "")

    def test_label_is_never_projected(self):
        raw = pd.DataFrame({"Dst Port": ["80"], "Label": ["DDoS"]})
        out = normalize_flows(raw, dataset="x", filepath="h.csv")
        values = set(out.iloc[0].astype(str))
        self.assertNotIn("DDoS", values)

    def test_invalid_timestamp_stays_empty(self):
        raw = pd.DataFrame({"Dst Port": ["80"], "Timestamp": ["Timestamp"]})
        out = normalize_flows(raw, dataset="x", filepath="h.csv")
        self.assertEqual(out.loc[0, "timestamp_iso"], "")


if __name__ == "__main__":
    unittest.main()
