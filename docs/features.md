# Features catalogue

[← Overview](../ARCHITECTURE.md) · Why each choice: [decisions.md](decisions.md) · What broke:
[defects.md](defects.md)

What data-map does, each feature with a stable identifier, its type, its status and what proves it: a test that
carries its identifier (`@pytest.mark.feature("…")` in Python, the `describe` that names it in
`tests/component`), a check, or "Manual:" with the reason. `tools/check_features.py` keeps the catalogue and the
tests aligned. Functional categories follow the product: **FORMAT** (the map document), **PRODUCER** (from dbt's
manifest), **MAP** (the component). Non-functional ones follow ISO/IEC 25010: **USAB** (usability and
accessibility), **COMPAT** (compatibility), **FLEX** (flexibility), **MAINT** (maintainability), **SEC**
(security).

Version 0.1.0 is the store's map of Portfolio Advisor (its features FRONT-27 and FRONT-28, validated there on
2026-11-04), made independent of it.

| ID | Feature | Type | Status | Proof |
|---|---|---|---|---|
| FORMAT-01 | One JSON document per map: zones of nodes, each node's columns, statuses from a fixed list (sound, to look at, blocking, not built), links between nodes; a key names one node, a link joins two nodes of the map, nothing unknown passes | Functional | Done | `tests/format/test_document.py` |
| FORMAT-02 | Its JSON Schema and the component's types generated from its one source (`data_map/document.py`), checked up to date before each commit and in CI | Functional | Done | Check: `tools/build_format.py` |
| PRODUCER-01 | Each node's definition and documented columns read from dbt's manifest (a model's alias, a source's identifier), where the host gave none; what the host gives is kept | Functional | Done | `tests/producer/test_build.py` |
| PRODUCER-02 | dbt's lineage collapsed onto the nodes shown (the steps not shown walked through); what dbt cannot know (a script's inputs, a page's reads) declared by the host | Functional | Done | `tests/producer/test_build.py` |
| PRODUCER-03 | A project not parsed yet (no manifest) gives a map without definitions or links, not an error | Functional | Done | `tests/producer/test_build.py` |
| MAP-01 | A column per zone, its name above it; each node by its functional name with its status; its key and definition on hover | Functional | Done | `tests/component/map.test.ts`, `tests/component/logic.test.ts` |
| MAP-02 | The links on a switch | Functional | Done | `tests/component/map.test.ts` |
| MAP-03 | The lineage on a switch: the node picked, where it comes from and what it reaches, however far, said in words under the map | Functional | Done | `tests/component/map.test.ts`, `tests/component/logic.test.ts` |
| MAP-04 | A node without a status of its own (a page, a report) is as sound as the worst node it comes from | Functional | Done | `tests/component/logic.test.ts` |
| MAP-05 | The detail of the node picked: its key figures, each column with what it holds, its status and the host's notes; a node not built says so | Functional | Done | `tests/component/map.test.ts` |
| MAP-06 | Zoom, pan, a minimap and the fit to view (Svelte Flow); the wheel scrolls the page, the map zooms by its buttons, a pinch or Ctrl and the wheel | Functional | Done | Manual: Svelte Flow's own behaviour, seen on the demo page (`npm run dev`); jsdom lays nothing out |
| USAB-01 | WCAG AA: axe finds no violation on the map, the lineage on; a status never shown by colour alone (an icon and a word) | Non-functional | Done | `tests/component/map.test.ts` |
| USAB-02 | Every text colour reaches AA contrast on each surface, in both themes, checked from the tokens | Non-functional | Done | `tests/component/contrast.test.ts` |
| COMPAT-01 | Runs in a Svelte 5 page with `@xyflow/svelte` 1 and `@lucide/svelte` as peers; Python 3.13 and pydantic 2 for the producer; installed from a git tag | Non-functional | Done | Check: CI builds the demo page as a host would, from the lockfiles |
| FLEX-01 | The host's words replace the component's (another language, its own status names), and its colours override the `--dm-*` tokens | Non-functional | Done | `tests/component/map.test.ts` |
| MAINT-01 | Files of 150 useful lines at most, functions of 60, complexity 12, one formatter per language | Non-functional | Done | Check: `tools/check_file_size.py`, ruff, eslint, prettier |
| MAINT-02 | The same guards before each commit, before each push and in CI (`tools/hooks.py`); a push whose folder changed during its checks is refused | Non-functional | Done | `tests/tools/test_hooks.py` |
| MAINT-03 | Every test carries the features it proves; the catalogue cannot claim a feature without its proof | Non-functional | Done | Check: `tools/check_features.py` |
| MAINT-04 | Every real defect in a register with its cause, its fix and its regression test (`docs/defects.toml`) | Non-functional | Done | Check: `tools/build_defects.py` |
| SEC-01 | Secrets searched before each commit and over the whole history in CI (gitleaks, pinned by digest); dependencies from lockfiles, updates proposed weekly (Dependabot) | Non-functional | Done | Check: `tools/hooks.py`, `.github/dependabot.yml` |
