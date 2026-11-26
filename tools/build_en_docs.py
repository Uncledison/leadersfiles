#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Build the English document pages (/en/about/, /en/privacy/, /en/terms/).

These three pages are static in the Korean tree (hand-maintained HTML), so the English
counterparts are produced here and the output is committed. Re-run after editing the
Korean copy so the two languages stay in step.

    python3 tools/build_en_docs.py
"""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = "https://leaders.uncledison.com"

STORIES = [
    ("edison-1914", "Edison · 1914", "At 67, the night the laboratory burned"),
    ("lincoln-1858", "Lincoln · 1858", "He won the votes and lost the seat"),
    ("tesla-1895", "Tesla · 1895", "The dawn the laboratory became ash"),
    ("carnegie-1873", "Carnegie · 1873", "At 37, the Year the Banks Closed"),
]

HEAD = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<meta name="theme-color" content="#121316">
<meta name="color-scheme" content="dark">
<title>{title} · LEADERS FILES</title>
<meta name="description" content="{desc}">
<meta name="author" content="LEADERS FILES Editorial">
<meta name="robots" content="index,follow,max-image-preview:large">
<link rel="canonical" href="{site}/en/{slug}/">
<link rel="alternate" hreflang="ko" href="{site}/{slug}/">
<link rel="alternate" hreflang="en" href="{site}/en/{slug}/">
<link rel="alternate" hreflang="x-default" href="{site}/{slug}/">
<meta property="og:type" content="website">
<meta property="og:site_name" content="LEADERS FILES">
<meta property="og:locale" content="en_US">
<meta property="og:locale:alternate" content="ko_KR">
<meta property="og:title" content="{title} · LEADERS FILES">
<meta property="og:description" content="{desc}">
<meta property="og:url" content="{site}/en/{slug}/">
<meta property="og:image" content="{site}/assets/img/og-edison.jpg">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{title} · LEADERS FILES">
<meta name="twitter:description" content="{desc}">
<meta name="twitter:image" content="{site}/assets/img/og-edison.jpg">
<link rel="icon" href="../../assets/img/favicon.svg" type="image/svg+xml">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;700&family=Noto+Serif+KR:wght@400;600;700&display=swap">
<link rel="stylesheet" href="../../assets/css/site.css">
<script type="application/ld+json">
{ldjson}
</script>
</head>
<body data-page="{page}">
<a class="skip" href="#main">Skip to content</a>
<div class="progress" aria-hidden="true"><i></i></div>
<header class="hdr" id="hdr">
  <div class="hdr-in">
    <div class="hdr-top">
      <a class="brand" href="../index.html" aria-label="LEADERS FILES home">
        <span class="brand-en">Leaders Files</span>
        <span class="brand-kr">Records of the Fall</span>
      </a>
      <div class="lang" role="group" aria-label="Language">
        <a class="lang-a" href="../../{slug}/index.html" lang="ko" hreflang="ko">KR</a>
        <span class="lang-sep" aria-hidden="true">|</span>
        <a class="lang-a current" href="index.html" lang="en" hreflang="en" aria-current="page">EN</a>
      </div>
      <button class="menu-btn" id="menuBtn" type="button" aria-label="Open menu" aria-expanded="false" aria-controls="drawer">
        <svg width="20" height="14" viewBox="0 0 20 14" fill="none" aria-hidden="true">
          <path d="M0.5 1h19M0.5 7h13M0.5 13h19" stroke="#E8A84C" stroke-width="1.1" stroke-linecap="round"/>
        </svg>
      </button>
    </div>
    <nav class="hdr-nav" aria-label="Main menu">
      <a class="nav-item" href="../index.html">Archive</a>
      <a class="nav-item" href="../leaders/index.html">Leaders</a>
      <a class="nav-item{about_active}" href="../about/index.html"{about_cur}>Principles</a>
      <a class="nav-item" href="../index.html#subscribe">Subscribe</a>
    </nav>
  </div>
</header>
<div class="scrim" id="scrim"></div>
<aside class="drawer" id="drawer" aria-hidden="true" aria-label="All menu">
  <div class="drawer-top">
    <span>Leaders Files</span>
    <button class="x-btn" id="closeBtn" type="button" aria-label="Close menu">
      <svg width="16" height="16" viewBox="0 0 16 16" fill="none" aria-hidden="true">
        <path d="M2 2l12 12M14 2L2 14" stroke="#C9C5BD" stroke-width="1.1" stroke-linecap="round"/>
      </svg>
    </button>
  </div>
  <nav aria-label="All menu items">
    <a class="dr-item" href="../index.html" data-close>
      <svg width="18" height="18" viewBox="0 0 18 18" fill="none" aria-hidden="true"><path d="M2.5 4.5h13M2.5 9h13M2.5 13.5h9" stroke="currentColor" stroke-width="1.1" stroke-linecap="round"/></svg>
      <span>Archive<small>Magazine home · every record</small></span>
    </a>
    <div class="dr-sep">Stories</div>
    {stories}
    <div class="dr-sep">Browse</div>
    <a class="dr-item" href="../leaders/index.html" data-close>
      <svg width="18" height="18" viewBox="0 0 18 18" fill="none" aria-hidden="true"><circle cx="9" cy="6" r="3.1" stroke="currentColor" stroke-width="1.1"/><path d="M3 15.5c.6-3.1 3-4.6 6-4.6s5.4 1.5 6 4.6" stroke="currentColor" stroke-width="1.1" stroke-linecap="round"/></svg>
      <span>Lineup of 30 candidates<small>Enterprise, science, leadership</small></span>
    </a>
    <a class="dr-item" href="../about/index.html" data-close>
      <svg width="18" height="18" viewBox="0 0 18 18" fill="none" aria-hidden="true"><path d="M3 2.5h12v13H3z" stroke="currentColor" stroke-width="1.1"/><path d="M5.6 6.2h6.8M5.6 9h6.8M5.6 11.8h4" stroke="currentColor" stroke-width="1.1" stroke-linecap="round"/></svg>
      <span>Editorial principles<small>Sources, images, how a failure is read</small></span>
    </a>
    <a class="dr-item" href="#" data-share data-share-title="LEADERS FILES · Records of the Fall" data-share-text="Records of the Fall — LEADERS FILES">
      <svg width="18" height="18" viewBox="0 0 18 18" fill="none" aria-hidden="true"><circle cx="14" cy="4" r="2.1" stroke="currentColor" stroke-width="1.1"/><circle cx="4" cy="9" r="2.1" stroke="currentColor" stroke-width="1.1"/><circle cx="14" cy="14" r="2.1" stroke="currentColor" stroke-width="1.1"/><path d="M6 8l6-3M6 10l6 3" stroke="currentColor" stroke-width="1.1"/></svg>
      <span>Share this magazine<small>Link · send it anywhere</small></span>
    </a>
  </nav>
  <div class="dr-foot">
    LEADERS FILES records failure and recovery verified against public-domain primary sources.<br>
    <a href="../privacy/index.html" data-close style="text-decoration:underline;text-underline-offset:2px">Privacy Policy</a> ·
    <a href="../terms/index.html" data-close style="text-decoration:underline;text-underline-offset:2px">Terms of Use</a>
  </div>
</aside>
<main id="main">
  <div class="backrow"><a href="../index.html">
    <svg width="14" height="12" viewBox="0 0 14 12" fill="none" aria-hidden="true"><path d="M13 6H2M6 1.5L1.5 6 6 10.5" stroke="currentColor" stroke-width="1.1" stroke-linecap="round" stroke-linejoin="round"/></svg>
    Archive</a><span class="now">{now}</span></div>

  <div class="doc-head">
    <span class="eyebrow"><span class="dash"></span>{eyebrow}</span>
    <h1>{h1}</h1>
    <p>{lead}</p>
  </div>

  <div class="doc">
{body}
  </div>

  <div class="orn" aria-hidden="true">
    <svg width="22" height="22" viewBox="0 0 22 22" fill="none"><path d="M11 1v20M1 11h20M4 4l14 14M18 4L4 18" stroke="currentColor" stroke-width=".7"/><circle cx="11" cy="11" r="3.2" stroke="currentColor" stroke-width=".9"/></svg>
  </div>
  <footer class="foot">
    <div class="f-en">Leaders Files</div>
    <p>An archive of primary records of people who got up after failure<br>© 2026 LEADERS FILES</p>
    <div class="f-links">
      <a href="../index.html">Archive</a><span>·</span>
      <a href="../leaders/index.html">Lineup of 30</a><span>·</span>
      <a href="../about/index.html">Principles</a><span>·</span>
      <a href="../privacy/index.html">Privacy</a><span>·</span>
      <a href="../terms/index.html">Terms</a>
    </div>
  </footer>

</main>
<div class="toast" id="toast" role="status" aria-live="polite"></div>
<script src="../../assets/js/site.js" defer></script>
</body>
</html>
"""

ABOUT_BODY = """    <h2>What we write</h2>
    <p>LEADERS FILES covers the &lsquo;failed day&rsquo; of people whose lives can be checked against public-domain primary sources. Not the birth date and the list of achievements, but a day on which a decision had to be made, and the words left on that day.</p>
    <p>Only historical figures long dead. Portraits of living people and press photographs still under copyright are not used.</p>

    <h2>Sources first</h2>
    <p>Dates and events rely first on primary sources (newspapers, letters and official records of the time), with secondary works used to cross-check. Every article ends with a &lsquo;source note&rsquo; naming the material it rests on.</p>
    <ul>
      <li>Statements are quoted directly only where the source is confirmed.</li>
      <li>Lines that were polished later, or whose origin is unclear, are marked &lsquo;widely attributed&rsquo;.</li>
      <li>Where figures differ between sources, the difference is not hidden: it is stated in the text or in the source note.</li>
    </ul>

    <h2>Numbers and dates</h2>
    <p>Ages, years, counts and frequencies are written in Arabic numerals: 67, 13 buildings, 10,000 people. A reader should be able to compare numbers at a glance.</p>

    <h2>Image policy</h2>
    <p>Every portrait on this site is an <strong>editorial portrait (AI-generated)</strong>. None is a historical photograph, and none is presented in a way that could be mistaken for one. Under each image runs the line &lsquo;Editorial portrait (AI-generated) · Not a historical photograph&rsquo;.</p>
    <p>Background and decorative images follow the same rule. Where a public-domain source image is used, its source and holding institution are named.</p>

    <h2>AI disclosure</h2>
    <p>Portrait images were produced with an image generation model. The text is written and checked by the editorial desk against the sources. No AI-generated sentence is published as fact without verification.</p>

    <h2>Corrections</h2>
    <p>If you find an error, write to <a href="mailto:hello@uncledison.com">hello@uncledison.com</a>. Once a factual error is confirmed, the text is corrected and the date and content of the correction are recorded below the article. Purely stylistic edits are not separately marked.</p>
    <p class="updated">In effect from 25 November 2026</p>

    <h2>Advertising and sponsorship</h2>
    <p>There is no advertising and no affiliate link on this site at present. If advertising is introduced, the advertising area will be clearly marked and kept separate from editorial content.</p>

    <h2>Contact</h2>
    <p>Editorial desk · <a href="mailto:hello@uncledison.com">hello@uncledison.com</a></p>"""

PRIVACY_BODY = """    <p class="updated">In effect from 25 November 2026</p>

    <h2>1. What we collect</h2>
    <table>
      <tr><th>Item</th><th>When</th><th>Purpose</th></tr>
      <tr><td>Email address</td><td>On subscribing</td><td>Sending the newsletter</td></tr>
      <tr><td>Time of consent, page the request came from</td><td>On subscribing</td><td>Recording consent, managing delivery</td></tr>
      <tr><td>Access log (IP, browser information)</td><td>On visiting a page</td><td>Hosting provider security and fault handling</td></tr>
    </table>
    <p>We do not collect names, telephone numbers, addresses or payment details.</p>

    <h2>2. How it is used</h2>
    <ul>
      <li>Sending the newsletter (1 story at a time)</li>
      <li>Confirming subscriptions, handling unsubscribe requests and delivery errors</li>
      <li>Keeping a record of consent</li>
    </ul>
    <p>It is not used for any other purpose, and no advertising information is sold or passed to a third party.</p>

    <h2>3. Retention and deletion</h2>
    <p>An email address is deleted without delay when the subscription is cancelled. A record left in a delivery system backup is deleted within at most 30 days. Where other law requires retention, the address is kept for that period.</p>

    <h2>4. Processing by others and third parties</h2>
    <p>No personal data processing is currently entrusted to an outside party. If a delivery service or mailing tool is introduced, the processor and the work entrusted will be listed on this page first.</p>
    <p>Data is not provided to third parties except where an investigating authority makes a lawful request under statute.</p>

    <h2>5. Cookies and analytics</h2>
    <p>This site sets no cookies of its own and contains no visitor analytics or advertising scripts.</p>
    <div class="callout">Fonts are loaded from Google Fonts. When they are requested, the IP address of the connecting device and similar data may be sent to Google. The font request is unrelated to the newsletter, and Google&rsquo;s own policy applies.</div>
    <p>The hosting provider may keep access logs to deliver the service and keep it secure.</p>

    <h2>6. Status of the subscription form</h2>
    <p>Subscriptions are being prepared. While requests are not being accepted, the screen says so, and the address you enter is not sent to a server. When the service opens, this page will say so.</p>

    <h2>7. Your rights</h2>
    <p>You may exercise the following rights at any time.</p>
    <ul>
      <li>To request access to the information collected</li>
      <li>To request correction of an error</li>
      <li>To request deletion and suspension of processing</li>
      <li>To withdraw consent (cancel the subscription)</li>
    </ul>
    <p>Send requests to <a href="mailto:hello@uncledison.com">hello@uncledison.com</a>. They are handled within 10 days of confirming your identity.</p>

    <h2>8. Children&rsquo;s data</h2>
    <p>Subscriptions from children under 14 are not accepted. Where we learn of one, the address is deleted immediately.</p>

    <h2>9. Security measures</h2>
    <p>All traffic uses HTTPS, and the number of people with access to personal data and their permissions is kept to a minimum. Access rights to the delivery system are reviewed regularly.</p>

    <h2>10. Changes to this policy</h2>
    <p>If this policy changes, the effective date and the change are recorded on this page. A change unfavourable to subscribers is also announced in the newsletter.</p>

    <h2>11. Contact</h2>
    <p>Data protection · LEADERS FILES editorial desk<br>
    <a href="mailto:hello@uncledison.com">hello@uncledison.com</a></p>"""

TERMS_BODY = """    <p class="updated">In effect from 25 November 2026</p>

    <h2>1. Purpose</h2>
    <p>These terms set the conditions for using the text and images provided by LEADERS FILES (the &lsquo;site&rsquo;). Using the site is taken as agreement to them.</p>

    <h2>2. Copyright</h2>
    <p>The text on the site is written and checked by the editorial desk. Quoted statements and sources name their original source, and rights in those parts belong to their authors.</p>
    <p>Portraits are AI-generated editorial images. They are not historical photographs and may not be used as such.</p>

    <h2>3. Permitted use</h2>
    <ul>
      <li>Reading and printing for personal use</li>
      <li>Quoting 2 to 3 sentences with the source and a link to the original</li>
      <li>Introducing and linking to the site for teaching or research</li>
    </ul>

    <h2>4. Not permitted</h2>
    <ul>
      <li>Copying a whole article onto another site or into print</li>
      <li>Removing or cropping a watermark or source notice from an image</li>
      <li>Automated bulk collection, redistribution or sale</li>
      <li>Using the site&rsquo;s name or design so that another service is mistaken for it</li>
    </ul>

    <h2>5. Accuracy and liability</h2>
    <p>The site records from published sources. Interpretation of historical events and figures can differ between sources, and we do not assert motives that the record does not show.</p>
    <p>Nothing on this site is investment, legal or medical advice. Decisions taken after reading it are the reader&rsquo;s own responsibility.</p>

    <h2>6. External links</h2>
    <p>Source notes contain links to other sites. Their content and operation are outside our control, and their own terms apply.</p>

    <h2>7. Advertising and partnerships</h2>
    <p>There is no advertising or affiliate link at present. If either is introduced, it will be clearly marked and kept separate from editorial content.</p>

    <h2>8. Changes to these terms</h2>
    <p>If the terms change, the change is posted on this page with an effective date. Continuing to use the site after a change is taken as agreement to it.</p>

    <h2>9. Governing law</h2>
    <p>These terms are governed by the law of the Republic of Korea. Disputes fall under the jurisdiction of the Korean courts.</p>

    <h2>10. Contact</h2>
    <p>LEADERS FILES editorial desk · <a href="mailto:hello@uncledison.com">hello@uncledison.com</a></p>"""

PAGES = [
    dict(slug="about", page="about", title="Editorial Principles",
         desc="How LEADERS FILES writes a record — sources first, image policy, Arabic numerals, corrections and AI disclosure.",
         now="Editorial", eyebrow="Editorial Principles", h1="How this record is written",
         lead="Emotion is a conclusion drawn from verification, not the other way round. That is why this magazine puts the hardest day at the centre, not the moment of success.",
         body=ABOUT_BODY, ldtype="AboutPage", ldname="LEADERS FILES editorial principles"),
    dict(slug="privacy", page="privacy", title="Privacy Policy",
         desc="This site collects only what is needed to send the newsletter. What is collected, where it is used and when it is deleted.",
         now="Privacy", eyebrow="Privacy Policy", h1="Privacy Policy",
         lead="This site takes only the minimum information needed to send the newsletter. What is collected, where it is used and when it is deleted is set out below.",
         body=PRIVACY_BODY, ldtype="WebPage", ldname="LEADERS FILES privacy policy"),
    dict(slug="terms", page="terms", title="Terms of Use",
         desc="How the text and images of this site may be read and quoted.",
         now="Terms", eyebrow="Terms of Use", h1="Terms of Use",
         lead="How the text and images on this site may be read and quoted. We have tried not to write it in a difficult way.",
         body=TERMS_BODY, ldtype="WebPage", ldname="LEADERS FILES terms of use"),
]


def build_stories():
    out = []
    for slug, label, title in STORIES:
        out.append(
            '    <a class="dr-item" href="../stories/%s.html" data-close>\n'
            '      <svg width="18" height="18" viewBox="0 0 18 18" fill="none" aria-hidden="true"><path d="M4 2.5h10v13l-5-3.2-5 3.2z" stroke="currentColor" stroke-width="1.1" stroke-linejoin="round"/></svg>\n'
            '      <span>%s<small>%s</small></span>\n'
            '    </a>' % (slug, label, title))
    return "\n".join(out)


def main():
    for p in PAGES:
        ld = ('{"@context":"https://schema.org","@type":"%s","name":"%s","url":"%s/en/%s/",'
              '"inLanguage":"en","isPartOf":{"@type":"WebSite","name":"LEADERS FILES","url":"%s/en/"}}'
              % (p["ldtype"], p["ldname"], SITE, p["slug"], SITE))
        html = HEAD.format(
            site=SITE,
            title=p["title"], desc=p["desc"], slug=p["slug"], page=p["page"],
            ldjson=ld, stories=build_stories(), now=p["now"], eyebrow=p["eyebrow"],
            h1=p["h1"], lead=p["lead"], body=p["body"],
            about_active=" active" if p["slug"] == "about" else "",
            about_cur=' aria-current="page"' if p["slug"] == "about" else "")
        out_dir = os.path.join(ROOT, "en", p["slug"])
        os.makedirs(out_dir, exist_ok=True)
        with open(os.path.join(out_dir, "index.html"), "w", encoding="utf-8") as f:
            f.write(html)
        print("wrote en/%s/index.html" % p["slug"])


if __name__ == "__main__":
    main()
