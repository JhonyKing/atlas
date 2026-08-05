"use client";

import { FormEvent, useEffect, useRef, useState } from "react";

import { cancelAnswer, streamCitedAnswer } from "./api";
import { EvidencePanel } from "../evidence/EvidencePanel";
import { putAnswerFeedback } from "../evidence/api";
import type { FeedbackInput } from "../evidence/types";
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
  const [question, setQuestion] = useState("");
  const [product, setProduct] = useState<CollectionSlug | "">("");
  const [status, setStatus] = useState("Ready to verify an answer.");
  const [error, setError] = useState<string | null>(null);
  const [answer, setAnswer] = useState<CompletedAnswer | null>(null);
  const [abstention, setAbstention] = useState<AbstentionNotice | null>(null);
  const [active, setActive] = useState(false);
  const [runId, setRunId] = useState<string | null>(null);
  const controller = useRef<AbortController | null>(null);
  const shellRef = useRef<HTMLElement | null>(null);

  useEffect(() => {
    shellRef.current?.setAttribute("data-hydrated", "true");
  }, []);

  function validate(): string | null {
    if (question.trim().length < 3 || !/[\p{L}\p{N}]/u.test(question)) {
      return "Enter a technical question with at least one word or number.";
    }
    if ((question.match(/\?/g) ?? []).length > 1) {
      return "Ask one related question at a time so every claim can be verified.";
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
    setStatus("Accepted. Preparing retrieval…");
    const nextController = new AbortController();
    controller.current = nextController;
    const input: AskQuestionInput = { question };
    if (product) input.product = product;
    try {
      const nextRunId = await streamCitedAnswer(
        input,
        handleEvent,
        nextController.signal,
        setRunId,
      );
      setRunId(nextRunId);
    } catch (caught) {
      if (!nextController.signal.aborted) {
        setError(caught instanceof Error ? caught.message : "ATLAS could not complete the request.");
        setStatus("Request ended without a verified answer.");
      }
    } finally {
      if (!nextController.signal.aborted) setActive(false);
      controller.current = null;
    }
  }

  function handleEvent(event: AnswerEvent) {
    const stage = typeof event.data.stage === "string" ? event.data.stage : event.event;
    const answerStatus = event.data.answer_status === "partial" ? "partial" : "complete";
    setStatus(
      stage === "completed"
        ? answerStatus === "partial"
          ? "Partial answer ready."
          : "Verified answer ready."
        : `${stage}…`,
    );
    if (event.event === "answer.completed") {
      setAbstention(null);
      setAnswer({
        answerStatus,
        claims: Array.isArray(event.data.claims) ? (event.data.claims as CitedClaim[]) : [],
        citations: Array.isArray(event.data.citations)
          ? (event.data.citations as CitedEvidence[])
          : [],
        limitations: Array.isArray(event.data.limitations) ? (event.data.limitations as string[]) : [],
      });
      setActive(false);
    }
    if (event.event === "answer.abstained") {
      const limitations = Array.isArray(event.data.limitations)
        ? event.data.limitations.filter((value): value is string => typeof value === "string")
        : [];
      const notice: AbstentionNotice = {
        limitations: limitations.length
          ? limitations
          : ["ATLAS could not verify an answer from the available evidence."],
      };
      if (typeof event.data.scope_suggestion === "string") {
        notice.scopeSuggestion = event.data.scope_suggestion;
      }
      if (typeof event.data.scope_explanation === "string") {
        notice.scopeExplanation = event.data.scope_explanation;
      }
      setAbstention(notice);
      setError(notice.limitations.join(" "));
      setActive(false);
    }
  }

  async function cancel() {
    controller.current?.abort();
    if (runId) await cancelAnswer(runId).catch(() => undefined);
    setActive(false);
    setStatus("Cancellation requested.");
  }

  async function handleFeedback(feedback: FeedbackInput) {
    if (!runId) {
      setError("ATLAS could not associate feedback with this answer.");
      return;
    }
    try {
      await putAnswerFeedback(runId, feedback);
      setError(null);
      setStatus("Feedback saved.");
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "ATLAS could not save this feedback.");
    }
  }

  return (
    <section
      ref={shellRef}
      className="answer-shell"
      aria-labelledby="page-title"
      data-hydrated="false"
    >
      <p className="eyebrow">ATLAS AI · evidence-first research</p>
      <h1 id="page-title">Answers you can verify.</h1>
      <p className="lede">
        Ask one technical question about the curated LangGraph, LangChain, or OpenAI corpus.
        Claims appear only after their evidence is checked.
      </p>
      <form onSubmit={submit} noValidate>
        <label htmlFor="question">Technical question</label>
        <textarea
          id="question"
          value={question}
          onChange={(event) => setQuestion(event.target.value)}
          aria-invalid={Boolean(error)}
          aria-describedby={error ? "question-error" : undefined}
          rows={5}
          placeholder="How does LangGraph persist state across a workflow?"
        />
        <label htmlFor="product">Corpus (optional)</label>
        <select id="product" value={product} onChange={(event) => setProduct(event.target.value as CollectionSlug | "")}>
          <option value="">All supported collections</option>
          <option value="langgraph">LangGraph</option>
          <option value="langchain">LangChain</option>
          <option value="openai">OpenAI API</option>
        </select>
        {error ? <p id="question-error" className="error" role="alert">{error}</p> : null}
        <div className="actions">
          <button type="submit" disabled={active}>Ask ATLAS</button>
          {active ? <button type="button" className="secondary" onClick={cancel}>Cancel request</button> : null}
        </div>
      </form>
      <p className="progress" role="status" aria-live="polite">{status}</p>
      {answer ? (
        <EvidencePanel
          answerStatus={answer.answerStatus}
          claims={answer.claims}
          citations={answer.citations}
          limitations={answer.limitations}
          onFeedback={handleFeedback}
        />
      ) : null}
      {abstention ? <AbstentionResult notice={abstention} /> : null}
    </section>
  );
}

function AbstentionResult({ notice }: { notice: AbstentionNotice }) {
  return (
    <article className="abstention-result" aria-labelledby="abstention-title">
      <h2 id="abstention-title">ATLAS could not verify this answer</h2>
      <ul>
        {notice.limitations.map((limitation) => <li key={limitation}>{limitation}</li>)}
      </ul>
      {notice.scopeExplanation ? <p>{notice.scopeExplanation}</p> : null}
      {notice.scopeSuggestion ? <p>{notice.scopeSuggestion}</p> : null}
    </article>
  );
}
