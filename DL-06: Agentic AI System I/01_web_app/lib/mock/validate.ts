import { RETRIEVAL_METHODS, TOP_K_OPTIONS, type ChatRequest, type RetrievalMethod } from "../types";

const MAX_MESSAGE_CHARS = 2000;

export function parseChatRequest(body: unknown): { value: ChatRequest } | { error: string } {
  if (!body || typeof body !== "object") return { error: "Invalid JSON body" };
  const b = body as Record<string, unknown>;

  const message = typeof b.message === "string" ? b.message.trim() : "";
  if (!message) return { error: "message is required" };
  if (message.length > MAX_MESSAGE_CHARS) return { error: `message exceeds ${MAX_MESSAGE_CHARS} characters` };

  const method = (b.method ?? "hybrid_rrf") as RetrievalMethod;
  if (!RETRIEVAL_METHODS.includes(method)) return { error: "invalid method" };

  const topK = Number(b.top_k ?? 5);
  if (!TOP_K_OPTIONS.includes(topK)) return { error: "invalid top_k" };

  const sessionId = typeof b.session_id === "string" && b.session_id ? b.session_id : null;
  const locale = b.locale === "en" ? "en" : "th";

  return { value: { session_id: sessionId, message, method, top_k: topK, locale } };
}
