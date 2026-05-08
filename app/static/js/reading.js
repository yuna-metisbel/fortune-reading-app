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
  var loadingEl  = document.getElementById('loading-crystal');
  var streamArea = document.getElementById('streaming-area');
  var streamEl   = document.getElementById('streaming-content');
  var actionsEl  = document.getElementById('generate-actions');
  var chatLink   = document.getElementById('chat-link');

  if (!streamEl) return;

  var reader = resp.body.getReader();
  var decoder = new TextDecoder('utf-8');
  var buffer = '';
  var rawText = '';
  var finishedReadingId = null;
  var isEventDone = false;

  // Show streaming area, hide loading crystal after first chunk
  var firstChunk = true;

  while (true) {
    var result = await reader.read();
    if (result.done) break;

    buffer += decoder.decode(result.value, { stream: true });

    // Process complete SSE lines
    var lines = buffer.split('\n');
    buffer = lines.pop(); // keep incomplete last line

    for (var i = 0; i < lines.length; i++) {
      var line = lines[i].trim();

      if (line === '') continue;

      if (line.startsWith('event:')) {
        var evtName = line.replace('event:', '').trim();
        if (evtName === 'done') {
          isEventDone = true;
        }
        continue;
      }

      if (line.startsWith('data:')) {
        var data = line.replace('data:', '').trim();

        if (isEventDone) {
          // data after "event: done" is the reading ID
          finishedReadingId = parseInt(data, 10);
          isEventDone = false;
        } else {
          // Regular text chunk
          rawText += data;

          if (firstChunk) {
            firstChunk = false;
            if (loadingEl) loadingEl.style.display = 'none';
            if (streamArea) streamArea.classList.add('visible');
          }

          streamEl.innerHTML = renderMarkdown(rawText);
          streamEl.scrollIntoView({ behavior: 'smooth', block: 'end' });
        }
      }
    }
  }

  // Stream complete — redirect to result page
  if (finishedReadingId) {
    window.location.href = '/reading/' + finishedReadingId;
    return;
  }

  // Fallback: show action buttons if no reading ID was received
  if (actionsEl) actionsEl.classList.add('visible');

  if (chatLink && finishedReadingId) {
    chatLink.href = '/chat/' + finishedReadingId;
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

    var data = {
      nickname:    form.nickname.value.trim(),
      birth_date:  form.birth_date.value,
      birth_time:  form.birth_time ? form.birth_time.value || null : null,
      birth_place: form.birth_place ? form.birth_place.value.trim() || null : null,
      gender:      form.gender ? form.gender.value || null : null,
      blood_type:  form.blood_type ? form.blood_type.value || null : null,
      theme:       form.theme.value.trim(),
    };

    try {
      var resp = await fetch('/api/readings/personal/stream', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data),
      });

      if (!resp.ok) {
        alert('エラーが発生しました。もう一度お試しください。');
        if (submitBtn) { submitBtn.disabled = false; submitBtn.textContent = '✦ 星図を読み解く'; }
        return;
      }

      // Navigate to generate page which streams the result
      // But since we're POSTing directly, handle the stream here on the same page
      // by transitioning the UI to a streaming view
      _showStreamingView();
      await handleStream(resp);

    } catch (err) {
      console.error(err);
      alert('通信エラーが発生しました。');
      if (submitBtn) { submitBtn.disabled = false; submitBtn.textContent = '✦ 星図を読み解く'; }
    }
  });
}

function _showStreamingView() {
  // If the form page is being used, we inject the streaming UI inline
  var formPage = document.querySelector('.form-page');
  if (!formPage) return;

  // Replace form with streaming UI
  formPage.innerHTML = [
    '<div class="generate-page" style="padding-top:40px">',
    '  <div id="loading-crystal" class="loading-crystal fade-in">',
    '    <span class="loading-crystal-emoji">🔮</span>',
    '    <h2 class="loading-title">星の配置を読み解いています</h2>',
    '    <p class="loading-text">少々お待ちください<span class="loading-dots"></span></p>',
    '  </div>',
    '  <div id="streaming-area" class="streaming-area" aria-live="polite">',
    '    <div class="streaming-header">✦ &nbsp;あなたへのメッセージ&nbsp; ✦</div>',
    '    <div id="streaming-content" class="streaming-content"></div>',
    '  </div>',
    '  <div id="generate-actions" class="generate-actions">',
    '    <a id="chat-link" href="#" class="btn btn-primary">💬 鑑定師に相談する</a>',
    '    <a href="/" class="btn btn-secondary">← トップに戻る</a>',
    '  </div>',
    '</div>',
  ].join('');
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

    var data = {
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
      var resp = await fetch('/api/readings/compatibility/stream', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data),
      });

      if (!resp.ok) {
        alert('エラーが発生しました。もう一度お試しください。');
        if (submitBtn) { submitBtn.disabled = false; submitBtn.textContent = '✦ 二人の星図を読み解く'; }
        return;
      }

      _showStreamingView();
      await handleStream(resp);

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

// ── Bootstrap ────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', function () {
  initPersonalForm();
  initCompatibilityForm();
  initSavedProfileHandlers();
  initGeneratePage();
});
