# Website Data Contract — V5.1.1

`analytics/build_v5_1_1_release.py` is the single CI build-time adapter between the authoritative observed/overlay inputs and the static website. It derives the website payload from the same model run that writes the V5.1.1 outputs, workbook and validation registers.

The shared contract contains release version/tag, selected-project counts, claim classes, PPA mode, decision boundary and remote-only status. Route datasets are:

- `website/data/shared-summary.json`
- `website/data/release-meta.json`
- `website/data/projects.json`
- `website/data/frontier.json`
- `website/data/risk.json`
- `website/data/evidence.json`
- `website/data/scenarios.json`

The payload intentionally excludes credentials, private transaction files and raw local snapshots. It does not claim an actual confidential PPA, lender commitment, bankability conclusion or site/engineering/tax sign-off. Exact source and artifact identity are sealed in CI runtime manifests and the Pages deployment evidence.