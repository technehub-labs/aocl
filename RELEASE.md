# Release checklist — aocl

Cutting vX.Y.Z (pattern adopted from the `mama` toolkit's proven pipeline):

1. **CI green on main** — all jobs (test, site, docs, schemas).
2. **Fold the changelog** — collapse `## [Unreleased]` into `## [vX.Y.Z] — YYYY-MM-DD`. The release workflow publishes that section verbatim as release notes; write it for users.
3. **Set versions** — `version` in `pyproject.toml`. If assessment items, level definitions, vector set, aggregation rule, or the realization formula changed, bump `RULESET_VERSION` (MAJOR per [docs/versioning.md](docs/versioning.md)) in **both** `src/aocl/assess.py` (+ `realization.py`) **and** `site/scoring.js`, and update `tests/corpus.json` in the same change (the corpus gate blocks release otherwise).
4. **Parity green (release blocker)**:
   ```bash
   python3 tools/aocl_score.py --self-test && python3 tools/aocl_realization.py --self-test
   python3 tools/aocl_ledger.py --self-test && python3 tools/aocl_model.py --self-test
   node tools/site_selftest.js && node tools/corpus_check.js && python3 tools/corpus_check.py
   ```
5. **PR merge**, then tag and push: `git tag vX.Y.Z && git push origin vX.Y.Z`.
6. **Release workflow** builds wheel+sdist (smoke-tested in a fresh venv), builds PyInstaller one-file binaries for macOS arm64 / Linux x86_64 / Windows x86_64 (each gate-tested with `--self-test`), and publishes the GitHub Release with `SHA256SUMS.txt`.
7. **Verify** — download the macOS binary, run `aocl-score --self-test`.
8. **PyPI (optional)** — one-time trusted-publisher configuration on PyPI for this repo, then dispatch `publish-pypi.yml`. Fallback package name if `aocl` is taken: `aocl-toolkit` (rename in `pyproject.toml` before building).
9. Move the kanban item to Done.

## Bump classes

| Change | RULESET_VERSION | model_version | ledger `schema` |
|---|---|---|---|
| Doc fixes, self-test-only changes | — | — | — |
| New optional outputs, new model fields (additive) | PATCH/MINOR | MINOR | — |
| Re-worded assessment items (clarification) | MINOR + changelog note | MINOR | — |
| Items, levels, vectors, aggregation rule, formula | **MAJOR** | **MAJOR** | MAJOR if fields change |
