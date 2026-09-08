from pathlib import Path


def patch(path: str, old: str, new: str, count: int = 1) -> None:
    p = Path(path)
    text = p.read_text(encoding="utf-8")
    found = text.count(old)
    if found != count:
        raise SystemExit(
            f"{path}: expected {count} occurrence(s), found {found}: {old[:140]!r}"
        )
    p.write_text(text.replace(old, new), encoding="utf-8")


# Page 3 — surplus is modeled; no grid-export entitlement is evidenced.
patch(
    "app/energy/page.tsx",
    "09:00 – 15:00<b>Solar &gt; load, self-consumption + export</b>",
    "09:00 – 15:00<b>Solar &gt; load, self-consumption + modeled surplus</b>",
)

# Page 6 — keep the internal debt-mode enum unchanged, but never present it as
# an executed contractual schedule in recruiter-facing copy.
patch(
    "app/risk/page.tsx",
    "function Heading({\n  n,",
    "function displayDebtMode(mode: string) {\n  if (mode === 'FIXED_CONTRACTUAL_SCHEDULE') return 'MODEL-DEFINED FIXED SCHEDULE';\n  return mode.replaceAll('_', ' ');\n}\n\nfunction Heading({\n  n,",
)
patch(
    "app/risk/page.tsx",
    "<dd>{scenario.mode.replaceAll('_', ' ')}</dd>",
    "<dd>{displayDebtMode(scenario.mode)}</dd>",
)
patch(
    "app/risk/page.tsx",
    "For fixed-contractual and no-new-debt cases, opening, principal",
    "For model-defined fixed-schedule and no-new-debt cases, opening, principal",
)
patch(
    "app/risk/page.tsx",
    "{scenario.mode.replaceAll('_', ' ')}",
    "{displayDebtMode(scenario.mode)}",
    count=2,
)
patch(
    "app/risk/page.tsx",
    "`${project.project_name}, ${scenario.label}, minimum DSCR ${formatCoverage(value)}, ${SCENARIOS.find((item) => item.id === scenario.id)?.mode}`",
    "`${project.project_name}, ${scenario.label}, minimum DSCR ${formatCoverage(value)}, ${displayDebtMode(SCENARIOS.find((item) => item.id === scenario.id)?.mode ?? 'NOT AVAILABLE')}`",
)

# Page 7 — traceability is supported; an independent audit is explicitly not.
patch(
    "app/diligence/page.tsx",
    'note="Every reduction in the universe is explicit and auditable."',
    'note="Every reduction in the universe is explicit and traceable."',
)

# Add regression assertions for the exact residues caught in the final readback.
test_path = Path("tests/v5_1_3_website_browser.spec.mjs")
test_text = test_path.read_text(encoding="utf-8")
energy_anchor = "  await expect(page.locator('.energy-takeaway')).toContainText('Traceable and reproducible');"
energy_extra = "\n  await expect(page.locator('main')).not.toContainText('self-consumption + export');"
if test_text.count(energy_anchor) != 1:
    raise SystemExit("energy residual-test anchor not found exactly once")
test_text = test_text.replace(energy_anchor, energy_anchor + energy_extra)
risk_anchor = "  await expect(page.locator('main')).not.toContainText('debt stays contractual');"
risk_extra = "\n  await expect(page.locator('main')).not.toContainText('FIXED CONTRACTUAL SCHEDULE');\n  await expect(page.locator('main')).toContainText('MODEL-DEFINED FIXED SCHEDULE');"
if test_text.count(risk_anchor) != 1:
    raise SystemExit("risk residual-test anchor not found exactly once")
test_text = test_text.replace(risk_anchor, risk_anchor + risk_extra)
diligence_anchor = "  await expect(page.locator('main')).not.toContainText('Structured, auditable analysis');"
diligence_extra = "\n  await expect(page.locator('main')).not.toContainText('explicit and auditable');"
if test_text.count(diligence_anchor) != 1:
    raise SystemExit("diligence residual-test anchor not found exactly once")
test_text = test_text.replace(diligence_anchor, diligence_anchor + diligence_extra)
test_path.write_text(test_text, encoding="utf-8")
