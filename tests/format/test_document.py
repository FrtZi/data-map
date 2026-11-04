"""The map document's format (data_map.document) and its example (format/example.map.json)."""

import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from data_map import MapDocument, Node, Zone

EXAMPLE = Path(__file__).parents[2] / "format" / "example.map.json"


def zone(*keys: str) -> Zone:
    return Zone(zone_code="z", name="Z", nodes=[Node(key=key, name=key) for key in keys])


@pytest.mark.feature("FORMAT-01")
def test_the_example_is_a_valid_document():
    document = MapDocument.model_validate_json(EXAMPLE.read_text(encoding="utf-8"))
    assert document.format_version == 1 and document.links


@pytest.mark.feature("FORMAT-01")
@pytest.mark.parametrize(
    ("zones", "links", "refused"),
    [
        ([zone("a", "b"), zone("b")], [], "keys on the map twice: b"),
        ([zone("a")], [("a", "nowhere")], "links to nodes not on the map: nowhere"),
    ],
)
def test_a_key_names_one_node_and_a_link_joins_two_nodes_of_the_map(zones, links, refused):
    with pytest.raises(ValidationError, match=refused):
        MapDocument(zones=zones, links=links)


@pytest.mark.feature("FORMAT-01")
def test_a_status_comes_from_the_fixed_list_and_nothing_unknown_passes():
    raw = json.loads(EXAMPLE.read_text(encoding="utf-8"))
    raw["zones"][0]["nodes"][0]["status_code"] = "FINE"
    with pytest.raises(ValidationError, match="status_code"):
        MapDocument.model_validate(raw)
    raw["zones"][0]["nodes"][0] = {**raw["zones"][0]["nodes"][1], "colour": "red"}
    with pytest.raises(ValidationError, match="colour"):
        MapDocument.model_validate(raw)
