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

  if (!payload) return <p className="news-status-message" aria-live="polite">{messages.newsLoading}</p>;

  return (
    <section className="daily-news" aria-labelledby="daily-news-title">
      <p className="eyebrow">{messages.newsEyebrow}</p>
      <div className="daily-news-heading">
        <h2 id="daily-news-title">{messages.newsTitle}</h2>
        <time dateTime={payload.day}>{payload.day} UTC</time>
      </div>
      {payload.status === "ready" && payload.candidate ? (
        <article className="daily-news-card">
          <p className="daily-news-label">{messages.newsOriginal}</p>
          <h3>{payload.candidate.title}</h3>
          <p>{payload.candidate.summary}</p>
          <p className="daily-news-meta">
            {messages.newsPublisher}: {payload.candidate.publisher} · {messages.newsPublished}: {formatDate(payload.candidate.published_at, locale, "medium")}
          </p>
          <a href={payload.candidate.canonical_url} target="_blank" rel="noreferrer noopener">{messages.newsOpen}</a>
        </article>
      ) : (
        <p className="news-status-message" aria-live="polite">
          {messages.newsUnavailable} {messages.newsNoEvidence}
        </p>
      )}
    </section>
  );
}

