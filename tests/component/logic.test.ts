// The map's logic without drawing it: the lineage followed, the statuses inherited, the layout's columns.
import { describe, expect, test } from "vitest";
import example from "../../format/example.map.json";
import type { MapDocument } from "../../component/document";
import { mapColumns, placed, LAYOUT } from "../../component/layout";
import { downstream, upstream, worstUpstream, type Link } from "../../component/lineage";

const MAP = example as MapDocument;
const LINKS: Link[] = [
  ["raw.a", "staging.a"],
  ["staging.a", "marts.x"],
  ["raw.b", "marts.x"],
  ["marts.x", "page:p"],
];

describe("MAP-03 the lineage of a node picked", () => {
  test("where it comes from, however far back, and what it reaches, however far on", () => {
    expect([...upstream(LINKS, "marts.x")].sort()).toEqual(["raw.a", "raw.b", "staging.a"]);
    expect([...downstream(LINKS, "raw.a")].sort()).toEqual(["marts.x", "page:p", "staging.a"]);
    expect(upstream(LINKS, "raw.a").size).toBe(0);
  });

  test("a loop in the links ends", () => {
    expect(
      [
        ...downstream(
          [
            ["a", "b"],
            ["b", "a"],
          ],
          "a",
        ),
      ].sort(),
    ).toEqual(["a", "b"]);
  });
});

describe("MAP-04 a node without a status of its own", () => {
  test("is as sound as the worst node it comes from", () => {
    const statuses = new Map([
      ["raw.a", "SOUND" as const],
      ["staging.a", "TO_LOOK_AT" as const],
      ["raw.b", "BLOCKING" as const],
    ]);
    expect(worstUpstream(LINKS, "page:p", statuses)).toBe("BLOCKING");
    expect(worstUpstream(LINKS, "staging.a", statuses)).toBe("SOUND");
  });

  test("on the example, the sales page takes the orders' To look at through the revenue", () => {
    const page = mapColumns(MAP).at(-1)!.nodes[0]!;
    expect([page.key, page.status]).toEqual(["page:sales", "TO_LOOK_AT"]);
  });
});

describe("MAP-01 zones as columns", () => {
  test("a column per zone, each node by its functional name, its key and definition for the hover", () => {
    const columns = mapColumns(MAP);
    expect(columns.map((column) => column.name)).toEqual(["As received", "Checked", "For reading", "Pages"]);
    expect(columns[1]!.nodes[0]).toEqual({
      key: "staging.orders",
      label: "Orders",
      hint: "staging.orders\nOne row per order, checked and in euro cents.",
      status: "TO_LOOK_AT",
    });
    const place = placed(columns);
    expect(place.get("staging.customers")).toEqual({
      x: LAYOUT.nodeWidth + LAYOUT.columnGap,
      y: LAYOUT.top + LAYOUT.rowHeight,
    });
  });
});
