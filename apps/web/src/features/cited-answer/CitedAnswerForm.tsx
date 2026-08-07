"use client";

import { FormEvent, useEffect, useRef, useState } from "react";

import { useLocale, type Locale } from "@/i18n";

import { AtlasLogo } from "@/components/brand/AtlasLogo";
import { Button, Field, Select, Textarea } from "@/components/forms";
import { ResearchProgress, type ResearchStep } from "@/components/research/ResearchProgress";

import { EvidencePanel } from "../evidence/EvidencePanel";
import { putAnswerFeedback } from "../evidence/api";
import type { FeedbackInput } from "../evidence/types";
import { AtlasApiError, cancelAnswer, streamCitedAnswer } from "./api";
import type {
  AnswerEvent,
  AskQuestionInput,
  CitedClaim,
  CitedEvidence,
  CollectionSlug,
} from "./types";

type CompletedAnswer = {
  answerStatus: "complete" | "partial";
  claims: CitedClaim[];
  citations: CitedEvidence[];
  limitations: string[];
};

type AbstentionNotice = {
  limitations: string[];
  scopeSuggestion?: string;
  scopeExplanation?: string;
};

export function CitedAnswerForm() {
  const { locale, setLocale, messages } = useLocale();
  const [question, setQuestion] = useState("");
  const [product, setProduct] = useState<CollectionSlug | "">("");
  const [status, setStatus] = useState(messages.ready);
  const [stageKey, setStageKey] = useState("accepted");
  const [error, setError] = useState<string | null>(null);
  const [answer, setAnswer] = useState<CompletedAnswer | null>(null);
  const [abstention, setAbstention] = useState<AbstentionNotice | null>(null);
  const [active, setActive] = useState(false);
  const [runId, setRunId] = useState<string | null>(null);
  const runIdRef = useRef<string | null>(null);
  const cancelRequestedRef = useRef(false);
  const controller = useRef<AbortController | null>(null);
  const shellRef = useRef<HTMLElement | null>(null);

  useEffect(() => {
    shellRef.current?.setAttribute("data-hydrated", "true");
  }, []);

  function validate(): string | null {
    if (question.trim().length < 3 || !/[\p{L}\p{N}]/u.test(question)) {
      return messages.invalidQuestion;
    }
    if ((question.match(/\?/g) ?? []).length > 1) {
      return messages.invalidMultiple;
    }
    return null;
  }

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const validationError = validate();
    if (validationError) {
      setError(validationError);
      return;
    }
    setError(null);
    setAnswer(null);
    setAbstention(null);
    setActive(true);
    setStatus(messages.accepted);
    setStageKey("accepted");
    cancelRequestedRef.current = false;
    const nextController = new AbortController();
    controller.current = nextController;
    const input: AskQuestionInput = { question, language: locale };
    if (product) input.product = product;
    try {
      const nextRunId = await streamCitedAnswer(
        input,
        handleEvent,
        nextController.signal,
        (nextRunId) => {
          runIdRef.current = nextRunId;
          setRunId(nextRunId);
          if (cancelRequestedRef.current) void cancelAnswer(nextRunId);
        },
      );
      runIdRef.current = nextRunId;
      setRunId(nextRunId);
    } catch (caught) {
      if (!nextController.signal.aborted) {
        const message = caught instanceof AtlasApiError
          ? messages.genericRequestError
          : caught instanceof TypeError
            ? messages.networkError
            : caught instanceof Error
              ? caught.message
              : messages.genericRequestError;
        setError(message);
        setStatus(messages.requestEnded);
      }
    } finally {
      if (!nextController.signal.aborted) setActive(false);
      controller.current = null;
    }
  }

  function handleEvent(event: AnswerEvent) {
    const stage = typeof event.data.stage === "string" ? event.data.stage : event.event;
    setStageKey(event.event === "answer.completed" ? "completed" : event.event === "answer.abstained" ? "abstained" : stage);
    const answerStatus = event.data.answer_status === "partial" ? "partial" : "complete";
    setStatus(
      stage === "completed"
        ? answerStatus === "partial" ? messages.partialReady : messages.verifiedReady
        : `${messages.stage[stage] ?? stage}...`,
    );
    if (event.event === "answer.completed") {
      setAbstention(null);
      setAnswer({
        answerStatus,
        claims: Array.isArray(event.data.claims) ? (event.data.claims as CitedClaim[]) : [],
        citations: Array.isArray(event.data.citations) ? (event.data.citations as CitedEvidence[]) : [],
        limitations: Array.isArray(event.data.limitations) ? (event.data.limitations as string[]) : [],
      });
      setActive(false);
    }
    if (event.event === "answer.abstained") {
      const limitations = Array.isArray(event.data.limitations)
        ? event.data.limitations.filter((value): value is string => typeof value === "string")
        : [];
      const notice: AbstentionNotice = {
        limitations: limitations.length ? limitations : [messages.defaultAbstention],
      };
      if (typeof event.data.scope_suggestion === "string") notice.scopeSuggestion = event.data.scope_suggestion;
      if (typeof event.data.scope_explanation === "string") notice.scopeExplanation = event.data.scope_explanation;
      setAbstention(notice);
      setError(notice.limitations.join(" "));
      setActive(false);
    }
  }

  async function cancel() {
    cancelRequestedRef.current = true;
    controller.current?.abort();
    if (runIdRef.current) await cancelAnswer(runIdRef.current).catch(() => undefined);
    setActive(false);
    setStatus(messages.stage.cancelled ?? messages.cancel);
  }

  async function handleFeedback(feedback: FeedbackInput) {
    if (!runId) {
      setError(messages.feedbackAssociationError);
      return;
    }
    try {
      await putAnswerFeedback(runId, feedback);
      setError(null);
      setStatus(messages.feedbackSaved);
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : messages.feedbackSaveError);
    }
  }

  return (
    <section ref={shellRef} className="answer-shell ask-experience" aria-labelledby="page-title" data-hydrated="false">
      <div className="ask-branding"><AtlasLogo variant="stacked" alt="ATLAS" className="ask-branding-logo" /></div>
      <div className="locale-control-legacy">
        <label htmlFor="locale">{messages.switchLabel}</label>
        <select id="locale" value={locale} onChange={(event) => setLocale(event.target.value as Locale)} aria-label={messages.switchTo}>
          <option value="en-US">English</option>
          <option value="es-MX">Español</option>
        </select>
      </div>
      <p className="eyebrow">{messages.eyebrow}</p>
      <h1 id="page-title">{messages.title}</h1>
      <p className="lede">{messages.lede}</p>
      <p className="ask-trust-note">{messages.trustNote}</p>
      <form onSubmit={submit} noValidate>
        <Field id="question" label={messages.technicalQuestion} helper={messages.trustNote} error={error ?? undefined}>
          <Textarea
            id="question"
            value={question}
            onChange={(event) => setQuestion(event.target.value)}
            aria-invalid={Boolean(error)}
            rows={5}
            placeholder={messages.questionPlaceholder}
          />
        </Field>
        <Field id="product" label={messages.corpus}>
          <Select id="product" value={product} onChange={(event) => setProduct(event.target.value as CollectionSlug | "")}>
            <option value="">{messages.allCollections}</option>
            <option value="langgraph">LangGraph</option>
            <option value="langchain">LangChain</option>
            <option value="openai">OpenAI API</option>
            <option value="anthropic">Anthropic Claude</option>
            <option value="gemini">Google Gemini</option>
          </Select>
        </Field>
        <div className="actions">
          <Button type="submit" disabled={active} loading={active && stageKey === "accepted"}>{messages.ask}</Button>
          {active ? <Button type="button" variant="secondary" onClick={cancel}>{messages.cancel}</Button> : null}
        </div>
      </form>
      <section className="ask-examples" aria-labelledby="ask-examples-title">
        <h2 id="ask-examples-title">{messages.examplesTitle}</h2>
        <div className="ask-example-list">
          {messages.examples.map((example) => <button key={example} type="button" className="ask-example" onClick={() => setQuestion(example)}>{example}</button>)}
        </div>
      </section>
      <p className="ask-supported-sources">{messages.supportedSources}</p>
      {active || answer || abstention ? <ResearchProgress steps={buildResearchSteps(stageKey, messages.stage)} label={messages.stage.verifying ?? "Research progress"} /> : null}
      <p className="progress" role="status" aria-live="polite">{status}</p>
      {answer ? <EvidencePanel answerStatus={answer.answerStatus} claims={answer.claims} citations={answer.citations} limitations={answer.limitations} onFeedback={handleFeedback} /> : null}
      {abstention ? <AbstentionResult notice={abstention} /> : null}
    </section>
  );
}

function buildResearchSteps(stage: string, labels: Record<string, string>): ResearchStep[] {
  const stages = ["accepted", "retrieving", "composing", "verifying", "completed"];
  const terminalFailure = stage === "abstained" || stage === "cancelled";
  const currentIndex = terminalFailure ? stages.length - 1 : Math.max(0, stages.indexOf(stage));
  return stages.map((id, index) => ({
    id,
    label: labels[id] ?? id,
    status: index < currentIndex ? "complete" : index === currentIndex ? terminalFailure ? "error" : stage === "completed" ? "complete" : "active" : "pending",
  }));
}

function AbstentionResult({ notice }: { notice: AbstentionNotice }) {
  const { messages } = useLocale();
  return (
    <article className="abstention-result" aria-labelledby="abstention-title">
      <h2 id="abstention-title">{messages.abstentionTitle}</h2>
      <ul>{notice.limitations.map((limitation) => <li key={limitation}>{limitation}</li>)}</ul>
      {notice.scopeExplanation ? <p>{notice.scopeExplanation}</p> : null}
      {notice.scopeSuggestion ? <p>{notice.scopeSuggestion}</p> : null}
    </article>
  );
}
