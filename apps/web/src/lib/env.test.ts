import { afterEach, describe, expect, it, vi } from "vitest";

import { getApiUrl, getPublicEnvironment } from "./env";

describe("getPublicEnvironment", () => {
  afterEach(() => {
    vi.unstubAllEnvs();
  });

  it("uses the documented local API origin by default", () => {
    vi.stubEnv("NEXT_PUBLIC_API_ORIGIN", "");
    vi.stubEnv("NEXT_PUBLIC_ATLAS_ENV", "development");

    expect(getPublicEnvironment()).toEqual({
      apiOrigin: "http://localhost:8000",
    });
  });

  it("fails closed instead of calling localhost when a hosted API origin is missing", () => {
    vi.stubEnv("NEXT_PUBLIC_API_ORIGIN", "");
    vi.stubEnv("NEXT_PUBLIC_ATLAS_ENV", "production");

    expect(() => getPublicEnvironment()).toThrowError(
      "NEXT_PUBLIC_API_ORIGIN is required in hosted environments",
    );
  });

  it("rejects local API origins in hosted environments", () => {
    vi.stubEnv("NEXT_PUBLIC_API_ORIGIN", "http://localhost:8000");
    vi.stubEnv("NEXT_PUBLIC_ATLAS_ENV", "preview");

    expect(() => getPublicEnvironment()).toThrowError(
      "NEXT_PUBLIC_API_ORIGIN must be a public HTTPS origin in hosted environments",
    );
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

  it("builds API URLs from the configured public origin only", () => {
    vi.stubEnv("NEXT_PUBLIC_API_ORIGIN", "https://api.atlas.example/");

    expect(getApiUrl("/v1/auth/session")).toBe("https://api.atlas.example/v1/auth/session");
    expect(() => getApiUrl("https://attacker.example/v1/auth/session")).toThrowError(
      "API paths must be root-relative",
    );
    expect(() => getApiUrl("//attacker.example/v1/auth/session")).toThrowError(
      "API paths must be root-relative",
    );
  });
});
