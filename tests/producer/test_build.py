"""The producer (data_map.build) on a fictitious shop's dbt project (tests/fixtures/manifest.json)."""

import json
from pathlib import Path

import pytest

from data_map import Column, Node, Status, Zone, build_map, read_manifest

FIXTURE = Path(__file__).parents[1] / "fixtures" / "manifest.json"
MANIFEST = json.loads(FIXTURE.read_text(encoding="utf-8"))


def zones(*extra: Zone) -> list[Zone]:
    """The host's layout: a zone per layer, each node by its key and its functional name."""
    return [
        Zone(zone_code="raw", name="As received", nodes=[Node(key="raw.shop_orders", name="Orders received"),
                                                        Node(key="raw.customers", name="Customers received")]),
        Zone(zone_code="staging", name="Checked", nodes=[Node(key="staging.orders", name="Orders"),
                                                        Node(key="staging.customers", name="Customers")]),
        Zone(zone_code="marts", name="For reading", nodes=[Node(key="marts.monthly_revenue", name="Revenue")]),
        *extra,
    ]  # fmt: skip


def node(document, key: str) -> Node:  # noqa: ANN001 (a MapDocument)
    return next(n for zone in document.zones for n in zone.nodes if n.key == key)


@pytest.mark.feature("PRODUCER-01")
def test_definitions_and_documented_columns_come_from_dbt_where_the_host_gave_none():
    document = build_map(MANIFEST, zones())
    orders = node(document, "staging.orders")
    assert orders.description == "One row per order, checked and in euro cents."
    assert [(c.column_name, c.data_type, c.description) for c in orders.columns] == [
        ("order_id", "varchar", "The shop's order number."),
        ("amount_cents", None, None),  # documented without words: no definition rather than an empty one
    ]
    assert (node(document, "raw.shop_orders").description or "").startswith("Orders as the fictitious")  # identifier
    assert node(document, "marts.monthly_revenue").description == "Revenue by month and country."  # its alias
    assert node(document, "raw.customers").description is None


@pytest.mark.feature("PRODUCER-01")
def test_what_the_host_gives_is_kept():
    own = Node(key="staging.orders", name="Orders", description="Ours", status_code=Status.TO_LOOK_AT,
               columns=[Column(column_name="order_id", notes=["3 duplicates"])])  # fmt: skip
    layout = zones()
    layout[1].nodes[0] = own
    assert node(build_map(MANIFEST, layout), "staging.orders") == own


@pytest.mark.feature("PRODUCER-02")
def test_dbt_lineage_is_collapsed_onto_the_shown_nodes():
    links = build_map(MANIFEST, zones()).links
    assert links == [
        ("raw.customers", "staging.customers"),
        ("raw.shop_orders", "staging.orders"),  # through orders__checked, which the map does not show
        ("staging.customers", "marts.monthly_revenue"),
        ("staging.orders", "marts.monthly_revenue"),
    ]


@pytest.mark.feature("PRODUCER-02")
def test_what_dbt_cannot_know_is_declared_by_the_host():
    pages = Zone(zone_code="pages", name="Pages", nodes=[Node(key="page:sales", name="Sales")])
    reads = {"page:sales": ["marts.monthly_revenue", "staging.orders__checked"]}
    links = build_map(MANIFEST, zones(pages), reads).links
    assert ("marts.monthly_revenue", "page:sales") in links
    assert ("raw.shop_orders", "page:sales") in links  # a read of a step not shown reaches back to what is shown


@pytest.mark.feature("PRODUCER-03")
def test_a_project_not_parsed_yet_gives_a_map_without_definitions_or_links(tmp_path):
    document = build_map(read_manifest(tmp_path / "target" / "manifest.json"), zones())
    assert document.links == [] and node(document, "staging.orders").description is None
