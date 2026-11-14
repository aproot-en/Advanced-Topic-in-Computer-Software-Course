// Safe renderer for the small markdown subset the assistant returns:
// paragraphs, "- " / "1. " lists, **bold** and reference markers [n].
// It only creates React elements (never raw HTML), so AI output cannot inject markup.

import type { ReactNode } from "react";

type Block =
  | { type: "p"; text: string }
  | { type: "ul" | "ol"; items: string[] };

function parseBlocks(text: string): Block[] {
  const blocks: Block[] = [];
  let para: string[] = [];
  const flush = () => {
    if (para.length) blocks.push({ type: "p", text: para.join(" ") });
    para = [];
  };

  for (const line of text.split("\n")) {
    const t = line.trim();
    const ul = /^[-*]\s+(.*)$/.exec(t);
    const ol = /^\d+[.)]\s+(.*)$/.exec(t);
    if (ul || ol) {
      flush();
      const type = ul ? "ul" : "ol";
      const item = (ul ?? ol)![1];
      const last = blocks[blocks.length - 1];
      if (last && last.type === type) last.items.push(item);
      else blocks.push({ type, items: [item] });
    } else if (!t) {
      flush();
    } else {
      para.push(t);
    }
  }
  flush();
  return blocks;
}

function inline(text: string, onRef?: (n: number) => void): ReactNode[] {
  return text.split(/(\*\*[^*]+\*\*|\[\d+\])/g).map((part, i) => {
    if (!part) return null;
    const bold = /^\*\*([^*]+)\*\*$/.exec(part);
    if (bold) return <strong key={i}>{bold[1]}</strong>;
    const ref = /^\[(\d+)\]$/.exec(part);
    if (ref) {
      const n = Number(ref[1]);
      return (
        <button key={i} type="button" className="ref-chip" onClick={() => onRef?.(n)} aria-label={`[${n}]`}>
          {n}
        </button>
      );
    }
    return part;
  });
}

export function RichText({ text, onRef }: { text: string; onRef?: (n: number) => void }) {
  return (
    <div className="rich">
      {parseBlocks(text).map((b, i) => {
        if (b.type === "p") return <p key={i}>{inline(b.text, onRef)}</p>;
        const items = b.items.map((it, j) => <li key={j}>{inline(it, onRef)}</li>);
        return b.type === "ul" ? <ul key={i}>{items}</ul> : <ol key={i}>{items}</ol>;
      })}
    </div>
  );
}
