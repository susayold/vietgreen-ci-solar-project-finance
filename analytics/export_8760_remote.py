"""Export derived 8,760 profiles to remote workflow artifacts only.

The runner writes both plan-specified Parquet streams and compressed CSV
compatibility streams to the ephemeral GitHub Actions workspace. Neither
hourly stream is committed to the public repository or the desktop workspace.
"""
from __future__ import annotations

import csv
import gzip
import hashlib
import io
from pathlib import Path

import pyarrow as pa
import pyarrow.parquet as pq

from analytics.load_match_8760 import profile

ROOT = Path(__file__).resolve().parents[1]
PVOUT = {"North": 1320.0, "Central": 1480.0, "South": 1420.0}


def projects():
    with (ROOT / "data/synthetic/project_master.csv").open(
        newline="", encoding="utf-8"
    ) as handle:
        return list(csv.DictReader(handle))


def write_profile(path, records, fields):
    """Write a byte-reproducible gzip CSV stream to the ephemeral runner."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("wb") as raw_handle:
        with gzip.GzipFile(
            fileobj=raw_handle, mode="wb", filename="", mtime=0
        ) as compressed:
            with io.TextIOWrapper(
                compressed, newline="", encoding="utf-8"
            ) as handle:
                writer = csv.DictWriter(handle, fieldnames=fields)
                writer.writeheader()
                writer.writerows(records)


def write_parquet(path, records):
    path.parent.mkdir(parents=True, exist_ok=True)
    table = pa.Table.from_pylist(records)
    pq.write_table(
        table,
        path,
        compression="zstd",
        version="2.6",
        data_page_version="1.0",
        write_statistics=True,
        use_dictionary=True,
    )


def main():
    loads, solars = [], []
    load_parquet_rows, solar_parquet_rows = [], []
    for project in projects():
        p50 = float(project["proposed_capacity_kwp"]) * PVOUT[project["region"]]
        hourly = profile(
            float(project["annual_load_kwh"]),
            p50,
            float(project["daytime_load_share"]),
        )
        for i, timestamp in enumerate(hourly["timestamps"]):
            load_kwh = hourly["load"][i]
            solar_kwh = hourly["solar"][i]
            self_consumed_kwh = hourly["self_consumed"][i]
            excess_kwh = hourly["excess"][i]
            loads.append(
                {
                    "project_id": project["project_id"],
                    "timestamp_local": timestamp,
                    "load_kwh": "%.10f" % load_kwh,
                }
            )
            solars.append(
                {
                    "project_id": project["project_id"],
                    "timestamp_local": timestamp,
                    "solar_kwh_p50": "%.10f" % solar_kwh,
                    "self_consumed_kwh": "%.10f" % self_consumed_kwh,
                    "excess_kwh": "%.10f" % excess_kwh,
                }
            )
            load_parquet_rows.append(
                {
                    "project_id": project["project_id"],
                    "timestamp_local": timestamp,
                    "load_kwh": float(load_kwh),
                }
            )
            solar_parquet_rows.append(
                {
                    "project_id": project["project_id"],
                    "timestamp_local": timestamp,
                    "solar_kwh_p50": float(solar_kwh),
                    "self_consumed_kwh": float(self_consumed_kwh),
                    "excess_kwh": float(excess_kwh),
                }
            )

    load_csv_gz = ROOT / "remote_derived/load_8760.csv.gz"
    solar_csv_gz = ROOT / "remote_derived/solar_8760.csv.gz"
    load_parquet = ROOT / "remote_derived/load_8760.parquet"
    solar_parquet = ROOT / "remote_derived/solar_8760.parquet"

    write_profile(load_csv_gz, loads, ["project_id", "timestamp_local", "load_kwh"])
    write_profile(
        solar_csv_gz,
        solars,
        ["project_id", "timestamp_local", "solar_kwh_p50", "self_consumed_kwh", "excess_kwh"],
    )
    write_parquet(load_parquet, load_parquet_rows)
    write_parquet(solar_parquet, solar_parquet_rows)

    index = []
    for path, count in (
        (load_csv_gz, len(loads)),
        (solar_csv_gz, len(solars)),
        (load_parquet, len(load_parquet_rows)),
        (solar_parquet, len(solar_parquet_rows)),
    ):
        index.append(
            {
                "path": str(path.relative_to(ROOT)).replace("\\", "/"),
                "row_count": count,
                "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                "storage": "GitHub Actions artifact",
                "local_storage": "NONE",
            }
        )

    with (ROOT / "validation/REMOTE_8760_INDEX.csv").open(
        "w", newline="", encoding="utf-8"
    ) as handle:
        writer = csv.DictWriter(handle, fieldnames=list(index[0]))
        writer.writeheader()
        writer.writerows(index)


if __name__ == "__main__":
    main()
