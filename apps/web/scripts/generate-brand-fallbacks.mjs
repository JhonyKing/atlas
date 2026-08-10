import { chromium } from "@playwright/test";
import { readFile, mkdir } from "node:fs/promises";
import { dirname, resolve } from "node:path";

const root = resolve(process.cwd(), "public", "brand");
const assets = [
  { source: "atlas-mark.svg", target: "atlas-mark.png", width: 512, height: 512 },
  { source: "atlas-logo-stacked.svg", target: "atlas-logo-stacked.png", width: 840, height: 1040 },
  { source: "atlas-logo-horizontal.svg", target: "atlas-logo-horizontal.png", width: 1440, height: 440 },
  { source: "favicon.svg", target: "favicon.png", width: 64, height: 64 },
  { source: "favicon.svg", target: "apple-touch-icon.png", width: 180, height: 180 },
];

const browser = await chromium.launch({ headless: true });
try {
  for (const asset of assets) {
    const svg = await readFile(resolve(root, asset.source), "utf8");
    const page = await browser.newPage({
      viewport: { width: asset.width, height: asset.height },
      deviceScaleFactor: 1,
    });
    const encoded = Buffer.from(svg, "utf8").toString("base64");
    await page.setContent(`<!doctype html><html><head><style>html,body{margin:0;width:100%;height:100%;background:transparent;overflow:hidden}img{display:block;width:100%;height:100%;object-fit:contain}</style></head><body><img alt="" src="data:image/svg+xml;base64,${encoded}"></body></html>`);
    await page.locator("img").screenshot({ path: resolve(root, asset.target), omitBackground: true });
    await page.close();
  }
} finally {
  await browser.close();
}

await mkdir(dirname(resolve(root, "favicon.png")), { recursive: true });
