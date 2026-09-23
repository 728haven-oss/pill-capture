/* 알약캡쳐 로그인 + 가입 후 무료체험 (config/auth.json → build.py 가 __PC_AUTH__ 주입)
   - 앱 코드(app.html)는 건드리지 않고 window.__pill.Pro.active 만 제어한다.
   - 체험 기간 동안은 Pro 와 동일하게 무제한, 끝나면 기존 페이월 로직이 그대로 작동. */
(function () {
  var CFG = window.__PC_AUTH || { enabled: false };
  if (!CFG.enabled || !CFG.supabaseUrl || !CFG.supabaseAnonKey) return;

  var SS = 'pc_session', API = CFG.supabaseUrl.replace(/\/+$/, '');
  var PROVIDERS = [
    { id: 'kakao', label: '카카오로 시작하기', bg: '#FEE500', fg: '#191600' },
    { id: 'google', label: 'Google로 시작하기', bg: '#ffffff', fg: '#1f1f1f', border: '#dadce0' },
    { id: 'naver', label: '네이버로 시작하기', bg: '#03C75A', fg: '#ffffff' },
    { id: 'apple', label: 'Apple로 시작하기', bg: '#000000', fg: '#ffffff' }
  ];
  var S = { session: null, profile: null, el: {} };

  function isNative() { try { return !!(window.Capacitor && window.Capacitor.isNativePlatform && window.Capacitor.isNativePlatform()); } catch (e) { return false; } }
  function plugin(n) { try { return (window.Capacitor.Plugins && window.Capacitor.Plugins[n]) || (window.Capacitor.registerPlugin && window.Capacitor.registerPlugin(n)); } catch (e) { return null; } }
  function load() { try { return JSON.parse(localStorage.getItem(SS) || 'null'); } catch (e) { return null; } }
  function save(s) { try { s ? localStorage.setItem(SS, JSON.stringify(s)) : localStorage.removeItem(SS); } catch (e) {} }
  function redirectTo() { return isNative() ? CFG.appScheme + '://auth' : location.origin + location.pathname; }

  async function api(path, opts) {
    opts = opts || {};
    var h = Object.assign({ apikey: CFG.supabaseAnonKey, 'Content-Type': 'application/json' }, opts.headers || {});
    if (S.session && S.session.access_token) h.Authorization = 'Bearer ' + S.session.access_token;
    var r = await fetch(API + path, Object.assign({}, opts, { headers: h }));
    if (r.status === 401 && S.session && S.session.refresh_token && !opts._retry) {
      if (await refresh()) return api(path, Object.assign({}, opts, { _retry: true }));
    }
    var t = await r.text();
    var j = t ? JSON.parse(t) : null;
    if (!r.ok) throw new Error((j && (j.msg || j.message || j.error_description)) || ('HTTP ' + r.status));
    return j;
  }

  async function refresh() {
    try {
      var r = await fetch(API + '/auth/v1/token?grant_type=refresh_token', {
        method: 'POST', headers: { apikey: CFG.supabaseAnonKey, 'Content-Type': 'application/json' },
        body: JSON.stringify({ refresh_token: S.session.refresh_token })
      });
      if (!r.ok) { signOut(true); return false; }
      var j = await r.json();
      S.session = { access_token: j.access_token, refresh_token: j.refresh_token, user: j.user };
      save(S.session); return true;
    } catch (e) { return false; }
  }

  // 가입 후 경과일로 남은 체험일 계산 (서버 기록 기준 → 재설치해도 초기화되지 않음)
  function daysLeft(startedAt) {
    var start = new Date(startedAt).getTime();
    if (!start) return 0;
    var used = Math.floor((Date.now() - start) / 86400000);
    return Math.max(0, (CFG.trialDays || 60) - used);
  }

  async function loadProfile() {
    var uid = S.session && S.session.user && S.session.user.id;
    if (!uid) return null;
    var rows = await api('/rest/v1/profiles?select=id,trial_started_at&id=eq.' + uid);
    if (!rows || !rows.length) {
      rows = await api('/rest/v1/profiles', {
        method: 'POST', headers: { Prefer: 'return=representation' },
        body: JSON.stringify({ id: uid, trial_started_at: new Date().toISOString() })
      });
    }
    S.profile = rows && rows[0];
    return S.profile;
  }

  function applyTrial() {
    var P = window.__pill && window.__pill.Pro;
    var left = S.profile ? daysLeft(S.profile.trial_started_at) : 0;
    if (P && left > 0) P.active = true;
    render(left);
    return left;
  }

  /* ───── UI ───── */
  function css() {
    var s = document.createElement('style');
    s.textContent = '.pc-auth{position:fixed;inset:0;background:#F3F6F4;z-index:80;display:flex;align-items:center;justify-content:center;padding:24px}' +
      '.pc-auth .card{width:100%;max-width:380px;text-align:center}' +
      '.pc-auth h2{margin:0 0 6px;font-size:22px;letter-spacing:-.02em}' +
      '.pc-auth p{margin:0 0 22px;font-size:14px;color:#5b6660;line-height:1.6}' +
      '.pc-auth button{width:100%;padding:13px 16px;margin:8px 0;border:0;border-radius:12px;font-size:15px;font-weight:600;cursor:pointer;font-family:inherit}' +
      '.pc-auth .fine{margin-top:18px;font-size:11.5px;color:#8b9691;line-height:1.55}' +
      '.pc-auth .err{min-height:1.2em;font-size:12.5px;color:#b4413c;margin-top:10px}' +
      '.pc-acct{display:flex;align-items:center;justify-content:space-between;gap:10px;background:#fff;border-radius:14px;padding:10px 14px;margin:0 0 12px;box-shadow:0 1px 3px rgba(0,0,0,.06);font-size:13px}' +
      '.pc-acct b{color:#0E8A74}.pc-acct button{border:0;background:transparent;color:#8b9691;font-size:12.5px;cursor:pointer;font-family:inherit}';
    document.head.appendChild(s);
  }

  function gate(show, err) {
    if (!S.el.gate) {
      var d = document.createElement('div');
      d.className = 'pc-auth'; d.hidden = true;
      var html = '<div class="card"><h2>알약캡쳐 시작하기</h2><p>간편 로그인 후 <b>' + (CFG.trialDays || 60) + '일 동안 모든 기능을 무료</b>로 사용할 수 있습니다.<br>기기를 바꿔도 계정으로 이어집니다.</p>';
      PROVIDERS.forEach(function (p) {
        if (!CFG.providers || !CFG.providers[p.id]) return;
        html += '<button data-p="' + p.id + '" style="background:' + p.bg + ';color:' + p.fg + (p.border ? ';border:1px solid ' + p.border : '') + '">' + p.label + '</button>';
      });
      html += '<div class="err" id="pc-auth-err"></div><div class="fine">로그인하면 <a href="terms.html">이용약관</a>과 <a href="privacy.html">개인정보처리방침</a>에 동의하는 것으로 봅니다. 사진은 기기 밖으로 전송되지 않으며, 계정에는 로그인 식별자와 가입일만 저장됩니다.</div></div>';
      d.innerHTML = html;
      d.addEventListener('click', function (e) { var b = e.target.closest('button[data-p]'); if (b) signIn(b.dataset.p); });
      document.body.appendChild(d); S.el.gate = d;
    }
    S.el.gate.hidden = !show;
    var e = document.getElementById('pc-auth-err'); if (e) e.textContent = err || '';
  }

  function render(left) {
    if (!S.el.acct) {
      var d = document.createElement('div'); d.className = 'pc-acct';
      var host = document.querySelector('.plan') || document.querySelector('.summary');
      if (!host || !host.parentNode) return;
      host.parentNode.insertBefore(d, host); S.el.acct = d;
      d.addEventListener('click', function (e) { if (e.target.dataset && e.target.dataset.act === 'out') signOut(); });
    }
    var u = S.session && S.session.user, id = (u && (u.email || (u.user_metadata && (u.user_metadata.name || u.user_metadata.nickname)))) || '로그인됨';
    S.el.acct.innerHTML = '<span>' + id + (left > 0 ? ' · <b>무료체험 D-' + left + '</b>' : ' · 무료체험 종료') + '</span><button data-act="out">로그아웃</button>';
  }

  /* ───── 로그인 / 로그아웃 ───── */
  async function signIn(provider) {
    var url = API + '/auth/v1/authorize?provider=' + encodeURIComponent(provider) +
      '&redirect_to=' + encodeURIComponent(redirectTo());
    if (isNative()) {
      var B = plugin('Browser');
      if (B && B.open) { await B.open({ url: url }); return; }
    }
    location.href = url;
  }

  function signOut(silent) {
    if (!silent) { try { api('/auth/v1/logout', { method: 'POST' }); } catch (e) {} }
    S.session = null; S.profile = null; save(null);
    var P = window.__pill && window.__pill.Pro; if (P) P.active = false;
    if (S.el.acct) { S.el.acct.remove(); S.el.acct = null; }
    gate(true);
  }

  function parseTokens(str) {
    var h = (str || '').split('#')[1] || '';
    if (!h) return null;
    var q = new URLSearchParams(h);
    if (!q.get('access_token')) return null;
    return { access_token: q.get('access_token'), refresh_token: q.get('refresh_token'), user: null };
  }

  async function adopt(tok) {
    S.session = tok;
    try { S.session.user = await api('/auth/v1/user'); } catch (e) {}
    save(S.session);
    try { await loadProfile(); } catch (e) {}
    gate(false); applyTrial();
  }

  async function start() {
    css();
    var tok = parseTokens(location.hash);
    if (tok) { history.replaceState(null, '', location.pathname + location.search); await adopt(tok); }
    else {
      S.session = load();
      if (S.session) {
        try { S.session.user = await api('/auth/v1/user'); save(S.session); await loadProfile(); gate(false); applyTrial(); }
        catch (e) { signOut(true); }
      } else gate(true);
    }
    if (isNative()) {
      var A = plugin('App');
      if (A && A.addListener) A.addListener('appUrlOpen', async function (d) {
        var t = parseTokens(d && d.url);
        if (t) { var B = plugin('Browser'); if (B && B.close) { try { await B.close(); } catch (e) {} } await adopt(t); }
      });
    }
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', start); else start();
  window.__pcAuth = { state: S, signIn: signIn, signOut: signOut, daysLeft: daysLeft };
})();
