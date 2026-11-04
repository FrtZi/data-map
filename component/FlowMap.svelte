<!-- The map drawn by Svelte Flow (@xyflow/svelte, MIT; docs/decisions.md): zoom, pan, a minimap and the fit to
     view come with it; the layout, the lineage and the statuses are ours (layout.ts, lineage.ts). -->
<script lang="ts">
  import { Background, Controls, MiniMap, SvelteFlow, type ColorMode, type Edge, type Node } from "@xyflow/svelte";
  import "@xyflow/svelte/dist/style.css";
  import FlowNode from "./FlowNode.svelte";
  import ZoneTitle from "./ZoneTitle.svelte";
  import { LAYOUT, placed, type MapColumn } from "./layout";
  import type { Labels } from "./labels";
  import type { Link } from "./lineage";

  type Props = {
    columns: MapColumn[];
    links: Link[];
    picked: string;
    onpick: (key: string) => void;
    tone: (key: string) => string;
    labels: Labels;
    colorMode: ColorMode;
  };
  let { columns, links, picked, onpick, tone, labels, colorMode }: Props = $props();
  const nodeTypes = { table: FlowNode, zone: ZoneTitle };
  const place = $derived(placed(columns));
  const rows = $derived(Math.max(0, ...columns.map((column) => column.nodes.length)));
  let shownWidth = $state(0); // 0 while hidden (a closed section): drawn once seen, so the fit to view has a size
  // each zone's name above its column: drawn as a node, so it zooms and pans with the map, but never picked
  const titles = $derived<Node[]>(
    columns.map((column, x) => ({
      id: `zone:${x}`,
      type: "zone",
      position: { x: x * (LAYOUT.nodeWidth + LAYOUT.columnGap), y: 0 },
      data: { label: column.name },
      draggable: false,
      selectable: false,
      focusable: false,
    })),
  );
  const nodes = $derived<Node[]>(
    titles.concat(
      columns.flatMap((column) =>
        column.nodes.map((node) => ({
          id: node.key,
          type: "table",
          position: place.get(node.key)!,
          data: {
            ...node,
            statusName: labels.statuses[node.status],
            tone: tone(node.key),
            picked: node.key === picked,
          },
          draggable: false,
          ariaLabel: `${node.label}: ${labels.statuses[node.status]}. ${node.hint}`,
        })),
      ),
    ),
  );
  const edges = $derived<Edge[]>(
    links
      .filter(([from, to]) => place.has(from) && place.has(to))
      .map(([from, to]) => ({
        id: `${from}>${to}`,
        source: from,
        target: to,
        class: tone(from) !== "aside" && tone(to) !== "aside" ? tone(to) : "aside",
      })),
  );
</script>

<div class="flow" style:height="{LAYOUT.top + (rows + 2) * LAYOUT.rowHeight}px" bind:clientWidth={shownWidth}>
  {#if shownWidth > 0}
    <!-- the wheel scrolls the page; the map zooms by its buttons, a pinch or Ctrl and the wheel -->
    <SvelteFlow
      {nodes}
      {edges}
      {nodeTypes}
      {colorMode}
      fitView
      nodesConnectable={false}
      zoomOnScroll={false}
      preventScrolling={false}
      onnodeclick={({ node }) => node.type === "table" && onpick(node.id)}
    >
      <Background gap={LAYOUT.rowHeight} />
      <Controls showLock={false} />
      <MiniMap pannable zoomable width={140} height={90} />
    </SvelteFlow>
  {/if}
</div>

<style>
  .flow {
    min-height: 300px;
    border: 1px solid var(--dm-rule);
    border-radius: 8px;
  }
  .flow :global(.svelte-flow) {
    --xy-background-color: var(--dm-ground);
    --xy-edge-stroke: var(--dm-rule);
  }
  .flow :global(.svelte-flow__edge.after path) {
    stroke: var(--dm-after);
    stroke-width: 2;
  }
  .flow :global(.svelte-flow__edge.before path) {
    stroke: var(--dm-before);
    stroke-width: 2;
  }
  .flow :global(.svelte-flow__edge.aside) {
    opacity: 0.25;
  }
</style>
