from pathlib import Path
import runpy


def patch(path: str, old: str, new: str, count: int = 1) -> None:
    p = Path(path)
    text = p.read_text(encoding="utf-8")
    found = text.count(old)
    if found != count:
        raise SystemExit(
            f"{path}: expected {count} occurrence(s), found {found}: {old[:140]!r}"
        )
    p.write_text(text.replace(old, new), encoding="utf-8")


# The first closure script deliberately uses exact-match guards. One wrapped
# sentence has only one exact occurrence in the current source, not three.
closure = Path("scripts/final_content_audit_closure_patch.py")
closure_text = closure.read_text(encoding="utf-8")
needle = '    "modeled debt service before operating CFADS.",\n    count=3,\n)'
replacement = '    "modeled debt service before operating CFADS.",\n    count=1,\n)'
if closure_text.count(needle) != 1:
    raise SystemExit("closure count guard target is not exactly one occurrence")
closure.write_text(closure_text.replace(needle, replacement), encoding="utf-8")
runpy.run_path(str(closure), run_name="__main__")

# Page 6 — finish the model-vs-real-contract boundary for remaining prose.
patch(
    "app/risk/page.tsx",
    "Stress the Cash Flow —<br />\n              Not the Contract Away.",
    "Stress the Cash Flow —<br />\n              Not the Debt Schedule Away.",
)
patch(
    "app/risk/page.tsx",
    "Operating cost is stressed while debt stays contractual.",
    "Operating cost is stressed while the model-defined debt schedule stays fixed.",
)
patch(
    "app/risk/page.tsx",
    "A one-year COD delay can leave contractual debt service before\n                operating CFADS.",
    "A one-year COD delay can leave modeled debt service before\n                operating CFADS.",
)
patch(
    "app/risk/page.tsx",
    "0.000x means contractual debt service\n                exists but stressed CFADS is zero.",
    "0.000x means modeled debt service\n                exists but stressed CFADS is zero.",
)

# Strengthen the browser regression with the remaining prohibited wording.
test_path = Path("tests/v5_1_3_website_browser.spec.mjs")
test_text = test_path.read_text(encoding="utf-8")
anchor = "  await expect(page.locator('main')).not.toContainText('CONTRACTUAL SCHEDULE SEMANTICS');"
extra = "\n  await expect(page.locator('main')).not.toContainText('Not the Contract Away');\n  await expect(page.locator('main')).not.toContainText('debt stays contractual');"
if test_text.count(anchor) != 1:
    raise SystemExit("risk claim-boundary browser-test anchor not found exactly once")
test_path.write_text(test_text.replace(anchor, anchor + extra), encoding="utf-8")
