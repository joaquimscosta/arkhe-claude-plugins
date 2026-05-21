/*
 * Gallery-flavored helper.
 *
 * Captures clicks on `.variant-btn[data-variant]` elements and ships them
 * as click events with action: 'select-variant'. Use when your agent
 * presents the user with a sidebar of variants to choose from.
 *
 * Adapted from internal-repos/tailwindplus/skills/tailwindplus-catalog/
 * scripts/server/helper.js. Updated to emit the canonical {type:'click',
 * action:..., payload:...} schema while preserving the gallery-specific
 * variant payload.
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

  // Capture clicks on .variant-btn[data-variant] elements
  document.addEventListener('click', (e) => {
    const target = e.target.closest('.variant-btn[data-variant]');
    if (!target) return;

    sendEvent({
      type: 'click',
      action: 'select-variant',
      payload: { variant: target.dataset.variant },
      text: target.textContent.trim().slice(0, 200),
      id: target.id || null
    });
  });

  // Public API
  window.arkhePreview = {
    send: sendEvent,
    selectVariant: (variant, metadata = {}) =>
      sendEvent({ type: 'click', action: 'select-variant', payload: { variant, ...metadata } })
  };

  connect();
})();
