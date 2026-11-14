import { NextResponse } from "next/server";
import { addFeedback, messageExists } from "@/lib/mock/store";

export const dynamic = "force-dynamic";

// POST /api/feedback — { message_id, rating: "up" | "down", comment? }
export async function POST(req: Request) {
  const body = (await req.json().catch(() => null)) as Record<string, unknown> | null;
  const messageId = typeof body?.message_id === "string" ? body.message_id : "";
  const rating = body?.rating;
  const comment = typeof body?.comment === "string" ? body.comment.slice(0, 500) : undefined;

  if (!messageId || (rating !== "up" && rating !== "down")) {
    return NextResponse.json({ error: "message_id and rating (up|down) are required" }, { status: 400 });
  }
  if (!messageExists(messageId)) {
    return NextResponse.json({ error: "message not found" }, { status: 404 });
  }
  addFeedback({ message_id: messageId, rating, comment });
  return NextResponse.json({ ok: true });
}
