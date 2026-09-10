"""Garde-fous méthodologiques des campagnes de renforcement des datasets."""

from __future__ import annotations

import json
import sys
from dataclasses import asdict
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
for directory in (ROOT / "scripts", ROOT / "src", ROOT / "src/logminer", ROOT / "src/logminer/parsers"):
    if str(directory) not in sys.path:
        sys.path.insert(0, str(directory))

from dataset_strengthening_common import select_threshold, sha256_file  # noqa: E402
from logminer.agents.bus import AgentMessage  # noqa: E402
from logminer.agents.contract_net import ContractNetCoordinator  # noqa: E402
from logminer.agents.intelligent_runtime import AgentCapability, AgentTask, MultiTaskIntelligentAgent  # noqa: E402
from logminer.agents.model_router import route_dataframe  # noqa: E402
from logminer.parsers.bgl import Parser as BglParser  # noqa: E402
from logminer.parsers.hdfs import Parser as HdfsParser  # noqa: E402
from run_bgl_known_unknown_strengthening import group_masks  # noqa: E402
from run_cicids_temporal_strengthening import candidate_models, temporal_files  # noqa: E402
from run_external_csecicids2018_strengthening import (  # noqa: E402
    candidate_models as external_candidate_models,
    feature_columns as external_feature_columns,
    seed_sample as external_seed_sample,
)
from run_external_csecicids2018_sensitivity import deduplicate_unambiguous  # noqa: E402
from run_hdfs_block_strengthening import assign_templates, fit_frozen_drain, make_full_splits  # noqa: E402
from run_multiformat_validation import select_text_lines  # noqa: E402


class RowCollector:
    def __init__(self) -> None:
        self.rows: list[dict[str, object]] = []

    def writerow(self, row: dict[str, object]) -> None:
        self.rows.append(row)


def test_hdfs_block_split_is_disjoint() -> None:
    splits = make_full_splits([f"blk_{index}" for index in range(100)], [0.6, 0.2, 0.2])
    assert set(splits["train"]).isdisjoint(splits["validation"])
    assert set(splits["train"]).isdisjoint(splits["test"])
    assert set(splits["validation"]).isdisjoint(splits["test"])


def test_drain3_is_fitted_on_train_then_match_only(tmp_path: Path) -> None:
    protocol = {"drain3": {"sim_th": 0.4, "depth": 4, "max_children": 100}}
    train = pd.Series(["Receiving block blk_1", "Received block blk_2"])
    state = tmp_path / "drain_state.bin"
    miner, audit = fit_frozen_drain(train, protocol, state)
    before = sha256_file(state)
    before_clusters = len(miner.drain.clusters)
    frame = pd.DataFrame({"message": ["Receiving block blk_9", "unknown validation message"]})
    identifiers = assign_templates(miner, frame)
    assert len(identifiers) == 2
    assert audit["add_log_message_calls"] == len(train)
    assert audit["fit_partition"] == "train_only"
    assert audit["inference_method"] == "match_only"
    assert sha256_file(state) == before
    assert len(miner.drain.clusters) == before_clusters


def test_cicids_scaler_is_not_fitted_on_test() -> None:
    model = candidate_models(42)["LogisticRegression"]
    x_train = pd.DataFrame({"a": [-1.0, 1.0], "b": [0.0, 0.0]})
    y_train = pd.Series([0, 1])
    x_test = pd.DataFrame({"a": [100.0, 200.0], "b": [100.0, 200.0]})
    model.fit(x_train, y_train)
    _ = model.predict(x_test)
    np.testing.assert_allclose(model.named_steps["scale"].mean_, x_train.mean().to_numpy())


def test_threshold_selection_has_no_test_input() -> None:
    validation_truth = np.asarray([0, 0, 1, 1])
    validation_scores = np.asarray([0.1, 0.2, 0.8, 0.9])
    first, _ = select_threshold(validation_truth, validation_scores)
    hypothetical_test = np.asarray([1000.0, -1000.0])
    second, _ = select_threshold(validation_truth, validation_scores)
    assert hypothetical_test.shape == (2,)
    assert first == second


def test_bgl_groups_are_exhaustive_and_disjoint() -> None:
    masks = group_masks(np.asarray([0, 2, 0, 7]))
    assert np.array_equal(masks["ALL"], masks["KNOWN_TEMPLATE"] | masks["UNKNOWN_TEMPLATE"])
    assert not np.any(masks["KNOWN_TEMPLATE"] & masks["UNKNOWN_TEMPLATE"])


def test_router_sources_are_unique_and_not_chunks() -> None:
    config = json.loads((ROOT / "experiments/phase_dataset_strengthening/configs/router_independent_sources.json").read_text(encoding="utf-8"))
    ids = [row["source_id"] for row in config["sources"]]
    paths = [row["path"] for row in config["sources"]]
    assert len(ids) == len(set(ids))
    assert len(paths) == len(set(paths))
    assert all("chunk" not in source_id.lower() for source_id in ids)
    assert all("chunk" not in path.lower() for path in paths)


def test_route_dataframe_normalizes_cicids_header_whitespace() -> None:
    frame = pd.DataFrame(
        {
            " Destination Port": [80],
            " Flow Duration": [100],
            " Total Fwd Packets": [3],
            " Total Backward Packets": [2],
            " Flow Bytes/s": [42],
            " Flow Packets/s": [5],
            " Label": ["BENIGN"],
        }
    )
    route = route_dataframe(frame)
    assert route["family"] == "network_cicids"


def test_route_dataframe_ignores_empty_common_schema_columns() -> None:
    frame = pd.DataFrame(
        {
            "dataset": ["bgl"],
            "subtype": ["bgl"],
            "event": ["-"],
            "source": ["KERNEL"],
            "component": ["KERNEL"],
            "severity": ["INFO"],
            "host": ["R02-M1"],
            "message": ["instruction cache parity error corrected"],
            "recno": [""],
            "session": [""],
            "src_ip": [""],
            "dst_ip": [""],
            "src_port": [""],
            "dst_port": [""],
            "proto": [""],
        }
    )
    route = route_dataframe(frame)
    assert route["family"] == "bgl"


def test_multiformat_text_selection_does_not_duplicate(tmp_path: Path) -> None:
    source = tmp_path / "source.log"
    source.write_text("one\ntwo\nthree\n", encoding="utf-8")
    selected = select_text_lines(source, tmp_path / "selected.log", 2)
    assert selected == ["one", "two"]
    assert len(selected) == len(set(selected))


def test_agent_message_contract_has_exactly_seven_fields() -> None:
    message = AgentMessage("run", "a", "b", "CFP", {"contract_id": "c"}, "ok")
    assert list(asdict(message)) == ["run_id", "source", "target", "message_type", "payload", "status", "timestamp"]
    assert "contract_id" in message.payload


def test_cnp_preserves_end_to_end_run_id() -> None:
    def handler(task: AgentTask, context: object) -> dict[str, str]:
        return {"run_id": str(task.payload["end_to_end_run_id"])}

    agent = MultiTaskIntelligentAgent(
        agent_id="agent-test",
        capabilities=[AgentCapability("test", ("pipeline.test",))],
        handlers={"pipeline.test": handler},
        memory_enabled=False,
    )
    agent.run_id = "e2e-run"
    coordinator = ContractNetCoordinator([agent], run_id="e2e-run")
    outcome = coordinator.negotiate(AgentTask.create("pipeline.test", {"end_to_end_run_id": "e2e-run"}))
    assert outcome.result is not None
    assert outcome.result.output["run_id"] == "e2e-run"
    assert all(message.run_id == "e2e-run" for message in coordinator.transcript)


def test_dataset_configs_have_hashable_sources() -> None:
    config = json.loads((ROOT / "experiments/phase_dataset_strengthening/configs/multiformat_balanced_protocol.json").read_text(encoding="utf-8"))
    for item in config["formats"]:
        path = ROOT / item["source"]
        assert path.exists()
        assert len(item["source_sha256"]) == 64
        assert sha256_file(path) == item["source_sha256"]


def test_hdfs_and_bgl_parsers_emit_normalized_rows(tmp_path: Path) -> None:
    hdfs_path = tmp_path / "hdfs.log"
    hdfs_path.write_text("081109 203518 143 INFO dfs.DataNode$DataXceiver: Receiving block blk_-1 src: /10.0.0.1:1 dest: /10.0.0.2:2\n", encoding="utf-8")
    hdfs_writer = RowCollector()
    HdfsParser().parse(str(hdfs_path), hdfs_writer)
    assert hdfs_writer.rows[0]["dataset"] == "hdfs"
    assert hdfs_writer.rows[0]["event"] == "blk_-1"

    bgl_path = tmp_path / "bgl.log"
    bgl_path.write_text("- 1117838570 2005.06.03 R02-M1-N0-C:J12-U11 2005-06-03-15.42.50.363779 R02-M1-N0-C:J12-U11 RAS KERNEL INFO instruction cache parity error corrected\n", encoding="utf-8")
    bgl_writer = RowCollector()
    BglParser().parse(str(bgl_path), bgl_writer)
    assert bgl_writer.rows[0]["dataset"] == "bgl"
    assert bgl_writer.rows[0]["message"]


def test_temporal_files_are_disjoint() -> None:
    directory = ROOT / "data/raw/Datasets/MachineLearningCSV/MachineLearningCVE"
    train, test = temporal_files(directory)
    assert {path.resolve() for path in train}.isdisjoint({path.resolve() for path in test})
    assert all(path.name.lower().startswith("friday") for path in test)


def test_external_protocol_uses_distinct_official_objects_without_test_selection() -> None:
    config = json.loads(
        (ROOT / "experiments/phase_dataset_strengthening/configs/external_csecicids2018_protocol.json").read_text(
            encoding="utf-8"
        )
    )
    train = config["partition"]["train"]
    test = config["partition"]["test"]
    assert config["official_bucket"] == "s3://cse-cic-ids2018/"
    assert train["object_key"] != test["object_key"]
    assert train["day"] != test["day"]
    assert train["url"].startswith("https://cse-cic-ids2018.s3.ca-central-1.amazonaws.com/")
    assert test["url"].startswith("https://cse-cic-ids2018.s3.ca-central-1.amazonaws.com/")
    assert config["model_or_threshold_selection_on_test"] is False
    assert config["decision_threshold"] == 0.5


def test_external_features_exclude_timestamp_label_and_identifiers(tmp_path: Path) -> None:
    header = "Flow ID,Src IP,Dst IP,Timestamp,Dst Port,Flow Duration,Label\n"
    train = tmp_path / "train.csv"
    test = tmp_path / "test.csv"
    train.write_text(header, encoding="utf-8")
    test.write_text(header, encoding="utf-8")
    columns, differences = external_feature_columns(train, test)
    assert columns == ["Dst Port", "Flow Duration"]
    assert differences == {"train_only": [], "test_only": []}


def test_external_scaler_is_fitted_on_train_only() -> None:
    model = external_candidate_models(42)["LogisticRegression"]
    x_train = pd.DataFrame({"a": [-2.0, 2.0], "b": [1.0, 1.0]})
    y_train = pd.Series([0, 1])
    x_test = pd.DataFrame({"a": [1000.0, 2000.0], "b": [500.0, 700.0]})
    model.fit(x_train, y_train)
    _ = model.predict(x_test)
    np.testing.assert_allclose(model.named_steps["scale"].mean_, x_train.mean().to_numpy())


def test_external_seed_sample_has_no_duplicate_source_rows() -> None:
    pool = pd.DataFrame(
        {
            "feature": np.arange(40),
            "target": [0] * 20 + [1] * 20,
            "__source_row": np.arange(40),
            "__priority": np.linspace(0, 1, 40),
        }
    )
    sample = external_seed_sample(pool, per_class=10, seed=42)
    assert len(sample) == 20
    assert sample["__source_row"].is_unique
    assert sample["target"].value_counts().to_dict() == {0: 10, 1: 10}


def test_external_deduplication_drops_ambiguous_feature_vectors() -> None:
    frame = pd.DataFrame(
        {
            "a": [1, 1, 2, 3, 3],
            "b": [4, 4, 5, 6, 6],
            "target": [0, 0, 1, 0, 1],
            "__source_row": np.arange(5),
            "__priority": np.linspace(0, 1, 5),
        }
    )
    result, audit = deduplicate_unambiguous(frame, ["a", "b"])
    assert len(result) == 2
    assert set(result["a"]) == {1, 2}
    assert audit["conflicting_hashes"] == 1
    assert audit["conflicting_rows_dropped"] == 2
