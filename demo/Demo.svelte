<!-- The example map (format/example.map.json) in a page: what a host does, its own heading around the map. -->
<script lang="ts">
  import example from "../format/example.map.json";
  import { DataMap, type MapDocument } from "../component";
</script>

<h1>A fictitious shop's dbt project</h1>
<p>Click a table to see its columns; switch the lineage on to see where it comes from and what it reaches.</p>
<DataMap map={example as MapDocument} picked="staging.orders" />

<style>
  :global(body) {
    margin: 0;
    padding: 16px;
    font-family: system-ui, sans-serif;
    background: var(--dm-ground);
    color: var(--dm-ink);
  }
  h1 {
    font-size: 1.25rem;
  }
</style>
