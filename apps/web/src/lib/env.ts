type PublicEnvironment = Readonly<{
  apiOrigin: string;
}>;

const DEFAULT_API_ORIGIN = "http://localhost:8000";

export function getPublicEnvironment(): PublicEnvironment {
  const rawApiOrigin = process.env.NEXT_PUBLIC_API_ORIGIN?.trim() || DEFAULT_API_ORIGIN;
  const atlasEnv = process.env.NEXT_PUBLIC_ATLAS_ENV?.trim() || "development";
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
  if (["preview", "staging", "production"].includes(atlasEnv) && (parsedApiOrigin.protocol !== "https:" ||
      ["localhost", "127.0.0.1", "0.0.0.0"].includes(parsedApiOrigin.hostname))) {
    throw new Error("NEXT_PUBLIC_API_ORIGIN must be a public HTTPS origin in hosted environments");
  }

  return Object.freeze({ apiOrigin: parsedApiOrigin.origin });
}
