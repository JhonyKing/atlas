import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import { expect, test } from "vitest";

function readPngDimensions(path: string) {
  const bytes = readFileSync(path);
  expect(bytes.subarray(0, 8)).toEqual(Buffer.from([137, 80, 78, 71, 13, 10, 26, 10]));
  return {
    width: bytes.readUInt32BE(16),
    height: bytes.readUInt32BE(20),
  };
}

const assets = [
  "atlas-mark.svg",
  "atlas-logo-stacked.svg",
  "atlas-logo-horizontal.svg",
  "favicon.svg",
];

const fallbackAssets = [
  ["atlas-mark.png", 512, 512],
  ["atlas-logo-stacked.png", 840, 1040],
  ["atlas-logo-horizontal.png", 1440, 440],
  ["favicon.png", 64, 64],
  ["apple-touch-icon.png", 180, 180],
] as const;

test.each(assets)("brand asset %s is a transparent vector without embedded raster data", (asset) => {
  const source = readFileSync(resolve(process.cwd(), "public", "brand", asset), "utf8");
  expect(source).toContain("<svg");
  expect(source).toContain("viewBox=");
  expect(source).not.toContain("<image");
  expect(source).not.toContain("data:image");
});

test.each(fallbackAssets)("PNG fallback %s has the expected dimensions", async (asset, width, height) => {
  const dimensions = readPngDimensions(resolve(process.cwd(), "public", "brand", asset));
  expect(dimensions.width).toBe(width);
  expect(dimensions.height).toBe(height);
});
