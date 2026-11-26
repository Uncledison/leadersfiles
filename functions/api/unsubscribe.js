// GET|POST /api/unsubscribe?email=...&token=...
// 토큰이 맞으면 구독을 해제(unsubscribed=true)하고 안내 HTML 페이지를 돌려준다.
// 메일 하단 링크와 List-Unsubscribe(one-click) POST 가 같은 경로를 쓴다.

const C = {
  page: "#0e1013",
  card: "#15171C",
  line: "#26282F",
  gold: "#C9A26A",
  text: "#F4F1EA",
  body: "#DEDAD2",
  mute: "#8E8A82",
};
const FONT =
  "-apple-system,BlinkMacSystemFont,'Apple SD Gothic Neo','Malgun Gothic','Helvetica Neue',Helvetica,Arial,sans-serif";
const SERIF = "'Iowan Old Style','Palatino Linotype',Palatino,Georgia,'Nanum Myeongjo',serif";

function page(lang, title, message, status) {
  const en = lang === "en";
  const html = `<!DOCTYPE html>
<html lang="${en ? "en" : "ko"}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>${title} · LEADERS FILES</title>
<style>
  :root{color-scheme:dark}
  *{box-sizing:border-box}
  body{margin:0;min-height:100vh;display:flex;align-items:center;justify-content:center;padding:32px 20px;
       background:${C.page};color:${C.body};font-family:${FONT};-webkit-font-smoothing:antialiased}
  .card{width:100%;max-width:520px;background:${C.card};border:1px solid ${C.line};border-radius:16px;padding:34px 30px}
  .brand{font-size:11px;letter-spacing:.32em;text-transform:uppercase;color:${C.gold}}
  .rule{height:1px;background:${C.gold};opacity:.45;margin:18px 0 24px}
  h1{font-family:${SERIF};font-size:24px;line-height:1.4;font-weight:600;color:${C.text};margin:0 0 14px}
  p{font-size:14.5px;line-height:1.85;color:${C.mute};margin:0 0 22px}
  a.btn{display:inline-block;padding:13px 24px;border-radius:9px;background:${C.gold};color:#16130B;
        font-size:14px;font-weight:600;text-decoration:none}
  .fine{margin-top:22px;font-size:11px;line-height:1.7;color:#5E5B56}
</style>
</head>
<body>
  <main class="card">
    <div class="brand">LEADERS FILES</div>
    <div class="rule"></div>
    <h1>${title}</h1>
    <p>${message}</p>
    <a class="btn" href="${en ? "https://leaders.uncledison.com/en/" : "https://leaders.uncledison.com/"}"
       style="color:#16130B">${en ? "Back to the archive" : "아카이브로 돌아가기"}</a>
    <div class="fine">${en ? "LEADERS FILES Editorial Desk · leaders.uncledison.com" : "LEADERS FILES 편집부 · leaders.uncledison.com"}</div>
  </main>
</body>
</html>`;
  return new Response(html, {
    status,
    headers: {
      "Content-Type": "text/html; charset=utf-8",
      "Cache-Control": "no-store",
    },
  });
}

const TEXT = {
  ko: {
    done_title: "구독을 해지했습니다",
    done_msg: "이 주소로는 다시 편지를 보내지 않습니다. 언제든 사이트에서 다시 구독하실 수 있습니다.",
    gone_title: "이미 해지된 주소입니다",
    gone_msg: "이 이메일 주소는 구독 목록에 없습니다. 이미 해지되었거나 처음부터 등록된 적이 없습니다.",
    bad_title: "링크가 올바르지 않습니다",
    bad_msg: "수신거부 링크의 주소나 토큰이 맞지 않습니다. 메일에 있는 링크를 그대로 눌러 주세요.",
    missing_title: "링크가 올바르지 않습니다",
    missing_msg: "메일에 있는 수신거부 링크 전체를 눌러 주세요. 주소나 토큰이 빠져 있습니다.",
    kv_title: "잠시 후 다시 시도해 주세요",
    kv_msg: "구독 목록에 일시적으로 접근할 수 없습니다.",
  },
  en: {
    done_title: "You have been unsubscribed",
    done_msg: "We will not send any more letters to this address. You can subscribe again on the site at any time.",
    gone_title: "Already unsubscribed",
    gone_msg: "This address is not on the list. It was already removed, or it was never subscribed.",
    bad_title: "This link is not valid",
    bad_msg: "The address or token in this unsubscribe link does not match. Please use the link from the email exactly as it is.",
    missing_title: "This link is not valid",
    missing_msg: "Please open the full unsubscribe link from the email. The address or token is missing.",
    kv_title: "Please try again shortly",
    kv_msg: "The subscription list cannot be reached right now.",
  },
};

async function handle(request, env) {
  const url = new URL(request.url);
  const email = String(url.searchParams.get("email") || "").trim().toLowerCase();
  const token = String(url.searchParams.get("token") || "").trim();

  if (!email && !token) {
    const t = TEXT.ko;
    return page("ko", t.missing_title, t.missing_msg, 400);
  }

  if (!env.SUBSCRIBERS_KV) {
    const t = TEXT.ko;
    return page("ko", t.kv_title, t.kv_msg, 503);
  }

  const key = `sub:${email}`;
  const record = await env.SUBSCRIBERS_KV.get(key, "json");
  const lang = record?.lang === "en" ? "en" : "ko";
  const t = TEXT[lang];

  if (!record) {
    return page(lang, t.gone_title, t.gone_msg, 200);
  }
  if (!token || token !== record.unsubscribeToken) {
    return page(lang, t.bad_title, t.bad_msg, 403);
  }

  if (record.unsubscribed) {
    return page(lang, t.gone_title, t.gone_msg, 200);
  }

  record.unsubscribed = true;
  record.active = false;
  record.unsubscribedAt = new Date().toISOString();
  record.updatedAt = record.unsubscribedAt;
  await env.SUBSCRIBERS_KV.put(key, JSON.stringify(record));

  return page(lang, t.done_title, t.done_msg, 200);
}

export async function onRequestGet(context) {
  return handle(context.request, context.env);
}

export async function onRequestPost(context) {
  return handle(context.request, context.env);
}
