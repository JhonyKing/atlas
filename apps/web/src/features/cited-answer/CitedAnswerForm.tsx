"use client";

import { FormEvent, useEffect, useRef, useState } from "react";

import { cancelAnswer, streamCitedAnswer } from "./api";
import type {
  AnswerEvent,
  AskQuestionInput,
  CitedClaim,
  CitedEvidence,
  CollectionSlug,
} from "./types";

type CompletedAnswer = {
  claims: CitedClaim[];
  citations: CitedEvidence[];
  limitations: string[];
};

export function CitedAnswerForm() {
  const [question, setQuestion] = useState("");
  const [product, setProduct] = useState<CollectionSlug | "">("");
  const [status, setStatus] = useState("Ready to verify an answer.");
  const [error, setError] = useState<string | null>(null);
  const [answer, setAnswer] = useState<CompletedAnswer | null>(null);
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
    setStatus(stage === "completed" ? "Verified answer ready." : `${stage}…`);
    if (event.event === "answer.completed") {
      setAnswer({
        claims: Array.isArray(event.data.claims) ? (event.data.claims as CitedClaim[]) : [],
        citations: Array.isArray(event.data.citations)
          ? (event.data.citations as CitedEvidence[])
          : [],
        limitations: Array.isArray(event.data.limitations) ? (event.data.limitations as string[]) : [],
      });
      setActive(false);
    }
    if (event.event === "answer.abstained") {
      setError("ATLAS could not verify an answer from the available evidence.");
      setActive(false);
    }
  }

  async function cancel() {
    controller.current?.abort();
    if (runId) await cancelAnswer(runId).catch(() => undefined);
    setActive(false);
    setStatus("Cancellation requested.");
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
      {answer ? <AnswerResult answer={answer} /> : null}
    </section>
  );
}

function AnswerResult({ answer }: { answer: CompletedAnswer }) {
  return (
    <article className="answer-result" aria-labelledby="answer-title">
      <h2 id="answer-title">Verified answer</h2>
      <ol>
        {answer.claims.map((claim) => <li key={claim.id}>{claim.text}</li>)}
      </ol>
      {answer.limitations.length ? <p>{answer.limitations.join(" ")}</p> : null}
      <h3>Evidence</h3>
      <ul>
        {answer.citations.map((citation) => (
          <li key={citation.id}>
            <a href={citation.canonical_url} target="_blank" rel="noreferrer">
              Open {citation.source_title}
            </a>
            <p>{citation.excerpt}</p>
          </li>
        ))}
      </ul>
    </article>
  );
}
