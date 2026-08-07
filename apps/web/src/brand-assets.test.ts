import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import { expect, test } from "vitest";

const assets = [
  "atlas-mark.svg",
  "atlas-logo-stacked.svg",
  "atlas-logo-horizontal.svg",
  "favicon.svg",
];

test.each(assets)("brand asset %s is a transparent vector without embedded raster data", (asset) => {
  const source = readFileSync(resolve(process.cwd(), "public", "brand", asset), "utf8");
  expect(source).toContain("<svg");
  expect(source).toContain("viewBox=");
  expect(source).not.toContain("<image");
  expect(source).not.toContain("data:image");
});
