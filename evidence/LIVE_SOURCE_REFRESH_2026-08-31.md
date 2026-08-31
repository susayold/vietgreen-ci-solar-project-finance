# LIVE_SOURCE_REFRESH_2026-08-31

Remote evidence note for the candidate release. Raw snapshots are intentionally not stored on the desktop or in this public repository; only URLs, classifications, retrieval date, and transformation destinations are recorded.

## Fresh official retrieval

- **SRC-TAR-278 — Decree 278/2026/ND-CP:** the Government Portal records the decree as issued and effective on 09 July 2026. It amends the mechanism and timing for average retail electricity-price adjustment. It is a legal dependency for the tariff chain, not invoice-cutover evidence.
- **SRC-TAR-60 — Circular 60/2025/TT-BCT:** the Government Portal records the electricity-pricing implementation circular as issued and effective on 02 December 2025.
- **SRC-REFRESH-EVN-BULLETIN-20260831 — EVN Bulletin No. 16/2026:** EVN states the Decision 963 time windows apply with the next relevant average retail-price adjustment and records preparation activity; it does not state an invoice cutover date.
- **SRC-REFRESH-MOIT-20260611 — MOIT briefing:** the official 11 June 2026 briefing quotes EVN that the new windows had not yet been applied and were awaiting the Circular 60 amendment; it is corroborative and not invoice-cutover evidence.
- **SRC-REFRESH-EVN-20260831 — Electricity Authority/EVN notice:** the 24 April 2026 notice ties application to the Circular 60 / average-retail-price-adjustment condition and requests meter and operational preparation.
- **SRC-REFRESH-EVN-20260730 — EVN explainer:** the 30 July 2026 article describes the revised windows and mandatory TOU customer scope, while stating that the adjustment does not change the electricity price; it does not establish a billed invoice cutover date.
- **SRC-REFRESH-EVN-963-20260423 — EVN republication:** the 23 April 2026 EVN page confirms the Decision 963 legal windows and EVN implementation role; it does not establish an invoice cutover date.
- **SRC-REFRESH-EVNSPC-20260715 — EVNSPC customer notice:** the customer-service page states the new use-of-electricity time frame from 22 April 2026, including the revised peak/off-peak periods; it is utility corroboration, not a customer-specific invoice record.
- **SRC-REFRESH-EVNSPC-PRICING-20260831 — EVNSPC pricing portal:** the official portal labels the tariff information as applying from 22 April 2026 and lists Decision 963/Circular 60 references; it does not identify the project account or invoice cutover.
- **SRC-REFRESH-EVNSPC-TRAINING-20260527 — EVNSPC meter-training notice:** the official page records training for reprogramming three-time-band meters and prioritising large production customers; it describes implementation preparation and does not establish production invoice cutover.
- **SRC-REFRESH-EVNSPC-IT-20260525 — EVNSPC IT readiness note:** the official page describes system readiness and paper testing of two-component invoices; it does not establish production invoice cutover.
- **SRC-REFRESH-MOIT-20260709 — MOIT Q2 briefing:** the 09 July 2026 briefing is retained as the contemporaneous statement that Decision 963 had not yet been applied in practice.
- **SRC-REFRESH-TAX-20260831 — Government Portal tax draft:** the 28 August 2026 draft amendment to Decree 320/2025 remains consultation material and is not treated as effective tax law.

## Rolling official-source recheck

- **SRC-REG-243 — Decree 243/2026/ND-CP:** Government Portal page was reachable and recorded as a metadata-only PASS (HTTP 200); the source remains registered for regulatory lineage.
- **SRC-TAX-067, SRC-TAX-320, SRC-TAX-141 and SRC-TAX-020:** Government Portal pages for the registered tax law, decree and guidance were reachable and recorded as metadata-only PASS (HTTP 200); the 2026 draft amendment remains a separate WATCH item and no effective model-tax input changed.
- **SRC-FX-008 and SRC-FX-019:** Government Portal pages for the registered foreign-borrowing rules were reachable and recorded as metadata-only PASS (HTTP 200); they remain legal/reference inputs, not proof of transaction-specific advice.
- **SRC-IRENA-2024:** the registered 2024 IRENA cost-benchmark URL returned HTTP 403 from the ephemeral runner, so it is retained as a WARN for recheck and is not used as certification evidence.

## Alternate official comparator recheck

- **SRC-SOLAR-NREL-ATB-REPORT-2024:** the official NREL ATB report URL was tested from the ephemeral runner and returned a DNS error; it remains a comparator-only WARN.
- **SRC-IRENA-2024-PUBLICATION:** the official IRENA publication landing page was tested from the ephemeral runner and returned HTTP 403; it remains a comparator-only WARN.
- These alternate URLs were retained alongside the original NREL/IRENA URLs so the inaccessible runner paths remain auditable rather than silently replaced.

## Claim boundary

The model keeps LEGAL_EFFECTIVE_NOT_BILLED, CURRENT_BILLED_REFERENCE, and SIMULATED_MODEL_INPUT as separate statuses. billing_status=WATCH remains a hard release limitation until a directly applicable utility/EVN billing record or authoritative implementation notice shows the invoice effective date.

## Official URLs

- NREL ATB 2024 report alternate: https://www.nrel.gov/docs/fy24osti/89960.pdf
- IRENA 2024 publication alternate: https://www.irena.org/Publications/2025/Jun/Renewable-Power-Generation-Costs-in-2024

- Decision 963: https://moit.gov.vn/van-ban-phap-luat/quyet-dinh-ve-khung-gio-cao-diem-thap-diem-va-gio-binh-thuong-cua-he-thong-dien-quoc-gia.html
- Decision 963 PDF: https://moit.gov.vn/upload/2005517/20260423/1_QD-BCT_2026_963_30f7a.pdf
- MOIT Q2 briefing: https://moit.gov.vn/tin-tuc/bo-cong-thuong-hop-bao-thuong-ky-quy-ii-2026.html
- Circular 60: https://vanban.chinhphu.vn/?classid=1&docid=216125&pageid=27160&typegroupid=6
- Decree 278/2026/NĐ-CP: https://vanban.chinhphu.vn/?classid=1&docid=218849&pageid=27160&typegroupid=4
- Electricity Authority / EVN notice: https://evn.com.vn/d/vi-VN/news-d/Cuc-Dien-luc-thong-tin-ve-thoi-gian-ap-dung-khung-gio-cao-diem-thap-diem-va-gio-binh-thuong-cua-he-thong-dien-quoc-gia-60-2025-507824
- EVN Bulletin No. 16/2026: https://www.evn.com.vn/userfile/User/tcdl/files/2026/4/BanTinEVNSo162026-20260428150748448.pdf
- EVN explainer: https://www.evn.com.vn/d/vi-VN/news/Dieu-chinh-khung-gio-cao-diem-Doanh-nghiep-duoc-loi-gi-60-3557-509124
- Tax draft: https://vanban.chinhphu.vn/du-thao-vbqppl/du-thao-nghi-dinh-sua-doi-bo-sung-mot-so-dieu-cua-nghi-dinh-so-320-2025-nd-cp-ngay-15-thang-12-n-7915
- EVNSPC customer notice: https://cskh.evnspc.vn/TinTuc/TinTucChiTiet?LoaiTinBai=ALL&MaTinBai=2987
- EVNSPC pricing portal: https://cskh.evnspc.vn/TraCuu/ThongTinGiaDien
- EVNSPC meter-training notice: https://evnspc.vn/bai-viet/ARTICLE26050302/evnspc-tap-huan-cai-dat-thay-doi-khung-gio-cao-diem-thap-diem-binh-thuong-cua-cong-to
- EVNSPC IT readiness note: https://it.evnspc.vn/CMS_Article/ArticleByID?ArticleID=F02WEB-202605-0000000000007

Retrieval date: 2026-08-31
Source rows: SRC-TAR-963, SRC-TAR-60, SRC-TAR-278, SRC-REFRESH-EVN-20260831, SRC-REFRESH-EVN-BULLETIN-20260831, SRC-REFRESH-EVN-20260730, SRC-REFRESH-MOIT-20260709, SRC-REFRESH-TAX-20260831, SRC-SOLAR-GSA, SRC-SOLAR-NREL, SRC-REFRESH-EVN-963-20260423, SRC-REFRESH-MOIT-20260611, SRC-REFRESH-EVNSPC-20260715, SRC-REFRESH-EVNSPC-PRICING-20260831, SRC-REFRESH-EVNSPC-TRAINING-20260527, SRC-REFRESH-EVNSPC-IT-20260525, SRC-REG-243, SRC-TAX-067, SRC-TAX-320, SRC-TAX-141, SRC-TAX-020, SRC-FX-008, SRC-FX-019, SRC-IRENA-2024, SRC-SOLAR-NREL-ATB-REPORT-2024, SRC-IRENA-2024-PUBLICATION

## Remote live-check provenance

- Workflow: 33371147810; job: 99422352549; metadata commit: 53f39020d6dfef5467768c81e18ddb19c76e9582; artifact: 9750130974; artifact digest: sha256:24d20a3bf9ee66f5eb94af620a40c3cc1352856ea97dcc413af02b4304d5b972.
- Live-check file: evidence/REMOTE_SOURCE_LIVE_CHECK.csv; GitHub blob 9a7f78b57e20ebe35502308412f2b0f536fb37fc; SHA-256 81145632b8e45ba53808ba06aa305d7434ef14f3e44ca21141c7c056d0676236; 26 rows; 20 PASS and 6 non-blocking WARNs.
- The two MOIT runner network-unreachable, NREL DNS and IRENA HTTP 403 warnings are preserved as WARNs and are not treated as evidence that a source is unavailable or that the model can claim certification.
- All 26 rows record raw_snapshot_stored=FALSE and storage_boundary=REMOTE_RUNNER_EPHEMERAL.

- Latest live-check result: 26 rows; 20 PASS and 6 non-blocking WARNs (MOIT runner network-unreachable on two pages; NREL DNS; IRENA HTTP 403). Warnings are retained for recheck and do not alter model inputs.

## Core validation lineage after core model refresh

- Push workflow 33367160495 / job 99410087552 completed successfully after the locked model-input evidence registration; artifact 9748676847, digest sha256:3f1f7c193192ca4bd652a131e453e9bd7cd996592f0f2343b081664618fdba70.
- Remote checks remained green: 20/20 data quality, 20/20 dynamic QA, 31/31 workbook checks, 7/7 tests and 13 PASS plus 1 intentional candidate WARN in release controls.
- The rebuilt native workbook is 22 sheets, 117493 bytes, SHA-256 9e72588fd7a084282befa74dd0f97036f15e1f306aac6080fc86fdd75f605c5f; GitHub blob c0d2e2dadf3720a35b9101205efdec108425bec5.
- Same-head repeat 33367239508 / job 99410324360 and remote comparator 33367293807 / job 99410490341 matched all six target files; comparator artifact 9748718166, digest sha256:5b445b9ad1b8b292edf19197ca25b7a7ecf7c4204d9d788baaed21afca483b3e; comparison CSV SHA-256 28b02df8bfa8516586597a374ac11fe02907056f3f787de34675683ab7a9b8df; raw artifact contents were not stored.
