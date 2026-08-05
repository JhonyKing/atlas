import { getPublicEnvironment } from "@/lib/env";

import type { CorpusStatusPayload } from "./types";

export async function getCorpusStatus(): Promise<CorpusStatusPayload> {
  const response = await fetch(`${getPublicEnvironment().apiOrigin}/v1/corpus`, {
    headers: { Accept: "application/json" },
    cache: "no-store",
  });
  if (!response.ok) throw new Error("Corpus status unavailable");
  return (await response.json()) as CorpusStatusPayload;
}
