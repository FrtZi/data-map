// Lint rules of the component, its demo and its tests: the golden rules' size limits (150 lines a file, 60 a
// function, complexity 12), as in the other projects of the workspace.
import js from "@eslint/js";
import svelte from "eslint-plugin-svelte";
import globals from "globals";
import ts from "typescript-eslint";

export default ts.config(
  { ignores: ["dist/", "node_modules/", ".venv/"] },
  js.configs.recommended,
  ...ts.configs.recommended,
  ...svelte.configs.recommended,
  {
    languageOptions: { globals: { ...globals.browser, ...globals.node } },
    rules: {
      eqeqeq: "error",
      "no-shadow": "error",
      "object-shorthand": "error",
      curly: ["error", "multi-line"],
      complexity: ["error", 12],
      "max-lines": ["error", { max: 150, skipBlankLines: true, skipComments: true }],
      "max-lines-per-function": ["error", { max: 60, skipBlankLines: true, skipComments: true }],
    },
  },
  { files: ["**/*.svelte", "**/*.svelte.ts"], languageOptions: { parserOptions: { parser: ts.parser } } },
  { files: ["tests/**/*.ts"], rules: { "max-lines": "off", "max-lines-per-function": "off" } },
);
