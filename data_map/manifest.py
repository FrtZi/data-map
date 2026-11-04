"""What the map reads in dbt's manifest.json (target/manifest.json, written by any dbt command that parses the
project): each relation by its key (schema.name), its definition, its documented columns and its parents.
"""

import json
from pathlib import Path

RELATIONS = ("model", "source", "seed", "snapshot")  # what is a table or a view in the warehouse


def read_manifest(path: Path) -> dict:
    """The manifest, or nothing when the project has not been parsed yet (the map then shows no definition)."""
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def _nodes(manifest: dict) -> dict[str, dict]:
    nodes = {**manifest.get("nodes", {}), **manifest.get("sources", {})}
    return {unique_id: node for unique_id, node in nodes.items() if node["resource_type"] in RELATIONS}


def relation_key(node: dict) -> str:
    """schema.name as the warehouse knows it: a model's alias or a source's identifier, when it has one."""
    return f"{node['schema']}.{node.get('alias') or node.get('identifier') or node['name']}"


def relations(manifest: dict) -> dict[str, dict]:
    """Every relation by its key."""
    return {relation_key(node): node for node in _nodes(manifest).values()}


def parents(manifest: dict) -> dict[str, set[str]]:
    """Each relation's parents (models, sources, seeds, snapshots), by key: dbt's own lineage."""
    nodes = _nodes(manifest)
    keys = {unique_id: relation_key(node) for unique_id, node in nodes.items()}
    return {
        keys[unique_id]: {keys[parent] for parent in node.get("depends_on", {}).get("nodes", []) if parent in keys}
        for unique_id, node in nodes.items()
    }
