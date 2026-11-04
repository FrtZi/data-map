// The component's words, in one place: a host in another language, or with its own names for the statuses,
// passes its own (DataMap's `labels`), the rest kept.
import type { Status } from "./document";

export const LABELS = {
  map: "Map",
  links: "Links",
  lineage: "Lineage",
  picked: "Picked",
  comesFrom: "comes from",
  reaches: "reaches",
  theSources: "the sources",
  nothingFurther: "nothing further",
  column: "Column",
  holds: "What it holds",
  status: "Status",
  noDefinition: "No definition yet",
  notBuilt: "Not built yet: there is nothing to describe.",
  statuses: { SOUND: "Sound", TO_LOOK_AT: "To look at", BLOCKING: "Blocking", NOT_BUILT: "Not built" } as Record<
    Status,
    string
  >,
};

export type Labels = typeof LABELS;

/** Each status's icon: the word goes with it, the colour only doubles them (WCAG 1.4.1). */
export const ICONS: Record<Status, string> = { SOUND: "✓", TO_LOOK_AT: "⚠", BLOCKING: "✕", NOT_BUILT: "○" };
