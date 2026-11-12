"""Tests des chargeurs de données de scripts/run_family_routing_ablation.py.

Ils couvrent les deux défauts découverts après coup dans les campagnes E-H3b :
sélection par premières lignes (CICIDS réduit aux DDoS d'un seul fichier) et fuite de
l'étiquette dans le résumé numérique d'UNSW-NB15. Chaque test échoue sur la version du
script au commit 27deb22.
"""
from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import run_family_routing_ablation as loaders  # noqa: E402


def write_cicids_file(path: Path, rows: list[tuple[str, int]]) -> None:
    pd.DataFrame(
        {
            " Destination Port": [port for _label, port in rows],
            " Flow Duration": [10] * len(rows),
            " Total Fwd Packets": [1] * len(rows),
            " Total Backward Packets": [1] * len(rows),
            "Total Length of Fwd Packets": [60] * len(rows),
            " Total Length of Bwd Packets": [60] * len(rows),
            " Flow Packets/s": [2.0] * len(rows),
            " Label": [label for label, _port in rows],
        }
    ).to_csv(path, index=False)


class CicidsLoaderTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self.tmp.name)
        # Premier fichier (ordre alphabétique) : uniquement du DDoS et du bénin.
        write_cicids_file(self.dir / "a_friday_ddos.csv", [("DDoS", 80)] * 50 + [("BENIGN", 443)] * 50)
        # Fichiers suivants : d'autres attaques, absentes du premier fichier.
        write_cicids_file(self.dir / "b_tuesday.csv", [("FTP-Patator", 21)] * 50 + [("BENIGN", 53)] * 50)
        write_cicids_file(self.dir / "c_thursday.csv", [("Web Attack", 8080)] * 50 + [("BENIGN", 22)] * 50)

    def tearDown(self):
        self.tmp.cleanup()

    def test_selection_draws_attacks_from_every_file(self):
        frame = loaders.load_cicids(self.dir, normal=60, anomaly=60, random_state=1)
        attack_ports = set(frame.loc[frame.target == 1, "dst_port"].astype(int))
        self.assertEqual(attack_ports, {80, 21, 8080})

    def test_quotas_and_labels(self):
        frame = loaders.load_cicids(self.dir, normal=30, anomaly=20, random_state=2)
        self.assertEqual(int((frame.target == 0).sum()), 30)
        self.assertEqual(int((frame.target == 1).sum()), 20)
        benign_ports = set(frame.loc[frame.target == 0, "dst_port"].astype(int))
        self.assertTrue(benign_ports <= {443, 53, 22})

    def test_selection_depends_on_seed(self):
        a = loaders.load_cicids(self.dir, normal=30, anomaly=30, random_state=1)
        b = loaders.load_cicids(self.dir, normal=30, anomaly=30, random_state=2)
        c = loaders.load_cicids(self.dir, normal=30, anomaly=30, random_state=1)
        self.assertNotEqual(sorted(a.dst_port.tolist()), sorted(b.dst_port.tolist()))
        self.assertEqual(sorted(a.dst_port.tolist()), sorted(c.dst_port.tolist()))


class UnswLoaderTests(unittest.TestCase):
    def test_label_does_not_leak_into_numeric_summary(self):
        # Mêmes variables pour toutes les lignes ; seules l'étiquette et sa copie diffèrent.
        n = 40
        frame = pd.DataFrame(
            {
                "dur": [1.0] * n, "spkts": [2] * n, "dpkts": [3] * n, "sbytes": [100] * n,
                "dbytes": [200] * n, "rate": [5.0] * n, "proto": ["tcp"] * n,
                "service": ["-"] * n, "state": ["FIN"] * n,
                "attack_cat": ["Normal"] * (n // 2) + ["Exploits"] * (n // 2),
                "label": [0] * (n // 2) + [1] * (n // 2),
            }
        )
        with mock.patch.object(loaders.pd, "read_parquet", side_effect=[frame, frame.iloc[0:0]]):
            out = loaders.load_unsw(Path("train"), Path("test"), normal=10, anomaly=10, random_state=3)
        summary_cols = [c for c in out.columns if c.startswith("numeric_")]
        self.assertTrue(summary_cols)
        by_class = out.groupby("target")[summary_cols].mean()
        pd.testing.assert_series_equal(by_class.loc[0], by_class.loc[1], check_names=False)


class LinuxAuthLoaderTests(unittest.TestCase):
    def test_target_mapping_and_quotas(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "auth.csv"
            pd.DataFrame(
                {
                    "timestamp": ["2025-01-01T10:00:00Z"] * 60,
                    "anomaly_label": ["normal"] * 40 + ["brute_force"] * 20,
                    "port": [22] * 60, "attempts": [1] * 40 + [9] * 20,
                    "protocol": ["ssh"] * 60, "service": ["sshd"] * 60, "status": ["ok"] * 60,
                }
            ).to_csv(path, index=False)
            frame = loaders.load_linux_auth(path, normal=15, anomaly=10, random_state=4)
        self.assertEqual(int((frame.target == 0).sum()), 15)
        self.assertEqual(int((frame.target == 1).sum()), 10)
        self.assertEqual(set(frame.loc[frame.target == 1, "attempts"].astype(int)), {9})


if __name__ == "__main__":
    unittest.main()
