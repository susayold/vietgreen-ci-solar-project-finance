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

## Claim boundary

The model keeps LEGAL_EFFECTIVE_NOT_BILLED, CURRENT_BILLED_REFERENCE, and SIMULATED_MODEL_INPUT as separate statuses. billing_status=WATCH remains a hard release limitation until a directly applicable utility/EVN billing record or authoritative implementation notice shows the invoice effective date.

## Official URLs

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
Source rows: SRC-TAR-963, SRC-TAR-60, SRC-TAR-278, SRC-REFRESH-EVN-20260831, SRC-REFRESH-EVN-BULLETIN-20260831, SRC-REFRESH-EVN-20260730, SRC-REFRESH-MOIT-20260709, SRC-REFRESH-TAX-20260831, SRC-SOLAR-GSA, SRC-SOLAR-NREL, SRC-REFRESH-EVN-963-20260423, SRC-REFRESH-MOIT-20260611, SRC-REFRESH-EVNSPC-20260715, SRC-REFRESH-EVNSPC-PRICING-20260831, SRC-REFRESH-EVNSPC-TRAINING-20260527, SRC-REFRESH-EVNSPC-IT-20260525

## Remote live-check provenance

- Workflow: 33366510106; job: 99408166781; metadata commit: 116c80ea7559cb55d9db11484bc7529177c77c8c; artifact: 9748486524; artifact digest: sha256:bbafe54b9991fb90b74ce39ca089c6b937855660411c3cfe859da506bff327aa.
- Live-check file: evidence/REMOTE_SOURCE_LIVE_CHECK.csv; GitHub blob 0619516e76b7de44059f2a0cc1f342e1e4c9715c; SHA-256 1accde29ebc20aabf8967a77acfcf968bd9092000e75511903546e92f73fd0a9; 16 rows; 13 PASS and 3 non-blocking WARNs.
- The two MOIT runner network-unreachable and NREL DNS warnings are preserved as WARNs and are not treated as evidence that a source is unavailable or that the model can claim certification.
- All 16 rows record raw_snapshot_stored=FALSE and storage_boundary=REMOTE_RUNNER_EPHEMERAL.

- Latest live-check result: 16 rows; 13 PASS and 3 non-blocking WARNs (MOIT runner network-unreachable on two pages; NREL DNS). Warnings are retained for recheck and do not alter model inputs.

## Core validation lineage after core model refresh

- Push workflow 33362871604 / job 99397534044 completed successfully after the EVN corroboration was added; artifact 9747272913, digest sha256:d98e61282a9fbc564bc5078a805d64009ef1f2906a288cb3ec541f4704db93d6.
- Remote checks remained green: 20/20 data quality, 20/20 dynamic QA, 31/31 workbook checks, 7/7 tests and 13 PASS plus 1 intentional candidate WARN in release controls.
- The rebuilt native workbook was 22 sheets, 116807 bytes, SHA-256 e01406f644ab6a9d810ca6dd5c31d240ec2ed99ff7f73e593d0f756cae2ff03a; GitHub blob c45b996de6cc364062966638da73666629179638.
- Same-head repeat 33362978966 / job 99397849553 and remote comparator 33363289510 / job 99398752408 matched all six target files; comparator artifact 9747403047, digest sha256:6ac16bc4879ef269180cee5032d177a57b05a372dd8bcc69cc45c7adc99bf0a3; comparison CSV SHA-256 eb571d45c45d54babb7e7dc23373d9ce35cec6fdcc2155420bca7546d42f79c0; raw artifact contents were not stored.
