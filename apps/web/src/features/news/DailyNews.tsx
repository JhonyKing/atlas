"use client";

import { useEffect, useState } from "react";

import { formatDate, useLocale } from "@/i18n";

import { getDailyNews } from "./api";
import type { DailyNewsPayload } from "./types";

export function DailyNews() {
  const { locale, messages } = useLocale();
  const [payload, setPayload] = useState<DailyNewsPayload | null>(null);

  useEffect(() => {
    const controller = new AbortController();
    void getDailyNews(controller.signal).then(setPayload).catch(() => {
      setPayload({
        status: "unavailable",
        day: new Date(Date.now() - 86_400_000).toISOString().slice(0, 10),
        timezone: "UTC",
        candidate: null,
        candidate_count: 0,
        score: null,
        reason_code: "not_configured",
      });
    });
    return () => controller.abort();
  }, []);

  if (!payload) return <p className="news-status-message news-loading" aria-live="polite"><span className="news-loading-mark" aria-hidden="true" />{messages.newsLoading}</p>;

  return (
    <section className="daily-news" aria-labelledby="daily-news-title" data-news-state={payload.status}>
      <p className="eyebrow">{messages.newsEyebrow}</p>
      <div className="daily-news-heading">
        <h2 id="daily-news-title">{messages.newsTitle}</h2>
        <time dateTime={payload.day}>{payload.day} UTC</time>
      </div>
      <p className="daily-news-deck">{locale === "es-MX" ? "Una noticia útil de IA del día anterior, elegida sólo cuando puedes abrir y revisar sus fuentes." : "One useful AI development from the previous day, selected only when you can open and inspect its sources."}</p>
      {payload.status === "ready" && payload.candidate ? (
        <article className="daily-news-card">
          <p className="daily-news-label">{messages.newsOriginal}</p>
          <h3>{payload.candidate.title}</h3>
          <p>{payload.candidate.summary}</p>
          <p className="daily-news-meta">
            {messages.newsPublisher}: {payload.candidate.publisher} · {messages.newsPublished}: {formatDate(payload.candidate.published_at, locale, "medium")}
          </p>
          <p className="daily-news-signal">{locale === "es-MX" ? `Señal ${Math.round((payload.score ?? 0) * 100)}% · ${payload.candidate.corroboration_count} fuentes corroborantes` : `Signal ${Math.round((payload.score ?? 0) * 100)}% · ${payload.candidate.corroboration_count} corroborating sources`}</p>
          <a href={payload.candidate.canonical_url} target="_blank" rel="noreferrer noopener">{messages.newsOpen}</a>
        </article>
      ) : (
        <p className="news-status-message" aria-live="polite">
          {messages.newsUnavailable} {reasonCopy(payload.reason_code, locale === "es-MX")}
        </p>
      )}
    </section>
  );
}

function reasonCopy(reason: DailyNewsPayload["reason_code"], spanish: boolean): string {
  if (reason === "not_configured") return spanish ? "La fuente diaria todavía no está configurada." : "The daily source is not configured yet.";
  if (reason === "insufficient_signal") return spanish ? "No hubo una señal suficientemente relevante y atribuible." : "No signal was relevant and attributable enough.";
  return spanish ? "La ventana de fuentes no aportó evidencia suficiente." : "The source window did not provide enough evidence.";
}
