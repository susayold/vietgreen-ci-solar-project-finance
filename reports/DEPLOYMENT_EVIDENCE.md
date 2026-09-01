# Deployment Evidence — V5.1.1

Status: DEPLOYED_EXACT_SHA_VERIFIED_IN_CI.

The Pages workflow is the authoritative deployment evidence producer. It verifies the exact checked-out SHA, live `release-meta.json`, HTTP 200 for the root and seven required JSON routes, and browser QA at 390/430/768/1024/1440px. The exact source SHA, workflow run, Pages artifact ID and digest are sealed in the uploaded CI runtime evidence and copied to the Drive control index after readback.

PPA remains FRONTIER_ONLY and the public site is a recruiter/diligence communication layer, not a bankability or transaction approval.