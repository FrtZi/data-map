// What the component exposes: the map, its document's types, its words to translate, and the lineage it follows.
export { default as DataMap } from "./DataMap.svelte";
export type * from "./document";
export { LABELS, type Labels } from "./labels";
export { downstream, upstream, worstUpstream, type Link } from "./lineage";
