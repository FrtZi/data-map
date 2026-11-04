<!-- The map of a dbt project's tables: a column per zone, each node by its functional name with its status (an icon
     and a word, the colour only doubling them), its key and definition on hover; the links on a switch; the
     lineage on another (a node picked: where it comes from, what it reaches); the picked node's detail below. -->
<script lang="ts">
  import { GitBranch, Share2 } from "@lucide/svelte";
  import type { ColorMode } from "@xyflow/svelte";
  import type { MapDocument } from "./document";
  import FlowMap from "./FlowMap.svelte";
  import { LABELS, type Labels } from "./labels";
  import { mapColumns } from "./layout";
  import { downstream, upstream, type Link } from "./lineage";
  import NodeDetail from "./NodeDetail.svelte";
  import "./tokens.css";

  type Props = {
    map: MapDocument;
    picked?: string;
    labels?: Partial<Labels>;
    locale?: string;
    colorMode?: ColorMode;
  };
  let { map, picked = $bindable(""), labels = {}, locale = "en-GB", colorMode = "system" }: Props = $props();
  const words = $derived({ ...LABELS, ...labels });
  const allLinks = $derived((map.links ?? []) as Link[]);
  let links = $state(true);
  let lineage = $state(false);
  const columns = $derived(mapColumns(map));
  const byKey = $derived(new Map(columns.flatMap((column) => column.nodes.map((node) => [node.key, node]))));
  const shownKey = $derived(byKey.has(picked) ? picked : (columns[0]?.nodes[0]?.key ?? ""));
  const before = $derived(lineage ? upstream(allLinks, shownKey) : new Set<string>());
  const after = $derived(lineage ? downstream(allLinks, shownKey) : new Set<string>());
  const tone = (key: string) =>
    !lineage ? "" : key === shownKey ? "picked" : after.has(key) ? "after" : before.has(key) ? "before" : "aside";
  const named = (keys: Set<string>) => [...keys].map((key) => byKey.get(key)?.label ?? key).join(", ");
  const node = $derived(map.zones.flatMap((zone) => zone.nodes).find((n) => n.key === shownKey));
</script>

<div class="data-map">
  <div class="tools" role="group" aria-label={words.map}>
    <button type="button" class="toggle" aria-pressed={links} onclick={() => (links = !links)}
      ><Share2 size={14} aria-hidden="true" /> {words.links}</button
    >
    <button type="button" class="toggle" aria-pressed={lineage} onclick={() => (lineage = !lineage)}
      ><GitBranch size={14} aria-hidden="true" /> {words.lineage}</button
    >
    {#if lineage}<span class="muted"
        >{words.picked} · <span class="before">{words.comesFrom}</span> ·
        <span class="after">{words.reaches}</span></span
      >{/if}
  </div>
  <FlowMap
    {columns}
    links={links || lineage ? allLinks : []}
    picked={shownKey}
    onpick={(key) => (picked = key)}
    {tone}
    labels={words}
    {colorMode}
  />
  {#if lineage}
    <p class="muted">
      {byKey.get(shownKey)?.label}
      {words.comesFrom}
      {named(before) || words.theSources}; {words.reaches}
      {named(after) || words.nothingFurther}.
    </p>
  {/if}
  {#if node}<NodeDetail {node} status={byKey.get(shownKey)!.status} labels={words} {locale} />{/if}
</div>

<style>
  .data-map {
    display: grid;
    grid-template-columns: minmax(0, 1fr); /* as wide as its box, never as its widest block */
    gap: 12px;
    color: var(--dm-ink);
  }
  .tools {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    align-items: center;
  }
  .toggle {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    border: 1px solid var(--dm-rule);
    border-radius: 999px;
    padding: 2px 12px;
    font: inherit;
    font-size: 0.8rem;
    background: none;
    color: var(--dm-ink);
    cursor: pointer;
  }
  .toggle[aria-pressed="true"] {
    border-color: var(--dm-accent);
    color: var(--dm-accent);
  }
  .muted {
    color: var(--dm-muted);
  }
  span.before {
    color: var(--dm-before);
  }
  span.after {
    color: var(--dm-after);
  }
</style>
