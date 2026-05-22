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
        var eventName = line.replace('event:', '').trim();
        if (eventName === 'done') isEventDone = true;
        if (eventName === 'error') {
          if (window._ritualInterval) clearInterval(window._ritualInterval);
          var nextLine = lines[i + 1];
          var errMsg = 'エラーが発生しました。もう一度お試しください。';
          if (nextLine && nextLine.trim().startsWith('data:')) {
            errMsg = nextLine.trim().replace(/^data:\s*/, '');
            i++;
          }
          alert(errMsg);
          window.location.href = '/';
          return;
        }
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
    if (phaseEl) phaseEl.textContent = '✦ 鑑定が完了しました';
    setTimeout(function() {
      window.location.href = '/reading/' + finishedReadingId;
    }, 1000);
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

    var y = (form.birth_year.value || '').trim();
    var m = (form.birth_month.value || '').trim().padStart(2, '0');
    var d = (form.birth_day.value || '').trim().padStart(2, '0');
    var birthDate = y + '-' + m + '-' + d;

    var bh = (form.birth_hour ? form.birth_hour.value.trim() : '');
    var bm = (form.birth_minute ? form.birth_minute.value.trim() : '');
    var birthTime = (bh && bm) ? bh.padStart(2, '0') + ':' + bm.padStart(2, '0') : null;

    var formData = {
      nickname:    form.nickname.value.trim(),
      birth_date:  birthDate,
      birth_time:  birthTime,
      birth_place: form.birth_place ? form.birth_place.value.trim() || null : null,
      gender:      form.gender ? form.gender.value || null : null,
      blood_type:  form.blood_type ? form.blood_type.value || null : null,
      theme:       form.theme.value.trim(),
    };

    localStorage.setItem('fortune_birth', JSON.stringify({
      y: y, m: (form.birth_month.value || '').trim(), d: (form.birth_day.value || '').trim()
    }));

    try {
      var resp = await fetch('/api/readings/personal/stream', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData),
      });

      if (!resp.ok) {
        alert('エラーが発生しました。もう一度お試しください。');
        if (submitBtn) { submitBtn.disabled = false; submitBtn.textContent = '星図を読み解く'; }
        return;
      }

      _showStreamingView();
      await handleStream(resp);

    } catch (err) {
      console.error(err);
      alert('通信エラーが発生しました。');
      if (submitBtn) { submitBtn.disabled = false; submitBtn.textContent = '星図を読み解く'; }
    }
  });
}

function _showStreamingView() {
  var container = document.querySelector('.container');
  if (!container) return;

  container.innerHTML = [
    '<div class="loading-page" style="min-height:80vh; padding-top:60px;">',
    '  <div class="ritual-orb">',
    '    <div class="ritual-ring ritual-ring--1"></div>',
    '    <div class="ritual-ring ritual-ring--2"></div>',
    '    <div class="ritual-ring ritual-ring--3"></div>',
    '    <div class="ritual-core">🔮</div>',
    '  </div>',
    '  <h2 class="loading-title" style="margin-top:32px;">星の配置を読み解いています</h2>',
    '  <p class="loading-sub" id="ritual-phase">西洋占星術の星座を確認中</p>',
    '  <div class="ritual-progress"><div class="ritual-bar" id="ritual-bar"></div></div>',
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

    function buildDate(prefix) {
      var y = (form[prefix + 'birth_year'].value || '').trim();
      var m = (form[prefix + 'birth_month'].value || '').trim().padStart(2, '0');
      var d = (form[prefix + 'birth_day'].value || '').trim().padStart(2, '0');
      return y + '-' + m + '-' + d;
    }
    function buildTime(prefix) {
      var h = form[prefix + 'birth_hour'] ? form[prefix + 'birth_hour'].value.trim() : '';
      var m = form[prefix + 'birth_minute'] ? form[prefix + 'birth_minute'].value.trim() : '';
      return (h && m) ? h.padStart(2, '0') + ':' + m.padStart(2, '0') : null;
    }

    var formData = {
      person1_nickname:    form.person1_nickname.value.trim(),
      person1_birth_date:  buildDate('person1_'),
      person1_birth_time:  buildTime('person1_'),
      person1_birth_place: form.person1_birth_place ? form.person1_birth_place.value.trim() || null : null,
      person1_gender:      form.person1_gender ? form.person1_gender.value || null : null,
      person1_blood_type:  form.person1_blood_type ? form.person1_blood_type.value || null : null,
      person2_nickname:    form.person2_nickname.value.trim(),
      person2_birth_date:  buildDate('person2_'),
      person2_birth_time:  buildTime('person2_'),
      person2_birth_place: form.person2_birth_place ? form.person2_birth_place.value.trim() || null : null,
      person2_gender:      form.person2_gender ? form.person2_gender.value || null : null,
      person2_blood_type:  form.person2_blood_type ? form.person2_blood_type.value || null : null,
      relationship_type:   form.relationship_type.value,
      met_date:            form.met_date ? form.met_date.value.trim() || null : null,
      theme:               form.theme.value.trim(),
    };

    try {
      var resp = await fetch('/api/readings/compatibility/stream', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData),
      });

      if (!resp.ok) {
        alert('エラーが発生しました。もう一度お試しください。');
        if (submitBtn) { submitBtn.disabled = false; submitBtn.textContent = '二人の星図を読み解く'; }
        return;
      }

      _showStreamingView();
      await handleStream(resp);

    } catch (err) {
      console.error(err);
      alert('通信エラーが発生しました。');
      if (submitBtn) { submitBtn.disabled = false; submitBtn.textContent = '二人の星図を読み解く'; }
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
  var bd = opt.dataset.birthDate || '';
  if (bd) {
    var parts = bd.split('-');
    setVal('birth_year',  parts[0] || '');
    setVal('birth_month', parts[1] ? String(parseInt(parts[1])) : '');
    setVal('birth_day',   parts[2] ? String(parseInt(parts[2])) : '');
  }
  var bt = opt.dataset.birthTime || '';
  if (bt) {
    var tp = bt.split(':');
    setVal('birth_hour',   tp[0] || '');
    setVal('birth_minute', tp[1] || '');
  }
  setVal('birth_place', opt.dataset.birthPlace || '');
  setVal('gender',      opt.dataset.gender     || '');
  setVal('blood_type',  opt.dataset.bloodType  || '');

  // Legacy support: also fill combined fields if they exist
  if (bd) setVal('birth_date', bd);
  if (bt) setVal('birth_time', bt);
}

// ── Generate page SSE auto-start ─────────────────────────────
function initGeneratePage() {
  if (typeof readingId === 'undefined' || !readingId) return;

  var loadingView = document.getElementById('loading-view');
  var phases = document.querySelectorAll('.phase');
  var actions = document.getElementById('generate-actions');

  if (!loadingView) {
    // Not on generate page
    return;
  }

  // Animate phases
  var phaseIdx = 0;
  var phaseInterval = setInterval(function() {
    if (phaseIdx < phases.length) {
      if (phaseIdx > 0) {
        phases[phaseIdx - 1].classList.remove('active');
        phases[phaseIdx - 1].classList.add('done');
      }
      phases[phaseIdx].classList.add('active');
      phaseIdx++;
    }
    if (phaseIdx >= phases.length) {
      clearInterval(phaseInterval);
      // All phases done, redirect to result
      setTimeout(function() {
        window.location.href = '/reading/' + readingId;
      }, 1500);
    }
  }, 3000);

  // Set result and chat links
  var resultLink = document.getElementById('result-link');
  var chatLink = document.getElementById('chat-link');
  if (resultLink) resultLink.href = '/reading/' + readingId;
  if (chatLink) chatLink.href = '/chat/' + readingId;
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
  // Auto-fill birth date from localStorage
  var savedBirth = localStorage.getItem('fortune_birth');
  if (savedBirth) {
    try {
      var sb = JSON.parse(savedBirth);
      var byEl = document.getElementById('birth_year');
      var bmEl = document.getElementById('birth_month');
      var bdEl = document.getElementById('birth_day');
      if (byEl && !byEl.value) byEl.value = sb.y || '';
      if (bmEl && !bmEl.value) bmEl.value = sb.m || '';
      if (bdEl && !bdEl.value) bdEl.value = sb.d || '';
      // Also fill person1 fields for compatibility form
      var p1y = document.getElementById('person1_birth_year');
      var p1m = document.getElementById('person1_birth_month');
      var p1d = document.getElementById('person1_birth_day');
      if (p1y && !p1y.value) p1y.value = sb.y || '';
      if (p1m && !p1m.value) p1m.value = sb.m || '';
      if (p1d && !p1d.value) p1d.value = sb.d || '';
    } catch(e) {}
  }

  initPersonalForm();
  initCompatibilityForm();
  initSavedProfileHandlers();
  initGeneratePage();
  autoFillLatestProfile();
});
