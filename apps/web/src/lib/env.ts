type PublicEnvironment = Readonly<{
  apiOrigin: string;
}>;

const DEFAULT_API_ORIGIN = "http://localhost:8000";

export function getPublicEnvironment(): PublicEnvironment {
  const rawApiOrigin = process.env.NEXT_PUBLIC_API_ORIGIN?.trim() || DEFAULT_API_ORIGIN;
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

  return Object.freeze({ apiOrigin: parsedApiOrigin.origin });
}
