// In-memory conversation and feedback store for the mock API (stands in for 07_response_logging).
// Data is lost when the dev server restarts.

import type { ChatResponse, ChatTurn, SessionDetail, SessionSummary } from "../types";

interface Session {
  session_id: string;
  title: string;
  updated_at: string;
  turns: ChatTurn[];
}

interface Feedback {
  message_id: string;
  rating: "up" | "down";
  comment?: string;
  created_at: string;
}

interface Store {
  sessions: Map<string, Session>;
  feedback: Feedback[];
}

// Kept on globalThis so all route handlers share one store in dev (hot reload).
const g = globalThis as unknown as { __uniragStore?: Store };
const store: Store = (g.__uniragStore ??= { sessions: new Map(), feedback: [] });

export function appendTurns(sessionId: string, message: string, response: ChatResponse) {
  const now = new Date().toISOString();
  let s = store.sessions.get(sessionId);
  if (!s) {
    s = { session_id: sessionId, title: message.slice(0, 60), updated_at: now, turns: [] };
    store.sessions.set(sessionId, s);
  }
  s.turns.push({ role: "user", content: message, created_at: now });
  s.turns.push({ role: "assistant", content: response.answer, created_at: now, response });
  s.updated_at = now;
}

export function listSessions(): SessionSummary[] {
  return Array.from(store.sessions.values())
    .sort((a, b) => b.updated_at.localeCompare(a.updated_at))
    .map((s) => ({
      session_id: s.session_id,
      title: s.title,
      updated_at: s.updated_at,
      message_count: s.turns.length,
    }));
}

export function getSession(id: string): SessionDetail | null {
  const s = store.sessions.get(id);
  return s ? { session_id: s.session_id, turns: s.turns } : null;
}

export function messageExists(messageId: string) {
  for (const s of Array.from(store.sessions.values())) {
    if (s.turns.some((t) => t.response?.message_id === messageId)) return true;
  }
  return false;
}

export function addFeedback(f: Omit<Feedback, "created_at">) {
  store.feedback = store.feedback.filter((x) => x.message_id !== f.message_id);
  store.feedback.push({ ...f, created_at: new Date().toISOString() });
}
