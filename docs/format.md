# The map document

[← Overview](../ARCHITECTURE.md) · Schema: [map.schema.json](../format/map.schema.json) · Example:
[example.map.json](../format/example.map.json)

What the producer writes and the component draws: one JSON document per map. Its source is
`data_map/document.py`; the JSON Schema and the component's types are generated from it
(`tools/build_format.py`), never written by hand. Version 1.

## Shape

| Element | Field | Holds |
|---|---|---|
| Document | `format_version` | 1 |
| | `zones` | The map's columns, left to right |
| | `links` | Pairs of keys: from a node to a node it feeds |
| Zone | `zone_code`, `name` | Its code, and its name shown above its column |
| | `nodes` | Its nodes, top to bottom |
| Node | `key` | Its technical name, unique on the map (`schema.name` for a table); shown on hover |
| | `name` | Its functional name, the one shown |
| | `description` | Its definition, on hover and in its detail |
| | `status_code` | `SOUND`, `TO_LOOK_AT`, `BLOCKING`, `NOT_BUILT`, or empty: then as sound as the worst node it comes from |
| | `figures` | Key figures (`label`, `value`): a number is formatted in the host's locale, a text shown as is |
| | `columns` | Its columns, described |
| Column | `column_name`, `data_type` | Its name, and its type on hover |
| | `description` | What it holds, in the reader's words |
| | `status_code` | As a node's, `SOUND` by default |
| | `notes` | What the host found on it, one line each |

Rules: a key names one node only; a link joins two nodes of the map; no field outside these. The producer and
the schema refuse a document that breaks them.

## Who fills what

- **dbt's manifest** (through `data_map.build_map`): each node's definition and documented columns, where the
  host gave none; the links, dbt's lineage collapsed onto the nodes shown.
- **The host**: the zones and their nodes (which tables, under which names), what dbt cannot know (a table a
  script writes, a page and what it reads: `other_parents`), and what only it knows: the statuses, the figures,
  the notes.

## Theming

The component's colours are CSS custom properties; a host sets them on any ancestor (`:root` or a wrapper),
and its rule always wins over the defaults:

| Token | For |
|---|---|
| `--dm-ground`, `--dm-panel`, `--dm-rule` | The map's ground, a node's background, the borders and links |
| `--dm-ink`, `--dm-muted`, `--dm-accent` | Text, secondary text, the switch on and the node picked |
| `--dm-sound`, `--dm-to-look-at`, `--dm-blocking` | The statuses (an icon and a word always go with them) |
| `--dm-before`, `--dm-after` | The lineage: what the node picked comes from, what it reaches |

A host keeps WCAG AA: each text colour at 4.5:1 on the ground and the panel (`tests/component/contrast.test.ts`
checks the defaults).
