/*
 * Brainstorm-flavored helper.
 *
 * Captures multi-select clicks on [data-choice] elements, ships them over WS,
 * and updates the indicator bar at the bottom of the frame template.
 *
 * Derived from external-repos/superpowers/skills/brainstorming/scripts/helper.js
 * (MIT, Jesse Vincent 2025). Adaptations:
 *   - Adds `action: 'choice'` to match the canonical event schema, while
 *     preserving the `choice` field for backward compat.
 *   - Exposes window.arkhePreview.send (renamed from window.brainstorm.send).
 *   - Replaces unsafe innerHTML interpolation with DOM construction (avoids
 *     XSS if an agent-supplied fragment contains hostile <h3> text content).
 */
(function () {
  const WS_URL = 'ws://' + window.location.host;
  let ws = null;
  let queue = [];
  let backoff = 1000;

  function connect() {
    ws = new WebSocket(WS_URL);

    ws.onopen = () => {
      backoff = 1000;
      while (queue.length > 0) ws.send(JSON.stringify(queue.shift()));
    };

    ws.onmessage = (msg) => {
      let data;
      try { data = JSON.parse(msg.data); } catch (_) { return; }
      if (data.type === 'reload') window.location.reload();
    };

    ws.onclose = () => {
      ws = null;
      setTimeout(connect, backoff);
      backoff = Math.min(backoff * 2, 30000);
    };

    ws.onerror = () => { try { ws.close(); } catch (_) {} };
  }

  function sendEvent(event) {
    if (!event.timestamp) event.timestamp = Date.now();
    if (ws && ws.readyState === WebSocket.OPEN) {
      ws.send(JSON.stringify(event));
    } else {
      queue.push(event);
    }
  }

  function setIndicatorText(plainLabel, suffix) {
    const indicator = document.getElementById('indicator-text');
    if (!indicator) return;
    // Clear children — never use innerHTML with agent-supplied text.
    while (indicator.firstChild) indicator.removeChild(indicator.firstChild);
    if (plainLabel == null) {
      indicator.textContent = suffix; // simple "click an option..." case
      return;
    }
    const accent = document.createElement('span');
    accent.className = 'selected-text';
    accent.textContent = plainLabel;
    indicator.appendChild(accent);
    indicator.appendChild(document.createTextNode(' ' + suffix));
  }

  // Capture clicks on [data-choice] elements
  document.addEventListener('click', (e) => {
    const target = e.target.closest('[data-choice]');
    if (!target) return;

    sendEvent({
      type: 'click',
      action: 'choice',
      choice: target.dataset.choice,
      text: target.textContent.trim().slice(0, 200),
      id: target.id || null
    });

    // Update indicator bar (defer so toggleSelect runs first)
    setTimeout(() => {
      const container = target.closest('.options') || target.closest('.cards');
      const selected = container ? container.querySelectorAll('.selected') : [];
      if (selected.length === 0) {
        setIndicatorText(null, 'Click an option above, then return to the terminal');
      } else if (selected.length === 1) {
        const headingEl = selected[0].querySelector('h3, .content h3, .card-body h3');
        const label = (headingEl && headingEl.textContent.trim()) || selected[0].dataset.choice || '';
        setIndicatorText(label + ' selected', '— return to terminal to continue');
      } else {
        setIndicatorText(selected.length + ' selected', '— return to terminal to continue');
      }
    }, 0);
  });

  // Frame UI: selection tracking helper (kept as a globally-exposed function
  // so HTML fragments can call onclick="toggleSelect(this)").
  window.toggleSelect = function (el) {
    const container = el.closest('.options') || el.closest('.cards');
    const multi = container && container.dataset.multiselect !== undefined;
    if (container && !multi) {
      container.querySelectorAll('.option, .card').forEach(o => o.classList.remove('selected'));
    }
    if (multi) {
      el.classList.toggle('selected');
    } else {
      el.classList.add('selected');
    }
  };

  // Public API (renamed from window.brainstorm)
  window.arkhePreview = {
    send: sendEvent,
    choice: (value, metadata = {}) => sendEvent({ type: 'click', action: 'choice', choice: value, ...metadata })
  };

  connect();
})();
