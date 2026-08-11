"use client";

import { createContext, createElement, useContext, useEffect, useMemo, useState, type ReactNode } from "react";

export type Locale = "en-US" | "es-MX";

type EngineeringCapabilityId =
  | "rag"
  | "agents"
  | "retrieval"
  | "verification"
  | "citations"
  | "structured"
  | "persistence"
  | "evals"
  | "observability"
  | "architecture";

type MessageCatalog = {
  localeName: string;
  switchLabel: string;
  switchTo: string;
  eyebrow: string;
  title: string;
  lede: string;
  supportedSources: string;
  trustNote: string;
  examplesTitle: string;
  examples: string[];
  technicalQuestion: string;
  questionPlaceholder: string;
  corpus: string;
  allCollections: string;
  advancedOptions: string;
  sourceHelp: string;
  apiUnavailable: string;
  askSectionTitle: string;
  askSectionLede: string;
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
  home: {
    actionPrompt: string;
    actionAria: string;
    researchBenefit: string;
    askTitle: string;
    askDescription: string;
    compareTitle: string;
    compareDescription: string;
    reportTitle: string;
    reportDescription: string;
    trustPoints: string[];
    builtBy: string;
    github: string;
    architecture: string;
    caseStudy: string;
  };
  engineering: {
    eyebrow: string;
    title: string;
    lede: string;
    flowTitle: string;
    flow: string[];
    capabilitiesTitle: string;
    capabilitiesLede: string;
    evidence: string;
    advancedTitle: string;
    advancedLede: string;
    capabilityCopy: Record<EngineeringCapabilityId, { title: string; summary: string }>;
  };
};

const catalogs: Record<Locale, MessageCatalog> = {
  "en-US": {
    localeName: "English",
    switchLabel: "Language",
    switchTo: "Switch language",
    eyebrow: "ATLAS AI · evidence-first research",
    title: "Answers you can verify.",
    lede: "Research AI topics and get answers backed by sources you can inspect.",
    supportedSources: "Verified sources: LangGraph · LangChain · OpenAI · Anthropic · Gemini",
    trustNote: "Every supported claim includes an inspectable source and capture date.",
    examplesTitle: "Try a real AI decision",
    examples: ["Should I use LangGraph or LangChain for a human-in-the-loop research agent?", "Compare OpenAI and Anthropic tool calling for a production agent.", "What are the trade-offs of long context versus RAG for technical support?"],
    technicalQuestion: "What do you want to research?",
    questionPlaceholder: "Example: Which agent framework fits a human-in-the-loop research workflow?",
    corpus: "Source selection",
    allCollections: "Automatic — use the most relevant verified sources",
    advancedOptions: "Advanced options",
    sourceHelp: "Automatic selection is recommended. Choose a collection only when you need to limit the research scope.",
    apiUnavailable: "Live research is temporarily unavailable while the public service is being connected. You can still explore comparisons, reports, sources, and the engineering case study.",
    askSectionTitle: "Ask a question",
    askSectionLede: "Describe the AI decision, problem, or technology you want ATLAS to investigate.",
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
    networkError: "The ATLAS API is unavailable. Try again later or contact the operator.",
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
    corpusEyebrow: "Sources you can inspect",
    corpusTitle: "Sources ATLAS can verify",
    snapshot: "Snapshot",
    loadingCorpus: "Checking the verified source catalog…",
    unavailableCorpus: "We couldn't load the source catalog. ATLAS will not claim sources it cannot inspect.",
    lastVerified: "Last verified",
    notVerified: "Not yet verified",
    sourceCount: "Sources",
    pageCount: "Pages",
    chunkCount: "Chunks",
    openCanonical: "Open canonical root",
    sourceTypes: { documentation: "documentation", changelog: "changelog", release_note: "release note" },
    states: { ready: "Ready", stale: "Stale", refreshing: "Refreshing", unavailable: "Unavailable" },
    newsEyebrow: "Verified AI news",
    newsTitle: "Yesterday's most important verified AI story",
    newsLoading: "Checking yesterday's AI sources…",
    newsUnavailable: "No story met the evidence threshold for the previous day.",
    newsNoEvidence: "The feed window did not contain enough attributable evidence.",
    newsOriginal: "Original headline and summary",
    newsPublisher: "Publisher",
    newsPublished: "Published",
    newsOpen: "Open source",
    comparison: {
      eyebrow: "Evidence-backed comparator",
      title: "Compare AI technologies for a real decision",
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
    home: {
      actionPrompt: "Start with the outcome you need",
      actionAria: "What would you like to do?",
      researchBenefit: "ATLAS researches technical AI questions, checks each supported claim, and keeps the original source one click away.",
      askTitle: "Ask a question",
      askDescription: "Research an AI problem and inspect the evidence behind the answer.",
      compareTitle: "Compare AI technologies",
      compareDescription: "Evaluate capabilities and trade-offs using the same evidence standard.",
      reportTitle: "Create a report",
      reportDescription: "Turn completed research into a shareable, reproducible document.",
      trustPoints: ["Inspect sources", "See capture dates", "Know when evidence is insufficient"],
      builtBy: "Built by Jhonnatan Vazquez — AI Engineer",
      github: "GitHub",
      architecture: "Architecture",
      caseStudy: "Case study",
    },
    engineering: {
      eyebrow: "Engineering case study",
      title: "How ATLAS earns a verifiable answer.",
      lede: "A production-minded AI research system with explicit retrieval, agent orchestration, verification, persistence, evaluation, and observability boundaries.",
      flowTitle: "From question to inspected evidence",
      flow: ["Understand the request", "Retrieve versioned sources", "Compose structured claims", "Verify every citation", "Return evidence or abstain"],
      capabilitiesTitle: "Engineering depth, with receipts",
      capabilitiesLede: "Each capability links to the public design or verification artifact that supports the claim.",
      evidence: "View evidence",
      advancedTitle: "Advanced agent controls",
      advancedLede: "Inspect the typed tool catalog, permission boundaries, approval decisions, and run timeline used by the agent layer.",
      capabilityCopy: {
        rag: { title: "Evidence-first RAG", summary: "Retrieval-augmented generation is bounded by curated, versioned technical sources." },
        agents: { title: "Explicit agents", summary: "Typed tools and resumable plans keep orchestration inspectable instead of hiding it in a prompt loop." },
        retrieval: { title: "Measured retrieval", summary: "Hybrid retrieval and reranking are evaluated against versioned multilingual cases." },
        verification: { title: "Claim verification", summary: "Factual claims are checked against cited evidence before they can appear as supported." },
        citations: { title: "Inspectable citations", summary: "Source, publisher, bounded excerpt, version, URL, and capture date stay attached to evidence." },
        structured: { title: "Structured outputs", summary: "Validated schemas separate model text from claims, evidence, reports, and tool decisions." },
        persistence: { title: "Durable persistence", summary: "Supabase Postgres stores governed system state with migrations, ownership, and row-level security." },
        evals: { title: "Evaluation gates", summary: "Deterministic and live evaluation records measure citations, usefulness, latency, cost, and regressions." },
        observability: { title: "Safe observability", summary: "LangSmith and application telemetry trace the research path without treating raw sensitive content as a metric." },
        architecture: { title: "Documented architecture", summary: "Specs, plans, tasks, ADRs, contracts, and verification evidence keep implementation decisions reviewable." },
      },
    },
  },
  "es-MX": {
    localeName: "Español",
    switchLabel: "Idioma",
    switchTo: "Cambiar idioma",
    eyebrow: "ATLAS AI · investigación con evidencia",
    title: "Respuestas que puedes verificar.",
    lede: "Investiga temas de IA y obtén respuestas respaldadas por fuentes que puedes inspeccionar.",
    supportedSources: "Fuentes verificadas: LangGraph · LangChain · OpenAI · Anthropic · Gemini",
    trustNote: "Cada afirmación respaldada incluye una fuente y fecha de captura que puedes inspeccionar.",
    examplesTitle: "Prueba una decisión real de IA",
    examples: ["¿Debo usar LangGraph o LangChain para un agente de investigación con revisión humana?", "Compara las llamadas de herramientas de OpenAI y Anthropic para un agente en producción.", "¿Qué ventajas y desventajas tienen el contexto largo y RAG para soporte técnico?"],
    technicalQuestion: "¿Qué quieres investigar?",
    questionPlaceholder: "Ejemplo: ¿Qué framework de agentes conviene para investigar con revisión humana?",
    corpus: "Selección de fuentes",
    allCollections: "Automática — usar las fuentes verificadas más relevantes",
    advancedOptions: "Opciones avanzadas",
    sourceHelp: "Se recomienda la selección automática. Elige una colección sólo cuando necesites limitar la investigación.",
    apiUnavailable: "La investigación en vivo no está disponible temporalmente mientras conectamos el servicio público. Aún puedes explorar comparaciones, reportes, fuentes y el caso de ingeniería.",
    askSectionTitle: "Haz una pregunta",
    askSectionLede: "Describe la decisión, problema o tecnología de IA que quieres que ATLAS investigue.",
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
    networkError: "La API de ATLAS no está disponible. Inténtalo más tarde o contacta al operador.",
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
    corpusEyebrow: "Fuentes que puedes inspeccionar",
    corpusTitle: "Fuentes que ATLAS puede verificar",
    snapshot: "Instantánea",
    loadingCorpus: "Revisando el catálogo de fuentes verificadas…",
    unavailableCorpus: "No pudimos cargar el catálogo de fuentes. ATLAS no afirmará que usa fuentes que no puede inspeccionar.",
    lastVerified: "Última verificación",
    notVerified: "Aún no verificada",
    sourceCount: "Fuentes",
    pageCount: "Páginas",
    chunkCount: "Fragmentos",
    openCanonical: "Abrir raíz canónica",
    sourceTypes: { documentation: "documentación", changelog: "registro de cambios", release_note: "nota de versión" },
    states: { ready: "Lista", stale: "Desactualizada", refreshing: "Actualizando", unavailable: "No disponible" },
    newsEyebrow: "Noticias de IA verificadas",
    newsTitle: "La noticia de IA verificada más importante de ayer",
    newsLoading: "Revisando las fuentes de IA de ayer…",
    newsUnavailable: "Ninguna noticia del día anterior alcanzó el umbral de evidencia.",
    newsNoEvidence: "La ventana de fuentes no tuvo evidencia atribuible suficiente.",
    newsOriginal: "Titular y resumen originales",
    newsPublisher: "Publicador",
    newsPublished: "Publicada",
    newsOpen: "Abrir fuente",
    comparison: {
      eyebrow: "Comparador con evidencia",
      title: "Compara tecnologías de IA para una decisión real",
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
    home: {
      actionPrompt: "Comienza con el resultado que necesitas",
      actionAria: "¿Qué quieres hacer?",
      researchBenefit: "ATLAS investiga preguntas técnicas de IA, comprueba cada afirmación respaldada y mantiene la fuente original a un clic.",
      askTitle: "Haz una pregunta",
      askDescription: "Investiga un problema de IA e inspecciona la evidencia detrás de la respuesta.",
      compareTitle: "Compara tecnologías de IA",
      compareDescription: "Evalúa capacidades y decisiones usando el mismo estándar de evidencia.",
      reportTitle: "Crea un reporte",
      reportDescription: "Convierte una investigación terminada en un documento compartible y reproducible.",
      trustPoints: ["Inspecciona fuentes", "Consulta fechas de captura", "Sabe cuándo falta evidencia"],
      builtBy: "Creado por Jhonnatan Vazquez — Ingeniero de IA",
      github: "GitHub",
      architecture: "Arquitectura",
      caseStudy: "Caso de estudio",
    },
    engineering: {
      eyebrow: "Caso de estudio de ingeniería",
      title: "Cómo ATLAS obtiene una respuesta verificable.",
      lede: "Un sistema de investigación de IA orientado a producción, con límites explícitos para recuperación, agentes, verificación, persistencia, evaluación y observabilidad.",
      flowTitle: "De la pregunta a la evidencia inspeccionada",
      flow: ["Entender la solicitud", "Recuperar fuentes versionadas", "Redactar afirmaciones estructuradas", "Verificar cada cita", "Entregar evidencia o abstenerse"],
      capabilitiesTitle: "Profundidad técnica con evidencia",
      capabilitiesLede: "Cada capacidad enlaza el diseño público o la verificación que respalda la afirmación.",
      evidence: "Ver evidencia",
      advancedTitle: "Controles avanzados del agente",
      advancedLede: "Inspecciona el catálogo de herramientas tipadas, permisos, aprobaciones y la línea de tiempo del agente.",
      capabilityCopy: {
        rag: { title: "RAG basado en evidencia", summary: "La generación aumentada por recuperación se limita a fuentes técnicas curadas y versionadas." },
        agents: { title: "Agentes explícitos", summary: "Herramientas tipadas y planes reanudables hacen visible la orquestación en vez de ocultarla en un prompt." },
        retrieval: { title: "Recuperación medida", summary: "La recuperación híbrida y el reranking se evalúan con casos multilingües versionados." },
        verification: { title: "Verificación de afirmaciones", summary: "Las afirmaciones factuales se contrastan con la evidencia citada antes de mostrarse como respaldadas." },
        citations: { title: "Citas inspeccionables", summary: "Fuente, editor, fragmento, versión, URL y fecha de captura permanecen unidos a la evidencia." },
        structured: { title: "Salidas estructuradas", summary: "Esquemas validados separan el texto del modelo de afirmaciones, evidencia, reportes y decisiones de herramientas." },
        persistence: { title: "Persistencia duradera", summary: "Supabase Postgres guarda estado gobernado con migraciones, propiedad y seguridad por fila." },
        evals: { title: "Compuertas de evaluación", summary: "Evaluaciones deterministas y en vivo miden citas, utilidad, latencia, costo y regresiones." },
        observability: { title: "Observabilidad segura", summary: "LangSmith y la telemetría siguen la investigación sin convertir contenido sensible en una métrica." },
        architecture: { title: "Arquitectura documentada", summary: "Specs, planes, tareas, ADRs, contratos y evidencia mantienen revisables las decisiones." },
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
  // An explicit localized URL is authoritative. Persisted preferences and the
  // browser language are only fallbacks for unprefixed routes.
  if (pathLocale === "es") return "es-MX";
  if (pathLocale === "en") return "en-US";
  const stored = window.localStorage.getItem("atlas-locale");
  const browserLocale = window.navigator.language.toLowerCase().startsWith("es") ? "es-MX" : "en-US";
  return stored === "es-MX" || (!stored && browserLocale === "es-MX") ? "es-MX" : "en-US";
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
