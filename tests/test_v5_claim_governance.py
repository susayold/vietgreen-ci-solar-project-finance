import json
from pathlib import Path
def test_surfaces_keep_claim_boundary():
 text=Path("artifacts/v5_surfaces/recruiter_package.md").read_text(encoding="utf-8")
 assert "not a bankable transaction" in text.lower()
 assert "confidential PPA" in text
 cards=json.loads(Path("artifacts/v5_website_data/project_cards.json").read_text(encoding="utf-8"))
 assert all(x["ppa_mode"]=="FRONTIER_ONLY" and x["exact_ppa_price_disclosed"] is False for x in cards["cards"])
