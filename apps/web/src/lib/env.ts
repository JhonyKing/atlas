type PublicEnvironment = Readonly<{
  apiOrigin: string;
}>;

const DEFAULT_API_ORIGIN = "http://localhost:8000";

export function getPublicEnvironment(): PublicEnvironment {
  const apiOrigin = process.env.NEXT_PUBLIC_API_ORIGIN ?? DEFAULT_API_ORIGIN;

  return { apiOrigin };
}
