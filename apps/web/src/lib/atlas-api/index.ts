/** Typed browser client entry point for the ATLAS HTTP/SSE contract. */

export { AtlasApiError, cancelAnswer, streamCitedAnswer } from "@/features/cited-answer/api";
export type { AnswerEvent, AnswerEventHandler, AskQuestionInput } from "@/features/cited-answer/types";
