"""V5.1.1 tax-loss engine. Losses are stored as positive carryforward balances."""
from __future__ import annotations
from typing import Dict

def apply_tax_loss(pre_loss_taxable_income: float, opening_loss: float, tax_rate: float) -> Dict[str, float]:
    income = float(pre_loss_taxable_income)
    opening = max(0.0, float(opening_loss))
    rate = max(0.0, float(tax_rate))
    if income >= 0:
        used = min(opening, income)
        taxable_after_loss = income - used
        closing_loss = opening - used
    else:
        used = 0.0
        taxable_after_loss = 0.0
        closing_loss = opening + abs(income)
    return {
        "pre_loss_taxable_income": income,
        "opening_loss": opening,
        "loss_used": used,
        "taxable_after_loss": taxable_after_loss,
        "tax": taxable_after_loss * rate,
        "closing_loss": closing_loss,
    }

def validate_tax_row(row: Dict[str, float]) -> None:
    if row["tax"] < -1e-8 or row["closing_loss"] < -1e-8:
        raise ValueError("tax and loss balances cannot be negative")
    if row["pre_loss_taxable_income"] < 0 and row["tax"] > 1e-8:
        raise ValueError("tax cannot be charged on a loss year")
