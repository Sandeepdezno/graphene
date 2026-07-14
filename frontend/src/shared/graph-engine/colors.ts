// Reads graph colors from the design tokens at runtime (tokens.css is the single
// source of truth — no hex is duplicated into components).

export type GraphColors = {
  nodeByLabel: Record<string, string>;
  direct: string;
  inferred: string;
  accent: string;
  text: string;
};

const LABEL_TO_VAR: Record<string, string> = {
  Program: "--node-program",
  Table: "--node-table",
  FunctionModule: "--node-function-module",
  BAdI: "--node-badi",
  Job: "--node-job",
  Transport: "--node-transport",
};

export function readGraphColors(): GraphColors {
  const css = getComputedStyle(document.documentElement);
  const v = (name: string) => css.getPropertyValue(name).trim();

  const nodeByLabel: Record<string, string> = {};
  for (const [label, varName] of Object.entries(LABEL_TO_VAR)) {
    nodeByLabel[label] = v(varName);
  }
  return {
    nodeByLabel,
    direct: v("--confidence-direct"),
    inferred: v("--confidence-inferred"),
    accent: v("--accent"),
    text: v("--text-primary"),
  };
}
