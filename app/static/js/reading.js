/* ============================================================
   reading.js — Form submission + SSE streaming handler
   ============================================================ */

'use strict';

// ── HTML escape utility ──────────────────────────────────────
function escapeHtml(str) {
  if (typeof str !== 'string') return '';
  return str
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;');
}

// ── Simple markdown → HTML converter ────────────────────────
function renderMarkdown(text) {
  if (!text) return '';
  var escaped = escapeHtml(text);
  var lines = escaped.split('\n');
  var html = '';
  var inList = false;

  for (var i = 0; i < lines.length; i++) {
    var line = lines[i];

    if (/^### (.+)/.test(line)) {
      if (inList) { html += '</ul>'; inList = false; }
      html += '<h3>' + line.replace(/^### /, '') + '</h3>';
    } else if (/^## (.+)/.test(line)) {
      if (inList) { html += '</ul>'; inList = false; }
      html += '<h2>' + line.replace(/^## /, '') + '</h2>';
    } else if (/^# (.+)/.test(line)) {
      if (inList) { html += '</ul>'; inList = false; }
      html += '<h2>' + line.replace(/^# /, '') + '</h2>';
    } else if (/^[-*] (.+)/.test(line)) {
      if (!inList) { html += '<ul>'; inList = true; }
      html += '<li>' + line.replace(/^[-*] /, '') + '</li>';
    } else if (/^\d+\. (.+)/.test(line)) {
      if (inList) { html += '</ul>'; inList = false; }
      html += '<li>' + line.replace(/^\d+\. /, '') + '</li>';
    } else if (line.trim() === '') {
      if (inList) { html += '</ul>'; inList = false; }
    } else {
      if (inList) { html += '</ul>'; inList = false; }
      html += '<p>' + line + '</p>';
    }
  }
  if (inList) html += '</ul>';

  // Bold: **text**
  html = html.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>');
  // Italic: *text*
  html = html.replace(/\*([^*\n]+)\*/g, '<em>$1</em>');

  return html;
}

// ── SSE stream handler ───────────────────────────────────────
async function handleStream(resp) {
  var reader = resp.body.getReader();
  var decoder = new TextDecoder('utf-8');
  var buffer = '';
  var finishedReadingId = null;
  var isEventDone = false;

  while (true) {
    var result = await reader.read();
    if (result.done) break;

    buffer += decoder.decode(result.value, { stream: true });
    var lines = buffer.split('\n');
    buffer = lines.pop();

    for (var i = 0; i < lines.length; i++) {
      var line = lines[i].trim();
      if (line === '') continue;

      if (line.startsWith('event:')) {
        if (line.replace('event:', '').trim() === 'done') isEventDone = true;
        continue;
      }

      if (line.startsWith('data:') && isEventDone) {
        var data = line.charAt(5) === ' ' ? line.slice(6) : line.slice(5);
        finishedReadingId = parseInt(data, 10);
        isEventDone = false;
      }
    }
  }

  if (window._ritualInterval) clearInterval(window._ritualInterval);

  if (finishedReadingId) {
    var barEl = document.getElementById('ritual-bar');
    var phaseEl = document.getElementById('ritual-phase');
    if (barEl) barEl.style.width = '100%';
    if (phaseEl) phaseEl.textContent = '鑑定が完了しました';
    setTimeout(function() {
      window.location.href = '/reading/' + finishedReadingId;
    }, 800);
  }
}

// ── Personal reading form ────────────────────────────────────
function initPersonalForm() {
  var form = document.getElementById('reading-form');
  if (!form) return;

  form.addEventListener('submit', async function (e) {
    e.preventDefault();

    var submitBtn = form.querySelector('[type="submit"]');
    if (submitBtn) {
      submitBtn.disabled = true;
      submitBtn.textContent = '読み解き中...';
    }

    var formData = {
      nickname:    form.nickname.value.trim(),
      birth_date:  form.birth_date.value,
      birth_time:  form.birth_time ? form.birth_time.value || null : null,
      birth_place: form.birth_place ? form.birth_place.value.trim() || null : null,
      gender:      form.gender ? form.gender.value || null : null,
      blood_type:  form.blood_type ? form.blood_type.value || null : null,
      theme:       form.theme.value.trim(),
    };

    try {
      var resp = await fetch('/api/payment/create-checkout', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ reading_type: 'personal', form_data: formData }),
      });

      var data = await resp.json();
      if (data.checkout_url) {
        window.location.href = data.checkout_url;
      } else {
        alert('決済の開始に失敗しました: ' + (data.error || '不明なエラー'));
        if (submitBtn) { submitBtn.disabled = false; submitBtn.textContent = '✦ 星図を読み解く'; }
      }

    } catch (err) {
      console.error(err);
      alert('通信エラーが発生しました。');
      if (submitBtn) { submitBtn.disabled = false; submitBtn.textContent = '✦ 星図を読み解く'; }
    }
  });
}

function _showStreamingView() {
  var formPage = document.querySelector('.form-page');
  if (!formPage) return;

  formPage.innerHTML = [
    '<div class="generate-page" style="padding-top:40px">',
    '  <div class="ritual-animation fade-in">',
    '    <div class="ritual-orb">',
    '      <div class="ritual-ring ritual-ring--1"></div>',
    '      <div class="ritual-ring ritual-ring--2"></div>',
    '      <div class="ritual-ring ritual-ring--3"></div>',
    '      <div class="ritual-core">🔮</div>',
    '    </div>',
    '    <div class="ritual-stars">',
    '      <span class="ritual-star" style="--d:0s;--x:-60px;--y:-80px">✦</span>',
    '      <span class="ritual-star" style="--d:0.4s;--x:70px;--y:-50px">✧</span>',
    '      <span class="ritual-star" style="--d:0.8s;--x:-40px;--y:60px">✦</span>',
    '      <span class="ritual-star" style="--d:1.2s;--x:55px;--y:70px">✧</span>',
    '      <span class="ritual-star" style="--d:1.6s;--x:0px;--y:-100px">☽</span>',
    '    </div>',
    '    <h2 class="ritual-title">星の配置を読み解いています</h2>',
    '    <p class="ritual-phase" id="ritual-phase">西洋占星術の星座を確認中</p>',
    '    <div class="ritual-progress"><div class="ritual-bar" id="ritual-bar"></div></div>',
    '  </div>',
    '  <div id="streaming-area" class="streaming-area" style="display:none"></div>',
    '  <div id="streaming-content" style="display:none"></div>',
    '</div>',
  ].join('');

  var phases = [
    '西洋占星術の星座を確認中',
    '数秘術のライフパスを算出中',
    '九星気学の本命星を照合中',
    '六星占術の運命星を判定中',
    '四柱推命の命式を解読中',
    'タロットカードを引いています',
    '6つの占術を統合しています',
    'あなただけのメッセージを紡いでいます',
  ];
  var phaseEl = document.getElementById('ritual-phase');
  var barEl = document.getElementById('ritual-bar');
  var idx = 0;
  var phaseInterval = setInterval(function() {
    idx++;
    if (idx < phases.length) {
      phaseEl.textContent = phases[idx];
      barEl.style.width = Math.min((idx + 1) / phases.length * 100, 95) + '%';
    }
  }, 4000);
  window._ritualInterval = phaseInterval;
}

// ── Compatibility reading form ───────────────────────────────
function initCompatibilityForm() {
  var form = document.getElementById('compatibility-form');
  if (!form) return;

  form.addEventListener('submit', async function (e) {
    e.preventDefault();

    var submitBtn = form.querySelector('[type="submit"]');
    if (submitBtn) {
      submitBtn.disabled = true;
      submitBtn.textContent = '読み解き中...';
    }

    var formData = {
      person1_nickname:    form.person1_nickname.value.trim(),
      person1_birth_date:  form.person1_birth_date.value,
      person1_birth_time:  form.person1_birth_time ? form.person1_birth_time.value || null : null,
      person1_birth_place: form.person1_birth_place ? form.person1_birth_place.value.trim() || null : null,
      person1_gender:      form.person1_gender ? form.person1_gender.value || null : null,
      person1_blood_type:  form.person1_blood_type ? form.person1_blood_type.value || null : null,
      person2_nickname:    form.person2_nickname.value.trim(),
      person2_birth_date:  form.person2_birth_date.value,
      person2_birth_time:  form.person2_birth_time ? form.person2_birth_time.value || null : null,
      person2_birth_place: form.person2_birth_place ? form.person2_birth_place.value.trim() || null : null,
      person2_gender:      form.person2_gender ? form.person2_gender.value || null : null,
      person2_blood_type:  form.person2_blood_type ? form.person2_blood_type.value || null : null,
      relationship_type:   form.relationship_type.value,
      met_date:            form.met_date ? form.met_date.value.trim() || null : null,
      theme:               form.theme.value.trim(),
    };

    try {
      var resp = await fetch('/api/payment/create-checkout', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ reading_type: 'compatibility', form_data: formData }),
      });

      var data = await resp.json();
      if (data.checkout_url) {
        window.location.href = data.checkout_url;
      } else {
        alert('決済の開始に失敗しました: ' + (data.error || '不明なエラー'));
        if (submitBtn) { submitBtn.disabled = false; submitBtn.textContent = '✦ 二人の星図を読み解く'; }
      }

    } catch (err) {
      console.error(err);
      alert('通信エラーが発生しました。');
      if (submitBtn) { submitBtn.disabled = false; submitBtn.textContent = '✦ 二人の星図を読み解く'; }
    }
  });
}

// ── Saved profile auto-fill ──────────────────────────────────
function initSavedProfileHandlers() {
  // Personal form
  var singleSelect = document.getElementById('saved-profile');
  if (singleSelect) {
    singleSelect.addEventListener('change', function () {
      var opt = this.options[this.selectedIndex];
      if (!opt || !opt.value) return;
      _fillFields('', opt);
    });
  }

  // Compatibility form — person 1 and person 2
  var p1Select = document.getElementById('saved-profile-p1');
  if (p1Select) {
    p1Select.addEventListener('change', function () {
      var opt = this.options[this.selectedIndex];
      if (!opt || !opt.value) return;
      _fillFields('person1_', opt);
    });
  }

  var p2Select = document.getElementById('saved-profile-p2');
  if (p2Select) {
    p2Select.addEventListener('change', function () {
      var opt = this.options[this.selectedIndex];
      if (!opt || !opt.value) return;
      _fillFields('person2_', opt);
    });
  }
}

function _fillFields(prefix, opt) {
  function setVal(name, val) {
    var el = document.getElementById(prefix + name) || document.querySelector('[name="' + prefix + name + '"]');
    if (el && val !== undefined && val !== null) el.value = val;
  }
  setVal('nickname',    opt.dataset.nickname   || '');
  setVal('birth_date',  opt.dataset.birthDate  || '');
  setVal('birth_time',  opt.dataset.birthTime  || '');
  setVal('birth_place', opt.dataset.birthPlace || '');
  setVal('gender',      opt.dataset.gender     || '');
  setVal('blood_type',  opt.dataset.bloodType  || '');
}

// ── Generate page SSE auto-start ─────────────────────────────
function initGeneratePage() {
  // Check if we're on the generate page AND the form was submitted to this URL
  // The generate page is served at /reading/generate/{id} but we want to stream
  // from the stored reading. The generate page just shows a loading state —
  // in this app the actual streaming is done inline on the form page.
  // If readingId is defined (injected by the template), we could fetch the result.
  // For this implementation: if readingId is set but there's no pending stream,
  // redirect to the saved result page.
  if (typeof readingId !== 'undefined' && readingId) {
    // On the standalone generate page we auto-redirect to result
    // (In the current flow, the stream is handled inline on the form page)
    var streamArea = document.getElementById('streaming-area');
    var loadingEl  = document.getElementById('loading-crystal');
    if (streamArea && loadingEl && !streamArea.classList.contains('visible')) {
      // Redirect to saved result after a brief pause
      setTimeout(function () {
        window.location.href = '/reading/' + readingId;
      }, 1200);
    }
  }
}

// ── Auto-fill latest profile into compatibility form ────────
function autoFillLatestProfile() {
  var p1Select = document.getElementById('saved-profile-p1');
  if (!p1Select) return;
  if (p1Select.options.length <= 1) return;

  var latestOpt = p1Select.options[1];
  p1Select.value = latestOpt.value;
  _fillFields('person1_', latestOpt);
}

// ── Bootstrap ────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', function () {
  initPersonalForm();
  initCompatibilityForm();
  initSavedProfileHandlers();
  initGeneratePage();
  autoFillLatestProfile();
});
