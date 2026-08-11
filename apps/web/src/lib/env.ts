type PublicEnvironment = Readonly<{
  apiOrigin: string;
}>;

const DEFAULT_API_ORIGIN = "http://localhost:8000";

export function getPublicEnvironment(): PublicEnvironment {
  const configuredApiOrigin = process.env.NEXT_PUBLIC_API_ORIGIN?.trim();
  const atlasEnv = process.env.NEXT_PUBLIC_ATLAS_ENV?.trim() || process.env.NODE_ENV || "development";
  const isHostedEnvironment = ["preview", "staging", "production"].includes(atlasEnv);

  if (!configuredApiOrigin && isHostedEnvironment) {
    throw new Error("NEXT_PUBLIC_API_ORIGIN is required in hosted environments");
  }

  const rawApiOrigin = configuredApiOrigin || DEFAULT_API_ORIGIN;
  let parsedApiOrigin: URL;

  try {
    parsedApiOrigin = new URL(rawApiOrigin);
  } catch {
    throw new Error("NEXT_PUBLIC_API_ORIGIN must be an absolute HTTP(S) URL");
  }

  const isHttp = parsedApiOrigin.protocol === "http:" || parsedApiOrigin.protocol === "https:";
  const isOriginOnly =
    parsedApiOrigin.pathname === "/" &&
    parsedApiOrigin.search === "" &&
    parsedApiOrigin.hash === "" &&
    parsedApiOrigin.username === "" &&
    parsedApiOrigin.password === "";

  if (!isHttp || !isOriginOnly) {
    throw new Error("NEXT_PUBLIC_API_ORIGIN must be an absolute HTTP(S) URL");
  }
  if (isHostedEnvironment && (parsedApiOrigin.protocol !== "https:" ||
      ["localhost", "127.0.0.1", "0.0.0.0"].includes(parsedApiOrigin.hostname))) {
    throw new Error("NEXT_PUBLIC_API_ORIGIN must be a public HTTPS origin in hosted environments");
  }

  return Object.freeze({ apiOrigin: parsedApiOrigin.origin });
}

export function getApiUrl(path: string): string {
  if (!path.startsWith("/") || path.startsWith("//")) {
    throw new Error("API paths must be root-relative");
  }
  return `${getPublicEnvironment().apiOrigin}${path}`;
}
