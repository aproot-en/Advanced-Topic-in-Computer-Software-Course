import { NextResponse } from "next/server";
import { handleChat } from "@/lib/mock/engine";
import { parseChatRequest } from "@/lib/mock/validate";

export const dynamic = "force-dynamic";

const CHUNK_CHARS = 4;
const CHUNK_DELAY_MS = 15;

// POST /api/chat/stream — Server-Sent Events:
//   event: delta  data: {"text": "..."}         (answer text, token by token)
//   event: done   data: <Unified Response>       (final object, replaces the streamed text)
export async function POST(req: Request) {
  const parsed = parseChatRequest(await req.json().catch(() => null));
  if ("error" in parsed) return NextResponse.json({ error: parsed.error }, { status: 400 });

  const response = handleChat(parsed.value);
  const encoder = new TextEncoder();
  const send = (event: string, data: unknown) =>
    encoder.encode(`event: ${event}\ndata: ${JSON.stringify(data)}\n\n`);

  const stream = new ReadableStream({
    async start(controller) {
      const chars = Array.from(response.answer);
      for (let i = 0; i < chars.length; i += CHUNK_CHARS) {
        if (req.signal.aborted) break;
        controller.enqueue(send("delta", { text: chars.slice(i, i + CHUNK_CHARS).join("") }));
        await new Promise((r) => setTimeout(r, CHUNK_DELAY_MS));
      }
      controller.enqueue(send("done", response));
      controller.close();
    },
  });

  return new Response(stream, {
    headers: {
      "Content-Type": "text/event-stream; charset=utf-8",
      "Cache-Control": "no-cache, no-transform",
      Connection: "keep-alive",
    },
  });
}
