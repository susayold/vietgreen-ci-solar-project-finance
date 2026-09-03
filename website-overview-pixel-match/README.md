# VietGreen Overview — pixel-match slice

This folder contains the first implementation slice only: Page 1 / Overview.

- Layout follows `VIETGREEN_OVERVIEW_PIXEL_MATCH_IMPLEMENTATION_PLAN_2026-09-03.md`.
- Quantitative model values are fetched at runtime from the authoritative V5.1.3 remote `summary.json` and `physical.json` endpoints.
- No project rows, workbooks, or raw model data are copied into this folder.
- Raster assets are limited to the approved hero, contextual project, and footer texture images.

Run locally with:

```bash
npm run dev -- --host 127.0.0.1 --port 5173
```
