import { afterEach, describe, expect, it, vi } from "vitest";

import { getPublicEnvironment } from "./env";

describe("getPublicEnvironment", () => {
  afterEach(() => {
    vi.unstubAllEnvs();
  });

  it("uses the documented local API origin by default", () => {
    vi.stubEnv("NEXT_PUBLIC_API_ORIGIN", "");

    expect(getPublicEnvironment()).toEqual({
      apiOrigin: "http://localhost:8000",
    });
  });

  it("accepts an HTTP or HTTPS API origin and removes its trailing slash", () => {
    vi.stubEnv("NEXT_PUBLIC_API_ORIGIN", "https://api.atlas.example/");

    expect(getPublicEnvironment().apiOrigin).toBe("https://api.atlas.example");
  });

  it("rejects malformed and non-HTTP public origins", () => {
    vi.stubEnv("NEXT_PUBLIC_API_ORIGIN", "javascript:alert(1)");

    expect(() => getPublicEnvironment()).toThrowError(
      "NEXT_PUBLIC_API_ORIGIN must be an absolute HTTP(S) URL",
    );
  });

  it("returns a frozen public-only object even when server secrets exist", () => {
    vi.stubEnv("NEXT_PUBLIC_API_ORIGIN", "https://api.atlas.example");
    vi.stubEnv("OPENAI_API_KEY", "sk-must-remain-server-side");
    vi.stubEnv("ATLAS_OPERATOR_TOKEN", "operator-must-remain-server-side");

    const publicEnvironment = getPublicEnvironment();
    const rendered = JSON.stringify(publicEnvironment);

    expect(Object.isFrozen(publicEnvironment)).toBe(true);
    expect(rendered).not.toContain("sk-must-remain-server-side");
    expect(rendered).not.toContain("operator-must-remain-server-side");
  });
});
