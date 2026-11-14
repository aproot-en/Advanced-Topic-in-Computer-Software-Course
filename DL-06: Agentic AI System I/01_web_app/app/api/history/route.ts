import { NextResponse } from "next/server";
import { listSessions } from "@/lib/mock/store";

export const dynamic = "force-dynamic";

// GET /api/history — the user's sessions, newest first
export async function GET() {
  return NextResponse.json(listSessions());
}
