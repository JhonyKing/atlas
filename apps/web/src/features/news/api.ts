import { getPublicEnvironment } from "@/lib/env";

import type { DailyNewsPayload } from "./types";

export async function getDailyNews(signal?: AbortSignal): Promise<DailyNewsPayload> {
  const response = await fetch(`${getPublicEnvironment().apiOrigin}/v1/news/daily`, {
    headers: { Accept: "application/json" },
    signal,
  });
  if (!response.ok) throw new Error(`news_${response.status}`);
  return response.json() as Promise<DailyNewsPayload>;
}

