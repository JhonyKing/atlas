"use client";

import { createContext, createElement, useContext, useEffect, useMemo, useState, type ReactNode } from "react";

export type Locale = "en-US" | "es-MX";

type MessageCatalog = {
  localeName: string;
  switchLabel: string;
  switchTo: string;
  eyebrow: string;
  title: string;
  lede: string;
  technicalQuestion: string;
  questionPlaceholder: string;
  corpus: string;
  allCollections: string;
  ask: string;
  cancel: string;
  ready: string;
  accepted: string;
  requestEnded: string;
  partialReady: string;
  verifiedReady: string;
  stage: Record<string, string>;
  invalidQuestion: string;
  invalidMultiple: string;
  networkError: string;
  genericRequestError: string;
  feedbackSaved: string;
  feedbackAssociationError: string;
  feedbackSaveError: string;
  abstentionTitle: string;
  defaultAbstention: string;
  evidenceTitle: string;
  partialAnswer: string;
  completeAnswer: string;
  inference: string;
  factualClaim: string;
  publisher: string;
  sourceType: string;
  captured: string;
  published: string;
  version: string;
  originalSource: string;
  openSource: string;
  openRevision: string;
  usefulQuestion: string;
  markUseful: string;
  markNotUseful: string;
  failureCategory: string;
  chooseCategory: string;
  comment: string;
  saveFeedback: string;
  categories: Record<string, string>;
  corpusEyebrow: string;
  corpusTitle: string;
  snapshot: string;
  loadingCorpus: string;
  unavailableCorpus: string;
  lastVerified: string;
  notVerified: string;
  sourceCount: string;
  pageCount: string;
  chunkCount: string;
  openCanonical: string;
  sourceTypes: Record<string, string>;
  states: Record<string, string>;
  newsEyebrow: string;
  newsTitle: string;
  newsLoading: string;
  newsUnavailable: string;
  newsNoEvidence: string;
  newsOriginal: string;
  newsPublisher: string;
  newsPublished: string;
  newsOpen: string;
  comparison: {
    eyebrow: string;
    title: string;
    technologies: string;
    criteria: string;
    compare: string;
    cancel: string;
    ready: string;
    accepted: string;
    verified: string;
    unsupported: string;
    partial: string;
    contradictory: string;
    noEvidence: string;
    criterionLabels: Record<string, string>;
  };
};

const catalogs: Record<Locale, MessageCatalog> = {
  "en-US": {
    localeName: "English",
    switchLabel: "Language",
    switchTo: "Switch language",
    eyebrow: "ATLAS AI · evidence-first research",
    title: "Answers you can verify.",
    lede: "Ask one technical question about the curated LangGraph, LangChain, or OpenAI corpus. Claims appear only after their evidence is checked.",
    technicalQuestion: "Technical question",
    questionPlaceholder: "How does LangGraph persist state across a workflow?",
    corpus: "Corpus (optional)",
    allCollections: "All supported collections",
    ask: "Ask ATLAS",
    cancel: "Cancel request",
    ready: "Ready to verify an answer.",
    accepted: "Accepted. Preparing retrieval…",
    requestEnded: "Request ended without a verified answer.",
    partialReady: "Partial answer ready.",
    verifiedReady: "Verified answer ready.",
    stage: {
      accepted: "Accepted",
      retrieving: "Retrieving evidence",
      composing: "Composing answer",
      verifying: "Verifying citations",
      completed: "Completed",
      abstained: "Abstained",
      cancelled: "Cancelled",
    },
    invalidQuestion: "Enter a technical question with at least one word or number.",
    invalidMultiple: "Ask one related question at a time so every claim can be verified.",
    networkError: "ATLAS could not connect to the local API. Check that the backend is running on port 8000.",
    genericRequestError: "ATLAS could not complete the request.",
    feedbackSaved: "Feedback saved.",
    feedbackAssociationError: "ATLAS could not associate feedback with this answer.",
    feedbackSaveError: "ATLAS could not save this feedback.",
    abstentionTitle: "ATLAS could not verify this answer",
    defaultAbstention: "ATLAS could not verify an answer from the available evidence.",
    evidenceTitle: "Evidence and feedback",
    partialAnswer: "Partial answer",
    completeAnswer: "Complete answer",
    inference: "Inference",
    factualClaim: "Factual claim",
    publisher: "Publisher",
    sourceType: "Source type",
    captured: "Captured",
    published: "Published",
    version: "Version",
    originalSource: "Original source excerpt",
    openSource: "Open",
    openRevision: "Open source revision",
    usefulQuestion: "Was this answer useful?",
    markUseful: "Mark answer useful",
    markNotUseful: "Mark answer not useful",
    failureCategory: "Failure category (optional)",
    chooseCategory: "Choose a category",
    comment: "Comment (optional)",
    saveFeedback: "Save feedback",
    categories: {
      incorrect_citation: "Incorrect citation",
      incorrect_answer: "Incorrect answer",
      outdated: "Outdated",
      incomplete: "Incomplete",
      other: "Other",
    },
    corpusEyebrow: "Verified source collections",
    corpusTitle: "Corpus status",
    snapshot: "Snapshot",
    loadingCorpus: "Loading corpus status…",
    unavailableCorpus: "Corpus status unavailable.",
    lastVerified: "Last verified",
    notVerified: "Not yet verified",
    sourceCount: "Sources",
    pageCount: "Pages",
    chunkCount: "Chunks",
    openCanonical: "Open canonical root",
    sourceTypes: { documentation: "documentation", changelog: "changelog", release_note: "release note" },
    states: { ready: "Ready", stale: "Stale", refreshing: "Refreshing", unavailable: "Unavailable" },
    newsEyebrow: "Internet signal",
    newsTitle: "Previous-day headline",
    newsLoading: "Loading yesterday's verified news…",
    newsUnavailable: "No verified headline is available for the previous day.",
    newsNoEvidence: "The feed window did not contain enough attributable evidence.",
    newsOriginal: "Original headline and summary",
    newsPublisher: "Publisher",
    newsPublished: "Published",
    newsOpen: "Open source",
    comparison: {
      eyebrow: "Evidence-backed comparator",
      title: "Compare technologies without invented data.",
      technologies: "Technologies (2 to 4)",
      criteria: "Criteria",
      compare: "Compare",
      cancel: "Cancel",
      ready: "Ready to compare.",
      accepted: "Comparison accepted…",
      verified: "Comparison verified.",
      unsupported: "Unsupported",
      partial: "Partial",
      contradictory: "Contradictory",
      noEvidence: "No verified evidence is available for this cell.",
      criterionLabels: {
        capability: "Capability",
        tool_calling: "Tool calling",
        context: "Context",
        latency: "Latency",
        price: "Price",
        license: "License",
        freshness: "Freshness",
        operational_risk: "Operational risk",
      },
    },
  },
  "es-MX": {
    localeName: "Español",
    switchLabel: "Idioma",
    switchTo: "Cambiar idioma",
    eyebrow: "ATLAS AI · investigación con evidencia",
    title: "Respuestas que puedes verificar.",
    lede: "Haz una pregunta técnica sobre el corpus curado de LangGraph, LangChain u OpenAI. Las afirmaciones aparecen sólo después de comprobar su evidencia.",
    technicalQuestion: "Pregunta técnica",
    questionPlaceholder: "¿Cómo conserva LangGraph el estado durante un flujo de trabajo?",
    corpus: "Corpus (opcional)",
    allCollections: "Todas las colecciones compatibles",
    ask: "Preguntar a ATLAS",
    cancel: "Cancelar solicitud",
    ready: "Listo para verificar una respuesta.",
    accepted: "Aceptada. Preparando la recuperación…",
    requestEnded: "La solicitud terminó sin una respuesta verificada.",
    partialReady: "La respuesta parcial está lista.",
    verifiedReady: "La respuesta verificada está lista.",
    stage: {
      accepted: "Aceptada",
      retrieving: "Recuperando evidencia",
      composing: "Redactando respuesta",
      verifying: "Verificando citas",
      completed: "Completada",
      abstained: "Sin respuesta verificada",
      cancelled: "Cancelada",
    },
    invalidQuestion: "Escribe una pregunta técnica con al menos una palabra o número.",
    invalidMultiple: "Haz una sola pregunta relacionada para poder verificar cada afirmación.",
    networkError: "ATLAS no pudo conectarse con la API local. Comprueba que el backend esté activo en el puerto 8000.",
    genericRequestError: "ATLAS no pudo completar la solicitud.",
    feedbackSaved: "Comentarios guardados.",
    feedbackAssociationError: "ATLAS no pudo asociar los comentarios con esta respuesta.",
    feedbackSaveError: "ATLAS no pudo guardar estos comentarios.",
    abstentionTitle: "ATLAS no pudo verificar esta respuesta",
    defaultAbstention: "ATLAS no pudo verificar una respuesta con la evidencia disponible.",
    evidenceTitle: "Evidencia y comentarios",
    partialAnswer: "Respuesta parcial",
    completeAnswer: "Respuesta completa",
    inference: "Inferencia",
    factualClaim: "Afirmación factual",
    publisher: "Publicador",
    sourceType: "Tipo de fuente",
    captured: "Capturada",
    published: "Publicada",
    version: "Versión",
    originalSource: "Fragmento original de la fuente",
    openSource: "Abrir",
    openRevision: "Abrir revisión de la fuente",
    usefulQuestion: "¿Te resultó útil esta respuesta?",
    markUseful: "Marcar respuesta útil",
    markNotUseful: "Marcar respuesta no útil",
    failureCategory: "Categoría del fallo (opcional)",
    chooseCategory: "Elige una categoría",
    comment: "Comentario (opcional)",
    saveFeedback: "Guardar comentarios",
    categories: {
      incorrect_citation: "Cita incorrecta",
      incorrect_answer: "Respuesta incorrecta",
      outdated: "Desactualizada",
      incomplete: "Incompleta",
      other: "Otro",
    },
    corpusEyebrow: "Colecciones de fuentes verificadas",
    corpusTitle: "Estado del corpus",
    snapshot: "Instantánea",
    loadingCorpus: "Cargando el estado del corpus…",
    unavailableCorpus: "El estado del corpus no está disponible.",
    lastVerified: "Última verificación",
    notVerified: "Aún no verificada",
    sourceCount: "Fuentes",
    pageCount: "Páginas",
    chunkCount: "Fragmentos",
    openCanonical: "Abrir raíz canónica",
    sourceTypes: { documentation: "documentación", changelog: "registro de cambios", release_note: "nota de versión" },
    states: { ready: "Lista", stale: "Desactualizada", refreshing: "Actualizando", unavailable: "No disponible" },
    newsEyebrow: "Señal de Internet",
    newsTitle: "Titular del día anterior",
    newsLoading: "Cargando la noticia verificada de ayer…",
    newsUnavailable: "No hay un titular verificado disponible del día anterior.",
    newsNoEvidence: "La ventana de fuentes no tuvo evidencia atribuible suficiente.",
    newsOriginal: "Titular y resumen originales",
    newsPublisher: "Publicador",
    newsPublished: "Publicada",
    newsOpen: "Abrir fuente",
    comparison: {
      eyebrow: "Comparador con evidencia",
      title: "Compara tecnologías sin inventar datos.",
      technologies: "Tecnologías (2 a 4)",
      criteria: "Criterios",
      compare: "Comparar",
      cancel: "Cancelar",
      ready: "Listo para comparar.",
      accepted: "Comparación aceptada…",
      verified: "Comparación verificada.",
      unsupported: "Sin evidencia",
      partial: "Parcial",
      contradictory: "Contradictoria",
      noEvidence: "No hay evidencia verificada disponible para esta celda.",
      criterionLabels: {
        capability: "Capacidad",
        tool_calling: "Llamada de herramientas",
        context: "Contexto",
        latency: "Latencia",
        price: "Precio",
        license: "Licencia",
        freshness: "Actualización",
        operational_risk: "Riesgo operativo",
      },
    },
  },
};

type LocaleContextValue = {
  locale: Locale;
  setLocale: (locale: Locale) => void;
  messages: MessageCatalog;
};

const LocaleContext = createContext<LocaleContextValue | null>(null);

function getInitialLocale(): Locale {
  if (typeof window === "undefined") return "en-US";
  const pathLocale = window.location.pathname.split("/")[1];
  const stored = window.localStorage.getItem("atlas-locale");
  const browserLocale = window.navigator.language.toLowerCase().startsWith("es") ? "es-MX" : "en-US";
  return pathLocale === "es" || stored === "es-MX" || (!stored && browserLocale === "es-MX") ? "es-MX" : "en-US";
}

export function LocaleProvider({ children }: { children: ReactNode }) {
  // Render the same locale on the server and the first client pass. The URL,
  // browser language and persisted preference are applied after hydration so
  // localized routes do not produce a different AppShell during hydration.
  const [locale, setLocaleState] = useState<Locale>("en-US");

  useEffect(() => {
    const initial = getInitialLocale();
    // eslint-disable-next-line react-hooks/set-state-in-effect -- apply the persisted/path locale after the stable SSR pass
    setLocaleState(initial);
    document.documentElement.lang = initial;
  }, []);

  const setLocale = (next: Locale) => {
    setLocaleState(next);
    if (typeof window !== "undefined") {
      window.localStorage.setItem("atlas-locale", next);
      document.cookie = `atlas-locale=${next}; Path=/; Max-Age=31536000; SameSite=Lax`;
      document.documentElement.lang = next;
      const pathLocale = next === "es-MX" ? "es" : "en";
      if (window.location.pathname === "/" || window.location.pathname === "/en" || window.location.pathname === "/es") {
        window.history.replaceState({}, "", `/${pathLocale}`);
      }
    }
  };

  useEffect(() => {
    document.documentElement.lang = locale;
  }, [locale]);

  const value = useMemo(() => ({ locale, setLocale, messages: catalogs[locale] }), [locale]);
  return createElement(LocaleContext.Provider, { value }, children);
}

export function useLocale(): LocaleContextValue {
  const value = useContext(LocaleContext);
  if (!value) throw new Error("useLocale must be used inside LocaleProvider");
  return value;
}

export function formatDate(value: string | null | undefined, locale: Locale, dateStyle: "long" | "medium" = "long"): string {
  if (!value) return catalogs[locale].notVerified;
  return new Intl.DateTimeFormat(locale, { dateStyle, timeZone: "UTC" }).format(new Date(value));
}
