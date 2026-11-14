import { NextResponse } from "next/server";
import { handleChat } from "@/lib/mock/engine";
import { parseChatRequest } from "@/lib/mock/validate";

export const dynamic = "force-dynamic";

// POST /api/chat — single JSON response (Unified Response Schema)
export async function POST(req: Request) {
  const parsed = parseChatRequest(await req.json().catch(() => null));
  if ("error" in parsed) return NextResponse.json({ error: parsed.error }, { status: 400 });
  return NextResponse.json(handleChat(parsed.value));
}
