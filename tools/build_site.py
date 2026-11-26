#!/usr/bin/env python3
"""LEADERS FILES 정적 빌더.

data/*.py 의 스토리 원고(사료 기반)에서 다음을 생성한다.

    python3 tools/build_site.py                    # KST 오늘 이전(publish_date <= 오늘) 원고만 발행
    python3 tools/build_site.py --today=2026-12-05 # 특정 날짜 기준 (검증용)
    python3 tools/build_site.py --check-numbers    # 한글 수사(개수·나이 등) 전수 검사만

생성물: stories/<slug>.html, index.html, leaders/index.html, sitemap.xml
미래 publish_date 의 스토리는 HTML을 만들지 않고, 이미 있던 파일은 지운다.
"""
import datetime
import html
import importlib.util
import json
import os
import re
import sys

try:
    from zoneinfo import ZoneInfo
except ImportError:  # pragma: no cover
    ZoneInfo = None

TOOLS = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(TOOLS)
DATA = os.path.join(ROOT, "data")
SITE = "https://leaders.uncledison.com"
STORY_TPL = open(os.path.join(TOOLS, "story_template.html"), encoding="utf-8").read()
INDEX_TPL = open(os.path.join(TOOLS, "index_template.html"), encoding="utf-8").read()
LEADERS_TPL = open(os.path.join(TOOLS, "leaders_template.html"), encoding="utf-8").read()

# 영문판(/en/) 템플릿. 같은 디자인 시스템을 쓰고 상대 경로만 깊이에 맞춰 둔다.
EN_ROOT = os.path.join(ROOT, "en")
EN_STORY_TPL = open(os.path.join(TOOLS, "en_story_template.html"), encoding="utf-8").read()
EN_INDEX_TPL = open(os.path.join(TOOLS, "en_index_template.html"), encoding="utf-8").read()
EN_LEADERS_TPL = open(os.path.join(TOOLS, "en_leaders_template.html"), encoding="utf-8").read()

CAT_NAME = {"sci": "과학·발명", "biz": "창업·도전", "lead": "리더·역경"}
CAT_NAME_EN = {"sci": "Science & Invention", "biz": "Enterprise & Endeavour", "lead": "Leadership & Adversity"}
DRAWER_LIMIT = 6

# 영문판에서 반드시 새로 써야 하는(한국어를 그대로 쓰면 안 되는) 필드.
EN_FIELDS = (
    "alt_name", "person", "person_short", "title", "title_html", "eyebrow", "desc", "card_desc",
    "minutes", "alt", "tl_head", "lead_html", "article_html", "quote_text_html", "quote_caption",
    "takeaway_line_html", "takeaway_sub", "share_title", "share_text", "sources_html", "fine",
    "filebox_title", "filebox", "timeline",
)


# ---------------------------------------------------------------- dates / loading
def today_kst():
    if ZoneInfo is not None:
        return datetime.datetime.now(ZoneInfo("Asia/Seoul")).date().isoformat()
    return (datetime.datetime.utcnow() + datetime.timedelta(hours=9)).date().isoformat()


def load_module(path):
    name = "rf_" + os.path.basename(path)[:-3]
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def load_stories():
    stories = []
    for fn in sorted(os.listdir(DATA)):
        if not (fn.startswith("s") and fn.endswith(".py")):
            continue
        mod = load_module(os.path.join(DATA, fn))
        st = getattr(mod, "STORY")
        st["_source"] = fn
        st["_en"] = getattr(mod, "STORY_EN", None)
        if st["_en"] is None:
            raise SystemExit("data/%s 에 STORY_EN(영문 원고)이 없습니다" % fn)
        for key in EN_FIELDS:
            if key not in st["_en"]:
                raise SystemExit("data/%s 의 STORY_EN 에 %r 필드가 없습니다" % (fn, key))
        for key in ("desc", "card_desc"):
            if key in st:
                st[key] = html.unescape(st[key])
        stories.append(st)
    for st in stories:
        for key in ("slug", "publish_date", "person", "person_short", "title", "title_html",
                    "desc", "card_desc", "category", "img", "alt", "years", "minutes",
                    "sources_count", "lead_html", "article_html", "quote_text_html",
                    "quote_en", "quote_caption", "takeaway_line_html", "takeaway_sub",
                    "share_title", "share_text", "sources_html", "fine", "timeline",
                    "lineup_name", "event_date", "birth", "death", "now_label", "eyebrow"):
            if key not in st:
                raise SystemExit("data/%s 에 %r 필드가 없습니다" % (st["_source"], key))
    stories.sort(key=lambda s: (s["publish_date"], s["slug"]))
    return stories


def load_lineup():
    mod = load_module(os.path.join(DATA, "lineup.py"))
    return mod.LINEUP


def load_lineup_en():
    mod = load_module(os.path.join(DATA, "lineup.py"))
    return mod.LEADERS_EN


def en_view(st):
    """한국어 STORY에 영문 필드를 덮어써 영문판 뷰를 만든다. 구조 필드(slug·발행일·이미지)는 공유한다."""
    view = {k: v for k, v in st.items() if k not in ("_en",)}
    view.update(st["_en"])
    view["_source"] = st["_source"]
    if not view.get("quote_en"):
        view["quote_en"] = ""
    return view


# ---------------------------------------------------------------- language switch
def lang_toggle(kr_href, en_href, current, label="Language"):
    def item(href, lang, text, cur):
        return ('<a class="lang-a%s" href="%s" lang="%s" hreflang="%s"%s>%s</a>'
                % (" current" if cur else "", href, lang, lang,
                   ' aria-current="page"' if cur else "", text))
    return ('<div class="lang" role="group" aria-label="%s">\n        %s\n'
            '        <span class="lang-sep" aria-hidden="true">|</span>\n        %s\n      </div>'
            % (label, item(kr_href, "ko", "KR", current == "ko"),
               item(en_href, "en", "EN", current == "en")))


def hreflang(ko_path, en_path):
    """ko / en / x-default 대응 URL. ko_path·en_path 는 도메인 뒤 경로."""
    return ('<link rel="alternate" hreflang="ko" href="%s%s">\n'
            '<link rel="alternate" hreflang="en" href="%s%s">\n'
            '<link rel="alternate" hreflang="x-default" href="%s%s">'
            % (SITE, ko_path, SITE, en_path, SITE, ko_path))


def dot(iso):
    return iso.replace("-", ".")


def e(s):
    return html.escape(s, quote=True)


# ---------------------------------------------------------------- fragments
def drawer_items(stories, prefix=""):
    out = []
    for s in list(reversed(stories))[:DRAWER_LIMIT]:
        year = s["now_label"].split("·")[-1].strip() if "·" in s["now_label"] else ""
        label = "%s · %s" % (s["person_short"], year) if year else s["person_short"]
        out.append(
            '<a class="dr-item" href="%sstories/%s.html" data-close>\n'
            '      <svg width="18" height="18" viewBox="0 0 18 18" fill="none" aria-hidden="true"><path d="M4 2.5h10v13l-5-3.2-5 3.2z" stroke="currentColor" stroke-width="1.1" stroke-linejoin="round"/></svg>\n'
            '      <span>%s<small>%s</small></span>\n'
            '    </a>' % (prefix, s["slug"], e(label), e(s["title"]))
        )
    return "\n    ".join(out)


def ldjson(st):
    article = {
        "@context": "https://schema.org",
        "@graph": [
            {
                "@type": "Article",
                "headline": st["title"],
                "description": st["desc"],
                "image": "%s/assets/img/og-%s.jpg" % (SITE, st["img"]),
                "datePublished": st["publish_date"] + "T08:00:00+09:00",
                "dateModified": st["publish_date"] + "T08:00:00+09:00",
                "inLanguage": "ko-KR",
                "articleSection": CAT_NAME[st["category"]],
                "author": {"@type": "Organization", "name": "LEADERS FILES 편집부"},
                "publisher": {"@type": "Organization", "name": "LEADERS FILES", "url": SITE + "/"},
                "mainEntityOfPage": {"@type": "WebPage", "@id": "%s/stories/%s.html" % (SITE, st["slug"])},
                "about": {"@type": "Person", "name": st["person"],
                          "birthDate": st["birth"], "deathDate": st["death"]},
            },
            {
                "@type": "BreadcrumbList",
                "itemListElement": [
                    {"@type": "ListItem", "position": 1, "name": "아카이브", "item": SITE + "/"},
                    {"@type": "ListItem", "position": 2, "name": "%s · %s" % (st["person_short"], st["now_label"].split("·")[-1].strip()),
                     "item": "%s/stories/%s.html" % (SITE, st["slug"])},
                ],
            },
        ],
    }
    return json.dumps(article, ensure_ascii=False)


def next_html(stories, st, published):
    if len(published) < 2:
        return ""
    idx = [s["slug"] for s in published].index(st["slug"])
    nxt = published[(idx + 1) % len(published)]
    return (
        '<a class="next" href="../stories/%s.html">\n'
        '    <div class="thumb"><img src="../assets/img/%s-thumb.webp" width="360" height="440" alt="%s 에디토리얼 초상(AI 생성)" loading="lazy" decoding="async"></div>\n'
        '    <div>\n'
        '      <div class="lbl">다음 기록</div>\n'
        '      <h3>%s</h3>\n'
        '    </div>\n'
        '    <svg class="arw" width="14" height="12" viewBox="0 0 14 12" fill="none" aria-hidden="true"><path d="M1 6h11M8 1.5L12.5 6 8 10.5" stroke="currentColor" stroke-width="1.1" stroke-linecap="round" stroke-linejoin="round"/></svg>\n'
        '  </a>' % (nxt["slug"], nxt["img"], e(nxt.get("alt_name") or nxt["person"]), e(nxt["title"]))
    )


def quote_block(st):
    if st.get("quote_inline"):
        return ""
    en_line = ('    <p class="en">%s</p>\n' % st["quote_en"]) if st.get("quote_en") else ""
    return ('  <figure class="quote">\n'
            '    <img class="bulb" src="../assets/img/bulb.webp" alt="" aria-hidden="true" width="1000" height="800" loading="lazy" decoding="async">\n'
            '    <div class="qm">&ldquo;</div>\n'
            '    <blockquote>%s</blockquote>\n'
            '%s'
            '    <figcaption>%s</figcaption>\n'
            '  </figure>' % (st["quote_text_html"], en_line, st["quote_caption"]))


def quote_block_en(st):
    """영문판 인용 블록. 원문이 영어가 아닌 경우에만 작은 글씨로 원문을 덧붙인다."""
    if st.get("quote_inline"):
        return ""
    en_line = ('    <p class="en">%s</p>\n' % st["quote_en"]) if st.get("quote_en") else ""
    return ('  <figure class="quote">\n'
            '    <img class="bulb" src="../../assets/img/bulb.webp" alt="" aria-hidden="true" width="1000" height="800" loading="lazy" decoding="async">\n'
            '    <div class="qm">&ldquo;</div>\n'
            '    <blockquote>%s</blockquote>\n'
            '%s'
            '    <figcaption>%s</figcaption>\n'
            '  </figure>' % (st["quote_text_html"], en_line, st["quote_caption"]))


def story_page(st, stories, published):
    tpl = STORY_TPL
    filebox = ""
    if st.get("filebox"):
        rows = "\n".join("      <dt>%s</dt><dd>%s</dd>" % (k, v) for k, v in st["filebox"])
        filebox = ('<div class="filebox">\n    <h3>%s</h3>\n    <dl>\n%s\n    </dl>\n  </div>'
                   % (e(st.get("filebox_title") or "사건 파일"), rows))
    tl_head = st.get("tl_head") or "실패의 연속에서<br>다시 서기까지"
    tokens = {
        "HREFLANG": hreflang("/stories/%s.html" % st["slug"], "/en/stories/%s.html" % st["slug"]),
        "LANG_TOGGLE": lang_toggle("../stories/%s.html" % st["slug"],
                                   "../en/stories/%s.html" % st["slug"], "ko",
                                   "Language · 언어"),
        "TITLE": e(st["title"]),
        "DESC": e(st["desc"]),
        "SLUG": st["slug"],
        "IMG": st["img"],
        "ALT": e(st["alt"]),
        "LDJSON": ldjson(st),
        "DRAWER_STORIES": drawer_items(published, "../"),
        "SHARE_TITLE": e(st["share_title"]),
        "SHARE_TEXT": e(st["share_text"]),
        "NOW_LABEL": e(st["now_label"]),
        "EYEBROW": e(st["eyebrow"]),
        "TITLE_HTML": st["title_html"],
        "LEAD_HTML": st["lead_html"],
        "PERSON": e(st["person"]),
        "YEARS": e(st["years"]),
        "MINUTES": e(st["minutes"]),
        "SOURCES_N": str(st["sources_count"]),
        "FILEBOX": filebox,
        "TL_HEAD": tl_head,
        "ARTICLE": "    " + st["article_html"].lstrip(),
        "QUOTE_BLOCK": quote_block(st),
        "TAKEAWAY_LINE": st["takeaway_line_html"],
        "TAKEAWAY_SUB": st["takeaway_sub"],
        "SOURCES": "      " + st["sources_html"].lstrip(),
        "FINE": st["fine"],
        "NEXT": next_html(stories, st, published),
        "TLDATA": json.dumps(st["timeline"], ensure_ascii=False, indent=1),
    }
    for k, v in tokens.items():
        tpl = tpl.replace("@@%s@@" % k, v)
    left = re.findall(r"@@\w+@@", tpl)
    if left:
        raise SystemExit("%s: 채우지 못한 토큰 %s" % (st["slug"], sorted(set(left))))
    return tpl


def home_page(stories, published, today):
    latest = published[-1]
    feat = (
        '<a class="feature" href="stories/%s.html">\n'
        '      <div class="feature-media">\n'
        '        <span class="tag">오늘의 기록</span>\n'
        '        <img src="assets/img/%s.webp" width="900" height="1350" alt="%s" fetchpriority="high" decoding="async">\n'
        '      </div>\n'
        '      <div class="feature-body">\n'
        '        <span class="eyebrow"><span class="dash"></span>%s</span>\n'
        '        <h2>%s</h2>\n'
        '        <p>%s</p>\n'
        '        <div class="meta"><span>%s</span><i></i><span>%s</span><i></i><span>사료 %d건</span></div>\n'
        '      </div>\n'
        '    </a>' % (latest["slug"], latest["img"], e(latest["alt"]), e(latest["eyebrow"]),
                     latest["title_html"], e(latest["card_desc"]), latest["event_date"],
                     e(latest["minutes"]), latest["sources_count"])
    )
    cards = []
    for s in reversed(published):
        cards.append(
            '        <a class="card" href="stories/%s.html">\n'
            '          <div class="thumb"><img src="assets/img/%s-thumb.webp" width="360" height="440" alt="%s 에디토리얼 초상(AI 생성)" loading="lazy" decoding="async"></div>\n'
            '          <div class="card-txt">\n'
            '            <h3>%s</h3>\n'
            '            <p>%s</p>\n'
            '            <div class="meta"><span>%s</span><i></i><span>%s</span><i></i><span>%s</span></div>\n'
            '          </div>\n'
            '        </a>' % (s["slug"], s["img"], e(s.get("alt_name") or s["person"]), e(s["title"]),
                            e(s["card_desc"]), e(s["person_short"]), dot(s["publish_date"]),
                            e(s["minutes"]))
        )
    desc = ("실패를 넘은 사람들의 1차 기록 아카이브. %d명의 가장 아팠던 하루를 날짜와 숫자, "
            "그날 남긴 말로 기록합니다." % len(published))
    tokens = {
        "HREFLANG": hreflang("/", "/en/"),
        "LANG_TOGGLE": lang_toggle("index.html", "en/index.html", "ko", "Language · 언어"),
        "DESC": e(desc),
        "DRAWER_STORIES": drawer_items(published),
        "ISSUE": "%03d" % len(published),
        "TODAY_DOT": dot(today),
        "FEATURE": feat,
        "FEATURE_SLUG": latest["slug"],
        "PUBLISHED_N": str(len(published)),
        "CARDS": "\n".join(cards),
    }
    tpl = INDEX_TPL
    for k, v in tokens.items():
        tpl = tpl.replace("@@%s@@" % k, v)
    left = re.findall(r"@@\w+@@", tpl)
    if left:
        raise SystemExit("index: 채우지 못한 토큰 %s" % sorted(set(left)))
    return tpl


def lineup_body(lineup, href_by_name):
    out = []
    for g in lineup:
        out.append('<section class="group"><div class="group-head">'
                   '<svg width="18" height="18" viewBox="0 0 18 18" fill="none" aria-hidden="true">%s</svg>'
                   "<h2>%s</h2><span class=\"cnt\">%d인</span></div><div class=\"people\">"
                   % (g["icon"], e(g["title"]), len(g["people"])))
        for i, p in enumerate(g["people"], 1):
            href = href_by_name.get(p["name"])
            name = ('<a class="nm" href="%s">%s</a>' % (href, e(p["name"]))) if href \
                else '<span class="nm">%s</span>' % e(p["name"])
            badge = ('<a class="badge" href="%s">읽기</a>' % href) if href \
                else '<span class="badge soon">예정</span>'
            out.append('<div class="person"><span class="idx">%02d</span>'
                       "<div><div>%s<span class=\"yr\">%s</span></div>"
                       '<p class="hook">%s</p></div>%s</div>'
                       % (i, name, e(p["years"]), e(p["hook"]), badge))
        out.append("</div></section>")
    return "\n      ".join(out)


def leaders_page(stories, published, lineup):
    href_by_name = {s["lineup_name"]: "../stories/%s.html" % s["slug"] for s in published}
    lu = json.loads(json.dumps(lineup, ensure_ascii=False))
    for g in lu:
        for p in g["people"]:
            if p["name"] in href_by_name:
                p["href"] = href_by_name[p["name"]]
    cards = []
    for s in reversed(published):
        cards.append(
            '        <a class="card" href="../stories/%s.html">\n'
            '          <div class="thumb"><img src="../assets/img/%s-thumb.webp" width="360" height="440" alt="%s 에디토리얼 초상(AI 생성)" loading="lazy" decoding="async"></div>\n'
            '          <div class="card-txt"><h3>%s</h3><p>%s</p><div class="meta"><span>%s</span><i></i><span>%s</span></div></div>\n'
            '        </a>' % (s["slug"], s["img"], e(s.get("alt_name") or s["person"]), e(s["title"]),
                            e(s["card_desc"]), e(s["person_short"]), e(s["minutes"]))
        )
    tokens = {
        "HREFLANG": hreflang("/leaders/", "/en/leaders/"),
        "LANG_TOGGLE": lang_toggle("../leaders/index.html", "../en/leaders/index.html", "ko",
                                   "Language · 언어"),
        "DRAWER_STORIES": drawer_items(published, "../"),
        "LU_BODY": lineup_body(lineup, href_by_name),
        "LU_DATA": json.dumps(lu, ensure_ascii=False, indent=1),
        "PUBLISHED_CARDS": "\n".join(cards),
        "PUBLISHED_N": str(len(published)),
    }
    tpl = LEADERS_TPL
    for k, v in tokens.items():
        tpl = tpl.replace("@@%s@@" % k, v)
    left = re.findall(r"@@\w+@@", tpl)
    if left:
        raise SystemExit("leaders: 채우지 못한 토큰 %s" % sorted(set(left)))
    return tpl


def sitemap(published, today):
    def entry(loc, lastmod, freq, prio, ko, en):
        alts = "".join('\n    <xhtml:link rel="alternate" hreflang="%s" href="%s"/>' % (h, u)
                       for h, u in (("ko", ko), ("en", en), ("x-default", ko)))
        return ('  <url>\n    <loc>%s</loc>\n    <lastmod>%s</lastmod>\n    <changefreq>%s</changefreq>\n'
                '    <priority>%s</priority>%s\n  </url>' % (loc, lastmod, freq, prio, alts))

    rows = []
    ko_home = SITE + "/"
    en_home = SITE + "/en/"
    rows.append(entry(ko_home, today, "daily", "1.0", ko_home, en_home))
    rows.append(entry(en_home, today, "daily", "0.9", ko_home, en_home))
    for s in reversed(published):
        ko = "%s/stories/%s.html" % (SITE, s["slug"])
        en = "%s/en/stories/%s.html" % (SITE, s["slug"])
        rows.append(entry(ko, s["publish_date"], "monthly", "0.9", ko, en))
        rows.append(entry(en, s["publish_date"], "monthly", "0.8", ko, en))
    for path, freq, prio in (("leaders/", "weekly", "0.8"), ("about/", "yearly", "0.5"),
                             ("privacy/", "yearly", "0.3"), ("terms/", "yearly", "0.3")):
        ko = "%s/%s" % (SITE, path)
        en = "%s/en/%s" % (SITE, path)
        rows.append(entry(ko, today, freq, prio, ko, en))
        rows.append(entry(en, today, freq, prio, ko, en))
    return ('<?xml version="1.0" encoding="UTF-8"?>\n'
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"\n'
            '        xmlns:xhtml="http://www.w3.org/1999/xhtml">\n'
            + "\n".join(rows) + "\n</urlset>\n")


# ---------------------------------------------------------------- english build
def en_drawer_items(stories, prefix=""):
    out = []
    for s in list(reversed(stories))[:DRAWER_LIMIT]:
        year = s["now_label"].split("·")[-1].strip() if "·" in s["now_label"] else ""
        label = "%s · %s" % (s["person_short"], year) if year else s["person_short"]
        out.append(
            '<a class="dr-item" href="%sstories/%s.html" data-close>\n'
            '      <svg width="18" height="18" viewBox="0 0 18 18" fill="none" aria-hidden="true"><path d="M4 2.5h10v13l-5-3.2-5 3.2z" stroke="currentColor" stroke-width="1.1" stroke-linejoin="round"/></svg>\n'
            '      <span>%s<small>%s</small></span>\n'
            '    </a>' % (prefix, s["slug"], e(label), e(s["title"]))
        )
    return "\n    ".join(out)


def en_ldjson(st):
    article = {
        "@context": "https://schema.org",
        "@graph": [
            {
                "@type": "Article",
                "headline": st["title"],
                "description": st["desc"],
                "image": "%s/assets/img/og-%s.jpg" % (SITE, st["img"]),
                "datePublished": st["publish_date"] + "T08:00:00+09:00",
                "dateModified": st["publish_date"] + "T08:00:00+09:00",
                "inLanguage": "en",
                "articleSection": CAT_NAME_EN[st["category"]],
                "author": {"@type": "Organization", "name": "LEADERS FILES Editorial"},
                "publisher": {"@type": "Organization", "name": "LEADERS FILES", "url": SITE + "/"},
                "mainEntityOfPage": {"@type": "WebPage", "@id": "%s/en/stories/%s.html" % (SITE, st["slug"])},
                "about": {"@type": "Person", "name": st["person"],
                          "birthDate": st["birth"], "deathDate": st["death"]},
            },
            {
                "@type": "BreadcrumbList",
                "itemListElement": [
                    {"@type": "ListItem", "position": 1, "name": "Archive", "item": SITE + "/en/"},
                    {"@type": "ListItem", "position": 2,
                     "name": "%s · %s" % (st["person_short"], st["now_label"].split("·")[-1].strip()),
                     "item": "%s/en/stories/%s.html" % (SITE, st["slug"])},
                ],
            },
        ],
    }
    return json.dumps(article, ensure_ascii=False)


def en_next_html(published, st):
    if len(published) < 2:
        return ""
    idx = [s["slug"] for s in published].index(st["slug"])
    nxt = published[(idx + 1) % len(published)]
    return (
        '<a class="next" href="../stories/%s.html">\n'
        '    <div class="thumb"><img src="../../assets/img/%s-thumb.webp" width="360" height="440" alt="Editorial portrait of %s (AI-generated)" loading="lazy" decoding="async"></div>\n'
        '    <div>\n'
        '      <div class="lbl">Next record</div>\n'
        '      <h3>%s</h3>\n'
        '    </div>\n'
        '    <svg class="arw" width="14" height="12" viewBox="0 0 14 12" fill="none" aria-hidden="true"><path d="M1 6h11M8 1.5L12.5 6 8 10.5" stroke="currentColor" stroke-width="1.1" stroke-linecap="round" stroke-linejoin="round"/></svg>\n'
        '  </a>' % (nxt["slug"], nxt["img"], e(nxt.get("alt_name") or nxt["person"]), e(nxt["title"]))
    )


def en_story_page(st, published):
    tpl = EN_STORY_TPL
    filebox = ""
    if st.get("filebox"):
        rows = "\n".join("      <dt>%s</dt><dd>%s</dd>" % (k, v) for k, v in st["filebox"])
        filebox = ('<div class="filebox">\n    <h3>%s</h3>\n    <dl>\n%s\n    </dl>\n  </div>'
                   % (e(st.get("filebox_title") or "Case file"), rows))
    tl_head = st.get("tl_head") or "From the failure<br>to standing again"
    tokens = {
        "HREFLANG": hreflang("/stories/%s.html" % st["slug"], "/en/stories/%s.html" % st["slug"]),
        "LANG_TOGGLE": lang_toggle("../../stories/%s.html" % st["slug"], "%s.html" % st["slug"],
                                   "en", "Language"),
        "TITLE": e(st["title"]),
        "DESC": e(st["desc"]),
        "SLUG": st["slug"],
        "IMG": st["img"],
        "ALT": e(st["alt"]),
        "LDJSON": en_ldjson(st),
        "DRAWER_STORIES": en_drawer_items(published, "../"),
        "SHARE_TITLE": e(st["share_title"]),
        "SHARE_TEXT": e(st["share_text"]),
        "NOW_LABEL": e(st["now_label"]),
        "EYEBROW": e(st["eyebrow"]),
        "TITLE_HTML": st["title_html"],
        "LEAD_HTML": st["lead_html"],
        "PERSON": e(st["person"]),
        "YEARS": e(st["years"]),
        "MINUTES": e(st["minutes"]),
        "SOURCES_N": str(st["sources_count"]),
        "FILEBOX": filebox,
        "TL_HEAD": tl_head,
        "ARTICLE": "    " + st["article_html"].lstrip(),
        "QUOTE_BLOCK": quote_block_en(st),
        "TAKEAWAY_LINE": st["takeaway_line_html"],
        "TAKEAWAY_SUB": st["takeaway_sub"],
        "SOURCES": "      " + st["sources_html"].lstrip(),
        "FINE": st["fine"],
        "NEXT": en_next_html(published, st),
        "TLDATA": json.dumps(st["timeline"], ensure_ascii=False, indent=1),
    }
    for k, v in tokens.items():
        tpl = tpl.replace("@@%s@@" % k, v)
    left = re.findall(r"@@\w+@@", tpl)
    if left:
        raise SystemExit("en/%s: 채우지 못한 토큰 %s" % (st["slug"], sorted(set(left))))
    return tpl


def en_home_page(published, today):
    latest = published[-1]
    feat = (
        '<a class="feature" href="stories/%s.html">\n'
        '      <div class="feature-media">\n'
        '        <span class="tag">Latest record</span>\n'
        '        <img src="../assets/img/%s.webp" width="900" height="1350" alt="%s" fetchpriority="high" decoding="async">\n'
        '      </div>\n'
        '      <div class="feature-body">\n'
        '        <span class="eyebrow"><span class="dash"></span>%s</span>\n'
        '        <h2>%s</h2>\n'
        '        <p>%s</p>\n'
        '        <div class="meta"><span>%s</span><i></i><span>%s</span><i></i><span>%d sources</span></div>\n'
        '      </div>\n'
        '    </a>' % (latest["slug"], latest["img"], e(latest["alt"]), e(latest["eyebrow"]),
                     latest["title_html"], e(latest["card_desc"]), latest["event_date"],
                     e(latest["minutes"]), latest["sources_count"])
    )
    cards = []
    for s in reversed(published):
        cards.append(
            '        <a class="card" href="stories/%s.html">\n'
            '          <div class="thumb"><img src="../assets/img/%s-thumb.webp" width="360" height="440" alt="Editorial portrait of %s (AI-generated)" loading="lazy" decoding="async"></div>\n'
            '          <div class="card-txt">\n'
            '            <h3>%s</h3>\n'
            '            <p>%s</p>\n'
            '            <div class="meta"><span>%s</span><i></i><span>%s</span><i></i><span>%s</span></div>\n'
            '          </div>\n'
            '        </a>' % (s["slug"], s["img"], e(s.get("alt_name") or s["person"]), e(s["title"]),
                            e(s["card_desc"]), e(s["person_short"]), dot(s["publish_date"]),
                            e(s["minutes"]))
        )
    desc = ("A primary-source archive of people who stood up the morning after failure. "
            "%d stories told through dates, numbers and the words they left that day." % len(published))
    tokens = {
        "HREFLANG": hreflang("/", "/en/"),
        "LANG_TOGGLE": lang_toggle("../index.html", "index.html", "en", "Language"),
        "DESC": e(desc),
        "DRAWER_STORIES": en_drawer_items(published),
        "ISSUE": "%03d" % len(published),
        "TODAY_DOT": dot(today),
        "FEATURE": feat,
        "FEATURE_SLUG": latest["slug"],
        "PUBLISHED_N": str(len(published)),
        "CARDS": "\n".join(cards),
    }
    tpl = EN_INDEX_TPL
    for k, v in tokens.items():
        tpl = tpl.replace("@@%s@@" % k, v)
    left = re.findall(r"@@\w+@@", tpl)
    if left:
        raise SystemExit("en/index: 채우지 못한 토큰 %s" % sorted(set(left)))
    return tpl


def en_lineup_body(lineup, published_slugs):
    out = []
    for g in lineup:
        out.append('<section class="group"><div class="group-head">'
                   '<svg width="18" height="18" viewBox="0 0 18 18" fill="none" aria-hidden="true">%s</svg>'
                   "<h2>%s</h2><span class=\"cnt\">%d people</span></div><div class=\"people\">"
                   % (g["icon"], e(g["title"]), len(g["people"])))
        for i, p in enumerate(g["people"], 1):
            href = ("../stories/%s.html" % p["story"]) if p.get("story") in published_slugs else None
            name = ('<a class="nm" href="%s">%s</a>' % (href, e(p["name"]))) if href \
                else '<span class="nm">%s</span>' % e(p["name"])
            badge = ('<a class="badge" href="%s">Read</a>' % href) if href \
                else '<span class="badge soon">Soon</span>'
            out.append('<div class="person"><span class="idx">%02d</span>'
                       "<div><div>%s<span class=\"yr\">%s</span></div>"
                       '<p class="hook">%s</p></div>%s</div>'
                       % (i, name, e(p["years"]), e(p["hook"]), badge))
        out.append("</div></section>")
    return "\n      ".join(out)


def en_leaders_page(published, lineup_en):
    published_slugs = {s["slug"] for s in published}
    lu = json.loads(json.dumps(lineup_en, ensure_ascii=False))
    for g in lu:
        for p in g["people"]:
            if p.get("story") in published_slugs:
                p["href"] = "../stories/%s.html" % p["story"]
            # 미발행 원고의 slug 는 클라이언트 데이터에 싣지 않는다(href 만으로 충분).
            p.pop("story", None)
    cards = []
    for s in reversed(published):
        cards.append(
            '        <a class="card" href="../stories/%s.html">\n'
            '          <div class="thumb"><img src="../../assets/img/%s-thumb.webp" width="360" height="440" alt="Editorial portrait of %s (AI-generated)" loading="lazy" decoding="async"></div>\n'
            '          <div class="card-txt"><h3>%s</h3><p>%s</p><div class="meta"><span>%s</span><i></i><span>%s</span></div></div>\n'
            '        </a>' % (s["slug"], s["img"], e(s.get("alt_name") or s["person"]), e(s["title"]),
                            e(s["card_desc"]), e(s["person_short"]), e(s["minutes"]))
        )
    tokens = {
        "HREFLANG": hreflang("/leaders/", "/en/leaders/"),
        "LANG_TOGGLE": lang_toggle("../../leaders/index.html", "index.html", "en", "Language"),
        "DRAWER_STORIES": en_drawer_items(published, "../"),
        "LU_BODY": en_lineup_body(lineup_en, published_slugs),
        "LU_DATA": json.dumps(lu, ensure_ascii=False, indent=1),
        "PUBLISHED_CARDS": "\n".join(cards),
        "PUBLISHED_N": str(len(published)),
    }
    tpl = EN_LEADERS_TPL
    for k, v in tokens.items():
        tpl = tpl.replace("@@%s@@" % k, v)
    left = re.findall(r"@@\w+@@", tpl)
    if left:
        raise SystemExit("en/leaders: 채우지 못한 토큰 %s" % sorted(set(left)))
    return tpl


# ---------------------------------------------------------------- mail data
MAIL_JS = os.path.join(ROOT, "functions", "api", "_stories.js")


def plain_text(fragment, keep_breaks=False):
    """HTML 조각을 메일용 평문으로 바꾼다(태그 제거 + 엔티티 복원 + 공백 정리)."""
    s = re.sub(r"(?is)<(script|style|svg)\b.*?</\1\s*>", " ", fragment or "")
    s = re.sub(r"(?i)<br\s*/?>", "\n" if keep_breaks else " ", s)
    s = re.sub(r"(?s)<[^>]+>", "", s)
    s = html.unescape(s).replace("\u00a0", " ")
    if keep_breaks:
        return "\n".join(re.sub(r"[ \t]+", " ", ln).strip() for ln in s.split("\n")).strip()
    return re.sub(r"\s+", " ", s).strip()


def mail_paragraphs(article_html, limit=2):
    """본문에서 메일 하이라이트로 쓸 문단을 순서대로 뽑는다(박스형 aside 는 제외)."""
    out = []
    for m in re.finditer(r"(?is)<p(\s[^>]*)?>(.*?)</p>", article_html or ""):
        attrs = m.group(1) or ""
        if "aside" in attrs:
            continue
        t = plain_text(m.group(2))
        if len(t) < 40:
            continue
        out.append(t)
        if len(out) >= limit:
            break
    return out


def mail_entry(st, index):
    """메일 발송에 필요한 필드만, 공개 가능한 값만 담는다."""
    en = en_view(st)

    def view(v, lang):
        slug = st["slug"]
        lead = plain_text(v["lead_html"])
        # 리드와 같은 문단은 하이라이트에서 빼고(중복), 다른 본문 문단을 앞쪽부터 2개 쓴다.
        highlight = [p for p in mail_paragraphs(v["article_html"], 4)
                     if not (len(p) >= 30 and p[:30] in lead)][:2]
        return {
            "person": v["person"],
            "personShort": v["person_short"],
            "title": v["title"],
            "eyebrow": v["eyebrow"],
            "category": CAT_NAME_EN[v["category"]] if lang == "en" else CAT_NAME[v["category"]],
            "desc": v["desc"],
            "lead": lead,
            "highlight": highlight,
            "quote": plain_text(v["quote_text_html"], keep_breaks=True),
            "quoteCaption": plain_text(v["quote_caption"]),
            "takeaway": plain_text(v["takeaway_sub"]),
            "minutes": v["minutes"],
            "url": ("%s/en/stories/%s.html" % (SITE, slug)) if lang == "en"
                   else ("%s/stories/%s.html" % (SITE, slug)),
            "home": ("%s/en/" % SITE) if lang == "en" else (SITE + "/"),
        }

    return {
        "n": index,
        "slug": st["slug"],
        "publishDate": st["publish_date"],
        "eventDate": st["event_date"],
        "img": st["img"],
        "ko": view(st, "ko"),
        "en": view(en, "en"),
    }


def mail_stories_js(published, today):
    entries = [mail_entry(s, i) for i, s in enumerate(published, 1)]
    body = json.dumps(entries, ensure_ascii=False, indent=1)
    return (
        "// AUTO-GENERATED by tools/build_site.py — 직접 고치지 마세요.\n"
        "// 메일 순차 발송(functions/api/subscribe.js, dispatch.js)용 공개 편 목록.\n"
        "// publish_date <= %s (KST) 인 편만 담는다. 미래 원고는 절대 들어가지 않는다.\n"
        "export const BUILD_DATE = %s;\n"
        "export const STORIES = %s;\n" % (today, json.dumps(today), body)
    )


# ---------------------------------------------------------------- number check
KO_NUM = ("한|두|세|네|다섯|여섯|일곱|여덟|아홉|열|스물|서른|마흔|쉰|예순|일흔|여든|아흔")
KO_CNT = ("개|명|번|번째|차례|년|살|가지|권|장|척|대|마리|달|주일|시간|분|초|곳|줄|걸음|동|층|편|회|군데|쌍|벌|그루|송이|알|달러|원|리|킬로미터|미터")
NUM_PATTERNS = [
    re.compile(r"(?<![가-힣])(%s)\s*(%s)(?![가-힣])" % (KO_NUM, KO_CNT)),
    re.compile(r"(?<![가-힣])(하나|둘|셋|넷)(?![가-힣])"),
    re.compile(r"(?<![가-힣수0-9,])([일이삼사오육칠팔구]?)(십|백|천|만)\s*(%s)" % KO_CNT),
]


def story_texts(st):
    parts = [st["title"], st["desc"], st["lead_html"], st["article_html"],
             st["quote_text_html"], st["takeaway_line_html"], st["takeaway_sub"]]
    for it in st["timeline"]:
        parts.extend([it.get("name", ""), it.get("year", ""), it.get("title", ""), it.get("body", "")])
        parts.extend(it.get("sub") or [])
    return "\n".join(parts)


def check_numbers(stories):
    bad = 0
    for st in stories:
        text = story_texts(st)
        clean = re.sub(r"(?is)<(script|style|svg)\b.*?</\1\s*>", " ", text)
        clean = re.sub(r"(?s)<[^>]+>", " ", clean)
        clean = clean.replace("삼천리강산", "XXX")  # 고정 관용구(검사 제외)
        for pat in NUM_PATTERNS:
            for m in pat.finditer(clean):
                ctx = clean[max(0, m.start() - 20):m.end() + 20].replace("\n", " ")
                print("  [숫자] %-22s %s  …%s…" % (st["slug"], m.group(0), ctx))
                bad += 1
    return bad


# ---------------------------------------------------------------- main
def main(argv):
    today = today_kst()
    check_only = False
    include_future = False
    for a in argv[1:]:
        if a.startswith("--today="):
            today = a.split("=", 1)[1]
            datetime.date.fromisoformat(today)
        elif a == "--include-future":
            include_future = True
        elif a == "--check-numbers":
            check_only = True
        else:
            raise SystemExit("알 수 없는 인자: %s" % a)

    stories = load_stories()
    lineup = load_lineup()
    lineup_en = load_lineup_en()
    bad = check_numbers(stories)
    if check_only:
        print("한글 수사 검사: %d건" % bad)
        return 1 if bad else 0

    published = [s for s in stories if include_future or s["publish_date"] <= today]

    # story pages
    os.makedirs(os.path.join(ROOT, "stories"), exist_ok=True)
    published_slugs = {s["slug"] for s in published}
    for s in published:
        with open(os.path.join(ROOT, "stories", s["slug"] + ".html"), "w", encoding="utf-8") as f:
            f.write(story_page(s, stories, published))
    removed = []
    for fn in os.listdir(os.path.join(ROOT, "stories")):
        if fn.endswith(".html") and fn[:-5] not in published_slugs:
            os.remove(os.path.join(ROOT, "stories", fn))
            removed.append(fn)

    # home / leaders / sitemap
    with open(os.path.join(ROOT, "index.html"), "w", encoding="utf-8") as f:
        f.write(home_page(stories, published, today))
    with open(os.path.join(ROOT, "leaders", "index.html"), "w", encoding="utf-8") as f:
        f.write(leaders_page(stories, published, lineup))
    with open(os.path.join(ROOT, "sitemap.xml"), "w", encoding="utf-8") as f:
        f.write(sitemap(published, today))

    # 메일 발송용 공개 편 목록(공개된 편만). functions/ 는 정적 서빙되지 않는다.
    os.makedirs(os.path.dirname(MAIL_JS), exist_ok=True)
    with open(MAIL_JS, "w", encoding="utf-8") as f:
        f.write(mail_stories_js(published, today))

    # ---------- english (/en/) : 같은 발행 조건으로 동시 공개 ----------
    en_published = [en_view(s) for s in published]
    os.makedirs(os.path.join(EN_ROOT, "stories"), exist_ok=True)
    os.makedirs(os.path.join(EN_ROOT, "leaders"), exist_ok=True)
    for s in en_published:
        with open(os.path.join(EN_ROOT, "stories", s["slug"] + ".html"), "w", encoding="utf-8") as f:
            f.write(en_story_page(s, en_published))
    removed_en = []
    for fn in os.listdir(os.path.join(EN_ROOT, "stories")):
        if fn.endswith(".html") and fn[:-5] not in published_slugs:
            os.remove(os.path.join(EN_ROOT, "stories", fn))
            removed_en.append(fn)
    with open(os.path.join(EN_ROOT, "index.html"), "w", encoding="utf-8") as f:
        f.write(en_home_page(en_published, today))
    with open(os.path.join(EN_ROOT, "leaders", "index.html"), "w", encoding="utf-8") as f:
        f.write(en_leaders_page(en_published, lineup_en))

    # asset check
    missing = []
    for s in published:
        for name in (s["img"] + ".jpg", s["img"] + ".webp", s["img"] + "-thumb.webp",
                     "og-" + s["img"] + ".jpg"):
            if not os.path.exists(os.path.join(ROOT, "assets", "img", name)):
                missing.append(name)
    print("발행 %d편 / 전체 %d편 (기준일 %s) — 한국어·영문 동시" % (len(published), len(stories), today))
    if removed:
        print("미래 날짜로 삭제: %s" % ", ".join(removed))
    if removed_en:
        print("미래 날짜로 삭제(en): %s" % ", ".join(removed_en))
    if missing:
        print("이미지 없음: %s" % ", ".join(sorted(set(missing))))
    print("한글 수사 검사: %d건" % bad)
    return 1 if (bad or missing) else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
