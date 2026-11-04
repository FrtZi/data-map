// WCAG AA from the tokens: jsdom draws nothing, so axe cannot measure colours; every text colour of the component
// is checked on each surface it sits on, in both themes, from component/tokens.css itself.
import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import { describe, expect, test } from "vitest";

const CSS = readFileSync(resolve(process.cwd(), "component", "tokens.css"), "utf8");
const AA_TEXT = 4.5;
const TEXTS = ["--dm-ink", "--dm-muted", "--dm-accent", "--dm-sound", "--dm-to-look-at", "--dm-blocking"];
const TEXTS_ON_GROUND = ["--dm-before", "--dm-after"]; // the lineage's words, under the map
const SURFACES = ["--dm-ground", "--dm-panel"];

function tokens(block: string): Record<string, string> {
  return Object.fromEntries([...block.matchAll(/(--dm-[a-z-]+):\s*(#[0-9a-f]{6})/g)].map((m) => [m[1]!, m[2]!]));
}

function theme(name: "dark" | "light"): Record<string, string> {
  const dark = CSS.slice(CSS.indexOf("@media"));
  return tokens(name === "light" ? CSS.slice(0, CSS.indexOf("@media")) : dark);
}

function luminance(hex: string): number {
  const [r, g, b] = [1, 3, 5].map((i) => parseInt(hex.slice(i, i + 2), 16) / 255);
  const linear = (c: number) => (c <= 0.03928 ? c / 12.92 : ((c + 0.055) / 1.055) ** 2.4);
  return 0.2126 * linear(r!) + 0.7152 * linear(g!) + 0.0722 * linear(b!);
}

function contrast(a: string, b: string): number {
  const [hi, lo] = [luminance(a), luminance(b)].sort((x, y) => y - x);
  return (hi! + 0.05) / (lo! + 0.05);
}

describe.each(["dark", "light"] as const)("USAB-02 %s theme", (name) => {
  const colours = theme(name);
  const pairs = [
    ...TEXTS.flatMap((text) => SURFACES.map((surface) => [text, surface])),
    ...TEXTS_ON_GROUND.map((text) => [text, "--dm-ground"]),
  ];

  test.each(pairs)("%s on %s reaches AA", (text, surface) => {
    expect(colours[text!], `${text} is defined`).toBeDefined();
    expect(contrast(colours[text!]!, colours[surface!]!)).toBeGreaterThanOrEqual(AA_TEXT);
  });
});
