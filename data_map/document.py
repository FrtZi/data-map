"""The map document: the format's one source (docs/format.md). Its JSON Schema (format/map.schema.json) and the
component's types (component/document.ts) are generated from these classes by tools/build_format.py, never
written by hand.

A host (the application that shows the map) builds one document: data_map.build gives the zones, the
definitions and the links from dbt's manifest; the host adds what only it knows (statuses, figures, notes).
"""

from enum import StrEnum
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, WithJsonSchema, model_validator

FORMAT_VERSION = 1
# A pair of keys; tsType gives the component's types the pair, which json-schema-to-typescript cannot read in
# prefixItems (a keyword validators ignore).
Link = Annotated[
    tuple[str, str],
    WithJsonSchema(
        {
            "type": "array",
            "prefixItems": [{"type": "string"}, {"type": "string"}],
            "minItems": 2,
            "maxItems": 2,
            "tsType": "[string, string]",
        }
    ),
]


class Status(StrEnum):
    """How sound a node or a column is; the component shows each with an icon and a word, never by colour alone."""

    SOUND = "SOUND"
    TO_LOOK_AT = "TO_LOOK_AT"
    BLOCKING = "BLOCKING"
    NOT_BUILT = "NOT_BUILT"


class Strict(BaseModel):
    model_config = ConfigDict(extra="forbid")


class Figure(Strict):
    """A key figure of a node, shown as a tile: a number is formatted by the component, a text shown as is."""

    label: str = Field(description="What the figure counts, e.g. 'Rows'.")
    value: int | float | str


class Column(Strict):
    column_name: str
    data_type: str | None = None
    description: str | None = Field(default=None, description="What the column holds, in the reader's words.")
    status_code: Status = Status.SOUND
    notes: list[str] = Field(default=[], description="What the host found on it, one line each.")


class Node(Strict):
    """A table, a view or anything that reads them (a page, a report), placed in its zone's column."""

    key: str = Field(description="Its technical name, unique on the map (schema.name for a table); shown on hover.")
    name: str = Field(description="Its functional name, the one shown.")
    description: str | None = None
    status_code: Status | None = Field(
        default=None, description="Empty: as sound as the worst node it comes from, however far back."
    )
    figures: list[Figure] = []
    columns: list[Column] = []


class Zone(Strict):
    """A column of the map: a layer of the project (sources, staging, marts…) or its readers."""

    zone_code: str
    name: str
    nodes: list[Node]


class MapDocument(Strict):
    """What the component draws: the zones left to right, their nodes top to bottom, and the links."""

    format_version: int = FORMAT_VERSION
    zones: list[Zone]
    links: list[Link] = Field(default=[], description="From a node's key to the key of a node it feeds.")

    @model_validator(mode="after")
    def _keys_hold(self) -> "MapDocument":
        """A key names one node only, and a link joins two nodes of the map."""
        keys = [node.key for zone in self.zones for node in zone.nodes]
        twice = sorted({key for key in keys if keys.count(key) > 1})
        if twice:
            raise ValueError(f"keys on the map twice: {', '.join(twice)}")
        unknown = sorted({end for link in self.links for end in link} - set(keys))
        if unknown:
            raise ValueError(f"links to nodes not on the map: {', '.join(unknown)}")
        return self
