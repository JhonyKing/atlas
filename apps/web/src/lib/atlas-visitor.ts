const VISITOR_TOKEN_HEADER = "X-Atlas-Visitor-Token";
const VISITOR_TOKEN_STORAGE_KEY = "atlas.visitor-token.v1";

export function atlasVisitorHeaders(): Record<string, string> {
  if (typeof window === "undefined") return {};
  try {
    const token = window.localStorage.getItem(VISITOR_TOKEN_STORAGE_KEY);
    return token ? { [VISITOR_TOKEN_HEADER]: token } : {};
  } catch {
    return {};
  }
}

export function rememberAtlasVisitor(response: Response): void {
  if (typeof window === "undefined") return;
  const token = response.headers.get(VISITOR_TOKEN_HEADER);
  if (!token) return;
  try {
    window.localStorage.setItem(VISITOR_TOKEN_STORAGE_KEY, token);
  } catch {
    // The browser may still use the response cookie for same-site requests.
  }
}
