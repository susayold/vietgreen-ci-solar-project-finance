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

    debt_rows = load("debt")["rows"]
    assert len(debt_rows) == 19
    go_debt = next(row for row in debt_rows if row["projectId"] == "VN-GY-GOMALL")
    assert go_debt["bindingConstraint"] == "PLCR"
    assert close(go_debt["minimumDscr"], 2.380)
    assert close(go_debt["plcr"], 1.336)
    schedule = go_debt["schedule"]
    assert len(schedule) == 15
    assert close(schedule[0]["debtService"], schedule[0]["principal"] + schedule[0]["interest"])
    assert all(row["closingDebt"] == 0 for row in schedule)
    assert all(row["debtService"] == 0 and row["dscr"] is None for row in schedule[1:])

    risk = load("risk")
    assert risk["rowCount"] == 171 and len(risk["rows"]) == 171
    assert len({(row["projectId"], row["scenarioId"]) for row in risk["rows"]}) == 171
    assert len(risk["scenarioDefinitions"]) == 9

    diligence = load("diligence")
    assert len(diligence["rows"]) == 20
    assert sum(row["economicsStatus"] == "READY_FOR_ECONOMICS" for row in diligence["rows"]) == 19
    assert sum(row["physicalStatus"] == "EXTREME_OUTLIER_BLOCK_BASE" for row in diligence["rows"]) == 1
    assert diligence["budgetUsd"] == diligence["approvedAllocationsUsd"] == 0

    reconciliation = load("reconciliation")["rows"]
    assert all(row["ok"] for row in reconciliation)
    assert load("release")["modelSha"] == SHA
    assert load("website-release")["modelSha"] == SHA
    print("website data validation: PASS")


if __name__ == "__main__":
    main()


