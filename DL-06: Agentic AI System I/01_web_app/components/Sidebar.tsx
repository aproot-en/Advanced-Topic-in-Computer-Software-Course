"use client";

import { formatDate, formatTime, type Dict } from "@/lib/i18n";
import type { ApiStatus, Locale, SessionSummary } from "@/lib/types";
import type { Theme } from "./ChatApp";
import { ChatIcon, CloseIcon, DatabaseIcon, MoonIcon, PlusIcon, SunIcon } from "./Icons";

interface Props {
  open: boolean;
  t: Dict;
  locale: Locale;
  status: ApiStatus | null;
  sessions: SessionSummary[];
  currentId: string | null;
  busy: boolean;
  onClose: () => void;
  onNewChat: () => void;
  onSelect: (id: string) => void;
  onLocale: (l: Locale) => void;
  theme: Theme;
  onTheme: (theme: Theme) => void;
}

export function Sidebar({
  open,
  t,
  locale,
  status,
  sessions,
  currentId,
  busy,
  onClose,
  onNewChat,
  onSelect,
  onLocale,
  theme,
  onTheme,
}: Props) {
  return (
    <>
      <div className={`sb-backdrop ${open ? "show" : ""}`} onClick={onClose} aria-hidden />
      <aside className={`sidebar ${open ? "open" : ""}`} aria-label={t.menu}>
        <div className="sb-brand">
          {/* CPE RMUTT logo (public/logo_cpe_mark.png, cropped from 01_web_app/logo_cpe.jpg) */}
          <img className="logo logo-img" src="/logo_cpe_mark.png" alt="Computer Engineering RMUTT" width={52} height={52} />
          <div className="brand-text">
            <span className="brand-name">{t.appName}</span>
          </div>
          <button type="button" className="icon-btn sb-close" onClick={onClose} aria-label={t.close}>
            <CloseIcon />
          </button>
        </div>

        <button type="button" className="btn-new" onClick={onNewChat} disabled={busy}>
          <PlusIcon width={16} height={16} />
          {t.newChat}
        </button>

        <div className="sb-section">{t.recent}</div>
        <nav className="sb-list">
          {sessions.length === 0 ? (
            <p className="sb-empty">{t.noHistory}</p>
          ) : (
            sessions.map((s) => (
              <button
                key={s.session_id}
                type="button"
                className={`sb-item ${s.session_id === currentId ? "current" : ""}`}
                onClick={() => onSelect(s.session_id)}
                disabled={busy}
              >
                <ChatIcon width={15} height={15} className="sb-item-icon" />
                <span className="sb-item-text">
                  <span className="sb-item-title">{s.title}</span>
                  <span className="sb-item-meta">{formatTime(s.updated_at, locale)}</span>
                </span>
              </button>
            ))
          )}
        </nav>

        <div className="sb-footer">
          <div className="kb-card">
            <span className="kb-icon">
              <DatabaseIcon width={16} height={16} />
            </span>
            <span className="kb-text">
              <strong>{status ? t.documents(status.documents) : t.loading}</strong>
              <span>
                {status?.kb_updated ? `${t.kbUpdated(formatDate(status.kb_updated, locale))} · ` : ""}
                {status ? t.modeLabel(status.mode) : ""}
              </span>
            </span>
            <span className={`live-dot ${status ? "ok" : ""}`} />
          </div>
          <div className="segmented" role="group" aria-label={t.language}>
            <button type="button" className={locale === "th" ? "on" : ""} onClick={() => onLocale("th")}>
              ไทย
            </button>
            <button type="button" className={locale === "en" ? "on" : ""} onClick={() => onLocale("en")}>
              English
            </button>
          </div>
          {/* Light / dark mode, under the language switch */}
          <div className="segmented" role="group" aria-label={`${t.themeLight} / ${t.themeDark}`}>
            <button type="button" className={theme === "light" ? "on" : ""} onClick={() => onTheme("light")}>
              <SunIcon width={15} height={15} />
              {t.themeLight}
            </button>
            <button type="button" className={theme === "dark" ? "on" : ""} onClick={() => onTheme("dark")}>
              <MoonIcon width={15} height={15} />
              {t.themeDark}
            </button>
          </div>
        </div>
      </aside>
    </>
  );
}
