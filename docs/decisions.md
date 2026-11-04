# Decisions

[← Overview](../ARCHITECTURE.md) · What it does: [features.md](features.md)

Why data-map is built as it is: each choice, the options set aside and why. The newest first.

## 2026-11-04 — A repository of its own, extracted from Portfolio Advisor

**Context.** Portfolio Advisor's Data tab drew its store's map (zones, lineage, statuses, columns described),
first in hand-written SVG, then on Svelte Flow once the search for existing tools had been made (its defect
DEF-055: built before checking what existed). Frantz asked for it to become a module any project can reuse,
public and under the same rules as every project of the workspace.

**Decided.**

- **What exists is reused, what is ours is the difference.** Before building, the search found:
  - *dbt docs* (`dbt docs generate`): a lineage graph of every node, for engineers; no zones, no functional
    names, no status per table or column, no host data. Kept as is for engineers; data-map is for readers.
  - *Elementary*: dbt observability (tests, anomalies) with its own report and lineage, a tool of its own with
    its tables in the warehouse; it does not embed in a host's page.
  - *Svelte Flow* (`@xyflow/svelte`, MIT): zoom, pan, minimap, fit to view, accessible nodes. Reused for the
    drawing; the layout by zones, the lineage, the inherited statuses and the detail are data-map's.
  - *ELK*, *dagre* (automatic layouts): set aside; a zone per column is the reading order wanted, a layout
    engine would reorder it.
- **Two halves and one format between them.** The producer (Python, beside dbt) and the component (Svelte, in
  the page) only share the map document. A host can produce the document another way, or draw it another way.
- **The format has one source: the Python classes.** The JSON Schema and the component's TypeScript types are
  generated from `data_map/document.py` (pydantic, then json-schema-to-typescript) and checked up to date in
  CI. Set aside: types written twice and kept aligned by hand (a fact in two places).
- **The host owns statuses, figures and notes.** data-map does not run checks nor query the warehouse: the host
  knows what "to look at" means for its data. The producer fills only what dbt knows.
- **The component ships its sources** (`.svelte` and `.ts`, compiled by the host's Vite), as Svelte libraries
  usually do; no build step of its own. Set aside: `svelte-package` to a `dist/`, a build without a consumer
  that needs it.
- **Installed from a git tag**, not from PyPI or npm: its hosts are our own projects. Publishing to the
  registries waits for a need.
- **Colours as `--dm-*` tokens**, with defaults of no weight (`:where(:root)`) any host rule overrides; **words
  as `labels`**, English by default.
- **Peers, not dependencies**: `svelte`, `@xyflow/svelte` and `@lucide/svelte` are the host's, one copy in its
  page.
