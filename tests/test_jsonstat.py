"""Proves del parser JSON-stat i dels controls de qualitat (sense connexió a l'API).

Executa des de l'arrel:  python -m pytest tests
"""
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from idescat_api import jsonstat_to_df  # noqa: E402
from qa import check_aggregation, check_mapping  # noqa: E402


def _dataset(geo_dim, geo_codes, geo_labels, values):
    return {
        "class": "dataset", "label": "prova", "updated": "2025-01-01",
        "id": ["YEAR", geo_dim, "CONCEPT"], "size": [2, len(geo_codes), 1],
        "role": {"time": ["YEAR"], "geo": [geo_dim], "metric": ["CONCEPT"]},
        "dimension": {
            "YEAR": {"category": {"index": ["2022", "2023"]}},
            geo_dim: {"category": {"index": {c: i for i, c in enumerate(geo_codes)},
                                   "label": dict(zip(geo_codes, geo_labels))}},
            "CONCEPT": {"category": {"index": ["GDP_ME"], "label": {"GDP_ME": "PIB (milions €)"}}},
        },
        "value": values,
        "status": {"1": "p"},
    }


COM = _dataset("COM", ["14", "22", "TOTAL"], ["Alt Penedès", "Garraf", "Catalunya"],
               [10, 20, 30, 11, 21, 32])
AT = _dataset("AT", ["AT08", "TOTAL"], ["Penedès", "Catalunya"], [30, 30, 32, 32])
MAPPING = pd.DataFrame({"comarca": ["Alt Penedès", "Garraf"], "ambit_code": ["AT08"] * 2, "ambit": ["Penedès"] * 2})


def test_parser_order_and_roles():
    df = jsonstat_to_df(COM)
    assert list(df.columns[:4]) == ["period_code", "period_label", "geo_code", "geo_label"]
    assert len(df) == 6
    # Ordre row-major: 2023 / Garraf ha de ser el 5è valor (21)
    row = df[(df.period_code == "2023") & (df.geo_code == "22")]
    assert row["value"].item() == 21
    assert df.loc[1, "status"] == "p"


def test_mapping_ok():
    assert check_mapping(jsonstat_to_df(COM), MAPPING) == []


def test_aggregation_ok_and_detects_error():
    issues, _ = check_aggregation(jsonstat_to_df(COM), jsonstat_to_df(AT), MAPPING, ["GDP_ME"])
    assert issues == []
    bad = dict(AT, value=[99, 30, 32, 32])
    issues, _ = check_aggregation(jsonstat_to_df(COM), jsonstat_to_df(bad), MAPPING, ["GDP_ME"])
    assert len(issues) == 1
