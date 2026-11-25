/* ============================================================
   LEADERS FILES — shared behaviour
   No dependencies. Everything degrades gracefully without JS.
   ============================================================ */
(function () {
  "use strict";

  var $ = function (s, c) { return (c || document).querySelector(s); };
  var $$ = function (s, c) { return Array.prototype.slice.call((c || document).querySelectorAll(s)); };

  /* ---------------- copy (Korean / English) ---------------- */
  var IS_EN = (document.documentElement.lang || "ko").toLowerCase().indexOf("en") === 0;
  var T = IS_EN ? {
    copied: "Link and line copied. Paste it into KakaoTalk or a message.",
    copyFail: "This browser does not support automatic copying.",
    step: " steps",
    read: "Read",
    soon: "Soon",
    people: " people",
    emailReq: "Please enter your email address.",
    emailBad: "Check the email address format. Example: name@example.com",
    consentReq: "Please agree to the collection and use of personal data.",
    notReady: "Subscriptions are being prepared · 1 story a day is coming soon. Your address was not sent.",
    sending: "Sending…",
    subscribe: "Subscribe",
    subscribed: "You are subscribed. The first story arrives tomorrow morning."
  } : {
    copied: "링크와 문장을 복사했어요. 카톡에 붙여넣기 하세요.",
    copyFail: "이 브라우저에서는 자동 복사를 지원하지 않아요.",
    step: " 단계",
    read: "읽기",
    soon: "예정",
    people: "인",
    emailReq: "이메일 주소를 입력해 주세요.",
    emailBad: "이메일 주소 형식을 확인해 주세요. 예: name@example.com",
    consentReq: "개인정보 수집·이용에 동의해 주세요.",
    notReady: "구독 기능을 준비하고 있습니다 · 곧 매일 1편씩 보내드릴게요. 입력한 주소는 전송되지 않았습니다.",
    sending: "신청 중…",
    subscribe: "구독하기",
    subscribed: "구독 신청을 받았습니다. 첫 편은 내일 아침에 보내드릴게요."
  };

  /* ---------------- header scroll + reading progress ---------------- */
  var hdr = $("#hdr");
  var bar = $(".progress i");
  var isArticle = document.body.getAttribute("data-article") === "true";
  function onScroll() {
    var y = window.pageYOffset || document.documentElement.scrollTop || 0;
    if (hdr) hdr.classList.toggle("scrolled", y > 6);
    if (bar && isArticle) {
      var max = document.documentElement.scrollHeight - window.innerHeight;
      bar.style.width = (max > 0 ? Math.min(100, (y / max) * 100) : 0) + "%";
    }
  }
  var ticking = false;
  window.addEventListener("scroll", function () {
    if (ticking) return;
    ticking = true;
    window.requestAnimationFrame(function () { onScroll(); ticking = false; });
  }, { passive: true });
  onScroll();

  /* ---------------- drawer ---------------- */
  var drawer = $("#drawer"), scrim = $("#scrim"), menuBtn = $("#menuBtn"), closeBtn = $("#closeBtn");
  function openDrawer() {
    if (!drawer) return;
    drawer.classList.add("on");
    if (scrim) scrim.classList.add("on");
    drawer.setAttribute("aria-hidden", "false");
    if (menuBtn) menuBtn.setAttribute("aria-expanded", "true");
    document.body.style.overflow = "hidden";
    if (closeBtn) closeBtn.focus();
  }
  function closeDrawer() {
    if (!drawer || !drawer.classList.contains("on")) return;
    drawer.classList.remove("on");
    if (scrim) scrim.classList.remove("on");
    drawer.setAttribute("aria-hidden", "true");
    if (menuBtn) menuBtn.setAttribute("aria-expanded", "false");
    document.body.style.overflow = "";
  }
  if (menuBtn) menuBtn.addEventListener("click", openDrawer);
  if (closeBtn) closeBtn.addEventListener("click", closeDrawer);
  if (scrim) scrim.addEventListener("click", closeDrawer);
  $$("[data-close]").forEach(function (a) { a.addEventListener("click", function () { window.setTimeout(closeDrawer, 10); }); });
  document.addEventListener("keydown", function (e) { if (e.key === "Escape") closeDrawer(); });

  /* ---------------- toast ---------------- */
  var toast = $("#toast"), toastTimer = null;
  function showToast(msg) {
    if (!toast) return;
    toast.textContent = msg;
    toast.classList.add("on");
    window.clearTimeout(toastTimer);
    toastTimer = window.setTimeout(function () { toast.classList.remove("on"); }, 2600);
  }

  /* ---------------- share ---------------- */
  function copyFallback(text) {
    var ta = document.createElement("textarea");
    ta.value = text;
    ta.setAttribute("readonly", "");
    ta.style.position = "fixed";
    ta.style.top = "-1000px";
    ta.style.opacity = "0";
    document.body.appendChild(ta);
    ta.select();
    ta.setSelectionRange(0, ta.value.length);
    var ok = false;
    try { ok = document.execCommand("copy"); } catch (e) { ok = false; }
    document.body.removeChild(ta);
    showToast(ok ? T.copied : T.copyFail);
  }
  function copyText(text) {
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(text)
        .then(function () { showToast(T.copied); })
        .catch(function () { copyFallback(text); });
    } else {
      copyFallback(text);
    }
  }
  function doShare(btn) {
    var title = btn.getAttribute("data-share-title") || document.title;
    var text = btn.getAttribute("data-share-text") || title;
    var url = location.href.split("#")[0];
    if (navigator.share) {
      navigator.share({ title: title, text: text, url: url }).catch(function (err) {
        if (err && err.name === "AbortError") return;
        copyText(text + "\n" + url);
      });
      return;
    }
    copyText(text + "\n" + url);
  }
  $$("[data-share]").forEach(function (b) {
    b.addEventListener("click", function (e) { e.preventDefault(); doShare(b); });
  });

  /* ---------------- timeline ---------------- */
  (function () {
    var wrap = $("#tl");
    var detail = $("#tlDetail");
    var hint = $("#tlHint");
    var dataEl = $("#tlData");
    if (!wrap || !detail || !dataEl) return;
    var steps;
    try { steps = JSON.parse(dataEl.textContent); } catch (e) { return; }
    if (!steps || !steps.length) return;

    var active = 0;
    var track = document.createElement("div");
    track.className = "tl-track";
    wrap.appendChild(track);

    steps.forEach(function (s, i) {
      var b = document.createElement("button");
      b.type = "button";
      b.className = "tl-item" + (i === active ? " active" : "");
      b.setAttribute("role", "tab");
      b.setAttribute("aria-selected", i === active ? "true" : "false");
      var subs = "";
      (s.sub || []).forEach(function (line) { subs += "<br>" + line; });
      b.innerHTML = '<span class="tl-name">' + s.name + '</span>' +
                    '<span class="tl-dotrow"><span class="tl-dot"></span></span>' +
                    '<span class="tl-sub">' + subs + "</span>";
      b.addEventListener("click", function () { select(i, true); });
      b.addEventListener("keydown", function (ev) {
        if (ev.key === "ArrowRight") { ev.preventDefault(); select(Math.min(steps.length - 1, i + 1), true); }
        if (ev.key === "ArrowLeft") { ev.preventDefault(); select(Math.max(0, i - 1), true); }
      });
      track.appendChild(b);
    });

    function paint() {
      var s = steps[active];
      detail.innerHTML = '<div class="k">' + s.k + " · " + s.year + "</div><h4>" + s.title + "</h4><p>" + s.body + "</p>";
    }
    function select(i, fromUser) {
      active = i;
      $$(".tl-item", wrap).forEach(function (el, j) {
        el.classList.toggle("active", j === i);
        el.setAttribute("aria-selected", j === i ? "true" : "false");
      });
      detail.classList.add("swap");
      window.setTimeout(function () { paint(); detail.classList.remove("swap"); }, 120);
      if (fromUser) {
        var el = $$(".tl-item", wrap)[i];
        var left = el.offsetLeft - (wrap.clientWidth - el.offsetWidth) / 2;
        if (wrap.scrollTo) wrap.scrollTo({ left: Math.max(0, left), behavior: "smooth" });
        else wrap.scrollLeft = Math.max(0, left);
        if (hint) hint.textContent = (i + 1) + " / " + steps.length + T.step;
      }
    }
    paint();
  })();

  /* ---------------- leader lineup ---------------- */
  (function () {
    var body = $("#luBody");
    var chips = $("#chips");
    var dataEl = $("#luData");
    if (!body || !dataEl) return;
    var groups;
    try { groups = JSON.parse(dataEl.textContent); } catch (e) { return; }
    if (!groups || !groups.length) return;

    function render(filter) {
      var html = "";
      groups.forEach(function (g) {
        if (filter !== "all" && filter !== g.id) return;
        html += '<section class="group"><div class="group-head">' +
          '<svg width="18" height="18" viewBox="0 0 18 18" fill="none" aria-hidden="true">' + g.icon + "</svg>" +
          "<h2>" + g.title + '</h2><span class="cnt">' + g.people.length + T.people + "</span></div><div class=\"people\">";
        g.people.forEach(function (p, i) {
          var name = p.href ? '<a class="nm" href="' + p.href + '">' + p.name + "</a>" : '<span class="nm">' + p.name + "</span>";
          var badge = p.href ? '<a class="badge" href="' + p.href + '">' + T.read + '</a>' : '<span class="badge soon">' + T.soon + "</span>";
          html += '<div class="person"><span class="idx">' + String(i + 1).padStart(2, "0") + "</span>" +
                  "<div><div>" + name + '<span class="yr">' + p.years + "</span></div>" +
                  '<p class="hook">' + p.hook + "</p></div>" + badge + "</div>";
        });
        html += "</div></section>";
      });
      body.innerHTML = html;
    }
    render("all");

    $$(".chip", chips).forEach(function (c) {
      c.addEventListener("click", function () {
        $$(".chip", chips).forEach(function (x) { x.classList.remove("active"); x.setAttribute("aria-selected", "false"); });
        c.classList.add("active");
        c.setAttribute("aria-selected", "true");
        render(c.getAttribute("data-g"));
      });
    });
  })();

  /* ---------------- email subscription ---------------- */
  /* Set this to "/api/subscribe" once the mailing backend is live.
     While it is empty, the form validates and shows the "준비 중" notice
     without sending a request, so no failed request appears in the console. */
  var SUBSCRIBE_ENDPOINT = "";
  (function () {
    var forms = $$("form.sub-form");
    if (!forms.length) return;
    var EMAIL = /^[^\s@]+@[^\s@]+\.[a-z]{2,}$/i;

    forms.forEach(function (form) {
      var input = $(".sub-input", form);
      var consent = $("input[type=checkbox]", form);
      var msg = $(".sub-msg", form);
      var btn = $("button[type=submit]", form);
      if (!input || !msg || !btn) return;

      function say(text, kind) {
        msg.textContent = text;
        msg.className = "sub-msg on" + (kind ? " " + kind : "");
      }

      form.addEventListener("submit", function (e) {
        e.preventDefault();
        var value = (input.value || "").trim();
        if (!value) { input.focus(); say(T.emailReq, "err"); return; }
        if (!EMAIL.test(value)) { input.focus(); say(T.emailBad, "err"); return; }
        if (consent && !consent.checked) { consent.focus(); say(T.consentReq, "err"); return; }

        var resetBtn = function () { btn.disabled = false; btn.textContent = T.subscribe; };
        var notReady = function () {
          resetBtn();
          say(T.notReady, "err");
        };

        if (!SUBSCRIBE_ENDPOINT) { notReady(); return; }

        btn.disabled = true;
        btn.textContent = T.sending;
        say(IS_EN ? "Sending your request…" : "신청을 보내고 있습니다…", "");

        fetch(SUBSCRIBE_ENDPOINT, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ email: value, consent: true, source: location.pathname })
        }).then(function (res) {
          if (!res.ok) throw new Error("not-configured");
          return res.json().catch(function () { return {}; });
        }).then(function () {
          resetBtn();
          form.reset();
          say(T.subscribed, "ok");
        }).catch(function () {
          notReady();
        });
      });

      if (input) input.addEventListener("input", function () {
        if (msg.classList.contains("err")) { msg.className = "sub-msg"; msg.textContent = ""; }
      });
    });
  })();

})();
