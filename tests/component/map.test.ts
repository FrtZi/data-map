// The component drawn on the example map (format/example.map.json), in jsdom: what a reader sees and reaches,
// and axe finding no violation (colours are checked from the tokens instead: contrast.test.ts).
import { fireEvent, render, screen } from "@testing-library/svelte";
import axe from "axe-core";
import { afterEach, describe, expect, test } from "vitest";
import example from "../../format/example.map.json";
import DataMap from "../../component/DataMap.svelte";
import type { MapDocument } from "../../component/document";

const MAP = example as MapDocument;
// rendered alone, outside a page's landmarks: a host checks those on its own pages
const RULES = { "color-contrast": { enabled: false }, region: { enabled: false } };

async function violations(): Promise<string[]> {
  const result = await axe.run(document.body, { rules: RULES });
  return result.violations.map((v) => `${v.id}: ${v.nodes.map((node) => node.target).join(", ")}`);
}

const nodeNamed = (name: string) =>
  [...document.querySelectorAll<HTMLElement>(".svelte-flow .node")].find(
    (node) => node.querySelector(".name")?.textContent === name,
  )!;

afterEach(() => document.body.replaceChildren());

describe("MAP-01 USAB-01 a node by its functional name, its status in an icon and a word", () => {
  test("its key and definition on hover; the map accessible", async () => {
    render(DataMap, { map: MAP });
    const orders = nodeNamed("Orders");
    expect(orders.getAttribute("title")).toBe("staging.orders\nOne row per order, checked and in euro cents.");
    expect(orders.textContent).toContain("⚠");
    expect(orders.textContent).toContain("To look at"); // the word, for a screen reader, beside the icon
    const zones = [...document.querySelectorAll(".svelte-flow .zone")].map((zone) => zone.textContent);
    // DEF-002: the layout kept room for each zone's name above its column, but never drew it
    expect(zones).toEqual(["As received", "Checked", "For reading", "Pages"]);
    expect(await violations()).toEqual([]);
  });
});

describe("MAP-02 the links on a switch", () => {
  test("drawn at first, hidden by the switch", async () => {
    render(DataMap, { map: MAP });
    const links = screen.getByRole("button", { name: "Links" });
    expect(links.getAttribute("aria-pressed")).toBe("true");
    expect(document.querySelectorAll(".svelte-flow__edge").length).toBe(MAP.links!.length);
    await fireEvent.click(links);
    expect(document.querySelectorAll(".svelte-flow__edge").length).toBe(0);
  });
});

describe("MAP-03 the lineage of a node picked", () => {
  test("said in words too, for the node picked", async () => {
    render(DataMap, { map: MAP, picked: "staging.orders" });
    await fireEvent.click(screen.getByRole("button", { name: "Lineage" }));
    expect(screen.getByText("Orders comes from Orders received; reaches Revenue, Sales.")).toBeTruthy();
    expect(nodeNamed("Customers received").classList).toContain("aside");
    expect(await violations()).toEqual([]);
  });
});

describe("MAP-05 the detail of the node picked", () => {
  test("its figures and each column, with what it holds, its status and the host's notes", () => {
    render(DataMap, { map: MAP, picked: "staging.orders" });
    expect(screen.getByRole("heading", { name: /Orders/ })).toBeTruthy();
    expect(screen.getByText(/One row per order/).textContent).toContain("staging.orders · One row per order");
    expect(screen.getByText("125,397")).toBeTruthy(); // a number formatted in the host's locale
    expect(screen.getByText("3 duplicates left out")).toBeTruthy();
    expect(screen.getAllByRole("row")).toHaveLength(3);
  });

  test("a node not built says so, and a node without a status of its own shows the one it inherits", () => {
    render(DataMap, { map: MAP, picked: "staging.returns" });
    expect(screen.getByText("Not built yet: there is nothing to describe.")).toBeTruthy();
    document.body.replaceChildren();
    render(DataMap, { map: MAP, picked: "page:sales" });
    expect(screen.getByRole("heading", { name: /Sales/ }).textContent).toContain("To look at");
  });
});

describe("FLEX-01 the host's words", () => {
  test("replace the component's, the others kept", () => {
    render(DataMap, { map: MAP, labels: { links: "Liens" } });
    expect(screen.getByRole("button", { name: "Liens" })).toBeTruthy();
    expect(screen.getByRole("button", { name: "Lineage" })).toBeTruthy();
  });
});
