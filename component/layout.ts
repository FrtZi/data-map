// The map laid out: a column per zone, each node with its functional name shown, its key and definition for the
// hover, and its status (its own, or the worst of what it comes from).
import type { MapDocument, Status } from "./document";
import { worstUpstream, type Link } from "./lineage";

export type MapNode = { key: string; label: string; hint: string; status: Status };
export type MapColumn = { name: string; nodes: MapNode[] };

export function mapColumns(map: MapDocument): MapColumn[] {
  const links = (map.links ?? []) as Link[];
  const statusOf = new Map(map.zones.flatMap((zone) => zone.nodes.map((node) => [node.key, node.status_code])));
  return map.zones.map((zone) => ({
    name: zone.name,
    nodes: zone.nodes.map((node) => ({
      key: node.key,
      label: node.name,
      hint: [node.key, node.description].filter(Boolean).join("\n"),
      status: node.status_code ?? worstUpstream(links, node.key, statusOf),
    })),
  }));
}

/** The map's dimensions in CSS pixels, in one place: the browser's zoom scales them like the rest of the page. */
export const LAYOUT = {
  nodeWidth: 196, // fits a name of about thirty letters at 12px
  nodeHeight: 26,
  columnGap: 48, // room for the links' curves
  rowHeight: 34,
  top: 24, // the zone's title above its column
} as const;

/** Each node's top-left corner: columns side by side, nodes one under the other. */
export function placed(columns: MapColumn[]) {
  const { nodeWidth, columnGap, rowHeight, top } = LAYOUT;
  return new Map(
    columns.flatMap((c, x) =>
      c.nodes.map((n, y) => [n.key, { x: x * (nodeWidth + columnGap), y: top + y * rowHeight }]),
    ),
  );
}
