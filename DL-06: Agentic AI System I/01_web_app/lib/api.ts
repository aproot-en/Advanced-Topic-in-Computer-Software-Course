// Client for 02_api_backend. Empty NEXT_PUBLIC_API_BASE_URL = same-origin mock API.

import type { ApiStatus, ChatRequest, ChatResponse, SessionDetail, SessionSummary } from "./types";

const BASE = (process.env.NEXT_PUBLIC_API_BASE_URL ?? "").replace(/\/$/, "");

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    ...init,
    credentials: "include", // auth token lives in an httpOnly cookie
    headers: { "Content-Type": "application/json", ...init?.headers },
  });
  if (!res.ok) throw new Error(`${res.status} ${res.statusText}`);
  return res.json() as Promise<T>;
}

export function fetchStatus() {
  return request<ApiStatus>("/api/status");
}

export function fetchHistory() {
  return request<SessionSummary[]>("/api/history");
}

export function fetchSession(id: string) {
  return request<SessionDetail>(`/api/sessions/${encodeURIComponent(id)}`);
}

export function sendFeedback(messageId: string, rating: "up" | "down") {
  return request<{ ok: boolean }>("/api/feedback", {
    method: "POST",
    body: JSON.stringify({ message_id: messageId, rating }),
  });
}

// POST /api/chat/stream — calls onDelta for each text chunk, resolves with the final response.
export async function streamChat(
  body: ChatRequest,
  onDelta: (text: string) => void,
  signal?: AbortSignal,
): Promise<ChatResponse> {
  const res = await fetch(`${BASE}/api/chat/stream`, {
    method: "POST",
    credentials: "include",
    headers: { "Content-Type": "application/json", Accept: "text/event-stream" },
    body: JSON.stringify(body),
    signal,
  });
  if (!res.ok || !res.body) throw new Error(`${res.status} ${res.statusText}`);

  const reader = res.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";
  let final: ChatResponse | null = null;

  for (;;) {
    const { done, value } = await reader.read();
    if (done) break;
    buffer += decoder.decode(value, { stream: true });
    let idx: number;
    while ((idx = buffer.indexOf("\n\n")) >= 0) {
      const raw = buffer.slice(0, idx);
      buffer = buffer.slice(idx + 2);
      let event = "message";
      let data = "";
      for (const line of raw.split("\n")) {
        if (line.startsWith("event:")) event = line.slice(6).trim();
        else if (line.startsWith("data:")) data += line.slice(5).trim();
      }
      if (!data) continue;
      const payload = JSON.parse(data);
      if (event === "delta") onDelta(payload.text);
      else if (event === "done") final = payload as ChatResponse;
      else if (event === "error") throw new Error(payload.message ?? "stream error");
    }
  }
  if (!final) throw new Error("stream ended without a final response");
  return final;
}
