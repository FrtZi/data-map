# data-map

An interactive map of a dbt project's tables, for the people who read them: a column per zone (sources, staging,
marts, and whatever reads them), each table by its functional name with its status, its technical name and
definition on hover; the links between tables on a switch; the lineage of a table picked, where it comes from
and what it reaches; and its detail below, its key figures and each column described.

Two halves, one format:

- **A Python producer** (`data_map`) reads dbt's `manifest.json` and builds the map document: your zones, each
  table's definition and documented columns, and dbt's lineage collapsed onto the tables you show.
- **A Svelte 5 component** (`DataMap`) draws the document, on [Svelte Flow](https://svelteflow.dev) (zoom, pan,
  minimap, fit to view).
- **The map document** between them is plain JSON, described in [docs/format.md](docs/format.md); your
  application adds what only it knows: a status per table and column, key figures, notes.

It was first the store's map of Portfolio Advisor, a personal project; it is kept apart to be reused.

## Use it

```python
from data_map import Node, Status, Zone, build_map, read_manifest

zones = [
    Zone(zone_code="staging", name="Checked", nodes=[Node(key="staging.orders", name="Orders")]),
    Zone(zone_code="marts", name="For reading", nodes=[Node(key="marts.monthly_revenue", name="Revenue")]),
]
document = build_map(read_manifest(Path("target/manifest.json")), zones)
document.zones[0].nodes[0].status_code = Status.TO_LOOK_AT  # what your checks found
print(document.model_dump_json())  # serve it to the page
```

```svelte
<script lang="ts">
  import { DataMap, type MapDocument } from "data-map";
  let { map }: { map: MapDocument } = $props();
</script>

<DataMap {map} />
```

The component's peers are `svelte` 5, `@xyflow/svelte` 1 and `@lucide/svelte`; its colours are CSS tokens
(`--dm-ink`, `--dm-panel`…, [docs/format.md](docs/format.md#theming)) your page overrides, and its words are
in English, replaced through its `labels` property.

Install both halves from a tag of this repository:

```bash
uv add "data-map @ git+https://github.com/FrtZi/data-map@v0.1.0"
npm install github:FrtZi/data-map#v0.1.0
```

## Work on it

```bash
uv sync && npm ci   # Python 3.13 and Node 22
npm run dev         # the demo page: the component on the example map
uv run python tools/hooks.py pre-push   # every check and test, as CI runs them
```

[ARCHITECTURE.md](ARCHITECTURE.md) is the way in; the features and what proves each are in
[docs/features.md](docs/features.md).

## Licence

MIT, see [LICENSE](LICENSE).
