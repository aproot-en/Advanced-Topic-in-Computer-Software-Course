// Unified Response Schema [C1] and request/history types shared by the UI and the mock API.

export type Locale = "th" | "en";

export type ResponseType =
  | "answer"
  | "answer_with_citations"
  | "local_task"
  | "clarify"
  | "decline";

export type Engine = "general_ai" | "university_rag" | "local_ai" | "none";

export type SourceCategory = "regulation" | "announcement" | "course" | "handbook";

export type RetrievalMethod = "hybrid_rrf" | "bm25" | "vector";

export interface Source {
  ref: number;
  title: string;
  url: string;
  page: number | null;
  published_at: string;
  category: SourceCategory;
}

export interface ChatResponse {
  message_id: string;
  session_id: string;
  response_type: ResponseType;
  answer: string;
  clarify_options: string[];
  sources: Source[];
  engine_used: Engine;
  confidence: number;
  data_freshness: string | null;
  degraded_services: string[];
  latency_ms: number;
  trace_id: string;
  timestamp: string;
}

export interface ChatRequest {
  session_id: string | null;
  message: string;
  method: RetrievalMethod;
  top_k: number;
  locale: Locale;
}

export interface ChatTurn {
  role: "user" | "assistant";
  content: string;
  created_at: string;
  response?: ChatResponse;
}

export interface SessionSummary {
  session_id: string;
  title: string;
  updated_at: string;
  message_count: number;
}

export interface SessionDetail {
  session_id: string;
  turns: ChatTurn[];
}

export interface ApiStatus {
  mode: "mock" | "live";
  documents: number;
  kb_updated: string | null;
}

export const RETRIEVAL_METHODS: RetrievalMethod[] = ["hybrid_rrf", "bm25", "vector"];
export const TOP_K_OPTIONS = [3, 5, 10];
