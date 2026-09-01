import csv
from pathlib import Path

def test_selected_data_contract_has_observed_fields():
    p=Path("data/public/project_master_real.csv")
    with p.open(encoding="utf-8") as f: row=next(csv.DictReader(f))
    for key in ("installed_capacity_kwp_observed","annual_generation_kwh_observed","self_consumption_observed","legacy_model_input_status"):
        assert key in row
    assert row["legacy_model_input_status"].startswith("RETAINED_")
