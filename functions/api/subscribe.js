// POST /api/subscribe  { email, consent, source }
// 구독자 KV 저장 + Brevo 로 1편(에디슨 1914, 해당 언어) 즉시 발송.
import { STORIES } from "./_stories.js";
import { htmlFor, subjectFor, textFor, unsubscribeUrl, sendBrevo } from "./_mail.js";

const EMAIL_RE = /^[^\s@]+@[^\s@]+\.[a-z]{2,}$/i;

function json(data, status = 200) {
  return new Response(JSON.stringify(data), {
    status,
    headers: {
      "Content-Type": "application/json; charset=utf-8",
      "Cache-Control": "no-store",
    },
  });
}

export function todayKST() {
  const now = new Date(Date.now() + 9 * 3600 * 1000);
  return now.toISOString().slice(0, 10);
}

export function makeToken() {
  const bytes = new Uint8Array(18);
  crypto.getRandomValues(bytes);
  return Array.from(bytes, (b) => b.toString(16).padStart(2, "0")).join("");
}

export async function onRequestPost(context) {
  const { request, env } = context;
  if (!env.SUBSCRIBERS_KV) {
    return json({ ok: false, error: "kv_not_bound" }, 503);
  }

  let body;
  try {
    body = await request.json();
  } catch {
    return json({ ok: false, error: "invalid_json" }, 400);
  }

  const email = String(body?.email || "").trim().toLowerCase();
  const consent = Boolean(body?.consent);
  const source = String(body?.source || "/").slice(0, 120);
  let lang = String(body?.lang || "").toLowerCase();
  if (lang !== "ko" && lang !== "en") lang = source.startsWith("/en") ? "en" : "ko";

  if (!EMAIL_RE.test(email) || email.length > 254) {
    return json({ ok: false, error: "invalid_email" }, 400);
  }
  if (!consent) {
    return json({ ok: false, error: "consent_required" }, 400);
  }

  const key = `sub:${email}`;
  const existing = await env.SUBSCRIBERS_KV.get(key, "json");
  const now = new Date().toISOString();
  const today = todayKST();

  // 이미 구독 중이면 중복 발송하지 않는다.
  if (existing && !existing.unsubscribed) {
    return json(
      {
        ok: true,
        alreadySubscribed: true,
        language: existing.lang || lang,
        nextIndex: existing.nextIndex || 1,
        sent: false,
      },
      200
    );
  }

  const token = (existing && existing.unsubscribeToken) || makeToken();
  const record = {
    email,
    lang,
    source,
    consent: true,
    subscribedAt: existing?.subscribedAt || now,
    updatedAt: now,
    active: true,
    unsubscribed: false,
    unsubscribedAt: null,
    nextIndex: 1,
    lastSentDate: null,
    lastMessageId: null,
    unsubscribeToken: token,
  };

  await env.SUBSCRIBERS_KV.put(key, JSON.stringify(record));

  // 1편 즉시 발송 (BREVO_API_KEY 가 없으면 저장만 하고 다음 날부터 순차 발송).
  const first = STORIES[0];
  if (!first || !env.BREVO_API_KEY) {
    return json(
      {
        ok: true,
        alreadySubscribed: false,
        resubscribed: Boolean(existing),
        sent: false,
        sentFirstIssue: false,
        reason: first ? "mailer_not_configured" : "no_published_story",
        language: lang,
      },
      200
    );
  }

  const unsub = unsubscribeUrl(email, token);
  const sent = await sendBrevo(env, {
    to: email,
    subject: subjectFor(first, lang),
    html: htmlFor(first, lang, unsub),
    text: textFor(first, lang, unsub),
    unsubUrl: unsub,
    tag: "leadersfiles-welcome",
  });

  if (sent.ok) {
    record.nextIndex = first.n + 1;
    record.lastSentDate = today;
    record.lastMessageId = sent.messageId || null;
    record.updatedAt = new Date().toISOString();
    await env.SUBSCRIBERS_KV.put(key, JSON.stringify(record));
    return json(
      {
        ok: true,
        alreadySubscribed: false,
        resubscribed: Boolean(existing),
        sent: true,
        sentFirstIssue: true,
        issue: first.n,
        slug: first.slug,
        language: lang,
        messageId: sent.messageId || null,
      },
      200
    );
  }

  // 구독 저장은 성공, 첫 편 발송만 실패 → 다음 순차 발송에서 1편부터 나간다.
  return json(
    {
      ok: true,
      alreadySubscribed: false,
      resubscribed: Boolean(existing),
      sent: false,
      sentFirstIssue: false,
      error: sent.error || "send_failed",
      detail: sent.detail || null,
      language: lang,
      nextIndex: 1,
    },
    200
  );
}
