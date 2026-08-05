# ATLAS AI cited-answer usability protocol

Status: ready to run; results are intentionally not asserted yet.  
Criterion: SC-007 — at least four of five participants complete all three critical actions without
guidance.

## Ethics and scope

- Recruit five adults who did not build ATLAS. Record the locale used by each participant (`en-US`
  or `es-MX`) and include both locales when feasible.
- Explain that this is a product usability test, not a test of the participant's intelligence.
- Obtain consent before recording notes. Do not collect names, email addresses, account details,
  questions about private systems, or any identifying demographic information.
- Record only a session number (`P1`–`P5`), task outcome, one short non-identifying observation,
  and whether a follow-up defect is required. Delete raw notes after the anonymized result is
  transferred.
- Do not ask participants to enter secrets, personal data, or high-stakes medical/legal/financial
  questions.

## Moderation script

1. “You are trying ATLAS for the first time. Please think aloud, but I will not guide you.”
2. “Choose English or Spanish, then ask one supported technical question about LangGraph,
   LangChain, or the OpenAI API.”
3. “Inspect the evidence for the answer and tell me whether ATLAS verified it.”
4. “Now ask a question outside the published corpus or with insufficient evidence. Tell me whether
   ATLAS answered or abstained, and why.”
5. Thank the participant; do not correct the participant during the tasks.

## Critical actions and scoring

| Action | Pass condition |
|---|---|
| Ask supported question | Participant submits one supported question and reaches a terminal result |
| Inspect evidence | Participant finds the claim, source title/publisher, canonical link, capture date, and excerpt |
| Identify safe failure | Participant recognizes the abstention/limitation and does not treat it as a verified answer |

A participant passes only when all three actions pass without moderator help. A failed critical flow
gets a follow-up defect in the results file; do not change the criterion after observing failures.
