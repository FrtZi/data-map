"""A map document from the host's zones and dbt's manifest: what dbt knows (definitions, documented columns,
lineage) filled in where the host gave nothing; what only the host knows (statuses, figures, notes) left to it.
"""

from collections.abc import Collection, Mapping

from data_map.document import Column, MapDocument, Node, Zone
from data_map.links import shown_links
from data_map.manifest import parents, relations


def _described(node: Node, relation: dict | None) -> Node:
    """The node with dbt's definition and documented columns, unless the host gave its own."""
    if relation is None:
        return node
    documented = relation.get("columns", {}).values()
    columns = node.columns or [
        Column(
            column_name=column["name"], data_type=column.get("data_type"), description=column.get("description") or None
        )
        for column in documented
    ]
    return node.model_copy(update={"description": node.description or relation.get("description") or None,
                                   "columns": columns})  # fmt: skip


def build_map(
    manifest: dict, zones: list[Zone], other_parents: Mapping[str, Collection[str]] | None = None
) -> MapDocument:
    """The host's zones described from the manifest, and the links between their nodes.

    other_parents: what dbt cannot know, by key: a table written by a script from others, or a page and the
    tables it reads (a page is a node too, in a zone of readers)."""
    known = relations(manifest)
    lineage = {key: set(found) for key, found in parents(manifest).items()}
    for key, extra in (other_parents or {}).items():
        lineage.setdefault(key, set()).update(extra)
    described = [
        zone.model_copy(update={"nodes": [_described(node, known.get(node.key)) for node in zone.nodes]})
        for zone in zones
    ]
    shown = {node.key for zone in zones for node in zone.nodes}
    return MapDocument(zones=described, links=shown_links(lineage, shown))
