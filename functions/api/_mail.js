// LEADERS FILES 메일 렌더러 — subscribe.js(1편 즉시 발송)와 dispatch.js(매일 순차 발송)가 함께 쓴다.
// 다크 시네마틱 톤(차콜 + 골드)을 메일 클라이언트에서도 유지하도록 표 기반 인라인 스타일만 쓴다.

const SITE = "https://leaders.uncledison.com";
const SENDER = { name: "LEADERS FILES", email: "hello@uncledison.com" };

const C = {
  page: "#0e1013",
  card: "#15171C",
  card2: "#1A1C22",
  line: "#26282F",
  gold: "#C9A26A",
  goldSoft: "#D9B57C",
  text: "#F4F1EA",
  body: "#DEDAD2",
  mute: "#8E8A82",
  mute2: "#75726B",
};

const FONT =
  "-apple-system,BlinkMacSystemFont,'Apple SD Gothic Neo','Malgun Gothic','Helvetica Neue',Helvetica,Arial,sans-serif";
const SERIF = "'Iowan Old Style','Palatino Linotype',Palatino,Georgia,'Nanum Myeongjo',serif";

function esc(s) {
  return String(s == null ? "" : s)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

function dotDate(iso) {
  return String(iso || "").replace(/-/g, ".");
}

export function unsubscribeUrl(email, token) {
  return `${SITE}/api/unsubscribe?email=${encodeURIComponent(email)}&token=${encodeURIComponent(token)}`;
}

export function subjectFor(entry, lang) {
  const v = entry[lang] || entry.ko;
  return lang === "en"
    ? `[LEADERS FILES] No.${entry.n} · ${v.personShort} — ${v.title}`
    : `[LEADERS FILES] ${entry.n}편 · ${v.personShort} — ${v.title}`;
}

export function textFor(entry, lang, unsub) {
  const v = entry[lang] || entry.ko;
  const L =
    lang === "en"
      ? {
          issue: `No.${entry.n}`,
          read: "Read the full story",
          unsub: "Unsubscribe",
          why: "You are receiving this because you subscribed at leaders.uncledison.com.",
          tagline: "1 story a day — primary sources of failure and the morning after.",
        }
      : {
          issue: `${entry.n}편`,
          read: "전문 읽기",
          unsub: "수신거부",
          why: "leaders.uncledison.com 에서 구독 신청하셔서 이 메일을 받고 있습니다.",
          tagline: "매일 1편 · 실패와 재기의 1차 기록",
        };
  const lines = [
    "LEADERS FILES",
    L.tagline,
    "",
    `${L.issue} · ${dotDate(entry.publishDate)} · ${v.category} · ${v.minutes}`,
    v.person,
    "",
    v.title,
    "",
    v.lead,
    "",
    ...(v.highlight || []).flatMap((p) => [p, ""]),
  ];
  if (v.quote) lines.push(`"${v.quote}"`, `— ${v.quoteCaption || v.person}`, "");
  if (v.takeaway) lines.push(v.takeaway, "");
  lines.push(`${L.read}: ${v.url}`, "", L.why, `${L.unsub}: ${unsub}`, SITE);
  return lines.join("\n");
}

export function htmlFor(entry, lang, unsub) {
  const v = entry[lang] || entry.ko;
  const L =
    lang === "en"
      ? {
          issue: `No.${entry.n}`,
          read: "Read the full story",
          unsub: "Unsubscribe",
          why: "You are receiving this because you subscribed at LEADERS FILES.",
          tagline: "1 story a day &middot; primary sources of failure and the morning after",
          next:
            entry.n > 1
              ? `Today&rsquo;s letter is No.${entry.n}.`
              : "This is the first letter of your subscription.",
        }
      : {
          issue: `${entry.n}편`,
          read: "전문 읽기",
          unsub: "수신거부",
          why: "LEADERS FILES 에서 구독 신청하셔서 이 메일을 받고 있습니다.",
          tagline: "매일 1편 · 실패와 재기의 1차 기록",
          next:
            entry.n > 1
              ? `오늘의 편지는 ${entry.n}편입니다.`
              : "구독 첫 편지입니다.",
        };

  const highlight = (v.highlight || [])
    .map(
      (p) =>
        `<p style="margin:0 0 16px 0;font-family:${FONT};font-size:15px;line-height:1.85;color:${C.body};">${esc(p)}</p>`
    )
    .join("");

  const quote = v.quote
    ? `<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="margin:6px 0 24px 0;">
        <tr>
          <td style="padding:20px 22px;background:${C.card2};border-left:2px solid ${C.gold};border-radius:2px;">
            <div style="font-family:${SERIF};font-size:30px;line-height:1;color:${C.gold};opacity:.5;">&ldquo;</div>
            <div style="margin-top:6px;font-family:${SERIF};font-size:17px;line-height:1.7;color:${C.text};">${esc(v.quote)}</div>
            <div style="margin-top:12px;font-family:${FONT};font-size:12px;letter-spacing:.04em;color:${C.mute};">${esc(v.quoteCaption || v.person)}</div>
          </td>
        </tr>
      </table>`
    : "";

  const takeaway = v.takeaway
    ? `<p style="margin:0 0 22px 0;font-family:${FONT};font-size:14px;line-height:1.8;color:${C.goldSoft};">${esc(v.takeaway)}</p>`
    : "";

  return `<!DOCTYPE html>
<html lang="${lang === "en" ? "en" : "ko"}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="color-scheme" content="dark light">
<meta name="supported-color-schemes" content="dark light">
<title>${esc(subjectFor(entry, lang))}</title>
</head>
<body style="margin:0;padding:0;background:${C.page};">
<div style="display:none;max-height:0;overflow:hidden;opacity:0;">${esc(v.desc)}</div>
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="background:${C.page};padding:24px 12px;">
  <tr>
    <td align="center">
      <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="max-width:600px;width:100%;background:${C.card};border:1px solid ${C.line};border-radius:14px;overflow:hidden;">

        <tr>
          <td style="padding:26px 28px 0 28px;">
            <div style="font-family:${FONT};font-size:11px;letter-spacing:.32em;color:${C.gold};text-transform:uppercase;">LEADERS FILES</div>
            <div style="margin-top:7px;font-family:${FONT};font-size:11.5px;letter-spacing:.02em;color:${C.mute};">${L.tagline}</div>
          </td>
        </tr>

        <tr>
          <td style="padding:18px 28px 0 28px;">
            <div style="height:1px;line-height:1px;font-size:0;background:${C.gold};opacity:.45;">&nbsp;</div>
          </td>
        </tr>

        <tr>
          <td style="padding:18px 28px 0 28px;">
            <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0">
              <tr>
                <td style="font-family:${FONT};font-size:11.5px;letter-spacing:.14em;color:${C.gold};">${L.issue}</td>
                <td align="right" style="font-family:${FONT};font-size:11.5px;letter-spacing:.06em;color:${C.mute2};">
                  ${esc(dotDate(entry.publishDate))} &nbsp;·&nbsp; ${esc(v.category)} &nbsp;·&nbsp; ${esc(v.minutes)}
                </td>
              </tr>
            </table>
          </td>
        </tr>

        <tr>
          <td style="padding:10px 28px 0 28px;">
            <div style="font-family:${FONT};font-size:12px;letter-spacing:.1em;color:${C.mute};">${esc(v.person)} &nbsp;/&nbsp; ${esc(entry.eventDate)}</div>
            <h1 style="margin:10px 0 0 0;font-family:${SERIF};font-size:28px;line-height:1.35;font-weight:600;color:${C.text};letter-spacing:-.01em;">${esc(v.title)}</h1>
            <p style="margin:14px 0 0 0;font-family:${FONT};font-size:14.5px;line-height:1.8;color:${C.mute};">${esc(v.desc)}</p>
          </td>
        </tr>

        <tr>
          <td style="padding:22px 28px 0 28px;">
            <p style="margin:0 0 18px 0;font-family:${FONT};font-size:15.5px;line-height:1.85;color:${C.text};">${esc(v.lead)}</p>
            ${highlight}
          </td>
        </tr>

        <tr><td style="padding:0 28px;">${quote}</td></tr>

        <tr>
          <td style="padding:0 28px 4px 28px;">
            ${takeaway}
            <table role="presentation" cellpadding="0" cellspacing="0" border="0">
              <tr>
                <td style="border-radius:8px;background:${C.gold};">
                  <a href="${esc(v.url)}" style="display:inline-block;padding:13px 26px;font-family:${FONT};font-size:14px;font-weight:600;letter-spacing:.02em;color:#16130B;text-decoration:none;">${L.read} &rarr;</a>
                </td>
              </tr>
            </table>
            <div style="margin-top:12px;font-family:${FONT};font-size:11.5px;line-height:1.7;color:${C.mute2};word-break:break-all;">${esc(v.url)}</div>
          </td>
        </tr>

        <tr>
          <td style="padding:26px 28px 0 28px;">
            <div style="height:1px;line-height:1px;font-size:0;background:${C.line};">&nbsp;</div>
          </td>
        </tr>

        <tr>
          <td style="padding:18px 28px 26px 28px;">
            <p style="margin:0 0 10px 0;font-family:${FONT};font-size:11.5px;line-height:1.8;color:${C.mute2};">${L.next} ${L.why}</p>
            <p style="margin:0;font-family:${FONT};font-size:11.5px;line-height:1.8;color:${C.mute2};">
              <a href="${esc(v.home)}" style="color:${C.gold};text-decoration:none;">LEADERS FILES</a>
              &nbsp;·&nbsp;
              <a href="${esc(unsub)}" style="color:${C.mute};text-decoration:underline;">${L.unsub}</a>
            </p>
            <p style="margin:10px 0 0 0;font-family:${FONT};font-size:10.5px;line-height:1.7;color:${C.mute2};opacity:.8;">
              ${lang === "en" ? "LEADERS FILES Editorial Desk · Primary sources, dates and numbers." : "LEADERS FILES 편집부 · 1차 사료와 날짜, 숫자로 기록합니다."}
            </p>
          </td>
        </tr>

      </table>
    </td>
  </tr>
</table>
</body>
</html>`;
}

// Brevo 트랜잭션 메일 1통 발송. 성공하면 { ok:true, messageId } 를 돌려준다.
export async function sendBrevo(env, { to, subject, html, text, unsubUrl, tag }) {
  if (!env.BREVO_API_KEY) return { ok: false, error: "brevo_api_key_missing" };

  const headers = { "content-type": "application/json", accept: "application/json" };
  headers["api-key"] = env.BREVO_API_KEY;

  const body = {
    sender: SENDER,
    to: [{ email: to }],
    subject,
    htmlContent: html,
    textContent: text,
    tags: [tag || "leadersfiles-daily"],
  };
  if (unsubUrl) {
    body.headers = {
      "List-Unsubscribe": `<${unsubUrl}>`,
      "List-Unsubscribe-Post": "List-Unsubscribe=One-Click",
    };
  }

  let res, data;
  try {
    res = await fetch("https://api.brevo.com/v3/smtp/email", {
      method: "POST",
      headers,
      body: JSON.stringify(body),
    });
    data = await res.json().catch(() => ({}));
  } catch (err) {
    return { ok: false, error: `network:${String(err && err.message ? err.message : err)}` };
  }

  if (!res.ok) {
    return {
      ok: false,
      error: `brevo_${res.status}`,
      detail: String((data && (data.message || data.code)) || "").slice(0, 200),
    };
  }
  return { ok: true, messageId: data && data.messageId ? data.messageId : null };
}

export { SITE, SENDER };
