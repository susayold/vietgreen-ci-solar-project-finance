"""Validate the generated website data contract against the frozen V5.1.3 release."""

import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "public" / "data"
SHA = "ff69e15d211ff1abc88200574242ed2f1db49074"


def load(name):
    return json.loads((DATA / f"{name}.json").read_text(encoding="utf-8"))


def close(actual, expected, tolerance=1e-6):
    return math.isclose(actual, expected, rel_tol=tolerance, abs_tol=tolerance)


def main():
    summary = load("summary")
    assert summary["modelSha"] == SHA
    assert (summary["candidateProjects"], summary["selectedRecords"]) == (54, 20)
    assert (summary["economicsReadyProjects"], summary["technicalBlockedProjects"]) == (19, 1)
    assert summary["observations"] == 441
    assert close(summary["economicsReadyCapacityMw"], 129.853)
    assert close(summary["readyObservedGenerationGwh"], 148.221)
    assert (summary["modeledHourlyRows"], summary["scenarios"]) == (166440, 171)

    projects = load("projects")["projects"]
    assert len(projects) == 20
    assert sum(bool(row["economicsReady"]) for row in projects) == 19
    assert sum(bool(row["technicalDataBlocked"]) for row in projects) == 1
    assert sum(row["physicalStatus"] == "PASS_WITHIN_SCREENING_BAND" for row in projects) == 15
    assert sum(row["physicalStatus"] == "LOW_YIELD_REVIEW" for row in projects) == 4

    physical = load("physical")
    assert physical["distribution"] == {
        "PASS_WITHIN_SCREENING_BAND": 15,
        "LOW_YIELD_REVIEW": 4,
        "EXTREME_OUTLIER_BLOCK_BASE": 1,
    }

    energy = load("energy")["projects"]
    assert len(energy) == 19 and all(len(row["representativeDay"]) == 24 for row in energy)
    go_energy = next(row for row in energy if row["projectId"] == "VN-GY-GOMALL")
    for key, expected in {
        "p50Gwh": 13.0,
        "annualLoadGwh": 14.444444,
        "selfConsumedGwh": 9.308575,
        "exportedGwh": 3.691425,
        "gridPurchaseGwh": 5.135869,
        "selfConsumptionShare": 0.716044,
        "solarCoverageShare": 0.6444398,
    }.items():
        assert close(go_energy[key], expected, 1e-5), (key, go_energy[key])

    economics = load("economics")["rows"]
    assert len(economics) == 19
    go_econ = next(row for row in economics if row["projectId"] == "VN-GY-GOMALL")
    assert close(go_econ["capexUsd"], 11_250_000)
    assert close(go_econ["projectNpvUsd"], 427_000, 0.01)
    assert close(go_econ["projectIrr"], 0.1051, 1e-3)
    assert go_econ["ppaStatus"] == "EMPTY_NEGOTIATION_ZONE"
    assert close(go_econ["equityNpvUsd"], -242_000, 0.01)
    assert close(go_econ["equityIrr"], 0.1316, 1e-3)
    assert close(go_econ["customerCeilingVndKwh"], 3460)
    assert close(go_econ["sponsorFloorVndKwh"], 3575.84)
    assert close(go_econ["lenderFloorVndKwh"], 3300.14)
    assert close(go_econ["negotiationGapVndKwh"], 115.84)

    debt_rows = load("debt")["rows"]
    assert len(debt_rows) == 19
    go_debt = next(row for row in debt_rows if row["projectId"] == "VN-GY-GOMALL")
    assert go_debt["bindingConstraint"] == "LEVERAGE"
    assert close(go_debt["debtCapacityUsd"], 7_875_000)
    assert close(go_debt["equityRequirementUsd"], 3_375_000)
    assert close(go_debt["leverage"], 0.70)
    assert close(go_debt["minimumDscr"], 1.35)
    assert close(go_debt["llcr"], 1.3772)
    assert close(go_debt["plcr"], 1.6645)
    schedule = go_debt["schedule"]
    assert len(schedule) == 15
    assert close(schedule[0]["debtService"], schedule[0]["principal"] + schedule[0]["interest"])
    assert schedule[0]["openingDebt"] > schedule[-1]["closingDebt"]
    assert all(row["debtService"] > 0 for row in schedule)
    assert schedule[-1]["closingDebt"] == 0

    risk = load("risk")
    assert risk["rowCount"] == 171 and len(risk["rows"]) == 171
    assert len({(row["projectId"], row["scenarioId"]) for row in risk["rows"]}) == 171
    assert all(row["sourceStatus"] == "MODEL_OUTPUT" for row in risk["rows"])
    assert len(risk["scenarioDefinitions"]) == 9
    go_risk = {row["scenarioId"]: row for row in risk["rows"] if row["projectId"] == "VN-GY-GOMALL"}
    for scenario, expected in {
        "BASE": (1.35, 1.3772, 1.6645),
        "P90_ENERGY": (1.2062, 1.2330, 1.4890),
        "CAPEX_OVERRUN": (1.3368, 1.3675, 1.6509),
        "INTEREST_RATE_SHOCK": (1.1675, 1.3772, 1.6645),
        "COD_DELAY": (0.0, 1.2272, 1.5341),
        "OPEX_INFLATION": (1.3221, 1.3533, 1.6333),
        "OFFTAKER_NONPAYMENT": (0.9904, 1.0168, 1.2257),
        "OFFTAKER_TERMINATION": (0.0, 0.1592, 0.1592),
        "COMBINED_DOWNSIDE": (0.0, 1.0904, 1.3598),
    }.items():
        assert scenario in go_risk
        assert all(close(go_risk[scenario][key], value) for key, value in zip(("minimumDscr", "llcr", "plcr"), expected))

    diligence = load("diligence")
    assert len(diligence["rows"]) == 19
    assert sum(row["economicsStatus"] == "READY_FOR_ECONOMICS" for row in diligence["rows"]) == 19
    assert sum(row["physicalStatus"] == "EXTREME_OUTLIER_BLOCK_BASE" for row in diligence["rows"]) == 0
    assert len(diligence["technicalValidationTrack"]) == 1
    assert diligence["technicalValidationTrack"][0]["projectId"] == "IN-FPEL-ARISUDHANA"
    assert diligence["budgetUsd"] == diligence["approvedAllocationsUsd"] == 0

    reconciliation = load("reconciliation")["rows"]
    assert all(row["ok"] for row in reconciliation)
    assert load("release")["modelSha"] == SHA
    website_release = load("website-release")
    assert website_release["modelSha"] == SHA
    assert website_release["websiteSha"] not in {"pending-build-sha", "WEBSITE_SOURCE_PENDING"}
    assert website_release["websiteRunId"] not in {"pending-run-id", "CI_PENDING"}
    print("website data validation: PASS")


if __name__ == "__main__":
    main()

