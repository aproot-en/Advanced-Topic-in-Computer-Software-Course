import { NextResponse } from "next/server";
import { KB } from "@/lib/mock/kb";
import type { ApiStatus } from "@/lib/types";

export const dynamic = "force-dynamic";

// GET /api/status — shown in the header status line
export async function GET() {
  const active = KB.filter((d) => d.status === "active");
  const status: ApiStatus = {
    mode: "mock",
    documents: active.length,
    kb_updated: active.map((d) => d.published_at).sort().at(-1) ?? null,
  };
  return NextResponse.json(status);
}
