"use client";

import { useCallback, useEffect, useRef, useState, type KeyboardEvent, type ReactNode } from "react";
import { fetchHistory, fetchSession, fetchStatus, sendFeedback, streamChat } from "@/lib/api";
import { DICTS, formatTime, type Topic } from "@/lib/i18n";
import {
  RETRIEVAL_METHODS,
  TOP_K_OPTIONS,
  type ApiStatus,
  type ChatTurn,
  type Locale,
  type RetrievalMethod,
  type SessionSummary,
} from "@/lib/types";
import { AssistantMessage, type UiMessage } from "./AssistantMessage";
import {
  ArrowUpIcon,
  AwardIcon,
  BookIcon,
  CalendarIcon,
  ClipboardIcon,
  GiftIcon,
  MenuIcon,
  MicIcon,
  SlidersIcon,
  SparkleIcon,
  WalletIcon,
} from "./Icons";
import { Sidebar } from "./Sidebar";

const STAFF_URL = process.env.NEXT_PUBLIC_STAFF_CONTACT_URL || "#";
const DEFAULT_LOCALE: Locale = process.env.NEXT_PUBLIC_DEFAULT_LOCALE === "en" ? "en" : "th";
const LOCALE_KEY = "unirag.locale";
const THEME_KEY = "unirag.theme";

export type Theme = "light" | "dark";

const TOPIC_ICON: Record<Topic, ReactNode> = {
  registration: <ClipboardIcon />,
  tuition: <WalletIcon />,
  honors: <AwardIcon />,
  course: <BookIcon />,
  leave: <CalendarIcon />,
  scholarship: <GiftIcon />,
};

function uid() {
  return typeof crypto !== "undefined" && "randomUUID" in crypto
    ? crypto.randomUUID()
    : Math.random().toString(36).slice(2);
}

function turnsToMessages(turns: ChatTurn[]): UiMessage[] {
  return turns.map((turn) => ({
    id: turn.response?.message_id ?? uid(),
    role: turn.role,
    text: turn.content,
    created_at: turn.created_at,
    response: turn.response,
  }));
}

function readStorage(key: string) {
  try {
    return localStorage.getItem(key);
  } catch {
    return null; // storage unavailable (private mode)
  }
}

function writeStorage(key: string, value: string) {
  try {
    localStorage.setItem(key, value);
  } catch {
    // ignore
  }
}

// Minimal typing for the Web Speech API (not in the TS DOM lib).
interface SpeechRec {
  lang: string;
  interimResults: boolean;
  onresult: (e: { results: ArrayLike<ArrayLike<{ transcript: string }>> }) => void;
  onend: () => void;
  onerror: () => void;
  start: () => void;
  stop: () => void;
}
type SpeechRecCtor = new () => SpeechRec;

function getSpeechRecognition(): SpeechRecCtor | null {
  if (typeof window === "undefined") return null;
  const w = window as unknown as { SpeechRecognition?: SpeechRecCtor; webkitSpeechRecognition?: SpeechRecCtor };
  return w.SpeechRecognition ?? w.webkitSpeechRecognition ?? null;
}

export default function ChatApp() {
  const [mounted, setMounted] = useState(false);
  const [locale, setLocale] = useState<Locale>(DEFAULT_LOCALE);
  const [theme, setTheme] = useState<Theme>("light");
  const [method, setMethod] = useState<RetrievalMethod>("hybrid_rrf");
  const [topK, setTopK] = useState(5);
  const [status, setStatus] = useState<ApiStatus | null>(null);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [messages, setMessages] = useState<UiMessage[]>([]);
  const [input, setInput] = useState("");
  const [busy, setBusy] = useState(false);
  const [feedback, setFeedback] = useState<Record<string, "up" | "down">>({});
  const [sessions, setSessions] = useState<SessionSummary[]>([]);
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [settingsOpen, setSettingsOpen] = useState(false);
  const [listening, setListening] = useState(false);
  const [micSupported, setMicSupported] = useState(false);

  const endRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);
  const recRef = useRef<SpeechRec | null>(null);
  const settingsRef = useRef<HTMLDivElement>(null);

  const t = DICTS[locale];

  const refreshHistory = useCallback(() => {
    fetchHistory().then(setSessions).catch(() => undefined);
  }, []);

  useEffect(() => {
    setMounted(true);
    setMicSupported(getSpeechRecognition() !== null);
    const savedLocale = readStorage(LOCALE_KEY);
    if (savedLocale === "th" || savedLocale === "en") setLocale(savedLocale);
    const savedTheme = readStorage(THEME_KEY);
    if (savedTheme === "light" || savedTheme === "dark") setTheme(savedTheme);
    else if (window.matchMedia("(prefers-color-scheme: dark)").matches) setTheme("dark");
    fetchStatus().then(setStatus).catch(() => setStatus(null));
    refreshHistory();

    // Always open on a new chat. Older chats stay in the sidebar history.
    const startNewChat = () => {
      setSessionId(null);
      setMessages([]);
      setInput("");
      setFeedback({});
    };
    startNewChat();
    // The browser can restore this page from its back/forward cache (Back button, reopened tab)
    // with the old chat still in memory; reset it in that case too.
    const onPageShow = (e: PageTransitionEvent) => {
      if (e.persisted) {
        startNewChat();
        refreshHistory();
      }
    };
    window.addEventListener("pageshow", onPageShow);
    return () => window.removeEventListener("pageshow", onPageShow);
  }, [refreshHistory]);

  useEffect(() => {
    document.documentElement.lang = locale;
  }, [locale]);

  useEffect(() => {
    if (mounted) document.documentElement.dataset.theme = theme;
  }, [theme, mounted]);

  useEffect(() => {
    endRef.current?.scrollIntoView({ block: "end", behavior: "smooth" });
  }, [messages]);

  // Close the settings popover on outside click / Escape.
  useEffect(() => {
    if (!settingsOpen) return;
    const onDown = (e: MouseEvent) => {
      if (!settingsRef.current?.contains(e.target as Node)) setSettingsOpen(false);
    };
    const onKey = (e: globalThis.KeyboardEvent) => e.key === "Escape" && setSettingsOpen(false);
    document.addEventListener("mousedown", onDown);
    document.addEventListener("keydown", onKey);
    return () => {
      document.removeEventListener("mousedown", onDown);
      document.removeEventListener("keydown", onKey);
    };
  }, [settingsOpen]);

  // Auto-grow the composer.
  useEffect(() => {
    const el = inputRef.current;
    if (!el) return;
    el.style.height = "auto";
    el.style.height = `${Math.min(el.scrollHeight, 180)}px`;
  }, [input]);

  const changeLocale = (l: Locale) => {
    setLocale(l);
    writeStorage(LOCALE_KEY, l);
  };

  const changeTheme = (next: Theme) => {
    setTheme(next);
    writeStorage(THEME_KEY, next);
  };

  const send = useCallback(
    async (raw: string) => {
      const message = raw.trim();
      if (!message || busy) return;
      setInput("");
      setBusy(true);
      const now = new Date().toISOString();
      const botId = uid();
      setMessages((m) => [
        ...m,
        { id: uid(), role: "user", text: message, created_at: now },
        { id: botId, role: "assistant", text: "", created_at: now, streaming: true, method },
      ]);
      const update = (fn: (x: UiMessage) => UiMessage) =>
        setMessages((m) => m.map((x) => (x.id === botId ? fn(x) : x)));

      try {
        const res = await streamChat({ session_id: sessionId, message, method, top_k: topK, locale }, (delta) =>
          update((x) => ({ ...x, text: x.text + delta })),
        );
        setSessionId(res.session_id);
        update((x) => ({ ...x, text: res.answer, response: res, streaming: false, created_at: res.timestamp }));
        refreshHistory();
      } catch {
        update((x) => ({ ...x, streaming: false, error: true, retryText: message }));
      } finally {
        setBusy(false);
        inputRef.current?.focus();
      }
    },
    [busy, sessionId, method, topK, locale, refreshHistory],
  );

  const retry = (msg: UiMessage) => {
    setMessages((m) => {
      const i = m.findIndex((x) => x.id === msg.id);
      return m.filter((_, j) => j !== i && j !== i - 1);
    });
    if (msg.retryText) send(msg.retryText);
  };

  const giveFeedback = async (messageId: string, rating: "up" | "down") => {
    setFeedback((f) => ({ ...f, [messageId]: rating }));
    try {
      await sendFeedback(messageId, rating);
    } catch {
      // feedback is best-effort; keep the UI state
    }
  };

  const newChat = () => {
    setSessionId(null);
    setMessages([]);
    setSidebarOpen(false);
    inputRef.current?.focus();
  };

  const loadSession = async (id: string) => {
    try {
      const s = await fetchSession(id);
      setSessionId(s.session_id);
      setMessages(turnsToMessages(s.turns));
      setSidebarOpen(false);
    } catch {
      refreshHistory();
    }
  };

  const toggleMic = () => {
    if (listening) {
      recRef.current?.stop();
      return;
    }
    const SR = getSpeechRecognition();
    if (!SR) return;
    const rec = new SR();
    rec.lang = locale === "th" ? "th-TH" : "en-US";
    rec.interimResults = false;
    rec.onresult = (e) => {
      const text = Array.from(e.results)
        .map((r) => r[0].transcript)
        .join("");
      setInput((v) => (v ? `${v} ${text}` : text));
    };
    rec.onend = () => setListening(false);
    rec.onerror = () => setListening(false);
    recRef.current = rec;
    rec.start();
    setListening(true);
  };

  const onKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    // isComposing: don't send while a Thai/IME composition is in progress
    if (e.key === "Enter" && !e.shiftKey && !e.nativeEvent.isComposing) {
      e.preventDefault();
      send(input);
    }
  };

  return (
    <div className="shell">
      <Sidebar
        open={sidebarOpen}
        t={t}
        locale={locale}
        status={status}
        sessions={sessions}
        currentId={sessionId}
        busy={busy}
        onClose={() => setSidebarOpen(false)}
        onNewChat={newChat}
        onSelect={loadSession}
        onLocale={changeLocale}
        theme={theme}
        onTheme={changeTheme}
      />

      <div className="main">
        {/* Small screens only: menu button that opens the sidebar (hidden on desktop) */}
        <header className="topbar">
          <button type="button" className="icon-btn menu-btn" onClick={() => setSidebarOpen(true)} aria-label={t.menu}>
            <MenuIcon />
          </button>
        </header>

        <main className="scroll">
          {mounted && messages.length === 0 ? (
            <section className="hero">
              <h2 className="hero-title">{t.heroTitle}</h2>
              <p className="hero-sub">{t.heroSubtitle}</p>
              <div className="cards">
                {t.suggestionCards.map((c) => (
                  <button key={c.topic} type="button" className="s-card" onClick={() => send(c.q)} disabled={busy}>
                    <span className={`s-icon topic-${c.topic}`}>{TOPIC_ICON[c.topic]}</span>
                    <span className="s-label">{c.label}</span>
                    <span className="s-q">{c.q}</span>
                  </button>
                ))}
              </div>
            </section>
          ) : (
            <div className="thread">
              {messages.map((m) =>
                m.role === "user" ? (
                  <div key={m.id} className="msg-user">
                    <div className="user-bubble">{m.text}</div>
                    <span className="msg-time">{formatTime(m.created_at, locale)}</span>
                  </div>
                ) : (
                  <div key={m.id} className="msg-bot">
                    <div className="bot-avatar">
                      <SparkleIcon width={16} height={16} />
                    </div>
                    <div className="bot-body">
                      <AssistantMessage
                        msg={m}
                        t={t}
                        locale={locale}
                        busy={busy}
                        staffUrl={STAFF_URL}
                        feedback={m.response ? feedback[m.response.message_id] : undefined}
                        onFeedback={giveFeedback}
                        onClarify={send}
                        onRetry={retry}
                      />
                    </div>
                  </div>
                ),
              )}
              <div ref={endRef} />
            </div>
          )}
        </main>

        <div className="composer-area">
          <div className="composer">
            <textarea
              ref={inputRef}
              rows={1}
              autoComplete="off"
              value={input}
              placeholder={t.placeholder}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={onKeyDown}
              maxLength={2000}
              aria-label={t.placeholder}
            />
            <div className="composer-actions">
              {/* Search method + number of references, next to the mic button */}
              <div className="settings" ref={settingsRef}>
                <button
                  type="button"
                  className={`pill-btn composer-pill ${settingsOpen ? "on" : ""}`}
                  onClick={() => setSettingsOpen((v) => !v)}
                  aria-expanded={settingsOpen}
                  aria-label={t.settings}
                  title={t.settings}
                >
                  <SlidersIcon width={16} height={16} />
                  <span className="pill-label">
                    {t.methods[method]} · {topK}
                  </span>
                </button>
                {settingsOpen && (
                  <div className="popover up" role="dialog" aria-label={t.settings}>
                    <div className="pop-title">{t.method}</div>
                    <div className="method-list">
                      {RETRIEVAL_METHODS.map((m) => (
                        <button
                          key={m}
                          type="button"
                          className={`method ${method === m ? "on" : ""}`}
                          onClick={() => setMethod(m)}
                        >
                          <span className="radio" />
                          <span>
                            <strong>{t.methods[m]}</strong>
                            <small>{t.methodHints[m]}</small>
                          </span>
                        </button>
                      ))}
                    </div>
                    <div className="pop-title">{t.references}</div>
                    <div className="segmented full">
                      {TOP_K_OPTIONS.map((k) => (
                        <button key={k} type="button" className={topK === k ? "on" : ""} onClick={() => setTopK(k)}>
                          {k}
                        </button>
                      ))}
                    </div>
                  </div>
                )}
              </div>
              <button
                type="button"
                className={`icon-btn mic ${listening ? "on" : ""}`}
                onClick={toggleMic}
                disabled={!micSupported}
                title={micSupported ? (listening ? t.micStop : t.micStart) : t.micUnsupported}
                aria-label={micSupported ? (listening ? t.micStop : t.micStart) : t.micUnsupported}
              >
                <MicIcon />
              </button>
              <button
                type="button"
                className="send-btn"
                onClick={() => send(input)}
                disabled={busy || !input.trim()}
                aria-label={t.send}
                title={t.send}
              >
                <ArrowUpIcon width={18} height={18} strokeWidth={2.4} />
              </button>
            </div>
          </div>
          <p className="footnote">{t.footer}</p>
        </div>
      </div>
    </div>
  );
}
