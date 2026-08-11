type PublicEnvironment = Readonly<{
  apiOrigin: string;
}>;

export type PublicApiUnavailableReason = "missing" | "invalid" | "insecure";

export type PublicApiAvailability =
  | Readonly<{ available: true; apiOrigin: string }>
  | Readonly<{ available: false; reason: PublicApiUnavailableReason }>;

export class PublicApiConfigurationError extends Error {
  readonly reason: PublicApiUnavailableReason;

  constructor(reason: PublicApiUnavailableReason) {
    super("ATLAS public API is unavailable");
    this.name = "PublicApiConfigurationError";
    this.reason = reason;
  }
}

const DEFAULT_API_ORIGIN = "http://localhost:8000";

export function getPublicApiAvailability(): PublicApiAvailability {
  const configuredApiOrigin = process.env.NEXT_PUBLIC_API_ORIGIN?.trim();
  const atlasEnv = process.env.NEXT_PUBLIC_ATLAS_ENV?.trim() || process.env.NODE_ENV || "development";
  const isHostedEnvironment = ["preview", "staging", "production"].includes(atlasEnv);

  if (!configuredApiOrigin && isHostedEnvironment) {
    return Object.freeze({ available: false, reason: "missing" });
  }

  const rawApiOrigin = configuredApiOrigin || DEFAULT_API_ORIGIN;
  let parsedApiOrigin: URL;

  try {
    parsedApiOrigin = new URL(rawApiOrigin);
  } catch {
    return Object.freeze({ available: false, reason: "invalid" });
  }

  const isHttp = parsedApiOrigin.protocol === "http:" || parsedApiOrigin.protocol === "https:";
  const isOriginOnly =
    parsedApiOrigin.pathname === "/" &&
    parsedApiOrigin.search === "" &&
    parsedApiOrigin.hash === "" &&
    parsedApiOrigin.username === "" &&
    parsedApiOrigin.password === "";

  if (!isHttp || !isOriginOnly) {
    return Object.freeze({ available: false, reason: "invalid" });
  }
  if (isHostedEnvironment && (parsedApiOrigin.protocol !== "https:" ||
      ["localhost", "127.0.0.1", "0.0.0.0"].includes(parsedApiOrigin.hostname))) {
    return Object.freeze({ available: false, reason: "insecure" });
  }

  return Object.freeze({ available: true, apiOrigin: parsedApiOrigin.origin });
}

export function getPublicEnvironment(): PublicEnvironment {
  const availability = getPublicApiAvailability();
  if (!availability.available) throw new PublicApiConfigurationError(availability.reason);
  return Object.freeze({ apiOrigin: availability.apiOrigin });
}

export function getApiUrl(path: string): string {
  if (!path.startsWith("/") || path.startsWith("//")) {
    throw new Error("API paths must be root-relative");
  }
  return `${getPublicEnvironment().apiOrigin}${path}`;
}
