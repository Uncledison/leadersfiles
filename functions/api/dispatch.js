// GET|POST /api/dispatch   Authorization: Bearer <DISPATCH_SECRET>
// 매일 1편 순차 발송. KV 구독자를 훑어 오늘 아직 받지 못한 사람에게 다음 편을 Brevo 로 보낸다.
import { STORIES } from "./_stories.js";
import { htmlFor, subjectFor, textFor, unsubscribeUrl, sendBrevo } from "./_mail.js";

const DAILY_FREE_LIMIT = 300; // Brevo 무료 하루 300통
const MAX_PER_RUN = 280; // 한 번 실행에서 남겨둘 여유분 포함 상한
const TIME_BUDGET_MS = 25000; // 요청 한 번이 너무 길어지지 않게
const DELAY_MS = 60; // 연속 호출 사이 간격

function json(data, status = 200) {
  return new Response(JSON.stringify(data, null, 1), {
    status,
    headers: { "Content-Type": "application/json; charset=utf-8", "Cache-Control": "no-store" },
  });
}

function todayKST() {
  return todayFrom(new Date());
}

function todayFrom(d) {
  return new Date(d.getTime() + 9 * 3600 * 1000).toISOString().slice(0, 10);
}

const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

async function listAll(kv) {
  const keys = [];
  let cursor;
  for (let i = 0; i < 50; i++) {
    const res = await kv.list({ prefix: "sub:", cursor });
    for (const k of res.keys) keys.push(k.name);
    if (res.list_complete) break;
    cursor = res.cursor;
    if (!cursor) break;
  }
  return keys;
}

async function handle(context) {
  const { request, env } = context;
  const started = Date.now();
  const today = todayKST();

  const expected = env.DISPATCH_SECRET ? `Bearer ${env.DISPATCH_SECRET}` : "";
  const given = (request.headers.get("Authorization") || "").trim();
  if (!expected || given !== expected) {
    return json({ ok: false, error: "unauthorized" }, 401);
  }
  if (!env.SUBSCRIBERS_KV) return json({ ok: false, error: "kv_not_bound" }, 503);
  if (!env.BREVO_API_KEY) return json({ ok: false, error: "brevo_api_key_missing" }, 503);

  const totalStories = STORIES.length;
  if (totalStories === 0) return json({ ok: true, today, sent: 0, note: "no_published_story" });

  // 오늘 이미 나간 통수(무료 한도 안전장치)
  const quotaKey = `stats:sent:${today}`;
  const usedToday = Number((await env.SUBSCRIBERS_KV.get(quotaKey)) || 0) || 0;
  const quotaLeft = Math.max(0, DAILY_FREE_LIMIT - usedToday);
  const cap = Math.min(MAX_PER_RUN, quotaLeft);

  const report = {
    ok: true,
    today,
    published: totalStories,
    latestIssue: totalStories,
    subscribers: 0,
    sent: 0,
    alreadySentToday: 0,
    finishedAllIssues: 0,
    inactive: 0,
    errors: [],
    usedTodayBefore: usedToday,
    quotaLeftBefore: quotaLeft,
    cap,
    capped: false,
    stopped: null,
    elapsedMs: 0,
  };

  if (cap <= 0) {
    report.capped = true;
    report.stopped = "daily_quota_reached";
    report.elapsedMs = Date.now() - started;
    return json(report);
  }

  const keys = await listAll(env.SUBSCRIBERS_KV);
  report.subscribers = keys.length;
  let sentThisRun = 0;

  for (const key of keys) {
    if (sentThisRun >= cap) {
      report.capped = true;
      report.stopped = "run_cap_reached";
      break;
    }
    if (Date.now() - started > TIME_BUDGET_MS) {
      report.stopped = "time_budget_reached";
      break;
    }

    let rec;
    try {
      rec = await env.SUBSCRIBERS_KV.get(key, "json");
    } catch {
      continue;
    }
    if (!rec || !rec.email) continue;
    if (rec.unsubscribed || rec.active === false) {
      report.inactive++;
      continue;
    }
    if (rec.lastSentDate === today) {
      report.alreadySentToday++;
      continue;
    }

    const idx = Number(rec.nextIndex) || 1;
    if (idx > totalStories) {
      report.finishedAllIssues++;
      continue;
    }

    const entry = STORIES[idx - 1];
    const lang = rec.lang === "en" ? "en" : "ko";
    const token = rec.unsubscribeToken || "";
    const unsub = unsubscribeUrl(rec.email, token);

    const res = await sendBrevo(env, {
      to: rec.email,
      subject: subjectFor(entry, lang),
      html: htmlFor(entry, lang, unsub),
      text: textFor(entry, lang, unsub),
      unsubUrl: unsub,
      tag: "leadersfiles-daily",
    });

    if (res.ok) {
      rec.nextIndex = idx + 1;
      rec.lastSentDate = today;
      rec.lastMessageId = res.messageId || null;
      rec.updatedAt = new Date().toISOString();
      await env.SUBSCRIBERS_KV.put(key, JSON.stringify(rec));
      sentThisRun++;
      report.sent++;
    } else {
      if (report.errors.length < 25) {
        report.errors.push({ email: rec.email, issue: idx, error: res.error, detail: res.detail || null });
      }
      // Brevo 쪽 한도/키 문제라면 더 돌지 않는다.
      if (String(res.error || "").startsWith("brevo_4")) {
        report.stopped = "brevo_auth_or_quota_error";
        break;
      }
    }

    if (DELAY_MS) await sleep(DELAY_MS);
  }

  if (sentThisRun > 0) {
    await env.SUBSCRIBERS_KV.put(quotaKey, String(usedToday + sentThisRun), {
      expirationTtl: 60 * 60 * 24 * 7,
    });
  }

  report.usedTodayAfter = usedToday + sentThisRun;
  report.quotaLeftAfter = Math.max(0, DAILY_FREE_LIMIT - report.usedTodayAfter);
  report.elapsedMs = Date.now() - started;
  return json(report);
}

export async function onRequestGet(context) {
  return handle(context);
}

export async function onRequestPost(context) {
  return handle(context);
}
