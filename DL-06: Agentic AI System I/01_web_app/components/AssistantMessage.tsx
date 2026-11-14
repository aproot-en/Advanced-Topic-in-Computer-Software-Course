"use client";

import { useState, type ReactNode } from "react";
import { confidenceLevel, formatDate, type Dict } from "@/lib/i18n";
import type { ChatResponse, Engine, Locale, RetrievalMethod } from "@/lib/types";
import {
  CheckIcon,
  ChipIcon,
  CopyIcon,
  ExternalIcon,
  GlobeIcon,
  SearchDocIcon,
  ShieldIcon,
  ThumbDownIcon,
  ThumbUpIcon,
  WarnIcon,
} from "./Icons";
import { RichText } from "./RichText";

export interface UiMessage {
  id: string;
  role: "user" | "assistant";
  text: string;
  created_at: string;
  response?: ChatResponse;
  method?: RetrievalMethod;
  streaming?: boolean;
  error?: boolean;
  retryText?: string;
}

const ENGINE_ICON: Record<Engine, ReactNode> = {
  university_rag: <SearchDocIcon width={14} height={14} />,
  general_ai: <GlobeIcon width={14} height={14} />,
  local_ai: <ChipIcon width={14} height={14} />,
  none: <ShieldIcon width={14} height={14} />,
};

interface Props {
  msg: UiMessage;
  t: Dict;
  locale: Locale;
  busy: boolean;
  staffUrl: string;
  feedback?: "up" | "down";
  onFeedback: (messageId: string, rating: "up" | "down") => void;
  onClarify: (option: string) => void;
  onRetry: (msg: UiMessage) => void;
}

// Strip markdown markers so "Copy" gives plain text.
function plainText(answer: string) {
  return answer.replace(/\*\*/g, "").replace(/\s*\[\d+\]/g, "");
}

export function AssistantMessage({ msg, t, locale, busy, staffUrl, feedback, onFeedback, onClarify, onRetry }: Props) {
  const [activeRef, setActiveRef] = useState<number | null>(null);
  const [copied, setCopied] = useState(false);
  const r = msg.response;

  const showRef = (n: number) => {
    setActiveRef(n);
    document.getElementById(`src-${msg.id}-${n}`)?.scrollIntoView({ behavior: "smooth", block: "nearest" });
  };

  const copy = async () => {
    if (!r) return;
    try {
      await navigator.clipboard.writeText(plainText(r.answer));
      setCopied(true);
      setTimeout(() => setCopied(false), 1500);
    } catch {
      // clipboard blocked (non-secure context); nothing to do
    }
  };

  if (msg.error) {
    return (
      <div className="answer-error">
        <WarnIcon width={16} height={16} />
        <span>{t.error}</span>
        <button type="button" className="btn-ghost sm" onClick={() => onRetry(msg)}>
          {t.retry}
        </button>
      </div>
    );
  }

  if (!r) {
    return msg.text ? (
      <div className="answer streaming">
        <RichText text={msg.text} />
      </div>
    ) : (
      <div className="thinking">
        <span className="shimmer">{t.searching}</span>
        <span className="dots">
          <i />
          <i />
          <i />
        </span>
      </div>
    );
  }

  const level = confidenceLevel(r.confidence);
  const bars = level === "high" ? 3 : level === "medium" ? 2 : 1;

  return (
    <div className={`answer type-${r.response_type}`}>
      <div className="answer-meta">
        <span className={`engine-pill engine-${r.engine_used}`}>
          {ENGINE_ICON[r.engine_used]}
          {t.engines[r.engine_used]}
        </span>
        {r.engine_used !== "none" && (
          <span className={`conf conf-${level}`} title={`${Math.round(r.confidence * 100)}%`}>
            <span className="conf-bars" aria-hidden>
              {[1, 2, 3].map((i) => (
                <i key={i} className={i <= bars ? "on" : ""} />
              ))}
            </span>
            {t.confidence(level)}
          </span>
        )}
        {r.data_freshness && <span className="meta-text">{t.dataAsOf(formatDate(r.data_freshness, locale))}</span>}
        {r.engine_used === "university_rag" && msg.method && (
          <span className="meta-text">· {t.methods[msg.method]}</span>
        )}
      </div>

      {r.degraded_services.length > 0 && (
        <div className="banner-warn" role="status">
          <WarnIcon width={16} height={16} /> {t.degraded(r.degraded_services.join(", "))}
        </div>
      )}

      {r.response_type === "local_task" ? (
        <div className="result-card">
          <RichText text={r.answer} />
          <p className="advisory">{t.advisory}</p>
        </div>
      ) : (
        <RichText text={r.answer} onRef={showRef} />
      )}

      {r.response_type === "clarify" && r.clarify_options.length > 0 && (
        <div className="clarify">
          <p className="hint">{t.clarifyHint}</p>
          <div className="clarify-options">
            {r.clarify_options.map((o) => (
              <button key={o} type="button" className="option" disabled={busy} onClick={() => onClarify(o)}>
                {o}
              </button>
            ))}
          </div>
        </div>
      )}

      {r.response_type === "decline" && (
        <a className="btn-outline" href={staffUrl} target="_blank" rel="noopener noreferrer">
          {t.contactStaff}
          <ExternalIcon width={14} height={14} />
        </a>
      )}

      {r.sources.length > 0 && (
        <div className="sources">
          <div className="sources-head">{t.sourcesTitle(r.sources.length)}</div>
          <div className="source-grid">
            {r.sources.map((s) => {
              const body = (
                <>
                  <span className="source-top">
                    <span className="source-num">{s.ref}</span>
                    <span className={`cat cat-${s.category}`}>{t.categories[s.category]}</span>
                  </span>
                  <span className="source-title">{s.title}</span>
                  <span className="source-meta">
                    {s.page !== null && `${t.page(s.page)} · `}
                    {formatDate(s.published_at, locale)}
                  </span>
                </>
              );
              const cls = `source-card ${activeRef === s.ref ? "active" : ""}`;
              return s.url ? (
                <a key={s.ref} id={`src-${msg.id}-${s.ref}`} className={cls} href={s.url} target="_blank" rel="noopener noreferrer">
                  {body}
                </a>
              ) : (
                <div key={s.ref} id={`src-${msg.id}-${s.ref}`} className={cls}>
                  {body}
                </div>
              );
            })}
          </div>
        </div>
      )}

      <div className="actions">
        <button type="button" className="act" onClick={copy} title={copied ? t.copied : t.copy} aria-label={t.copy}>
          {copied ? <CheckIcon width={16} height={16} /> : <CopyIcon width={16} height={16} />}
        </button>
        <button
          type="button"
          className={`act ${feedback === "up" ? "on" : ""}`}
          aria-pressed={feedback === "up"}
          title={t.helpful}
          aria-label={t.helpful}
          onClick={() => onFeedback(r.message_id, "up")}
        >
          <ThumbUpIcon width={16} height={16} />
        </button>
        <button
          type="button"
          className={`act ${feedback === "down" ? "on" : ""}`}
          aria-pressed={feedback === "down"}
          title={t.notHelpful}
          aria-label={t.notHelpful}
          onClick={() => onFeedback(r.message_id, "down")}
        >
          <ThumbDownIcon width={16} height={16} />
        </button>
        {feedback && <span className="thanks">{t.thanks}</span>}
        <span className="latency">
          {r.latency_ms < 1000 ? `${r.latency_ms} ms` : `${(r.latency_ms / 1000).toFixed(2)} s`}
        </span>
      </div>
    </div>
  );
}
