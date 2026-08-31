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

Retrieval date: 2026-08-31
Source rows: SRC-TAR-963, SRC-TAR-60, SRC-TAR-278, SRC-REFRESH-EVN-20260831, SRC-REFRESH-MOIT-20260709, SRC-REFRESH-MOIT-20260611, SRC-REFRESH-EVN-20260730, SRC-REFRESH-EVN-BULLETIN-20260831, SRC-REFRESH-TAX-20260831

## Remote live-check provenance

- Workflow: 33364978503; job: 99403637315; metadata commit: b362990222c1094cdaca1fd27727cb6cd7c9e1dd; artifact: 9747970647; artifact digest: sha256:ac5be014c1e70ac410644d15de925add5c6e73a9e295f0447e7c4c71999ab44f.
- Live-check file: evidence/REMOTE_SOURCE_LIVE_CHECK.csv; GitHub blob 5147275bf286ac594bf31beb694faaafe1c5880c; SHA-256 d5ee76a9ad4db76ae2ab0c242876356ffc1840613e10e9fcd037d1be5420ebaa; 12 rows; 10 PASS and 2 non-blocking WARNs.
- The NREL comparator endpoint returned a DNS warning on the runner. This is preserved as WARN and is not treated as evidence that the source is unavailable or that the model can claim certification.
- All 11 rows record raw_snapshot_stored=FALSE and storage_boundary=REMOTE_RUNNER_EPHEMERAL.

- Latest live-check result: 12 rows; 10 PASS and 2 non-blocking WARNs (MOIT runner network-unreachable; NREL DNS). Warnings are retained for recheck and do not alter model inputs.

## Core validation after SR-1.10 evidence refresh

- Push workflow 33362871604 / job 99397534044 completed successfully after the EVN corroboration was added; artifact 9747272913, digest sha256:d98e61282a9fbc564bc5078a805d64009ef1f2906a288cb3ec541f4704db93d6.
- Remote checks remained green: 20/20 data quality, 20/20 dynamic QA, 31/31 workbook checks, 7/7 tests and 13 PASS plus 1 intentional candidate WARN in release controls.
- The rebuilt native workbook was 22 sheets, 116807 bytes, SHA-256 e01406f644ab6a9d810ca6dd5c31d240ec2ed99ff7f73e593d0f756cae2ff03a; GitHub blob c45b996de6cc364062966638da73666629179638.
- Same-head repeat 33362978966 / job 99397849553 and remote comparator 33363289510 / job 99398752408 matched all six target files; comparator artifact 9747403047, digest sha256:6ac16bc4879ef269180cee5032d177a57b05a372dd8bcc69cc45c7adc99bf0a3; comparison CSV SHA-256 eb571d45c45d54babb7e7dc23373d9ce35cec6fdcc2155420bca7546d42f79c0; raw artifact contents were not stored.
