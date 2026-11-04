// A node's lineage on the map: where it comes from and what it reaches, following the links.
import type { Status } from "./document";

export type Link = [string, string];

function reached(links: Link[], start: string, from: 0 | 1): Set<string> {
  const found = new Set<string>();
  const waiting = [start];
  while (waiting.length) {
    const node = waiting.pop()!;
    for (const link of links) {
      const next = link[1 - from]!;
      if (link[from] === node && !found.has(next)) {
        found.add(next);
        waiting.push(next);
      }
    }
  }
  return found;
}

/** Every node a node is computed from, however far back. */
export const upstream = (links: Link[], node: string) => reached(links, node, 1);

/** Every node a node feeds, however far on: where a problem in it propagates. */
export const downstream = (links: Link[], node: string) => reached(links, node, 0);

const SEVERITY: Status[] = ["SOUND", "TO_LOOK_AT", "BLOCKING"];

/** A node without a status of its own (a page, a report) is as sound as the worst node it comes from. */
export function worstUpstream(links: Link[], node: string, statusOf: Map<string, Status | null | undefined>): Status {
  const statuses = [...upstream(links, node)].map((key) => statusOf.get(key) ?? "SOUND");
  return statuses.reduce<Status>(
    (worst, status) => (SEVERITY.indexOf(status) > SEVERITY.indexOf(worst) ? status : worst),
    "SOUND",
  );
}
