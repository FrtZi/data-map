<!-- A zone's name above its column, drawn by Svelte Flow with the nodes so it follows the zoom and the pan. -->
<script lang="ts">
  import { LAYOUT } from "./layout";

  let { data }: { data: { label: string } } = $props();
</script>

<div class="zone" style:--node-width="{LAYOUT.nodeWidth}px">{data.label}</div>

<style>
  .zone {
    width: var(--node-width);
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 0.04em;
    text-transform: uppercase;
    color: var(--dm-muted);
  }
</style>
