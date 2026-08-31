# REMOTE_STORAGE_POLICY

1. The plan was read from the user-supplied Downloads path for analysis only.
2. No source copy, raw snapshot, project data or generated artifact is written to the local workspace.
3. Synthetic data, metadata, code and public release artifacts are stored on GitHub.
4. The Drive control document stores the execution record and links.
5. GitHub Actions is the remote execution surface; runner storage is ephemeral.
6. Hidden truth and private/proprietary data are excluded from this public repository.

7. Official-source refreshes run on a manually dispatched GitHub Actions runner; response bodies are read and hashed in memory, while only status/hash metadata is committed to GitHub. No raw public source snapshot is stored locally or in the repository.
