"use client";

import Link from "next/link";

import { useLocale } from "@/i18n";

import { CitedAnswerForm } from "../cited-answer/CitedAnswerForm";

const GITHUB_URL = "https://github.com/JhonyKing/atlas";

export function ProductHome() {
  const { locale, messages } = useLocale();
  const prefix = locale === "es-MX" ? "/es" : "/en";
  const actions = [
    { id: "ask", title: messages.home.askTitle, description: messages.home.askDescription, href: "#ask-atlas", primary: true },
    { id: "compare", title: messages.home.compareTitle, description: messages.home.compareDescription, href: `${prefix}/compare`, primary: false },
    { id: "report", title: messages.home.reportTitle, description: messages.home.reportDescription, href: `${prefix}/reports`, primary: false },
  ] as const;

  return (
    <>
      <section className="product-hero" aria-labelledby="page-title">
        <p className="eyebrow">{messages.eyebrow}</p>
        <h1 id="page-title">{messages.title}</h1>
        <p className="product-hero-lede">{messages.home.researchBenefit}</p>
        <p className="product-action-prompt">{messages.home.actionPrompt}</p>
        <ul className="product-action-grid" aria-label={messages.home.actionAria}>
          {actions.map((action) => (
            <li key={action.id} className={action.primary ? "product-action-primary" : undefined}>
              <Link className={action.primary ? "product-action-card primary" : "product-action-card"} href={action.href}>
                <strong>{action.title}</strong>
                <span>{action.description}</span>
                <span className="product-action-arrow" aria-hidden="true">→</span>
              </Link>
            </li>
          ))}
        </ul>
        <ul className="product-trust-list" aria-label={messages.trustNote}>
          {messages.home.trustPoints.map((point) => <li key={point}>{point}</li>)}
        </ul>
      </section>

      <CitedAnswerForm />

      <footer className="portfolio-attribution">
        <p>{messages.home.builtBy}</p>
        <nav aria-label={messages.home.builtBy}>
          <a href={GITHUB_URL} target="_blank" rel="noreferrer">{messages.home.github}</a>
          <Link href={`${prefix}/engineering`}>{messages.home.architecture}</Link>
          <Link href={`${prefix}/engineering#case-study-title`}>{messages.home.caseStudy}</Link>
        </nav>
      </footer>
    </>
  );
}
