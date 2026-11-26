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
  const lang = source.startsWith("/en") ? "en" : "ko";

  if (!EMAIL_RE.test(email)) {
    return json({ ok: false, error: "invalid_email" }, 400);
  }
  if (!consent) {
    return json({ ok: false, error: "consent_required" }, 400);
  }

  const key = `sub:${email}`;
  const existing = await env.SUBSCRIBERS_KV.get(key, "json");
  const now = new Date().toISOString();

  const record = {
    email,
    lang,
    source,
    consent: true,
    subscribedAt: existing?.subscribedAt || now,
    updatedAt: now,
    active: true,
  };

  await env.SUBSCRIBERS_KV.put(key, JSON.stringify(record));

  if (env.RESEND_API_KEY && !existing) {
    const from = env.MAIL_FROM || "LEADERS FILES <onboarding@resend.dev>";
    const subject =
      lang === "en"
        ? "Subscribed to LEADERS FILES"
        : "[LEADERS FILES] 구독 신청이 완료되었습니다";
    const text =
      lang === "en"
        ? "Thank you for subscribing to LEADERS FILES (https://leaders.uncledison.com/en/). We will share primary-source stories of resilience and leadership."
        : "LEADERS FILES (https://leaders.uncledison.com) 구독 신청이 완료되었습니다. 매일 1차 사료 기반의 위대한 리더들의 이야기를 전해드리겠습니다.";

    await fetch("https://api.resend.com/emails", {
      method: "POST",
      headers: {
        Authorization: `Bearer ${env.RESEND_API_KEY}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ from, to: [email], subject, text }),
    }).catch(() => {});
  }

  return json({ ok: true, alreadySubscribed: Boolean(existing) }, 200);
}
