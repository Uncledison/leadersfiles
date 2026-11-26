// GET /api/preview?n=1&lang=ko — 메일 HTML 미리보기(공개된 편만, 개인정보 없음).
// 디자인 확인용. 실제 발송은 subscribe.js / dispatch.js 가 한다.
import { STORIES } from "./_stories.js";
import { htmlFor } from "./_mail.js";

export async function onRequestGet(context) {
  const url = new URL(context.request.url);
  const raw = Number(url.searchParams.get("n") || 1);
  const n = Math.max(1, Math.min(STORIES.length || 1, Number.isFinite(raw) ? Math.floor(raw) : 1));
  const lang = url.searchParams.get("lang") === "en" ? "en" : "ko";
  const entry = STORIES[n - 1];
  if (!entry) {
    return new Response("no published story", { status: 404, headers: { "content-type": "text/plain" } });
  }
  const unsub = "https://leaders.uncledison.com/api/unsubscribe?email=preview%40example.com&token=preview";
  return new Response(htmlFor(entry, lang, unsub), {
    headers: {
      "content-type": "text/html; charset=utf-8",
      "cache-control": "no-store",
      "x-robots-tag": "noindex",
    },
  });
}
