import { NextResponse } from "next/server";
import { getSession } from "@/lib/mock/store";

export const dynamic = "force-dynamic";

// GET /api/sessions/{id} — all messages in one session
export async function GET(_req: Request, { params }: { params: { id: string } }) {
  const session = getSession(params.id);
  if (!session) return NextResponse.json({ error: "session not found" }, { status: 404 });
  return NextResponse.json(session);
}
