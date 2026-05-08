/* ============================================================
   chat.js — LINE-style chat with SSE streaming
   ============================================================ */

'use strict';

var isStreaming = false;

// ── HTML escape ──────────────────────────────────────────────
function escapeHtml(str) {
  if (typeof str !== 'string') return '';
  return str
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;');
}

// ── Chat-flavoured markdown renderer ────────────────────────
// Lighter than the reading renderer: bold, headings as bold+br, list items as ・
function renderChatMarkdown(text) {
  if (!text) return '';
  var escaped = escapeHtml(text);

  // Headings → bold text + line break
  escaped = escaped.replace(/^#{1,3} (.+)/gm, '<strong>$1</strong><br>');

  // Bold: **text**
  escaped = escaped.replace(/\*\*([^*\n]+)\*\*/g, '<strong>$1</strong>');

  // Italic: *text*
  escaped = escaped.replace(/\*([^*\n]+)\*/g, '<em>$1</em>');

  // Unordered list items → ・
  escaped = escaped.replace(/^[-*] (.+)/gm, '・$1');

  // Ordered list items → 数字. text
  escaped = escaped.replace(/^\d+\. (.+)/gm, '・$1');

  // Double newlines → paragraph break
  escaped = escaped.replace(/\n{2,}/g, '</p><p>');

  // Single newlines → <br>
  escaped = escaped.replace(/\n/g, '<br>');

  return '<p>' + escaped + '</p>';
}

// ── Scroll to bottom of messages area ───────────────────────
function scrollToBottom() {
  var messages = document.getElementById('chat-messages');
  if (messages) {
    messages.scrollTop = messages.scrollHeight;
  }
}

// ── Create a new bubble element ──────────────────────────────
function createBubble(role, senderLabel) {
  var bubble = document.createElement('div');
  bubble.className = 'chat-bubble ' + role;

  var sender = document.createElement('div');
  sender.className = 'chat-bubble-sender';
  sender.textContent = senderLabel;

  var body = document.createElement('div');
  body.className = 'chat-bubble-body';

  bubble.appendChild(sender);
  bubble.appendChild(body);
  return bubble;
}

// ── Create typing indicator ──────────────────────────────────
function createTypingIndicator() {
  var el = document.createElement('div');
  el.className = 'typing-indicator';
  el.id = 'typing-indicator';
  for (var i = 0; i < 3; i++) {
    var dot = document.createElement('div');
    dot.className = 'typing-dot';
    el.appendChild(dot);
  }
  return el;
}

// ── Main send function ───────────────────────────────────────
async function sendMessage() {
  if (isStreaming) return;

  var inputEl  = document.getElementById('chat-input');
  var sendBtn  = document.getElementById('chat-send-btn');
  var messages = document.getElementById('chat-messages');

  if (!inputEl || !messages) return;

  var text = inputEl.value.trim();
  if (!text) return;

  isStreaming = true;
  inputEl.value = '';
  inputEl.style.height = 'auto';
  if (sendBtn) sendBtn.disabled = true;

  // Remove welcome placeholder if present
  var welcome = messages.querySelector('.chat-welcome');
  if (welcome) welcome.remove();

  // Append user bubble
  var userBubble = createBubble('user', 'あなた');
  userBubble.querySelector('.chat-bubble-body').textContent = text;
  messages.appendChild(userBubble);
  scrollToBottom();

  // Show typing indicator
  var typingEl = createTypingIndicator();
  messages.appendChild(typingEl);
  scrollToBottom();

  try {
    var resp = await fetch('/api/chat/' + readingId + '/send', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message: text }),
    });

    // Remove typing indicator
    typingEl.remove();

    if (!resp.ok) {
      var errBubble = createBubble('assistant', '✦ 鑑定師');
      errBubble.querySelector('.chat-bubble-body').textContent = 'エラーが発生しました。もう一度お試しください。';
      messages.appendChild(errBubble);
      scrollToBottom();
      return;
    }

    // Create assistant bubble
    var asstBubble = createBubble('assistant', '✦ 鑑定師');
    var bodyEl = asstBubble.querySelector('.chat-bubble-body');
    bodyEl.innerHTML = '';
    messages.appendChild(asstBubble);
    scrollToBottom();

    // Stream the response
    var reader  = resp.body.getReader();
    var decoder = new TextDecoder('utf-8');
    var buffer  = '';
    var rawText = '';

    while (true) {
      var result = await reader.read();
      if (result.done) break;

      buffer += decoder.decode(result.value, { stream: true });
      var lines = buffer.split('\n');
      buffer = lines.pop();

      for (var i = 0; i < lines.length; i++) {
        var line = lines[i].trim();
        if (line === '') continue;

        if (line === 'event: done' || line.startsWith('event:')) continue;

        if (line.startsWith('data:')) {
          var data = line.replace('data:', '').trim();
          if (data === 'ok') continue;

          rawText += data;
          bodyEl.innerHTML = renderChatMarkdown(rawText);
          scrollToBottom();
        }
      }
    }

  } catch (err) {
    console.error(err);
    typingEl.remove();
    var errBubble2 = createBubble('assistant', '✦ 鑑定師');
    errBubble2.querySelector('.chat-bubble-body').textContent = '通信エラーが発生しました。';
    messages.appendChild(errBubble2);
    scrollToBottom();
  } finally {
    isStreaming = false;
    if (sendBtn) sendBtn.disabled = false;
    inputEl.focus();
    scrollToBottom();
  }
}

// ── Auto-resize textarea ─────────────────────────────────────
function autoResize(el) {
  el.style.height = 'auto';
  el.style.height = Math.min(el.scrollHeight, 120) + 'px';
}

// ── Bootstrap ────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', function () {
  var inputEl = document.getElementById('chat-input');
  var sendBtn = document.getElementById('chat-send-btn');

  if (inputEl) {
    // Auto-resize
    inputEl.addEventListener('input', function () {
      autoResize(this);
    });

    // Enter key — send on Enter, newline on Shift+Enter
    inputEl.addEventListener('keydown', function (e) {
      if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        sendMessage();
      }
    });
  }

  if (sendBtn) {
    sendBtn.addEventListener('click', function () {
      sendMessage();
    });
  }

  // Scroll to bottom on load (for existing messages)
  scrollToBottom();
});
