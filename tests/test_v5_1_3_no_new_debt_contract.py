import csv
from pathlib import Path

import pytest

from analytics.build_v5_1_3_economics import (
    _apply_contractual_schedule,
    _contractual_schedule_for_mode,
    _schedule_signature,
)

ROOT = Path(__file__).resolve().parents[1]


def _rows():
    with (ROOT / "outputs/v5_1_3_scenarios.csv").open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def _scenario(sid):
    return [r for r in _rows() if r["scenario_id"] == sid]


def test_scenario_row_count():
    assert len(_rows()) == 19 * 9


@pytest.mark.parametrize("sid", ["CAPEX_OVERRUN", "OFFTAKER_TERMINATION", "COMBINED_DOWNSIDE"])
def test_no_new_debt_principal_opening_closing_preserved(sid):
    for r in _scenario(sid):
        assert r["debt_mode"] == "NO_NEW_DEBT"
        assert r["principal_schedule_preserved"] == "TRUE"
        assert r["opening_schedule_preserved"] == "TRUE"
        assert r["closing_schedule_preserved"] == "TRUE"


@pytest.mark.parametrize("sid", ["CAPEX_OVERRUN", "OFFTAKER_TERMINATION", "COMBINED_DOWNSIDE"])
def test_no_new_debt_is_zero(sid):
    for r in _scenario(sid):
        assert abs(float(r["additional_debt_local"])) < 1e-7
        assert r["no_new_debt_increase"] == "TRUE"


def test_capex_equity_funding():
    for r in _scenario("CAPEX_OVERRUN"):
        assert float(r["equity_funded_incremental_capex_local"]) == pytest.approx(float(r["incremental_capex_local"]))


def test_combined_equity_funding():
    for r in _scenario("COMBINED_DOWNSIDE"):
        assert float(r["equity_funded_incremental_capex_local"]) == pytest.approx(float(r["incremental_capex_local"]))


def test_combined_floating_rate_reprices_interest_only():
    for r in _scenario("COMBINED_DOWNSIDE"):
        assert r["interest_schedule_changed"] == "TRUE"
        assert r["principal_schedule_preserved"] == "TRUE"


@pytest.mark.parametrize("sid", ["P90_ENERGY", "COD_DELAY", "OPEX_INFLATION", "OFFTAKER_NONPAYMENT"])
def test_fixed_contractual_schedule_preserved(sid):
    for r in _scenario(sid):
        assert r["debt_mode"] == "FIXED_CONTRACTUAL_SCHEDULE"
        assert r["principal_schedule_preserved"] == "TRUE"
        assert r["opening_schedule_preserved"] == "TRUE"
        assert r["closing_schedule_preserved"] == "TRUE"


def test_lower_cfads_cannot_lower_contractual_principal():
    base = [{"opening": 100.0, "interest": 8.0, "principal": 30.0, "debt_service": 38.0, "closing": 70.0}]
    stressed = _apply_contractual_schedule(base, [30.0], 0.08, 0.08, "FIXED_REFERENCE")
    assert _schedule_signature(base, "principal") == _schedule_signature(stressed, "principal")


def test_unknown_debt_mode_fails_closed():
    with pytest.raises(ValueError):
        _contractual_schedule_for_mode("UNSUPPORTED", [], [], 0.08, 0.08, "FLOATING_REFERENCE")


def test_floating_rate_fixture():
    base = [{"opening": 100.0, "interest": 8.0, "principal": 30.0, "debt_service": 38.0, "closing": 70.0}]
    stressed = _apply_contractual_schedule(base, [30.0], 0.08, 0.10, "FLOATING_REFERENCE")
    assert stressed[0]["interest"] == pytest.approx(10.0)
    assert stressed[0]["principal"] == pytest.approx(30.0)
    assert stressed[0]["closing"] == pytest.approx(70.0)


def test_fixed_rate_fixture():
    base = [{"opening": 100.0, "interest": 8.0, "principal": 30.0, "debt_service": 38.0, "closing": 70.0}]
    stressed = _apply_contractual_schedule(base, [30.0], 0.08, 0.10, "FIXED_REFERENCE")
    assert stressed[0]["interest"] == pytest.approx(8.0)
    assert stressed[0]["principal"] == pytest.approx(30.0)


def test_cod_regression():
    for r in _scenario("COD_DELAY"):
        assert r["first_operating_year"] == "2"
        assert float(r["year_1_revenue_local"]) == 0.0
        assert float(r["year_1_depreciation_local"]) == 0.0


def test_arithmetic_output_contract():
    required = {
        "base_debt_local", "scenario_debt_local", "additional_debt_local",
        "base_opening_schedule_signature", "scenario_opening_schedule_signature",
        "base_principal_schedule_signature", "scenario_principal_schedule_signature",
        "base_closing_schedule_signature", "scenario_closing_schedule_signature",
        "base_interest_schedule_signature", "scenario_interest_schedule_signature",
        "base_debt_service_signature", "scenario_debt_service_signature",
        "equity_funded_incremental_capex_local", "min_dscr", "llcr", "plcr",
    }
    assert required.issubset(_rows()[0])
