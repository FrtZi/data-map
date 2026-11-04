<!-- A node on the map, drawn by Svelte Flow: its functional name and its status; its key and definition on hover. -->
<script lang="ts">
  import { Handle, Position } from "@xyflow/svelte";
  import type { Status } from "./document";
  import { LAYOUT } from "./layout";
  import StatusMark from "./StatusMark.svelte";

  type Data = { label: string; hint: string; status: Status; statusName: string; tone: string; picked: boolean };
  let { data }: { data: Data } = $props();
</script>

<div class="node {data.tone}" class:picked={data.picked} title={data.hint} style:--node-width="{LAYOUT.nodeWidth}px">
  <Handle type="target" position={Position.Left} />
  <span class="name">{data.label}</span>
  <StatusMark status={data.status} name={data.statusName} />
  <Handle type="source" position={Position.Right} />
</div>

<style>
  .node {
    width: var(--node-width);
    display: flex;
    justify-content: space-between;
    gap: 4px;
    padding: 4px 8px;
    font-size: 12px;
    background: var(--dm-panel);
    color: var(--dm-ink);
    border: 1px solid var(--dm-rule);
    border-radius: 6px;
  }
  .picked {
    border-color: var(--dm-accent);
  }
  .name {
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }
  .before {
    color: var(--dm-before);
  }
  .after {
    color: var(--dm-after);
  }
  .aside {
    opacity: 0.45;
  }
</style>
