import { describe, expect, it } from "vitest";

import { metadata as engineeringMetadata } from "./engineering/page";
import { metadata as rootMetadata } from "./layout";
import { metadata as homeMetadata } from "./page";
import robots from "./robots";

describe("public metadata", () => {
  it("uses the public canonical Vercel domain", () => {
    expect(rootMetadata.metadataBase?.toString()).toBe("https://atlasai-lilac.vercel.app/");
    expect(homeMetadata.alternates?.canonical).toBe("/");
    expect(homeMetadata.openGraph).toMatchObject({
      type: "website",
      url: "/",
    });
  });

  it("publishes specific engineering metadata", () => {
    expect(engineeringMetadata.title).toContain("Engineering");
    expect(engineeringMetadata.alternates?.canonical).toBe("/engineering");
    expect(engineeringMetadata.openGraph).toMatchObject({ url: "/engineering" });
  });

  it("allows canonical public pages to be indexed", () => {
    expect(robots()).toMatchObject({
      rules: { userAgent: "*", allow: "/" },
      sitemap: "https://atlasai-lilac.vercel.app/sitemap.xml",
    });
  });
});
